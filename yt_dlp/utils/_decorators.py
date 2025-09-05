# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import functools
import inspect
import sys

def _functools_cache(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper


def _getargspec(func):
    if sys.version_info >= (3, 0):
        return inspect.getfullargspec(func)
    return inspect.getargspec(func)


def partial_application(func):
    argspec = _getargspec(func)
    required_args = argspec.args[:-len(argspec.defaults or [])]

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if set(required_args[len(args):]).difference(kwargs.keys()):
            return functools.partial(func, *args, **kwargs)
        return func(*args, **kwargs)
    return wrapped


class classproperty(object):
    def __init__(self, func, cache=False):
        functools.update_wrapper(self, func)
        self.func = func
        self._cache = {} if cache else None

    def __get__(self, _, cls):
        if self._cache is None:
            return self.func(cls)
        elif cls not in self._cache:
            self._cache[cls] = self.func(cls)
        return self._cache[cls]


def cached_method(f):
    argspec = _getargspec(f)

    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        key = inspect.getcallargs(f, self, *args, **kwargs)
        key = tuple(key.values())[1:]
        cache = vars(self).setdefault('_cached_method__cache', {}).setdefault(f.__name__, {})
        if key not in cache:
            cache[key] = f(self, *args, **kwargs)
        return cache[key]
    return wrapper


class function_with_repr(object):
    def __init__(self, func, repr_=None):
        functools.update_wrapper(self, func)
        self.func, self.__repr = func, repr_

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    @classmethod
    def set_repr(cls, repr_):
        return functools.partial(cls, repr_=repr_)

    def __repr__(self):
        if self.__repr:
            return self.__repr
        return '{0}.{1}'.format(self.func.__module__, self.func.__name__)
