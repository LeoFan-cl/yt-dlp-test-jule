b'--- ./devscripts/zsh-completion.py\t(original)'
b'+++ ./devscripts/zsh-completion.py\t(refactored)'
b'@@ -1,23 +1,26 @@'
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
b"-ZSH_COMPLETION_FILE = 'completions/zsh/_yt-dlp'"
b"-ZSH_COMPLETION_TEMPLATE = 'devscripts/zsh-completion.in'"
b"+ZSH_COMPLETION_FILE = u'completions/zsh/_yt-dlp'"
b"+ZSH_COMPLETION_TEMPLATE = u'devscripts/zsh-completion.in'"
b' '
b' '
b' def build_completion(opt_parser):'
b'     opts = [opt for group in opt_parser.option_groups'
b'             for opt in group.option_list]'
b"-    opts_file = [opt for opt in opts if opt.metavar == 'FILE']"
b"-    opts_dir = [opt for opt in opts if opt.metavar == 'DIR']"
b"+    opts_file = [opt for opt in opts if opt.metavar == u'FILE']"
b"+    opts_dir = [opt for opt in opts if opt.metavar == u'DIR']"
b' '
b'     fileopts = []'
b'     for opt in opts_file:'
b'@@ -38,11 +41,11 @@'
b'     with open(ZSH_COMPLETION_TEMPLATE) as f:'
b'         template = f.read()'
b' '
b"-    template = template.replace('{{fileopts}}', '|'.join(fileopts))"
b"-    template = template.replace('{{diropts}}', '|'.join(diropts))"
b"-    template = template.replace('{{flags}}', ' '.join(flags))"
b"+    template = template.replace(u'{{fileopts}}', u'|'.join(fileopts))"
b"+    template = template.replace(u'{{diropts}}', u'|'.join(diropts))"
b"+    template = template.replace(u'{{flags}}', u' '.join(flags))"
b' '
b"-    with open(ZSH_COMPLETION_FILE, 'w') as f:"
b"+    with open(ZSH_COMPLETION_FILE, u'w') as f:"
b'         f.write(template)'
b' '
b' '
