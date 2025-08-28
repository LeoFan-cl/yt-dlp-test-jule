b'--- ./yt_dlp/compat/types.py\t(original)'
b'+++ ./yt_dlp/compat/types.py\t(refactored)'
b'@@ -1,9 +1,10 @@'
b' # flake8: noqa: F405'
b'+from __future__ import absolute_import'
b' from types import *  # noqa: F403'
b' '
b' from .compat_utils import passthrough_module'
b' '
b"-passthrough_module(__name__, 'types')"
b"+passthrough_module(__name__, u'types')"
b' del passthrough_module'
b' '
b' try:'
