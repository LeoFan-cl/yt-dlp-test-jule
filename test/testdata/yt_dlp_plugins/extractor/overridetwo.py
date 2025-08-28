b'--- ./test/testdata/yt_dlp_plugins/extractor/overridetwo.py\t(original)'
b'+++ ./test/testdata/yt_dlp_plugins/extractor/overridetwo.py\t(refactored)'
b'@@ -1,5 +1,6 @@'
b'+from __future__ import absolute_import'
b' from yt_dlp.extractor.generic import GenericIE'
b' '
b' '
b"-class _UnderscoreOverrideGenericIE(GenericIE, plugin_name='underscore-override'):"
b"-    SECONDARY_TEST_FIELD = 'underscore-override'"
b"+class _UnderscoreOverrideGenericIE(GenericIE, plugin_name=u'underscore-override'):"
b"+    SECONDARY_TEST_FIELD = u'underscore-override'"
