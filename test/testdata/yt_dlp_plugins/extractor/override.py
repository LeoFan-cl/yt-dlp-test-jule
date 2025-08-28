b'--- ./test/testdata/yt_dlp_plugins/extractor/override.py\t(original)'
b'+++ ./test/testdata/yt_dlp_plugins/extractor/override.py\t(refactored)'
b'@@ -1,5 +1,6 @@'
b'+from __future__ import absolute_import'
b' from yt_dlp.extractor.generic import GenericIE'
b' '
b' '
b"-class OverrideGenericIE(GenericIE, plugin_name='override'):"
b"-    TEST_FIELD = 'override'"
b"+class OverrideGenericIE(GenericIE, plugin_name=u'override'):"
b"+    TEST_FIELD = u'override'"
