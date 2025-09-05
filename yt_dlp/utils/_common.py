# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import collections

class NO_DEFAULT(object):
    pass

def is_iterable_like(x, allowed_types=collections.Iterable, blocked_types=NO_DEFAULT):
    if blocked_types is NO_DEFAULT:
        blocked_types = (str, bytes, collections.Mapping)
    return isinstance(x, allowed_types) and not isinstance(x, blocked_types)

def try_call(*funcs, **kwargs):
    expected_type = kwargs.get('expected_type')
    args = kwargs.get('args', [])
    kwargs = kwargs.get('kwargs', {})
    for f in funcs:
        try:
            val = f(*args, **kwargs)
        except (AttributeError, KeyError, TypeError, IndexError, ValueError, ZeroDivisionError):
            pass
        else:
            if expected_type is None or isinstance(val, expected_type):
                return val
