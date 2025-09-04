from __future__ import with_statement
from __future__ import absolute_import

import contextlib
import os
import socket
import ssl
import sys
import urlparse
import urllib

from .exceptions import RequestError
from ..dependencies import certifi
from ..utils import network_exceptions
from ..compat import compat_os_name

if compat_os_name == u'nt':
    from ..dependencies import socks
    if socks:
        from socks import (
            sockssocket,
            ProxyType,
        )
else:
    socks = None

if sys.version_info >= (3, 0):
    from ..utils import HTTPHeaderDict
else:
    from ..utils.networking import HTTPHeaderDict


def ssl_load_certs(context, use_certifi=True):
    if certifi and use_certifi:
        context.load_verify_locations(cafile=certifi.where())
    else:
        try:
            context.load_default_certs()
        except (IOError, OSError):
            # See: https://github.com/yt-dlp/yt-dlp/issues/4893,
            # https://bugs.python.org/issue35665, https://bugs.python.org/issue45312
            if sys.platform == u'win32' and hasattr(ssl, u'enum_certificates'):
                for storename in (u'CA', u'ROOT'):
                    ssl_load_windows_store_certs(context, storename)
            context.set_default_verify_paths()


def ssl_load_windows_store_certs(context, storename):
    # Code adapted from _load_windows_store_certs in https://github.com/python/cpython/blob/main/Lib/ssl.py
    try:
        certs = [cert for cert, encoding, trust in ssl.enum_certificates(storename)
                 if encoding == u'x509_asn' and (
                     trust is True or ssl.Purpose.SERVER_AUTH.oid in trust)]
    except (IOError, OSError):
        return
    for cert in certs:
        context.load_verify_locations(cadata=cert)


def make_socks_proxy_opts(socks_proxy):
    url_components = urlparse.urlparse(socks_proxy)
    if url_components.scheme.lower() == u'socks5':
        socks_type = ProxyType.SOCKS5
        rdns = False
    elif url_components.scheme.lower() == u'socks5h':
        socks_type = ProxyType.SOCKS5
        rdns = True
    elif url_components.scheme.lower() == u'socks4':
        socks_type = ProxyType.SOCKS4
        rdns = False
    elif url_components.scheme.lower() == u'socks4a':
        socks_type = ProxyType.SOCKS4A
        rdns = True
    else:
        raise ValueError(u'Unsupported SOCKS proxy scheme: %s' % url_components.scheme)

    def unquote_if_non_empty(s):
        if not s:
            return s
        return urllib.unquote_plus(s)
    return {
        u'proxytype': socks_type,
        u'addr': url_components.hostname,
        u'port': url_components.port or 1080,
        u'rdns': rdns,
        u'username': unquote_if_non_empty(url_components.username),
        u'password': unquote_if_non_empty(url_components.password),
    }


def get_redirect_method(method, status):
    u"""Unified redirect method handling"""

    # A 303 must either use GET or HEAD for subsequent request
    # https://datatracker.ietf.org/doc/html/rfc7231#section-6.4.4
    if status == 303 and method != u'HEAD':
        method = u'GET'
    # 301 and 302 redirects are commonly turned into a GET from a POST
    # for subsequent requests by browsers, so we'll do the same.
    # https://datatracker.ietf.org/doc/html/rfc7231#section-6.4.2
    # https://datatracker.ietf.org/doc/html/rfc7231#section-6.4.3
    if status in (301, 302) and method == u'POST':
        method = u'GET'
    return method


def create_ssl_context(
        verify=True, use_certifi=True, legacy_support=False, client_certificate=None):
    context = ssl.create_default_context()
    context.check_hostname = verify
    context.verify_mode = ssl.CERT_REQUIRED if verify else ssl.CERT_NONE
    # OpenSSL 1.1.1+ Python 3.8+ keylog file
    if hasattr(context, u'keylog_filename'):
        context.keylog_filename = os.environ.get(u'SSLKEYLOGFILE') or None

    # Some servers may reject requests if ALPN extension is not sent. See:
    # https://github.com/python/cpython/issues/85140
    # https://github.com/yt-dlp/yt-dlp/issues/3878
    try:
        context.set_alpn_protocols([u'http/1.1'])
    except NotImplementedError:
        pass
    if verify:
        ssl_load_certs(context, use_certifi)

    if legacy_support:
        context.options |= 4  # SSL_OP_LEGACY_SERVER_CONNECT
        context.set_ciphers(u'DEFAULT')  # compat

    elif ssl.OPENSSL_VERSION_INFO >= (1, 1, 1) and not ssl.OPENSSL_VERSION.startswith(u'LibreSSL'):
        # Use the default SSL ciphers and minimum TLS version settings from Python 3.10 [1].
        # This is to ensure consistent behavior across Python versions and libraries, and help avoid fingerprinting
        # in some situations [2][3].
        # [1] https://github.com/python/cpython/blob/3.10/Lib/ssl.py#L143-L144
        # [2] https://github.com/yt-dlp/yt-dlp/issues/772
        # [3] https://github.com/yt-dlp/yt-dlp/issues/1400
        # [4] https://github.com/yt-dlp/yt-dlp/issues/3354
        # 5. https://peps.python.org/pep-0644/#libressl-support
        # 6. https://github.com/yt-dlp/yt-dlp/commit/5b9f253fa0aee996cf1ed30185d4b502e00609c4#commitcomment-89054368
        context.set_ciphers(
            u'@SECLEVEL=2:ECDH+AESGCM:ECDH+CHACHA20:ECDH+AES:DHE+AES:!aNULL:!eNULL:!aDSS:!SHA1:!AESCCM')
        context.minimum_version = ssl.TLSVersion.TLSv1_2

    if client_certificate:
        client_certificate_key = client_certificate.get(u'client_certificate_key')
        client_certificate_password = client_certificate.get(u'client_certificate_password')
        try:
            context.load_cert_chain(
                client_certificate[u'client_certificate'], keyfile=client_certificate_key,
                password=client_certificate_password)
        except ssl.SSLError:
            raise RequestError(u'Unable to load client certificate')

        if getattr(context, u'post_handshake_auth', None) is not None:
            context.post_handshake_auth = True
    return context


class InstanceStoreMixin(object):
    def __init__(self, **kwargs):
        self.__instances = []
        super(InstanceStoreMixin, self).__init__(**kwargs)  # So that both MRO works

    @staticmethod
    def _create_instance(**kwargs):
        raise NotImplementedError

    def _get_instance(self, **kwargs):
        # TODO: Allow multiple instances to be stored for different keys
        if not self.__instances:
            self.__instances.append(self._create_instance(**kwargs))
        return self.__instances[0]

    def _close_instance(self, instance):
        if callable(getattr(instance, u'close', None)):
            instance.close()

    def _clear_instances(self):
        for instance in self.__instances:
            self._close_instance(instance)
        del self.__instances[:]


def add_accept_encoding_header(headers, supported_encodings):
    if u'Accept-Encoding' not in headers:
        headers[u'Accept-Encoding'] = u', '.join(supported_encodings) or u'identity'


def wrap_request_errors(func):
    u"""Wraps a request function to add the request handler to any Exception"""

    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RequestError, e:
            if e.handler is None:
                e.handler = self
            raise
        except Exception, e:
            raise RequestError(e, handler=self)

    return wrapper


def _socket_connect(af, socktype, proto, sa, timeout, source_address):
    sock = socket.socket(af, socktype, proto)
    try:
        if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
            sock.settimeout(timeout)
        if source_address is not None:
            sock.bind(source_address)
        sock.connect(sa)
        return sock
    except Exception:
        sock.close()
        raise


def _socks_connect(af, socktype, proto, sa, proxy_args, timeout, source_address):
    sock = sockssocket(af, socktype, proto)
    try:
        connect_proxy_args = proxy_args.copy()
        connect_proxy_args.update({u'addr': sa[0], u'port': sa[1]})
        sock.setproxy(**connect_proxy_args)
        if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
            sock.settimeout(timeout)
        if source_address is not None:
            sock.bind(source_address)
        sock.connect(sa)
        return sock
    except Exception:
        sock.close()
        raise


def create_connection(
    address,
    timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
    source_address=None,
    **_3to2kwargs
):
    # Work around socket.create_connection() which tries all addresses from getaddrinfo() including IPv6.
    # This filters the addresses based on the given source_address.
    # Based on: https://github.com/python/cpython/blob/main/Lib/socket.py#L810
    if u'_create_socket_func' in _3to2kwargs:
        _create_socket_func = _3to2kwargs[u'_create_socket_func']
        del _3to2kwargs[u'_create_socket_func']
    else:
        _create_socket_func = _socket_connect
    host, port = address
    ip_addrs = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
    if not ip_addrs:
        raise OSError(u'getaddrinfo returns an empty list')
    if source_address is not None:
        af = socket.AF_INET if u':' not in source_address[0] else socket.AF_INET6
        ip_addrs = [addr for addr in ip_addrs if addr[0] == af]
        if not ip_addrs:
            raise OSError(
                u'no matching address family for %s:%s and source_address %s' % (
                    host, port, source_address))
    err = None
    for res in ip_addrs:
        af, socktype, proto, _, sa = res
        sock = None
        try:
            sock = _create_socket_func(af, socktype, proto, sa, timeout, source_address)
            # See: https://github.com/python/cpython/commit/3569623
            #      https://bugs.python.org/issue36820
            err = None
            return sock
        except OSError, e:
            err = e

    try:
        raise err
    finally:
        err = None
