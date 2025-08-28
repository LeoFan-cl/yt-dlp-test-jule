# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import abc

from yt_dlp.extractor.youtube.pot._provider import (
    IEContentProvider,
    IEContentProviderError,
    register_preference_generic,
    register_provider_generic,
)
from yt_dlp.extractor.youtube.pot._registry import (
    _pot_cache_provider_preferences,
    _pot_cache_providers,
    _pot_pcs_providers,
)
from yt_dlp.extractor.youtube.pot.provider import PoTokenRequest
from ...compat._legacy import compat_dataclasses as dataclasses


class PoTokenCacheProviderError(IEContentProviderError):
    """An error occurred while fetching a PO Token"""


class PoTokenCacheProvider(IEContentProvider):
    __metaclass__ = abc.ABCMeta
    _PROVIDER_KEY_SUFFIX = 'PCP'

    @abc.abstractmethod
    def get(self, key):
        pass

    @abc.abstractmethod
    def store(self, key, value, expires_at):
        pass

    @abc.abstractmethod
    def delete(self, key):
        pass


class CacheProviderWritePolicy(object):
    WRITE_ALL = 1
    WRITE_FIRST = 2


class PoTokenCacheSpec(object):
    def __init__(self, key_bindings, default_ttl, write_policy=CacheProviderWritePolicy.WRITE_ALL, _provider=None):
        self.key_bindings = key_bindings
        self.default_ttl = default_ttl
        self.write_policy = write_policy
        self._provider = _provider


class PoTokenCacheSpecProvider(IEContentProvider):
    __metaclass__ = abc.ABCMeta
    _PROVIDER_KEY_SUFFIX = 'PCSP'

    def is_available(self):
        return True

    @abc.abstractmethod
    def generate_cache_spec(self, request):
        """Generate a cache spec for the given request"""
        pass


def register_provider(provider):
    """Register a PoTokenCacheProvider class"""
    return register_provider_generic(
        provider=provider,
        base_class=PoTokenCacheProvider,
        registry=_pot_cache_providers.value,
    )


def register_spec(provider):
    """Register a PoTokenCacheSpecProvider class"""
    return register_provider_generic(
        provider=provider,
        base_class=PoTokenCacheSpecProvider,
        registry=_pot_pcs_providers.value,
    )


def register_preference(*providers):
    """Register a preference for a PoTokenCacheProvider"""
    return register_preference_generic(
        PoTokenCacheProvider,
        _pot_cache_provider_preferences.value,
        *providers,
    )
