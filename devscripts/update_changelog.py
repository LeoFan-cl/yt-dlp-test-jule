b'--- ./devscripts/update_changelog.py\t(original)'
b'+++ ./devscripts/update_changelog.py\t(refactored)'
b'@@ -1,6 +1,8 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import division'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' '
b'@@ -13,14 +15,14 @@'
b' '
b' # Always run after devscripts/update-version.py, and run before `make doc|pypi-files|tar|all`'
b' '
b"-if __name__ == '__main__':"
b"+if __name__ == u'__main__':"
b'     parser = create_parser()'
b"-    parser.description = 'Update an existing changelog file with an entry for a new release'"
b"+    parser.description = u'Update an existing changelog file with an entry for a new release'"
b'     parser.add_argument('
b"-        '--changelog-path', type=Path, default=Path(__file__).parent.parent / 'Changelog.md',"
b"-        help='path to the Changelog file')"
b"+        u'--changelog-path', type=Path, default=Path(__file__).parent.parent / u'Changelog.md',"
b"+        help=u'path to the Changelog file')"
b'     args = parser.parse_args()'
b'     new_entry = create_changelog(args)'
b' '
b"-    header, sep, changelog = read_file(args.changelog_path).partition('\\n### ')"
b"+    header, sep, changelog = read_file(args.changelog_path).partition(u'\\n### ')"
b"     write_file(args.changelog_path, f'{header}{sep}{read_version()}\\n{new_entry}\\n{sep}{changelog}')"
