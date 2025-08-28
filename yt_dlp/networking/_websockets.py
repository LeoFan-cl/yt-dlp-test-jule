from __future__ import with_statement
from __future__ import absolute_import

import functools
import io
import logging
import ssl
import sys
import socket

from .common import (
    Features,
    WebSocketRequestHandler,
    WebSocketResponse,
    register_rh,
)
from .exceptions import (
    CertificateVerifyError,
    HTTPError,
    ProxyError,
    RequestError,
    SSLError,
    TransportError,
)
from ._helper import (
    create_ssl_context,
    make_socks_proxy_opts,
)
from ..dependencies import websocket
from ..socks import ProxyError as SocksProxyError
from ..utils import int_or_none
from itertools import imap
from urlparse import urlparse

if not websocket:
    raise ImportError(u'websocket-client is not installed. Please install by running `python -m pip install websocket-client`')

from websocket import create_connection, WebSocketException


class WebsocketsResponseAdapter(WebSocketResponse):

    def __init__(self, ws, url):
        # websocket-client does not expose the HTTP upgrade response
        # We create a dummy response with status 101
        super(WebsocketsResponseAdapter, self).__init__(
            fp=io.BytesIO(b''),
            url=url,
            headers={},
            status=101,
            reason='Switching Protocols')
        self._ws = ws

    def close(self):
        self._ws.close()
        super(WebsocketsResponseAdapter, self).close()

    def send(self, message):
        try:
            return self._ws.send(message)
        except (WebSocketException, RuntimeError, socket.timeout,
                # See https://github.com/websocket-client/websocket-client/issues/630
                socket.error, ssl.SSLError), e:
            raise TransportError(cause=e)
        except SocksProxyError, e:
            raise ProxyError(cause=e)
        except TypeError, e:
            raise RequestError(cause=e)

    def recv(self):
        try:
            return self._ws.recv()
        except SocksProxyError, e:
            raise ProxyError(cause=e)
        except (WebSocketException, RuntimeError, socket.timeout,
                socket.error, ssl.SSLError), e:
            raise TransportError(cause=e)


class WebsocketsRH(WebSocketRequestHandler):
    u"""
    Websockets request handler
    https://github.com/websocket-client/websocket-client
    """
    _SUPPORTED_URL_SCHEMES = (u'wss', u'ws')
    _SUPPORTED_PROXY_SCHEMES = (u'socks4', u'socks4a', u'socks5', u'socks5h')
    _SUPPORTED_FEATURES = (Features.ALL_PROXY, Features.NO_PROXY)
    RH_NAME = u'websocket_client'

    def __init__(self, *args, **kwargs):
        super(WebsocketsRH, self).__init__(*args, **kwargs)
        if self._logger.level == logging.DEBUG:
            websocket.enableTrace(True, sys.stdout)

    def _check_extensions(self, extensions):
        super(WebsocketsRH, self)._check_extensions(extensions)
        extensions.pop(u'timeout', None)
        extensions.pop(u'cookiejar', None)
        extensions.pop(u'legacy_ssl', None)
        extensions.pop(u'keep_header_casing', None)

    def close(self):
        pass

    def _prepare_headers(self, request, headers):
        if u'cookie' not in headers:
            cookiejar = self._get_cookiejar(request)
            cookie_header = cookiejar.get_cookie_header(request.url)
            if cookie_header:
                headers[u'cookie'] = cookie_header

    def _send(self, request):
        timeout = self._calculate_timeout(request)
        headers = self._get_headers(request)

        conn_kwargs = {
            'timeout': timeout,
            'header': headers,
            'source_address': (self.source_address, 0) if self.source_address else None,
        }

        proxy = select_proxy(request.url, self._get_proxies(request))
        if proxy:
            proxy_opts = make_socks_proxy_opts(proxy)
            conn_kwargs.update({
                'http_proxy_host': proxy_opts['addr'],
                'http_proxy_port': proxy_opts['port'],
                'http_proxy_auth': (proxy_opts['username'], proxy_opts['password']) if proxy_opts['username'] else None,
                'proxy_type': proxy_opts['proxytype'].lower(),
            })

        ssl_ctx = self._make_sslcontext(legacy_ssl_support=request.extensions.get(u'legacy_ssl'))
        sslopt = {
            "cert_reqs": ssl_ctx.verify_mode,
            "check_hostname": ssl_ctx.check_hostname,
        }
        if ssl_ctx.verify_mode != ssl.CERT_NONE:
            # websocket-client does not support load_default_certs,
            # so we can't do that. It uses the system's default certs.
            pass
        conn_kwargs['sslopt'] = sslopt

        try:
            conn = create_connection(request.url, **conn_kwargs)
            return WebsocketsResponseAdapter(conn, url=request.url)

        except (WebSocketException, socket.error, ssl.SSLError,
                # See https://github.com/websocket-client/websocket-client/issues/506
                IOError), e:
            if isinstance(e, ssl.SSLCertVerificationError):
                raise CertificateVerifyError(cause=e)
            elif isinstance(e, ssl.SSLError):
                raise SSLError(cause=e)
            elif isinstance(e, socket.timeout):
                raise TransportError(cause=e)
            elif isinstance(e, SocksProxyError):
                raise ProxyError(cause=e)

            # websocket.WebSocketBadStatusException is a subclass of WebSocketException
            # It is raised for non-101 responses.
            if isinstance(e, websocket.WebSocketBadStatusException):
                raise HTTPError(
                    Response(
                        fp=io.BytesIO(e.resp_body),
                        url=request.url,
                        headers=e.headers,
                        status=e.status_code,
                        reason=None),
                )
            raise TransportError(cause=e)
        except Exception, e:
            raise RequestError(cause=e)

WebsocketsRH = register_rh(WebsocketsRH)
