b'--- ./devscripts/set-variant.py\t(original)'
b'+++ ./devscripts/set-variant.py\t(refactored)'
b'@@ -1,6 +1,7 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' '
b'@@ -13,13 +14,13 @@'
b' '
b' from devscripts.utils import compose_functions, read_file, write_file'
b' '
b"-VERSION_FILE = 'yt_dlp/version.py'"
b"+VERSION_FILE = u'yt_dlp/version.py'"
b' '
b' '
b' def parse_options():'
b"-    parser = argparse.ArgumentParser(description='Set the build variant of the package')"
b"-    parser.add_argument('variant', help='Name of the variant')"
b"-    parser.add_argument('-M', '--update-message', default=None, help='Message to show in -U')"
b"+    parser = argparse.ArgumentParser(description=u'Set the build variant of the package')"
b"+    parser.add_argument(u'variant', help=u'Name of the variant')"
b"+    parser.add_argument(u'-M', u'--update-message', default=None, help=u'Message to show in -U')"
b'     return parser.parse_args()'
b' '
b' '
b'@@ -29,8 +30,8 @@'
b' '
b' opts = parse_options()'
b' transform = compose_functions('
b"-    property_setter('VARIANT', opts.variant),"
b"-    property_setter('UPDATE_HINT', opts.update_message),"
b"+    property_setter(u'VARIANT', opts.variant),"
b"+    property_setter(u'UPDATE_HINT', opts.update_message),"
b' )'
b' '
b' write_file(VERSION_FILE, transform(read_file(VERSION_FILE)))'
