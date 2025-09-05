from __future__ import absolute_import

import abc
import functools
import io
from ..dependencies import typing
import urlparse
import urllib2
from collections import Iterable, Mapping
from email.message import Message

from ..utils import (
    bug_reports_message,
    deprecation_warning,
    error_to_str,
    HTTPHeaderDict,
    network_exceptions,
    update_url_query,
)
from ..utils._decorators import classproperty
from .exceptions import RequestError, UnsupportedRequest

# typing
if typing.TYPE_CHECKING:
    from typing import Type

DEFAULT_TIMEOUT = 20


def register_preference(*handlers):
    assert all(issubclass(handler, RequestHandler) for handler in handlers)

    def outer(preference):
        @functools.wraps(preference)
        def inner(handler, *args, **kwargs):
            if not handlers or isinstance(handler, handlers):
                return preference(handler, *args, **kwargs)
            return 0
        _RH_PREFERENCES.add(inner)
        return inner
    return outer


class RequestDirector(object):
    u"""RequestDirector class

    Helper class that, when given a request, forward it to a RequestHandler that supports it.

    This class is not meant to be used directly by the user.
    Instead, it is used by the YoutubeDL class to handle all network requests.

    The RequestDirector is responsible for:
    - Managing RequestHandlers
    - Selecting the best handler for a given request
    - Forwarding the request to the selected handler
    - Handling errors and retries
    """

    def __init__(self, logger, verbose=False):
        self.handlers = {}
        self.preferences = set()
        self.logger = logger  # TODO(Grub4k): default logger
        self.verbose = verbose

    def __del__(self):
        for handler in self.handlers.values():
            handler.close()
        self.handlers.clear()

    def add_handler(self, handler):
        u"""Add a handler. If a handler of the same RH_KEY exists, it will overwrite it"""
        assert isinstance(handler, RequestHandler), u'handler must be a RequestHandler'
        self.handlers[handler.RH_KEY] = handler

    def _get_handlers(self, request):
        u"""Sorts handlers by preference, given a request"""
        preferences = dict(
            (rh, sum(pref(rh, request) for pref in self.preferences))
            for rh in self.handlers.values()
        )
        self._print_verbose(u'Handler preferences for this request: %s' % (u', '.join(
            u'%s=%s' % (rh.RH_NAME, pref) for rh, pref in preferences.items())))
        return sorted(self.handlers.values(), key=preferences.get, reverse=True)

    def _print_verbose(self, msg):
        if self.verbose:
            self.logger.stdout('director: %s' % msg)

    def send(self, request):
        u"""
        Passes a request onto a suitable RequestHandler
        """
        if not self.handlers:
            raise RequestError(u'No request handlers configured')

        assert isinstance(request, Request)

        unsupported_errors = []
        for handler in self._get_handlers(request):
            self._print_verbose('Checking if "%s" supports this request.' % handler.RH_NAME)
            try:
                handler.validate(request)
            except UnsupportedRequest, e:
                self._print_verbose(
                    '"%s" cannot handle this request (reason: %s)' % (handler.RH_NAME, error_to_str(e)))
                unsupported_errors.append(e)
                continue

            self._print_verbose('"%s" is the best handler for this request' % handler.RH_NAME)
            try:
                response = handler.send(request)
            except RequestError:
                raise
            except Exception, e:
                self.logger.error(
                    '[%s] Unexpected error: %s%s' % (handler.RH_NAME, error_to_str(e), bug_reports_message()),
                    is_error=False)
                # We do not want to retry on unexpected errors
                raise RequestError(e, handler=handler)

            return response

        raise UnsupportedRequest(
            'No handler is able to handle this request. The following reasons were given:\n%s'
            % '\n'.join('  {0}'.format(error_to_str(e)) for e in unsupported_errors),
            errors=unsupported_errors)


_REQUEST_HANDLERS = {}


def register_rh(handler):
    u"""Register a RequestHandler class"""
    assert issubclass(handler, RequestHandler), '%s must be a subclass of RequestHandler' % handler
    assert handler.RH_KEY not in _REQUEST_HANDLERS, 'RequestHandler %s already registered' % handler.RH_KEY
    _REQUEST_HANDLERS[handler.RH_KEY] = handler
    return handler


def get_rh(key):
    return _REQUEST_HANDLERS[key]


class RequestHandler(object):
    __metaclass__ = abc.ABCMeta

    u"""Request Handler class

    Request handlers are class that, given a Request,
    process the request from start to finish and return a Response.

    Request handlers are responsible for:
    - Handling proxies
    - Handling cookies
    - Handling authentication
    - Handling redirects
    - Handling retries
    - Handling timeouts
    - etc.

    A RequestHandler can be configured with the following options:
    - `headers`: A dictionary of headers to be sent with every request.
    - `cookiejar`: A `YoutubeDLCookieJar` instance to use for cookies.
    - `timeout`: The timeout for every request.
    - `proxies`: A dictionary of proxies to use for every request.
    - `source_address`: The source address to use for every request.
    - `verbose`: Whether to print verbose output.
    - `prefer_system_certs`: Whether to prefer system certificates over certifi.
    - `client_cert`: A dictionary containing the client certificate and key.
    - `verify`: Whether to verify the server's TLS certificate.
    - `legacy_ssl_support`: Whether to enable legacy SSL support.

    To create a new RequestHandler, you must subclass this class and implement
    the `_send` method. You must also set the `RH_NAME` and `RH_KEY` class
    attributes. The `RH_KEY` must be unique across all RequestHandlers.

    The `_send` method is responsible for handling the request and returning a
    `Response` object. It should not be called directly by the user.

    The `validate` method is used to check if the handler can handle a given

    request. It should not be called directly by the user.

    The `close` method is used to clean up any resources used by the handler.
    It should be called when the handler is no longer needed.
    """

    # The name of the request handler
    RH_NAME = None
    # A tuple of supported URL schemes (e.g. ('http', 'https'))
    # If None, all URL schemes are supported
    _SUPPORTED_URL_SCHEMES = ()
    # A tuple of supported proxy schemes (e.g. ('http', 'https'))
    # If None, all proxy schemes are supported
    _SUPPORTED_PROXY_SCHEMES = None
    # A tuple of supported features
    _SUPPORTED_FEATURES = ()

    def __init__(
        self,
        **_
    ):
        if 'legacy_ssl_support' in _: legacy_ssl_support = _['legacy_ssl_support']; del _['legacy_ssl_support']
        else: legacy_ssl_support = False
        if 'verify' in _: verify = _['verify']; del _['verify']
        else: verify = True
        if 'client_cert' in _: client_cert = _['client_cert']; del _['client_cert']
        else: client_cert = None
        if 'prefer_system_certs' in _: prefer_system_certs = _['prefer_system_certs']; del _['prefer_system_certs']
        else: prefer_system_certs = False
        if 'verbose' in _: verbose = _['verbose']; del _['verbose']
        else: verbose = False
        if 'source_address' in _: source_address = _['source_address']; del _['source_address']
        else: source_address = None
        if 'proxies' in _: proxies = _['proxies']; del _['proxies']
        else: proxies = None
        if 'timeout' in _: timeout = _['timeout']; del _['timeout']
        else: timeout = None
        if 'cookiejar' in _: cookiejar = _['cookiejar']; del _['cookiejar']
        else: cookiejar = None
        if 'headers' in _: headers = _['headers']; del _['headers']
        else: headers = None
        logger = _['logger']; del _['logger']

        from ..cookies import YoutubeDLCookieJar
        self._logger = logger
        self.headers = headers or {}
        self.cookiejar = cookiejar if cookiejar is not None else YoutubeDLCookieJar()
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.proxies = proxies or {}
        self.source_address = source_address
        self.verbose = verbose
        self.prefer_system_certs = prefer_system_certs
        self._client_cert = client_cert or {}
        self.verify = verify
        self.legacy_ssl_support = legacy_ssl_support
        super(RequestHandler, self).__init__()

    def _make_sslcontext(self, legacy_ssl_support=None):
        return make_ssl_context(
            verify=self.verify,
            use_certifi=not self.prefer_system_certs,
            legacy_support=self.legacy_ssl_support if legacy_ssl_support is None else legacy_ssl_support,
            client_certificate=self._client_cert)

    def _merge_headers(self, request_headers):
        return HTTPHeaderDict(self.headers, request_headers)

    def _prepare_headers(self, request, headers):  # noqa: B027
        u"""Additional operations to prepare headers before building. To be extended by subclasses.
        @param request: Request object
        @param headers: Merged headers to prepare
        """

    def _get_headers(self, request):
        u"""
        Get headers for external use.
        Subclasses may define a _prepare_headers method to modify headers after merge but before building.
        """
        headers = self._merge_headers(request.headers)
        self._prepare_headers(request, headers)
        if request.extensions.get(u'keep_header_casing'):
            return headers.sensitive()
        return dict(headers)

    def _calculate_timeout(self, request):
        return float(request.extensions.get(u'timeout') or self.timeout)

    def _get_cookiejar(self, request):
        cookiejar = request.extensions.get(u'cookiejar')
        return self.cookiejar if cookiejar is None else cookiejar

    def _get_proxies(self, request):
        return (request.proxies or self.proxies).copy()

    def _check_url_scheme(self, request):
        scheme = urlparse.urlparse(request.url).scheme.lower()
        if self._SUPPORTED_URL_SCHEMES is not None and scheme not in self._SUPPORTED_URL_SCHEMES:
            raise UnsupportedRequest('Unsupported url scheme: "%s"' % scheme)
        return scheme  # for further processing

    def _check_proxies(self, proxies):
        for proxy_key, proxy_url in proxies.items():
            if proxy_url is None:
                continue
            if proxy_key == u'no':
                if self._SUPPORTED_FEATURES is not None and Features.NO_PROXY not in self._SUPPORTED_FEATURES:
                    raise UnsupportedRequest(u'"no" proxy is not supported')
                continue
            if (
                proxy_key == u'all'
                and self._SUPPORTED_FEATURES is not None
                and Features.ALL_PROXY not in self._SUPPORTED_FEATURES
            ):
                raise UnsupportedRequest(u'"all" proxy is not supported')

            # Unlikely this handler will use this proxy, so ignore.
            # This is to allow a case where a proxy may be set for a protocol
            # for one handler in which such protocol (and proxy) is not supported by another handler.
            if self._SUPPORTED_URL_SCHEMES is not None and proxy_key not in self._SUPPORTED_URL_SCHEMES + (u'all',):
                continue

            if self._SUPPORTED_PROXY_SCHEMES is None:
                raise UnsupportedRequest('Proxies are not supported by this handler')

            try:
                if urllib2._parse_proxy(proxy_url)[0] is None:
                    # Scheme-less proxies are not supported
                    raise UnsupportedRequest('Proxy "%s" missing scheme' % proxy_url)
            except ValueError, e:
                # parse_proxy may raise on some invalid proxy urls such as "/a/b/c"
                raise UnsupportedRequest('Invalid proxy url "%s": %s' % (proxy_url, e))

            scheme = urlparse.urlparse(proxy_url).scheme.lower()
            if scheme not in self._SUPPORTED_PROXY_SCHEMES:
                raise UnsupportedRequest('Unsupported proxy type: "%s"' % scheme)

    def _check_extensions(self, extensions):
        u"""Check extensions for unsupported extensions. Subclasses should extend this."""
        from ..cookies import YoutubeDLCookieJar
        assert isinstance(extensions.get(u'cookiejar'), (YoutubeDLCookieJar, type(None)))
        assert isinstance(extensions.get(u'timeout'), (float, int, type(None)))
        assert isinstance(extensions.get(u'legacy_ssl'), (bool, type(None)))
        assert isinstance(extensions.get(u'keep_header_casing'), (bool, type(None)))

    def _validate(self, request):
        self._check_url_scheme(request)
        self._check_proxies(request.proxies)
        extensions = request.extensions.copy()
        self._check_extensions(extensions)
        if extensions:
            raise UnsupportedRequest('Unsupported extensions: %s' % ", ".join(extensions.keys()))

    @wrap_request_errors
    def validate(self, request):
        if not isinstance(request, Request):
            raise TypeError(u'Expected an instance of Request')
        self._validate(request)

    @wrap_request_errors
    def send(self, request):
        if not isinstance(request, Request):
            raise TypeError(u'Expected an instance of Request')
        return self._send(request)

    @abc.abstractmethod
    def _send(self, request):
        u"""Handle a request from start to finish. Redefine in subclasses."""
        pass

    def close(self):  # noqa: B027
        pass

    @classproperty
    def RH_KEY(cls):
        assert cls.__name__.endswith(u'RH'), u'RequestHandler class names must end with "RH"'
        return cls.__name__[:-2]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class Request(object):
    u"""
    Represents a request to be made.
    Partially backwards-compatible with urllib.request.Request.

    This class is not meant to be used directly by the user.
    Instead, it is used by the YoutubeDL class to handle all network requests.
    """

    def __init__(
            self,
            url,
            data=None,
            headers=None,
            proxies=None,
            query=None,
            method=None,
            extensions=None,
    ):

        self._headers = HTTPHeaderDict()
        self.url = url
        self.method = method
        # Must be set after method since it can affect the method
        self.data = data
        self.headers = headers or {}
        self.proxies = proxies or {}
        self.extensions = extensions or {}

        # urllib.request.Request compatibility
        self.origin_req_host = None
        self.unverifiable = False

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        if not isinstance(url, (str, unicode)):
            raise TypeError(u'url must be a string')
        elif url.startswith(u'//'):
            url = u'http:' + url
        self._url = normalize_url(url)

    @property
    def method(self):
        return self._method or (u'POST' if self.data is not None else u'GET')

    @method.setter
    def method(self, method):
        if method is None:
            self._method = None
        elif isinstance(method, (str, unicode)):
            self._method = method.upper()
        else:
            raise TypeError(u'method must be a string')

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        # Try catch some common mistakes
        if data is not None and (
            not isinstance(data, (bytes, io.IOBase, Iterable)) or isinstance(data, (unicode, Mapping))
        ):
            raise TypeError(u'data must be bytes, iterable of bytes, or a file-like object')

        if data == self._data and self._data is None:
            self.headers.pop(u'Content-Length', None)

        # https://docs.python.org/3/library/urllib.request.html#urllib.request.Request.data
        if data != self._data:
            if self._data is not None:
                self.headers.pop(u'Content-Length', None)
            self._data = data

        if self._data is None:
            self.headers.pop(u'Content-Type', None)

        if u'Content-Type' not in self.headers and self._data is not None:
            self.headers[u'Content-Type'] = u'application/x-www-form-urlencoded'

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, new_headers):
        u"""Replaces headers of the request. If not a HTTPHeaderDict, it will be converted to one."""
        if isinstance(new_headers, HTTPHeaderDict):
            self._headers = new_headers
        elif isinstance(new_headers, Mapping):
            self._headers = HTTPHeaderDict(new_headers)
        else:
            raise TypeError(u'headers must be a mapping')

    def update(self, url=None, data=None, headers=None, query=None, extensions=None):
        self.data = data if data is not None else self.data
        self.url = update_url_query(url or self.url, query)
        self.headers.update(headers or {})
        self.extensions.update(extensions or {})

    def __repr__(self):
        return '<Request for %s at %s>' % (
            self.url,
            hex(id(self))
        )


HEADRequest = functools.partial(Request, method=u'HEAD')
PATCHRequest = functools.partial(Request, method=u'PATCH')
PUTRequest = functools.partial(Request, method=u'PUT')


class Response(io.IOBase):
    u"""
    Base class for HTTP response adapters.

    By default, it provides a basic wrapper for a file-like response object.
    It is also partially backwards-compatible with `urllib.response.addinfourl`.

    The Response object is responsible for:
    - Exposing the response body as a file-like object
    - Exposing the response headers
    - Exposing the response status code and reason
    - Exposing the response URL
    """

    def __init__(
            self,
            fp,
            url,
            headers,
            status=200,
            reason=None,
            extensions=None,
    ):

        self.fp = fp
        self.url = url
        self.headers = HTTPHeaderDict(headers)
        self.status = status
        self.reason = reason
        self.extensions = extensions or {}

    def __repr__(self):
        return '<Response for %s at %s>' % (
            self.url,
            hex(id(self))
        )

    def readable(self):
        return self.fp.readable()

    def read(self, amt=None):
        # Expected errors raised here should be of type RequestError or subclasses.
        # Subclasses should redefine this method with more precise error handling.
        try:
            return self.fp.read(amt)
        except Exception, e:
            raise TransportError(cause=e)

    def close(self):
        self.fp.close()
        return super(Response, self).close()

    def get_header(self, name, default=None):
        u"""Get header for name.
        If there are multiple matching headers, return all seperated by comma."""
        headers = self.headers.get_all(name)
        if not headers:
            return default
        if name.title() == u'Set-Cookie':
            # Special case, only get the first one
            # https://www.rfc-editor.org/rfc/rfc9110.html#section-5.3-4.1
            return headers[0]
        return u', '.join(headers)

    # The following methods are for compatability reasons and are deprecated
    @property
    def code(self):
        deprecation_warning(u'Response.code is deprecated, use Response.status', stacklevel=2)
        return self.status

    def getcode(self):
        deprecation_warning(u'Response.getcode() is deprecated, use Response.status', stacklevel=2)
        return self.status

    def geturl(self):
        deprecation_warning(u'Response.geturl() is deprecated, use Response.url', stacklevel=2)
        return self.url

    def info(self):
        deprecation_warning(u'Response.info() is deprecated, use Response.headers', stacklevel=2)
        return self.headers

    def getheader(self, name, default=None):
        deprecation_warning(u'Response.getheader() is deprecated, use Response.get_header', stacklevel=2)
        return self.get_header(name, default)


if typing.TYPE_CHECKING:
    RequestData = bytes | Iterable[bytes] | typing.IO | None
    Preference = typing.Callable[[RequestHandler, Request], int]

_RH_PREFERENCES = set()
from ..cookies import YoutubeDLCookieJar
NoneType = type(None)
if typing.TYPE_CHECKING:
    RequestData = str | Iterable[str] | typing.IO | None
    Preference = typing.Callable[[RequestHandler, Request], int]
else:
    RequestData = (bytes, str, Iterable, io.IOBase, type(None))
    Preference = typing.Callable
_RH_PREFERENCES = set()
