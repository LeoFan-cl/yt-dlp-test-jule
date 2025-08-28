from __future__ import absolute_import

import io
import itertools
import math
import re
import urlparse

from ._helper import InstanceStoreMixin
from ..utils.networking import select_proxy
from .common import (
    Features,
    Request,
    Response,
    register_preference,
    register_rh,
)
from .exceptions import (
    CertificateVerifyError,
    IncompleteRead,
    ProxyError,
    SSLError,
    TransportError,
)
from ..compat import compat_urllib_error
from ..downloader.http import HTTPError
from .impersonate import ImpersonateRequestHandler, ImpersonateTarget
from ..dependencies import curl_cffi, certifi
from ..utils import int_or_none
from itertools import imap

if curl_cffi is None:
    raise ImportError(u'curl_cffi is not installed')


curl_cffi_version = tuple(imap(int, re.split(ur'[^\d]+', curl_cffi.__version__)[:3]))

if curl_cffi_version != (0, 5, 10) and not (0, 10) <= curl_cffi_version < (0, 14):
    curl_cffi._yt_dlp__version = '%s (unsupported)' % curl_cffi.__version__
    raise ImportError(u'Only curl_cffi versions 0.5.10, 0.10.x, 0.11.x, 0.12.x, 0.13.x are supported')

import curl_cffi.requests
from curl_cffi.const import CurlECode, CurlOpt


class CurlCFFIResponseReader(io.IOBase):
    def __init__(self, response):
        self._response = response
        self._iterator = response.iter_content()
        self._buffer = b''
        self.bytes_read = 0

    def readable(self):
        return True

    def read(self, size=None):
        exception_raised = True
        try:
            while self._iterator and (size is None or len(self._buffer) < size):
                try:
                    chunk = self._iterator.next()
                    self._buffer += chunk
                except StopIteration:
                    self._iterator = None
                    break
            if size is None:
                ret = self._buffer
                self._buffer = b''
            else:
                ret = self._buffer[:size]
                self._buffer = self._buffer[size:]
            self.bytes_read += len(ret)
            exception_raised = False
            return ret
        finally:
            if exception_raised:
                self.close()

    def close(self):
        if not self.closed:
            self._response.close()
            self._buffer = b''
        super(CurlCFFIResponseReader, self).close()


class CurlCFFIResponseAdapter(Response):
    def __init__(self, response):
        super(CurlCFFIResponseAdapter, self).__init__(
            fp=CurlCFFIResponseReader(response),
            headers=response.headers,
            url=response.url,
            code=response.status_code,
            reason=response.reason)

    def read(self, amt=None):
        try:
            return self.fp.read(amt)
        except curl_cffi.requests.errors.RequestsError, e:
            if e.code == CurlECode.PARTIAL_FILE:
                content_length = e.response and int_or_none(e.response.headers.get(u'Content-Length'))
                raise IncompleteRead(
                    partial=self.fp.bytes_read,
                    expected=content_length - self.fp.bytes_read if content_length is not None else None,
                    cause=e)
            raise TransportError(cause=e)


# See: https://github.com/lexiforest/curl_cffi?tab=readme-ov-file#supported-impersonate-browsers
#      https://github.com/lexiforest/curl-impersonate?tab=readme-ov-file#supported-browsers
BROWSER_TARGETS = {
    (0, 5): {
        u'chrome99': ImpersonateTarget(u'chrome', u'99', u'windows', u'10'),
        u'chrome99_android': ImpersonateTarget(u'chrome', u'99', u'android', u'12'),
        u'chrome100': ImpersonateTarget(u'chrome', u'100', u'windows', u'10'),
        u'chrome101': ImpersonateTarget(u'chrome', u'101', u'windows', u'10'),
        u'chrome104': ImpersonateTarget(u'chrome', u'104', u'windows', u'10'),
        u'chrome107': ImpersonateTarget(u'chrome', u'107', u'windows', u'10'),
        u'chrome110': ImpersonateTarget(u'chrome', u'110', u'windows', u'10'),
        u'edge99': ImpersonateTarget(u'edge', u'99', u'windows', u'10'),
        u'edge101': ImpersonateTarget(u'edge', u'101', u'windows', u'10'),
        u'safari153': ImpersonateTarget(u'safari', u'15.3', u'macos', u'11'),
        u'safari155': ImpersonateTarget(u'safari', u'15.5', u'macos', u'12'),
    },
    (0, 7): {
        u'chrome116': ImpersonateTarget(u'chrome', u'116', u'windows', u'10'),
        u'chrome119': ImpersonateTarget(u'chrome', u'119', u'macos', u'14'),
        u'chrome120': ImpersonateTarget(u'chrome', u'120', u'macos', u'14'),
        u'chrome123': ImpersonateTarget(u'chrome', u'123', u'macos', u'14'),
        u'chrome124': ImpersonateTarget(u'chrome', u'124', u'macos', u'14'),
        u'safari170': ImpersonateTarget(u'safari', u'17.0', u'macos', u'14'),
        u'safari172_ios': ImpersonateTarget(u'safari', u'17.2', u'ios', u'17.2'),
    },
    (0, 9): {
        u'safari153': ImpersonateTarget(u'safari', u'15.3', u'macos', u'14'),
        u'safari155': ImpersonateTarget(u'safari', u'15.5', u'macos', u'14'),
        u'chrome119': ImpersonateTarget(u'chrome', u'119', u'macos', u'14'),
        u'chrome120': ImpersonateTarget(u'chrome', u'120', u'macos', u'14'),
        u'chrome123': ImpersonateTarget(u'chrome', u'123', u'macos', u'14'),
        u'chrome124': ImpersonateTarget(u'chrome', u'124', u'macos', u'14'),
        u'chrome131': ImpersonateTarget(u'chrome', u'131', u'macos', u'14'),
        u'chrome131_android': ImpersonateTarget(u'chrome', u'131', u'android', u'14'),
        u'chrome133a': ImpersonateTarget(u'chrome', u'133', u'macos', u'15'),
        u'firefox133': ImpersonateTarget(u'firefox', u'133', u'macos', u'14'),
        u'safari180': ImpersonateTarget(u'safari', u'18.0', u'macos', u'15'),
        u'safari180_ios': ImpersonateTarget(u'safari', u'18.0', u'ios', u'18.0'),
    },
    (0, 10): {
        u'firefox135': ImpersonateTarget(u'firefox', u'135', u'macos', u'14'),
    },
    (0, 11): {
        u'tor145': ImpersonateTarget(u'tor', u'14.5', u'macos', u'14'),
        u'safari184': ImpersonateTarget(u'safari', u'18.4', u'macos', u'15'),
        u'safari184_ios': ImpersonateTarget(u'safari', u'18.4', u'ios', u'18.4'),
        u'chrome136': ImpersonateTarget(u'chrome', u'136', u'macos', u'15'),
    },
    (0, 12): {
        u'safari260': ImpersonateTarget(u'safari', u'26.0', u'macos', u'26'),
        u'safari260_ios': ImpersonateTarget(u'safari', u'26.0', u'ios', u'26.0'),
    },
}

# Needed for curl_cffi < 0.11
# See: https://github.com/lexiforest/curl_cffi/commit/d2f15c7a31506a08d217fcc04ae7570c39f5f5bb
_TARGETS_COMPAT_LOOKUP = {
    u'safari153': u'safari15_3',
    u'safari155': u'safari15_5',
    u'safari170': u'safari17_0',
    u'safari172_ios': u'safari17_2_ios',
    u'safari180': u'safari18_0',
    u'safari180_ios': u'safari18_0_ios',
}


class CurlCFFIRH(ImpersonateRequestHandler, InstanceStoreMixin):
    RH_NAME = u'curl_cffi'
    _SUPPORTED_URL_SCHEMES = (u'http', u'https')
    _SUPPORTED_FEATURES = (Features.NO_PROXY, Features.ALL_PROXY)
    _SUPPORTED_PROXY_SCHEMES = (u'http', u'https', u'socks4', u'socks4a', u'socks5', u'socks5h')
    _SUPPORTED_IMPERSONATE_TARGET_MAP = dict(
        (
            target,
            (
                name if curl_cffi_version >= (0, 11)
                else _TARGETS_COMPAT_LOOKUP.get(name, name) if curl_cffi_version >= (0, 9)
                else curl_cffi.requests.BrowserType[_TARGETS_COMPAT_LOOKUP.get(name, name)]
            )
        ) for name, target in dict(sorted(itertools.chain.from_iterable(
            targets.items()
            for version, targets in BROWSER_TARGETS.items()
            if curl_cffi_version >= version
        ), key=lambda x: (
            # deprioritize mobile targets since they give very different behavior
            x[1].os not in (u'ios', u'android'),
            # prioritize tor < edge < firefox < safari < chrome
            (u'tor', u'edge', u'firefox', u'safari', u'chrome').index(x[1].client),
            # prioritize newest version
            float(x[1].version) if x[1].version else 0,
            # group by os name
            x[1].os,
        ), reverse=True)).items()
    )

    def _create_instance(self, cookiejar=None):
        return curl_cffi.requests.Session(cookies=cookiejar)

    def _check_extensions(self, extensions):
        super(CurlCFFIRH, self)._check_extensions(extensions)
        extensions.pop(u'impersonate', None)
        extensions.pop(u'cookiejar', None)
        extensions.pop(u'timeout', None)
        # CurlCFFIRH ignores legacy ssl options currently.
        # Impersonation generally uses a looser SSL configuration than urllib/requests.
        extensions.pop(u'legacy_ssl', None)

    def send(self, request):
        target = self._get_request_target(request)
        try:
            response = super(CurlCFFIRH, self).send(request)
        except HTTPError, e:
            e.response.extensions[u'impersonate'] = target
            raise
        response.extensions[u'impersonate'] = target
        return response

    def _send(self, request):
        max_redirects_exceeded = False
        session = self._get_instance(
            cookiejar=self._get_cookiejar(request) if u'cookie' not in request.headers else None)

        if self.verbose:
            session.curl.setopt(CurlOpt.VERBOSE, 1)

        proxies = self._get_proxies(request)
        if u'no' in proxies:
            session.curl.setopt(CurlOpt.NOPROXY, proxies[u'no'])
            proxies.pop(u'no', None)

        # curl doesn't support per protocol proxies, so we select the one that matches the request protocol
        proxy = select_proxy(request.url, proxies=proxies)
        if proxy:
            session.curl.setopt(CurlOpt.PROXY, proxy)
            scheme = urlparse.urlparse(request.url).scheme.lower()
            if scheme != u'http':
                # Enable HTTP CONNECT for HTTPS urls.
                # Don't use CONNECT for http for compatibility with urllib behaviour.
                # See: https://curl.se/libcurl/c/CURLOPT_HTTPPROXYTUNNEL.html
                session.curl.setopt(CurlOpt.HTTPPROXYTUNNEL, 1)

        headers = self._get_impersonate_headers(request)

        if self._client_cert:
            session.curl.setopt(CurlOpt.SSLCERT, self._client_cert[u'client_certificate'])
            client_certificate_key = self._client_cert.get(u'client_certificate_key')
            client_certificate_password = self._client_cert.get(u'client_certificate_password')
            if client_certificate_key:
                session.curl.setopt(CurlOpt.SSLKEY, client_certificate_key)
            if client_certificate_password:
                session.curl.setopt(CurlOpt.KEYPASSWD, client_certificate_password)

        try:
            curl_response = session.request(
                method=request.method,
                url=request.url,
                headers=headers,
                data=request.data,
                verify=certifi.where(),
                allow_redirects=False,
                timeout=self._get_timeout(request.extensions),
                impersonate=self._get_impersonate_target(request),
                interface=self.source_address,
                stream=True,
            )
        except curl_cffi.requests.errors.RequestsError, e:
            if e.code == CurlECode.PEER_FAILED_VERIFICATION:
                raise CertificateVerifyError(cause=e)

            elif e.code == CurlECode.SSL_CONNECT_ERROR:
                raise SSLError(cause=e)

            elif e.code == CurlECode.TOO_MANY_REDIRECTS:
                max_redirects_exceeded = True
                curl_response = e.response

            elif (
                e.code == CurlECode.PROXY
                or (e.code == CurlECode.RECV_ERROR and u'CONNECT' in unicode(e))
            ):
                raise ProxyError(cause=e)
            else:
                raise TransportError(cause=e)

        response = CurlCFFIResponseAdapter(curl_response)

        if max_redirects_exceeded:
            raise HTTPError(response, redirect_loop=True)

        return response

CurlCFFIRH = register_rh(CurlCFFIRH)

@register_preference(CurlCFFIRH)
def curl_cffi_preference(rh, request):
    if request.extensions.get('impersonate'):
        return 2
    return -1
