b'--- ./devscripts/bash-completion.py\t(original)'
b'+++ ./devscripts/bash-completion.py\t(refactored)'
b'@@ -1,16 +1,19 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import with_statement'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b'+from io import open'
b' '
b' sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'
b' '
b' '
b' import yt_dlp'
b' '
b"-BASH_COMPLETION_FILE = 'completions/bash/yt-dlp'"
b"-BASH_COMPLETION_TEMPLATE = 'devscripts/bash-completion.in'"
b"+BASH_COMPLETION_FILE = u'completions/bash/yt-dlp'"
b"+BASH_COMPLETION_TEMPLATE = u'devscripts/bash-completion.in'"
b' '
b' '
b' def build_completion(opt_parser):'
b'@@ -21,9 +24,9 @@'
b'             opts_flag.append(option.get_opt_string())'
b'     with open(BASH_COMPLETION_TEMPLATE) as f:'
b'         template = f.read()'
b"-    with open(BASH_COMPLETION_FILE, 'w') as f:"
b"+    with open(BASH_COMPLETION_FILE, u'w') as f:"
b'         # just using the special char'
b"-        filled_template = template.replace('{{flags}}', ' '.join(opts_flag))"
b"+        filled_template = template.replace(u'{{flags}}', u' '.join(opts_flag))"
b'         f.write(filled_template)'
b' '
b' '
