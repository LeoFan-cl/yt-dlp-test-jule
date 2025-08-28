b'--- ./devscripts/make_supportedsites.py\t(original)'
b'+++ ./devscripts/make_supportedsites.py\t(refactored)'
b'@@ -1,6 +1,7 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' '
b'@@ -10,7 +11,7 @@'
b' from devscripts.utils import get_filename_args, write_file'
b' from yt_dlp.extractor import list_extractor_classes'
b' '
b"-TEMPLATE = '''\\"
b"+TEMPLATE = u'''\\"
b' # Supported sites'
b' '
b' Below is a list of all extractors that are currently included with yt-dlp.'
b'@@ -23,9 +24,9 @@'
b' '
b' '
b' def main():'
b"-    out = '\\n'.join(ie.description() for ie in list_extractor_classes() if ie.IE_DESC is not False)"
b"+    out = u'\\n'.join(ie.description() for ie in list_extractor_classes() if ie.IE_DESC is not False)"
b'     write_file(get_filename_args(), TEMPLATE.format(ie_list=out))'
b' '
b' '
b"-if __name__ == '__main__':"
b"+if __name__ == u'__main__':"
b'     main()'
