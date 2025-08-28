# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import abc
import functools

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import NO_DEFAULT, bug_reports_message, classproperty, traverse_obj
from yt_dlp.version import __version__

# xxx: these could be generalized outside YoutubeIE eventually


class IEContentProviderLogger(object):
    __metaclass__ = abc.ABCMeta

    class LogLevel(object):
        TRACE = 0
        DEBUG = 10
        INFO = 20
        WARNING = 30
        ERROR = 40

        @classmethod
        def _missing_(cls, value):
            if isinstance(value, str):
                value = value.upper()
                if hasattr(cls, value):
                    return getattr(cls, value)
            return cls.INFO

    log_level = LogLevel.INFO

    @abc.abstractmethod
    def trace(self, message):
        pass

    @abc.abstractmethod
    def debug(self, message):
        pass

    @abc.abstractmethod
    def info(self, message):
        pass

    @abc.abstractmethod
    def warning(self, message, **kwargs):
        pass

    @abc.abstractmethod
    def error(self, message):
        pass


class IEContentProviderError(Exception):
    def __init__(self, msg=None, expected=False):
        super(IEContentProviderError, self).__init__(msg)
        self.expected = expected


class IEContentProvider(object):
    __metaclass__ = abc.ABCMeta
    PROVIDER_VERSION = '0.0.0'
    BUG_REPORT_LOCATION = '(developer has not provided a bug report location)'

    def __init__(
        self,
        ie,
        logger,
        settings, *_, **__,
    ):
        self.ie = ie
        self.settings = settings or {}
        self.logger = logger
        super(IEContentProvider, self).__init__()

    @classproperty
    def PROVIDER_NAME(cls):
        return cls.__name__[:-len(cls._PROVIDER_KEY_SUFFIX)]

    @classproperty
    def BUG_REPORT_MESSAGE(cls):
        return 'please report this issue to the provider developer at  {0}  .'.format(cls.BUG_REPORT_LOCATION)

    @classproperty
    def PROVIDER_KEY(cls):
        assert hasattr(cls, '_PROVIDER_KEY_SUFFIX'), 'Content Provider implementation must define a suffix for the provider key'
        assert cls.__name__.endswith(cls._PROVIDER_KEY_SUFFIX), 'PoTokenProvider class names must end with "{0}"'.format(cls._PROVIDER_KEY_SUFFIX)
        return cls.__name__[:-len(cls._PROVIDER_KEY_SUFFIX)]

    @abc.abstractmethod
    def is_available(self):
        raise NotImplementedError

    def close(self):
        pass

    def _configuration_arg(self, key, default=NO_DEFAULT, **kwargs):
        casesense = kwargs.get('casesense', False)
        val = traverse_obj(self.settings, key)
        if val is None:
            return [] if default is NO_DEFAULT else default
        return list(val) if casesense else [x.lower() for x in val]


class BuiltinIEContentProvider(IEContentProvider):
    __metaclass__ = abc.ABCMeta
    PROVIDER_VERSION = __version__
    BUG_REPORT_MESSAGE = bug_reports_message(before='')


def register_provider_generic(
    provider,
    base_class,
    registry,
):
    assert issubclass(provider, base_class), '{0} must be a subclass of {1}'.format(provider, base_class.__name__)
    assert provider.PROVIDER_KEY not in registry, '{0} {1} already registered'.format(base_class.__name__, provider.PROVIDER_KEY)
    registry[provider.PROVIDER_KEY] = provider
    return provider


def register_preference_generic(
    base_class,
    registry,
    *providers,
):
    assert all(issubclass(provider, base_class) for provider in providers)

    def outer(preference):
        @functools.wraps(preference)
        def inner(provider, *args, **kwargs):
            if not providers or isinstance(provider, providers):
                return preference(provider, *args, **kwargs)
            return 0
        registry.add(inner)
        return preference
    return outer
