b'--- ./test/testdata/yt_dlp_plugins/extractor/normal.py\t(original)'
b'+++ ./test/testdata/yt_dlp_plugins/extractor/normal.py\t(refactored)'
b'@@ -1,11 +1,12 @@'
b'+from __future__ import absolute_import'
b' from yt_dlp.extractor.common import InfoExtractor'
b' '
b' '
b' class NormalPluginIE(InfoExtractor):'
b"-    _VALID_URL = 'normalpluginie'"
b"+    _VALID_URL = u'normalpluginie'"
b'     REPLACED = False'
b' '
b' '
b' class _IgnoreUnderscorePluginIE(InfoExtractor):'
b"-    _VALID_URL = 'ignoreunderscorepluginie'"
b"+    _VALID_URL = u'ignoreunderscorepluginie'"
b'     pass'
