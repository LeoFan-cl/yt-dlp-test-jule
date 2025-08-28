b'--- ./test/testdata/zipped_plugins/yt_dlp_plugins/extractor/zipped.py\t(original)'
b'+++ ./test/testdata/zipped_plugins/yt_dlp_plugins/extractor/zipped.py\t(refactored)'
b'@@ -1,6 +1,7 @@'
b'+from __future__ import absolute_import'
b' from yt_dlp.extractor.common import InfoExtractor'
b' '
b' '
b' class ZippedPluginIE(InfoExtractor):'
b"-    _VALID_URL = 'zippedpluginie'"
b"+    _VALID_URL = u'zippedpluginie'"
b'     pass'
