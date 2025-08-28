# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import base64
import collections
import contextlib
import functools
import getpass
import inspect
import itertools
import json
import math
import netrc
import os
import random
import re
import subprocess
import sys
import time
import types
import xml.etree.ElementTree

from ..compat import (
    compat_etree_fromstring,
    compat_expanduser,
    compat_urllib_parse as urllib_parse,
    compat_urllib_request as urllib_request,
    compat_http_client as http_client,
    compat_http_cookiejar as http_cookiejar,
    compat_http_cookies as http_cookies,
    urllib_req_to_req,
)
from ..cookies import LenientSimpleCookie
from ..downloader.f4m import get_base_url, remove_encrypted_media
from ..downloader.hls import HlsFD
from ..globals import plugin_ies_overrides
from ..networking import HEADRequest, Request
from ..networking.exceptions import (
    HTTPError,
    IncompleteRead,
    TransportError,
    network_exceptions,
)
from ..utils import (
    IDENTITY,
    JSON_LD_RE,
    NO_DEFAULT,
    ExtractorError,
    FormatSorter,
    GeoRestrictedError,
    GeoUtils,
    ISO639Utils,
    LenientJSONDecoder,
    Popen,
    RegexNotFoundError,
    RetryManager,
    UnsupportedError,
    age_restricted,
    base_url,
    bug_reports_message,
    classproperty,
    clean_html,
    deprecation_warning,
    determine_ext,
    dict_get,
    encode_data_uri,
    extract_attributes,
    filter_dict,
    fix_xml_ampersands,
    float_or_none,
    format_field,
    int_or_none,
    join_nonempty,
    js_to_json,
    mimetype2ext,
    netrc_from_content,
    orderedSet,
    parse_bitrate,
    parse_codecs,
    parse_duration,
    parse_iso8601,
    parse_m3u8_attributes,
    parse_resolution,
    qualities,
    sanitize_url,
    smuggle_url,
    str_or_none,
    str_to_int,
    strip_or_none,
    traverse_obj,
    truncate_string,
    try_call,
    try_get,
    unescapeHTML,
    unified_strdate,
    unified_timestamp,
    url_basename,
    url_or_none,
    urlhandle_detect_ext,
    urljoin,
    variadic,
    xpath_element,
    xpath_text,
    xpath_with_ns,
)
from ..utils._utils import _request_dump_filename
from ..utils.jslib import devalue


class InfoExtractorMetaclass(type):
    def __init__(cls, name, bases, dct):
        super(InfoExtractorMetaclass, cls).__init__(name, bases, dct)
        plugin_name = dct.get('plugin_name')
        if plugin_name:
            mro = inspect.getmro(cls)
            next_mro_class = super_class = mro[mro.index(cls) + 1]

            while getattr(super_class, '__wrapped__', None):
                super_class = super_class.__wrapped__

            if not any(override.PLUGIN_NAME == plugin_name for override in plugin_ies_overrides.value[super_class]):
                cls.__wrapped__ = next_mro_class
                cls.PLUGIN_NAME, cls.ie_key = plugin_name, next_mro_class.ie_key
                cls.IE_NAME = '{0}+{1}'.format(next_mro_class.IE_NAME, plugin_name)

                setattr(sys.modules[super_class.__module__], super_class.__name__, cls)
                plugin_ies_overrides.value[super_class].append(cls)


class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class InfoExtractor(object):
    """Information Extractor class.

    Information extractors are the classes that, given a URL, extract
    information about the video (or videos) the URL refers to. This
    information includes the real video URL, the video title, author and
    others. The information is stored in a dictionary which is then
    passed to the YoutubeDL. The YoutubeDL processes this
    information possibly downloading the video to the file system, among
    other possible outcomes.
    ...
    """
    __metaclass__ = InfoExtractorMetaclass

    _ready = False
    _downloader = None
    _x_forwarded_for_ip = None
    _GEO_BYPASS = True
    _GEO_COUNTRIES = None
    _GEO_IP_BLOCKS = None
    _WORKING = True
    _ENABLED = True
    _NETRC_MACHINE = None
    IE_DESC = None
    SEARCH_KEY = None
    _VALID_URL = None
    _EMBED_REGEX = []

    def _login_hint(self, method=NO_DEFAULT, netrc=None):
        password_hint = '--username and --password, --netrc-cmd, or --netrc ({0}) to provide account credentials'.format(netrc or self._NETRC_MACHINE)
        cookies_hint = 'See  https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp  for how to manually pass cookies'
        return {
            None: '',
            'any': 'Use --cookies, --cookies-from-browser, {0}. {1}'.format(password_hint, cookies_hint),
            'password': 'Use {0}'.format(password_hint),
            'cookies': 'Use --cookies-from-browser or --cookies for the authentication. {0}'.format(cookies_hint),
            'session_cookies': 'Use --cookies for the authentication (--cookies-from-browser might not work). {0}'.format(cookies_hint),
        }[method if method is not NO_DEFAULT else 'any' if self.supports_login() else 'cookies']

    def __init__(self, downloader=None):
        """Constructor. Receives an optional downloader (a YoutubeDL instance).
        If a downloader is not passed during initialization,
        it must be set using "set_downloader()" before "extract()" is called"""
        self._ready = False
        self._x_forwarded_for_ip = None
        self._printed_messages = set()
        self.set_downloader(downloader)

    @classmethod
    def _match_valid_url(cls, url):
        if cls._VALID_URL is False:
            return None
        if '_VALID_URL_RE' not in cls.__dict__:
            cls._VALID_URL_RE = tuple(map(re.compile, variadic(cls._VALID_URL)))
        return next(filter(None, (regex.match(url) for regex in cls._VALID_URL_RE)), None)

    @classmethod
    def suitable(cls, url):
        return cls._match_valid_url(url) is not None

    @classmethod
    def _match_id(cls, url):
        return cls._match_valid_url(url).group('id')

    @classmethod
    def get_temp_id(cls, url):
        try:
            return cls._match_id(url)
        except (IndexError, AttributeError):
            return None

    @classmethod
    def working(cls):
        return cls._WORKING

    @classmethod
    def supports_login(cls):
        return bool(cls._NETRC_MACHINE)

    def initialize(self):
        self._printed_messages = set()
        self._initialize_geo_bypass({
            'countries': self._GEO_COUNTRIES,
            'ip_blocks': self._GEO_IP_BLOCKS,
        })
        if not self._ready:
            self._initialize_pre_login()
            if self.supports_login():
                username, password = self._get_login_info()
                if username:
                    self._perform_login(username, password)
            elif self.get_param('username') and False not in (self.IE_DESC, self._NETRC_MACHINE):
                self.report_warning('Login with password is not supported for this website. {0}'.format(self._login_hint("cookies")))
            self._real_initialize()
            self._ready = True

    def _initialize_geo_bypass(self, geo_bypass_context):
        if not self._x_forwarded_for_ip:
            if not self.get_param('geo_bypass', True):
                return
            if not geo_bypass_context:
                geo_bypass_context = {}
            if isinstance(geo_bypass_context, (list, tuple)):
                geo_bypass_context = {
                    'countries': geo_bypass_context,
                }
            ip_block = self.get_param('geo_bypass_ip_block', None)
            if not ip_block:
                ip_blocks = geo_bypass_context.get('ip_blocks')
                if self._GEO_BYPASS and ip_blocks:
                    ip_block = random.choice(ip_blocks)
            if ip_block:
                self._x_forwarded_for_ip = GeoUtils.random_ipv4(ip_block)
                self.write_debug('Using fake IP {0} as X-Forwarded-For'.format(self._x_forwarded_for_ip))
                return
            country = self.get_param('geo_bypass_country', None)
            if not country:
                countries = geo_bypass_context.get('countries')
                if self._GEO_BYPASS and countries:
                    country = random.choice(countries)
            if country:
                self._x_forwarded_for_ip = GeoUtils.random_ipv4(country)
                self._downloader.write_debug(
                    'Using fake IP {0} ({1}) as X-Forwarded-For'.format(self._x_forwarded_for_ip, country.upper()))

    def extract(self, url):
        try:
            for _ in range(2):
                try:
                    self.initialize()
                    self.to_screen('Extracting URL: %s' % (
                        url if self.get_param('verbose') else truncate_string(url, 100, 20)))
                    ie_result = self._real_extract(url)
                    if ie_result is None:
                        return None
                    if self._x_forwarded_for_ip:
                        ie_result['__x_forwarded_for_ip'] = self._x_forwarded_for_ip
                    subtitles = ie_result.get('subtitles') or {}
                    if 'no-live-chat' in self.get_param('compat_opts'):
                        for lang in ('live_chat', 'comments', 'danmaku'):
                            subtitles.pop(lang, None)
                    return ie_result
                except GeoRestrictedError as e:
                    if self.__maybe_fake_ip_and_retry(e.countries):
                        continue
                    raise
        except UnsupportedError:
            raise
        except ExtractorError as e:
            e.video_id = e.video_id or self.get_temp_id(url)
            e.ie = e.ie or self.IE_NAME
            e.traceback = e.traceback or sys.exc_info()[2]
            raise
        except IncompleteRead as e:
            raise ExtractorError('A network error has occurred.', cause=e, expected=True, video_id=self.get_temp_id(url))
        except (KeyError, StopIteration) as e:
            raise ExtractorError('An extractor error has occurred.', cause=e, video_id=self.get_temp_id(url))

    def __maybe_fake_ip_and_retry(self, countries):
        if (not self.get_param('geo_bypass_country', None)
                and self._GEO_BYPASS
                and self.get_param('geo_bypass', True)
                and not self._x_forwarded_for_ip
                and countries):
            country_code = random.choice(countries)
            self._x_forwarded_for_ip = GeoUtils.random_ipv4(country_code)
            if self._x_forwarded_for_ip:
                self.report_warning(
                    'Video is geo restricted. Retrying extraction with fake IP {0} ({1}) as X-Forwarded-For.'.format(self._x_forwarded_for_ip, country_code.upper()))
                return True
        return False

    def set_downloader(self, downloader):
        self._downloader = downloader

    @property
    def cache(self):
        return self._downloader.cache

    @property
    def cookiejar(self):
        return self._downloader.cookiejar

    def _initialize_pre_login(self):
        pass

    def _perform_login(self, username, password):
        pass

    def _real_initialize(self):
        pass

    def _real_extract(self, url):
        raise NotImplementedError('This method must be implemented by subclasses')

    @classmethod
    def ie_key(cls):
        return cls.__name__[:-2]

    @classproperty
    def IE_NAME(cls):
        return cls.__name__[:-2]

    @staticmethod
    def __can_accept_status_code(err, expected_status):
        assert isinstance(err, HTTPError)
        if expected_status is None:
            return False
        elif callable(expected_status):
            return expected_status(err.status) is True
        else:
            return err.status in variadic(expected_status)

    def _create_request(self, url_or_request, data=None, headers=None, query=None, extensions=None):
        if isinstance(url_or_request, urllib_request.Request):
            self._downloader.deprecation_warning(
                'Passing a urllib.request.Request to _create_request() is deprecated. '
                'Use yt_dlp.networking.common.Request instead.')
            url_or_request = urllib_req_to_req(url_or_request)
        elif not isinstance(url_or_request, Request):
            url_or_request = Request(url_or_request)

        url_or_request.update(data=data, headers=headers, query=query, extensions=extensions)
        return url_or_request

    def _request_webpage(self, url_or_request, video_id, note=None, errnote=None, fatal=True, data=None,
                         headers=None, query=None, expected_status=None, impersonate=None, require_impersonation=False):
        if not self._downloader._first_webpage_request:
            sleep_interval = self.get_param('sleep_interval_requests') or 0
            if sleep_interval > 0:
                self.to_screen('Sleeping {0} seconds ...'.format(sleep_interval))
                time.sleep(sleep_interval)
        else:
            self._downloader._first_webpage_request = False

        if note is None:
            self.report_download_webpage(video_id)
        elif note is not False:
            if video_id is None:
                self.to_screen(str(note))
            else:
                self.to_screen('{0}: {1}'.format(video_id, note))

        if self._x_forwarded_for_ip:
            headers = (headers or {}).copy()
            headers.setdefault('X-Forwarded-For', self._x_forwarded_for_ip)

        extensions = {}

        available_target, requested_targets = self._downloader._parse_impersonate_targets(impersonate)
        if available_target:
            extensions['impersonate'] = available_target
        elif requested_targets:
            msg = 'The extractor is attempting impersonation'
            if require_impersonation:
                raise ExtractorError(
                    self._downloader._unavailable_targets_message(requested_targets, note=msg, is_error=True),
                    expected=True)
            self.report_warning(
                self._downloader._unavailable_targets_message(requested_targets, note=msg), only_once=True)

        try:
            return self._downloader.urlopen(self._create_request(url_or_request, data, headers, query, extensions))
        except network_exceptions as err:
            if isinstance(err, HTTPError):
                if self.__can_accept_status_code(err, expected_status):
                    return err.response

            if errnote is False:
                return False
            if errnote is None:
                errnote = 'Unable to download webpage'

            errmsg = '{0}: {1}'.format(errnote, err)
            if fatal:
                raise ExtractorError(errmsg, cause=err)
            else:
                self.report_warning(errmsg)
                return False

    def _download_webpage_handle(self, url_or_request, video_id, note=None, errnote=None, fatal=True,
                                 encoding=None, data=None, headers={}, query={}, expected_status=None,
                                 impersonate=None, require_impersonation=False):
        if isinstance(url_or_request, str):
            url_or_request = url_or_request.partition('#')[0]

        urlh = self._request_webpage(url_or_request, video_id, note, errnote, fatal, data=data,
                                     headers=headers, query=query, expected_status=expected_status,
                                     impersonate=impersonate, require_impersonation=require_impersonation)
        if urlh is False:
            assert not fatal
            return False
        content = self._webpage_read_content(urlh, url_or_request, video_id, note, errnote, fatal,
                                             encoding=encoding, data=data)
        if content is False:
            assert not fatal
            return False
        return (content, urlh)

    @staticmethod
    def _guess_encoding_from_content(content_type, webpage_bytes):
        m = re.match(r'[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+\s*;\s*charset=(.+)', content_type)
        if m:
            encoding = m.group(1)
        else:
            m = re.search(br'<meta[^>]+charset=[\'"]?([^\'")]+)[ /\'">]',
                          webpage_bytes[:1024])
            if m:
                encoding = m.group(1).decode('ascii')
            elif webpage_bytes.startswith(b'\xff\xfe'):
                encoding = 'utf-16'
            else:
                encoding = 'utf-8'

        return encoding

    def __check_blocked(self, content):
        first_block = content[:512]
        if ('<title>Access to this site is blocked</title>' in content
                and 'Websense' in first_block):
            msg = 'Access to this webpage has been blocked by Websense filtering software in your network.'
            blocked_iframe = self._html_search_regex(
                r'<iframe src="([^"]+)"', content,
                'Websense information URL', default=None)
            if blocked_iframe:
                msg += ' Visit {0} for more details'.format(blocked_iframe)
            raise ExtractorError(msg, expected=True)
        if '<title>The URL you requested has been blocked</title>' in first_block:
            msg = (
                'Access to this webpage has been blocked by Indian censorship. '
                'Use a VPN or proxy server (with --proxy) to route around it.')
            block_msg = self._html_search_regex(
                r'</h1><p>(.*?)</p>',
                content, 'block message', default=None)
            if block_msg:
                msg += ' (Message: "{0}")'.format(block_msg.replace('\n', ' '))
            raise ExtractorError(msg, expected=True)
        if ('<title>TTK :: Доступ к ресурсу ограничен</title>' in content
                and 'blocklist.rkn.gov.ru' in content):
            raise ExtractorError(
                'Access to this webpage has been blocked by decision of the Russian government. '
                'Visit http://blocklist.rkn.gov.ru/ for a block reason.',
                expected=True)

    def __decode_webpage(self, webpage_bytes, encoding, headers):
        if not encoding:
            encoding = self._guess_encoding_from_content(headers.get('Content-Type', ''), webpage_bytes)
        try:
            return webpage_bytes.decode(encoding, 'replace')
        except LookupError:
            return webpage_bytes.decode('utf-8', 'replace')

    def _webpage_read_content(self, urlh, url_or_request, video_id, note=None, errnote=None, fatal=True,
                              prefix=None, encoding=None, data=None):
        try:
            webpage_bytes = urlh.read()
        except TransportError as err:
            errmsg = '{0}: Error reading response: {1}'.format(video_id, err.msg)
            if fatal:
                raise ExtractorError(errmsg, cause=err)
            self.report_warning(errmsg)
            return False

        if prefix is not None:
            webpage_bytes = prefix + webpage_bytes
        if self.get_param('dump_intermediate_pages', False):
            self.to_screen('Dumping request to ' + urlh.geturl())
            dump = base64.b64encode(webpage_bytes).decode('ascii')
            self._downloader.to_screen(dump)
        if self.get_param('write_pages'):
            if isinstance(url_or_request, Request):
                data = self._create_request(url_or_request, data).data
            filename = _request_dump_filename(
                urlh.geturl(), video_id, data,
                trim_length=self.get_param('trim_file_name'))
            self.to_screen('Saving request to {0}'.format(filename))
            with open(filename, 'wb') as outf:
                outf.write(webpage_bytes)

        content = self.__decode_webpage(webpage_bytes, encoding, urlh.headers)
        self.__check_blocked(content)

        return content

    def __print_error(self, errnote, fatal, video_id, err):
        if fatal:
            raise ExtractorError('{0}: {1}'.format(video_id, errnote), cause=err)
        elif errnote:
            self.report_warning('{0}: {1}: {2}'.format(video_id, errnote, err))

    def _parse_xml(self, xml_string, video_id, transform_source=None, fatal=True, errnote=None):
        if transform_source:
            xml_string = transform_source(xml_string)
        try:
            return compat_etree_fromstring(xml_string.encode())
        except xml.etree.ElementTree.ParseError as ve:
            self.__print_error('Failed to parse XML' if errnote is None else errnote, fatal, video_id, ve)

    def _parse_json(self, json_string, video_id, transform_source=None, fatal=True, errnote=None, **parser_kwargs):
        try:
            return json.loads(
                json_string, cls=LenientJSONDecoder, strict=False, transform_source=transform_source, **parser_kwargs)
        except ValueError as ve:
            self.__print_error('Failed to parse JSON' if errnote is None else errnote, fatal, video_id, ve)

    def _parse_socket_response_as_json(self, data, *args, **kwargs):
        return self._parse_json(data[data.find('{'):data.rfind('}') + 1], *args, **kwargs)

    def __create_download_methods(name, parser, note, errnote, return_value):
        ...
    # ... (the rest of the file is omitted for brevity)
