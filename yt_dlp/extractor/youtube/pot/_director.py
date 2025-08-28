# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import base64
import binascii
import calendar
import datetime as dt
import hashlib
import json
import typing
from threading import Lock

from yt_dlp.extractor.youtube.pot._provider import (
    BuiltinIEContentProvider,
    IEContentProvider,
    IEContentProviderLogger,
)
from yt_dlp.extractor.youtube.pot._registry import (
    _pot_cache_provider_preferences,
    _pot_cache_providers,
    _pot_pcs_providers,
    _pot_providers,
    _ptp_preferences,
)
from yt_dlp.extractor.youtube.pot.cache import (
    CacheProviderWritePolicy,
    PoTokenCacheProvider,
    PoTokenCacheProviderError,
    PoTokenCacheSpec,
    PoTokenCacheSpecProvider,
)
from yt_dlp.extractor.youtube.pot.provider import (
    PoTokenProvider,
    PoTokenProviderError,
    PoTokenProviderRejectedRequest,
    PoTokenRequest,
    PoTokenResponse,
    provider_bug_report_message,
)
from yt_dlp.utils import bug_reports_message, format_field, join_nonempty
from...compat._legacy import compat_dataclasses as dataclasses


class YoutubeIEContentProviderLogger(IEContentProviderLogger):
    def __init__(self, ie, prefix, log_level=None):
        self.__ie = ie
        self.prefix = prefix
        self.log_level = log_level if log_level is not None else self.LogLevel.INFO

    def _format_msg(self, message):
        prefixstr = format_field(self.prefix, None, '[%s] ')
        return '{0}{1}'.format(prefixstr, message)

    def trace(self, message):
        if self.log_level <= self.LogLevel.TRACE:
            self.__ie.write_debug(self._format_msg('TRACE: ' + message))

    def debug(self, message):
        if self.log_level <= self.LogLevel.DEBUG:
            self.__ie.write_debug(self._format_msg(message))

    def info(self, message):
        if self.log_level <= self.LogLevel.INFO:
            self.__ie.to_screen(self._format_msg(message))

    def warning(self, message, once=False):
        if self.log_level <= self.LogLevel.WARNING:
            self.__ie.report_warning(self._format_msg(message), only_once=once)

    def error(self, message):
        if self.log_level <= self.LogLevel.ERROR:
            self.__ie._downloader.report_error(self._format_msg(message), is_error=False)


class PoTokenCache(object):

    def __init__(
        self,
        logger,
        cache_providers,
        cache_spec_providers,
        cache_provider_preferences=None,
    ):
        self.cache_providers = {
            provider.PROVIDER_KEY: provider for provider in (cache_providers or [])}
        self.cache_provider_preferences = cache_provider_preferences or []
        self.cache_spec_providers = {
            provider.PROVIDER_KEY: provider for provider in (cache_spec_providers or [])}
        self.logger = logger

    def _get_cache_providers(self, request):
        preferences = {
            provider: sum(pref(provider, request) for pref in self.cache_provider_preferences)
            for provider in self.cache_providers.values()
        }
        if self.logger.log_level <= self.logger.LogLevel.TRACE:
            self.logger.trace('PO Token Cache Providers: {0}'.format(provider_display_list(self.cache_providers.values())))
            self.logger.trace('Cache Provider preferences for this request: {}'.format(', '.join(
                '{0}={1}'.format(provider.PROVIDER_KEY, pref) for provider, pref in preferences.items())))

        return (
            provider for provider in sorted(
                self.cache_providers.values(), key=preferences.get, reverse=True) if provider.is_available())

    def _get_cache_spec(self, request):
        for provider in self.cache_spec_providers.values():
            if not provider.is_available():
                continue
            try:
                spec = provider.generate_cache_spec(request)
                if not spec:
                    continue
                if not validate_cache_spec(spec):
                    self.logger.error(
                        'PoTokenCacheSpecProvider "{0}" generate_cache_spec() returned invalid spec {1}{2}'.format(
                            provider.PROVIDER_KEY, spec, provider_bug_report_message(provider)))
                    continue
                spec = dataclasses.replace(spec, _provider=provider)
                self.logger.trace(
                    'Retrieved cache spec {0} from cache spec provider "{1}"'.format(spec, provider.PROVIDER_NAME))
                return spec
            except Exception as e:
                self.logger.error(
                    'Error occurred with "{0}" PO Token cache spec provider: {1!r}{2}'.format(
                        provider.PROVIDER_NAME, e, provider_bug_report_message(provider)))
                continue
        return None

    def _generate_key_bindings(self, spec):
        bindings_cleaned = {
            k: v for k, v in spec.key_bindings.items() if v is not None
        }
        bindings_cleaned.update({'_dlp_cache': 'v1'})

        if spec._provider:
            bindings_cleaned['_p'] = spec._provider.PROVIDER_KEY
        self.logger.trace('Generated cache key bindings: {0}'.format(bindings_cleaned))
        return bindings_cleaned

    def _generate_key(self, bindings):
        binding_string = ''.join(repr(dict(sorted(bindings.items()))))
        return hashlib.sha256(binding_string.encode()).hexdigest()

    def get(self, request):
        spec = self._get_cache_spec(request)
        if not spec:
            self.logger.trace('No cache spec available for this request, unable to fetch from cache')
            return None

        cache_key = self._generate_key(self._generate_key_bindings(spec))
        self.logger.trace('Attempting to access PO Token cache using key: {0}'.format(cache_key))

        for idx, provider in enumerate(self._get_cache_providers(request)):
            try:
                self.logger.trace(
                    'Attempting to fetch PO Token response from "{0}" cache provider'.format(provider.PROVIDER_NAME))
                cache_response = provider.get(cache_key)
                if not cache_response:
                    continue
                try:
                    po_token_response = PoTokenResponse(**json.loads(cache_response))
                except (TypeError, ValueError, json.JSONDecodeError):
                    po_token_response = None
                if not validate_response(po_token_response):
                    self.logger.error(
                        'Invalid PO Token response retrieved from cache provider "{0}": {1}{2}'.format(
                            provider.PROVIDER_NAME, cache_response, provider_bug_report_message(provider)))
                    provider.delete(cache_key)
                    continue
                self.logger.trace(
                    'PO Token response retrieved from cache using "{0}" provider: {1}'.format(
                        provider.PROVIDER_NAME, po_token_response))
                if idx > 0:
                    self.logger.trace('Writing PO Token response to highest priority cache provider')
                    self.store(request, po_token_response, write_policy=CacheProviderWritePolicy.WRITE_FIRST)

                return po_token_response
            except PoTokenCacheProviderError as e:
                self.logger.warning(
                    'Error from "{0}" PO Token cache provider: {1!r}{2}'.format(
                        provider.PROVIDER_NAME, e, provider_bug_report_message(provider) if not e.expected else ""))
                continue
            except Exception as e:
                self.logger.error(
                    'Error occurred with "{0}" PO Token cache provider: {1!r}{2}'.format(
                        provider.PROVIDER_NAME, e, provider_bug_report_message(provider)),
                )
                continue
        return None

    def store(
        self,
        request,
        response,
        write_policy=None,
    ):
        spec = self._get_cache_spec(request)
        if not spec:
            self.logger.trace('No cache spec available for this request. Not caching.')
            return

        if not validate_response(response):
            self.logger.error(
                'Invalid PO Token response provided to PoTokenCache.store(): {0}{1}'.format(
                    response, bug_reports_message()))
            return

        cache_key = self._generate_key(self._generate_key_bindings(spec))
        self.logger.trace('Attempting to access PO Token cache using key: {0}'.format(cache_key))

        default_expires_at = int(calendar.timegm(dt.datetime.utcnow().utctimetuple())) + spec.default_ttl
        cache_response = dataclasses.replace(response, expires_at=response.expires_at or default_expires_at)

        write_policy = write_policy or spec.write_policy
        self.logger.trace('Using write policy: {0}'.format(write_policy))

        for idx, provider in enumerate(self._get_cache_providers(request)):
            try:
                self.logger.trace(
                    'Caching PO Token response in "{0}" cache provider (key={1}, expires_at={2})'.format(
                        provider.PROVIDER_NAME, cache_key, cache_response.expires_at))
                provider.store(
                    key=cache_key,
                    value=json.dumps(dataclasses.asdict(cache_response)),
                    expires_at=cache_response.expires_at)
            except PoTokenCacheProviderError as e:
                self.logger.warning(
                    'Error from "{0}" PO Token cache provider: {1!r}{2}'.format(
                        provider.PROVIDER_NAME, e, provider_bug_report_message(provider) if not e.expected else ""))
            except Exception as e:
                self.logger.error(
                    'Error occurred with "{0}" PO Token cache provider: {1!r}{2}'.format(
                        provider.PROVIDER_NAME, e, provider_bug_report_message(provider)))

            if idx == 0 and write_policy == CacheProviderWritePolicy.WRITE_FIRST:
                return

    def close(self):
        for provider in self.cache_providers.values():
            provider.close()
        for spec_provider in self.cache_spec_providers.values():
            spec_provider.close()


class PoTokenRequestDirector(object):

    def __init__(self, logger, cache):
        self.providers = {}
        self.preferences = []
        self.cache = cache
        self.logger = logger

    def register_provider(self, provider):
        self.providers[provider.PROVIDER_KEY] = provider

    def register_preference(self, preference):
        self.preferences.append(preference)

    def _get_providers(self, request):
        preferences = {
            provider: sum(pref(provider, request) for pref in self.preferences)
            for provider in self.providers.values()
        }
        if self.logger.log_level <= self.logger.LogLevel.TRACE:
            self.logger.trace('PO Token Providers: {0}'.format(provider_display_list(self.providers.values())))
            self.logger.trace('Provider preferences for this request: {}'.format(', '.join(
                '{0}={1}'.format(provider.PROVIDER_NAME, pref) for provider, pref in preferences.items())))

        return (
            provider for provider in sorted(
                self.providers.values(), key=preferences.get, reverse=True)
            if provider.is_available()
        )

    def _get_po_token(self, request):
        for provider in self._get_providers(request):
            try:
                self.logger.trace(
                    'Attempting to fetch a PO Token from "{0}" provider'.format(provider.PROVIDER_NAME))
                response = provider.request_pot(request.copy())
            except PoTokenProviderRejectedRequest as e:
                self.logger.trace(
                    'PO Token Provider "{0}" rejected this request, trying next available provider. Reason: {1}'.format(
                        provider.PROVIDER_NAME, e))
                continue
            except PoTokenProviderError as e:
                self.logger.warning(
                    'Error fetching PO Token from "{0}" provider: {1!r}{2}'.format(
                        provider.PROVIDER_NAME, e, provider_bug_report_message(provider) if not e.expected else ""))
                continue
            except Exception as e:
                self.logger.error(
                    'Unexpected error when fetching PO Token from "{0}" provider: {1!r}{2}'.format(
                        provider.PROVIDER_NAME, e, provider_bug_report_message(provider)))
                continue

            self.logger.trace('PO Token response from "{0}" provider: {1}'.format(provider.PROVIDER_NAME, response))

            if not validate_response(response):
                self.logger.error(
                    'Invalid PO Token response received from "{0}" provider: {1}{2}'.format(
                        provider.PROVIDER_NAME, response, provider_bug_report_message(provider)))
                continue

            return response

        self.logger.trace('No PO Token providers were able to provide a valid PO Token')
        return None

    def get_po_token(self, request):
        if not request.bypass_cache:
            pot_response = self.cache.get(request)
            if pot_response:
                return clean_pot(pot_response.po_token)

        if not self.providers:
            self.logger.trace('No PO Token providers registered')
            return None

        pot_response = self._get_po_token(request)
        if not pot_response:
            return None

        pot_response.po_token = clean_pot(pot_response.po_token)

        if pot_response.expires_at is None or pot_response.expires_at > 0:
            self.cache.store(request, pot_response)
        else:
            self.logger.trace(
                'PO Token response will not be cached (expires_at={0})'.format(pot_response.expires_at))

        return pot_response.po_token

    def close(self):
        for provider in self.providers.values():
            provider.close()
        self.cache.close()


EXTRACTOR_ARG_PREFIX = 'youtubepot'


def initialize_pot_director(ie):
    assert ie._downloader is not None, 'Downloader not set'

    enable_trace = ie._configuration_arg(
        'pot_trace', ['false'], ie_key='youtube', casesense=False)[0] == 'true'

    if enable_trace:
        log_level = IEContentProviderLogger.LogLevel.TRACE
    elif ie.get_param('verbose', False):
        log_level = IEContentProviderLogger.LogLevel.DEBUG
    else:
        log_level = IEContentProviderLogger.LogLevel.INFO

    def get_provider_logger_and_settings(provider, logger_key):
        logger_prefix = '{0}:{1}'.format(logger_key, provider.PROVIDER_NAME)
        extractor_key = '{0}-{1}'.format(EXTRACTOR_ARG_PREFIX, provider.PROVIDER_KEY.lower())
        return (
            YoutubeIEContentProviderLogger(ie, logger_prefix, log_level=log_level),
            ie.get_param('extractor_args', {}).get(extractor_key, {}))

    cache_providers = []
    for cache_provider in _pot_cache_providers.value.values():
        logger, settings = get_provider_logger_and_settings(cache_provider, 'pot:cache')
        cache_providers.append(cache_provider(ie, logger, settings))
    cache_spec_providers = []
    for cache_spec_provider in _pot_pcs_providers.value.values():
        logger, settings = get_provider_logger_and_settings(cache_spec_provider, 'pot:cache:spec')
        cache_spec_providers.append(cache_spec_provider(ie, logger, settings))

    cache = PoTokenCache(
        logger=YoutubeIEContentProviderLogger(ie, 'pot:cache', log_level=log_level),
        cache_providers=cache_providers,
        cache_spec_providers=cache_spec_providers,
        cache_provider_preferences=list(_pot_cache_provider_preferences.value),
    )

    director = PoTokenRequestDirector(
        logger=YoutubeIEContentProviderLogger(ie, 'pot', log_level=log_level),
        cache=cache,
    )

    ie._downloader.add_close_hook(director.close)

    for provider in _pot_providers.value.values():
        logger, settings = get_provider_logger_and_settings(provider, 'pot')
        director.register_provider(provider(ie, logger, settings))

    for preference in _ptp_preferences.value:
        director.register_preference(preference)

    if director.logger.log_level <= director.logger.LogLevel.DEBUG:
        director.logger.debug('PO Token Providers: {0}'.format(provider_display_list(director.providers.values())))
        director.logger.debug('PO Token Cache Providers: {0}'.format(provider_display_list(cache.cache_providers.values())))
        director.logger.debug('PO Token Cache Spec Providers: {0}'.format(provider_display_list(cache.cache_spec_providers.values())))
        director.logger.trace('Registered {0} provider preferences'.format(len(director.preferences)))
        director.logger.trace('Registered {0} cache provider preferences'.format(len(cache.cache_provider_preferences)))

    return director


def provider_display_list(providers):
    def provider_display_name(provider):
        display_str = join_nonempty(
            provider.PROVIDER_NAME,
            provider.PROVIDER_VERSION if not isinstance(provider, BuiltinIEContentProvider) else None)
        statuses = []
        if not isinstance(provider, BuiltinIEContentProvider):
            statuses.append('external')
        if not provider.is_available():
            statuses.append('unavailable')
        if statuses:
            display_str += ' ({0})'.format(", ".join(statuses))
        return display_str

    return ', '.join(provider_display_name(provider) for provider in providers) or 'none'


def clean_pot(po_token):
    try:
        return base64.urlsafe_b64encode(
            base64.urlsafe_b64decode(urllib_parse.unquote(po_token))).decode()
    except (binascii.Error, ValueError):
        raise ValueError('Invalid PO Token')


def validate_response(response):
    if (
        not isinstance(response, PoTokenResponse)
        or not isinstance(response.po_token, str)
        or not response.po_token
    ):
        return False

    try:
        clean_pot(response.po_token)
    except ValueError:
        return False

    if not isinstance(response.expires_at, int):
        return response.expires_at is None

    return response.expires_at <= 0 or response.expires_at > int(calendar.timegm(dt.datetime.utcnow().utctimetuple()))


def validate_cache_spec(spec):
    return (
        isinstance(spec, PoTokenCacheSpec)
        and isinstance(spec.write_policy, CacheProviderWritePolicy)
        and isinstance(spec.default_ttl, int)
        and isinstance(spec.key_bindings, dict)
        and all(isinstance(k, str) for k in spec.key_bindings)
        and all(v is None or isinstance(v, str) for v in spec.key_bindings.values())
        and bool([v for v in spec.key_bindings.values() if v is not None])
    )
