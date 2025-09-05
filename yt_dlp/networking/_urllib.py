from __future__ import absolute_import

import functools
import httplib
import io
import ssl
import urllib2
import urllib
import urlparse
import zlib
from urllib2 import (
    OpenerDirector,
    ProxyHandler as UrllibProxyHandler,
    HTTPRedirectHandler as UrllibRedirectHandler,
    Request as UrllibRequest,
    UnknownHandler,
)

from ..dependencies import brotli
from .common import (
    Request,
    RequestHandler,
    Response,
    register_rh,
)
from .exceptions import (
    CertificateVerifyError,
    Features,
    HTTPError,
    IncompleteRead,
    ProxyError,
    RequestError,
    SSLError,
    TransportError,
)
from ._helper import (
    InstanceStoreMixin,
    add_accept_encoding_header,
    create_ssl_context,
    get_redirect_method,
    make_socks_proxy_opts,
    _socket_connect as create_connection,
    _socks_connect as create_socks_proxy_socket,
)
from ..utils import update_url_query
from ..utils.networking import normalize_url, select_proxy

SUPPORTED_ENCODINGS = [u'gzip', u'deflate']
CONTENT_DECODE_ERRORS = [zlib.error, OSError]

if brotli:
    SUPPORTED_ENCODINGS.append(u'br')
    CONTENT_DECODE_ERRORS.append(brotli.error)


def _create_http_connection(http_class, source_address, *args, **kwargs):
    hc = http_class(*args, **kwargs)

    if hasattr(hc, u'_create_connection'):
        hc._create_connection = create_connection

    if source_address is not None:
        hc.source_address = (source_address, 0)

    return hc


class HTTPHandler(urllib2.AbstractHTTPHandler):
    u"""Handler for HTTP requests and responses.

    This class, when installed with an OpenerDirector, automatically adds
    the standard headers to every HTTP request and handles gzipped, deflated and
    brotli encoded responses.

    It also supports SOCKS proxies. To do so, a handler must be passing a
    `Ytdl-socks-proxy` header in the request.

    This is a subclass of `urllib.request.AbstractHTTPHandler` and not
    `urllib.request.HTTPHandler` since we need to resolve proxies manually.
    """

    def __init__(self, context=None, source_address=None, *args, **kwargs):
        super(HTTPHandler, self).__init__(*args, **kwargs)
        self._source_address = source_address
        self._context = context

    @staticmethod
    def _make_conn_class(base, req):
        conn_class = base
        socks_proxy = req.headers.pop(u'Ytdl-socks-proxy', None)
        if socks_proxy:
            conn_class = make_socks_conn_class(conn_class, socks_proxy)
        return conn_class

    def http_open(self, req):
        conn_class = self._make_conn_class(httplib.HTTPConnection, req)
        return self.do_open(functools.partial(
            _create_http_connection, conn_class, self._source_address), req)

    def https_open(self, req):
        conn_class = self._make_conn_class(httplib.HTTPSConnection, req)
        return self.do_open(
            functools.partial(
                _create_http_connection, conn_class, self._source_address),
            req,
            context=self._context)

    def http_request(self, req):
        add_accept_encoding_header(req.headers, SUPPORTED_ENCODINGS)
        # We need to repeat the code from `AbstractHTTPHandler.do_request_`
        # since we need to modify the request object.
        # See: https://github.com/python/cpython/blob/main/Lib/urllib/request.py#L1367
        host = req.host
        if not host:
            raise urllib2.URLError(u'no host given')

        # `Request.get_method()` is not used since it is not available in Python 2
        if req.get_method() not in (u'GET', u'HEAD'):
            if u'Content-Length' not in req.headers and u'Transfer-Encoding' not in req.headers:
                req.headers[u'Content-Length'] = unicode(len(req.data or ''))
        if u'Host' not in req.headers:
            req.headers[u'Host'] = host

        # Escape the path component of the URL to satisfy RFC 3986
        # See: https://github.com/python/cpython/issues/91306
        url_escaped = normalize_url(req.get_full_url())
        if req.get_full_url() != url_escaped:
            req = update_Request(req, url=url_escaped)

        return super(HTTPHandler, self).do_request_(req)

    def http_response(self, req, resp):
        old_resp = resp
        # gzip, deflate and brotli decoding
        # See: https://github.com/python/cpython/blob/main/Lib/urllib/request.py#L652
        # To decompress, we simply do the reverse.
        # [1]: https://datatracker.ietf.org/doc/html/rfc9110#name-content-encoding
        decoded_response = None
        for encoding in (e.strip() for e in reversed(resp.headers.get(u'Content-encoding', u'').split(u','))):
            if encoding == u'gzip':
                decoded_response = self.gz(decoded_response or resp.read())
            elif encoding == u'deflate':
                decoded_response = self.deflate(decoded_response or resp.read())
            elif encoding == u'br' and brotli:
                decoded_response = self.brotli(decoded_response or resp.read())

        if decoded_response is not None:
            resp = urllib.addinfourl(io.BytesIO(decoded_response), old_resp.headers, old_resp.url, old_resp.code)
            resp.msg = old_resp.msg
        # Percent-encode redirect URL of Location HTTP header to satisfy RFC 3986 (see
        # https://github.com/ytdl-org/youtube-dl/issues/6457).
        if 300 <= resp.code < 400:
            location = resp.headers.get(u'Location')
            if location:
                # As of RFC 2616 default charset is iso-8859-1 that is respected by Python 3
                location = location.encode(u'iso-8859-1').decode()
                location_escaped = normalize_url(location)
                if location != location_escaped:
                    del resp.headers[u'Location']
                    resp.headers[u'Location'] = location_escaped
        return resp

    https_request = http_request
    https_response = http_response
    gz = lambda self, data: zlib.decompress(data, zlib.MAX_WBITS | 16)
    deflate = zlib.decompress
    brotli = brotli.decompress if brotli else None


def make_socks_conn_class(base_class, socks_proxy):
    assert issubclass(base_class, (
        httplib.HTTPConnection, httplib.HTTPSConnection))

    proxy_args = make_socks_proxy_opts(socks_proxy)

    class SocksConnection(base_class):

        def connect(self):
            self.sock = create_connection(
                (proxy_args[u'addr'], proxy_args[u'port']),
                timeout=self.timeout,
                source_address=self.source_address,
                _create_socket_func=functools.partial(
                    create_socks_proxy_socket, (self.host, self.port), proxy_args))
            if isinstance(self, httplib.HTTPSConnection):
                self.sock = self._context.wrap_socket(self.sock, server_hostname=self.host)

    return SocksConnection


class RedirectHandler(UrllibRedirectHandler):
    u"""YoutubeDL redirect handler

    The code is based on HTTPRedirectHandler implementation from CPython [1].

    [1] https://github.com/python/cpython/blob/main/Lib/urllib/request.py
    [2] https://github.com/ytdl-org/youtube-dl/issues/630
    3. https://github.com/python/cpython/issues/91306
    """

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = UrllibRedirectHandler.http_error_302

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code not in (301, 302, 303, 307, 308):
            raise urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)

        new_data = req.data

        # Technically the Cookie header should be in unredirected_hdrs,
        # however in practice some may set it in normal headers anyway.
        # We will remove it here to prevent any leaks.
        remove_headers = [u'Cookie']

        new_method = get_redirect_method(req.get_method(), code)
        # only remove payload if method changed (e.g. POST to GET)
        if new_method != req.get_method():
            new_data = None
            remove_headers.extend([u'Content-Length', u'Content-Type'])

        new_headers = dict((k, v) for k, v in req.headers.items() if k.title() not in remove_headers)

        return UrllibRequest(
            newurl, headers=new_headers, origin_req_host=req.origin_req_host,
            unverifiable=True, method=new_method, data=new_data)


class ProxyHandler(urllib2.BaseHandler):
    handler_order = 100

    def __init__(self, proxies=None):
        self.proxies = proxies
        # Set default handlers
        for scheme in (u'http', u'https', u'ftp'):
            setattr(self, u'%s_open' % scheme, lambda r, meth=self.proxy_open: meth(r))

    def proxy_open(self, req):
        proxy = select_proxy(req.get_full_url(), self.proxies)
        if proxy is None:
            return
        if urlparse.urlparse(proxy).scheme.lower() in (u'socks4', u'socks4a', u'socks5', u'socks5h'):
            req.add_header(u'Ytdl-socks-proxy', proxy)
            # yt-dlp's http/https handlers do wrapping the socket with socks
            return None
        return UrllibProxyHandler.proxy_open(
            self, req, proxy, None)


class PUTRequest(UrllibRequest):
    def get_method(self):
        return u'PUT'


class HEADRequest(UrllibRequest):
    def get_method(self):
        return u'HEAD'


def update_Request(req, url=None, data=None, headers=None, query=None):
    # This is a compatibility function for urllib.request.Request
    req_headers = req.headers.copy()
    req_headers.update(headers or {})
    req_data = data if data is not None else req.data
    req_url = update_url_query(url or req.get_full_url(), query)
    req_get_method = req.get_method()
    if req_get_method == u'HEAD':
        req_type = HEADRequest
    elif req_get_method == u'PUT':
        req_type = PUTRequest
    else:
        req_type = UrllibRequest
    new_req = req_type(
        req_url, data=req_data, headers=req_headers,
        origin_req_host=req.origin_req_host, unverifiable=req.unverifiable)
    if hasattr(req, u'timeout'):
        new_req.timeout = req.timeout
    return new_req


class UrllibResponseAdapter(Response):
    u"""
    HTTP Response adapter class for urllib addinfourl and http.client.HTTPResponse
    """

    def __init__(self, res):
        # addinfourl: In Python 3.9+, .status was introduced and .getcode() was deprecated [1]'
        # HTTPResponse: .getcode() was deprecated, .status always existed [2]'
        # 1. https://docs.python.org/3/library/urllib.request.html#urllib.response.addinfourl.getcode
        # 2. https://docs.python.org/3.10/library/http.client.html#http.client.HTTPResponse.status
        super(UrllibResponseAdapter, self).__init__(
            fp=res, headers=res.headers, url=res.url,
            status=getattr(res, u'status', None) or res.getcode(), reason=getattr(res, u'reason', None))

    def read(self, amt=None):
        try:
            return self.fp.read(amt)
        except Exception, e:
            handle_response_read_exceptions(e)
            raise e


def handle_sslerror(e):
    if not isinstance(e, ssl.SSLError):
        return
    if isinstance(e, ssl.SSLCertVerificationError):
        raise CertificateVerifyError(cause=e)
    raise SSLError(cause=e)


def handle_response_read_exceptions(e):
    if isinstance(e, httplib.IncompleteRead):
        raise IncompleteRead(partial=len(e.partial), cause=e, expected=e.expected)
    elif isinstance(e, ssl.SSLError):
        handle_sslerror(e)
    elif isinstance(e, (OSError, EOFError, httplib.HTTPException) + tuple(CONTENT_DECODE_ERRORS)):
        # OSErrors raised here should mostly be network related
        raise TransportError(cause=e)


class UrllibRH(RequestHandler, InstanceStoreMixin):
    _SUPPORTED_URL_SCHEMES = (u'http', u'https', u'data', u'ftp')
    _SUPPORTED_PROXY_SCHEMES = (u'http', u'socks4', u'socks4a', u'socks5', u'socks5h')
    _SUPPORTED_FEATURES = (Features.NO_PROXY, Features.ALL_PROXY)
    RH_NAME = u'urllib'

    def __init__(self, **kwargs):
        if u'enable_file_urls' in kwargs:
            enable_file_urls = kwargs[u'enable_file_urls']
            del kwargs[u'enable_file_urls']
        else:
            enable_file_urls = False
        super(UrllibRH, self).__init__(**kwargs)
        self.enable_file_urls = enable_file_urls
        if self.enable_file_urls:
            self._SUPPORTED_URL_SCHEMES = self._SUPPORTED_URL_SCHEMES + (u'file',)

    def _check_extensions(self, extensions):
        super(UrllibRH, self)._check_extensions(extensions)
        extensions.pop(u'cookiejar', None)
        extensions.pop(u'timeout', None)
        extensions.pop(u'legacy_ssl', None)

    def _create_instance(self, proxies, cookiejar, legacy_ssl_support=None):
        from ..compat import compat_urllib_request
        opener = OpenerDirector()
        handlers = [
            ProxyHandler(proxies),
            HTTPHandler(
                context=create_ssl_context(legacy_support=legacy_ssl_support),
                source_address=self.source_address),
            compat_urllib_request.HTTPCookieProcessor(cookiejar),
            RedirectHandler(),
            UnknownHandler(),
        ]
        if self.enable_file_urls:
            handlers.insert(0, compat_urllib_request.FileHandler())
        for handler in handlers:
            opener.add_handler(handler)
        return opener

    def _send(self, request):
        headers = self._get_headers(request)
        urllib_req = UrllibRequest(
            url=request.url,
            data=request.data,
            headers=headers,
            origin_req_host=request.origin_req_host,
            unverifiable=request.unverifiable,
        )
        opener = self._get_instance(
            proxies=self._get_proxies(request),
            cookiejar=self._get_cookiejar(request),
            legacy_ssl_support=request.extensions.get(u'legacy_ssl'),
        )
        try:
            res = opener.open(urllib_req, timeout=self._calculate_timeout(request))
        except urllib2.HTTPError, e:
            if isinstance(e.fp, (httplib.HTTPResponse, urllib.addinfourl)):
                # Prevent file object from being closed when urllib.error.HTTPError is destroyed.
                e._closer.close_called = True
                raise HTTPError(UrllibResponseAdapter(e.fp), redirect_loop=u'redirect error' in unicode(e))
            raise  # unexpected
        except urllib2.URLError, e:
            cause = e.reason  # NOTE: cause may be a string

            # proxy errors
            if u'tunnel connection failed' in unicode(cause).lower() or (SocksProxyError and isinstance(cause, SocksProxyError)):
                raise ProxyError(cause=e)

            handle_response_read_exceptions(cause)
            raise TransportError(cause=e)
        except (httplib.InvalidURL, ValueError), e:
            # Validation errors
            # http.client.HTTPConnection raises ValueError in some validation cases
            # such as if request method contains illegal control characters [1]
            # 1. https://github.com/python/cpython/blob/987b712b4aeeece336eed24fcc87a950a756c3e2/Lib/http/client.py#L1256
            raise RequestError(cause=e)
        except Exception, e:
            handle_response_read_exceptions(e)
            raise  # unexpected

        return UrllibResponseAdapter(res)

UrllibRH = register_rh(UrllibRH)
