# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import base64
import binascii
import calendar
import codecs
import collections
import contextlib
import datetime as dt
import email.header
import email.utils
import errno
import functools
import hashlib
import hmac
import inspect
import io
import itertools
import json
import locale
import math
import mimetypes
import netrc
import operator
import os
import platform
import random
import re
import shlex
import socket
import ssl
import struct
import subprocess
import sys
import tempfile
import time
import traceback
import types
import unicodedata
import xml.etree.ElementTree
from ..dependencies import enum

from . import traversal

from ..compat._legacy import (
    compat_etree_fromstring,
    compat_expanduser,
    compat_HTMLParseError,
    compat_urllib_parse as urllib_parse,
    compat_urllib_request as urllib_request,
    compat_urllib_error as urllib_error,
    compat_html_entities as html_entities,
    compat_html_parser as html_parser,
)
from ..dependencies import xattr
from ..globals import IN_CLI, WINDOWS_VT_MODE

__name__ = __name__.rsplit('.', 1)[0]  # noqa: A001 # Pretend to be the parent module


class NO_DEFAULT(object):
    pass


def IDENTITY(x):
    return x


ENGLISH_MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December']

MONTH_NAMES = {
    'en': ENGLISH_MONTH_NAMES,
    'fr': [
        'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'],
    'pl': ['stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca',
           'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia'],
}

TIMEZONE_NAMES = {
    'UT': 0, 'UTC': 0, 'GMT': 0, 'Z': 0,
    'AST': -4, 'ADT': -3,
    'EST': -5, 'EDT': -4,
    'CST': -6, 'CDT': -5,
    'MST': -7, 'MDT': -6,
    'PST': -8, 'PDT': -7,
}

ACCENT_CHARS = dict(zip('ÂÃÄÀÁÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖŐØŒÙÚÛÜŰÝÞßàáâãäåæçèéêëìíîïðñòóôõöőøœùúûüűýþÿ',
                        itertools.chain('AAAAAA', ['AE'], 'CEEEEIIIIDNOOOOOOO', ['OE'], 'UUUUUY', ['TH', 'ss'],
                                        'aaaaaa', ['ae'], 'ceeeeiiiionooooooo', ['oe'], 'uuuuuy', ['th'], 'y')))

DATE_FORMATS = (
    '%d %B %Y', '%d %b %Y', '%B %d %Y', '%B %dst %Y', '%B %dnd %Y', '%B %drd %Y', '%B %dth %Y',
    '%b %d %Y', '%b %dst %Y', '%b %dnd %Y', '%b %drd %Y', '%b %dth %Y', '%b %dst %Y %I:%M',
    '%b %dnd %Y %I:%M', '%b %drd %Y %I:%M', '%b %dth %Y %I:%M', '%Y %m %d', '%Y-%m-%d',
    '%Y.%m.%d.', '%Y/%m/%d', '%Y/%m/%d %H:%M', '%Y/%m/%d %H:%M:%S', '%Y%m%d%H%M', '%Y%m%d%H%M%S',
    '%Y%m%d', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S:%f',
    '%d.%m.%Y %H:%M', '%d.%m.%Y %H.%M', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ',
    '%Y-%m-%dT%H:%M:%S.%f0Z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M',
    '%b %d %Y at %H:%M', '%b %d %Y at %H:%M:%S', '%B %d %Y at %H:%M', '%B %d %Y at %H:%M:%S',
    '%H:%M %d-%b-%Y',
)

DATE_FORMATS_DAY_FIRST = list(DATE_FORMATS)
DATE_FORMATS_DAY_FIRST.extend([
    '%d-%m-%Y', '%d.%m.%Y', '%d.%m.%y', '%d/%m/%Y', '%d/%m/%y', '%d/%m/%Y %H:%M:%S',
    '%d-%m-%Y %H:%M', '%H:%M %d/%m/%Y',
])

DATE_FORMATS_MONTH_FIRST = list(DATE_FORMATS)
DATE_FORMATS_MONTH_FIRST.extend([
    '%m-%d-%Y', '%m.%d.%Y', '%m/%d/%Y', '%m/%d/%y', '%m/%d/%Y %H:%M:%S',
])

PACKED_CODES_RE = r"}\('(.+)',(\d+),(\d+),'([^']+)'\.split\('\|'\)"
JSON_LD_RE = r'(?is)<script[^>]+type=(["\']?)application/ld\+json\1[^>]*>\s*(?P<json_ld>{.+?}|\[.+?\])\s*</script>'
NUMBER_RE = r'\d+(?:\.\d+)?'


def _functools_cache(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper


@_functools_cache
def preferredencoding():
    try:
        pref = locale.getpreferredencoding()
        'TEST'.encode(pref)
    except Exception:
        pref = 'UTF-8'
    return pref


def write_json_file(obj, fn):
    tf = tempfile.NamedTemporaryFile(
        prefix='{0}.'.format(os.path.basename(fn)), dir=os.path.dirname(fn),
        suffix='.tmp', delete=False, mode='w', encoding='utf-8')
    try:
        with tf:
            json.dump(obj, tf, ensure_ascii=False)
        if sys.platform == 'win32':
            with contextlib.suppress(OSError):
                os.unlink(fn)
        with contextlib.suppress(OSError):
            mask = os.umask(0)
            os.umask(mask)
            os.chmod(tf.name, 0o666 & ~mask)
        os.rename(tf.name, fn)
    except Exception:
        with contextlib.suppress(OSError):
            os.remove(tf.name)
        raise


def _getargspec(func):
    if sys.version_info >= (3, 0):
        return inspect.getfullargspec(func)
    return inspect.getargspec(func)


def partial_application(func):
    argspec = _getargspec(func)
    required_args = argspec.args[:-len(argspec.defaults or [])]

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if set(required_args[len(args):]).difference(kwargs.keys()):
            return functools.partial(func, *args, **kwargs)
        return func(*args, **kwargs)
    return wrapped


def find_xpath_attr(node, xpath, key, val=None):
    assert re.match(r'^[a-zA-Z_-]+$', key)
    expr = xpath + ('[@{0}]'.format(key) if val is None else "[@{0}='{1}']".format(key, val))
    return node.find(expr)


def xpath_with_ns(path, ns_map):
    components = [c.split(':') for c in path.split('/')]
    replaced = []
    for c in components:
        if len(c) == 1:
            replaced.append(c[0])
        else:
            ns, tag = c
            replaced.append('{{{0}}}{1}'.format(ns_map[ns], tag))
    return '/'.join(replaced)


def xpath_element(node, xpath, name=None, fatal=False, default=NO_DEFAULT):
    def _find_xpath(xpath):
        return node.find(xpath)

    if isinstance(xpath, str):
        n = _find_xpath(xpath)
    else:
        for xp in xpath:
            n = _find_xpath(xp)
            if n is not None:
                break

    if n is None:
        if default is not NO_DEFAULT:
            return default
        elif fatal:
            name = xpath if name is None else name
            raise ExtractorError('Could not find XML element {0}'.format(name))
        else:
            return None
    return n


def xpath_text(node, xpath, name=None, fatal=False, default=NO_DEFAULT):
    n = xpath_element(node, xpath, name, fatal=fatal, default=default)
    if n is None or n == default:
        return n
    if n.text is None:
        if default is not NO_DEFAULT:
            return default
        elif fatal:
            name = xpath if name is None else name
            raise ExtractorError('Could not find XML element\'s text {0}'.format(name))
        else:
            return None
    return n.text


def xpath_attr(node, xpath, key, name=None, fatal=False, default=NO_DEFAULT):
    n = find_xpath_attr(node, xpath, key)
    if n is None:
        if default is not NO_DEFAULT:
            return default
        elif fatal:
            name = '{0}[@{1}]'.format(xpath, key) if name is None else name
            raise ExtractorError('Could not find XML attribute {0}'.format(name))
        else:
            return None
    return n.attrib[key]


def get_element_by_id(id, html, **kwargs):
    return get_element_by_attribute('id', id, html, **kwargs)


def get_element_html_by_id(id, html, **kwargs):
    return get_element_html_by_attribute('id', id, html, **kwargs)


def get_element_by_class(class_name, html):
    retval = get_elements_by_class(class_name, html)
    return retval[0] if retval else None


def get_element_html_by_class(class_name, html):
    retval = get_elements_html_by_class(class_name, html)
    return retval[0] if retval else None


def get_element_by_attribute(attribute, value, html, **kwargs):
    retval = get_elements_by_attribute(attribute, value, html, **kwargs)
    return retval[0] if retval else None


def get_element_html_by_attribute(attribute, value, html, **kargs):
    retval = get_elements_html_by_attribute(attribute, value, html, **kargs)
    return retval[0] if retval else None


def get_elements_by_class(class_name, html, **kargs):
    return get_elements_by_attribute(
        'class', r'[^\'"]*(?<=[\'"\s]){re.escape(class_name)}(?=[\'"\s])[^\'"]*'.format(re=re),
        html, escape_value=False)


def get_elements_html_by_class(class_name, html):
    return get_elements_html_by_attribute(
        'class', r'[^\'"]*(?<=[\'"\s]){re.escape(class_name)}(?=[\'"\s])[^\'"]*'.format(re=re),
        html, escape_value=False)


def get_elements_by_attribute(*args, **kwargs):
    return [content for content, _ in get_elements_text_and_html_by_attribute(*args, **kwargs)]


def get_elements_html_by_attribute(*args, **kwargs):
    return [whole for _, whole in get_elements_text_and_html_by_attribute(*args, **kwargs)]


def get_elements_text_and_html_by_attribute(attribute, value, html, **kargs):
    tag = kargs.get('tag', r'[\w:.-]+')
    escape_value = kargs.get('escape_value', True)
    if not value:
        return

    quote = '' if re.match(r'''[\s"'`=<>]''', value) else '?'
    value = re.escape(value) if escape_value else value
    partial_element_re = (
        r'''(?x)
        <(?P<tag>{tag})
         (?:\s(?:[^>"']|"[^"]*"|'[^']*')*)?
         \s{attr}\s*=\s*(?P<_q>['"]{quote})'''.format(
            tag=tag, attr=re.escape(attribute), quote=quote)
        + '(?-x:' + value + ')(?P=_q)'
    )
    for m in re.finditer(partial_element_re, html):
        content, whole = get_element_text_and_html_by_tag(m.group('tag'), html[m.start():])
        yield (
            unescapeHTML(re.sub(r'^(?P<q>["\'])(?P<content>.*)(?P=q)$', r'\g<content>', content, flags=re.DOTALL)),
            whole,
        )


class HTMLBreakOnClosingTagParser(html_parser.HTMLParser):
    class HTMLBreakOnClosingTagException(Exception):
        pass

    def __init__(self):
        self.tagstack = collections.deque()
        html_parser.HTMLParser.__init__(self)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        pass

    def handle_starttag(self, tag, _):
        self.tagstack.append(tag)

    def handle_endtag(self, tag):
        if not self.tagstack:
            raise compat_HTMLParseError('no tags in the stack')
        while self.tagstack:
            inner_tag = self.tagstack.pop()
            if inner_tag == tag:
                break
        else:
            raise compat_HTMLParseError('matching opening tag for closing {0} tag not found'.format(tag))
        if not self.tagstack:
            raise self.HTMLBreakOnClosingTagException


def get_element_text_and_html_by_tag(tag, html):
    def find_or_raise(haystack, needle, exc):
        try:
            return haystack.index(needle)
        except ValueError:
            raise exc
    closing_tag = '</{0}>'.format(tag)
    whole_start = find_or_raise(
        html, '<{0}'.format(tag), compat_HTMLParseError('opening {0} tag not found'.format(tag)))
    content_start = find_or_raise(
        html[whole_start:], '>', compat_HTMLParseError('malformed opening {0} tag'.format(tag)))
    content_start += whole_start + 1
    with HTMLBreakOnClosingTagParser() as parser:
        parser.feed(html[whole_start:content_start])
        if not parser.tagstack or parser.tagstack[0] != tag:
            raise compat_HTMLParseError('parser did not match opening {0} tag'.format(tag))
        offset = content_start
        while offset < len(html):
            next_closing_tag_start = find_or_raise(
                html[offset:], closing_tag,
                compat_HTMLParseError('closing {0} tag not found'.format(tag)))
            next_closing_tag_end = next_closing_tag_start + len(closing_tag)
            try:
                parser.feed(html[offset:offset + next_closing_tag_end])
                offset += next_closing_tag_end
            except HTMLBreakOnClosingTagParser.HTMLBreakOnClosingTagException:
                return html[content_start:offset + next_closing_tag_start], \
                    html[whole_start:offset + next_closing_tag_end]
        raise compat_HTMLParseError('unexpected end of html')


class HTMLAttributeParser(html_parser.HTMLParser):
    def __init__(self):
        self.attrs = {}
        html_parser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)
        raise compat_HTMLParseError('done')


class HTMLListAttrsParser(html_parser.HTMLParser):
    def __init__(self):
        html_parser.HTMLParser.__init__(self)
        self.items = []
        self._level = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'li' and self._level == 0:
            self.items.append(dict(attrs))
        self._level += 1

    def handle_endtag(self, tag):
        self._level -= 1


def extract_attributes(html_element):
    parser = HTMLAttributeParser()
    with contextlib.suppress(compat_HTMLParseError):
        parser.feed(html_element)
        parser.close()
    return parser.attrs


def parse_list(webpage):
    parser = HTMLListAttrsParser()
    parser.feed(webpage)
    parser.close()
    return parser.items


def clean_html(html):
    if html is None:
        return html
    html = re.sub(r'\s+', ' ', html)
    html = re.sub(r'(?u)\s?<\s?br\s?/?\s?>\s?', '\n', html)
    html = re.sub(r'(?u)<\s?/\s?p\s?>\s?<\s?p[^>]*>', '\n', html)
    html = re.sub('<.*?>', '', html)
    html = unescapeHTML(html)
    return html.strip()


class LenientJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        self.transform_source = kwargs.pop('transform_source', None)
        self.ignore_extra = kwargs.pop('ignore_extra', False)
        self._close_objects = kwargs.pop('close_objects', 0)
        self._close_attempts = 2 * self._close_objects
        super(LenientJSONDecoder, self).__init__(*args, **kwargs)

    @staticmethod
    def _close_object(err):
        doc = err.doc[:err.pos]
        if err.msg.startswith('Expecting \','):
            return doc + ','
        elif not doc.endswith(','):
            return

        if err.msg.startswith('Expecting property name'):
            return doc[:-1] + '}'
        elif err.msg.startswith('Expecting value'):
            return doc[:-1] + ']'

    def decode(self, s):
        if self.transform_source:
            s = self.transform_source(s)
        for attempt in range(self._close_attempts + 1):
            try:
                if self.ignore_extra:
                    return self.raw_decode(s.lstrip())[0]
                return super(LenientJSONDecoder, self).decode(s)
            except json.JSONDecodeError as e:
                if e.pos is None:
                    raise
                elif attempt < self._close_attempts:
                    s = self._close_object(e)
                    if s is not None:
                        continue
                raise type(e)('{0} in {1!r}'.format(e.msg, s[e.pos - 10:e.pos + 10]), s, e.pos)
        assert False, 'Too many attempts to decode JSON'


def sanitize_open(filename, open_mode):
    if filename == '-':
        if sys.platform == 'win32':
            import msvcrt
            with contextlib.suppress(io.UnsupportedOperation):
                msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        return (sys.stdout.buffer if hasattr(sys.stdout, 'buffer') else sys.stdout, filename)

    for attempt in range(2):
        try:
            try:
                if sys.platform == 'win32':
                    raise LockingUnsupportedError
                stream = locked_file(filename, open_mode, block=False).__enter__()
            except OSError:
                stream = open(filename, open_mode)
            return stream, filename
        except OSError as err:
            if attempt or err.errno in (errno.EACCES,):
                raise
            old_filename, filename = filename, sanitize_path(filename)
            if old_filename == filename:
                raise


def timeconvert(timestr):
    timestamp = None
    timetuple = email.utils.parsedate_tz(timestr)
    if timetuple is not None:
        timestamp = email.utils.mktime_tz(timetuple)
    return timestamp


def sanitize_filename(s, restricted=False, is_id=NO_DEFAULT):
    if s == '':
        return ''

    def replace_insane(char):
        if restricted and char in ACCENT_CHARS:
            return ACCENT_CHARS[char]
        elif not restricted and char == '\n':
            return '\0 '
        elif is_id is NO_DEFAULT and not restricted and char in '"*:<>?|/\\':
            return {'/': '\u29F8', '\\': '\u29f9'}.get(char, unichr(ord(char) + 0xfee0))
        elif char == '?' or ord(char) < 32 or ord(char) == 127:
            return ''
        elif char == '"':
            return '' if restricted else '\''
        elif char == ':':
            return '\0_\0-' if restricted else '\0 \0-'
        elif char in '\\/|*<>':
            return '\0_'
        if restricted and (char in '!&\'()[]{}$;`^,#' or char.isspace() or ord(char) > 127):
            return '' if unicodedata.category(char)[0] in 'CM' else '\0_'
        return char

    if restricted and (is_id is NO_DEFAULT or not is_id):
        s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'[0-9]+(?::[0-9]+)+', lambda m: m.group(0).replace(':', '_'), s)
    result = ''.join(map(replace_insane, s))
    if is_id is NO_DEFAULT:
        result = re.sub(r'(\0.)(?:(?=\1)..)+', r'\1', result)
        STRIP_RE = r'(?:\0.|[ _-])*'
        result = re.sub(r'^\0.{0}|{0}\0.$'.format(STRIP_RE), '', result)
    result = result.replace('\0', '') or '_'

    if not is_id:
        while '__' in result:
            result = result.replace('__', '_')
        result = result.strip('_')
        if restricted and result.startswith('-_'):
            result = result[2:]
        if result.startswith('-'):
            result = '_' + result[len('-'):]
        result = result.lstrip('.')
        if not result:
            result = '_'
    return result


def _sanitize_path_parts(parts):
    sanitized_parts = []
    for part in parts:
        if not part or part == '.':
            continue
        elif part == '..':
            if sanitized_parts and sanitized_parts[-1] != '..':
                sanitized_parts.pop()
            else:
                sanitized_parts.append('..')
            continue
        sanitized_part = re.sub(r'[/<>:"\|\\?\*]|[\s.]$', '#', part)
        sanitized_parts.append(sanitized_part)
    return sanitized_parts


def sanitize_path(s, force=False):
    if sys.platform != 'win32':
        if not force:
            return s
        root = '/' if s.startswith('/') else ''
        path = '/'.join(_sanitize_path_parts(s.split('/')))
        return root + path if root or path else '.'

    normed = s.replace('/', '\\')
    if normed.startswith('\\\\'):
        parts = normed.split('\\')
        root = '\\'.join(parts[:4]) + '\\'
        parts = parts[4:]
    elif normed[1:2] == ':':
        offset = 3 if normed[2:3] == '\\' else 2
        root = normed[:offset]
        parts = normed[offset:].split('\\')
    else:
        root = '\\' if normed[:1] == '\\' else ''
        parts = normed.split('\\')

    path = '\\'.join(_sanitize_path_parts(parts))
    return root + path if root or path else '.'


def sanitize_url(url, scheme='http'):
    if url is None:
        return
    elif url.startswith('//'):
        return '{0}:{1}'.format(scheme, url)
    COMMON_TYPOS = (
        (r'^httpss://', r'https://'),
        (r'^rmtp([es]?)://', r'rtmp\1://'),
    )
    for mistake, fixup in COMMON_TYPOS:
        if re.match(mistake, url):
            return re.sub(mistake, fixup, url)
    return url


def extract_basic_auth(url):
    parts = urllib_parse.urlsplit(url)
    if parts.username is None:
        return url, None
    url = urllib_parse.urlunsplit(parts._replace(netloc=(
        parts.hostname if parts.port is None
        else '{0}:{1}'.format(parts.hostname, parts.port))))
    auth_payload = base64.b64encode(
        ('{0}:{1}'.format(parts.username, parts.password or '')).encode())
    return url, 'Basic {0}'.format(auth_payload.decode())


def expand_path(s):
    return os.path.expandvars(compat_expanduser(s))


def orderedSet(iterable, lazy=False):
    def _iter():
        seen = []
        for x in iterable:
            if x not in seen:
                seen.append(x)
                yield x
    return _iter() if lazy else list(_iter())


def _htmlentity_transform(entity_with_semicolon):
    entity = entity_with_semicolon[:-1]
    if entity in html_entities.name2codepoint:
        return unichr(html_entities.name2codepoint[entity])
    if entity_with_semicolon in html_entities.html5:
        return html_entities.html5[entity_with_semicolon]
    mobj = re.match(r'#(x[0-9a-fA-F]+|[0-9]+)', entity)
    if mobj is not None:
        numstr = mobj.group(1)
        if numstr.startswith('x'):
            base = 16
            numstr = '0{0}'.format(numstr)
        else:
            base = 10
        with contextlib.suppress(ValueError):
            return unichr(int(numstr, base))
    return '&{0};'.format(entity)


def unescapeHTML(s):
    if s is None:
        return None
    assert isinstance(s, str)
    return re.sub(
        r'&([^&;]+;)', lambda m: _htmlentity_transform(m.group(1)), s)


def escapeHTML(text):
    return (
        text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#39;')
    )


class netrc_from_content(netrc.netrc):
    def __init__(self, content):
        self.hosts, self.macros = {}, {}
        with io.StringIO(content) as stream:
            self._parse('-', stream, False)


class Popen(subprocess.Popen):
    if sys.platform == 'win32':
        _startupinfo = subprocess.STARTUPINFO()
        _startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    else:
        _startupinfo = None

    @staticmethod
    def _fix_pyinstaller_issues(env):
        if not hasattr(sys, '_MEIPASS'):
            return
        env['PYINSTALLER_RESET_ENVIRONMENT'] = '1'

        def _fix(key):
            orig = env.get('{0}_ORIG'.format(key))
            if orig is None:
                env.pop(key, None)
            else:
                env[key] = orig
        _fix('LD_LIBRARY_PATH')
        _fix('DYLD_LIBRARY_PATH')

    def __init__(self, args, *remaining, **kwargs):
        env = kwargs.get('env')
        if env is None:
            env = os.environ.copy()
            kwargs['env'] = env
        self._fix_pyinstaller_issues(env)

        text = kwargs.get('text', False)
        self.__text_mode = kwargs.get('encoding') or kwargs.get('errors') or text or kwargs.get('universal_newlines')
        if text is True:
            kwargs['universal_newlines'] = True
            kwargs.setdefault('encoding', 'utf-8')
            kwargs.setdefault('errors', 'replace')

        shell = kwargs.get('shell', False)
        if shell and os.name == 'nt' and kwargs.get('executable') is None:
            if not isinstance(args, str):
                args = shell_quote(args, shell=True)
            kwargs['shell'] = False
            env['='] = '"^\n\n"'
            args = '{0} /Q /S /D /V:OFF /E:ON /C "{1}"'.format(self.__comspec(), args)

        kwargs['startupinfo'] = self._startupinfo
        super(Popen, self).__init__(args, *remaining, **kwargs)

    def __comspec(self):
        comspec = os.environ.get('ComSpec') or os.path.join(
            os.environ.get('SystemRoot', ''), 'System32', 'cmd.exe')
        if os.path.isabs(comspec):
            return comspec
        raise FileNotFoundError('shell not found: neither %ComSpec% nor %SystemRoot% is set')

    def communicate_or_kill(self, *args, **kwargs):
        try:
            return self.communicate(*args, **kwargs)
        except BaseException:
            self.kill(timeout=None)
            raise

    def kill(self, timeout=0):
        super(Popen, self).kill()
        if timeout != 0:
            self.wait(timeout=timeout)

    @classmethod
    def run(cls, *args, **kwargs):
        timeout = kwargs.pop('timeout', None)
        with cls(*args, **kwargs) as proc:
            default = '' if proc.__text_mode else b''
            stdout, stderr = proc.communicate_or_kill(timeout=timeout)
            return stdout or default, stderr or default, proc.returncode


def encodeArgument(s):
    return s if isinstance(s, str) else s.decode('ascii')


_timetuple = collections.namedtuple('Time', ('hours', 'minutes', 'seconds', 'milliseconds'))


def timetuple_from_msec(msec):
    secs, msec = divmod(msec, 1000)
    mins, secs = divmod(secs, 60)
    hrs, mins = divmod(mins, 60)
    return _timetuple(hrs, mins, secs, msec)


def formatSeconds(secs, delim=':', msec=False):
    time = timetuple_from_msec(secs * 1000)
    if time.hours:
        ret = '%d%s%02d%s%02d' % (time.hours, delim, time.minutes, delim, time.seconds)
    elif time.minutes:
        ret = '%d%s%02d' % (time.minutes, delim, time.seconds)
    else:
        ret = '%d' % time.seconds
    return '%s.%03d' % (ret, time.milliseconds) if msec else ret


def bug_reports_message(before=';'):
    from ..update import REPOSITORY
    msg = ('please report this issue on  https://github.com/{0}/issues?q= , '
           'filling out the appropriate issue template. Confirm you are on the latest version using  yt-dlp -U'.format(REPOSITORY))
    before = before.rstrip()
    if not before or before.endswith(('.', '!', '?')):
        msg = msg[0].title() + msg[1:]
    return (before + ' ' if before else '') + msg


class YoutubeDLError(Exception):
    msg = None

    def __init__(self, msg=None):
        if msg is not None:
            self.msg = msg
        elif self.msg is None:
            self.msg = type(self).__name__
        super(YoutubeDLError, self).__init__(self.msg)


class ExtractorError(YoutubeDLError):
    def __init__(self, msg, tb=None, expected=False, cause=None, video_id=None, ie=None):
        from ..networking.exceptions import network_exceptions
        if sys.exc_info()[0] in network_exceptions:
            expected = True
        self.orig_msg = str(msg)
        self.traceback = tb
        self.expected = expected
        self.cause = cause
        self.video_id = video_id
        self.ie = ie
        self.exc_info = sys.exc_info()
        if isinstance(self.exc_info[1], ExtractorError):
            self.exc_info = self.exc_info[1].exc_info
        super(ExtractorError, self).__init__(self.__msg)

    @property
    def __msg(self):
        return ''.join((
            format_field(self.ie, None, '[%s] '),
            format_field(self.video_id, None, '%s: '),
            self.orig_msg,
            format_field(self.cause, None, ' (caused by %r)'),
            '' if self.expected else bug_reports_message()))

    def format_traceback(self):
        return join_nonempty(
            self.traceback and ''.join(traceback.format_tb(self.traceback)),
            self.cause and ''.join(traceback.format_exception(None, self.cause, self.cause.__traceback__)[1:]),
            delim='\n') or None

    def __setattr__(self, name, value):
        super(ExtractorError, self).__setattr__(name, value)
        if getattr(self, 'msg', None) and name not in ('msg', 'args'):
            self.msg = self.__msg or type(self).__name__
            self.args = (self.msg, )


class UnsupportedError(ExtractorError):
    def __init__(self, url):
        super(UnsupportedError, self).__init__(
            'Unsupported URL: {0}'.format(url), expected=True)
        self.url = url


class RegexNotFoundError(ExtractorError):
    pass


class GeoRestrictedError(ExtractorError):
    def __init__(self, msg, countries=None, **kwargs):
        kwargs['expected'] = True
        super(GeoRestrictedError, self).__init__(msg, **kwargs)
        self.countries = countries


class UserNotLive(ExtractorError):
    def __init__(self, msg=None, **kwargs):
        kwargs['expected'] = True
        super(UserNotLive, self).__init__(msg or 'The channel is not currently live', **kwargs)


class DownloadError(YoutubeDLError):
    def __init__(self, msg, exc_info=None):
        super(DownloadError, self).__init__(msg)
        self.exc_info = exc_info


class EntryNotInPlaylist(YoutubeDLError):
    msg = 'Entry not found in info'


class SameFileError(YoutubeDLError):
    msg = 'Fixed output name but more than one file to download'

    def __init__(self, filename=None):
        if filename is not None:
            self.msg += ': {0}'.format(filename)
        super(SameFileError, self).__init__(self.msg)


class PostProcessingError(YoutubeDLError):
    pass


class DownloadCancelled(YoutubeDLError):
    msg = 'The download was cancelled'


class ExistingVideoReached(DownloadCancelled):
    msg = 'Encountered a video that is already in the archive, stopping due to --break-on-existing'


class RejectedVideoReached(DownloadCancelled):
    msg = 'Encountered a video that did not match filter, stopping due to --break-match-filter'


class MaxDownloadsReached(DownloadCancelled):
    msg = 'Maximum number of downloads reached, stopping due to --max-downloads'


class ReExtractInfo(YoutubeDLError):
    def __init__(self, msg, expected=False):
        super(ReExtractInfo, self).__init__(msg)
        self.expected = expected


class ThrottledDownload(ReExtractInfo):
    msg = 'The download speed is below throttle limit'

    def __init__(self):
        super(ThrottledDownload, self).__init__(self.msg, expected=False)


class UnavailableVideoError(YoutubeDLError):
    msg = 'Unable to download video'

    def __init__(self, err=None):
        if err is not None:
            self.msg += ': {0}'.format(err)
        super(UnavailableVideoError, self).__init__(self.msg)


class ContentTooShortError(YoutubeDLError):
    def __init__(self, downloaded, expected):
        super(ContentTooShortError, self).__init__('Downloaded {0} bytes, expected {1} bytes'.format(downloaded, expected))
        self.downloaded = downloaded
        self.expected = expected


class XAttrMetadataError(YoutubeDLError):
    def __init__(self, code=None, msg='Unknown error'):
        super(XAttrMetadataError, self).__init__(msg)
        self.code = code
        self.msg = msg
        if (self.code in (errno.ENOSPC, errno.EDQUOT)
                or 'No space left' in self.msg or 'Disk quota exceeded' in self.msg):
            self.reason = 'NO_SPACE'
        elif self.code == errno.E2BIG or 'Argument list too long' in self.msg:
            self.reason = 'VALUE_TOO_LONG'
        else:
            self.reason = 'NOT_SUPPORTED'


class XAttrUnavailableError(YoutubeDLError):
    pass


def is_path_like(f):
    return isinstance(f, (str, bytes, os.PathLike)) if sys.version_info >= (3, 6) else isinstance(f, (str, bytes))


def extract_timezone(date_str, default=None):
    m = re.search(
        r'''(?x)
            ^.{8,}?
            (?P<tz>Z|
                (?:(?<=.\b\d{4}|\b\d{2}:\d\d)|
                   (?<!.\b[a-zA-Z]{3}|[a-zA-Z]{4}|..\b\d\d))
                   [ ]?
                (?P<sign>\+|-)
                (?P<hours>[0-9]{2}):?(?P<minutes>[0-9]{2})
            $)
        ''', date_str)
    timezone = None

    if not m:
        m = re.search(r'\d{1,2}:\d{1,2}(?:\.\d+)?(?P<tz>\s*[A-Z]+)$', date_str)
        timezone = TIMEZONE_NAMES.get(m and m.group('tz').strip())
        if timezone is not None:
            date_str = date_str[:-len(m.group('tz'))]
            timezone = dt.timedelta(hours=timezone)
    else:
        date_str = date_str[:-len(m.group('tz'))]
        if m.group('sign'):
            sign = 1 if m.group('sign') == '+' else -1
            timezone = dt.timedelta(
                hours=sign * int(m.group('hours')),
                minutes=sign * int(m.group('minutes')))

    if timezone is None and default is not NO_DEFAULT:
        timezone = default or dt.timedelta()

    return timezone, date_str


@partial_application
def parse_iso8601(date_str, delimiter='T', timezone=None):
    if date_str is None:
        return None
    date_str = re.sub(r'\.[0-9]+', '', date_str)
    timezone, date_str = extract_timezone(date_str, timezone)
    with contextlib.suppress(ValueError, TypeError):
        date_format = '{0}-{1}-{2}{3}{4}:{5}:{6}'.format('%Y', '%m', '%d', delimiter, '%H', '%M', '%S')
        dt_ = dt.datetime.strptime(date_str, date_format) - timezone
        return calendar.timegm(dt_.timetuple())


def date_formats(day_first=True):
    return DATE_FORMATS_DAY_FIRST if day_first else DATE_FORMATS_MONTH_FIRST


def unified_strdate(date_str, day_first=True):
    if date_str is None:
        return None
    upload_date = None
    date_str = date_str.replace(',', ' ')
    date_str = re.sub(r'(?i)\s*(?:AM|PM)(?:\s+[A-Z]+)?', '', date_str)
    _, date_str = extract_timezone(date_str)

    for expression in date_formats(day_first):
        with contextlib.suppress(ValueError):
            upload_date = dt.datetime.strptime(date_str, expression).strftime('%Y%m%d')
    if upload_date is None:
        timetuple = email.utils.parsedate_tz(date_str)
        if timetuple:
            with contextlib.suppress(ValueError):
                upload_date = dt.datetime(*timetuple[:6]).strftime('%Y%m%d')
    if upload_date is not None:
        return str(upload_date)


def unified_timestamp(date_str, day_first=True):
    if not isinstance(date_str, str):
        return None
    date_str = re.sub(r'\s+', ' ', re.sub(
        r'(?i)[,|]|(mon|tues?|wed(nes)?|thu(rs)?|fri|sat(ur)?|sun)(day)?', '', date_str))
    pm_delta = 12 if re.search(r'(?i)PM', date_str) else 0
    timezone, date_str = extract_timezone(date_str)
    date_str = re.sub(r'(?i)\s*(?:AM|PM)(?:\s+[A-Z]+)?', '', date_str)
    m = re.search(r'\d{1,2}:\d{1,2}(?:\.\d+)?(?P<tz>\s*[A-Z]+)$', date_str)
    if m:
        date_str = date_str[:-len(m.group('tz'))]
    m = re.search(r'^([0-9]{4,}-[0-9]{1,2}-[0-9]{1,2}T[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}\.[0-9]{6})[0-9]+$', date_str)
    if m:
        date_str = m.group(1)

    for expression in date_formats(day_first):
        with contextlib.suppress(ValueError):
            dt_ = dt.datetime.strptime(date_str, expression) - timezone + dt.timedelta(hours=pm_delta)
            return calendar.timegm(dt_.timetuple())

    timetuple = email.utils.parsedate_tz(date_str)
    if timetuple:
        return calendar.timegm(timetuple) + pm_delta * 3600 - int(timezone.total_seconds())


@partial_application
def determine_ext(url, default_ext='unknown_video'):
    if url is None or '.' not in url:
        return default_ext
    guess = url.partition('?')[0].rpartition('.')[2]
    if re.match(r'^[A-Za-z0-9]+$', guess):
        return guess
    elif guess.rstrip('/') in KNOWN_EXTENSIONS:
        return guess.rstrip('/')
    else:
        return default_ext


def subtitles_filename(filename, sub_lang, sub_format, expected_real_ext=None):
    return replace_extension(filename, sub_lang + '.' + sub_format, expected_real_ext)


def datetime_from_str(date_str, precision='auto', format='%Y%m%d'):
    auto_precision = False
    if precision == 'auto':
        auto_precision = True
        precision = 'microsecond'
    today = datetime_round(dt.datetime.utcnow(), precision)
    if date_str in ('now', 'today'):
        return today
    if date_str == 'yesterday':
        return today - dt.timedelta(days=1)
    match = re.match(
        r'(?P<start>.+)(?P<sign>[+-])(?P<time>\d+)(?P<unit>microsecond|second|minute|hour|day|week|month|year)s?',
        date_str)
    if match is not None:
        start_time = datetime_from_str(match.group('start'), precision, format)
        time = int(match.group('time')) * (-1 if match.group('sign') == '-' else 1)
        unit = match.group('unit')
        if unit == 'month' or unit == 'year':
            new_date = datetime_add_months(start_time, time * 12 if unit == 'year' else time)
            unit = 'day'
        else:
            if unit == 'week':
                unit = 'day'
                time *= 7
            delta = dt.timedelta(**{unit + 's': time})
            new_date = start_time + delta
        if auto_precision:
            return datetime_round(new_date, unit)
        return new_date
    return datetime_round(dt.datetime.strptime(date_str, format), precision)


def date_from_str(date_str, format='%Y%m%d', strict=False):
    if strict and not re.fullmatch(r'\d{8}|(now|today|yesterday)(-\d+(day|week|month|year)s?)?', date_str):
        raise ValueError('Invalid date format "{0}"'.format(date_str))
    return datetime_from_str(date_str, precision='microsecond', format=format).date()


def datetime_add_months(dt_, months):
    month = dt_.month + months - 1
    year = dt_.year + month // 12
    month = month % 12 + 1
    day = min(dt_.day, calendar.monthrange(year, month)[1])
    return dt_.replace(year, month, day)


def datetime_round(dt_, precision='day'):
    if precision == 'microsecond':
        return dt_
    unit_seconds = {
        'day': 86400, 'hour': 3600, 'minute': 60, 'second': 1,
    }
    roundto = lambda x, n: ((x + n / 2) // n) * n
    timestamp = roundto(calendar.timegm(dt_.timetuple()), unit_seconds[precision])
    return dt.datetime.utcfromtimestamp(timestamp)


def hyphenate_date(date_str):
    match = re.match(r'^(\d\d\d\d)(\d\d)(\d\d)$', date_str)
    if match is not None:
        return '-'.join(match.groups())
    else:
        return date_str


class DateRange(object):
    def __init__(self, start=None, end=None):
        if start is not None:
            self.start = date_from_str(start, strict=True)
        else:
            self.start = dt.datetime.min.date()
        if end is not None:
            self.end = date_from_str(end, strict=True)
        else:
            self.end = dt.datetime.max.date()
        if self.start > self.end:
            raise ValueError('Date range: "{0}" , the start date must be before the end date'.format(self))

    @classmethod
    def day(cls, day):
        return cls(day, day)

    def __contains__(self, date):
        if not isinstance(date, dt.date):
            date = date_from_str(date)
        return self.start <= date <= self.end

    def __repr__(self):
        return '{0}.{1}({2!r}, {3!r})'.format(__name__, type(self).__name__, self.start.isoformat(), self.end.isoformat())

    def __str__(self):
        return '{0} to {1}'.format(self.start, self.end)

    def __eq__(self, other):
        return (isinstance(other, DateRange)
                and self.start == other.start and self.end == other.end)


@_functools_cache
def system_identifier():
    python_implementation = platform.python_implementation()
    if python_implementation == 'PyPy' and hasattr(sys, 'pypy_version_info'):
        python_implementation += ' version %d.%d.%d' % sys.pypy_version_info[:3]
    libc_ver = []
    with contextlib.suppress(OSError):
        libc_ver = platform.libc_ver()
    return 'Python {0} ({1} {2} {3}) - {4} ({5}{6})'.format(
        platform.python_version(), python_implementation, platform.machine(),
        platform.architecture()[0], platform.platform(), ssl.OPENSSL_VERSION,
        format_field(join_nonempty(*libc_ver, delim=' '), None, ', %s'),
    )


@_functools_cache
def get_windows_version():
    if os.name == 'nt':
        return version_tuple(platform.win32_ver()[1])
    else:
        return ()


def write_string(s, out=None, encoding=None):
    assert isinstance(s, str)
    out = out or sys.stderr
    if not out:
        return
    if os.name == 'nt' and supports_terminal_sequences(out):
        s = re.sub(r'([\r\n]+)', r' \1', s)
    enc, buffer = None, out
    if 'b' in (getattr(out, 'mode', None) or ''):
        enc = encoding or preferredencoding()
    elif hasattr(out, 'buffer'):
        buffer = out.buffer
        enc = encoding or getattr(out, 'encoding', None) or preferredencoding()
    buffer.write(s.encode(enc, 'ignore') if enc else s)
    out.flush()


def deprecation_warning(msg, printer=None, stacklevel=0, **kwargs):
    if IN_CLI.value:
        if msg in deprecation_warning._cache:
            return
        deprecation_warning._cache.add(msg)
        if printer:
            return printer('{0}{1}'.format(msg, bug_reports_message()), **kwargs)
        return write_string('ERROR: {0}{1}\n'.format(msg, bug_reports_message()), **kwargs)
    else:
        import warnings
        warnings.warn(DeprecationWarning(msg), stacklevel=stacklevel + 3)

deprecation_warning._cache = set()


class LockingUnsupportedError(OSError):
    msg = 'File locking is not supported'

    def __init__(self):
        super(LockingUnsupportedError, self).__init__(self.msg)


if sys.platform == 'win32':
    import ctypes
    import ctypes.wintypes
    import msvcrt

    class OVERLAPPED(ctypes.Structure):
        _fields_ = [
            ('Internal', ctypes.wintypes.LPVOID),
            ('InternalHigh', ctypes.wintypes.LPVOID),
            ('Offset', ctypes.wintypes.DWORD),
            ('OffsetHigh', ctypes.wintypes.DWORD),
            ('hEvent', ctypes.wintypes.HANDLE),
        ]

    kernel32 = ctypes.WinDLL('kernel32')
    LockFileEx = kernel32.LockFileEx
    LockFileEx.argtypes = [
        ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD,
        ctypes.wintypes.DWORD, ctypes.wintypes.DWORD, ctypes.POINTER(OVERLAPPED),
    ]
    LockFileEx.restype = ctypes.wintypes.BOOL
    UnlockFileEx = kernel32.UnlockFileEx
    UnlockFileEx.argtypes = [
        ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD,
        ctypes.wintypes.DWORD, ctypes.wintypes.DWORD, ctypes.POINTER(OVERLAPPED),
    ]
    UnlockFileEx.restype = ctypes.wintypes.BOOL
    whole_low = 0xffffffff
    whole_high = 0x7fffffff

    def _lock_file(f, exclusive, block):
        overlapped = OVERLAPPED()
        overlapped.Offset = 0
        overlapped.OffsetHigh = 0
        overlapped.hEvent = 0
        f._lock_file_overlapped_p = ctypes.pointer(overlapped)
        if not LockFileEx(msvcrt.get_osfhandle(f.fileno()),
                          (0x2 if exclusive else 0x0) | (0x0 if block else 0x1),
                          0, whole_low, whole_high, f._lock_file_overlapped_p):
            raise BlockingIOError('Locking file failed: {0!r}'.format(ctypes.FormatError(ctypes.GetLastError())))

    def _unlock_file(f):
        assert f._lock_file_overlapped_p
        handle = msvcrt.get_osfhandle(f.fileno())
        if not UnlockFileEx(handle, 0, whole_low, whole_high, f._lock_file_overlapped_p):
            raise OSError('Unlocking file failed: {0!r}'.format(ctypes.FormatError()))
else:
    try:
        import fcntl

        def _lock_file(f, exclusive, block):
            flags = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
            if not block:
                flags |= fcntl.LOCK_NB
            try:
                fcntl.flock(f, flags)
            except BlockingIOError:
                raise
            except OSError:
                fcntl.lockf(f, flags)

        def _unlock_file(f):
            with contextlib.suppress(OSError):
                return fcntl.flock(f, fcntl.LOCK_UN)
            with contextlib.suppress(OSError):
                return fcntl.lockf(f, fcntl.LOCK_UN)
            return fcntl.flock(f, fcntl.LOCK_UN | fcntl.LOCK_NB)
    except ImportError:
        def _lock_file(f, exclusive, block):
            raise LockingUnsupportedError

        def _unlock_file(f):
            raise LockingUnsupportedError


class locked_file(object):
    locked = False

    def __init__(self, filename, mode, block=True, encoding=None):
        if mode not in {'r', 'rb', 'a', 'ab', 'w', 'wb'}:
            raise NotImplementedError(mode)
        self.mode, self.block = mode, block
        writable = any(f in mode for f in 'wax+')
        readable = any(f in mode for f in 'r+')
        flags = functools.reduce(operator.ior, (
            getattr(os, 'O_CLOEXEC', 0), getattr(os, 'O_BINARY', 0),
            getattr(os, 'O_NOINHERIT', 0), os.O_CREAT if writable else 0,
            os.O_APPEND if 'a' in mode else 0, os.O_EXCL if 'x' in mode else 0,
            os.O_RDONLY if not writable else os.O_RDWR if readable else os.O_WRONLY,
        ))
        self.f = os.fdopen(os.open(filename, flags, 0o666), mode, encoding=encoding)

    def __enter__(self):
        exclusive = 'r' not in self.mode
        try:
            _lock_file(self.f, exclusive, self.block)
            self.locked = True
        except OSError:
            self.f.close()
            raise
        if 'w' in self.mode:
            try:
                self.f.truncate()
            except OSError as e:
                if e.errno not in (errno.ESPIPE, errno.EINVAL):
                    raise
        return self

    def unlock(self):
        if not self.locked:
            return
        try:
            _unlock_file(self.f)
        finally:
            self.locked = False

    def __exit__(self, *_):
        try:
            self.unlock()
        finally:
            self.f.close()

    open = __enter__
    close = __exit__

    def __getattr__(self, attr):
        return getattr(self.f, attr)

    def __iter__(self):
        return iter(self.f)


@_functools_cache
def get_filesystem_encoding():
    encoding = sys.getfilesystemencoding()
    return encoding if encoding is not None else 'utf-8'


_WINDOWS_QUOTE_TRANS = dict(zip(map(ord, '"'), map(ord, R'\"')))
_CMD_QUOTE_TRANS = dict(zip(map(ord, '"\n\r%'), map(ord, ('""', '%=%', '%=%', '%%cd:~,%'))))


def shell_quote(args, shell=False):
    args = list(variadic(args))
    if os.name != 'nt':
        return shlex.join(args) if sys.version_info >= (3, 8) else ' '.join(map(shlex.quote, args))

    trans = _CMD_QUOTE_TRANS if shell else _WINDOWS_QUOTE_TRANS
    return ' '.join(
        s if re.fullmatch(r'[\w#$*\-+./:?@\\]+', s, re.ASCII)
        else re.sub(r'(\\+)("|$)', r'\1\1\2', s).translate(trans).join('""')
        for s in args)


def smuggle_url(url, data):
    url, idata = unsmuggle_url(url, {})
    data.update(idata)
    sdata = urllib_parse.urlencode(
        {'__youtubedl_smuggle': json.dumps(data)})
    return url + '#' + sdata


def unsmuggle_url(smug_url, default=None):
    if '#__youtubedl_smuggle' not in smug_url:
        return smug_url, default
    url, _, sdata = smug_url.rpartition('#')
    jsond = urllib_parse.parse_qs(sdata)['__youtubedl_smuggle'][0]
    data = json.loads(jsond)
    return url, data


def format_decimal_suffix(num, fmt='%d%s', factor=1000):
    num, factor = float_or_none(num), float(factor)
    if num is None or num < 0:
        return None
    POSSIBLE_SUFFIXES = 'kMGTPEZY'
    exponent = 0 if num == 0 else min(int(math.log(num, factor)), len(POSSIBLE_SUFFIXES))
    suffix = ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'][exponent]
    if factor == 1024:
        suffix = {'k': 'Ki', '': ''}.get(suffix, '{0}i'.format(suffix))
    converted = num / (factor ** exponent)
    return fmt % (converted, suffix)


def format_bytes(bytes):
    return format_decimal_suffix(bytes, '%.2f%sB', factor=1024) or 'N/A'


def lookup_unit_table(unit_table, s, strict=False):
    num_re = NUMBER_RE if strict else NUMBER_RE.replace(R'\.', '[,.]')
    units_re = '|'.join(re.escape(u) for u in unit_table)
    m = (re.fullmatch if strict else re.match)(
        r'(?P<num>{0})\s*(?P<unit>{1})\b'.format(num_re, units_re), s)
    if not m:
        return None
    num = float(m.group('num').replace(',', '.'))
    mult = unit_table[m.group('unit')]
    return round(num * mult)


def parse_bytes(s):
    return lookup_unit_table(
        {u: 1024**i for i, u in enumerate(['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'])},
        s.upper(), strict=True)


def parse_filesize(s):
    if s is None:
        return None
    _UNIT_TABLE = {
        'B': 1, 'b': 1, 'bytes': 1,
        'KiB': 1024, 'KB': 1000, 'kB': 1024, 'Kb': 1000, 'kb': 1000,
        'kilobytes': 1000, 'kibibytes': 1024,
        'MiB': 1024 ** 2, 'MB': 1000 ** 2, 'mB': 1024 ** 2, 'Mb': 1000 ** 2, 'mb': 1000 ** 2,
        'megabytes': 1000 ** 2, 'mebibytes': 1024 ** 2,
        'GiB': 1024 ** 3, 'GB': 1000 ** 3, 'gB': 1024 ** 3, 'Gb': 1000 ** 3, 'gb': 1000 ** 3,
        'gigabytes': 1000 ** 3, 'gibibytes': 1024 ** 3,
        'TiB': 1024 ** 4, 'TB': 1000 ** 4, 'tB': 1024 ** 4, 'Tb': 1000 ** 4, 'tb': 1000 ** 4,
        'terabytes': 1000 ** 4, 'tebibytes': 1024 ** 4,
        'PiB': 1024 ** 5, 'PB': 1000 ** 5, 'pB': 1024 ** 5, 'Pb': 1000 ** 5, 'pb': 1000 ** 5,
        'petabytes': 1000 ** 5, 'pebibytes': 1024 ** 5,
        'EiB': 1024 ** 6, 'EB': 1000 ** 6, 'eB': 1024 ** 6, 'Eb': 1000 ** 6, 'eb': 1000 ** 6,
        'exabytes': 1000 ** 6, 'exbibytes': 1024 ** 6,
        'ZiB': 1024 ** 7, 'ZB': 1000 ** 7, 'zB': 1024 ** 7, 'Zb': 1000 ** 7, 'zb': 1000 ** 7,
        'zettabytes': 1000 ** 7, 'zebibytes': 1024 ** 7,
        'YiB': 1024 ** 8, 'YB': 1000 ** 8, 'yB': 1024 ** 8, 'Yb': 1000 ** 8, 'yb': 1000 ** 8,
        'yottabytes': 1000 ** 8, 'yobibytes': 1024 ** 8,
    }
    return lookup_unit_table(_UNIT_TABLE, s)


def parse_count(s):
    if s is None:
        return None
    s = re.sub(r'^[^\d]+\s', '', s).strip()
    if re.match(r'^[\d,.]+$', s):
        return str_to_int(s)
    _UNIT_TABLE = {
        'k': 1000, 'K': 1000, 'm': 1000 ** 2, 'M': 1000 ** 2,
        'kk': 1000 ** 2, 'KK': 1000 ** 2, 'b': 1000 ** 3, 'B': 1000 ** 3,
    }
    ret = lookup_unit_table(_UNIT_TABLE, s)
    if ret is not None:
        return ret
    mobj = re.match(r'([\d,.]+)(?:$|\s)', s)
    if mobj:
        return str_to_int(mobj.group(1))


def parse_resolution(s, lenient=False):
    if s is None:
        return {}
    if lenient:
        mobj = re.search(r'(?P<w>\d+)\s*[xX×,]\s*(?P<h>\d+)', s)
    else:
        mobj = re.search(r'(?<![a-zA-Z0-9])(?P<w>\d+)\s*[xX×,]\s*(?P<h>\d+)(?![a-zA-Z0-9])', s)
    if mobj:
        return {
            'width': int(mobj.group('w')),
            'height': int(mobj.group('h')),
        }
    mobj = re.search(r'(?<![a-zA-Z0-9])(\d+)[pPiI](?![a-zA-Z0-9])', s)
    if mobj:
        return {'height': int(mobj.group(1))}
    mobj = re.search(r'\b([48])[kK]\b', s)
    if mobj:
        return {'height': int(mobj.group(1)) * 540}
    if lenient:
        mobj = re.search(r'(?<!\d)(\d{2,5})w(?![a-zA-Z0-9])', s)
        if mobj:
            return {'width': int(mobj.group(1))}
    return {}


def parse_bitrate(s):
    if not isinstance(s, str):
        return
    mobj = re.search(r'\b(\d+)\s*kbps', s)
    if mobj:
        return int(mobj.group(1))


def month_by_name(name, lang='en'):
    month_names = MONTH_NAMES.get(lang, MONTH_NAMES['en'])
    try:
        return month_names.index(name) + 1
    except ValueError:
        return None


def month_by_abbreviation(abbrev):
    try:
        return [s[:3] for s in ENGLISH_MONTH_NAMES].index(abbrev) + 1
    except ValueError:
        return None


def fix_xml_ampersands(xml_str):
    return re.sub(
        r'&(?!amp;|lt;|gt;|apos;|quot;|#x[0-9a-fA-F]{,4};|#[0-9]{,4};)',
        '&amp;',
        xml_str)


def setproctitle(title):
    assert isinstance(title, str)
    try:
        import ctypes
    except ImportError:
        return
    try:
        libc = ctypes.cdll.LoadLibrary('libc.so.6')
    except OSError:
        return
    except TypeError:
        return
    title_bytes = title.encode()
    buf = ctypes.create_string_buffer(len(title_bytes))
    buf.value = title_bytes
    try:
        libc.prctl(15, buf, 0, 0, 0)
    except AttributeError:
        return


def remove_start(s, start):
    return s[len(start):] if s is not None and s.startswith(start) else s


def remove_end(s, end):
    return s[:-len(end)] if s is not None and end and s.endswith(end) else s


def remove_quotes(s):
    if s is None or len(s) < 2:
        return s
    for quote in ('"', "'"):
        if s[0] == quote and s[-1] == quote:
            return s[1:-1]
    return s


def get_domain(url):
    return remove_start(urllib_parse.urlparse(url).netloc, 'www.') or None


def url_basename(url):
    path = urllib_parse.urlparse(url).path
    return path.strip('/').split('/')[-1]


def base_url(url):
    return re.match(r'https?://[^?#]+/', url).group()


@partial_application
def urljoin(base, path):
    if isinstance(path, bytes):
        path = path.decode()
    if not isinstance(path, str) or not path:
        return None
    if re.match(r'(?:[a-zA-Z][a-zA-Z0-9+-.]*:)?//', path):
        return path
    if isinstance(base, bytes):
        base = base.decode()
    if not isinstance(base, str) or not re.match(
            r'^(?:https?:)?//', base):
        return None
    return urllib_parse.urljoin(base, path)


@partial_application
def int_or_none(v, scale=1, default=None, get_attr=None, invscale=1, base=None):
    if get_attr and v is not None:
        v = getattr(v, get_attr, None)
    if invscale == 1 and scale < 1:
        invscale = int(1 / scale)
        scale = 1
    try:
        return (int(v) if base is None else int(v, base=base)) * invscale // scale
    except (ValueError, TypeError, OverflowError):
        return default


def str_or_none(v, default=None):
    return default if v is None else str(v)


def str_to_int(int_str):
    if isinstance(int_str, int):
        return int_str
    elif isinstance(int_str, str):
        int_str = re.sub(r'[,\.\+]', '', int_str)
        return int_or_none(int_str)


@partial_application
def float_or_none(v, scale=1, invscale=1, default=None):
    if v is None:
        return default
    if invscale == 1 and scale < 1:
        invscale = int(1 / scale)
        scale = 1
    try:
        return float(v) * invscale / scale
    except (ValueError, TypeError):
        return default


def bool_or_none(v, default=None):
    return v if isinstance(v, bool) else default


def strip_or_none(v, default=None):
    return v.strip() if isinstance(v, str) else default


def url_or_none(url):
    if not url or not isinstance(url, str):
        return None
    url = url.strip()
    return url if re.match(r'(?:(?:https?|rt(?:m(?:pt?[es]?|fp)|sp[su]?)|mms|ftps?|wss?):)?//', url) else None


def strftime_or_none(timestamp, date_format='%Y%m%d', default=None):
    datetime_object = None
    try:
        if isinstance(timestamp, (int, float)):
            datetime_object = (dt.datetime.utcfromtimestamp(0) + dt.timedelta(seconds=timestamp))
        elif isinstance(timestamp, str):
            datetime_object = dt.datetime.strptime(timestamp, '%Y%m%d')
        date_format = re.sub(
            r'(?<!%)(%%)*%s', r'\g<1>{0}'.format(int(calendar.timegm(datetime_object.utctimetuple()))), date_format)
        return datetime_object.strftime(date_format)
    except (ValueError, TypeError, AttributeError):
        return default


def parse_duration(s):
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None
    days, hours, mins, secs, ms = [None] * 5
    m = re.match(r'''(?x)
            (?P<before_secs>
                (?:(?:(?P<days>[0-9]+):)?(?P<hours>[0-9]+):)?(?P<mins>[0-9]+):)?
            (?P<secs>(?(before_secs)[0-9]{1,2}|[0-9]+))
            (?P<ms>[.:][0-9]+)?Z?$
        ''', s)
    if m:
        days, hours, mins, secs, ms = m.group('days', 'hours', 'mins', 'secs', 'ms')
    else:
        m = re.match(
            r'''(?ix)(?:P?
                (?:[0-9]+\s*y(?:ears?)?,?\s*)?
                (?:[0-9]+\s*m(?:onths?)?,?\s*)?
                (?:[0-9]+\s*w(?:eeks?)?,?\s*)?
                (?:(?P<days>[0-9]+)\s*d(?:ays?)?,?\s*)?
                T)?
                (?:(?P<hours>[0-9]+)\s*h(?:(?:ou)?rs?)?,?\s*)?
                (?:(?P<mins>[0-9]+)\s*m(?:in(?:ute)?s?)?,?\s*)?
                (?:(?P<secs>[0-9]+)(?P<ms>\.[0-9]+)?\s*s(?:ec(?:ond)?s?)?\s*)?Z?$''', s)
        if m:
            days, hours, mins, secs, ms = m.groups()
        else:
            m = re.match(r'(?i)(?:(?P<hours>[0-9.]+)\s*(?:hours?)|(?P<mins>[0-9.]+)\s*(?:mins?\.?|minutes?)\s*)Z?$', s)
            if m:
                hours, mins = m.groups()
            else:
                return None
    if ms:
        ms = ms.replace(':', '.')
    return sum(float(part or 0) * mult for part, mult in (
        (days, 86400), (hours, 3600), (mins, 60), (secs, 1), (ms, 1)))


def _change_extension(prepend, filename, ext, expected_real_ext=None):
    name, real_ext = os.path.splitext(filename)
    if not expected_real_ext or real_ext[1:] == expected_real_ext:
        filename = name
        if prepend and real_ext:
            _UnsafeExtensionError.sanitize_extension(ext, prepend=True)
            return '{0}.{1}{2}'.format(filename, ext, real_ext)
    return '{0}.{1}'.format(filename, _UnsafeExtensionError.sanitize_extension(ext))


prepend_extension = functools.partial(_change_extension, True)
replace_extension = functools.partial(_change_extension, False)


def check_executable(exe, args=[]):
    try:
        Popen.run([exe] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return False
    return exe


def _get_exe_version_output(exe, args):
    try:
        stdout, _, ret = Popen.run([encodeArgument(exe)] + args, text=True,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if ret:
            return None
    except OSError:
        return False
    return stdout


def detect_exe_version(output, version_re=None, unrecognized='present'):
    assert isinstance(output, str)
    if version_re is None:
        version_re = r'version\s+([-0-9._a-zA-Z]+)'
    m = re.search(version_re, output)
    if m:
        return m.group(1)
    else:
        return unrecognized


def get_exe_version(exe, args=['--version'], version_re=None, unrecognized=('present', 'broken')):
    unrecognized = variadic(unrecognized)
    assert len(unrecognized) in (1, 2)
    out = _get_exe_version_output(exe, args)
    if out is None:
        return unrecognized[-1]
    return out and detect_exe_version(out, version_re, unrecognized[0])


def frange(start=0, stop=None, step=1):
    if stop is None:
        start, stop = 0, start
    sign = [-1, 1][step > 0] if step else 0
    while sign * start < sign * stop:
        yield start
        start += step


class LazyList(collections.Sequence):
    class IndexError(IndexError):
        pass

    def __init__(self, iterable, reverse=False, _cache=None):
        self._iterable = iter(iterable)
        self._cache = [] if _cache is None else _cache
        self._reversed = reverse

    def __iter__(self):
        if self._reversed:
            for item in self.exhaust():
                yield item
            return
        for item in self._cache:
            yield item
        for item in self._iterable:
            self._cache.append(item)
            yield item

    def _exhaust(self):
        self._cache.extend(self._iterable)
        self._iterable = []
        return self._cache

    def exhaust(self):
        return self._exhaust()[::-1 if self._reversed else 1]

    @staticmethod
    def _reverse_index(x):
        return None if x is None else ~x

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            if self._reversed:
                idx = slice(self._reverse_index(idx.start), self._reverse_index(idx.stop), -(idx.step or 1))
            start, stop, step = idx.start, idx.stop, idx.step or 1
        elif isinstance(idx, int):
            if self._reversed:
                idx = self._reverse_index(idx)
            start, stop, step = idx, idx, 0
        else:
            raise TypeError('indices must be integers or slices')
        if ((start or 0) < 0 or (stop or 0) < 0
                or (start is None and step < 0)
                or (stop is None and step > 0)):
            self._exhaust()
            try:
                return self._cache[idx]
            except IndexError as e:
                raise self.IndexError(e)
        n = max(start or 0, stop or 0) - len(self._cache) + 1
        if n > 0:
            self._cache.extend(itertools.islice(self._iterable, n))
        try:
            return self._cache[idx]
        except IndexError as e:
            raise self.IndexError(e)

    def __nonzero__(self):
        try:
            self[-1] if self._reversed else self[0]
        except self.IndexError:
            return False
        return True

    def __len__(self):
        self._exhaust()
        return len(self._cache)

    def __reversed__(self):
        return type(self)(self._iterable, reverse=not self._reversed, _cache=self._cache)

    def __copy__(self):
        return type(self)(self._iterable, reverse=self._reversed, _cache=self._cache)

    def __repr__(self):
        return repr(self.exhaust())

    def __str__(self):
        return repr(self.exhaust())


class PagedList(object):
    class IndexError(IndexError):
        pass

    def __len__(self):
        return len(self.getslice())

    def __init__(self, pagefunc, pagesize, use_cache=True):
        self._pagefunc = pagefunc
        self._pagesize = pagesize
        self._pagecount = float('inf')
        self._use_cache = use_cache
        self._cache = {}

    def getpage(self, pagenum):
        page_results = self._cache.get(pagenum)
        if page_results is None:
            page_results = [] if pagenum > self._pagecount else list(self._pagefunc(pagenum))
        if self._use_cache:
            self._cache[pagenum] = page_results
        return page_results

    def getslice(self, start=0, end=None):
        return list(self._getslice(start, end))

    def _getslice(self, start, end):
        raise NotImplementedError('This method must be implemented by subclasses')

    def __getitem__(self, idx):
        assert self._use_cache, 'Indexing PagedList requires cache'
        if not isinstance(idx, int) or idx < 0:
            raise TypeError('indices must be non-negative integers')
        entries = self.getslice(idx, idx + 1)
        if not entries:
            raise self.IndexError
        return entries[0]

    def __nonzero__(self):
        return bool(self.getslice(0, 1))


class OnDemandPagedList(PagedList):
    def _getslice(self, start, end):
        for pagenum in itertools.count(start // self._pagesize):
            firstid = pagenum * self._pagesize
            nextfirstid = pagenum * self._pagesize + self._pagesize
            if start >= nextfirstid:
                continue
            startv = (
                start % self._pagesize
                if firstid <= start < nextfirstid
                else 0)
            endv = (
                ((end - 1) % self._pagesize) + 1
                if (end is not None and firstid <= end <= nextfirstid)
                else None)
            try:
                page_results = self.getpage(pagenum)
            except Exception:
                self._pagecount = pagenum - 1
                raise
            if startv != 0 or endv is not None:
                page_results = page_results[startv:endv]
            for item in page_results:
                yield item
            if len(page_results) + startv < self._pagesize:
                break
            if end == nextfirstid:
                break


class InAdvancePagedList(PagedList):
    def __init__(self, pagefunc, pagecount, pagesize):
        PagedList.__init__(self, pagefunc, pagesize, True)
        self._pagecount = pagecount

    def _getslice(self, start, end):
        start_page = start // self._pagesize
        end_page = self._pagecount if end is None else min(self._pagecount, end // self._pagesize + 1)
        skip_elems = start - start_page * self._pagesize
        only_more = None if end is None else end - start
        for pagenum in range(start_page, end_page):
            page_results = self.getpage(pagenum)
            if skip_elems:
                page_results = page_results[skip_elems:]
                skip_elems = None
            if only_more is not None:
                if len(page_results) < only_more:
                    only_more -= len(page_results)
                else:
                    for item in page_results[:only_more]:
                        yield item
                    break
            for item in page_results:
                yield item


class PlaylistEntries(object):
    MissingEntry = object()
    is_exhausted = False

    def __init__(self, ydl, info_dict):
        self.ydl = ydl
        entries = info_dict.get('entries')
        if entries is None:
            raise EntryNotInPlaylist('There are no entries')
        elif isinstance(entries, list):
            self.is_exhausted = True
        requested_entries = info_dict.get('requested_entries')
        self.is_incomplete = requested_entries is not None
        if self.is_incomplete:
            assert self.is_exhausted
            self._entries = [self.MissingEntry] * max(requested_entries or [0])
            for i, entry in zip(requested_entries, entries):
                self._entries[i - 1] = entry
        elif isinstance(entries, (list, PagedList, LazyList)):
            self._entries = entries
        else:
            self._entries = LazyList(entries)

    PLAYLIST_ITEMS_RE = re.compile(r'''(?x)
        (?P<start>[+-]?\d+)?
        (?P<range>[:-]
            (?P<end>[+-]?\d+|inf(?:inite)?)?
            (?::(?P<step>[+-]?\d+))?
        )?''')

    @classmethod
    def parse_playlist_items(cls, string):
        for segment in string.split(','):
            if not segment:
                raise ValueError('There is two or more consecutive commas')
            mobj = cls.PLAYLIST_ITEMS_RE.fullmatch(segment)
            if not mobj:
                raise ValueError('{0!r} is not a valid specification'.format(segment))
            start, end, step, has_range = mobj.group('start', 'end', 'step', 'range')
            if int_or_none(step) == 0:
                raise ValueError('Step in {0!r} cannot be zero'.format(segment))
            yield slice(int_or_none(start), float_or_none(end), int_or_none(step)) if has_range else int(start)

    def get_requested_items(self):
        playlist_items = self.ydl.params.get('playlist_items')
        playlist_start = self.ydl.params.get('playliststart', 1)
        playlist_end = self.ydl.params.get('playlistend')
        if playlist_end in (-1, None):
            playlist_end = ''
        if not playlist_items:
            playlist_items = '{0}:{1}'.format(playlist_start, playlist_end)
        elif playlist_start != 1 or playlist_end:
            self.ydl.report_warning('Ignoring playliststart and playlistend because playlistitems was given', only_once=True)

        for index in self.parse_playlist_items(playlist_items):
            for i, entry in self[index]:
                yield i, entry
                if not entry:
                    continue
                try:
                    if not self.ydl.params.get('lazy_playlist'):
                        self.ydl._match_entry(entry, incomplete=True, silent=True)
                except (ExistingVideoReached, RejectedVideoReached):
                    return

    def get_full_count(self):
        if self.is_exhausted and not self.is_incomplete:
            return len(self)
        elif isinstance(self._entries, InAdvancePagedList):
            if self._entries._pagesize == 1:
                return self._entries._pagecount

    @property
    @_functools_cache
    def _getter(self):
        if isinstance(self._entries, list):
            def get_entry(i):
                try:
                    entry = self._entries[i]
                except IndexError:
                    entry = self.MissingEntry
                    if not self.is_incomplete:
                        raise self.IndexError
                if entry is self.MissingEntry:
                    raise EntryNotInPlaylist('Entry {0} cannot be found'.format(i + 1))
                return entry
        else:
            def get_entry(i):
                try:
                    return type(self.ydl)._handle_extraction_exceptions(lambda _, i: self._entries[i])(self.ydl, i)
                except (LazyList.IndexError, PagedList.IndexError):
                    raise self.IndexError
        return get_entry

    def __getitem__(self, idx):
        if isinstance(idx, int):
            idx = slice(idx, idx)
        step = 1 if idx.step is None else idx.step
        if idx.start is None:
            start = 0 if step > 0 else len(self) - 1
        else:
            start = idx.start - 1 if idx.start >= 0 else len(self) + idx.start
        if idx.stop is None:
            stop = 0 if step < 0 else float('inf')
        else:
            stop = idx.stop - 1 if idx.stop >= 0 else len(self) + idx.stop
        stop += [-1, 1][step > 0]
        for i in frange(start, stop, step):
            if i < 0:
                continue
            try:
                entry = self._getter(i)
            except self.IndexError:
                self.is_exhausted = True
                if step > 0:
                    break
                continue
            yield i + 1, entry

    def __len__(self):
        return len(tuple(self[:]))

    class IndexError(IndexError):
        pass


def uppercase_escape(s):
    unicode_escape = codecs.getdecoder('unicode_escape')
    return re.sub(
        r'\\U[0-9a-fA-F]{8}',
        lambda m: unicode_escape(m.group(0))[0],
        s)


def lowercase_escape(s):
    unicode_escape = codecs.getdecoder('unicode_escape')
    return re.sub(
        r'\\u[0-9a-fA-F]{4}',
        lambda m: unicode_escape(m.group(0))[0],
        s)


def parse_qs(url, **kwargs):
    return urllib_parse.parse_qs(urllib_parse.urlparse(url).query, **kwargs)


def read_batch_urls(batch_fd):
    def fixup(url):
        if not isinstance(url, str):
            url = url.decode('utf-8', 'replace')
        BOM_UTF8 = ('\xef\xbb\xbf', '\ufeff')
        for bom in BOM_UTF8:
            if url.startswith(bom):
                url = url[len(bom):]
        url = url.lstrip()
        if not url or url.startswith(('#', ';', ']')):
            return False
        return re.split(r'\s#', url, maxsplit=1)[0].rstrip()
    with contextlib.closing(batch_fd) as fd:
        return [url for url in map(fixup, fd) if url]


def urlencode_postdata(*args, **kargs):
    return urllib_parse.urlencode(*args, **kargs).encode('ascii')


@partial_application
def update_url(url, query_update=None, **kwargs):
    if isinstance(url, str):
        if not kwargs and not query_update:
            return url
        else:
            url = urllib_parse.urlparse(url)
    if query_update:
        assert 'query' not in kwargs, 'query_update and query cannot be specified at the same time'
        query = urllib_parse.parse_qs(url.query)
        query.update(query_update)
        kwargs['query'] = urllib_parse.urlencode(query, True)
    return urllib_parse.urlunparse(url._replace(**kwargs))


@partial_application
def update_url_query(url, query):
    return update_url(url, query_update=query)


def _multipart_encode_impl(data, boundary):
    content_type = 'multipart/form-data; boundary={0}'.format(boundary)
    out = b''
    for k, v in data.items():
        out += b'--' + boundary.encode('ascii') + b'\r\n'
        if isinstance(k, str):
            k = k.encode()
        if isinstance(v, str):
            v = v.encode()
        content = b'Content-Disposition: form-data; name="' + k + b'"\r\n\r\n' + v + b'\r\n'
        if boundary.encode('ascii') in content:
            raise ValueError('Boundary overlaps with data')
        out += content
    out += b'--' + boundary.encode('ascii') + b'--\r\n'
    return out, content_type


def multipart_encode(data, boundary=None):
    has_specified_boundary = boundary is not None
    while True:
        if boundary is None:
            boundary = '---------------' + str(random.randrange(0x0fffffff, 0xffffffff))
        try:
            out, content_type = _multipart_encode_impl(data, boundary)
            break
        except ValueError:
            if has_specified_boundary:
                raise
            boundary = None
    return out, content_type


def is_iterable_like(x, allowed_types=collections.Iterable, blocked_types=NO_DEFAULT):
    if blocked_types is NO_DEFAULT:
        blocked_types = (str, bytes, collections.Mapping)
    return isinstance(x, allowed_types) and not isinstance(x, blocked_types)


def variadic(x, allowed_types=NO_DEFAULT):
    if not isinstance(allowed_types, (tuple, type)):
        deprecation_warning('allowed_types should be a tuple or a type')
        allowed_types = tuple(allowed_types)
    return x if is_iterable_like(x, blocked_types=allowed_types) else (x, )


def try_call(*funcs, **kwargs):
    expected_type = kwargs.get('expected_type')
    args = kwargs.get('args', [])
    kwargs = kwargs.get('kwargs', {})
    for f in funcs:
        try:
            val = f(*args, **kwargs)
        except (AttributeError, KeyError, TypeError, IndexError, ValueError, ZeroDivisionError):
            pass
        else:
            if expected_type is None or isinstance(val, expected_type):
                return val


def try_get(src, getter, expected_type=None):
    return try_call(*variadic(getter), args=(src,), expected_type=expected_type)


def filter_dict(dct, cndn=lambda _, v: v is not None):
    return {k: v for k, v in dct.items() if cndn(k, v)}


def merge_dicts(*dicts):
    merged = {}
    for a_dict in dicts:
        for k, v in a_dict.items():
            if ((v is not None and k not in merged)
                    or (isinstance(v, str) and merged[k] == '')):
                merged[k] = v
    return merged


def encode_compat_str(string, encoding=preferredencoding(), errors='strict'):
    return string if isinstance(string, str) else str(string, encoding, errors)


US_RATINGS = {'G': 0, 'PG': 10, 'PG-13': 13, 'R': 16, 'NC': 18}
TV_PARENTAL_GUIDELINES = {'TV-Y': 0, 'TV-Y7': 7, 'TV-G': 0, 'TV-PG': 0, 'TV-14': 14, 'TV-MA': 17}


def parse_age_limit(s):
    if type(s) is int:
        return s if 0 <= s <= 21 else None
    elif not isinstance(s, str):
        return None
    m = re.match(r'^(?P<age>\d{1,2})\+?$', s)
    if m:
        return int(m.group('age'))
    s = s.upper()
    if s in US_RATINGS:
        return US_RATINGS[s]
    m = re.match(r'^TV[_-]?({0})$'.format('|'.join(k[3:] for k in TV_PARENTAL_GUIDELINES)), s)
    if m:
        return TV_PARENTAL_GUIDELINES['TV-' + m.group(1)]
    return None


def strip_jsonp(code):
    return re.sub(
        r'''(?sx)^
            (?:window\.)?(?P<func_name>[a-zA-Z0-9_.$]*)
            (?:\s*&&\s*(?P=func_name))?
            \s*\(\s*(?P<callback_data>.*)\);?
            \s*?(?://[^\n]*)*$''',
        r'\g<callback_data>', code)


def js_to_json(code, vars={}, strict=False):
    STRING_QUOTES = '\'"`'
    STRING_RE = '|'.join(r'{0}(?:\\.|[^\\{0}])*'.format(q) for q in STRING_QUOTES)
    COMMENT_RE = r'/\*(?:(?!\*/).)*?\*/|//[^\n]*\n'
    SKIP_RE = r'\s*(?:{0})?\s*'.format(COMMENT_RE)
    INTEGER_TABLE = (
        (r'(?s)^(0[xX][0-9a-fA-F]+){0}:?$'.format(SKIP_RE), 16),
        (r'(?s)^(0+[0-7]+){0}:?$'.format(SKIP_RE), 8),
    )

    def process_escape(match):
        JSON_PASSTHROUGH_ESCAPES = r'"\bfnrtu'
        escape = match.group(1) or match.group(2)
        return (r'\{0}'.format(escape) if escape in JSON_PASSTHROUGH_ESCAPES
                else u'\\u00' if escape == 'x'
                else '' if escape == '\n'
                else escape)

    def template_substitute(match):
        evaluated = js_to_json(match.group(1), vars, strict=strict)
        if evaluated[0] == '"':
            with contextlib.suppress(json.JSONDecodeError):
                return json.loads(evaluated)
        return evaluated

    def fix_kv(m):
        v = m.group(0)
        if v in ('true', 'false', 'null'):
            return v
        elif v in ('undefined', 'void 0'):
            return 'null'
        elif v.startswith(('/*', '//', '!')) or v == ',':
            return ''
        if v[0] in STRING_QUOTES:
            v = re.sub(r'(?s)\${([^}]+)}', template_substitute, v[1:-1]) if v[0] == '`' else v[1:-1]
            escaped = re.sub(r'(?s)(")|\\(.)', process_escape, v)
            return '"{0}"'.format(escaped)
        for regex, base in INTEGER_TABLE:
            im = re.match(regex, v)
            if im:
                i = int(im.group(1), base)
                return '"{0}":'.format(i) if v.endswith(':') else str(i)
        if v in vars:
            try:
                if not strict:
                    json.loads(vars[v])
            except json.JSONDecodeError:
                return json.dumps(vars[v])
            else:
                return vars[v]
        if not strict:
            return '"{0}"'.format(v)
        raise ValueError('Unknown value: {0}'.format(v))

    def create_map(mobj):
        return json.dumps(dict(json.loads(js_to_json(mobj.group(1) or '[]', vars=vars))))

    code = re.sub(r'(?:new\s+)?Array\((.*?)\)', r'[\g<1>]', code)
    code = re.sub(r'new Map\((\[.*?\])?\)', create_map, code)
    if not strict:
        code = re.sub(r'new Date\(({0})\)'.format(STRING_RE), r'\g<1>', code)
        code = re.sub(r'new \w+\((.*?)\)', lambda m: json.dumps(m.group(0)), code)
        code = re.sub(r'parseInt\([^\d]+(\d+)[^\d]+\)', r'\1', code)
        code = re.sub(r'\(function\([^)]*\)\s*\{[^}]*\}\s*\)\s*\(\s*(["\'][^)]*["\'])\s*\)', r'\1', code)
    return re.sub(r'''(?sx)
        {0}|
        {1}|,(?={2}[\]}}])|
        void\s0|(?:(?<![0-9])[eE]|[a-df-zA-DF-Z_$])[.a-zA-Z_$0-9]*|
        \b(?:0[xX][0-9a-fA-F]+|0+[0-7]+)(?:{2}:)?|
        [0-9]+(?={2}:)|
        !+
        '''.format(STRING_RE, COMMENT_RE, SKIP_RE), fix_kv, code)


def qualities(quality_ids):
    def q(qid):
        try:
            return quality_ids.index(qid)
        except ValueError:
            return -1
    return q


POSTPROCESS_WHEN = ('pre_process', 'after_filter', 'video', 'before_dl', 'post_process', 'after_move', 'after_video', 'playlist')
DEFAULT_OUTTMPL = {
    'default': '%(title)s [%(id)s].%(ext)s',
    'chapter': '%(title)s - %(section_number)03d %(section_title)s [%(id)s].%(ext)s',
}
OUTTMPL_TYPES = {
    'chapter': None, 'subtitle': None, 'thumbnail': None,
    'description': 'description', 'annotation': 'annotations.xml',
    'infojson': 'info.json', 'link': None, 'pl_video': None,
    'pl_thumbnail': None, 'pl_description': 'description',
    'pl_infojson': 'info.json',
}
STR_FORMAT_RE_TMPL = r'''(?x)
    (?<!%)(?P<prefix>(?:%%)*)
    %
    (?P<has_key>\((?P<key>{0})\))?
    (?P<format>
        (?P<conversion>[#0\-+ ]+)?
        (?P<min_width>\d+)?
        (?P<precision>\.\d+)?
        (?P<len_mod>[hlL])?
        {1}
    )
'''
STR_FORMAT_TYPES = 'diouxXeEfFgGcrsa'


def limit_length(s, length):
    if s is None:
        return None
    ELLIPSES = '...'
    if len(s) > length:
        return s[:length - len(ELLIPSES)] + ELLIPSES
    return s


def version_tuple(v):
    return tuple(int(e) for e in re.split(r'[-.]', v))


def is_outdated_version(version, limit, assume_new=True):
    if not version:
        return not assume_new
    try:
        return version_tuple(version) < version_tuple(limit)
    except ValueError:
        return not assume_new


def ytdl_is_updateable():
    from ..update import is_non_updateable
    return not is_non_updateable()


def args_to_str(args):
    return shell_quote(args)


def error_to_str(err):
    return '{0}: {1}'.format(type(err).__name__, err)


@partial_application
def mimetype2ext(mt, default=NO_DEFAULT):
    if not isinstance(mt, str):
        if default is not NO_DEFAULT:
            return default
        return None
    MAP = {
        '3gpp': '3gp', 'mp2t': 'ts', 'mp4': 'mp4', 'mpeg': 'mpeg', 'mpegurl': 'm3u8',
        'quicktime': 'mov', 'webm': 'webm', 'vp9': 'vp9', 'video/ogg': 'ogv',
        'x-flv': 'flv', 'x-m4v': 'm4v', 'x-matroska': 'mkv', 'x-mng': 'mng',
        'x-mp4-fragmented': 'mp4', 'x-ms-asf': 'asf', 'x-ms-wmv': 'wmv', 'x-msvideo': 'avi',
        'dash+xml': 'mpd', 'f4m+xml': 'f4m', 'hds+xml': 'f4m',
        'vnd.apple.mpegurl': 'm3u8', 'vnd.ms-sstr+xml': 'ism', 'x-mpegurl': 'm3u8',
        'audio/mp4': 'm4a', 'audio/mpeg': 'mp3', 'audio/webm': 'webm',
        'audio/x-matroska': 'mka', 'audio/x-mpegurl': 'm3u', 'aacp': 'aac',
        'flac': 'flac', 'midi': 'mid', 'ogg': 'ogg', 'wav': 'wav', 'wave': 'wav',
        'x-aac': 'aac', 'x-flac': 'flac', 'x-m4a': 'm4a', 'x-realaudio': 'ra', 'x-wav': 'wav',
        'avif': 'avif', 'bmp': 'bmp', 'gif': 'gif', 'jpeg': 'jpg', 'png': 'png',
        'svg+xml': 'svg', 'tiff': 'tif', 'vnd.wap.wbmp': 'wbmp', 'webp': 'webp',
        'x-icon': 'ico', 'x-jng': 'jng', 'x-ms-bmp': 'bmp',
        'filmstrip+json': 'fs', 'smptett+xml': 'tt', 'ttaf+xml': 'dfxp', 'ttml+xml': 'ttml', 'x-ms-sami': 'sami',
        'gzip': 'gz', 'json': 'json', 'xml': 'xml', 'zip': 'zip',
    }
    mimetype = mt.partition(';')[0].strip().lower()
    _, _, subtype = mimetype.rpartition('/')
    ext = traversal.traverse_obj(MAP, mimetype, subtype, subtype.rsplit('+')[-1])
    if ext:
        return ext
    elif default is not NO_DEFAULT:
        return default
    return subtype.replace('+', '.')


def ext2mimetype(ext_or_url):
    if not ext_or_url:
        return None
    if '.' not in ext_or_url:
        ext_or_url = 'file.{0}'.format(ext_or_url)
    return mimetypes.guess_type(ext_or_url)[0]


def parse_codecs(codecs_str):
    if not codecs_str:
        return {}
    split_codecs = list(filter(None, map(
        str.strip, codecs_str.strip().strip(',').split(','))))
    vcodec, acodec, scodec, hdr = None, None, None, None
    for full_codec in split_codecs:
        full_codec = re.sub(r'^([^.]+)', lambda m: m.group(1).lower(), full_codec)
        parts = re.sub(r'0+(?=\d)', '', full_codec).split('.')
        if parts[0] in ('avc1', 'avc2', 'avc3', 'avc4', 'vp9', 'vp8', 'hev1', 'hev2',
                        'h263', 'h264', 'mp4v', 'hvc1', 'av1', 'theora', 'dvh1', 'dvhe'):
            if vcodec:
                continue
            vcodec = full_codec
            if parts[0] in ('dvh1', 'dvhe'):
                hdr = 'DV'
            elif parts[0] == 'av1' and traversal.traverse_obj(parts, 3) == '10':
                hdr = 'HDR10'
            elif parts[:2] == ['vp9', '2']:
                hdr = 'HDR10'
        elif parts[0] in ('flac', 'mp4a', 'opus', 'vorbis', 'mp3', 'aac', 'ac-4',
                          'ac-3', 'ec-3', 'eac3', 'dtsc', 'dtse', 'dtsh', 'dtsl'):
            acodec = acodec or full_codec
        elif parts[0] in ('stpp', 'wvtt'):
            scodec = scodec or full_codec
        else:
            write_string('WARNING: Unknown codec {0}\n'.format(full_codec))
    if vcodec or acodec or scodec:
        return {
            'vcodec': vcodec or 'none',
            'acodec': acodec or 'none',
            'dynamic_range': hdr,
            'scodec': scodec,
        } if scodec is not None else {
            'vcodec': vcodec or 'none',
            'acodec': acodec or 'none',
            'dynamic_range': hdr,
        }
    elif len(split_codecs) == 2:
        return {
            'vcodec': split_codecs[0],
            'acodec': split_codecs[1],
        }
    return {}


def get_compatible_ext(vcodecs, acodecs, vexts, aexts, preferences=None):
    assert len(vcodecs) == len(vexts) and len(acodecs) == len(aexts)
    allow_mkv = not preferences or 'mkv' in preferences
    if allow_mkv and max(len(acodecs), len(vcodecs)) > 1:
        return 'mkv'
    COMPATIBLE_CODECS = {
        'mp4': {'av1', 'hevc', 'avc1', 'mp4a', 'ac-4', 'h264', 'aacl', 'ec-3'},
        'webm': {'av1', 'vp9', 'vp8', 'opus', 'vrbs', 'vp9x', 'vp8x'},
    }
    sanitize_codec = functools.partial(
        try_get, getter=lambda x: x[0].split('.')[0].replace('0', '').lower())
    vcodec, acodec = sanitize_codec(vcodecs), sanitize_codec(acodecs)
    for ext in preferences or COMPATIBLE_CODECS.keys():
        codec_set = COMPATIBLE_CODECS.get(ext, set())
        if ext == 'mkv' or codec_set.issuperset((vcodec, acodec)):
            return ext
    COMPATIBLE_EXTS = (
        {'mp3', 'mp4', 'm4a', 'm4p', 'm4b', 'm4r', 'm4v', 'ismv', 'isma', 'mov'},
        {'webm', 'weba'},
    )
    for ext in preferences or vexts:
        current_exts = {ext} | set(vexts) | set(aexts)
        if ext == 'mkv' or current_exts == {ext} or any(
                ext_sets.issuperset(current_exts) for ext_sets in COMPATIBLE_EXTS):
            return ext
    return 'mkv' if allow_mkv else preferences[-1]


def urlhandle_detect_ext(url_handle, default=NO_DEFAULT):
    getheader = url_handle.headers.get
    cd = getheader('Content-Disposition')
    if cd:
        m = re.match(r'attachment;\s*filename="(?P<filename>[^"]+)"', cd)
        if m:
            ext = determine_ext(m.group('filename'), default_ext=None)
            if ext:
                return ext
    return (
        determine_ext(getheader('x-amz-meta-name'), default_ext=None)
        or getheader('x-amz-meta-file-type')
        or mimetype2ext(getheader('Content-Type'), default=default))


def encode_data_uri(data, mime_type):
    return 'data:{0};base64,{1}'.format(mime_type, base64.b64encode(data).decode('ascii'))


def age_restricted(content_limit, age_limit):
    if age_limit is None:
        return False
    if content_limit is None:
        return False
    return age_limit < content_limit


BOMS = [
    (b'\xef\xbb\xbf', 'utf-8'),
    (b'\x00\x00\xfe\xff', 'utf-32-be'),
    (b'\xff\xfe\x00\x00', 'utf-32-le'),
    (b'\xff\xfe', 'utf-16-le'),
    (b'\xfe\xff', 'utf-16-be'),
]


def is_html(first_bytes):
    encoding = 'utf-8'
    for bom, enc in BOMS:
        while first_bytes.startswith(bom):
            encoding, first_bytes = enc, first_bytes[len(bom):]
    return re.match(r'\s*<', first_bytes.decode(encoding, 'replace'))


def determine_protocol(info_dict):
    protocol = info_dict.get('protocol')
    if protocol is not None:
        return protocol
    url = sanitize_url(info_dict['url'])
    if url.startswith('rtmp'):
        return 'rtmp'
    elif url.startswith('mms'):
        return 'mms'
    elif url.startswith('rtsp'):
        return 'rtsp'
    ext = determine_ext(url)
    if ext == 'm3u8':
        return 'm3u8' if info_dict.get('is_live') else 'm3u8_native'
    elif ext == 'f4m':
        return 'f4m'
    return urllib_parse.urlparse(url).scheme


def render_table(header_row, data, delim=False, extra_gap=0, hide_empty=False):
    def width(string):
        return len(remove_terminal_sequences(string).replace('\t', ''))

    def get_max_lens(table):
        return [max(width(str(v)) for v in col) for col in zip(*table)]

    def filter_using_list(row, filter_array):
        return [col for take, col in itertools.izip_longest(filter_array, row, fillvalue=True) if take]

    max_lens = get_max_lens(data) if hide_empty else []
    header_row = filter_using_list(header_row, max_lens)
    data = [filter_using_list(row, max_lens) for row in data]
    table = [header_row] + data
    max_lens = get_max_lens(table)
    extra_gap += 1
    if delim:
        table = [header_row, [delim * (ml + extra_gap) for ml in max_lens]] + data
        table[1][-1] = table[1][-1][:-extra_gap * len(delim)]
    for row in table:
        for pos, text in enumerate(map(str, row)):
            if '\t' in text:
                row[pos] = text.replace('\t', ' ' * (max_lens[pos] - width(text))) + ' ' * extra_gap
            else:
                row[pos] = text + ' ' * (max_lens[pos] - width(text) + extra_gap)
    return '\n'.join(''.join(row).rstrip() for row in table)


def _match_one(filter_part, dct, incomplete):
    STRING_OPERATORS = {
        '*=': operator.contains,
        '^=': lambda attr, value: attr.startswith(value),
        '$=': lambda attr, value: attr.endswith(value),
        '~=': lambda attr, value: re.search(value, attr),
    }
    COMPARISON_OPERATORS = STRING_OPERATORS.copy()
    COMPARISON_OPERATORS.update({
        '<=': operator.le, '<': operator.lt, '>=': operator.ge, '>': operator.gt, '=': operator.eq,
    })

    if isinstance(incomplete, bool):
        is_incomplete = lambda _: incomplete
    else:
        is_incomplete = lambda k: k in incomplete
    operator_rex = re.compile(r'''(?x)
        (?P<key>[a-z_]+)
        \s*(?P<negation>!\s*)?(?P<op>{0})(?P<none_inclusive>\s*\?)?\s*
        (?:
            (?P<quote>["\'])(?P<quotedstrval>.+?)(?P=quote)|
            (?P<strval>.+?)
        )
        '''.format('|'.join(map(re.escape, COMPARISON_OPERATORS.keys()))))
    m = operator_rex.fullmatch(filter_part.strip())
    if m:
        m = m.groupdict()
        unnegated_op = COMPARISON_OPERATORS[m['op']]
        op = (lambda attr, value: not unnegated_op(attr, value)) if m['negation'] else unnegated_op
        comparison_value = m['quotedstrval'] or m['strval']
        if m['quote']:
            comparison_value = comparison_value.replace(r'\{0}'.format(m['quote']), m['quote'])
        actual_value = dct.get(m['key'])
        numeric_comparison = None
        if isinstance(actual_value, (int, float)):
            try:
                numeric_comparison = int(comparison_value)
            except ValueError:
                numeric_comparison = parse_filesize(comparison_value)
                if numeric_comparison is None:
                    numeric_comparison = parse_filesize('{0}B'.format(comparison_value))
                if numeric_comparison is None:
                    numeric_comparison = parse_duration(comparison_value)
        if numeric_comparison is not None and m['op'] in STRING_OPERATORS:
            raise ValueError('Operator {0} only supports string values!'.format(m['op']))
        if actual_value is None:
            return is_incomplete(m['key']) or m['none_inclusive']
        return op(actual_value, comparison_value if numeric_comparison is None else numeric_comparison)

    UNARY_OPERATORS = {
        '': lambda v: (v is True) if isinstance(v, bool) else (v is not None),
        '!': lambda v: (v is False) if isinstance(v, bool) else (v is None),
    }
    operator_rex = re.compile(r'''(?x)
        (?P<op>{0})\s*(?P<key>[a-z_]+)
        '''.format('|'.join(map(re.escape, UNARY_OPERATORS.keys()))))
    m = operator_rex.fullmatch(filter_part.strip())
    if m:
        op = UNARY_OPERATORS[m.group('op')]
        actual_value = dct.get(m.group('key'))
        if is_incomplete(m.group('key')) and actual_value is None:
            return True
        return op(actual_value)
    raise ValueError('Invalid filter part {0!r}'.format(filter_part))


def match_str(filter_str, dct, incomplete=False):
    return all(
        _match_one(filter_part.replace(r'\&', '&'), dct, incomplete)
        for filter_part in re.split(r'(?<!\\)&', filter_str))


def match_filter_func(filters, breaking_filters=None):
    if not filters and not breaking_filters:
        return None
    repr_ = '{0}.{1}({2}, {3})'.format(match_filter_func.__module__, match_filter_func.__name__, filters, breaking_filters)
    breaking_filters = match_filter_func(breaking_filters) or (lambda _, __: None)
    filters = set(variadic(filters or []))
    interactive = '-' in filters
    if interactive:
        filters.remove('-')

    @function_with_repr.set_repr(repr_)
    def _match_func(info_dict, incomplete=False):
        ret = breaking_filters(info_dict, incomplete)
        if ret is not None:
            raise RejectedVideoReached(ret)
        if not filters or any(match_str(f, info_dict, incomplete) for f in filters):
            return NO_DEFAULT if interactive and not incomplete else None
        else:
            video_title = info_dict.get('title') or info_dict.get('id') or 'entry'
            filter_str = ') | ('.join(map(str.strip, filters))
            return '{0} does not pass filter ({1}), skipping ..'.format(video_title, filter_str)
    return _match_func


class download_range_func(object):
    def __init__(self, chapters, ranges, from_info=False):
        self.chapters, self.ranges, self.from_info = chapters, ranges, from_info

    def __call__(self, info_dict, ydl):
        warning = ('There are no chapters matching the regex' if info_dict.get('chapters')
                   else 'Cannot match chapters since chapter information is unavailable')
        for regex in self.chapters or []:
            for i, chapter in enumerate(info_dict.get('chapters') or []):
                if re.search(regex, chapter['title']):
                    warning = None
                    yield dict(chapter, index=i)
        if self.chapters and warning:
            ydl.to_screen('[info] {0}: {1}'.format(info_dict["id"], warning))
        for start, end in self.ranges or []:
            yield {
                'start_time': self._handle_negative_timestamp(start, info_dict),
                'end_time': self._handle_negative_timestamp(end, info_dict),
            }
        if self.from_info and (info_dict.get('start_time') or info_dict.get('end_time')):
            yield {
                'start_time': info_dict.get('start_time') or 0,
                'end_time': info_dict.get('end_time') or float('inf'),
            }
        elif not self.ranges and not self.chapters:
            yield {}

    @staticmethod
    def _handle_negative_timestamp(time, info):
        return max(info['duration'] + time, 0) if info.get('duration') and time < 0 else time

    def __eq__(self, other):
        return (isinstance(other, download_range_func)
                and self.chapters == other.chapters and self.ranges == other.ranges)

    def __repr__(self):
        return '{0}.{1}({2}, {3})'.format(__name__, type(self).__name__, self.chapters, self.ranges)


def parse_dfxp_time_expr(time_expr):
    if not time_expr:
        return
    mobj = re.match(r'^(?P<time_offset>{0})s?$'.format(NUMBER_RE), time_expr)
    if mobj:
        return float(mobj.group('time_offset'))
    mobj = re.match(r'^(\d+):(\d\d):(\d\d(?:(?:\.|:)\d+)?)$', time_expr)
    if mobj:
        return 3600 * int(mobj.group(1)) + 60 * int(mobj.group(2)) + float(mobj.group(3).replace(':', '.'))


def srt_subtitles_timecode(seconds):
    return '%02d:%02d:%02d,%03d' % timetuple_from_msec(seconds * 1000)


def ass_subtitles_timecode(seconds):
    time = timetuple_from_msec(seconds * 1000)
    return '%01d:%02d:%02d.%02d' % (time.hours, time.minutes, time.seconds, time.milliseconds / 10)


def dfxp2srt(dfxp_data):
    LEGACY_NAMESPACES = (
        (b'http://www.w3.org/ns/ttml', [
            b'http://www.w3.org/2004/11/ttaf1', b'http://www.w3.org/2006/04/ttaf1',
            b'http://www.w3.org/2006/10/ttaf1',
        ]),
        (b'http://www.w3.org/ns/ttml#styling', [b'http://www.w3.org/ns/ttml#style']),
    )
    SUPPORTED_STYLING = ['color', 'fontFamily', 'fontSize', 'fontStyle', 'fontWeight', 'textDecoration']
    _x = functools.partial(xpath_with_ns, ns_map={
        'xml': 'http://www.w3.org/XML/1998/namespace', 'ttml': 'http://www.w3.org/ns/ttml',
        'tts': 'http://www.w3.org/ns/ttml#styling',
    })
    styles, default_style = {}, {}

    class TTMLPElementParser(object):
        _out = ''
        _unclosed_elements = []
        _applied_styles = []

        def start(self, tag, attrib):
            if tag in (_x('ttml:br'), 'br'):
                self._out += '\n'
            else:
                unclosed_elements = []
                style = {}
                element_style_id = attrib.get('style')
                if default_style:
                    style.update(default_style)
                if element_style_id:
                    style.update(styles.get(element_style_id, {}))
                for prop in SUPPORTED_STYLING:
                    prop_val = attrib.get(_x('tts:' + prop))
                    if prop_val:
                        style[prop] = prop_val
                if style:
                    font = ''
                    for k, v in sorted(style.items()):
                        if self._applied_styles and self._applied_styles[-1].get(k) == v:
                            continue
                        if k == 'color':
                            font += ' color="{0}"'.format(v)
                        elif k == 'fontSize':
                            font += ' size="{0}"'.format(v)
                        elif k == 'fontFamily':
                            font += ' face="{0}"'.format(v)
                        elif k == 'fontWeight' and v == 'bold':
                            self._out += '<b>'
                            unclosed_elements.append('b')
                        elif k == 'fontStyle' and v == 'italic':
                            self._out += '<i>'
                            unclosed_elements.append('i')
                        elif k == 'textDecoration' and v == 'underline':
                            self._out += '<u>'
                            unclosed_elements.append('u')
                    if font:
                        self._out += '<font' + font + '>'
                        unclosed_elements.append('font')
                    applied_style = {}
                    if self._applied_styles:
                        applied_style.update(self._applied_styles[-1])
                    applied_style.update(style)
                    self._applied_styles.append(applied_style)
                self._unclosed_elements.append(unclosed_elements)

        def end(self, tag):
            if tag not in (_x('ttml:br'), 'br'):
                unclosed_elements = self._unclosed_elements.pop()
                for element in reversed(unclosed_elements):
                    self._out += '</{0}>'.format(element)
                if unclosed_elements and self._applied_styles:
                    self._applied_styles.pop()

        def data(self, data):
            self._out += data

        def close(self):
            return self._out.strip()

    dfxp_data = dfxp_data.replace(b'encoding=\'UTF-16\'', b'encoding=\'UTF-8\'')

    def parse_node(node):
        target = TTMLPElementParser()
        parser = xml.etree.ElementTree.XMLParser(target=target)
        parser.feed(xml.etree.ElementTree.tostring(node))
        return parser.close()

    for k, v in LEGACY_NAMESPACES:
        for ns in v:
            dfxp_data = dfxp_data.replace(ns, k)
    dfxp = compat_etree_fromstring(dfxp_data)
    out = []
    paras = dfxp.findall(_x('.//ttml:p')) or dfxp.findall('.//p')
    if not paras:
        raise ValueError('Invalid dfxp/TTML subtitle')
    repeat = False
    while True:
        for style in dfxp.findall(_x('.//ttml:style')):
            style_id = style.get('id') or style.get(_x('xml:id'))
            if not style_id:
                continue
            parent_style_id = style.get('style')
            if parent_style_id:
                if parent_style_id not in styles:
                    repeat = True
                    continue
                styles[style_id] = styles[parent_style_id].copy()
            for prop in SUPPORTED_STYLING:
                prop_val = style.get(_x('tts:' + prop))
                if prop_val:
                    styles.setdefault(style_id, {})[prop] = prop_val
        if repeat:
            repeat = False
        else:
            break
    for p in ('body', 'div'):
        ele = xpath_element(dfxp, [_x('.//ttml:' + p), './/' + p])
        if ele is None:
            continue
        style = styles.get(ele.get('style'))
        if not style:
            continue
        default_style.update(style)
    for para, index in zip(paras, itertools.count(1)):
        begin_time = parse_dfxp_time_expr(para.attrib.get('begin'))
        end_time = parse_dfxp_time_expr(para.attrib.get('end'))
        dur = parse_dfxp_time_expr(para.attrib.get('dur'))
        if begin_time is None:
            continue
        if not end_time:
            if not dur:
                continue
            end_time = begin_time + dur
        out.append('%d\n%s --> %s\n%s\n\n' % (
            index, srt_subtitles_timecode(begin_time),
            srt_subtitles_timecode(end_time), parse_node(para)))
    return ''.join(out)


def cli_option(params, command_option, param, separator=None):
    param = params.get(param)
    return ([] if param is None
            else [command_option, str(param)] if separator is None
            else ['{0}{1}{2}'.format(command_option, separator, param)])


def cli_bool_option(params, command_option, param, true_value='true', false_value='false', separator=None):
    param = params.get(param)
    assert param in (True, False, None)
    return cli_option({True: true_value, False: false_value}, command_option, param, separator)


def cli_valueless_option(params, command_option, param, expected_value=True):
    return [command_option] if params.get(param) == expected_value else []


def cli_configuration_args(argdict, keys, default=[], use_compat=True):
    if isinstance(argdict, (list, tuple)):
        if use_compat:
            return argdict
        else:
            argdict = None
    if argdict is None:
        return default
    assert isinstance(argdict, dict)
    assert isinstance(keys, (list, tuple))
    for key_list in keys:
        arg_list = list(filter(
            lambda x: x is not None,
            [argdict.get(key.lower()) for key in variadic(key_list)]))
        if arg_list:
            return [arg for args in arg_list for arg in args]
    return default


def _configuration_args(main_key, argdict, exe, keys=None, default=[], use_compat=True):
    main_key, exe = main_key.lower(), exe.lower()
    root_key = exe if main_key == exe else '{0}+{1}'.format(main_key, exe)
    keys = ['{0}{1}'.format(root_key, k) for k in (keys or [''])]
    if root_key in keys:
        if main_key != exe:
            keys.append((main_key, exe))
        keys.append('default')
    else:
        use_compat = False
    return cli_configuration_args(argdict, keys, default, use_compat)


class ISO639Utils(object):
    _lang_map = {
        'aa': 'aar', 'ab': 'abk', 'ae': 'ave', 'af': 'afr', 'ak': 'aka', 'am': 'amh',
        'an': 'arg', 'ar': 'ara', 'as': 'asm', 'av': 'ava', 'ay': 'aym', 'az': 'aze',
        'ba': 'bak', 'be': 'bel', 'bg': 'bul', 'bh': 'bih', 'bi': 'bis', 'bm': 'bam',
        'bn': 'ben', 'bo': 'bod', 'br': 'bre', 'bs': 'bos', 'ca': 'cat', 'ce': 'che',
        'ch': 'cha', 'co': 'cos', 'cr': 'cre', 'cs': 'ces', 'cu': 'chu', 'cv': 'chv',
        'cy': 'cym', 'da': 'dan', 'de': 'deu', 'dv': 'div', 'dz': 'dzo', 'ee': 'ewe',
        'el': 'ell', 'en': 'eng', 'eo': 'epo', 'es': 'spa', 'et': 'est', 'eu': 'eus',
        'fa': 'fas', 'ff': 'ful', 'fi': 'fin', 'fj': 'fij', 'fo': 'fao', 'fr': 'fra',
        'fy': 'fry', 'ga': 'gle', 'gd': 'gla', 'gl': 'glg', 'gn': 'grn', 'gu': 'guj',
        'gv': 'glv', 'ha': 'hau', 'he': 'heb', 'iw': 'heb', 'hi': 'hin', 'ho': 'hmo',
        'hr': 'hrv', 'ht': 'hat', 'hu': 'hun', 'hy': 'hye', 'hz': 'her', 'ia': 'ina',
        'id': 'ind', 'in': 'ind', 'ie': 'ile', 'ig': 'ibo', 'ii': 'iii', 'ik': 'ipk',
        'io': 'ido', 'is': 'isl', 'it': 'ita', 'iu': 'iku', 'ja': 'jpn', 'jv': 'jav',
        'ka': 'kat', 'kg': 'kon', 'ki': 'kik', 'kj': 'kua', 'kk': 'kaz', 'kl': 'kal',
        'km': 'khm', 'kn': 'kan', 'ko': 'kor', 'kr': 'kau', 'ks': 'kas', 'ku': 'kur',
        'kv': 'kom', 'kw': 'cor', 'ky': 'kir', 'la': 'lat', 'lb': 'ltz', 'lg': 'lug',
        'li': 'lim', 'ln': 'lin', 'lo': 'lao', 'lt': 'lit', 'lu': 'lub', 'lv': 'lav',
        'mg': 'mlg', 'mh': 'mah', 'mi': 'mri', 'mk': 'mkd', 'ml': 'mal', 'mn': 'mon',
        'mr': 'mar', 'ms': 'msa', 'mt': 'mlt', 'my': 'mya', 'na': 'nau', 'nb': 'nob',
        'nd': 'nde', 'ne': 'nep', 'ng': 'ndo', 'nl': 'nld', 'nn': 'nno', 'no': 'nor',
        'nr': 'nbl', 'nv': 'nav', 'ny': 'nya', 'oc': 'oci', 'oj': 'oji', 'om': 'orm',
        'or': 'ori', 'os': 'oss', 'pa': 'pan', 'pe': 'per', 'pi': 'pli', 'pl': 'pol',
        'ps': 'pus', 'pt': 'por', 'qu': 'que', 'rm': 'roh', 'rn': 'run', 'ro': 'ron',
        'ru': 'rus', 'rw': 'kin', 'sa': 'san', 'sc': 'srd', 'sd': 'snd', 'se': 'sme',
        'sg': 'sag', 'si': 'sin', 'sk': 'slk', 'sl': 'slv', 'sm': 'smo', 'sn': 'sna',
        'so': 'som', 'sq': 'sqi', 'sr': 'srp', 'ss': 'ssw', 'st': 'sot', 'su': 'sun',
        'sv': 'swe', 'sw': 'swa', 'ta': 'tam', 'te': 'tel', 'tg': 'tgk', 'th': 'tha',
        'ti': 'tir', 'tk': 'tuk', 'tl': 'tgl', 'tn': 'tsn', 'to': 'ton', 'tr': 'tur',
        'ts': 'tso', 'tt': 'tat', 'tw': 'twi', 'ty': 'tah', 'ug': 'uig', 'uk': 'ukr',
        'ur': 'urd', 'uz': 'uzb', 've': 'ven', 'vi': 'vie', 'vo': 'vol', 'wa': 'wln',
        'wo': 'wol', 'xh': 'xho', 'yi': 'yid', 'ji': 'yid', 'yo': 'yor', 'za': 'zha',
        'zh': 'zho', 'zu': 'zul',
    }

    @classmethod
    def short2long(cls, code):
        return cls._lang_map.get(code[:2])

    @classmethod
    def long2short(cls, code):
        for short_name, long_name in cls._lang_map.items():
            if long_name == code:
                return short_name


class ISO3166Utils(object):
    _country_map = {
        'AF': 'Afghanistan', 'AX': 'Åland Islands', 'AL': 'Albania', 'DZ': 'Algeria',
        'AS': 'American Samoa', 'AD': 'Andorra', 'AO': 'Angola', 'AI': 'Anguilla',
        'AQ': 'Antarctica', 'AG': 'Antigua and Barbuda', 'AR': 'Argentina', 'AM': 'Armenia',
        'AW': 'Aruba', 'AU': 'Australia', 'AT': 'Austria', 'AZ': 'Azerbaijan',
        'BS': 'Bahamas', 'BH': 'Bahrain', 'BD': 'Bangladesh', 'BB': 'Barbados',
        'BY': 'Belarus', 'BE': 'Belgium', 'BZ': 'Belize', 'BJ': 'Benin', 'BM': 'Bermuda',
        'BT': 'Bhutan', 'BO': 'Bolivia, Plurinational State of', 'BQ': 'Bonaire, Sint Eustatius and Saba',
        'BA': 'Bosnia and Herzegovina', 'BW': 'Botswana', 'BV': 'Bouvet Island', 'BR': 'Brazil',
        'IO': 'British Indian Ocean Territory', 'BN': 'Brunei Darussalam', 'BG': 'Bulgaria',
        'BF': 'Burkina Faso', 'BI': 'Burundi', 'KH': 'Cambodia', 'CM': 'Cameroon',
        'CA': 'Canada', 'CV': 'Cape Verde', 'KY': 'Cayman Islands', 'CF': 'Central African Republic',
        'TD': 'Chad', 'CL': 'Chile', 'CN': 'China', 'CX': 'Christmas Island',
        'CC': 'Cocos (Keeling) Islands', 'CO': 'Colombia', 'KM': 'Comoros', 'CG': 'Congo',
        'CD': 'Congo, the Democratic Republic of the', 'CK': 'Cook Islands', 'CR': 'Costa Rica',
        'CI': 'Côte d\'Ivoire', 'HR': 'Croatia', 'CU': 'Cuba', 'CW': 'Curaçao',
        'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DK': 'Denmark', 'DJ': 'Djibouti',
        'DM': 'Dominica', 'DO': 'Dominican Republic', 'EC': 'Ecuador', 'EG': 'Egypt',
        'SV': 'El Salvador', 'GQ': 'Equatorial Guinea', 'ER': 'Eritrea', 'EE': 'Estonia',
        'ET': 'Ethiopia', 'FK': 'Falkland Islands (Malvinas)', 'FO': 'Faroe Islands', 'FJ': 'Fiji',
        'FI': 'Finland', 'FR': 'France', 'GF': 'French Guiana', 'PF': 'French Polynesia',
        'TF': 'French Southern Territories', 'GA': 'Gabon', 'GM': 'Gambia', 'GE': 'Georgia',
        'DE': 'Germany', 'GH': 'Ghana', 'GI': 'Gibraltar', 'GR': 'Greece', 'GL': 'Greenland',
        'GD': 'Grenada', 'GP': 'Guadeloupe', 'GU': 'Guam', 'GT': 'Guatemala',
        'GG': 'Guernsey', 'GN': 'Guinea', 'GW': 'Guinea-Bissau', 'GY': 'Guyana',
        'HT': 'Haiti', 'HM': 'Heard Island and McDonald Islands', 'VA': 'Holy See (Vatican City State)',
        'HN': 'Honduras', 'HK': 'Hong Kong', 'HU': 'Hungary', 'IS': 'Iceland',
        'IN': 'India', 'ID': 'Indonesia', 'IR': 'Iran, Islamic Republic of', 'IQ': 'Iraq',
        'IE': 'Ireland', 'IM': 'Isle of Man', 'IL': 'Israel', 'IT': 'Italy',
        'JM': 'Jamaica', 'JP': 'Japan', 'JE': 'Jersey', 'JO': 'Jordan', 'KZ': 'Kazakhstan',
        'KE': 'Kenya', 'KI': 'Kiribati', 'KP': 'Korea, Democratic People\'s Republic of',
        'KR': 'Korea, Republic of', 'KW': 'Kuwait', 'KG': 'Kyrgyzstan', 'LA': 'Lao People\'s Democratic Republic',
        'LV': 'Latvia', 'LB': 'Lebanon', 'LS': 'Lesotho', 'LR': 'Liberia', 'LY': 'Libya',
        'LI': 'Liechtenstein', 'LT': 'Lithuania', 'LU': 'Luxembourg', 'MO': 'Macao',
        'MK': 'Macedonia, the Former Yugoslav Republic of', 'MG': 'Madagascar', 'MW': 'Malawi',
        'MY': 'Malaysia', 'MV': 'Maldives', 'ML': 'Mali', 'MT': 'Malta', 'MH': 'Marshall Islands',
        'MQ': 'Martinique', 'MR': 'Mauritania', 'MU': 'Mauritius', 'YT': 'Mayotte',
        'MX': 'Mexico', 'FM': 'Micronesia, Federated States of', 'MD': 'Moldova, Republic of',
        'MC': 'Monaco', 'MN': 'Mongolia', 'ME': 'Montenegro', 'MS': 'Montserrat',
        'MA': 'Morocco', 'MZ': 'Mozambique', 'MM': 'Myanmar', 'NA': 'Namibia',
        'NR': 'Nauru', 'NP': 'Nepal', 'NL': 'Netherlands', 'NC': 'New Caledonia',
        'NZ': 'New Zealand', 'NI': 'Nicaragua', 'NE': 'Niger', 'NG': 'Nigeria',
        'NU': 'Niue', 'NF': 'Norfolk Island', 'MP': 'Northern Mariana Islands', 'NO': 'Norway',
        'OM': 'Oman', 'PK': 'Pakistan', 'PW': 'Palau', 'PS': 'Palestine, State of',
        'PA': 'Panama', 'PG': 'Papua New Guinea', 'PY': 'Paraguay', 'PE': 'Peru',
        'PH': 'Philippines', 'PN': 'Pitcairn', 'PL': 'Poland', 'PT': 'Portugal',
        'PR': 'Puerto Rico', 'QA': 'Qatar', 'RE': 'Réunion', 'RO': 'Romania',
        'RU': 'Russian Federation', 'RW': 'Rwanda', 'BL': 'Saint Barthélemy',
        'SH': 'Saint Helena, Ascension and Tristan da Cunha', 'KN': 'Saint Kitts and Nevis',
        'LC': 'Saint Lucia', 'MF': 'Saint Martin (French part)', 'PM': 'Saint Pierre and Miquelon',
        'VC': 'Saint Vincent and the Grenadines', 'WS': 'Samoa', 'SM': 'San Marino',
        'ST': 'Sao Tome and Principe', 'SA': 'Saudi Arabia', 'SN': 'Senegal', 'RS': 'Serbia',
        'SC': 'Seychelles', 'SL': 'Sierra Leone', 'SG': 'Singapore', 'SX': 'Sint Maarten (Dutch part)',
        'SK': 'Slovakia', 'SI': 'Slovenia', 'SB': 'Solomon Islands', 'SO': 'Somalia',
        'ZA': 'South Africa', 'GS': 'South Georgia and the South Sandwich Islands', 'SS': 'South Sudan',
        'ES': 'Spain', 'LK': 'Sri Lanka', 'SD': 'Sudan', 'SR': 'Suriname',
        'SJ': 'Svalbard and Jan Mayen', 'SZ': 'Swaziland', 'SE': 'Sweden', 'CH': 'Switzerland',
        'SY': 'Syrian Arab Republic', 'TW': 'Taiwan, Province of China', 'TJ': 'Tajikistan',
        'TZ': 'Tanzania, United Republic of', 'TH': 'Thailand', 'TL': 'Timor-Leste', 'TG': 'Togo',
        'TK': 'Tokelau', 'TO': 'Tonga', 'TT': 'Trinidad and Tobago', 'TN': 'Tunisia',
        'TR': 'Turkey', 'TM': 'Turkmenistan', 'TC': 'Turks and Caicos Islands', 'TV': 'Tuvalu',
        'UG': 'Uganda', 'UA': 'Ukraine', 'AE': 'United Arab Emirates', 'GB': 'United Kingdom',
        'US': 'United States', 'UM': 'United States Minor Outlying Islands', 'UY': 'Uruguay',
        'UZ': 'Uzbekistan', 'VU': 'Vanuatu', 'VE': 'Venezuela, Bolivarian Republic of',
        'VN': 'Viet Nam', 'VG': 'Virgin Islands, British', 'VI': 'Virgin Islands, U.S.',
        'WF': 'Wallis and Futuna', 'EH': 'Western Sahara', 'YE': 'Yemen', 'ZM': 'Zambia',
        'ZW': 'Zimbabwe', 'AP': 'Asia/Pacific Region', 'EU': 'Europe',
    }

    @classmethod
    def short2full(cls, code):
        return cls._country_map.get(code.upper())


class GeoUtils(object):
    _country_ip_map = {
        'AD': '46.172.224.0/19', 'AE': '94.200.0.0/13', 'AF': '149.54.0.0/17',
        'AG': '209.59.64.0/18', 'AI': '204.14.248.0/21', 'AL': '46.99.0.0/16',
        'AM': '46.70.0.0/15', 'AO': '105.168.0.0/13', 'AP': '182.50.184.0/21',
        'AQ': '23.154.160.0/24', 'AR': '181.0.0.0/12', 'AS': '202.70.112.0/20',
        'AT': '77.116.0.0/14', 'AU': '1.128.0.0/11', 'AW': '181.41.0.0/18',
        'AX': '185.217.4.0/22', 'AZ': '5.197.0.0/16', 'BA': '31.176.128.0/17',
        'BB': '65.48.128.0/17', 'BD': '114.130.0.0/16', 'BE': '57.0.0.0/8',
        'BF': '102.178.0.0/15', 'BG': '95.42.0.0/15', 'BH': '37.131.0.0/17',
        'BI': '154.117.192.0/18', 'BJ': '137.255.0.0/16', 'BL': '185.212.72.0/23',
        'BM': '196.12.64.0/18', 'BN': '156.31.0.0/16', 'BO': '161.56.0.0/16',
        'BQ': '161.0.80.0/20', 'BR': '191.128.0.0/12', 'BS': '24.51.64.0/18',
        'BT': '119.2.96.0/19', 'BW': '168.167.0.0/16', 'BY': '178.120.0.0/13',
        'BZ': '179.42.192.0/18', 'CA': '99.224.0.0/11', 'CD': '41.243.0.0/16',
        'CF': '197.242.176.0/21', 'CG': '160.113.0.0/16', 'CH': '85.0.0.0/13',
        'CI': '102.136.0.0/14', 'CK': '202.65.32.0/19', 'CL': '152.172.0.0/14',
        'CM': '102.244.0.0/14', 'CN': '36.128.0.0/10', 'CO': '181.240.0.0/12',
        'CR': '201.192.0.0/12', 'CU': '152.206.0.0/15', 'CV': '165.90.96.0/19',
        'CW': '190.88.128.0/17', 'CY': '31.153.0.0/16', 'CZ': '88.100.0.0/14',
        'DE': '53.0.0.0/8', 'DJ': '197.241.0.0/17', 'DK': '87.48.0.0/12',
        'DM': '192.243.48.0/20', 'DO': '152.166.0.0/15', 'DZ': '41.96.0.0/12',
        'EC': '186.68.0.0/15', 'EE': '90.190.0.0/15', 'EG': '156.160.0.0/11',
        'ER': '196.200.96.0/20', 'ES': '88.0.0.0/11', 'ET': '196.188.0.0/14',
        'EU': '2.16.0.0/13', 'FI': '91.152.0.0/13', 'FJ': '144.120.0.0/16',
        'FK': '80.73.208.0/21', 'FM': '119.252.112.0/20', 'FO': '88.85.32.0/19',
        'FR': '90.0.0.0/9', 'GA': '41.158.0.0/15', 'GB': '25.0.0.0/8',
        'GD': '74.122.88.0/21', 'GE': '31.146.0.0/16', 'GF': '161.22.64.0/18',
        'GG': '62.68.160.0/19', 'GH': '154.160.0.0/12', 'GI': '95.164.0.0/16',
        'GL': '88.83.0.0/19', 'GM': '160.182.0.0/15', 'GN': '197.149.192.0/18',
        'GP': '104.250.0.0/19', 'GQ': '105.235.224.0/20', 'GR': '94.64.0.0/13',
        'GT': '168.234.0.0/16', 'GU': '168.123.0.0/16', 'GW': '197.214.80.0/20',
        'GY': '181.41.64.0/18', 'HK': '113.252.0.0/14', 'HN': '181.210.0.0/16',
        'HR': '93.136.0.0/13', 'HT': '148.102.128.0/17', 'HU': '84.0.0.0/14',
        'ID': '39.192.0.0/10', 'IE': '87.32.0.0/12', 'IL': '79.176.0.0/13',
        'IM': '5.62.80.0/20', 'IN': '117.192.0.0/10', 'IO': '203.83.48.0/21',
        'IQ': '37.236.0.0/14', 'IR': '2.176.0.0/12', 'IS': '82.221.0.0/16',
        'IT': '79.0.0.0/10', 'JE': '87.244.64.0/18', 'JM': '72.27.0.0/17',
        'JO': '176.29.0.0/16', 'JP': '133.0.0.0/8', 'KE': '105.48.0.0/12',
        'KG': '158.181.128.0/17', 'KH': '36.37.128.0/17', 'KI': '103.25.140.0/22',
        'KM': '197.255.224.0/20', 'KN': '198.167.192.0/19', 'KP': '175.45.176.0/22',
        'KR': '175.192.0.0/10', 'KW': '37.36.0.0/14', 'KY': '64.96.0.0/15',
        'KZ': '2.72.0.0/13', 'LA': '115.84.64.0/18', 'LB': '178.135.0.0/16',
        'LC': '24.92.144.0/20', 'LI': '82.117.0.0/19', 'LK': '112.134.0.0/15',
        'LR': '102.183.0.0/16', 'LS': '129.232.0.0/17', 'LT': '78.56.0.0/13',
        'LU': '188.42.0.0/16', 'LV': '46.109.0.0/16', 'LY': '41.252.0.0/14',
        'MA': '105.128.0.0/11', 'MC': '88.209.64.0/18', 'MD': '37.246.0.0/16',
        'ME': '178.175.0.0/17', 'MF': '74.112.232.0/21', 'MG': '154.126.0.0/17',
        'MH': '117.103.88.0/21', 'MK': '77.28.0.0/15', 'ML': '154.118.128.0/18',
        'MM': '37.111.0.0/17', 'MN': '49.0.128.0/17', 'MO': '60.246.0.0/16',
        'MP': '202.88.64.0/20', 'MQ': '109.203.224.0/19', 'MR': '41.188.64.0/18',
        'MS': '208.90.112.0/22', 'MT': '46.11.0.0/16', 'MU': '105.16.0.0/12',
        'MV': '27.114.128.0/18', 'MW': '102.70.0.0/15', 'MX': '187.192.0.0/11',
        'MY': '175.136.0.0/13', 'MZ': '197.218.0.0/15', 'NA': '41.182.0.0/16',
        'NC': '101.101.0.0/18', 'NE': '197.214.0.0/18', 'NF': '203.17.240.0/22',
        'NG': '105.112.0.0/12', 'NI': '186.76.0.0/15', 'NL': '145.96.0.0/11',
        'NO': '84.208.0.0/13', 'NP': '36.252.0.0/15', 'NR': '203.98.224.0/19',
        'NU': '49.156.48.0/22', 'NZ': '49.224.0.0/14', 'OM': '5.36.0.0/15',
        'PA': '186.72.0.0/15', 'PE': '186.160.0.0/14', 'PF': '123.50.64.0/18',
        'PG': '124.240.192.0/19', 'PH': '49.144.0.0/13', 'PK': '39.32.0.0/11',
        'PL': '83.0.0.0/11', 'PM': '70.36.0.0/20', 'PR': '66.50.0.0/16',
        'PS': '188.161.0.0/16', 'PT': '85.240.0.0/13', 'PW': '202.124.224.0/20',
        'PY': '181.120.0.0/14', 'QA': '37.210.0.0/15', 'RE': '102.35.0.0/16',
        'RO': '79.112.0.0/13', 'RS': '93.86.0.0/15', 'RU': '5.136.0.0/13',
        'RW': '41.186.0.0/16', 'SA': '188.48.0.0/13', 'SB': '202.1.160.0/19',
        'SC': '154.192.0.0/11', 'SD': '102.120.0.0/13', 'SE': '78.64.0.0/12',
        'SG': '8.128.0.0/10', 'SI': '188.196.0.0/14', 'SK': '78.98.0.0/15',
        'SL': '102.143.0.0/17', 'SM': '89.186.32.0/19', 'SN': '41.82.0.0/15',
        'SO': '154.115.192.0/18', 'SR': '186.179.128.0/17', 'SS': '105.235.208.0/21',
        'ST': '197.159.160.0/19', 'SV': '168.243.0.0/16', 'SX': '190.102.0.0/20',
        'SY': '5.0.0.0/16', 'SZ': '41.84.224.0/19', 'TC': '65.255.48.0/20',
        'TD': '154.68.128.0/19', 'TG': '196.168.0.0/14', 'TH': '171.96.0.0/13',
        'TJ': '85.9.128.0/18', 'TK': '27.96.24.0/21', 'TL': '180.189.160.0/20',
        'TM': '95.85.96.0/19', 'TN': '197.0.0.0/11', 'TO': '175.176.144.0/21',
        'TR': '78.160.0.0/11', 'TT': '186.44.0.0/15', 'TV': '202.2.96.0/19',
        'TW': '120.96.0.0/11', 'TZ': '156.156.0.0/14', 'UA': '37.52.0.0/14',
        'UG': '102.80.0.0/13', 'US': '6.0.0.0/8', 'UY': '167.56.0.0/13',
        'UZ': '84.54.64.0/18', 'VA': '212.77.0.0/19', 'VC': '207.191.240.0/21',
        'VE': '186.88.0.0/13', 'VG': '66.81.192.0/20', 'VI': '146.226.0.0/16',
        'VN': '14.160.0.0/11', 'VU': '202.80.32.0/20', 'WF': '117.20.32.0/21',
        'WS': '202.4.32.0/19', 'YE': '134.35.0.0/16', 'YT': '41.242.116.0/22',
        'ZA': '41.0.0.0/11', 'ZM': '102.144.0.0/13', 'ZW': '102.177.192.0/18',
    }

    @classmethod
    def random_ipv4(cls, code_or_block):
        if len(code_or_block) == 2:
            block = cls._country_ip_map.get(code_or_block.upper())
            if not block:
                return None
        else:
            block = code_or_block
        addr, preflen = block.split('/')
        addr_min = struct.unpack('!L', socket.inet_aton(addr))[0]
        addr_max = addr_min | (0xffffffff >> int(preflen))
        return str(socket.inet_ntoa(
            struct.pack('!L', random.randint(addr_min, addr_max))))


def long_to_bytes(n, blocksize=0):
    s = b''
    n = int(n)
    while n > 0:
        s = struct.pack('>I', n & 0xffffffff) + s
        n = n >> 32
    for i in range(len(s)):
        if s[i] != b'\000'[0]:
            break
    else:
        s = b'\000'
        i = 0
    s = s[i:]
    if blocksize > 0 and len(s) % blocksize:
        s = (blocksize - len(s) % blocksize) * b'\000' + s
    return s


def bytes_to_long(s):
    acc = 0
    length = len(s)
    if length % 4:
        extra = (4 - length % 4)
        s = b'\000' * extra + s
        length = length + extra
    for i in range(0, length, 4):
        acc = (acc << 32) + struct.unpack('>I', s[i:i + 4])[0]
    return acc


def ohdave_rsa_encrypt(data, exponent, modulus):
    payload = int(binascii.hexlify(data[::-1]), 16)
    encrypted = pow(payload, exponent, modulus)
    return '{0:x}'.format(encrypted)


def pkcs1pad(data, length):
    if len(data) > length - 11:
        raise ValueError('Input data too long for PKCS#1 padding')
    pseudo_random = [random.randint(0, 254) for _ in range(length - len(data) - 3)]
    return [0, 2] + pseudo_random + [0] + data


def _base_n_table(n, table):
    if not table and not n:
        raise ValueError('Either table or n must be specified')
    table = (table or '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')[:n]
    if n and n != len(table):
        raise ValueError('base {0} exceeds table length {1}'.format(n, len(table)))
    return table


def encode_base_n(num, n=None, table=None):
    table = _base_n_table(n, table)
    if not num:
        return table[0]
    result, base = '', len(table)
    while num:
        result = table[num % base] + result
        num = num // base
    return result


def decode_base_n(string, n=None, table=None):
    table = {char: index for index, char in enumerate(_base_n_table(n, table))}
    result, base = 0, len(table)
    for char in string:
        result = result * base + table[char]
    return result


def decode_packed_codes(code):
    mobj = re.search(PACKED_CODES_RE, code)
    obfuscated_code, base, count, symbols = mobj.groups()
    base = int(base)
    count = int(count)
    symbols = symbols.split('|')
    symbol_table = {}
    while count:
        count -= 1
        base_n_count = encode_base_n(count, base)
        symbol_table[base_n_count] = symbols[count] or base_n_count
    return re.sub(
        r'\b(\w+)\b', lambda mobj: symbol_table[mobj.group(0)],
        obfuscated_code)


def caesar(s, alphabet, shift):
    if shift == 0:
        return s
    l = len(alphabet)
    return ''.join(
        alphabet[(alphabet.index(c) + shift) % l] if c in alphabet else c
        for c in s)


def rot47(s):
    return caesar(s, r'''!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~''', 47)


def parse_m3u8_attributes(attrib):
    info = {}
    for (key, val) in re.findall(r'(?P<key>[A-Z0-9-]+)=(?P<val>"[^"]+"|[^",]+)(?:,|$)', attrib):
        if val.startswith('"'):
            val = val[1:-1]
        info[key] = val
    return info


def urshift(val, n):
    return val >> n if val >= 0 else (val + 0x100000000) >> n


def write_xattr(path, key, value):
    if os.name == 'nt':
        assert ':' not in key
        assert os.path.exists(path)
        try:
            with open('{0}:{1}'.format(path, key), 'wb') as f:
                f.write(value)
        except OSError as e:
            raise XAttrMetadataError(e.errno, e.strerror)
        return
    setxattr = None
    if callable(getattr(os, 'setxattr', None)):
        setxattr = os.setxattr
    elif getattr(xattr, '_yt_dlp__identifier', None) == 'pyxattr':
        if version_tuple(xattr.__version__) >= (0, 5, 0):
            setxattr = xattr.set
    elif xattr:
        setxattr = xattr.setxattr
    if setxattr:
        try:
            setxattr(path, key, value)
        except OSError as e:
            raise XAttrMetadataError(e.errno, e.strerror)
        return
    exe = ('setfattr' if check_executable('setfattr', ['--version'])
           else 'xattr' if check_executable('xattr', ['-h']) else None)
    if not exe:
        raise XAttrUnavailableError(
            'Couldn\'t find a tool to set the xattrs. Install either the "xattr" or "pyxattr" Python modules or the '
            + ('"xattr" binary' if sys.platform != 'linux' else 'GNU "attr" package (which contains the "setfattr" tool)'))
    value = value.decode()
    try:
        _, stderr, returncode = Popen.run(
            [exe, '-w', key, value, path] if exe == 'xattr' else [exe, '-n', key, '-v', value, path],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    except OSError as e:
        raise XAttrMetadataError(e.errno, e.strerror)
    if returncode:
        raise XAttrMetadataError(returncode, stderr)


def random_birthday(year_field, month_field, day_field):
    start_date = dt.date(1950, 1, 1)
    end_date = dt.date(1995, 12, 31)
    offset = random.randint(0, (end_date - start_date).days)
    random_date = start_date + dt.timedelta(offset)
    return {
        year_field: str(random_date.year),
        month_field: str(random_date.month),
        day_field: str(random_date.day),
    }


def find_available_port(interface=''):
    try:
        with socket.socket() as sock:
            sock.bind((interface, 0))
            return sock.getsockname()[1]
    except OSError:
        return None


DOT_URL_LINK_TEMPLATE = '''\
[InternetShortcut]
URL=%(url)s
'''
DOT_WEBLOC_LINK_TEMPLATE = '''\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
\t<key>URL</key>
\t<string>%(url)s</string>
</dict>
</plist>
'''
DOT_DESKTOP_LINK_TEMPLATE = '''\
[Desktop Entry]
Encoding=UTF-8
Name=%(filename)s
Type=Link
URL=%(url)s
Icon=text-html
'''
LINK_TEMPLATES = {
    'url': DOT_URL_LINK_TEMPLATE,
    'desktop': DOT_DESKTOP_LINK_TEMPLATE,
    'webloc': DOT_WEBLOC_LINK_TEMPLATE,
}


def iri_to_uri(iri):
    iri_parts = urllib_parse.urlparse(iri)
    if '[' in iri_parts.netloc:
        raise ValueError('IPv6 URIs are not, yet, supported.')
    net_location = ''
    if iri_parts.username:
        net_location += urllib_parse.quote(iri_parts.username, safe=r"!$%&'()*+,~")
        if iri_parts.password is not None:
            net_location += ':' + urllib_parse.quote(iri_parts.password, safe=r"!$%&'()*+,~")
        net_location += '@'
    net_location += iri_parts.hostname.encode('idna').decode()
    if iri_parts.port is not None and iri_parts.port != 80:
        net_location += ':' + str(iri_parts.port)
    return urllib_parse.urlunparse(
        (iri_parts.scheme, net_location,
         urllib_parse.quote_plus(iri_parts.path, safe=r"!$%&'()*+,/:;=@|~"),
         urllib_parse.quote_plus(iri_parts.params, safe=r"!$%&'()*+,/:;=@|~"),
         urllib_parse.quote_plus(iri_parts.query, safe=r"!$%&'()*+,/:;=?@{|}~"),
         urllib_parse.quote_plus(iri_parts.fragment, safe=r"!#$%&'()*+,/:;=?@{|}~")))


def to_high_limit_path(path):
    if sys.platform in ['win32', 'cygwin']:
        return '\\\\?\\' + os.path.abspath(path)
    return path


@partial_application
def format_field(obj, field=None, template='%s', ignore=NO_DEFAULT, default='', func=IDENTITY):
    val = traversal.traverse_obj(obj, *variadic(field))
    if not val if ignore is NO_DEFAULT else val in variadic(ignore):
        return default
    return template % func(val)


def clean_podcast_url(url):
    url = re.sub(r'''(?x)
        (?:(?:chtbl\.com/track|media\.blubrry\.com|play\.podtrac\.com|chrt\.fm/track|mgln\.ai/e)(?:/[^/.]+)?|
        (?:dts|www)\.podtrac\.com/(?:pts/)?redirect\.[0-9a-z]{3,4}|flex\.acast\.com|
        pd(?:cn\.co|st\.fm)/e|[0-9]\.gum\.fm|pscrb\.fm/rss/p)/''', '', url)
    return re.sub(r'^\w+://(\w+://)', r'\1', url)


_HEX_TABLE = '0123456789abcdef'


def random_uuidv4():
    return re.sub(r'[xy]', lambda x: _HEX_TABLE[random.randint(0, 15)], 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx')


def make_dir(path, to_screen=None):
    try:
        dn = os.path.dirname(path)
        if dn:
            os.makedirs(dn, exist_ok=True)
        return True
    except OSError as err:
        if callable(to_screen) is not None:
            to_screen('unable to create directory {0}'.format(err))
        return False


def get_executable_path():
    from ..update import _get_variant_and_executable_path
    return os.path.dirname(os.path.abspath(_get_variant_and_executable_path()[1]))


def get_user_config_dirs(package_name):
    xdg_config_home = os.getenv('XDG_CONFIG_HOME') or compat_expanduser('~/.config')
    yield os.path.join(xdg_config_home, package_name)
    appdata_dir = os.getenv('appdata')
    if appdata_dir:
        yield os.path.join(appdata_dir, package_name)
    yield os.path.join(compat_expanduser('~'), '.{0}'.format(package_name))


def get_system_config_dirs(package_name):
    yield os.path.join('/etc', package_name)


def time_seconds(**kwargs):
    return time.time() + dt.timedelta(**kwargs).total_seconds()


def jwt_encode(payload_data, key, alg='HS256', headers=None):
    assert alg in ('HS256',), 'Unsupported algorithm "{0}"'.format(alg)

    def jwt_json_bytes(obj):
        return json.dumps(obj, separators=(',', ':')).encode()

    def jwt_b64encode(bytestring):
        return base64.urlsafe_b64encode(bytestring).rstrip(b'=')

    header_data = {'alg': alg, 'typ': 'JWT'}
    if headers:
        if 'alg' in headers and 'typ' in headers:
            header_data = headers
        else:
            header_data.update(headers)
    header_b64 = jwt_b64encode(jwt_json_bytes(header_data))
    payload_b64 = jwt_b64encode(jwt_json_bytes(payload_data))
    h = hmac.new(key.encode(), header_b64 + b'.' + payload_b64, hashlib.sha256)
    signature_b64 = jwt_b64encode(h.digest())
    return (header_b64 + b'.' + payload_b64 + b'.' + signature_b64).decode()


def jwt_decode_hs256(jwt):
    header_b64, payload_b64, signature_b64 = jwt.split('.')
    return json.loads(base64.urlsafe_b64decode('{0}==='.format(payload_b64)))


@_functools_cache
def supports_terminal_sequences(stream):
    if os.name == 'nt':
        if not WINDOWS_VT_MODE.value:
            return False
    elif not os.getenv('TERM'):
        return False
    try:
        return stream.isatty()
    except BaseException:
        return False


def windows_enable_vt_mode():
    if get_windows_version() < (10, 0, 10586):
        return
    import ctypes
    import ctypes.wintypes
    import msvcrt
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    dll = ctypes.WinDLL('kernel32', use_last_error=False)
    handle = os.open('CONOUT$', os.O_RDWR)
    try:
        h_out = ctypes.wintypes.HANDLE(msvcrt.get_osfhandle(handle))
        dw_original_mode = ctypes.wintypes.DWORD()
        success = dll.GetConsoleMode(h_out, ctypes.byref(dw_original_mode))
        if not success:
            raise Exception('GetConsoleMode failed')
        success = dll.SetConsoleMode(h_out, ctypes.wintypes.DWORD(
            dw_original_mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING))
        if not success:
            raise Exception('SetConsoleMode failed')
    finally:
        os.close(handle)
    WINDOWS_VT_MODE.value = True
    supports_terminal_sequences.cache_clear()


_terminal_sequences_re = re.compile('\033\\[[^m]+m')


def remove_terminal_sequences(string):
    return _terminal_sequences_re.sub('', string)


def number_of_digits(number):
    return len('%d' % number)


def join_nonempty(*values, **kwargs):
    delim = kwargs.get('delim', '-')
    from_dict = kwargs.get('from_dict')
    if from_dict is not None:
        values = (traversal.traverse_obj(from_dict, variadic(v)) for v in values)
    return delim.join(map(str, filter(None, values)))


def scale_thumbnails_to_max_format_width(formats, thumbnails, url_width_re):
    _keys = ('width', 'height')
    max_dimensions = max(
        (tuple(fmt.get(k) or 0 for k in _keys) for fmt in formats),
        default=(0, 0))
    if not max_dimensions[0]:
        return thumbnails
    return [
        merge_dicts(
            {'url': re.sub(url_width_re, str(max_dimensions[0]), thumbnail['url'])},
            dict(zip(_keys, max_dimensions)), thumbnail)
        for thumbnail in thumbnails
    ]


def parse_http_range(range):
    if not range:
        return None, None, None
    crg = re.search(r'bytes[ =](\d+)-(\d+)?(?:/(\d+))?', range)
    if not crg:
        return None, None, None
    return int(crg.group(1)), int_or_none(crg.group(2)), int_or_none(crg.group(3))


def read_stdin(what):
    if what:
        eof = 'Ctrl+Z' if os.name == 'nt' else 'Ctrl+D'
        write_string('Reading {0} from STDIN - EOF ({1}) to end:\n'.format(what, eof))
    return sys.stdin


def determine_file_encoding(data):
    for bom, enc in BOMS:
        if data.startswith(bom):
            return enc, len(bom)
    data = data.replace(b'\0', b'')
    mobj = re.match(b'(?m)^#\\s*coding\\s*:\\s*(\\S+)\\s*$', data)
    return mobj.group(1).decode() if mobj else None, 0


class Config(object):
    own_args = None
    parsed_args = None
    filename = None
    __initialized = False

    def __init__(self, parser, label=None):
        self.parser, self.label = parser, label
        self._loaded_paths, self.configs = set(), []

    def init(self, args=None, filename=None):
        assert not self.__initialized
        self.own_args, self.filename = args, filename
        return self.load_configs()

    def load_configs(self):
        directory = ''
        if self.filename:
            location = os.path.realpath(self.filename)
            directory = os.path.dirname(location)
            if location in self._loaded_paths:
                return False
            self._loaded_paths.add(location)
        self.__initialized = True
        opts, _ = self.parser.parse_known_args(self.own_args)
        self.parsed_args = self.own_args
        for location in opts.config_locations or []:
            if location == '-':
                if location in self._loaded_paths:
                    continue
                self._loaded_paths.add(location)
                self.append_config(shlex.split(read_stdin('options'), comments=True), label='stdin')
                continue
            location = os.path.join(directory, expand_path(location))
            if os.path.isdir(location):
                location = os.path.join(location, 'yt-dlp.conf')
            if not os.path.exists(location):
                self.parser.error('config location {0} does not exist'.format(location))
            self.append_config(self.read_file(location), location)
        return True

    def __str__(self):
        label = join_nonempty(
            self.label, 'config', '"{0}"'.format(self.filename) if self.filename else '',
            delim=' ')
        return join_nonempty(
            self.own_args is not None and '{0}{1}: {2}'.format(label[0].upper(), label[1:], self.hide_login_info(self.own_args)),
            *('\n{0}'.replace('\n', '\n| ')[1:] for c in self.configs),
            delim='\n')

    @staticmethod
    def read_file(filename, default=[]):
        try:
            optionf = open(filename, 'rb')
        except OSError:
            return default
        try:
            enc, skip = determine_file_encoding(optionf.read(512))
            optionf.seek(skip, io.SEEK_SET)
        except OSError:
            enc = None
        try:
            contents = optionf.read().decode(enc or preferredencoding())
            res = shlex.split(contents, comments=True)
        except Exception as err:
            raise ValueError('Unable to parse "{0}": {1}'.format(filename, err))
        finally:
            optionf.close()
        return res

    @staticmethod
    def hide_login_info(opts):
        PRIVATE_OPTS = {'-p', '--password', '-u', '--username', '--video-password', '--ap-password', '--ap-username'}
        eqre = re.compile('^(?P<key>' + ('|'.join(re.escape(po) for po in PRIVATE_OPTS)) + ')=.+$')

        def _scrub_eq(o):
            m = eqre.match(o)
            if m:
                return m.group('key') + '=PRIVATE'
            else:
                return o
        opts = list(map(_scrub_eq, opts))
        for idx, opt in enumerate(opts):
            if opt in PRIVATE_OPTS and idx + 1 < len(opts):
                opts[idx + 1] = 'PRIVATE'
        return opts

    def append_config(self, *args, **kwargs):
        label = kwargs.get('label')
        config = type(self)(self.parser, label)
        config._loaded_paths = self._loaded_paths
        if config.init(*args):
            self.configs.append(config)

    @property
    def all_args(self):
        for config in reversed(self.configs):
            for arg in config.all_args:
                yield arg
        for arg in self.parsed_args or []:
            yield arg

    def parse_known_args(self, **kwargs):
        return self.parser.parse_known_args(self.all_args, **kwargs)

    def parse_args(self):
        return self.parser.parse_args(self.all_args)


def merge_headers(*dicts):
    return {k.title(): v for k, v in itertools.chain.from_iterable(map(dict.items, dicts))}


def cached_method(f):
    argspec = _getargspec(f)

    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        key = inspect.getcallargs(f, self, *args, **kwargs)
        key = tuple(key.values())[1:]
        cache = vars(self).setdefault('_cached_method__cache', {}).setdefault(f.__name__, {})
        if key not in cache:
            cache[key] = f(self, *args, **kwargs)
        return cache[key]
    return wrapper


class classproperty(object):
    def __init__(self, func, cache=False):
        functools.update_wrapper(self, func)
        self.func = func
        self._cache = {} if cache else None

    def __get__(self, _, cls):
        if self._cache is None:
            return self.func(cls)
        elif cls not in self._cache:
            self._cache[cls] = self.func(cls)
        return self._cache[cls]


class function_with_repr(object):
    def __init__(self, func, repr_=None):
        functools.update_wrapper(self, func)
        self.func, self.__repr = func, repr_

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    @classmethod
    def set_repr(cls, repr_):
        return functools.partial(cls, repr_=repr_)

    def __repr__(self):
        if self.__repr:
            return self.__repr
        return '{0}.{1}'.format(self.func.__module__, self.func.__name__)


class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __iter__(self):
        return iter(self.__dict__.values())

    @property
    def items_(self):
        return self.__dict__.items()


MEDIA_EXTENSIONS = Namespace(
    common_video=('avi', 'flv', 'mkv', 'mov', 'mp4', 'webm'),
    video=('3g2', '3gp', 'f4v', 'mk3d', 'divx', 'mpg', 'ogv', 'm4v', 'wmv'),
    common_audio=('aiff', 'alac', 'flac', 'm4a', 'mka', 'mp3', 'ogg', 'opus', 'wav'),
    audio=('aac', 'ape', 'asf', 'f4a', 'f4b', 'm4r', 'oga', 'ogx', 'spx', 'vorbis', 'wma', 'weba'),
    thumbnails=('jpg', 'png', 'webp'),
    storyboards=('mhtml', ),
    subtitles=('srt', 'vtt', 'ass', 'lrc'),
    manifests=('f4f', 'f4m', 'm3u8', 'smil', 'mpd'),
)
MEDIA_EXTENSIONS.video += MEDIA_EXTENSIONS.common_video
MEDIA_EXTENSIONS.audio += MEDIA_EXTENSIONS.common_audio
KNOWN_EXTENSIONS = MEDIA_EXTENSIONS.video + MEDIA_EXTENSIONS.audio + MEDIA_EXTENSIONS.manifests


class _UnsafeExtensionError(Exception):
    ALLOWED_EXTENSIONS = frozenset([
        'description', 'json', 'meta', 'orig', 'part', 'temp', 'uncut', 'unknown_video', 'ytdl',
        'asx', 'ismv', 'm2t', 'm2ts', 'm2v', 'm4s', 'mng', 'mp2v', 'mp4v', 'mpe', 'mpeg',
        'mpeg1', 'mpeg2', 'mpeg4', 'mxf', 'ogm', 'qt', 'rm', 'swf', 'ts', 'vid', 'vob', 'vp9',
        '3ga', 'ac3', 'adts', 'aif', 'au', 'dts', 'isma', 'it', 'mid', 'mod', 'mpga',
        'mp1', 'mp2', 'mp4a', 'mpa', 'ra', 'shn', 'xm',
        'avif', 'bmp', 'gif', 'heic', 'ico', 'image', 'jfif', 'jng', 'jpe', 'jpeg', 'jxl',
        'svg', 'tif', 'tiff', 'wbmp',
        'dfxp', 'fs', 'ismt', 'json3', 'sami', 'scc', 'srv1', 'srv2', 'srv3', 'ssa', 'tt', 'ttml', 'xml',
        'desktop', 'ism', 'm3u', 'sbv', 'url', 'webloc',
    ] + list(MEDIA_EXTENSIONS.video) + list(MEDIA_EXTENSIONS.audio) + list(MEDIA_EXTENSIONS.thumbnails)
                                     + list(MEDIA_EXTENSIONS.storyboards) + list(MEDIA_EXTENSIONS.subtitles)
                                     + list(MEDIA_EXTENSIONS.manifests))

    def __init__(self, extension):
        super(_UnsafeExtensionError, self).__init__('unsafe file extension: {0!r}'.format(extension))
        self.extension = extension

    @classmethod
    def sanitize_extension(cls, extension, prepend=False):
        if extension is None:
            return None
        if '/' in extension or '\\' in extension:
            raise cls(extension)
        if not prepend:
            _, _, last = extension.rpartition('.')
            if last == 'bin':
                extension = last = 'unknown_video'
            if last.lower() not in cls.ALLOWED_EXTENSIONS:
                raise cls(extension)
        return extension


class RetryManager(object):
    attempt, _error = 0, None

    def __init__(self, _retries, _error_callback, **kwargs):
        self.retries = _retries or 0
        self.error_callback = functools.partial(_error_callback, **kwargs)

    def _should_retry(self):
        return self._error is not NO_DEFAULT and self.attempt <= self.retries

    @property
    def error(self):
        if self._error is NO_DEFAULT:
            return None
        return self._error

    @error.setter
    def error(self, value):
        self._error = value

    def __iter__(self):
        while self._should_retry():
            self.error = NO_DEFAULT
            self.attempt += 1
            yield self
            if self.error:
                self.error_callback(self.error, self.attempt, self.retries)

    @staticmethod
    def report_retry(e, count, retries, sleep_func, info, warn, error=None, suffix=None):
        if count > retries:
            if error:
                return error('{0}. Giving up after {1} retries'.format(e, count - 1)) if count > 1 else error(str(e))
            raise e
        if not count:
            return warn(e)
        elif isinstance(e, ExtractorError):
            e = remove_end(str_or_none(e.cause) or e.orig_msg, '.')
        warn('{0}. Retrying{1} ({2}/{3})...'.format(e, format_field(suffix, None, " %s"), count, retries))
        delay = float_or_none(sleep_func(n=count - 1)) if callable(sleep_func) else sleep_func
        if delay:
            info('Sleeping {0:.2f} seconds ...'.format(delay))
            time.sleep(delay)


@partial_application
def make_archive_id(ie, video_id):
    ie_key = ie if isinstance(ie, str) else ie.ie_key()
    return '{0} {1}'.format(ie_key.lower(), video_id)


@partial_application
def truncate_string(s, left, right=0):
    assert left > 3 and right >= 0
    if s is None or len(s) <= left + right:
        return s
    return '{0}...{1}'.format(s[:left - 3], s[-right:] if right else "")


def orderedSet_from_options(options, alias_dict, use_regex=False, start=None):
    assert 'all' in alias_dict, '"all" alias is required'
    requested = list(start or [])
    for val in options:
        discard = val.startswith('-')
        if discard:
            val = val[1:]
        if val in alias_dict:
            val = alias_dict[val] if not discard else [
                i[1:] if i.startswith('-') else '-{0}'.format(i) for i in alias_dict[val]]
            requested = orderedSet_from_options(val, alias_dict, start=requested)
            continue
        current = (filter(re.compile(val, re.I).fullmatch, alias_dict['all']) if use_regex
                   else [val] if val in alias_dict['all'] else None)
        if current is None:
            raise ValueError(val)
        if discard:
            for item in current:
                while item in requested:
                    requested.remove(item)
        else:
            requested.extend(current)
    return orderedSet(requested)


class FormatSorter(object):
    regex = r' *((?P<reverse>\+)?(?P<field>[a-zA-Z0-9_]+)((?P<separator>[~:])(?P<limit>.*?))?)? *$'
    default = ('hidden', 'aud_or_vid', 'hasvid', 'ie_pref', 'lang', 'quality',
               'res', 'fps', 'hdr:12', 'vcodec', 'channels', 'acodec',
               'size', 'br', 'asr', 'proto', 'ext', 'hasaud', 'source', 'id')
    _prefer_vp9_sort = ('hidden', 'aud_or_vid', 'hasvid', 'ie_pref', 'lang', 'quality',
                        'res', 'fps', 'hdr:12', 'vcodec:vp9.2', 'channels', 'acodec',
                        'size', 'br', 'asr', 'proto', 'ext', 'hasaud', 'source', 'id')
    ytdl_default = ('hasaud', 'lang', 'quality', 'tbr', 'filesize', 'vbr',
                    'height', 'width', 'proto', 'vext', 'abr', 'aext',
                    'fps', 'fs_approx', 'source', 'id')
    settings = {
        'vcodec': {'type': 'ordered', 'regex': True,
                   'order': ['av0?1', r'vp0?9\.0?2', 'vp0?9', '[hx]265|he?vc?', '[hx]264|avc', 'vp0?8', 'mp4v|h263', 'theora', '', None, 'none']},
        'acodec': {'type': 'ordered', 'regex': True,
                   'order': ['[af]lac', 'wav|aiff', 'opus', 'vorbis|ogg', 'aac', 'mp?4a?', 'mp3', 'ac-?4', 'e-?a?c-?3', 'ac-?3', 'dts', '', None, 'none']},
        'hdr': {'type': 'ordered', 'regex': True, 'field': 'dynamic_range',
                'order': ['dv', '(hdr)?12', r'(hdr)?10\+', '(hdr)?10', 'hlg', '', 'sdr', None]},
        'proto': {'type': 'ordered', 'regex': True, 'field': 'protocol',
                  'order': ['(ht|f)tps', '(ht|f)tp$', 'm3u8.*', '.*dash', 'websocket_frag', 'rtmpe?', '', 'mms|rtsp', 'ws|websocket', 'f4']},
        'vext': {'type': 'ordered', 'field': 'video_ext',
                 'order': ('mp4', 'mov', 'webm', 'flv', '', 'none'),
                 'order_free': ('webm', 'mp4', 'mov', 'flv', '', 'none')},
        'aext': {'type': 'ordered', 'regex': True, 'field': 'audio_ext',
                 'order': ('m4a', 'aac', 'mp3', 'ogg', 'opus', 'web[am]', '', 'none'),
                 'order_free': ('ogg', 'opus', 'web[am]', 'mp3', 'm4a', 'aac', '', 'none')},
        'hidden': {'visible': False, 'forced': True, 'type': 'extractor', 'max': -1000},
        'aud_or_vid': {'visible': False, 'forced': True, 'type': 'multiple',
                       'field': ('vcodec', 'acodec'),
                       'function': lambda it: int(any(v != 'none' for v in it))},
        'ie_pref': {'priority': True, 'type': 'extractor'},
        'hasvid': {'priority': True, 'field': 'vcodec', 'type': 'boolean', 'not_in_list': ('none',)},
        'hasaud': {'field': 'acodec', 'type': 'boolean', 'not_in_list': ('none',)},
        'lang': {'convert': 'float', 'field': 'language_preference', 'default': -1},
        'quality': {'convert': 'float', 'default': -1},
        'filesize': {'convert': 'bytes'},
        'fs_approx': {'convert': 'bytes', 'field': 'filesize_approx'},
        'id': {'convert': 'string', 'field': 'format_id'},
        'height': {'convert': 'float_none'},
        'width': {'convert': 'float_none'},
        'fps': {'convert': 'float_none'},
        'channels': {'convert': 'float_none', 'field': 'audio_channels'},
        'tbr': {'convert': 'float_none'},
        'vbr': {'convert': 'float_none'},
        'abr': {'convert': 'float_none'},
        'asr': {'convert': 'float_none'},
        'source': {'convert': 'float', 'field': 'source_preference', 'default': -1},
        'codec': {'type': 'combined', 'field': ('vcodec', 'acodec')},
        'br': {'type': 'multiple', 'field': ('tbr', 'vbr', 'abr'), 'convert': 'float_none',
               'function': lambda it: next(filter(None, it), None)},
        'size': {'type': 'multiple', 'field': ('filesize', 'fs_approx'), 'convert': 'bytes',
                 'function': lambda it: next(filter(None, it), None)},
        'ext': {'type': 'combined', 'field': ('vext', 'aext')},
        'res': {'type': 'multiple', 'field': ('height', 'width'),
                'function': lambda it: min(filter(None, it), default=0)},
        'format_id': {'type': 'alias', 'field': 'id'},
        'preference': {'type': 'alias', 'field': 'ie_pref'},
        'language_preference': {'type': 'alias', 'field': 'lang'},
        'source_preference': {'type': 'alias', 'field': 'source'},
        'protocol': {'type': 'alias', 'field': 'proto'},
        'filesize_approx': {'type': 'alias', 'field': 'fs_approx'},
        'audio_channels': {'type': 'alias', 'field': 'channels'},
        'dimension': {'type': 'alias', 'field': 'res', 'deprecated': True},
        'resolution': {'type': 'alias', 'field': 'res', 'deprecated': True},
        'extension': {'type': 'alias', 'field': 'ext', 'deprecated': True},
        'bitrate': {'type': 'alias', 'field': 'br', 'deprecated': True},
        'total_bitrate': {'type': 'alias', 'field': 'tbr', 'deprecated': True},
        'video_bitrate': {'type': 'alias', 'field': 'vbr', 'deprecated': True},
        'audio_bitrate': {'type': 'alias', 'field': 'abr', 'deprecated': True},
        'framerate': {'type': 'alias', 'field': 'fps', 'deprecated': True},
        'filesize_estimate': {'type': 'alias', 'field': 'size', 'deprecated': True},
        'samplerate': {'type': 'alias', 'field': 'asr', 'deprecated': True},
        'video_ext': {'type': 'alias', 'field': 'vext', 'deprecated': True},
        'audio_ext': {'type': 'alias', 'field': 'aext', 'deprecated': True},
        'video_codec': {'type': 'alias', 'field': 'vcodec', 'deprecated': True},
        'audio_codec': {'type': 'alias', 'field': 'acodec', 'deprecated': True},
        'video': {'type': 'alias', 'field': 'hasvid', 'deprecated': True},
        'has_video': {'type': 'alias', 'field': 'hasvid', 'deprecated': True},
        'audio': {'type': 'alias', 'field': 'hasaud', 'deprecated': True},
        'has_audio': {'type': 'alias', 'field': 'hasaud', 'deprecated': True},
        'extractor': {'type': 'alias', 'field': 'ie_pref', 'deprecated': True},
        'extractor_preference': {'type': 'alias', 'field': 'ie_pref', 'deprecated': True},
    }

    def __init__(self, ydl, field_preference):
        self.ydl = ydl
        self._order = []
        self.evaluate_params(self.ydl.params, field_preference)
        if ydl.params.get('verbose'):
            self.print_verbose_info(self.ydl.write_debug)

    def _get_field_setting(self, field, key):
        if field not in self.settings:
            if key in ('forced', 'priority'):
                return False
            self.ydl.deprecated_feature('Using arbitrary fields ({0}) for format sorting is '
                                        'deprecated and may be removed in a future version'.format(field))
            self.settings[field] = {}
        prop_obj = self.settings[field]
        if key not in prop_obj:
            type_ = prop_obj.get('type')
            if key == 'field':
                default = 'preference' if type_ == 'extractor' else (field,) if type_ in ('combined', 'multiple') else field
            elif key == 'convert':
                default = 'order' if type_ == 'ordered' else 'float_string' if field else 'ignore'
            else:
                default = {'type': 'field', 'visible': True, 'order': [], 'not_in_list': (None,)}.get(key)
            prop_obj[key] = default
        return prop_obj[key]

    def _resolve_field_value(self, field, value, convert_none=False):
        if value is None:
            if not convert_none:
                return None
        else:
            value = value.lower()
        conversion = self._get_field_setting(field, 'convert')
        if conversion == 'ignore':
            return None
        if conversion == 'string':
            return value
        elif conversion == 'float_none':
            return float_or_none(value)
        elif conversion == 'bytes':
            return parse_bytes(value)
        elif conversion == 'order':
            order_list = (self._use_free_order and self._get_field_setting(field, 'order_free')) or self._get_field_setting(field, 'order')
            use_regex = self._get_field_setting(field, 'regex')
            list_length = len(order_list)
            empty_pos = order_list.index('') if '' in order_list else list_length + 1
            if use_regex and value is not None:
                for i, regex in enumerate(order_list):
                    if regex and re.match(regex, value):
                        return list_length - i
                return list_length - empty_pos
            else:
                return list_length - (order_list.index(value) if value in order_list else empty_pos)
        else:
            if value.isnumeric():
                return float(value)
            else:
                self.settings[field]['convert'] = 'string'
                return value

    def evaluate_params(self, params, sort_extractor):
        self._use_free_order = params.get('prefer_free_formats', False)
        self._sort_user = params.get('format_sort', [])
        self._sort_extractor = sort_extractor

        def add_item(field, reverse, closest, limit_text):
            field = field.lower()
            if field in self._order:
                return
            self._order.append(field)
            limit = self._resolve_field_value(field, limit_text)
            data = {'reverse': reverse, 'closest': False if limit is None else closest,
                    'limit_text': limit_text, 'limit': limit}
            if field in self.settings:
                self.settings[field].update(data)
            else:
                self.settings[field] = data

        sort_list = (
            tuple(field for field in self.default if self._get_field_setting(field, 'forced'))
            + (tuple() if params.get('format_sort_force', False)
                else tuple(field for field in self.default if self._get_field_setting(field, 'priority')))
            + tuple(self._sort_user) + tuple(sort_extractor) + self.default)
        for item in sort_list:
            match = re.match(self.regex, item)
            if match is None:
                raise ExtractorError('Invalid format sort string "{0}" given by extractor'.format(item))
            field = match.group('field')
            if field is None:
                continue
            if self._get_field_setting(field, 'type') == 'alias':
                alias, field = field, self._get_field_setting(field, 'field')
                if self._get_field_setting(alias, 'deprecated'):
                    self.ydl.deprecated_feature('Format sorting alias {0} is deprecated and may '
                                                'be removed in a future version. Please use {1} instead'.format(alias, field))
            reverse = match.group('reverse') is not None
            closest = match.group('separator') == '~'
            limit_text = match.group('limit')
            has_limit = limit_text is not None
            has_multiple_fields = self._get_field_setting(field, 'type') == 'combined'
            has_multiple_limits = has_limit and has_multiple_fields and not self._get_field_setting(field, 'same_limit')
            fields = self._get_field_setting(field, 'field') if has_multiple_fields else (field,)
            limits = limit_text.split(':') if has_multiple_limits else (limit_text,) if has_limit else tuple()
            limit_count = len(limits)
            for (i, f) in enumerate(fields):
                add_item(f, reverse, closest,
                         limits[i] if i < limit_count
                         else limits[0] if has_limit and not has_multiple_limits
                         else None)

    def print_verbose_info(self, write_debug):
        if self._sort_user:
            write_debug('Sort order given by user: {0}'.format(', '.join(self._sort_user)))
        if self._sort_extractor:
            write_debug('Sort order given by extractor: {0}'.format(', '.join(self._sort_extractor)))
        write_debug('Formats sorted by: {0}'.format(', '.join(['{0}{1}{2}'.format(
            '+' if self._get_field_setting(field, 'reverse') else '', field,
            '{0}{1}({2})'.format('~' if self._get_field_setting(field, 'closest') else ':',
                                 self._get_field_setting(field, 'limit_text'),
                                 self._get_field_setting(field, 'limit'))
            if self._get_field_setting(field, 'limit_text') is not None else '')
            for field in self._order if self._get_field_setting(field, 'visible')])))

    def _calculate_field_preference_from_value(self, format_, field, type_, value):
        reverse = self._get_field_setting(field, 'reverse')
        closest = self._get_field_setting(field, 'closest')
        limit = self._get_field_setting(field, 'limit')
        if type_ == 'extractor':
            maximum = self._get_field_setting(field, 'max')
            if value is None or (maximum is not None and value >= maximum):
                value = -1
        elif type_ == 'boolean':
            in_list = self._get_field_setting(field, 'in_list')
            not_in_list = self._get_field_setting(field, 'not_in_list')
            value = 0 if ((in_list is None or value in in_list) and (not_in_list is None or value not in not_in_list)) else -1
        elif type_ == 'ordered':
            value = self._resolve_field_value(field, value, True)
        val_num = float_or_none(value, default=self._get_field_setting(field, 'default'))
        is_num = self._get_field_setting(field, 'convert') != 'string' and val_num is not None
        if is_num:
            value = val_num
        return ((-10, 0) if value is None
                else (1, value, 0) if not is_num
                else (0, -abs(value - limit), value - limit if reverse else limit - value) if closest
                else (0, value, 0) if not reverse and (limit is None or value <= limit)
                else (0, -value, 0) if limit is None or (reverse and value == limit) or value > limit
                else (-1, value, 0))

    def _calculate_field_preference(self, format_, field):
        type_ = self._get_field_setting(field, 'type')
        get_value = lambda f: format_.get(self._get_field_setting(f, 'field'))
        if type_ == 'multiple':
            type_ = 'field'
            actual_fields = self._get_field_setting(field, 'field')
            value = self._get_field_setting(field, 'function')(get_value(f) for f in actual_fields)
        else:
            value = get_value(field)
        return self._calculate_field_preference_from_value(format_, field, type_, value)

    @staticmethod
    def _fill_sorting_fields(format):
        if not format.get('protocol'):
            format['protocol'] = determine_protocol(format)
        if not format.get('ext') and 'url' in format:
            format['ext'] = determine_ext(format['url']).lower()
        if format.get('vcodec') == 'none':
            format['audio_ext'] = format['ext'] if format.get('acodec') != 'none' else 'none'
            format['video_ext'] = 'none'
        else:
            format['video_ext'] = format['ext']
            format['audio_ext'] = 'none'
        if format.get('preference') is None and format.get('ext') == 'flv' and re.match('[hx]265|he?vc?', format.get('vcodec') or ''):
            format['preference'] = -100
        if format.get('vcodec') == 'none':
            format['vbr'] = 0
        if format.get('acodec') == 'none':
            format['abr'] = 0
        if not format.get('vbr') and format.get('vcodec') != 'none':
            format['vbr'] = try_call(lambda: format['tbr'] - format['abr']) or None
        if not format.get('abr') and format.get('acodec') != 'none':
            format['abr'] = try_call(lambda: format['tbr'] - format['vbr']) or None
        if not format.get('tbr'):
            format['tbr'] = try_call(lambda: format['vbr'] + format['abr']) or None

    def calculate_preference(self, format):
        self._fill_sorting_fields(format)
        return tuple(self._calculate_field_preference(format, field) for field in self._order)


def filesize_from_tbr(tbr, duration):
    if tbr is None or duration is None:
        return None
    return int(duration * tbr * (1000 / 8))


def _request_dump_filename(url, video_id, data=None, trim_length=None):
    if data is not None:
        data = hashlib.md5(data).hexdigest()
    basen = join_nonempty(video_id, data, url, delim='_')
    trim_length = trim_length or 240
    if len(basen) > trim_length:
        h = '___' + hashlib.md5(basen.encode()).hexdigest()
        basen = basen[:trim_length - len(h)] + h
    filename = sanitize_filename('{0}.dump'.format(basen), restricted=True)
    if os.name == 'nt':
        absfilepath = os.path.abspath(filename)
        if len(absfilepath) > 259:
            filename = r'\\?\{0}'.format(absfilepath)
    return filename


class _YDLLogger(object):
    def __init__(self, ydl=None):
        self._ydl = ydl

    def debug(self, message):
        if self._ydl:
            self._ydl.write_debug(message)

    def info(self, message):
        if self._ydl:
            self._ydl.to_screen(message)

    def warning(self, message, once=False):
        if self._ydl:
            self._ydl.report_warning(message, once)

    def error(self, message, is_error=True):
        if self._ydl:
            self._ydl.report_error(message, is_error=is_error)

    def stdout(self, message):
        if self._ydl:
            self._ydl.to_stdout(message)

    def stderr(self, message):
        if self._ydl:
            self._ydl.to_stderr(message)


class _ProgressState(enum.Enum):
    HIDDEN = 0
    INDETERMINATE = 3
    VISIBLE = 1
    WARNING = 4
    ERROR = 2

    @classmethod
    def from_dict(cls, s):
        if s['status'] == 'finished':
            return cls.INDETERMINATE
        if s['status'] == 'error':
            return cls.ERROR
        return cls.INDETERMINATE if s.get('_percent') is None else cls.VISIBLE

    def get_ansi_escape(self, percent=None):
        percent = 0 if percent is None else int(percent)
        return '\033]9;4;{0};{1}\007'.format(self.value, percent)
