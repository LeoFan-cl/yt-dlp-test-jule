from __future__ import absolute_import

from ..dependencies import typing

from itertools import ifilter

class YoutubeDLError(Exception):
    msg = None

    def __init__(self, msg=None):
        if msg is not None:
            self.msg = msg
        elif self.msg is None:
            self.msg = type(self).__name__
        super(YoutubeDLError, self).__init__(self.msg)

if typing.TYPE_CHECKING:
    from .common import RequestHandler, Response


class RequestError(YoutubeDLError):
    def __init__(
        self,
        msg=None,
        cause=None,
        handler=None,
    ):
        self.handler = handler
        self.cause = cause
        if not msg and cause:
            msg = unicode(cause)
        super(RequestError, self).__init__(msg)


class UnsupportedRequest(RequestError):
    u"""raised when a handler cannot handle a request"""
    pass


class NoSupportingHandlers(RequestError):
    u"""raised when no handlers can support a request for various reasons"""

    def __init__(self, unsupported_errors, unexpected_errors):
        self.unsupported_errors = unsupported_errors or []
        self.unexpected_errors = unexpected_errors or []

        err_handler_map = {}
        for err in unsupported_errors:
            err_handler_map.setdefault(err.msg, []).append(err.handler.RH_NAME)

        reason_str = u', '.join([u'%s (%s)' % (msg, u", ".join(handlers)) for msg, handlers in err_handler_map.items()])
        if unexpected_errors:
            reason_str = u' + '.join(ifilter(None, [reason_str, u'%d unexpected error(s)' % len(unexpected_errors)]))

        err_str = u'Unable to handle request'
        if reason_str:
            err_str += u': %s' % reason_str

        super(NoSupportingHandlers, self).__init__(msg=err_str)


class TransportError(RequestError):
    u"""Network related errors"""


class HTTPError(RequestError):
    def __init__(self, response, redirect_loop=False):
        self.response = response
        self.status = response.status
        self.reason = response.reason
        self.redirect_loop = redirect_loop
        msg = u'HTTP Error %s: %s' % (response.status, response.reason)
        if redirect_loop:
            msg += u' (redirect loop detected)'

        super(HTTPError, self).__init__(msg=msg)

    def close(self):
        self.response.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class SSLError(TransportError):
    pass


class IncompleteRead(TransportError):
    def __init__(self, partial, expected=None, **kwargs):
        self.partial = partial
        self.expected = expected
        msg = u'%d bytes read' % partial
        if expected is not None:
            msg += u', %d more expected' % expected

        super(IncompleteRead, self).__init__(msg=msg, **kwargs)

    def __repr__(self):
        return u'<IncompleteRead: %s>' % self.msg


class ProxyError(TransportError):
    pass


class CertificateVerifyError(SSLError):
    u"""Raised when certificate validated has failed"""
    pass

network_exceptions = (
    RequestError,
    UnsupportedRequest,
    NoSupportingHandlers,
    TransportError,
    HTTPError,
    SSLError,
    IncompleteRead,
    ProxyError,
    CertificateVerifyError,
)
