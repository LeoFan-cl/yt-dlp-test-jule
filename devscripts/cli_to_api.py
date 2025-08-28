b'--- ./devscripts/cli_to_api.py\t(original)'
b'+++ ./devscripts/cli_to_api.py\t(refactored)'
b'@@ -1,6 +1,7 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' '
b'@@ -15,12 +16,12 @@'
b' def parse_patched_options(opts):'
b'     patched_parser = create_parser()'
b'     patched_parser.defaults.update({'
b"-        'ignoreerrors': False,"
b"-        'retries': 0,"
b"-        'fragment_retries': 0,"
b"-        'extract_flat': False,"
b"-        'concat_playlist': 'never',"
b"-        'update_self': False,"
b"+        u'ignoreerrors': False,"
b"+        u'retries': 0,"
b"+        u'fragment_retries': 0,"
b"+        u'extract_flat': False,"
b"+        u'concat_playlist': u'never',"
b"+        u'update_self': False,"
b'     })'
b'     yt_dlp.options.create_parser = lambda: patched_parser'
b'     try:'
b'@@ -35,17 +36,17 @@'
b' def cli_to_api(opts, cli_defaults=False):'
b'     opts = (yt_dlp.parse_options if cli_defaults else parse_patched_options)(opts).ydl_opts'
b' '
b'-    diff = {k: v for k, v in opts.items() if default_opts[k] != v}'
b"-    if 'postprocessors' in diff:"
b"-        diff['postprocessors'] = [pp for pp in diff['postprocessors']"
b"-                                  if pp not in default_opts['postprocessors']]"
b'+    diff = dict((k, v) for k, v in opts.items() if default_opts[k] != v)'
b"+    if u'postprocessors' in diff:"
b"+        diff[u'postprocessors'] = [pp for pp in diff[u'postprocessors']"
b"+                                  if pp not in default_opts[u'postprocessors']]"
b'     return diff'
b' '
b' '
b"-if __name__ == '__main__':"
b"+if __name__ == u'__main__':"
b'     from pprint import pprint'
b' '
b"-    print('\\nThe arguments passed translate to:\\n')"
b"+    print u'\\nThe arguments passed translate to:\\n'"
b'     pprint(cli_to_api(sys.argv[1:]))'
b"-    print('\\nCombining these with the CLI defaults gives:\\n')"
b"+    print u'\\nCombining these with the CLI defaults gives:\\n'"
b'     pprint(cli_to_api(sys.argv[1:], True))'
