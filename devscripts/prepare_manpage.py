b'--- ./devscripts/prepare_manpage.py\t(original)'
b'+++ ./devscripts/prepare_manpage.py\t(refactored)'
b'@@ -1,6 +1,7 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' '
b'@@ -18,9 +19,9 @@'
b' )'
b' '
b' ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))'
b"-README_FILE = os.path.join(ROOT_DIR, 'README.md')"
b"+README_FILE = os.path.join(ROOT_DIR, u'README.md')"
b' '
b"-PREFIX = r'''%yt-dlp(1)"
b"+PREFIX = ur'''%yt-dlp(1)"
b' '
b' # NAME'
b' '
b'@@ -36,11 +37,11 @@'
b' '
b' '
b' def filter_excluded_sections(readme):'
b"-    EXCLUDED_SECTION_BEGIN_STRING = re.escape('<!-- MANPAGE: BEGIN EXCLUDED SECTION -->')"
b"-    EXCLUDED_SECTION_END_STRING = re.escape('<!-- MANPAGE: END EXCLUDED SECTION -->')"
b"+    EXCLUDED_SECTION_BEGIN_STRING = re.escape(u'<!-- MANPAGE: BEGIN EXCLUDED SECTION -->')"
b"+    EXCLUDED_SECTION_END_STRING = re.escape(u'<!-- MANPAGE: END EXCLUDED SECTION -->')"
b'     return re.sub('
b"         rf'(?s){EXCLUDED_SECTION_BEGIN_STRING}.+?{EXCLUDED_SECTION_END_STRING}\\n',"
b"-        '', readme)"
b"+        u'', readme)"
b' '
b' '
b' def _convert_code_blocks(readme):'
b'@@ -50,24 +51,24 @@'
b'         if current_code_block:'
b'             if line == current_code_block:'
b'                 current_code_block = None'
b"-                yield '\\n'"
b"+                yield u'\\n'"
b'             else:'
b"                 yield f'    {line}'"
b"-        elif line.startswith('```'):"
b"-            current_code_block = line.count('`') * '`' + '\\n'"
b"-            yield '\\n'"
b"+        elif line.startswith(u'```'):"
b"+            current_code_block = line.count(u'`') * u'`' + u'\\n'"
b"+            yield u'\\n'"
b'         else:'
b'             yield line'
b' '
b' '
b' def convert_code_blocks(readme):'
b"-    return ''.join(_convert_code_blocks(readme))"
b"+    return u''.join(_convert_code_blocks(readme))"
b' '
b' '
b' def move_sections(readme):'
b'-    MOVE_TAG_TEMPLATE = \'<!-- MANPAGE: MOVE "%s" SECTION HERE -->\''
b"-    sections = re.findall(r'(?m)^%s$' % ("
b"-        re.escape(MOVE_TAG_TEMPLATE).replace(r'\\%', '%') % '(.+)'), readme)"
b'+    MOVE_TAG_TEMPLATE = u\'<!-- MANPAGE: MOVE "%s" SECTION HERE -->\''
b"+    sections = re.findall(ur'(?m)^%s$' % ("
b"+        re.escape(MOVE_TAG_TEMPLATE).replace(ur'\\%', u'%') % u'(.+)'), readme)"
b' '
b'     for section_name in sections:'
b'         move_tag = MOVE_TAG_TEMPLATE % section_name'
b'@@ -80,17 +81,17 @@'
b'         elif len(sections) > 1:'
b"             raise Exception(f'There are multiple occurrences of section {section_name}, this is unhandled')"
b' '
b"-        readme = readme.replace(sections[0], '', 1).replace(move_tag, sections[0], 1)"
b"+        readme = readme.replace(sections[0], u'', 1).replace(move_tag, sections[0], 1)"
b'     return readme'
b' '
b' '
b' def filter_options(readme):'
b"-    section = re.search(r'(?sm)^# USAGE AND OPTIONS\\n.+?(?=^# )', readme).group(0)"
b"-    section_new = section.replace('*', R'\\*')"
b"+    section = re.search(ur'(?sm)^# USAGE AND OPTIONS\\n.+?(?=^# )', readme).group(0)"
b"+    section_new = section.replace(u'*', uR'\\*')"
b' '
b"-    options = '# OPTIONS\\n'"
b"-    for line in section_new.split('\\n')[1:]:"
b"-        mobj = re.fullmatch(r'''(?x)"
b"+    options = u'# OPTIONS\\n'"
b"+    for line in section_new.split(u'\\n')[1:]:"
b"+        mobj = re.fullmatch(ur'''(?x)"
b'                 \\s{4}(?P<opt>-(?:,\\s|[^\\s])+)'
b'                 (?:\\s(?P<meta>(?:[^\\s]|\\s(?!\\s))+))?'
b'                 (\\s{2,}(?P<desc>.+))?'
b'@@ -98,11 +99,11 @@'
b'         if not mobj:'
b"             options += f'{line.lstrip()}\\n'"
b'             continue'
b"-        option, metavar, description = mobj.group('opt', 'meta', 'desc')"
b"+        option, metavar, description = mobj.group(u'opt', u'meta', u'desc')"
b' '
b"         # Pandoc's definition_lists. See http://pandoc.org/README.html"
b"         option = f'{option} *{metavar}*' if metavar else option"
b"-        description = f'{description}\\n' if description else ''"
b"+        description = f'{description}\\n' if description else u''"
b"         options += f'\\n{option}\\n:   {description}'"
b'         continue'
b' '
b'@@ -116,5 +117,5 @@'
b'     write_file(get_filename_args(), PREFIX + TRANSFORM(read_file(README_FILE)))'
b' '
b' '
b"-if __name__ == '__main__':"
b"+if __name__ == u'__main__':"
b'     main()'
