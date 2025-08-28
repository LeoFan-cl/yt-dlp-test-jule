b'--- ./devscripts/fish-completion.py\t(original)'
b'+++ ./devscripts/fish-completion.py\t(refactored)'
b'@@ -1,8 +1,11 @@'
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
b'@@ -12,18 +15,18 @@'
b' import yt_dlp'
b' from yt_dlp.utils import shell_quote'
b' '
b"-FISH_COMPLETION_FILE = 'completions/fish/yt-dlp.fish'"
b"-FISH_COMPLETION_TEMPLATE = 'devscripts/fish-completion.in'"
b"+FISH_COMPLETION_FILE = u'completions/fish/yt-dlp.fish'"
b"+FISH_COMPLETION_TEMPLATE = u'devscripts/fish-completion.in'"
b' '
b' EXTRA_ARGS = {'
b"-    'remux-video': ['--arguments', 'mp4 mkv', '--exclusive'],"
b"-    'recode-video': ['--arguments', 'mp4 flv ogg webm mkv', '--exclusive'],"
b"+    u'remux-video': [u'--arguments', u'mp4 mkv', u'--exclusive'],"
b"+    u'recode-video': [u'--arguments', u'mp4 flv ogg webm mkv', u'--exclusive'],"
b' '
b'     # Options that need a file parameter'
b"-    'download-archive': ['--require-parameter'],"
b"-    'cookies': ['--require-parameter'],"
b"-    'load-info': ['--require-parameter'],"
b"-    'batch-file': ['--require-parameter'],"
b"+    u'download-archive': [u'--require-parameter'],"
b"+    u'cookies': [u'--require-parameter'],"
b"+    u'load-info': [u'--require-parameter'],"
b"+    u'batch-file': [u'--require-parameter'],"
b' }'
b' '
b' '
b'@@ -32,19 +35,19 @@'
b' '
b'     for group in opt_parser.option_groups:'
b'         for option in group.option_list:'
b"-            long_option = option.get_opt_string().strip('-')"
b"-            complete_cmd = ['complete', '--command', 'yt-dlp', '--long-option', long_option]"
b"+            long_option = option.get_opt_string().strip(u'-')"
b"+            complete_cmd = [u'complete', u'--command', u'yt-dlp', u'--long-option', long_option]"
b'             if option._short_opts:'
b"-                complete_cmd += ['--short-option', option._short_opts[0].strip('-')]"
b"+                complete_cmd += [u'--short-option', option._short_opts[0].strip(u'-')]"
b'             if option.help != optparse.SUPPRESS_HELP:'
b"-                complete_cmd += ['--description', option.help]"
b"+                complete_cmd += [u'--description', option.help]"
b'             complete_cmd.extend(EXTRA_ARGS.get(long_option, []))'
b'             commands.append(shell_quote(complete_cmd))'
b' '
b'     with open(FISH_COMPLETION_TEMPLATE) as f:'
b'         template = f.read()'
b"-    filled_template = template.replace('{{commands}}', '\\n'.join(commands))"
b"-    with open(FISH_COMPLETION_FILE, 'w') as f:"
b"+    filled_template = template.replace(u'{{commands}}', u'\\n'.join(commands))"
b"+    with open(FISH_COMPLETION_FILE, u'w') as f:"
b'         f.write(filled_template)'
b' '
b' '
