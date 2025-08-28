b'--- ./yt_dlp/utils/__init__.py\t(original)'
b'+++ ./yt_dlp/utils/__init__.py\t(refactored)'
b'@@ -1,7 +1,8 @@'
b' # flake8: noqa: F403'
b'+from __future__ import absolute_import'
b' from ..compat.compat_utils import passthrough_module'
b' '
b"-passthrough_module(__name__, '._deprecated')"
b"+passthrough_module(__name__, u'._deprecated')"
b' del passthrough_module'
b' '
b' # isort: off'
