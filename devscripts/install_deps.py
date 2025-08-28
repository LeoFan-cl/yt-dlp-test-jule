b'--- ./devscripts/install_deps.py\t(original)'
b'+++ ./devscripts/install_deps.py\t(refactored)'
b'@@ -1,8 +1,12 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow execution from anywhere'
b'+from __future__ import division'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b'+from itertools import imap'
b'+from itertools import ifilter'
b' '
b' sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'
b' '
b'@@ -17,65 +21,65 @@'
b' '
b' '
b' def parse_args():'
b"-    parser = argparse.ArgumentParser(description='Install dependencies for yt-dlp')"
b"+    parser = argparse.ArgumentParser(description=u'Install dependencies for yt-dlp')"
b'     parser.add_argument('
b"-        'input', nargs='?', metavar='TOMLFILE', default=Path(__file__).parent.parent / 'pyproject.toml',"
b"-        help='input file (default: %(default)s)')"
b"+        u'input', nargs=u'?', metavar=u'TOMLFILE', default=Path(__file__).parent.parent / u'pyproject.toml',"
b"+        help=u'input file (default: %(default)s)')"
b'     parser.add_argument('
b"-        '-e', '--exclude', metavar='DEPENDENCY', action='append',"
b"-        help='exclude a dependency')"
b"+        u'-e', u'--exclude', metavar=u'DEPENDENCY', action=u'append',"
b"+        help=u'exclude a dependency')"
b'     parser.add_argument('
b"-        '-i', '--include', metavar='GROUP', action='append',"
b"-        help='include an optional dependency group')"
b"+        u'-i', u'--include', metavar=u'GROUP', action=u'append',"
b"+        help=u'include an optional dependency group')"
b'     parser.add_argument('
b"-        '-o', '--only-optional', action='store_true',"
b"-        help='only install optional dependencies')"
b"+        u'-o', u'--only-optional', action=u'store_true',"
b"+        help=u'only install optional dependencies')"
b'     parser.add_argument('
b"-        '-p', '--print', action='store_true',"
b"-        help='only print requirements to stdout')"
b"+        u'-p', u'--print', action=u'store_true',"
b"+        help=u'only print requirements to stdout')"
b'     parser.add_argument('
b"-        '-u', '--user', action='store_true',"
b"-        help='install with pip as --user')"
b"+        u'-u', u'--user', action=u'store_true',"
b"+        help=u'install with pip as --user')"
b'     return parser.parse_args()'
b' '
b' '
b' def main():'
b'     args = parse_args()'
b"-    project_table = parse_toml(read_file(args.input))['project']"
b"+    project_table = parse_toml(read_file(args.input))[u'project']"
b'     recursive_pattern = re.compile(rf\'{project_table["name"]}\\[(?P<group_name>[\\w-]+)\\]\')'
b"-    optional_groups = project_table['optional-dependencies']"
b"+    optional_groups = project_table[u'optional-dependencies']"
b'     excludes = args.exclude or []'
b' '
b'     def yield_deps(group):'
b'         for dep in group:'
b'             if mobj := recursive_pattern.fullmatch(dep):'
b"-                yield from optional_groups.get(mobj.group('group_name'), [])"
b"+                yield from optional_groups.get(mobj.group(u'group_name'), [])"
b'             else:'
b'                 yield dep'
b' '
b'     targets = []'
b"     if not args.only_optional:  # `-o` should exclude 'dependencies' and the 'default' group"
b"-        targets.extend(project_table['dependencies'])"
b"-        if 'default' not in excludes:  # `--exclude default` should exclude entire 'default' group"
b"-            targets.extend(yield_deps(optional_groups['default']))"
b"+        targets.extend(project_table[u'dependencies'])"
b"+        if u'default' not in excludes:  # `--exclude default` should exclude entire 'default' group"
b"+            targets.extend(yield_deps(optional_groups[u'default']))"
b' '
b'-    for include in filter(None, map(optional_groups.get, args.include or [])):'
b'+    for include in ifilter(None, imap(optional_groups.get, args.include or [])):'
b'         targets.extend(yield_deps(include))'
b' '
b"-    targets = [t for t in targets if re.match(r'[\\w-]+', t).group(0).lower() not in excludes]"
b"+    targets = [t for t in targets if re.match(ur'[\\w-]+', t).group(0).lower() not in excludes]"
b' '
b'     if args.print:'
b'         for target in targets:'
b'-            print(target)'
b'+            print target'
b'         return'
b' '
b"-    pip_args = [sys.executable, '-m', 'pip', 'install', '-U']"
b"+    pip_args = [sys.executable, u'-m', u'pip', u'install', u'-U']"
b'     if args.user:'
b"-        pip_args.append('--user')"
b"+        pip_args.append(u'--user')"
b'     pip_args.extend(targets)'
b' '
b'     return subprocess.call(pip_args)'
b' '
b' '
b"-if __name__ == '__main__':"
b"+if __name__ == u'__main__':"
b'     sys.exit(main())'
