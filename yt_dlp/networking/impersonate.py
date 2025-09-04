from __future__ import absolute_import

import re
from abc import ABC
from functools import total_ordering

from .common import (
    Features,
    register_preference,
    RequestHandler,
)
from .exceptions import UnsupportedRequest
from ..utils import join_nonempty
from ..utils.networking import std_headers, HTTPHeaderDict


class ImpersonateTarget(object):
    u"""
    A target for browser impersonation.

    Parameters:
    client: The client to impersonate (e.g. 'chrome', 'firefox').
    version: The version of the client to impersonate.
    os: The OS to impersonate (e.g. 'windows', 'macos').
    os_version: The version of the OS to impersonate.

    Note: None is used to indicate to match any.

    """
    def __init__(self, client=None, version=None, os=None, os_version=None):
        self._client = client
        self._version = version
        self._os = os
        self._os_version = os_version
        self._initialized = True
        self.__post_init__()

    @property
    def client(self):
        return self._client

    @property
    def version(self):
        return self._version

    @property
    def os(self):
        return self._os

    @property
    def os_version(self):
        return self._os_version

    def __setattr__(self, name, value):
        if hasattr(self, u'_initialized'):
            raise AttributeError(u"can't set attribute")
        super(ImpersonateTarget, self).__setattr__(name, value)

    def __post_init__(self):
        if self.version and not self.client:
            raise ValueError(u'client is required if version is set')
        if self.os_version and not self.os:
            raise ValueError(u'os is required if os_version is set')

    def __contains__(self, target):
        if not isinstance(target, ImpersonateTarget):
            return False
        return (
            (self.client is None or self.client == target.client)
            and (self.version is None or self.version == target.version)
            and (self.os is None or self.os == target.os)
            and (self.os_version is None or self.os_version == target.os_version)
        )

    def __str__(self):
        return u'%s:%s' % (join_nonempty(self.client, self.version), join_nonempty(self.os, self.os_version).rstrip(u':'))

    def __repr__(self):
        return u"ImpersonateTarget(client=%r, version=%r, os=%r, os_version=%r)" % (
            self.client, self.version, self.os, self.os_version)

    def __eq__(self, other):
        if not isinstance(other, ImpersonateTarget):
            return NotImplemented
        return (self.client, self.version, self.os, self.os_version) == (other.client, other.version, other.os, other.os_version)

    def __lt__(self, other):
        if not isinstance(other, ImpersonateTarget):
            return NotImplemented
        # None is smaller than any string
        return (self.client or u'', self.version or u'', self.os or u'', self.os_version or u'') < \
               (other.client or u'', other.version or u'', other.os or u'', other.os_version or u'')

    def __hash__(self):
        return hash((self.client, self.version, self.os, self.os_version))

    @classmethod
    def from_str(cls, target):
        mobj = re.fullmatch(ur'(?:(?P<client>[^:-]+)(?:-(?P<version>[^:-]+))?)?(?::(?:(?P<os>[^:-]+)(?:-(?P<os_version>[^:-]+))?)?)?', target)
        if not mobj:
            raise ValueError(u'Invalid impersonate target "%s"' % target)
        return cls(**mobj.groupdict())


ImpersonateTarget = total_ordering(ImpersonateTarget)

class ImpersonateRequestHandler(RequestHandler, ABC):
    u"""
    Base class for request handlers that support browser impersonation.

    This provides a method for checking the validity of the impersonate extension,
    and for getting the headers for a given request.

    To add support for impersonation to a RequestHandler, you must:
    1. Subclass this class.
    2. Define a `_SUPPORTED_IMPERSONATE_TARGET_MAP` dictionary.
       This should map an `ImpersonateTarget` to the value that the underlying
       library expects for the impersonation target.
    3. Call `self._get_impersonate_headers(request)` in your `_send` method
       to get the headers for the request.
    """
    _SUPPORTED_IMPERSONATE_TARGET_MAP = {}

    def __init__(self, **kwargs):
        if u'impersonate' in kwargs:
            impersonate = kwargs[u'impersonate']
            del kwargs[u'impersonate']
        else:
            impersonate = None
        super(ImpersonateRequestHandler, self).__init__(**kwargs)
        self.impersonate = impersonate

    def _check_impersonate_target(self, target):
        assert isinstance(target, (ImpersonateTarget, type(None)))
        if target is None or not self.supported_targets:
            return
        if not self.is_supported_target(target):
            raise UnsupportedRequest(u'Unsupported impersonate target: %s' % target)

    def _check_extensions(self, extensions):
        super(ImpersonateRequestHandler, self)._check_extensions(extensions)
        if u'impersonate' in extensions:
            self._check_impersonate_target(extensions.get(u'impersonate'))

    def _validate(self, request):
        super(ImpersonateRequestHandler, self)._validate(request)
        self._check_impersonate_target(self.impersonate)

    def _resolve_target(self, target):
        u"""Resolve a target to a supported target."""
        if target is None:
            return
        for supported_target in self.supported_targets:
            if target in supported_target:
                # Resolve to the first supported target that matches
                # Since the supported targets are sorted by preference,
                # this will be the best match
                return supported_target

    @classproperty
    def supported_targets(cls):
        return tuple(cls._SUPPORTED_IMPERSONATE_TARGET_MAP.keys())

    def is_supported_target(self, target):
        assert isinstance(target, ImpersonateTarget)
        return self._resolve_target(target) is not None

    def _get_request_target(self, request):
        u"""Get the requested target for the request"""
        return self._resolve_target(request.extensions.get(u'impersonate') or self.impersonate)

    def _prepare_impersonate_headers(self, request, headers):  # noqa: B027
        u"""Additional operations to prepare headers before building. To be extended by subclasses.
        @param request: Request object
        @param headers: Merged headers to prepare
        """

    def _get_impersonate_headers(self, request):
        u"""
        Get headers for external impersonation use.
        Subclasses may define a _prepare_impersonate_headers method to modify headers after merge but before building.
        """
        # Remove any existing impersonation headers
        headers = self._merge_headers(request.headers)
        if self._get_request_target(request):
            for k in list(headers.keys()):
                if k.lower() in (u'user-agent', u'accept', u'accept-language', u'accept-encoding', u'sec-ch-ua'):
                    headers.pop(k)

        self._prepare_impersonate_headers(request, headers)
        if request.extensions.get(u'keep_header_casing'):
            return headers.sensitive()
        return dict(headers)


@register_preference(ImpersonateRequestHandler)
def impersonate_preference(rh, request):
    if request.extensions.get(u'impersonate') or rh.impersonate:
        return 1000
    return 0
