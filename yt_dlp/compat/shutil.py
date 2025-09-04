# flake8: noqa: F405
from __future__ import absolute_import
from shutil import *  # noqa: F403

from .compat_utils import passthrough_module

passthrough_module(__name__, u'shutil')
del passthrough_module


import sys

if sys.platform.startswith(u'freebsd'):
    import errno
    import os
    import shutil

    def copy2(src, dst, *args, **kwargs):
        shutil.copyfile(src, dst, *args, **kwargs)
        try:
            shutil.copystat(src, dst, *args, **kwargs)
        except OSError, e:
            if e.errno != getattr(errno, u'EPERM', None):
                raise
        return dst

    def move(*args, **kwargs):
        if u'copy_function' not in kwargs:
            kwargs[u'copy_function'] = copy2
        return shutil.move(*args, **kwargs)
