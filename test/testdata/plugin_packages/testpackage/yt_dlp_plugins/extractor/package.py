b'--- ./test/testdata/plugin_packages/testpackage/yt_dlp_plugins/extractor/package.py\t(original)'
b'+++ ./test/testdata/plugin_packages/testpackage/yt_dlp_plugins/extractor/package.py\t(refactored)'
b'@@ -1,6 +1,7 @@'
b'+from __future__ import absolute_import'
b' from yt_dlp.extractor.common import InfoExtractor'
b' '
b' '
b' class PackagePluginIE(InfoExtractor):'
b"-    _VALID_URL = 'package'"
b"+    _VALID_URL = u'package'"
b'     pass'
