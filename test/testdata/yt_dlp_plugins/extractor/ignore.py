b'--- ./test/testdata/yt_dlp_plugins/extractor/ignore.py\t(original)'
b'+++ ./test/testdata/yt_dlp_plugins/extractor/ignore.py\t(refactored)'
b'@@ -1,3 +1,4 @@'
b'+from __future__ import absolute_import'
b' from yt_dlp.extractor.common import InfoExtractor'
b' '
b' '
b'@@ -6,8 +7,8 @@'
b' '
b' '
b' class InAllPluginIE(InfoExtractor):'
b"-    _VALID_URL = 'inallpluginie'"
b"+    _VALID_URL = u'inallpluginie'"
b'     pass'
b' '
b' '
b"-__all__ = ['InAllPluginIE']"
b"+__all__ = [u'InAllPluginIE']"
