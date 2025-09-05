import collections
try:
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc
import random
from ..dependencies import typing
try:
    import urllib.parse as urllib_parse
    import urllib.request as urllib_request
except ImportError:
    import urlparse as urllib_parse
    import urllib2 as urllib_request

if typing.TYPE_CHECKING:
    T = typing.TypeVar('T')

from ._utils import NO_DEFAULT, remove_start, format_field
from .traversal import traverse_obj


def random_user_agent():
    USER_AGENT_TMPL = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36'
    # Target versions released within the last ~6 months
    CHROME_MAJOR_VERSION_RANGE = (132, 138)
    chrome_version = '{0}.0.0.0'.format(random.randint(*CHROME_MAJOR_VERSION_RANGE))
    return USER_AGENT_TMPL.format(chrome_version)


class HTTPHeaderDict(dict):
    def __new__(cls, *args, **kwargs):
        obj = dict.__new__(cls, *args, **kwargs)
        obj.__sensitive_map = {}
        return obj

    def __init__(self, *args, **kwargs):
        super(HTTPHeaderDict, self).__init__()
        self.__sensitive_map = {}

        for dct in filter(None, args):
            self.update(dct)
        if kwargs:
            self.update(kwargs)

    def sensitive(self):
        return {
            self.__sensitive_map[key]: value
            for key, value in self.items()
        }

    def __contains__(self, key):
        return super(HTTPHeaderDict, self).__contains__(key.title() if isinstance(key, str) else key)

    def __delitem__(self, key):
        key = key.title()
        del self.__sensitive_map[key]
        super(HTTPHeaderDict, self).__delitem__(key)

    def __getitem__(self, key):
        return super(HTTPHeaderDict, self).__getitem__(key.title())

    def __ior__(self, other):
        if isinstance(other, type(self)):
            other = other.sensitive()
        if isinstance(other, dict):
            self.update(other)
            return
        return NotImplemented

    def __or__(self, other):
        if isinstance(other, type(self)):
            other = other.sensitive()
        if isinstance(other, dict):
            return type(self)(self.sensitive(), other)
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, type(self)):
            other = other.sensitive()
        if isinstance(other, dict):
            return type(self)(other, self.sensitive())
        return NotImplemented

    def __setitem__(self, key, value):
        if isinstance(value, bytes):
            value = value.decode('latin-1')
        key_title = key.title()
        self.__sensitive_map[key_title] = key
        super(HTTPHeaderDict, self).__setitem__(key_title, str(value).strip())

    def clear(self):
        self.__sensitive_map.clear()
        super(HTTPHeaderDict, self).clear()

    def copy(self):
        return type(self)(self.sensitive())

    def get(self, key, default=NO_DEFAULT):
        key = key.title()
        if default is NO_DEFAULT:
            return super(HTTPHeaderDict, self).get(key)
        return super(HTTPHeaderDict, self).get(key, default)

    def pop(self, key, default=NO_DEFAULT):
        key = key.title()
        if default is NO_DEFAULT:
            self.__sensitive_map.pop(key)
            return super(HTTPHeaderDict, self).pop(key)
        self.__sensitive_map.pop(key, default)
        return super(HTTPHeaderDict, self).pop(key, default)

    def popitem(self):
        self.__sensitive_map.popitem()
        return super(HTTPHeaderDict, self).popitem()

    def setdefault(self, key, default=None):
        key = key.title()
        if key in self.__sensitive_map:
            return super(HTTPHeaderDict, self).__getitem__(key)

        self[key] = default or ''
        return self[key]

    def update(self, other, **kwargs):
        if isinstance(other, type(self)):
            other = other.sensitive()
        if isinstance(other, collections_abc.Mapping):
            for key, value in other.items():
                self[key] = value

        elif hasattr(other, 'keys'):
            for key in other.keys():
                self[key] = other[key]

        else:
            for key, value in other:
                self[key] = value

        for key, value in kwargs.items():
            self[key] = value


std_headers = HTTPHeaderDict({
    'User-Agent': random_user_agent(),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
    'Sec-Fetch-Mode': 'navigate',
})


def clean_proxies(proxies, headers):
    req_proxy = headers.pop('Ytdl-Request-Proxy', None)
    if req_proxy:
        proxies.clear()  # XXX: compat: Ytdl-Request-Proxy takes preference over everything, including NO_PROXY
        proxies['all'] = req_proxy
    for proxy_key, proxy_url in proxies.items():
        if proxy_url == '__noproxy__':
            proxies[proxy_key] = None
            continue
        if proxy_key == 'no':  # special case
            continue
        if proxy_url is not None:
            # Ensure proxies without a scheme are http.
            try:
                proxy_scheme = urllib.request._parse_proxy(proxy_url)[0]
            except ValueError:
                # Ignore invalid proxy URLs. Sometimes these may be introduced through environment
                # variables unrelated to proxy settings - e.g. Colab `COLAB_LANGUAGE_SERVER_PROXY`.
                # If the proxy is going to be used, the Request Handler proxy validation will handle it.
                continue
            if proxy_scheme is None:
                proxies[proxy_key] = 'http://' + remove_start(proxy_url, '//')

            replace_scheme = {
                'socks5': 'socks5h',  # compat: socks5 was treated as socks5h
                'socks': 'socks4',  # compat: non-standard
            }
            if proxy_scheme in replace_scheme:
                proxies[proxy_key] = urllib_parse.urlunparse(
                    urllib_parse.urlparse(proxy_url)._replace(scheme=replace_scheme[proxy_scheme]))


def clean_headers(headers):
    if 'Youtubedl-No-Compression' in headers:  # compat
        del headers['Youtubedl-No-Compression']
        headers['Accept-Encoding'] = 'identity'
    headers.pop('Ytdl-socks-proxy', None)


def remove_dot_segments(path):
    # Implements RFC3986 5.2.4 remote_dot_segments
    # Pseudo-code: https://tools.ietf.org/html/rfc3986#section-5.2.4
    # https://github.com/urllib3/urllib3/blob/ba49f5c4e19e6bca6827282feb77a3c9f937e64b/src/urllib3/util/url.py#L263
    output = []
    segments = path.split('/')
    for s in segments:
        if s == '.':
            continue
        elif s == '..':
            if output:
                output.pop()
        else:
            output.append(s)
    if not segments[0] and (not output or output[0]):
        output.insert(0, '')
    if segments[-1] in ('.', '..'):
        output.append('')
    return '/'.join(output)


def escape_rfc3986(s):
    """Escape non-ASCII characters as suggested by RFC 3986"""
    return urllib.parse.quote(s, b"%/;:@&=+$,!~*'()?#[]")


def normalize_url(url):
    """Normalize URL as suggested by RFC 3986"""
    url_parsed = urllib_parse.urlparse(url)
    return url_parsed._replace(
        netloc=url_parsed.netloc.encode('idna').decode('ascii'),
        path=escape_rfc3986(remove_dot_segments(url_parsed.path)),
        params=escape_rfc3986(url_parsed.params),
        query=escape_rfc3986(url_parsed.query),
        fragment=escape_rfc3986(url_parsed.fragment),
    ).geturl()


def select_proxy(url, proxies):
    """Unified proxy selector for all backends"""
    url_components = urllib_parse.urlparse(url)
    if 'no' in proxies:
        hostport = url_components.hostname + format_field(url_components.port, None, ':%s')
        if urllib_request.proxy_bypass_environment(hostport, {'no': proxies['no']}):
            return
        elif urllib_request.proxy_bypass(hostport):  # check system settings
            return

    return traverse_obj(proxies, url_components.scheme or 'http', 'all')
