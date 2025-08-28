# flake8: noqa: F405
from __future__ import absolute_import
from shutil import *  # noqa: F403

from .compat_utils import passthrough_module

passthrough_module(__name__, 'shutil')
del passthrough_module


import sys

if sys.platform.startswith('freebsd'):
    import errno
    import os
    import shutil

    def copy2(src, dst, *args, **kwargs):
        shutil.copyfile(src, dst, *args, **kwargs)
        try:
            shutil.copystat(src, dst, *args, **kwargs)
        except OSError as e:
            if e.errno != getattr(errno, 'EPERM', None):
                raise
        return dst

    def move(*args, **kwargs):
        if 'copy_function' not in kwargs:
            kwargs['copy_function'] = copy2
        return shutil.move(*args, **kwargs)
