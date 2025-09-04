# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import abc
import copy
import functools

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import NO_DEFAULT, bug_reports_message, classproperty, traverse_obj, cached_property
from yt_dlp.version import __version__
from ._provider import IEContentProvider, IEContentProviderError, register_provider_generic, register_preference_generic
from ._registry import _pot_providers, _ptp_preferences
from ...compat._legacy import compat_urllib_parse as urllib_parse
from ...compat._legacy import compat_dataclasses as dataclasses
from ...networking import Request, Response
from ...cookies import YoutubeDLCookieJar
from ...utils.networking import HTTPHeaderDict


class PoTokenContext(object):
    GVS = u'gvs'
    PLAYER = u'player'
    SUBS = u'subs'


class PoTokenRequest(object):
    context = None
    innertube_context = None
    innertube_host = None
    session_index = None
    player_url = None
    is_authenticated = False
    video_webpage = None
    internal_client_name = None
    visitor_data = None
    data_sync_id = None
    video_id = None
    request_cookiejar = None
    request_proxy = None
    request_headers = None
    request_timeout = None
    request_source_address = None
    request_verify_tls = True
    bypass_cache = False

    def __init__(self, context, innertube_context, innertube_host=None, session_index=None,
                 player_url=None, is_authenticated=False, video_webpage=None,
                 internal_client_name=None, visitor_data=None, data_sync_id=None,
                 video_id=None, request_cookiejar=None, request_proxy=None,
                 request_headers=None, request_timeout=None, request_source_address=None,
                 request_verify_tls=True, bypass_cache=False):
        self.context = context
        self.innertube_context = innertube_context
        self.innertube_host = innertube_host
        self.session_index = session_index
        self.player_url = player_url
        self.is_authenticated = is_authenticated
        self.video_webpage = video_webpage
        self.internal_client_name = internal_client_name
        self.visitor_data = visitor_data
        self.data_sync_id = data_sync_id
        self.video_id = video_id
        self.request_cookiejar = request_cookiejar or YoutubeDLCookieJar()
        self.request_proxy = request_proxy
        self.request_headers = request_headers or HTTPHeaderDict()
        self.request_timeout = request_timeout
        self.request_source_address = request_source_address
        self.request_verify_tls = request_verify_tls
        self.bypass_cache = bypass_cache

    def copy(self):
        return dataclasses.replace(
            self,
            request_headers=HTTPHeaderDict(self.request_headers),
            innertube_context=copy.deepcopy(self.innertube_context),
        )


PoTokenRequest = dataclasses.dataclass(PoTokenRequest)

class PoTokenResponse(object):
    po_token = None
    expires_at = None

    def __init__(self, po_token, expires_at=None):
        self.po_token = po_token
        self.expires_at = expires_at


PoTokenResponse = dataclasses.dataclass(PoTokenResponse)

class PoTokenProviderRejectedRequest(IEContentProviderError):
    u"""Reject the PoTokenRequest (cannot handle the request)"""


class PoTokenProviderError(IEContentProviderError):
    u"""An error occurred while fetching a PO Token"""


class ExternalRequestFeature(object):
    PROXY_SCHEME_HTTP = 1
    PROXY_SCHEME_HTTPS = 2
    PROXY_SCHEME_SOCKS4 = 3
    PROXY_SCHEME_SOCKS4A = 4
    PROXY_SCHEME_SOCKS5 = 5
    PROXY_SCHEME_SOCKS5H = 6
    SOURCE_ADDRESS = 7
    DISABLE_TLS_VERIFICATION = 8


class PoTokenProvider(IEContentProvider):
    __metaclass__ = abc.ABCMeta
    _PROVIDER_KEY_SUFFIX = u'PTP'

    _SUPPORTED_CONTEXTS = ()
    _SUPPORTED_CLIENTS = ()
    _SUPPORTED_EXTERNAL_REQUEST_FEATURES = ()

    def __validate_request(self, request):
        if not self.is_available():
            raise PoTokenProviderRejectedRequest(u'{0} is not available'.format(self.PROVIDER_NAME))

        if (
            self._SUPPORTED_CONTEXTS is not None
            and request.context not in self._SUPPORTED_CONTEXTS
        ):
            raise PoTokenProviderRejectedRequest(
                u'PO Token Context "{0}" is not supported by {1}'.format(request.context, self.PROVIDER_NAME))

        if self._SUPPORTED_CLIENTS is not None:
            client_name = traverse_obj(
                request.innertube_context, (u'client', u'clientName'))
            if client_name not in self._SUPPORTED_CLIENTS:
                raise PoTokenProviderRejectedRequest(
                    u'Client "{0}" is not supported by {1}. Supported clients: {2}'.format(
                        client_name, self.PROVIDER_NAME, u", ".join(self._SUPPORTED_CLIENTS) or u"none"))

        self.__validate_external_request_features(request)

    @cached_property
    def _supported_proxy_schemes(self):
        return dict((
            scheme, feature)
            for scheme, feature in {
                u'http': ExternalRequestFeature.PROXY_SCHEME_HTTP,
                u'https': ExternalRequestFeature.PROXY_SCHEME_HTTPS,
                u'socks4': ExternalRequestFeature.PROXY_SCHEME_SOCKS4,
                u'socks4a': ExternalRequestFeature.PROXY_SCHEME_SOCKS4A,
                u'socks5': ExternalRequestFeature.PROXY_SCHEME_SOCKS5,
                u'socks5h': ExternalRequestFeature.PROXY_SCHEME_SOCKS5H,
            }.items()
            if feature in (self._SUPPORTED_EXTERNAL_REQUEST_FEATURES or []))

    def __validate_external_request_features(self, request):
        if self._SUPPORTED_EXTERNAL_REQUEST_FEATURES is None:
            return

        if request.request_proxy:
            scheme = urllib_parse.urlparse(request.request_proxy).scheme
            if scheme.lower() not in self._supported_proxy_schemes:
                raise PoTokenProviderRejectedRequest(
                    u'External requests by "{0}" provider do not support proxy scheme "{1}". Supported proxy schemes: {2}'.format(
                        self.PROVIDER_NAME, scheme, u", ".join(self._supported_proxy_schemes) or u"none"))

        if (
            request.request_source_address
            and ExternalRequestFeature.SOURCE_ADDRESS not in self._SUPPORTED_EXTERNAL_REQUEST_FEATURES
        ):
            raise PoTokenProviderRejectedRequest(
                u'External requests by "{0}" provider do not support setting source address'.format(self.PROVIDER_NAME))

        if (
            not request.request_verify_tls
            and ExternalRequestFeature.DISABLE_TLS_VERIFICATION not in self._SUPPORTED_EXTERNAL_REQUEST_FEATURES
        ):
            raise PoTokenProviderRejectedRequest(
                u'External requests by "{0}" provider do not support ignoring TLS certificate failures'.format(self.PROVIDER_NAME))

    def request_pot(self, request):
        self.__validate_request(request)
        return self._real_request_pot(request)

    @abc.abstractmethod
    def _real_request_pot(self, request):
        u"""To be implemented by subclasses"""
        pass

    def _request_webpage(self, request, pot_request=None, note=None, **kwargs):
        req = request.copy()

        if pot_request is not None:
            req.headers = HTTPHeaderDict(pot_request.request_headers, req.headers)
            req.proxies = req.proxies or ({u'all': pot_request.request_proxy} if pot_request.request_proxy else {})

            if pot_request.request_cookiejar is not None:
                req.extensions[u'cookiejar'] = req.extensions.get(u'cookiejar', pot_request.request_cookiejar)

        if note is not False:
            self.logger.info(unicode(note) if note else u'Requesting webpage')
        return self.ie._downloader.urlopen(req)


def register_provider(provider):
    u"""Register a PoTokenProvider class"""
    return register_provider_generic(
        provider=provider,
        base_class=PoTokenProvider,
        registry=_pot_providers.value,
    )


def provider_bug_report_message(provider, before=u';'):
    msg = provider.BUG_REPORT_MESSAGE

    before = before.rstrip()
    if not before or before.endswith((u'.', u'!', u'?')):
        msg = msg[0].title() + msg[1:]

    return u'{0} {1}'.format(before, msg) if before else msg


def register_preference(*providers):
    u"""Register a preference for a PoTokenProvider"""
    return register_preference_generic(
        PoTokenProvider,
        _ptp_preferences.value,
        *providers,
    )
