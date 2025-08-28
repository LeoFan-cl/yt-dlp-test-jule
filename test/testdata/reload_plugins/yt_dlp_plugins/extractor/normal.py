b'--- ./test/testdata/reload_plugins/yt_dlp_plugins/extractor/normal.py\t(original)'
b'+++ ./test/testdata/reload_plugins/yt_dlp_plugins/extractor/normal.py\t(refactored)'
b'@@ -1,8 +1,9 @@'
b'+from __future__ import absolute_import'
b' from yt_dlp.extractor.common import InfoExtractor'
b' '
b' '
b' class NormalPluginIE(InfoExtractor):'
b"-    _VALID_URL = 'normal'"
b"+    _VALID_URL = u'normal'"
b'     REPLACED = True'
b' '
b' '
