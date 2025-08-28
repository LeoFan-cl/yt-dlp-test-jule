b'--- ./bundle/pyinstaller.py\t(original)'
b'+++ ./bundle/pyinstaller.py\t(refactored)'
b'@@ -1,8 +1,11 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b'+from itertools import ifilter'
b'+from itertools import imap'
b' '
b' sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'
b' '
b'@@ -13,39 +16,39 @@'
b' from devscripts.utils import read_version'
b' '
b' OS_NAME, MACHINE, ARCH = sys.platform, platform.machine().lower(), platform.architecture()[0][:2]'
b"-if MACHINE in ('x86', 'x86_64', 'amd64', 'i386', 'i686'):"
b"-    MACHINE = 'x86' if ARCH == '32' else ''"
b"+if MACHINE in (u'x86', u'x86_64', u'amd64', u'i386', u'i686'):"
b"+    MACHINE = u'x86' if ARCH == u'32' else u''"
b' '
b' '
b' def main():'
b'     opts, version = parse_options(), read_version()'
b' '
b"-    onedir = '--onedir' in opts or '-D' in opts"
b"-    if not onedir and '-F' not in opts and '--onefile' not in opts:"
b"-        opts.append('--onefile')"
b"+    onedir = u'--onedir' in opts or u'-D' in opts"
b"+    if not onedir and u'-F' not in opts and u'--onefile' not in opts:"
b"+        opts.append(u'--onefile')"
b' '
b'     name, final_file = exe(onedir)'
b"-    print(f'Building yt-dlp v{version} for {OS_NAME} {platform.machine()} with options {opts}')"
b'-    print(\'Remember to update the version using  "devscripts/update-version.py"\')'
b"-    if not os.path.isfile('yt_dlp/extractor/lazy_extractors.py'):"
b"-        print('WARNING: Building without lazy_extractors. Run  '"
b'-              \'"devscripts/make_lazy_extractors.py"  to build lazy extractors\', file=sys.stderr)'
b"-    print(f'Destination: {final_file}\\n')"
b"+    print f'Building yt-dlp v{version} for {OS_NAME} {platform.machine()} with options {opts}'"
b'+    print u\'Remember to update the version using  "devscripts/update-version.py"\''
b"+    if not os.path.isfile(u'yt_dlp/extractor/lazy_extractors.py'):"
b"+        print >>sys.stderr, u'WARNING: Building without lazy_extractors. Run  '"
b'+              u\'"devscripts/make_lazy_extractors.py"  to build lazy extractors\''
b"+    print f'Destination: {final_file}\\n'"
b' '
b'     opts = ['
b"         f'--name={name}',"
b"-        '--icon=devscripts/logo.ico',"
b"-        '--upx-exclude=vcruntime140.dll',"
b"+        u'--icon=devscripts/logo.ico',"
b"+        u'--upx-exclude=vcruntime140.dll',"
b'         # Ref: https://github.com/yt-dlp/yt-dlp/issues/13311'
b'         #      https://github.com/pyinstaller/pyinstaller/issues/9149'
b"-        '--exclude-module=pkg_resources',"
b"-        '--noconfirm',"
b"-        '--additional-hooks-dir=yt_dlp/__pyinstaller',"
b"+        u'--exclude-module=pkg_resources',"
b"+        u'--noconfirm',"
b"+        u'--additional-hooks-dir=yt_dlp/__pyinstaller',"
b'         *opts,'
b"-        'yt_dlp/__main__.py',"
b"+        u'yt_dlp/__main__.py',"
b'     ]'
b' '
b"-    print(f'Running PyInstaller with {opts}')"
b"+    print f'Running PyInstaller with {opts}'"
b'     run_pyinstaller(opts)'
b'     set_version_info(final_file, version)'
b' '
b'@@ -53,7 +56,7 @@'
b' def parse_options():'
b'     # Compatibility with older arguments'
b'     opts = sys.argv[1:]'
b"-    if opts[0:1] in (['32'], ['64']):"
b"+    if opts[0:1] in ([u'32'], [u'64']):"
b'         if ARCH != opts[0]:'
b"             raise Exception(f'{opts[0]}bit executable cannot be built on a {ARCH}bit system')"
b'         opts = opts[1:]'
b'@@ -61,20 +64,20 @@'
b' '
b' '
b' def exe(onedir):'
b'-    """@returns (name, path)"""'
b'+    u"""@returns (name, path)"""'
b'     platform_name, machine, extension = {'
b"-        'win32': (None, MACHINE, '.exe'),"
b"-        'darwin': ('macos', None, None),"
b"+        u'win32': (None, MACHINE, u'.exe'),"
b"+        u'darwin': (u'macos', None, None),"
b'     }.get(OS_NAME, (OS_NAME, MACHINE, None))'
b' '
b"-    name = '_'.join(filter(None, ("
b"-        'yt-dlp',"
b"+    name = u'_'.join(ifilter(None, ("
b"+        u'yt-dlp',"
b'         platform_name,'
b'         machine,'
b'     )))'
b' '
b"-    return name, ''.join(filter(None, ("
b"-        'dist/',"
b"+    return name, u''.join(ifilter(None, ("
b"+        u'dist/',"
b"         onedir and f'{name}/',"
b'         name,'
b'         extension,'
b'@@ -82,12 +85,12 @@'
b' '
b' '
b' def version_to_list(version):'
b"-    version_list = version.split('.')"
b'-    return list(map(int, version_list)) + [0] * (4 - len(version_list))'
b"+    version_list = version.split(u'.')"
b'+    return list(imap(int, version_list)) + [0] * (4 - len(version_list))'
b' '
b' '
b' def set_version_info(exe, version):'
b"-    if OS_NAME == 'win32':"
b"+    if OS_NAME == u'win32':"
b'         windows_set_version(exe, version)'
b' '
b' '
b'@@ -121,21 +124,21 @@'
b'             date=(0, 0),'
b'         ),'
b'         kids=['
b"-            StringFileInfo([StringTable('040904B0', ["
b"-                StringStruct('Comments', f'yt-dlp{suffix} Command Line Interface'),"
b"-                StringStruct('CompanyName', 'https://github.com/yt-dlp'),"
b"-                StringStruct('FileDescription', 'yt-dlp%s' % (MACHINE and f' ({MACHINE})')),"
b"-                StringStruct('FileVersion', version),"
b"-                StringStruct('InternalName', f'yt-dlp{suffix}'),"
b"-                StringStruct('LegalCopyright', 'pukkandan.ytdlp@gmail.com | UNLICENSE'),"
b"-                StringStruct('OriginalFilename', f'yt-dlp{suffix}.exe'),"
b"-                StringStruct('ProductName', f'yt-dlp{suffix}'),"
b"+            StringFileInfo([StringTable(u'040904B0', ["
b"+                StringStruct(u'Comments', f'yt-dlp{suffix} Command Line Interface'),"
b"+                StringStruct(u'CompanyName', u'https://github.com/yt-dlp'),"
b"+                StringStruct(u'FileDescription', u'yt-dlp%s' % (MACHINE and f' ({MACHINE})')),"
b"+                StringStruct(u'FileVersion', version),"
b"+                StringStruct(u'InternalName', f'yt-dlp{suffix}'),"
b"+                StringStruct(u'LegalCopyright', u'pukkandan.ytdlp@gmail.com | UNLICENSE'),"
b"+                StringStruct(u'OriginalFilename', f'yt-dlp{suffix}.exe'),"
b"+                StringStruct(u'ProductName', f'yt-dlp{suffix}'),"
b'                 StringStruct('
b"-                    'ProductVersion', f'{version}{suffix} on Python {platform.python_version()}'),"
b"-            ])]), VarFileInfo([VarStruct('Translation', [0, 1200])]),"
b"+                    u'ProductVersion', f'{version}{suffix} on Python {platform.python_version()}'),"
b"+            ])]), VarFileInfo([VarStruct(u'Translation', [0, 1200])]),"
b'         ],'
b'     ))'
b' '
b' '
b"-if __name__ == '__main__':"
b"+if __name__ == u'__main__':"
b'     main()'
