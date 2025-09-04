from __future__ import absolute_import

import functools
import httplib
import logging
import re
import socket
import warnings

from ..dependencies import brotli, requests, urllib3
from ..utils import int_or_none, variadic, bug_reports_message
from ..utils.networking import normalize_url, select_proxy

if requests is None:
    raise ImportError(u'requests module is not installed')

if urllib3 is None:
    raise ImportError(u'urllib3 module is not installed')

urllib3_version = tuple(int_or_none(x, default=0) for x in urllib3.__version__.split(u'.'))

if urllib3_version < (2, 0, 2):
    urllib3._yt_dlp__version = u'%s (unsupported)' % urllib3.__version__
    raise ImportError(u'Only urllib3 >= 2.0.2 is supported')

if requests.__build__ < 0x023202:
    requests._yt_dlp__version = u'%s (unsupported)' % requests.__version__
    raise ImportError(u'Only requests >= 2.32.2 is supported')

import requests.adapters
import requests.utils
from requests.cookies import RequestsCookieJar
from urllib3.connection import HTTPConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from urllib3.poolmanager import PoolManager

from .common import (
    Features,
    Request,
    RequestHandler,
    Response,
    register_preference,
    register_rh,
)
from .exceptions import (
    CertificateVerifyError,
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
    make_socks_proxy_opts,
    _socket_connect as create_connection,
    _socks_connect as create_socks_proxy_socket,
)

# PySocks is not a dependency of requests, so we need to vendor it
# if it is not installed
try:
    from ..dependencies.socks import (
        SocksProxyError,
        sockssocket,
        ProxyType,
    )
except ImportError:
    SocksProxyError = None
    sockssocket = None
    ProxyType = None


SUPPORTED_ENCODINGS = [
    u'gzip', u'deflate',
]

if brotli is not None:
    SUPPORTED_ENCODINGS.append(u'br')

u'''
Override urllib3's behavior to not convert lower-case percent-encoded characters
to upper-case during url normalization process.

This is to avoid issues with sites that are picky about url casing.
See: https://github.com/yt-dlp/yt-dlp/issues/3715
     https://github.com/yt-dlp/yt-dlp/issues/8820
     https://github.com/urllib3/urllib3/issues/922
     https://github.com/urllib3/urllib3/pull/2153
'''


class Urllib3PercentREOverride(object):
    def __init__(self, r):
        self.re = r

    # pass through all other attribute calls to the original re
    def __getattr__(self, name):
        return getattr(self.re, name)

    # urllib3 calls `re.sub` to normalize the url, so we must override it
    def sub(self, repl, string, count=0):
        return string


# See: https://github.com/urllib3/urllib3/blob/2.2.1/src/urllib3/util/url.py#L20
# https://github.com/urllib3/urllib3/commit/a2697e7c6b275f05879b60f593c5854a816489f0
import urllib3.util.url

if hasattr(urllib3.util.url, u'_PERCENT_RE'):  # was 'PERCENT_RE' in urllib3 < 2.0.0
    urllib3.util.url._PERCENT_RE = Urllib3PercentREOverride(urllib3.util.url._PERCENT_RE)
else:
    warnings.warn(u'Failed to patch _PERCENT_RE in urllib3 (does the attribute exist?)' + bug_reports_message())


# Requests will not automatically handle no_proxy by default
# See: https://github.com/psf/requests/issues/5344
#      https://github.com/psf/requests/issues/2573
requests.utils.should_bypass_proxies = lambda url, no_proxy: no_proxy and any(
    requests.utils.proxy_bypass_registry.get(host)(url) for host in no_proxy)


class RequestsResponseAdapter(Response):
    def __init__(self, res):
        super(RequestsResponseAdapter, self).__init__(
            fp=res.raw, headers=res.headers, url=res.url,
            status=res.status_code, reason=res.reason)

        self._requests_response = res

    def read(self, amt=None):
        try:
            # Work around issue with `.read(amt)` then `.read()`
            # See: https://github.com/urllib3/urllib3/issues/3636
            if amt is None:
                # Python 3.9 preallocates the whole read buffer, read in chunks
                read_chunk = functools.partial(self.fp.read, 1 << 20, decode_content=True)
                return u''.join(iter(read_chunk, u''))
            # Interact with urllib3 response directly.
            return self.fp.read(amt, decode_content=True)

        # See urllib3.response.HTTPResponse.read() for exceptions raised on read
        except urllib3.exceptions.SSLError, e:
            raise SSLError(cause=e)

        except urllib3.exceptions.ProtocolError, e:
            # IncompleteRead is always contained within ProtocolError
            # See urllib3.response.HTTPResponse._error_catcher()
            ir_err = None
            for err in e.args:
                if isinstance(err, httplib.IncompleteRead):
                    ir_err = err
                    break
            if ir_err is not None:
                # `urllib3.exceptions.IncompleteRead` is subclass of `http.client.IncompleteRead`
                # but uses an `int` for its `partial` property.
                partial = ir_err.partial if isinstance(ir_err.partial, int) else len(ir_err.partial)
                raise IncompleteRead(partial=partial, expected=ir_err.expected)
            raise TransportError(cause=e)

        except urllib3.exceptions.HTTPError, e:
            # catch-all for any other urllib3 response exceptions
            raise TransportError(cause=e)


class RequestsHTTPAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, ssl_context=None, proxy_ssl_context=None, source_address=None, **kwargs):
        self._pm_args = {}
        if ssl_context:
            self._pm_args[u'ssl_context'] = ssl_context
        if source_address:
            self._pm_args[u'source_address'] = (source_address, 0)
        self._proxy_ssl_context = proxy_ssl_context or ssl_context
        super(RequestsHTTPAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        return super(RequestsHTTPAdapter, self).init_poolmanager(*args, **kwargs, **self._pm_args)

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        extra_kwargs = {}
        if not proxy.lower().startswith(u'socks') and self._proxy_ssl_context:
            extra_kwargs[u'proxy_ssl_context'] = self._proxy_ssl_context
        return super(RequestsHTTPAdapter, self).proxy_manager_for(proxy, **proxy_kwargs, **self._pm_args, **extra_kwargs)

    # Skip `requests` internal verification; we use our own SSLContext
    def cert_verify(self, *args, **kwargs):
        pass

    # Don't resolve hostnames with the proxy; SOCKS proxies should do this
    def get_connection(self, url, proxies=None):
        proxy = requests.utils.select_proxy(url, proxies)
        if proxy and proxy.lower().startswith(u'socks'):
            return self.get_connection_with_proxy_dns(url, proxies)
        return super(RequestsHTTPAdapter, self).get_connection(url, proxies)


class RequestsSession(requests.sessions.Session):
    u"""
    Ensure unified redirect method handling with our urllib redirect handler.
    """

    def rebuild_method(self, prepared_request, response):
        u"""
        Don't change the method of the request on redirects.
        This is to simplify the logic of our redirect handler, which will
        determine the correct method to use for the subsequent request.
        """
        # HACK: store the original status code so we can undo the changes
        # from `rebuild_auth` if applicable
        response._real_status_code = response.status_code
        response.status_code = 200  # a status code that won't trigger any special handling
        return super(RequestsSession, self).rebuild_method(prepared_request, response)

    def rebuild_auth(self, prepared_request, response):
        # HACK: undo status code change from rebuild_method, if applicable.
        # rebuild_auth runs after requests would remove headers/body based on status code
        if hasattr(response, u'_real_status_code'):
            response.status_code = response._real_status_code
            del response._real_status_code
        return super(RequestsSession, self).rebuild_auth(prepared_request, response)


class Urllib3LoggingFilter(logging.Filter):

    def filter(self, record):
        # Ignore HTTP request messages since HTTPConnection prints those
        return record.msg != u'%s://%s:%s "%s %s %s" %s %s'


class Urllib3LoggingHandler(logging.Handler):
    u"""Redirect urllib3 logs to our logger"""

    def __init__(self, logger, *args, **kwargs):
        super(Urllib3LoggingHandler, self).__init__(*args, **kwargs)
        self._logger = logger

    def emit(self, record):
        try:
            msg = self.format(record)
            self._logger.debug(msg)
        except Exception:
            self.handleError(record)


class RequestsRH(RequestHandler, InstanceStoreMixin):

    u"""Requests RequestHandler
    https://github.com/psf/requests
    """
    _SUPPORTED_URL_SCHEMES = (u'http', u'https')
    _SUPPORTED_ENCODINGS = tuple(SUPPORTED_ENCODINGS)
    _SUPPORTED_PROXY_SCHEMES = (u'http', u'https', u'socks4', u'socks4a', u'socks5', u'socks5h')
    _SUPPORTED_FEATURES = (Features.NO_PROXY, Features.ALL_PROXY)
    RH_NAME = u'requests'

    def __init__(self, *args, **kwargs):
        super(RequestsRH, self).__init__(*args, **kwargs)

        # Forward urllib3 debug messages to our logger
        logger = logging.getLogger(u'urllib3')
        self.__logging_handler = Urllib3LoggingHandler(logger=self._logger)
        self.__logging_handler.setFormatter(logging.Formatter(u'requests: %(message)s'))
        self.__logging_handler.addFilter(Urllib3LoggingFilter())
        logger.addHandler(self.__logging_handler)
        # TODO: Use a logger filter to suppress pool reuse warning instead
        # See: https://github.com/urllib3/urllib3/issues/2142
        if logger.level == logging.DEBUG:
            HTTPConnection.debuglevel = 1
            logging.getLogger().setLevel(logging.DEBUG)

    def __del__(self):
        self._clear_instances()
        # Remove the logging handler that contains a reference to our logger
        # See: https://github.com/yt-dlp/yt-dlp/issues/8922
        logging.getLogger(u'urllib3').removeHandler(self.__logging_handler)

    def _check_extensions(self, extensions):
        super(RequestsRH, self)._check_extensions(extensions)
        extensions.pop(u'cookiejar', None)
        extensions.pop(u'timeout', None)
        extensions.pop(u'legacy_ssl', None)
        extensions.pop(u'keep_header_casing', None)

    def _create_instance(self, cookiejar, legacy_ssl_support=None):
        session = RequestsSession()

        http_adapter = RequestsHTTPAdapter(
            ssl_context=create_ssl_context(legacy_support=legacy_ssl_support),
            proxy_ssl_context=create_ssl_context(legacy_support=legacy_ssl_support),
            source_address=self.source_address,
        )
        session.adapters.clear()
        session.headers = requests.models.CaseInsensitiveDict()
        session.mount(u'https://', http_adapter)
        session.mount(u'http://', http_adapter)
        session.cookies = cookiejar
        session.trust_env = False  # no need, we already load proxies from env
        return session

    def _prepare_headers(self, _, headers):
        add_accept_encoding_header(headers, SUPPORTED_ENCODINGS)
        headers.setdefault(u'Connection', u'keep-alive')

    def _send(self, request):

        self._prepare_headers(request, request.headers)
        max_redirects_exceeded = False

        session = self._get_instance(
            cookiejar=self._get_cookiejar(request),
            legacy_ssl_support=request.extensions.get(u'legacy_ssl'),
        )

        try:
            requests_res = session.request(
                request.method,
                normalize_url(request.url),
                headers=request.headers,
                data=request.data,
                proxies=self._get_proxies(request),
                timeout=self._get_timeout(request.extensions),
                allow_redirects=False,
                verify=False,
                stream=True,
            )

        except requests.exceptions.TooManyRedirects, e:
            max_redirects_exceeded = True
            requests_res = e.response

        except requests.exceptions.SSLError, e:
            if u'CERTIFICATE_VERIFY_FAILED' in unicode(e):
                raise CertificateVerifyError(cause=e)
            raise SSLError(cause=e)

        except requests.exceptions.ProxyError, e:
            raise ProxyError(cause=e)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout), e:
            raise TransportError(cause=e)

        except urllib3.exceptions.HTTPError, e:
            # Catch any urllib3 exceptions that may leak through
            raise TransportError(cause=e)

        except requests.exceptions.RequestException, e:
            # Miscellaneous Requests exceptions. May not necessary be network related e.g. InvalidURL
            raise RequestError(cause=e)

        res = RequestsResponseAdapter(requests_res)

        if max_redirects_exceeded:
            raise HTTPError(res, redirect_loop=True)

        return res

RequestsRH = register_rh(RequestsRH)

@register_preference(RequestsRH)
def requests_preference(rh, request):
    if not SocksProxyError:
        return -1
    proxies = rh._get_proxies(request)
    if u'socks' in select_proxy(request.url, proxies):
        return 2
    return 0


class SocksHTTPConnection(urllib3.connection.HTTPConnection):
    def __init__(self, _socks_options, *args, **kwargs):  # must use _socks_options to pass PoolKey checks
        self._proxy_args = _socks_options
        super(SocksHTTPConnection, self).__init__(*args, **kwargs)

    def _new_conn(self):
        try:
            return create_connection(
                address=(self._proxy_args[u'addr'], self._proxy_args[u'port']),
                timeout=self.timeout,
                source_address=self.source_address,
                _create_socket_func=functools.partial(
                    create_socks_proxy_socket, (self.host, self.port), self._proxy_args))
        except (socket.timeout, TimeoutError), e:
            raise urllib3.exceptions.ConnectTimeoutError(
                self, u'Connection to %s timed out. (connect timeout=%s)' % (self.host, self.timeout))
        except SocksProxyError, e:
            raise urllib3.exceptions.ProxyError(unicode(e), e)
        except OSError, e:
            raise urllib3.exceptions.NewConnectionError(
                self, u'Failed to establish a new connection: %s' % e)


class SocksHTTPSConnection(SocksHTTPConnection, urllib3.connection.HTTPSConnection):
    pass


class SocksHTTPConnectionPool(HTTPConnectionPool):
    ConnectionCls = SocksHTTPConnection


class SocksHTTPSConnectionPool(HTTPSConnectionPool):
    ConnectionCls = SocksHTTPSConnection


class SocksProxyManager(urllib3.PoolManager):

    def __init__(self, socks_proxy, username=None, password=None, num_pools=10, headers=None, **connection_pool_kw):
        connection_pool_kw[u'_socks_options'] = make_socks_proxy_opts(socks_proxy)
        super(SocksProxyManager, self).__init__(num_pools, headers, **connection_pool_kw)
        self.pool_classes_by_scheme = {
            u'http': SocksHTTPConnectionPool,
            u'https': SocksHTTPSConnectionPool,
        }


requests.adapters.register_transport(u'socks', SocksProxyManager)
