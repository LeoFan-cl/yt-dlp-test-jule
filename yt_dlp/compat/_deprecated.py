#"""Deprecated - New code should avoid these"""
from __future__ import absolute_import
import warnings

from .compat_utils import passthrough_module

# XXX: Implement this the same way as other DeprecationWarnings without circular import
passthrough_module(__name__, '.._legacy', callback=lambda attr: warnings.warn(
    DeprecationWarning('{0}.{1} is deprecated'.format(__name__, attr)), stacklevel=6))
del passthrough_module
