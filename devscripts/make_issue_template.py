b'--- ./devscripts/make_issue_template.py\t(original)'
b'+++ ./devscripts/make_issue_template.py\t(refactored)'
b'@@ -1,6 +1,7 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' '
b'@@ -11,7 +12,7 @@'
b' '
b' from devscripts.utils import get_filename_args, read_file, write_file'
b' '
b"-VERBOSE = '''"
b"+VERBOSE = u'''"
b'   - type: checkboxes'
b'     id: verbose'
b'     attributes:'
b'@@ -51,7 +52,7 @@'
b'       required: true'
b" '''.strip()"
b' '
b"-NO_SKIP = '''"
b"+NO_SKIP = u'''"
b'   - type: markdown'
b'     attributes:'
b'       value: |'
b'@@ -62,14 +63,14 @@'
b' '
b' def main():'
b'     fields = {'
b"-        'no_skip': NO_SKIP,"
b"-        'verbose': VERBOSE,"
b"-        'verbose_optional': re.sub(r'(\\n\\s+validations:)?\\n\\s+required: true', '', VERBOSE),"
b"+        u'no_skip': NO_SKIP,"
b"+        u'verbose': VERBOSE,"
b"+        u'verbose_optional': re.sub(ur'(\\n\\s+validations:)?\\n\\s+required: true', u'', VERBOSE),"
b'     }'
b' '
b'     infile, outfile = get_filename_args(has_infile=True)'
b'     write_file(outfile, read_file(infile) % fields)'
b' '
b' '
b"-if __name__ == '__main__':"
b"+if __name__ == u'__main__':"
b'     main()'
