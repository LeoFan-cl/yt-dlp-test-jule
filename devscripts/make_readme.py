b'--- ./devscripts/make_readme.py\t(original)'
b'+++ ./devscripts/make_readme.py\t(refactored)'
b'@@ -1,13 +1,15 @@'
b' #!/usr/bin/env python3'
b' '
b'-"""'
b'+u"""'
b' yt-dlp --help | make_readme.py'
b' This must be run in a console of correct width'
b' """'
b' '
b' # Allow direct execution'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b'+from itertools import imap'
b' '
b' sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'
b' '
b'@@ -17,17 +19,19 @@'
b' '
b' from devscripts.utils import read_file, write_file'
b' '
b"-README_FILE = 'README.md'"
b"+README_FILE = u'README.md'"
b' '
b"-OPTIONS_START = 'General Options:'"
b"-OPTIONS_END = 'CONFIGURATION'"
b"-EPILOG_START = 'See full documentation'"
b"+OPTIONS_START = u'General Options:'"
b"+OPTIONS_END = u'CONFIGURATION'"
b"+EPILOG_START = u'See full documentation'"
b' ALLOWED_OVERSHOOT = 2'
b' '
b' DISABLE_PATCH = object()'
b' '
b' '
b'-def take_section(text, start=None, end=None, *, shift=0):'
b'+def take_section(text, start=None, end=None, **_3to2kwargs):'
b"+    if 'shift' in _3to2kwargs: shift = _3to2kwargs['shift']; del _3to2kwargs['shift']"
b'+    else: shift = 0'
b'     return text['
b'         text.index(start) + shift if start else None:'
b'         text.index(end) + shift if end else None'
b'@@ -40,54 +44,54 @@'
b' '
b" options = take_section(sys.stdin.read(), f'\\n  {OPTIONS_START}', f'\\n{EPILOG_START}', shift=1)"
b' '
b"-max_width = max(map(len, options.split('\\n')))"
b"-switch_col_width = len(re.search(r'(?m)^\\s{5,}', options).group())"
b"+max_width = max(imap(len, options.split(u'\\n')))"
b"+switch_col_width = len(re.search(ur'(?m)^\\s{5,}', options).group())"
b' delim = f\'\\n{" " * switch_col_width}\''
b' '
b' PATCHES = ('
b'     (   # Standardize `--update` message'
b"-        r'(?m)^(    -U, --update\\s+).+(\\n    \\s.+)*$',"
b"-        r'\\1Update this program to the latest version',"
b"+        ur'(?m)^(    -U, --update\\s+).+(\\n    \\s.+)*$',"
b"+        ur'\\1Update this program to the latest version',"
b'     ),'
b'     (   # Headings'
b"-        r'(?m)^  (\\w.+\\n)(    (?=\\w))?',"
b"-        r'## \\1',"
b"+        ur'(?m)^  (\\w.+\\n)(    (?=\\w))?',"
b"+        ur'## \\1',"
b'     ),'
b'     (   # Fixup `--date` formatting'
b"         rf'(?m)(    --date DATE.+({delim}[^\\[]+)*)\\[.+({delim}.+)*$',"
b"         (rf'\\1[now|today|yesterday][-N[day|week|month|year]].{delim}'"
b'          f\'E.g. "--date today-2weeks" downloads only{delim}\''
b"-         'videos uploaded on the same day two weeks ago'),"
b"+         u'videos uploaded on the same day two weeks ago'),"
b'     ),'
b'     (   # Do not split URLs'
b"         rf'({delim[:-1]})? (?P<label>\\[\\S+\\] )?(?P<url>https?({delim})?:({delim})?/({delim})?/(({delim})?\\S+)+)\\s',"
b"-        lambda mobj: ''.join((delim, mobj.group('label') or '', re.sub(r'\\s+', '', mobj.group('url')), '\\n')),"
b"+        lambda mobj: u''.join((delim, mobj.group(u'label') or u'', re.sub(ur'\\s+', u'', mobj.group(u'url')), u'\\n')),"
b'     ),'
b'     (   # Do not split "words"'
b"         rf'(?m)({delim}\\S+)+$',"
b"-        lambda mobj: ''.join((delim, mobj.group(0).replace(delim, ''))),"
b"+        lambda mobj: u''.join((delim, mobj.group(0).replace(delim, u''))),"
b'     ),'
b'     (   # Allow overshooting last line'
b"         rf'(?m)^(?P<prev>.+)${delim}(?P<current>.+)$(?!{delim})',"
b"-        lambda mobj: (mobj.group().replace(delim, ' ')"
b"+        lambda mobj: (mobj.group().replace(delim, u' ')"
b'                       if len(mobj.group()) - len(delim) + 1 <= max_width + ALLOWED_OVERSHOOT'
b'                       else mobj.group()),'
b'     ),'
b'     (   # Avoid newline when a space is available b/w switch and description'
b'         DISABLE_PATCH,  # This creates issues with prepare_manpage'
b"-        r'(?m)^(\\s{4}-.{%d})(%s)' % (switch_col_width - 6, delim),"
b"-        r'\\1 ',"
b"+        ur'(?m)^(\\s{4}-.{%d})(%s)' % (switch_col_width - 6, delim),"
b"+        ur'\\1 ',"
b'     ),'
b'     (   # Replace brackets with a Markdown link'
b"-        r'SponsorBlock API \\((http.+)\\)',"
b"-        r'[SponsorBlock API](\\1)',"
b"+        ur'SponsorBlock API \\((http.+)\\)',"
b"+        ur'[SponsorBlock API](\\1)',"
b'     ),'
b' )'
b' '
b' readme = read_file(README_FILE)'
b' '
b"-write_file(README_FILE, ''.join(("
b"+write_file(README_FILE, u''.join(("
b"     take_section(readme, end=f'## {OPTIONS_START}'),"
b'-    functools.reduce(apply_patch, PATCHES, options),'
b'+    reduce(apply_patch, PATCHES, options),'
b"     take_section(readme, f'# {OPTIONS_END}'),"
b' )))'
