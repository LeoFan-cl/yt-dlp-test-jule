b'--- ./devscripts/make_changelog.py\t(original)'
b'+++ ./devscripts/make_changelog.py\t(refactored)'
b'@@ -1,8 +1,13 @@'
b'+from __future__ import division'
b'+from __future__ import absolute_import'
b' from __future__ import annotations'
b' '
b' # Allow direct execution'
b' import os'
b' import sys'
b'+from itertools import imap'
b'+from itertools import izip'
b'+from itertools import ifilter'
b' '
b' sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'
b' '
b'@@ -18,7 +23,7 @@'
b' '
b' from devscripts.utils import read_file, run_process, write_file'
b' '
b"-BASE_URL = 'https://github.com'"
b"+BASE_URL = u'https://github.com'"
b' LOCATION_PATH = Path(__file__).parent'
b' HASH_LENGTH = 7'
b' '
b'@@ -26,13 +31,13 @@'
b' '
b' '
b' class CommitGroup(enum.Enum):'
b"-    PRIORITY = 'Important'"
b"-    CORE = 'Core'"
b"-    EXTRACTOR = 'Extractor'"
b"-    DOWNLOADER = 'Downloader'"
b"-    POSTPROCESSOR = 'Postprocessor'"
b"-    NETWORKING = 'Networking'"
b"-    MISC = 'Misc.'"
b"+    PRIORITY = u'Important'"
b"+    CORE = u'Core'"
b"+    EXTRACTOR = u'Extractor'"
b"+    DOWNLOADER = u'Downloader'"
b"+    POSTPROCESSOR = u'Postprocessor'"
b"+    NETWORKING = u'Networking'"
b"+    MISC = u'Misc.'"
b' '
b'     @classmethod'
b'     @lru_cache'
b'@@ -40,17 +45,15 @@'
b'         return {'
b'             name: group'
b'             for group, names in {'
b'-                cls.MISC: {'
b"-                    'build',"
b"-                    'ci',"
b"-                    'cleanup',"
b"-                    'devscripts',"
b"-                    'docs',"
b"-                    'test',"
b'-                },'
b'-                cls.NETWORKING: {'
b"-                    'rh',"
b'-                },'
b'+                cls.MISC: set(['
b"+                    u'build',"
b"+                    u'ci',"
b"+                    u'cleanup',"
b"+                    u'devscripts',"
b"+                    u'docs',"
b"+                    u'test',]),"
b'+                cls.NETWORKING: set(['
b"+                    u'rh',]),"
b'             }.items()'
b'             for name in names'
b'         }'
b'@@ -59,17 +62,17 @@'
b'     @lru_cache'
b'     def group_lookup(cls):'
b'         result = {'
b"-            'fd': cls.DOWNLOADER,"
b"-            'ie': cls.EXTRACTOR,"
b"-            'pp': cls.POSTPROCESSOR,"
b"-            'upstream': cls.CORE,"
b"+            u'fd': cls.DOWNLOADER,"
b"+            u'ie': cls.EXTRACTOR,"
b"+            u'pp': cls.POSTPROCESSOR,"
b"+            u'upstream': cls.CORE,"
b'         }'
b'-        result.update({item.name.lower(): item for item in iter(cls)})'
b'+        result.update(dict((item.name.lower(), item) for item in iter(cls)))'
b'         return result'
b' '
b'     @classmethod'
b'-    def get(cls, value: str) -> tuple[CommitGroup | None, str | None]:'
b"-        group, _, subgroup = (group.strip().lower() for group in value.partition('/'))"
b'+    def get(cls, value):'
b"+        group, _, subgroup = (group.strip().lower() for group in value.partition(u'/'))"
b' '
b'         if result := cls.group_lookup().get(group):'
b'             return result, subgroup or None'
b'@@ -80,11 +83,10 @@'
b'         return cls.subgroup_lookup().get(group), group or None'
b' '
b' '
b'-@dataclass'
b'-class Commit:'
b'-    hash: str | None'
b'-    short: str'
b'-    authors: list[str]'
b'+class Commit(object):'
b'+    hash: unicode | None'
b'+    short: unicode'
b'+    authors: list[unicode]'
b' '
b'     def __str__(self):'
b"         result = f'{self.short!r}'"
b'@@ -93,31 +95,34 @@'
b"             result += f' ({self.hash[:HASH_LENGTH]})'"
b' '
b'         if self.authors:'
b"-            authors = ', '.join(self.authors)"
b"+            authors = u', '.join(self.authors)"
b"             result += f' by {authors}'"
b' '
b'         return result'
b' '
b' '
b'-@dataclass'
b'-class CommitInfo:'
b'-    details: str | None'
b'-    sub_details: tuple[str, ...]'
b'-    message: str'
b'-    issues: list[str]'
b'+Commit = dataclass(Commit)'
b'+'
b'+class CommitInfo(object):'
b'+    details: unicode | None'
b'+    sub_details: tuple[unicode, ...]'
b'+    message: unicode'
b'+    issues: list[unicode]'
b'     commit: Commit'
b'     fixes: list[Commit]'
b' '
b'     def key(self):'
b"-        return ((self.details or '').lower(), self.sub_details, self.message)"
b'-'
b"+        return ((self.details or u'').lower(), self.sub_details, self.message)"
b'+'
b'+'
b'+CommitInfo = dataclass(CommitInfo)'
b' '
b' def unique(items):'
b'-    return sorted({item.strip().lower(): item for item in items if item}.values())'
b'-'
b'-'
b'-class Changelog:'
b"-    MISC_RE = re.compile(r'(?:^|\\b)(?:lint(?:ing)?|misc|format(?:ting)?|fixes)(?:\\b|$)', re.IGNORECASE)"
b'+    return sorted(dict((item.strip().lower(), item) for item in items if item).values())'
b'+'
b'+'
b'+class Changelog(object):'
b"+    MISC_RE = re.compile(ur'(?:^|\\b)(?:lint(?:ing)?|misc|format(?:ting)?|fixes)(?:\\b|$)', re.IGNORECASE)"
b'     ALWAYS_SHOWN = (CommitGroup.PRIORITY,)'
b' '
b'     def __init__(self, groups, repo, collapsible=False):'
b'@@ -126,44 +131,44 @@'
b'         self._collapsible = collapsible'
b' '
b'     def __str__(self):'
b"-        return '\\n'.join(self._format_groups(self._groups)).replace('\\t', '    ')"
b"+        return u'\\n'.join(self._format_groups(self._groups)).replace(u'\\t', u'    ')"
b' '
b'     def _format_groups(self, groups):'
b'         first = True'
b'         for item in CommitGroup:'
b'             if self._collapsible and item not in self.ALWAYS_SHOWN and first:'
b'                 first = False'
b"-                yield '\\n<details><summary><h3>Changelog</h3></summary>\\n'"
b"+                yield u'\\n<details><summary><h3>Changelog</h3></summary>\\n'"
b' '
b'             if group := groups[item]:'
b'                 yield self.format_module(item.value, group)'
b' '
b'         if self._collapsible:'
b"-            yield '\\n</details>'"
b"+            yield u'\\n</details>'"
b' '
b'     def format_module(self, name, group):'
b"-        result = f'\\n#### {name} changes\\n' if name else '\\n'"
b"-        return result + '\\n'.join(self._format_group(group))"
b"+        result = f'\\n#### {name} changes\\n' if name else u'\\n'"
b"+        return result + u'\\n'.join(self._format_group(group))"
b' '
b'     def _format_group(self, group):'
b'         sorted_group = sorted(group, key=CommitInfo.key)'
b"-        detail_groups = itertools.groupby(sorted_group, lambda item: (item.details or '').lower())"
b"+        detail_groups = itertools.groupby(sorted_group, lambda item: (item.details or u'').lower())"
b'         for _, items in detail_groups:'
b'             items = list(items)'
b'             details = items[0].details'
b' '
b"-            if details == 'cleanup':"
b"+            if details == u'cleanup':"
b'                 items = self._prepare_cleanup_misc_items(items)'
b' '
b"-            prefix = '-'"
b"+            prefix = u'-'"
b'             if details:'
b'                 if len(items) == 1:'
b"                     prefix = f'- **{details}**:'"
b'                 else:'
b"                     yield f'- **{details}**'"
b"-                    prefix = '\\t-'"
b'-'
b'-            sub_detail_groups = itertools.groupby(items, lambda item: tuple(map(str.lower, item.sub_details)))'
b"+                    prefix = u'\\t-'"
b'+'
b'+            sub_detail_groups = itertools.groupby(items, lambda item: tuple(imap(unicode.lower, item.sub_details)))'
b'             for sub_details, entries in sub_detail_groups:'
b'                 if not sub_details:'
b'                     for entry in entries:'
b'@@ -191,16 +196,16 @@'
b' '
b'         for commit_infos in cleanup_misc_items.values():'
b'             sorted_items.append(CommitInfo('
b"-                'cleanup', ('Miscellaneous',), ', '.join("
b"+                u'cleanup', (u'Miscellaneous',), u', '.join("
b'                     self._format_message_link(None, info.commit.hash)'
b"-                    for info in sorted(commit_infos, key=lambda item: item.commit.hash or '')),"
b"-                [], Commit(None, '', commit_infos[0].commit.authors), []))"
b"+                    for info in sorted(commit_infos, key=lambda item: item.commit.hash or u'')),"
b"+                [], Commit(None, u'', commit_infos[0].commit.authors), []))"
b' '
b'         return sorted_items'
b' '
b'-    def format_single_change(self, info: CommitInfo):'
b"-        message, sep, rest = info.message.partition('\\n')"
b"-        if '[' not in message:"
b'+    def format_single_change(self, info):'
b"+        message, sep, rest = info.message.partition(u'\\n')"
b"+        if u'[' not in message:"
b"             # If the message doesn't already contain markdown links, try to add a link to the commit"
b'             message = self._format_message_link(message, info.commit.hash)'
b' '
b'@@ -211,9 +216,9 @@'
b"             message = f'{message} by {self._format_authors(info.commit.authors)}'"
b' '
b'         if info.fixes:'
b"-            fix_message = ', '.join(f'{self._format_message_link(None, fix.hash)}' for fix in info.fixes)"
b'-'
b'-            authors = sorted({author for fix in info.fixes for author in fix.authors}, key=str.casefold)'
b"+            fix_message = u', '.join(f'{self._format_message_link(None, fix.hash)}' for fix in info.fixes)"
b'+'
b'+            authors = sorted(set([author for fix in info.fixes for author in fix.authors]), key=unicode.casefold)'
b'             if authors != info.commit.authors:'
b"                 fix_message = f'{fix_message} by {self._format_authors(authors)}'"
b' '
b'@@ -222,37 +227,37 @@'
b"         return message if not sep else f'{message}{sep}{rest}'"
b' '
b'     def _format_message_link(self, message, commit_hash):'
b"-        assert message or commit_hash, 'Improperly defined commit message or override'"
b"+        assert message or commit_hash, u'Improperly defined commit message or override'"
b'         message = message if message else commit_hash[:HASH_LENGTH]'
b"         return f'[{message}]({self.repo_url}/commit/{commit_hash})' if commit_hash else message"
b' '
b'     def _format_issues(self, issues):'
b"-        return ', '.join(f'[#{issue}]({self.repo_url}/issues/{issue})' for issue in issues)"
b"+        return u', '.join(f'[#{issue}]({self.repo_url}/issues/{issue})' for issue in issues)"
b' '
b'     @staticmethod'
b'     def _format_authors(authors):'
b"-        return ', '.join(f'[{author}]({BASE_URL}/{author})' for author in authors)"
b"+        return u', '.join(f'[{author}]({BASE_URL}/{author})' for author in authors)"
b' '
b'     @property'
b'     def repo_url(self):'
b"         return f'{BASE_URL}/{self._repo}'"
b' '
b' '
b'-class CommitRange:'
b"-    COMMAND = 'git'"
b"-    COMMIT_SEPARATOR = '-----'"
b'-'
b"-    AUTHOR_INDICATOR_RE = re.compile(r'Authored by:? ', re.IGNORECASE)"
b"-    MESSAGE_RE = re.compile(r'''"
b'+class CommitRange(object):'
b"+    COMMAND = u'git'"
b"+    COMMIT_SEPARATOR = u'-----'"
b'+'
b"+    AUTHOR_INDICATOR_RE = re.compile(ur'Authored by:? ', re.IGNORECASE)"
b"+    MESSAGE_RE = re.compile(ur'''"
b'         (?:\\[(?P<prefix>[^\\]]+)\\]\\ )?'
b'         (?:(?P<sub_details>`?[\\w.-]+`?): )?'
b'         (?P<message>.+?)'
b'         (?:\\ \\((?P<issues>\\#\\d+(?:,\\ \\#\\d+)*)\\))?'
b"         ''', re.VERBOSE | re.DOTALL)"
b"-    EXTRACTOR_INDICATOR_RE = re.compile(r'(?:Fix|Add)\\s+Extractors?', re.IGNORECASE)"
b"-    REVERT_RE = re.compile(r'(?:\\[[^\\]]+\\]\\s+)?(?i:Revert)\\s+([\\da-f]{40})')"
b"-    FIXES_RE = re.compile(r'(?i:(?:bug\\s*)?fix(?:es)?(?:\\s+bugs?)?(?:\\s+in|\\s+for)?|Improve)\\s+([\\da-f]{40})')"
b"-    UPSTREAM_MERGE_RE = re.compile(r'Update to ytdl-commit-([\\da-f]+)')"
b"+    EXTRACTOR_INDICATOR_RE = re.compile(ur'(?:Fix|Add)\\s+Extractors?', re.IGNORECASE)"
b"+    REVERT_RE = re.compile(ur'(?:\\[[^\\]]+\\]\\s+)?(?i:Revert)\\s+([\\da-f]{40})')"
b"+    FIXES_RE = re.compile(ur'(?i:(?:bug\\s*)?fix(?:es)?(?:\\s+bugs?)?(?:\\s+in|\\s+for)?|Improve)\\s+([\\da-f]{40})')"
b"+    UPSTREAM_MERGE_RE = re.compile(ur'Update to ytdl-commit-([\\da-f]+)')"
b' '
b'     def __init__(self, start, end, default_author=None):'
b'         self._start, self._end = start, end'
b'@@ -275,24 +280,24 @@'
b' '
b'     def _get_commits_and_fixes(self, default_author):'
b'         result = run_process('
b"-            self.COMMAND, 'log', f'--format=%H%n%s%n%b%n{self.COMMIT_SEPARATOR}',"
b"+            self.COMMAND, u'log', f'--format=%H%n%s%n%b%n{self.COMMIT_SEPARATOR}',"
b"             f'{self._start}..{self._end}' if self._start else self._end).stdout"
b' '
b'         commits, reverts = {}, {}'
b'         fixes = defaultdict(list)'
b'         lines = iter(result.splitlines(False))'
b'         for i, commit_hash in enumerate(lines):'
b'-            short = next(lines)'
b"-            skip = short.startswith('Release ') or short == '[version] update'"
b'+            short = lines.next()'
b"+            skip = short.startswith(u'Release ') or short == u'[version] update'"
b' '
b'             fix_commitish = None'
b'             if match := self.FIXES_RE.search(short):'
b'                 fix_commitish = match.group(1)'
b' '
b'             authors = [default_author] if default_author else []'
b'-            for line in iter(lambda: next(lines), self.COMMIT_SEPARATOR):'
b'+            for line in iter(lambda: lines.next(), self.COMMIT_SEPARATOR):'
b'                 if match := self.AUTHOR_INDICATOR_RE.match(line):'
b"-                    authors = sorted(map(str.strip, line[match.end():].split(',')), key=str.casefold)"
b"+                    authors = sorted(imap(unicode.strip, line[match.end():].split(u',')), key=unicode.casefold)"
b'                 if not fix_commitish and (match := self.FIXES_RE.fullmatch(line)):'
b'                     fix_commitish = match.group(1)'
b' '
b'@@ -321,7 +326,7 @@'
b' '
b'         for commitish, fix_commits in fixes.items():'
b'             if commitish in commits:'
b"-                hashes = ', '.join(commit.hash[:HASH_LENGTH] for commit in fix_commits)"
b"+                hashes = u', '.join(commit.hash[:HASH_LENGTH] for commit in fix_commits)"
b"                 logger.info(f'Found fix(es) for {commitish[:HASH_LENGTH]}: {hashes}')"
b'                 for fix_commit in fix_commits:'
b'                     del commits[fix_commit.hash]'
b'@@ -332,26 +337,26 @@'
b' '
b'     def apply_overrides(self, overrides):'
b'         for override in overrides:'
b"-            when = override.get('when')"
b"+            when = override.get(u'when')"
b'             if when and when not in self and when != self._start:'
b"                 logger.debug(f'Ignored {when!r} override')"
b'                 continue'
b' '
b"-            override_hash = override.get('hash') or when"
b"-            if override['action'] == 'add':"
b"-                commit = Commit(override.get('hash'), override['short'], override.get('authors') or [])"
b"+            override_hash = override.get(u'hash') or when"
b"+            if override[u'action'] == u'add':"
b"+                commit = Commit(override.get(u'hash'), override[u'short'], override.get(u'authors') or [])"
b"                 logger.info(f'ADD    {commit}')"
b'                 self._commits_added.append(commit)'
b' '
b"-            elif override['action'] == 'remove':"
b"+            elif override[u'action'] == u'remove':"
b'                 if override_hash in self._commits:'
b"                     logger.info(f'REMOVE {self._commits[override_hash]}')"
b'                     del self._commits[override_hash]'
b' '
b"-            elif override['action'] == 'change':"
b"+            elif override[u'action'] == u'change':"
b'                 if override_hash not in self._commits:'
b'                     continue'
b"-                commit = Commit(override_hash, override['short'], override.get('authors') or [])"
b"+                commit = Commit(override_hash, override[u'short'], override.get(u'authors') or [])"
b"                 logger.info(f'CHANGE {self._commits[commit.hash]} -> {commit}')"
b'                 self._commits[commit.hash] = commit'
b' '
b'@@ -370,12 +375,12 @@'
b'                 continue'
b' '
b'             prefix, sub_details_alt, message, issues = match.groups()'
b"-            issues = [issue.strip()[1:] for issue in issues.split(',')] if issues else []"
b"+            issues = [issue.strip()[1:] for issue in issues.split(u',')] if issues else []"
b' '
b'             if prefix:'
b"-                groups, details, sub_details = zip(*map(self.details_from_prefix, prefix.split(',')))"
b'-                group = next(iter(filter(None, groups)), None)'
b"-                details = ', '.join(unique(details))"
b"+                groups, details, sub_details = izip(*imap(self.details_from_prefix, prefix.split(u',')))"
b'+                group = iter(ifilter(None, groups)), None.next()'
b"+                details = u', '.join(unique(details))"
b'                 sub_details = list(itertools.chain.from_iterable(sub_details))'
b'             else:'
b'                 group = CommitGroup.CORE'
b'@@ -407,20 +412,21 @@'
b'         if not prefix:'
b'             return CommitGroup.CORE, None, ()'
b' '
b"-        prefix, *sub_details = prefix.split(':')"
b"+        _3to2list = list(prefix.split(u':'))"
b'+prefix, sub_details, = _3to2list[:1] + [_3to2list[1:]]'
b' '
b'         group, details = CommitGroup.get(prefix)'
b'         if group is CommitGroup.PRIORITY and details:'
b"-            details = details.partition('/')[2].strip()"
b'-'
b"-        if details and '/' in details:"
b"+            details = details.partition(u'/')[2].strip()"
b'+'
b"+        if details and u'/' in details:"
b"             logger.error(f'Prefix is overnested, using first part: {prefix}')"
b"-            details = details.partition('/')[0].strip()"
b'-'
b"-        if details == 'common':"
b"+            details = details.partition(u'/')[0].strip()"
b'+'
b"+        if details == u'common':"
b'             details = None'
b"-        elif group is CommitGroup.NETWORKING and details == 'rh':"
b"-            details = 'Request Handler'"
b"+        elif group is CommitGroup.NETWORKING and details == u'rh':"
b"+            details = u'Request Handler'"
b' '
b'         return group, details, sub_details'
b' '
b'@@ -429,9 +435,9 @@'
b'     contributors = set()'
b'     if contributors_path.exists():'
b'         for line in read_file(contributors_path).splitlines():'
b"-            author, _, _ = line.strip().partition(' (')"
b"-            authors = author.split('/')"
b'-            contributors.update(map(str.casefold, authors))'
b"+            author, _, _ = line.strip().partition(u' (')"
b"+            authors = author.split(u'/')"
b'+            contributors.update(imap(unicode.casefold, authors))'
b' '
b'     new_contributors = set()'
b'     for commit in commits:'
b'@@ -441,13 +447,13 @@'
b'                 contributors.add(author_folded)'
b'                 new_contributors.add(author)'
b' '
b'-    return sorted(new_contributors, key=str.casefold)'
b'+    return sorted(new_contributors, key=unicode.casefold)'
b' '
b' '
b' def create_changelog(args):'
b'     logging.basicConfig('
b"-        datefmt='%Y-%m-%d %H-%M-%S', format='{asctime} | {levelname:<8} | {message}',"
b"-        level=logging.WARNING - 10 * args.verbosity, style='{', stream=sys.stderr)"
b"+        datefmt=u'%Y-%m-%d %H-%M-%S', format=u'{asctime} | {levelname:<8} | {message}',"
b"+        level=logging.WARNING - 10 * args.verbosity, style=u'{', stream=sys.stderr)"
b' '
b'     commits = CommitRange(None, args.commitish, args.default_author)'
b' '
b'@@ -462,7 +468,7 @@'
b' '
b'     if new_contributors := get_new_contributors(args.contributors_path, commits):'
b'         if args.contributors:'
b"-            write_file(args.contributors_path, '\\n'.join(new_contributors) + '\\n', mode='a')"
b"+            write_file(args.contributors_path, u'\\n'.join(new_contributors) + u'\\n', mode=u'a')"
b'         logger.info(f\'New contributors: {", ".join(new_contributors)}\')'
b' '
b'     return Changelog(commits.groups(), args.repo, args.collapsible)'
b'@@ -472,37 +478,37 @@'
b'     import argparse'
b' '
b'     parser = argparse.ArgumentParser('
b"-        description='Create a changelog markdown from a git commit range')"
b'-    parser.add_argument('
b"-        'commitish', default='HEAD', nargs='?',"
b"-        help='The commitish to create the range from (default: %(default)s)')"
b'-    parser.add_argument('
b"-        '-v', '--verbosity', action='count', default=0,"
b"-        help='increase verbosity (can be used twice)')"
b'-    parser.add_argument('
b"-        '-c', '--contributors', action='store_true',"
b"-        help='update CONTRIBUTORS file (default: %(default)s)')"
b'-    parser.add_argument('
b"-        '--contributors-path', type=Path, default=LOCATION_PATH.parent / 'CONTRIBUTORS',"
b"-        help='path to the CONTRIBUTORS file')"
b'-    parser.add_argument('
b"-        '--no-override', action='store_true',"
b"-        help='skip override json in commit generation (default: %(default)s)')"
b'-    parser.add_argument('
b"-        '--override-path', type=Path, default=LOCATION_PATH / 'changelog_override.json',"
b"-        help='path to the changelog_override.json file')"
b'-    parser.add_argument('
b"-        '--default-author', default='pukkandan',"
b"-        help='the author to use without a author indicator (default: %(default)s)')"
b'-    parser.add_argument('
b"-        '--repo', default='yt-dlp/yt-dlp',"
b"-        help='the github repository to use for the operations (default: %(default)s)')"
b'-    parser.add_argument('
b"-        '--collapsible', action='store_true',"
b"-        help='make changelog collapsible (default: %(default)s)')"
b"+        description=u'Create a changelog markdown from a git commit range')"
b'+    parser.add_argument('
b"+        u'commitish', default=u'HEAD', nargs=u'?',"
b"+        help=u'The commitish to create the range from (default: %(default)s)')"
b'+    parser.add_argument('
b"+        u'-v', u'--verbosity', action=u'count', default=0,"
b"+        help=u'increase verbosity (can be used twice)')"
b'+    parser.add_argument('
b"+        u'-c', u'--contributors', action=u'store_true',"
b"+        help=u'update CONTRIBUTORS file (default: %(default)s)')"
b'+    parser.add_argument('
b"+        u'--contributors-path', type=Path, default=LOCATION_PATH.parent / u'CONTRIBUTORS',"
b"+        help=u'path to the CONTRIBUTORS file')"
b'+    parser.add_argument('
b"+        u'--no-override', action=u'store_true',"
b"+        help=u'skip override json in commit generation (default: %(default)s)')"
b'+    parser.add_argument('
b"+        u'--override-path', type=Path, default=LOCATION_PATH / u'changelog_override.json',"
b"+        help=u'path to the changelog_override.json file')"
b'+    parser.add_argument('
b"+        u'--default-author', default=u'pukkandan',"
b"+        help=u'the author to use without a author indicator (default: %(default)s)')"
b'+    parser.add_argument('
b"+        u'--repo', default=u'yt-dlp/yt-dlp',"
b"+        help=u'the github repository to use for the operations (default: %(default)s)')"
b'+    parser.add_argument('
b"+        u'--collapsible', action=u'store_true',"
b"+        help=u'make changelog collapsible (default: %(default)s)')"
b' '
b'     return parser'
b' '
b' '
b"-if __name__ == '__main__':"
b'-    print(create_changelog(create_parser().parse_args()))'
b"+if __name__ == u'__main__':"
b'+    print create_changelog(create_parser().parse_args())'
