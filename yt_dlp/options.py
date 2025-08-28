b'--- ./yt_dlp/options.py\t(original)'
b'+++ ./yt_dlp/options.py\t(refactored)'
b'@@ -1,3 +1,5 @@'
b'+from __future__ import with_statement'
b'+from __future__ import absolute_import'
b' import collections'
b' import contextlib'
b' import optparse'
b'@@ -38,13 +40,15 @@'
b'     write_string,'
b' )'
b' from .version import CHANNEL, __version__'
b'-'
b'-'
b"-def parseOpts(overrideArguments=None, ignore_config_files='if_override'):  # noqa: N803"
b"-    PACKAGE_NAME = 'yt-dlp'"
b'+from itertools import ifilter'
b'+from itertools import imap'
b'+'
b'+'
b"+def parseOpts(overrideArguments=None, ignore_config_files=u'if_override'):  # noqa: N803"
b"+    PACKAGE_NAME = u'yt-dlp'"
b' '
b'     root = Config(create_parser())'
b"-    if ignore_config_files == 'if_override':"
b"+    if ignore_config_files == u'if_override':"
b'         ignore_config_files = overrideArguments is not None'
b' '
b'     def read_config(*paths):'
b'@@ -56,24 +60,24 @@'
b'     def _load_from_config_dirs(config_dirs):'
b'         for config_dir in config_dirs:'
b'             head, tail = os.path.split(config_dir)'
b"-            assert tail == PACKAGE_NAME or config_dir == os.path.join(compat_expanduser('~'), f'.{PACKAGE_NAME}')"
b"+            assert tail == PACKAGE_NAME or config_dir == os.path.join(compat_expanduser(u'~'), f'.{PACKAGE_NAME}')"
b' '
b"             yield read_config(head, f'{PACKAGE_NAME}.conf')"
b"-            if tail.startswith('.'):  # ~/.PACKAGE_NAME"
b"+            if tail.startswith(u'.'):  # ~/.PACKAGE_NAME"
b"                 yield read_config(head, f'{PACKAGE_NAME}.conf.txt')"
b"-            yield read_config(config_dir, 'config')"
b"-            yield read_config(config_dir, 'config.txt')"
b"+            yield read_config(config_dir, u'config')"
b"+            yield read_config(config_dir, u'config.txt')"
b' '
b'     def add_config(label, path=None, func=None):'
b'-        """ Adds config and returns whether to continue """'
b'+        u""" Adds config and returns whether to continue """'
b'         if root.parse_known_args()[0].ignoreconfig:'
b'             return False'
b'         elif func:'
b'             assert path is None'
b'-            args, current_path = next('
b'-                filter(None, _load_from_config_dirs(func(PACKAGE_NAME))), (None, None))'
b'+            args, current_path = '
b'+                ifilter(None, _load_from_config_dirs(func(PACKAGE_NAME))), (None, None).next()'
b'         else:'
b"-            current_path = os.path.join(path, 'yt-dlp.conf')"
b"+            current_path = os.path.join(path, u'yt-dlp.conf')"
b'             args = Config.read_file(current_path, default=None)'
b'         if args is not None:'
b'             root.append_config(args, current_path, label=label)'
b'@@ -81,33 +85,33 @@'
b' '
b'     def load_configs():'
b'         yield not ignore_config_files'
b"-        yield add_config('Portable', get_executable_path())"
b"-        yield add_config('Home', expand_path(root.parse_known_args()[0].paths.get('home', '')).strip())"
b"-        yield add_config('User', func=get_user_config_dirs)"
b"-        yield add_config('System', func=get_system_config_dirs)"
b'-'
b"-    opts = optparse.Values({'verbose': True, 'print_help': False})"
b"+        yield add_config(u'Portable', get_executable_path())"
b"+        yield add_config(u'Home', expand_path(root.parse_known_args()[0].paths.get(u'home', u'')).strip())"
b"+        yield add_config(u'User', func=get_user_config_dirs)"
b"+        yield add_config(u'System', func=get_system_config_dirs)"
b'+'
b"+    opts = optparse.Values({u'verbose': True, u'print_help': False})"
b'     try:'
b'         try:'
b'             if overrideArguments is not None:'
b"-                root.append_config(overrideArguments, label='Override')"
b"+                root.append_config(overrideArguments, label=u'Override')"
b'             else:'
b"-                root.append_config(sys.argv[1:], label='Command-line')"
b"+                root.append_config(sys.argv[1:], label=u'Command-line')"
b'             loaded_all_configs = all(load_configs())'
b'-        except ValueError as err:'
b'+        except ValueError, err:'
b'             raise root.parser.error(err)'
b' '
b'         if loaded_all_configs:'
b'             # If ignoreconfig is found inside the system configuration file,'
b'             # the user configuration is removed'
b'             if root.parse_known_args()[0].ignoreconfig:'
b"-                user_conf = next((i for i, conf in enumerate(root.configs) if conf.label == 'User'), None)"
b"+                user_conf = (i for i, conf in enumerate(root.configs) if conf.label == u'User'), None.next()"
b'                 if user_conf is not None:'
b'                     root.configs.pop(user_conf)'
b' '
b'         try:'
b'             root.configs[0].load_configs()  # Resolve any aliases using --config-location'
b'-        except ValueError as err:'
b'+        except ValueError, err:'
b'             raise root.parser.error(err)'
b' '
b'         opts, args = root.parse_args()'
b'@@ -119,12 +123,12 @@'
b'         opts.verbose = False'
b'         raise'
b'     finally:'
b"-        verbose = opts.verbose and f'\\n{root}'.replace('\\n| ', '\\n[debug] ')[1:]"
b"+        verbose = opts.verbose and f'\\n{root}'.replace(u'\\n| ', u'\\n[debug] ')[1:]"
b'         if verbose:'
b"             write_string(f'{verbose}\\n')"
b'         if opts.print_help:'
b'             if verbose:'
b"-                write_string('\\n')"
b"+                write_string(u'\\n')"
b'             root.parser.print_help()'
b'     if opts.print_help:'
b'         sys.exit()'
b'@@ -136,42 +140,42 @@'
b"         # No need to wrap help messages if we're on a wide console"
b'         max_width = shutil.get_terminal_size().columns or 80'
b'         # The % is chosen to get a pretty output in README.md'
b'-        super().__init__(width=max_width, max_help_position=int(0.45 * max_width))'
b'+        super(_YoutubeDLHelpFormatter, self).__init__(width=max_width, max_help_position=int(0.45 * max_width))'
b' '
b'     @staticmethod'
b'     def format_option_strings(option):'
b'-        """ (\'-o\', \'--option\') -> -o, --format METAVAR """'
b'+        u""" (\'-o\', \'--option\') -> -o, --format METAVAR """'
b'         opts = join_nonempty('
b'             option._short_opts and option._short_opts[0],'
b'             option._long_opts and option._long_opts[0],'
b"-            delim=', ')"
b"+            delim=u', ')"
b'         if option.takes_value():'
b"             opts += f' {option.metavar}'"
b'         return opts'
b' '
b' '
b' _PRESET_ALIASES = {'
b"-    'mp3': ['-f', 'ba[acodec^=mp3]/ba/b', '-x', '--audio-format', 'mp3'],"
b"-    'aac': ['-f', 'ba[acodec^=aac]/ba[acodec^=mp4a.40.]/ba/b', '-x', '--audio-format', 'aac'],"
b"-    'mp4': ['--merge-output-format', 'mp4', '--remux-video', 'mp4', '-S', 'vcodec:h264,lang,quality,res,fps,hdr:12,acodec:aac'],"
b"-    'mkv': ['--merge-output-format', 'mkv', '--remux-video', 'mkv'],"
b"-    'sleep': ['--sleep-subtitles', '5', '--sleep-requests', '0.75', '--sleep-interval', '10', '--max-sleep-interval', '20'],"
b"+    u'mp3': [u'-f', u'ba[acodec^=mp3]/ba/b', u'-x', u'--audio-format', u'mp3'],"
b"+    u'aac': [u'-f', u'ba[acodec^=aac]/ba[acodec^=mp4a.40.]/ba/b', u'-x', u'--audio-format', u'aac'],"
b"+    u'mp4': [u'--merge-output-format', u'mp4', u'--remux-video', u'mp4', u'-S', u'vcodec:h264,lang,quality,res,fps,hdr:12,acodec:aac'],"
b"+    u'mkv': [u'--merge-output-format', u'mkv', u'--remux-video', u'mkv'],"
b"+    u'sleep': [u'--sleep-subtitles', u'5', u'--sleep-requests', u'0.75', u'--sleep-interval', u'10', u'--max-sleep-interval', u'20'],"
b' }'
b' '
b' '
b' class _YoutubeDLOptionParser(optparse.OptionParser):'
b'     # optparse is deprecated since Python 3.2. So assume a stable interface even for private methods'
b"-    ALIAS_DEST = '_triggered_aliases'"
b"+    ALIAS_DEST = u'_triggered_aliases'"
b'     ALIAS_TRIGGER_LIMIT = 100'
b' '
b'     def __init__(self):'
b'-        super().__init__('
b"-            prog='yt-dlp' if detect_variant() == 'source' else None,"
b'+        super(_YoutubeDLOptionParser, self).__init__('
b"+            prog=u'yt-dlp' if detect_variant() == u'source' else None,"
b'             version=__version__,'
b"-            usage='%prog [OPTIONS] URL [URL...]',"
b"-            epilog='See full documentation at  https://github.com/yt-dlp/yt-dlp#readme',"
b"+            usage=u'%prog [OPTIONS] URL [URL...]',"
b"+            epilog=u'See full documentation at  https://github.com/yt-dlp/yt-dlp#readme',"
b'             formatter=_YoutubeDLHelpFormatter(),'
b"-            conflict_handler='resolve',"
b"+            conflict_handler=u'resolve',"
b'         )'
b'         self.set_default(self.ALIAS_DEST, collections.defaultdict(int))'
b' '
b'@@ -179,29 +183,29 @@'
b'     _BAD_OPTION = optparse.OptionValueError'
b' '
b'     def parse_known_args(self, args=None, values=None, strict=True):'
b'-        """Same as parse_args, but ignore unknown switches. Similar to argparse.parse_known_args"""'
b'+        u"""Same as parse_args, but ignore unknown switches. Similar to argparse.parse_known_args"""'
b'         self.rargs, self.largs = self._get_args(args), []'
b'         self.values = values or self.get_default_values()'
b'         while self.rargs:'
b'             arg = self.rargs[0]'
b'             try:'
b"-                if arg == '--':"
b"+                if arg == u'--':"
b'                     del self.rargs[0]'
b'                     break'
b"-                elif arg.startswith('--'):"
b"+                elif arg.startswith(u'--'):"
b'                     self._process_long_opt(self.rargs, self.values)'
b"-                elif arg.startswith('-') and arg != '-':"
b"+                elif arg.startswith(u'-') and arg != u'-':"
b'                     self._process_short_opts(self.rargs, self.values)'
b'                 elif self.allow_interspersed_args:'
b'                     self.largs.append(self.rargs.pop(0))'
b'                 else:'
b'                     break'
b'-            except optparse.OptParseError as err:'
b'+            except optparse.OptParseError, err:'
b'                 if isinstance(err, self._UNKNOWN_OPTION):'
b'                     self.largs.append(err.opt_str)'
b'                 elif strict:'
b'                     if isinstance(err, self._BAD_OPTION):'
b'-                        self.error(str(err))'
b'+                        self.error(unicode(err))'
b'                     raise'
b'         return self.check_values(self.values, self.largs)'
b' '
b'@@ -216,69 +220,69 @@'
b'         return sys.argv[1:] if args is None else list(args)'
b' '
b'     def _match_long_opt(self, opt):'
b'-        """Improve ambiguous argument resolution by comparing option objects instead of argument strings"""'
b'+        u"""Improve ambiguous argument resolution by comparing option objects instead of argument strings"""'
b'         try:'
b'-            return super()._match_long_opt(opt)'
b'-        except optparse.AmbiguousOptionError as e:'
b'-            if len({self._long_opt[p] for p in e.possibilities}) == 1:'
b'+            return super(_YoutubeDLOptionParser, self)._match_long_opt(opt)'
b'+        except optparse.AmbiguousOptionError, e:'
b'+            if len(set(self._long_opt[p] for p in e.possibilities)) == 1:'
b'                 return e.possibilities[0]'
b'             raise'
b' '
b'     def format_option_help(self, formatter=None):'
b"-        assert formatter, 'Formatter can not be None'"
b'-        formatted_help = super().format_option_help(formatter=formatter)'
b"+        assert formatter, u'Formatter can not be None'"
b'+        formatted_help = super(_YoutubeDLOptionParser, self).format_option_help(formatter=formatter)'
b'         formatter.indent()'
b"-        heading = formatter.format_heading('Preset Aliases')"
b"+        heading = formatter.format_heading(u'Preset Aliases')"
b'         formatter.indent()'
b'         description = formatter.format_description('
b"-            'Predefined aliases for convenience and ease of use. Note that future versions of yt-dlp '"
b"-            'may add or adjust presets, but the existing preset names will not be changed or removed')"
b"+            u'Predefined aliases for convenience and ease of use. Note that future versions of yt-dlp '"
b"+            u'may add or adjust presets, but the existing preset names will not be changed or removed')"
b'         result = []'
b'         for name, args in _PRESET_ALIASES.items():'
b"-            option = optparse.Option('-t', help=shlex.join(args))"
b"+            option = optparse.Option(u'-t', help=shlex.join(args))"
b"             formatter.option_strings[option] = f'-t {name}'"
b'             result.append(formatter.format_option(option))'
b'         formatter.dedent()'
b'         formatter.dedent()'
b"-        help_lines = '\\n'.join(result)"
b"+        help_lines = u'\\n'.join(result)"
b"         return f'{formatted_help}\\n{heading}{description}\\n{help_lines}'"
b' '
b' '
b' def create_parser():'
b"-    def _list_from_options_callback(option, opt_str, value, parser, append=True, delim=',', process=str.strip):"
b"+    def _list_from_options_callback(option, opt_str, value, parser, append=True, delim=u',', process=unicode.strip):"
b'         # append can be True, False or -1 (prepend)'
b'         current = list(getattr(parser.values, option.dest)) if append else []'
b'-        value = list(filter(None, [process(value)] if delim is None else map(process, value.split(delim))))'
b'+        value = list(ifilter(None, [process(value)] if delim is None else imap(process, value.split(delim))))'
b'         setattr('
b'             parser.values, option.dest,'
b'             current + value if append is True else value + current)'
b' '
b'     def _set_from_options_callback('
b"-            option, opt_str, value, parser, allowed_values, delim=',', aliases={},"
b"+            option, opt_str, value, parser, allowed_values, delim=u',', aliases={},"
b'             process=lambda x: x.lower().strip()):'
b'-        values = [process(value)] if delim is None else map(process, value.split(delim))'
b'+        values = [process(value)] if delim is None else imap(process, value.split(delim))'
b'         try:'
b"-            requested = orderedSet_from_options(values, collections.ChainMap(aliases, {'all': allowed_values}),"
b"+            requested = orderedSet_from_options(values, collections.ChainMap(aliases, {u'all': allowed_values}),"
b'                                                 start=getattr(parser.values, option.dest))'
b'-        except ValueError as e:'
b'+        except ValueError, e:'
b"             raise optparse.OptionValueError(f'wrong {option.metavar} for {opt_str}: {e.args[0]}')"
b' '
b'         setattr(parser.values, option.dest, set(requested))'
b' '
b'     def _dict_from_options_callback('
b'             option, opt_str, value, parser,'
b"-            allowed_keys=r'[\\w-]+', delimiter=':', default_key=None, process=None, multiple_keys=True,"
b'-            process_key=str.lower, append=False):'
b"+            allowed_keys=ur'[\\w-]+', delimiter=u':', default_key=None, process=None, multiple_keys=True,"
b'+            process_key=unicode.lower, append=False):'
b' '
b'         out_dict = dict(getattr(parser.values, option.dest))'
b'-        multiple_args = not isinstance(value, str)'
b'+        multiple_args = not isinstance(value, unicode)'
b'         if multiple_keys:'
b"             allowed_keys = fr'({allowed_keys})(,({allowed_keys}))*'"
b'         mobj = re.match('
b"             fr'(?is)(?P<keys>{allowed_keys}){delimiter}(?P<val>.*)$',"
b'             value[0] if multiple_args else value)'
b'         if mobj is not None:'
b"-            keys, val = mobj.group('keys').split(','), mobj.group('val')"
b"+            keys, val = mobj.group(u'keys').split(u','), mobj.group(u'val')"
b'             if multiple_args:'
b'                 val = [val, *value[1:]]'
b'         elif default_key is not None:'
b'@@ -287,9 +291,9 @@'
b'             raise optparse.OptionValueError('
b'                 f\'wrong {opt_str} formatting; it should be {option.metavar}, not "{value}"\')'
b'         try:'
b'-            keys = map(process_key, keys) if process_key else keys'
b'+            keys = imap(process_key, keys) if process_key else keys'
b'             val = process(val) if process else val'
b'-        except Exception as err:'
b'+        except Exception, err:'
b"             raise optparse.OptionValueError(f'wrong {opt_str} formatting; {err}')"
b'         for key in keys:'
b'             out_dict[key] = [*out_dict.get(key, []), val] if append else val'
b'@@ -297,41 +301,41 @@'
b' '
b'     def when_prefix(default):'
b'         return {'
b"-            'default': {},"
b"-            'type': 'str',"
b"-            'action': 'callback',"
b"-            'callback': _dict_from_options_callback,"
b"-            'callback_kwargs': {"
b"-                'allowed_keys': '|'.join(map(re.escape, POSTPROCESS_WHEN)),"
b"-                'default_key': default,"
b"-                'multiple_keys': False,"
b"-                'append': True,"
b"+            u'default': {},"
b"+            u'type': u'str',"
b"+            u'action': u'callback',"
b"+            u'callback': _dict_from_options_callback,"
b"+            u'callback_kwargs': {"
b"+                u'allowed_keys': u'|'.join(imap(re.escape, POSTPROCESS_WHEN)),"
b"+                u'default_key': default,"
b"+                u'multiple_keys': False,"
b"+                u'append': True,"
b'             },'
b'         }'
b' '
b'     parser = _YoutubeDLOptionParser()'
b"-    alias_group = optparse.OptionGroup(parser, 'Aliases')"
b"+    alias_group = optparse.OptionGroup(parser, u'Aliases')"
b'     Formatter = string.Formatter()'
b' '
b'     def _create_alias(option, opt_str, value, parser):'
b'         aliases, opts = value'
b'         try:'
b"-            nargs = len({i if f == '' else f"
b'-                         for i, (_, f, _, _) in enumerate(Formatter.parse(opts)) if f is not None})'
b'-            opts.format(*map(str, range(nargs)))  # validate'
b'-        except Exception as err:'
b"+            nargs = len(set(i if f == u'' else f"
b'+                         for i, (_, f, _, _) in enumerate(Formatter.parse(opts)) if f is not None))'
b'+            opts.format(*imap(unicode, xrange(nargs)))  # validate'
b'+        except Exception, err:'
b"             raise optparse.OptionValueError(f'wrong {opt_str} OPTIONS formatting; {err}')"
b'         if alias_group not in parser.option_groups:'
b'             parser.add_option_group(alias_group)'
b' '
b"-        aliases = (x if x.startswith('-') else f'--{x}' for x in map(str.strip, aliases.split(',')))"
b"+        aliases = (x if x.startswith(u'-') else f'--{x}' for x in imap(unicode.strip, aliases.split(u',')))"
b'         try:'
b"-            args = [f'ARG{i}' for i in range(nargs)]"
b"+            args = [f'ARG{i}' for i in xrange(nargs)]"
b'             alias_group.add_option('
b"-                *aliases, nargs=nargs, dest=parser.ALIAS_DEST, type='str' if nargs else None,"
b"-                metavar=' '.join(args), help=opts.format(*args), action='callback',"
b"-                callback=_alias_callback, callback_kwargs={'opts': opts, 'nargs': nargs})"
b'-        except Exception as err:'
b"+                *aliases, nargs=nargs, dest=parser.ALIAS_DEST, type=u'str' if nargs else None,"
b"+                metavar=u' '.join(args), help=opts.format(*args), action=u'callback',"
b"+                callback=_alias_callback, callback_kwargs={u'opts': opts, u'nargs': nargs})"
b'+        except Exception, err:'
b"             raise optparse.OptionValueError(f'wrong {opt_str} formatting; {err}')"
b' '
b'     def _alias_callback(option, opt_str, value, parser, opts, nargs):'
b'@@ -343,7 +347,7 @@'
b'             value = [value]'
b'         assert (nargs == 0 and value is None) or len(value) == nargs'
b'         parser.rargs[:0] = shlex.split('
b'-            opts if value is None else opts.format(*map(shlex.quote, value)))'
b'+            opts if value is None else opts.format(*imap(shlex.quote, value)))'
b' '
b'     def _preset_alias_callback(option, opt_str, value, parser):'
b'         if not value:'
b'@@ -352,1636 +356,1635 @@'
b"             raise optparse.OptionValueError(f'Unknown preset alias: {value}')"
b'         parser.rargs[:0] = _PRESET_ALIASES[value]'
b' '
b"-    general = optparse.OptionGroup(parser, 'General Options')"
b'-    general.add_option('
b"-        '-h', '--help', dest='print_help', action='store_true',"
b"-        help='Print this help text and exit')"
b'-    general.add_option('
b"-        '--version',"
b"-        action='version',"
b"-        help='Print program version and exit')"
b'-    general.add_option('
b"-        '-U', '--update',"
b"-        action='store_const', dest='update_self', const=CHANNEL,"
b"+    general = optparse.OptionGroup(parser, u'General Options')"
b'+    general.add_option('
b"+        u'-h', u'--help', dest=u'print_help', action=u'store_true',"
b"+        help=u'Print this help text and exit')"
b'+    general.add_option('
b"+        u'--version',"
b"+        action=u'version',"
b"+        help=u'Print program version and exit')"
b'+    general.add_option('
b"+        u'-U', u'--update',"
b"+        action=u'store_const', dest=u'update_self', const=CHANNEL,"
b'         help=format_field('
b"-            is_non_updateable(), None, 'Check if updates are available. %s',"
b"+            is_non_updateable(), None, u'Check if updates are available. %s',"
b"             default=f'Update this program to the latest {CHANNEL} version'))"
b'     general.add_option('
b"-        '--no-update',"
b"-        action='store_false', dest='update_self',"
b"-        help='Do not check for updates (default)')"
b'-    general.add_option('
b"-        '--update-to',"
b"-        action='store', dest='update_self', metavar='[CHANNEL]@[TAG]',"
b'-        help=('
b"-            'Upgrade/downgrade to a specific version. CHANNEL can be a repository as well. '"
b"+        u'--no-update',"
b"+        action=u'store_false', dest=u'update_self',"
b"+        help=u'Do not check for updates (default)')"
b'+    general.add_option('
b"+        u'--update-to',"
b"+        action=u'store', dest=u'update_self', metavar=u'[CHANNEL]@[TAG]',"
b'+        help=('
b"+            u'Upgrade/downgrade to a specific version. CHANNEL can be a repository as well. '"
b'             f\'CHANNEL and TAG default to "{CHANNEL.partition("@")[0]}" and "latest" respectively if omitted; \''
b'             f\'See "UPDATE" for details. Supported channels: {", ".join(UPDATE_SOURCES)}\'))'
b'     general.add_option('
b"-        '-i', '--ignore-errors',"
b"-        action='store_true', dest='ignoreerrors',"
b"-        help='Ignore download and postprocessing errors. The download will be considered successful even if the postprocessing fails')"
b'-    general.add_option('
b"-        '--no-abort-on-error',"
b"-        action='store_const', dest='ignoreerrors', const='only_download',"
b"-        help='Continue with next video on download errors; e.g. to skip unavailable videos in a playlist (default)')"
b'-    general.add_option('
b"-        '--abort-on-error', '--no-ignore-errors',"
b"-        action='store_false', dest='ignoreerrors',"
b"-        help='Abort downloading of further videos if an error occurs (Alias: --no-ignore-errors)')"
b'-    general.add_option('
b"-        '--dump-user-agent',"
b"-        action='store_true', dest='dump_user_agent', default=False,"
b"-        help='Display the current user-agent and exit')"
b'-    general.add_option('
b"-        '--list-extractors',"
b"-        action='store_true', dest='list_extractors', default=False,"
b"-        help='List all supported extractors and exit')"
b'-    general.add_option('
b"-        '--extractor-descriptions',"
b"-        action='store_true', dest='list_extractor_descriptions', default=False,"
b"-        help='Output descriptions of all supported extractors and exit')"
b'-    general.add_option('
b"-        '--use-extractors', '--ies',"
b"-        action='callback', dest='allowed_extractors', metavar='NAMES', type='str',"
b"+        u'-i', u'--ignore-errors',"
b"+        action=u'store_true', dest=u'ignoreerrors',"
b"+        help=u'Ignore download and postprocessing errors. The download will be considered successful even if the postprocessing fails')"
b'+    general.add_option('
b"+        u'--no-abort-on-error',"
b"+        action=u'store_const', dest=u'ignoreerrors', const=u'only_download',"
b"+        help=u'Continue with next video on download errors; e.g. to skip unavailable videos in a playlist (default)')"
b'+    general.add_option('
b"+        u'--abort-on-error', u'--no-ignore-errors',"
b"+        action=u'store_false', dest=u'ignoreerrors',"
b"+        help=u'Abort downloading of further videos if an error occurs (Alias: --no-ignore-errors)')"
b'+    general.add_option('
b"+        u'--dump-user-agent',"
b"+        action=u'store_true', dest=u'dump_user_agent', default=False,"
b"+        help=u'Display the current user-agent and exit')"
b'+    general.add_option('
b"+        u'--list-extractors',"
b"+        action=u'store_true', dest=u'list_extractors', default=False,"
b"+        help=u'List all supported extractors and exit')"
b'+    general.add_option('
b"+        u'--extractor-descriptions',"
b"+        action=u'store_true', dest=u'list_extractor_descriptions', default=False,"
b"+        help=u'Output descriptions of all supported extractors and exit')"
b'+    general.add_option('
b"+        u'--use-extractors', u'--ies',"
b"+        action=u'callback', dest=u'allowed_extractors', metavar=u'NAMES', type=u'str',"
b'         default=[], callback=_list_from_options_callback,'
b'         help=('
b"-            'Extractor names to use separated by commas. '"
b'-            \'You can also use regexes, "all", "default" and "end" (end URL matching); \''
b'-            \'e.g. --ies "holodex.*,end,youtube". \''
b'-            \'Prefix the name with a "-" to exclude it, e.g. --ies default,-generic. \''
b"-            'Use --list-extractors for a list of extractor names. (Alias: --ies)'))"
b'-    general.add_option('
b"-        '--force-generic-extractor',"
b"-        action='store_true', dest='force_generic_extractor', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    general.add_option('
b"-        '--default-search',"
b"-        dest='default_search', metavar='PREFIX',"
b'-        help=('
b"-            'Use this prefix for unqualified URLs. '"
b'-            \'E.g. "gvsearch2:python" downloads two videos from google videos for the search term "python". \''
b'-            \'Use the value "auto" to let yt-dlp guess ("auto_warning" to emit a warning when guessing). \''
b'-            \'"error" just throws an error. The default value "fixup_error" repairs broken URLs, \''
b"-            'but emits an error if this is not possible instead of searching'))"
b'-    general.add_option('
b"-        '--ignore-config', '--no-config',"
b"-        action='store_true', dest='ignoreconfig',"
b'-        help=('
b"-            'Don\\'t load any more configuration files except those given to --config-locations. '"
b"-            'For backward compatibility, if this option is found inside the system configuration file, the user configuration is not loaded. '"
b"-            '(Alias: --no-config)'))"
b'-    general.add_option('
b"-        '--no-config-locations',"
b"-        action='store_const', dest='config_locations', const=None,"
b'-        help=('
b"-            'Do not load any custom configuration files (default). When given inside a '"
b"-            'configuration file, ignore all previous --config-locations defined in the current file'))"
b'-    general.add_option('
b"-        '--config-locations',"
b"-        dest='config_locations', metavar='PATH', action='append',"
b'-        help=('
b"-            'Location of the main configuration file; either the path to the config or its containing directory '"
b'-            \'("-" for stdin). Can be used multiple times and inside other configuration files\'))'
b'-    general.add_option('
b"-        '--plugin-dirs',"
b"-        metavar='PATH',"
b"-        dest='plugin_dirs',"
b"-        action='callback',"
b"+            u'Extractor names to use separated by commas. '"
b'+            u\'You can also use regexes, "all", "default" and "end" (end URL matching); \''
b'+            u\'e.g. --ies "holodex.*,end,youtube". \''
b'+            u\'Prefix the name with a "-" to exclude it, e.g. --ies default,-generic. \''
b"+            u'Use --list-extractors for a list of extractor names. (Alias: --ies)'))"
b'+    general.add_option('
b"+        u'--force-generic-extractor',"
b"+        action=u'store_true', dest=u'force_generic_extractor', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    general.add_option('
b"+        u'--default-search',"
b"+        dest=u'default_search', metavar=u'PREFIX',"
b'+        help=('
b"+            u'Use this prefix for unqualified URLs. '"
b'+            u\'E.g. "gvsearch2:python" downloads two videos from google videos for the search term "python". \''
b'+            u\'Use the value "auto" to let yt-dlp guess ("auto_warning" to emit a warning when guessing). \''
b'+            u\'"error" just throws an error. The default value "fixup_error" repairs broken URLs, \''
b"+            u'but emits an error if this is not possible instead of searching'))"
b'+    general.add_option('
b"+        u'--ignore-config', u'--no-config',"
b"+        action=u'store_true', dest=u'ignoreconfig',"
b'+        help=('
b"+            u'Don\\'t load any more configuration files except those given to --config-locations. '"
b"+            u'For backward compatibility, if this option is found inside the system configuration file, the user configuration is not loaded. '"
b"+            u'(Alias: --no-config)'))"
b'+    general.add_option('
b"+        u'--no-config-locations',"
b"+        action=u'store_const', dest=u'config_locations', const=None,"
b'+        help=('
b"+            u'Do not load any custom configuration files (default). When given inside a '"
b"+            u'configuration file, ignore all previous --config-locations defined in the current file'))"
b'+    general.add_option('
b"+        u'--config-locations',"
b"+        dest=u'config_locations', metavar=u'PATH', action=u'append',"
b'+        help=('
b"+            u'Location of the main configuration file; either the path to the config or its containing directory '"
b'+            u\'("-" for stdin). Can be used multiple times and inside other configuration files\'))'
b'+    general.add_option('
b"+        u'--plugin-dirs',"
b"+        metavar=u'PATH',"
b"+        dest=u'plugin_dirs',"
b"+        action=u'callback',"
b'         callback=_list_from_options_callback,'
b"-        type='str',"
b"-        callback_kwargs={'delim': None},"
b"-        default=['default'],"
b'-        help=('
b"-            'Path to an additional directory to search for plugins. '"
b"-            'This option can be used multiple times to add multiple directories. '"
b'-            \'Use "default" to search the default plugin directories (default)\'))'
b'-    general.add_option('
b"-        '--no-plugin-dirs',"
b"-        dest='plugin_dirs', action='store_const', const=[],"
b"-        help='Clear plugin directories to search, including defaults and those provided by previous --plugin-dirs')"
b'-    general.add_option('
b"-        '--flat-playlist',"
b"-        action='store_const', dest='extract_flat', const='in_playlist', default=False,"
b'-        help=('
b"-            'Do not extract a playlist\\'s URL result entries; '"
b"-            'some entry metadata may be missing and downloading may be bypassed'))"
b'-    general.add_option('
b"-        '--no-flat-playlist',"
b"-        action='store_false', dest='extract_flat',"
b"-        help='Fully extract the videos of a playlist (default)')"
b'-    general.add_option('
b"-        '--live-from-start',"
b"-        action='store_true', dest='live_from_start',"
b"-        help='Download livestreams from the start. Currently experimental and only supported for YouTube and Twitch')"
b'-    general.add_option('
b"-        '--no-live-from-start',"
b"-        action='store_false', dest='live_from_start',"
b"-        help='Download livestreams from the current time (default)')"
b'-    general.add_option('
b"-        '--wait-for-video',"
b"-        dest='wait_for_video', metavar='MIN[-MAX]', default=None,"
b'-        help=('
b"-            'Wait for scheduled streams to become available. '"
b"-            'Pass the minimum number of seconds (or range) to wait between retries'))"
b'-    general.add_option('
b"-        '--no-wait-for-video',"
b"-        dest='wait_for_video', action='store_const', const=None,"
b"-        help='Do not wait for scheduled streams (default)')"
b'-    general.add_option('
b"-        '--mark-watched',"
b"-        action='store_true', dest='mark_watched', default=False,"
b"-        help='Mark videos watched (even with --simulate)')"
b'-    general.add_option('
b"-        '--no-mark-watched',"
b"-        action='store_false', dest='mark_watched',"
b"-        help='Do not mark videos watched (default)')"
b'-    general.add_option('
b"-        '--no-colors', '--no-colours',"
b"-        action='store_const', dest='color', const={"
b"-            'stdout': 'no_color',"
b"-            'stderr': 'no_color',"
b"+        type=u'str',"
b"+        callback_kwargs={u'delim': None},"
b"+        default=[u'default'],"
b'+        help=('
b"+            u'Path to an additional directory to search for plugins. '"
b"+            u'This option can be used multiple times to add multiple directories. '"
b'+            u\'Use "default" to search the default plugin directories (default)\'))'
b'+    general.add_option('
b"+        u'--no-plugin-dirs',"
b"+        dest=u'plugin_dirs', action=u'store_const', const=[],"
b"+        help=u'Clear plugin directories to search, including defaults and those provided by previous --plugin-dirs')"
b'+    general.add_option('
b"+        u'--flat-playlist',"
b"+        action=u'store_const', dest=u'extract_flat', const=u'in_playlist', default=False,"
b'+        help=('
b"+            u'Do not extract a playlist\\'s URL result entries; '"
b"+            u'some entry metadata may be missing and downloading may be bypassed'))"
b'+    general.add_option('
b"+        u'--no-flat-playlist',"
b"+        action=u'store_false', dest=u'extract_flat',"
b"+        help=u'Fully extract the videos of a playlist (default)')"
b'+    general.add_option('
b"+        u'--live-from-start',"
b"+        action=u'store_true', dest=u'live_from_start',"
b"+        help=u'Download livestreams from the start. Currently experimental and only supported for YouTube and Twitch')"
b'+    general.add_option('
b"+        u'--no-live-from-start',"
b"+        action=u'store_false', dest=u'live_from_start',"
b"+        help=u'Download livestreams from the current time (default)')"
b'+    general.add_option('
b"+        u'--wait-for-video',"
b"+        dest=u'wait_for_video', metavar=u'MIN[-MAX]', default=None,"
b'+        help=('
b"+            u'Wait for scheduled streams to become available. '"
b"+            u'Pass the minimum number of seconds (or range) to wait between retries'))"
b'+    general.add_option('
b"+        u'--no-wait-for-video',"
b"+        dest=u'wait_for_video', action=u'store_const', const=None,"
b"+        help=u'Do not wait for scheduled streams (default)')"
b'+    general.add_option('
b"+        u'--mark-watched',"
b"+        action=u'store_true', dest=u'mark_watched', default=False,"
b"+        help=u'Mark videos watched (even with --simulate)')"
b'+    general.add_option('
b"+        u'--no-mark-watched',"
b"+        action=u'store_false', dest=u'mark_watched',"
b"+        help=u'Do not mark videos watched (default)')"
b'+    general.add_option('
b"+        u'--no-colors', u'--no-colours',"
b"+        action=u'store_const', dest=u'color', const={"
b"+            u'stdout': u'no_color',"
b"+            u'stderr': u'no_color',"
b'         },'
b'         help=optparse.SUPPRESS_HELP)'
b'     general.add_option('
b"-        '--color',"
b"-        dest='color', metavar='[STREAM:]POLICY', default={}, type='str',"
b"-        action='callback', callback=_dict_from_options_callback,"
b"+        u'--color',"
b"+        dest=u'color', metavar=u'[STREAM:]POLICY', default={}, type=u'str',"
b"+        action=u'callback', callback=_dict_from_options_callback,"
b'         callback_kwargs={'
b"-            'allowed_keys': 'stdout|stderr',"
b"-            'default_key': ['stdout', 'stderr'],"
b"-            'process': str.strip,"
b"+            u'allowed_keys': u'stdout|stderr',"
b"+            u'default_key': [u'stdout', u'stderr'],"
b"+            u'process': unicode.strip,"
b'         }, help=('
b"-            'Whether to emit color codes in output, optionally prefixed by '"
b"-            'the STREAM (stdout or stderr) to apply the setting to. '"
b'-            \'Can be one of "always", "auto" (default), "never", or \''
b'-            \'"no_color" (use non color terminal sequences). \''
b'-            \'Use "auto-tty" or "no_color-tty" to decide based on terminal support only. \''
b"-            'Can be used multiple times'))"
b'-    general.add_option('
b"-        '--compat-options',"
b"-        metavar='OPTS', dest='compat_opts', default=set(), type='str',"
b"-        action='callback', callback=_set_from_options_callback,"
b"+            u'Whether to emit color codes in output, optionally prefixed by '"
b"+            u'the STREAM (stdout or stderr) to apply the setting to. '"
b'+            u\'Can be one of "always", "auto" (default), "never", or \''
b'+            u\'"no_color" (use non color terminal sequences). \''
b'+            u\'Use "auto-tty" or "no_color-tty" to decide based on terminal support only. \''
b"+            u'Can be used multiple times'))"
b'+    general.add_option('
b"+        u'--compat-options',"
b"+        metavar=u'OPTS', dest=u'compat_opts', default=set(), type=u'str',"
b"+        action=u'callback', callback=_set_from_options_callback,"
b'         callback_kwargs={'
b"-            'allowed_values': {"
b"-                'filename', 'filename-sanitization', 'format-sort', 'abort-on-error', 'format-spec', 'no-playlist-metafiles',"
b"-                'multistreams', 'no-live-chat', 'playlist-index', 'list-formats', 'no-direct-merge', 'playlist-match-filter',"
b"-                'no-attach-info-json', 'embed-thumbnail-atomicparsley', 'no-external-downloader-progress',"
b"-                'embed-metadata', 'seperate-video-versions', 'no-clean-infojson', 'no-keep-subs', 'no-certifi',"
b"-                'no-youtube-channel-redirect', 'no-youtube-unavailable-videos', 'no-youtube-prefer-utc-upload-date',"
b"-                'prefer-legacy-http-handler', 'manifest-filesize-approx', 'allow-unsafe-ext', 'prefer-vp9-sort', 'mtime-by-default',"
b"-            }, 'aliases': {"
b"-                'youtube-dl': ['all', '-multistreams', '-playlist-match-filter', '-manifest-filesize-approx', '-allow-unsafe-ext', '-prefer-vp9-sort'],"
b"-                'youtube-dlc': ['all', '-no-youtube-channel-redirect', '-no-live-chat', '-playlist-match-filter', '-manifest-filesize-approx', '-allow-unsafe-ext', '-prefer-vp9-sort'],"
b"-                '2021': ['2022', 'no-certifi', 'filename-sanitization'],"
b"-                '2022': ['2023', 'no-external-downloader-progress', 'playlist-match-filter', 'prefer-legacy-http-handler', 'manifest-filesize-approx'],"
b"-                '2023': ['2024', 'prefer-vp9-sort'],"
b"-                '2024': ['mtime-by-default'],"
b"+            u'allowed_values': set(["
b"+                u'filename', u'filename-sanitization', u'format-sort', u'abort-on-error', u'format-spec', u'no-playlist-metafiles',"
b"+                u'multistreams', u'no-live-chat', u'playlist-index', u'list-formats', u'no-direct-merge', u'playlist-match-filter',"
b"+                u'no-attach-info-json', u'embed-thumbnail-atomicparsley', u'no-external-downloader-progress',"
b"+                u'embed-metadata', u'seperate-video-versions', u'no-clean-infojson', u'no-keep-subs', u'no-certifi',"
b"+                u'no-youtube-channel-redirect', u'no-youtube-unavailable-videos', u'no-youtube-prefer-utc-upload-date',"
b"+                u'prefer-legacy-http-handler', u'manifest-filesize-approx', u'allow-unsafe-ext', u'prefer-vp9-sort', u'mtime-by-default',]), u'aliases': {"
b"+                u'youtube-dl': [u'all', u'-multistreams', u'-playlist-match-filter', u'-manifest-filesize-approx', u'-allow-unsafe-ext', u'-prefer-vp9-sort'],"
b"+                u'youtube-dlc': [u'all', u'-no-youtube-channel-redirect', u'-no-live-chat', u'-playlist-match-filter', u'-manifest-filesize-approx', u'-allow-unsafe-ext', u'-prefer-vp9-sort'],"
b"+                u'2021': [u'2022', u'no-certifi', u'filename-sanitization'],"
b"+                u'2022': [u'2023', u'no-external-downloader-progress', u'playlist-match-filter', u'prefer-legacy-http-handler', u'manifest-filesize-approx'],"
b"+                u'2023': [u'2024', u'prefer-vp9-sort'],"
b"+                u'2024': [u'mtime-by-default'],"
b'             },'
b'         }, help=('
b"-            'Options that can help keep compatibility with youtube-dl or youtube-dlc '"
b"-            'configurations by reverting some of the changes made in yt-dlp. '"
b'-            \'See "Differences in default behavior" for details\'))'
b'-    general.add_option('
b"-        '--alias', metavar='ALIASES OPTIONS', dest='_', type='str', nargs=2,"
b"-        action='callback', callback=_create_alias,"
b'-        help=('
b'-            \'Create aliases for an option string. Unless an alias starts with a dash "-", it is prefixed with "--". \''
b"-            'Arguments are parsed according to the Python string formatting mini-language. '"
b'-            \'E.g. --alias get-audio,-X "-S aext:{0},abr -x --audio-format {0}" creates options \''
b'-            \'"--get-audio" and "-X" that takes an argument (ARG0) and expands to \''
b'-            \'"-S aext:ARG0,abr -x --audio-format ARG0". All defined aliases are listed in the --help output. \''
b"-            'Alias options can trigger more aliases; so be careful to avoid defining recursive options. '"
b"+            u'Options that can help keep compatibility with youtube-dl or youtube-dlc '"
b"+            u'configurations by reverting some of the changes made in yt-dlp. '"
b'+            u\'See "Differences in default behavior" for details\'))'
b'+    general.add_option('
b"+        u'--alias', metavar=u'ALIASES OPTIONS', dest=u'_', type=u'str', nargs=2,"
b"+        action=u'callback', callback=_create_alias,"
b'+        help=('
b'+            u\'Create aliases for an option string. Unless an alias starts with a dash "-", it is prefixed with "--". \''
b"+            u'Arguments are parsed according to the Python string formatting mini-language. '"
b'+            u\'E.g. --alias get-audio,-X "-S aext:{0},abr -x --audio-format {0}" creates options \''
b'+            u\'"--get-audio" and "-X" that takes an argument (ARG0) and expands to \''
b'+            u\'"-S aext:ARG0,abr -x --audio-format ARG0". All defined aliases are listed in the --help output. \''
b"+            u'Alias options can trigger more aliases; so be careful to avoid defining recursive options. '"
b"             f'As a safety measure, each alias may be triggered a maximum of {_YoutubeDLOptionParser.ALIAS_TRIGGER_LIMIT} times. '"
b"-            'This option can be used multiple times'))"
b'-    general.add_option('
b"-        '-t', '--preset-alias',"
b"-        metavar='PRESET', dest='_', type='str',"
b"-        action='callback', callback=_preset_alias_callback,"
b'-        help=('
b"-            'Applies a predefined set of options. e.g. --preset-alias mp3. '"
b"+            u'This option can be used multiple times'))"
b'+    general.add_option('
b"+        u'-t', u'--preset-alias',"
b"+        metavar=u'PRESET', dest=u'_', type=u'str',"
b"+        action=u'callback', callback=_preset_alias_callback,"
b'+        help=('
b"+            u'Applies a predefined set of options. e.g. --preset-alias mp3. '"
b'             f\'The following presets are available: {", ".join(_PRESET_ALIASES)}. \''
b'-            \'See the "Preset Aliases" section at the end for more info. \''
b"-            'This option can be used multiple times'))"
b'-'
b"-    network = optparse.OptionGroup(parser, 'Network Options')"
b'+            u\'See the "Preset Aliases" section at the end for more info. \''
b"+            u'This option can be used multiple times'))"
b'+'
b"+    network = optparse.OptionGroup(parser, u'Network Options')"
b'     network.add_option('
b"-        '--proxy', dest='proxy',"
b"-        default=None, metavar='URL',"
b'-        help=('
b"-            'Use the specified HTTP/HTTPS/SOCKS proxy. To enable SOCKS proxy, specify a proper scheme, '"
b'-            \'e.g. socks5://user:pass@127.0.0.1:1080/. Pass in an empty string (--proxy "") for direct connection\'))'
b"+        u'--proxy', dest=u'proxy',"
b"+        default=None, metavar=u'URL',"
b'+        help=('
b"+            u'Use the specified HTTP/HTTPS/SOCKS proxy. To enable SOCKS proxy, specify a proper scheme, '"
b'+            u\'e.g. socks5://user:pass@127.0.0.1:1080/. Pass in an empty string (--proxy "") for direct connection\'))'
b'     network.add_option('
b"-        '--socket-timeout',"
b"-        dest='socket_timeout', type=float, default=None, metavar='SECONDS',"
b"-        help='Time to wait before giving up, in seconds')"
b"+        u'--socket-timeout',"
b"+        dest=u'socket_timeout', type=float, default=None, metavar=u'SECONDS',"
b"+        help=u'Time to wait before giving up, in seconds')"
b'     network.add_option('
b"-        '--source-address',"
b"-        metavar='IP', dest='source_address', default=None,"
b"-        help='Client-side IP address to bind to',"
b"+        u'--source-address',"
b"+        metavar=u'IP', dest=u'source_address', default=None,"
b"+        help=u'Client-side IP address to bind to',"
b'     )'
b'     network.add_option('
b"-        '--impersonate',"
b"-        metavar='CLIENT[:OS]', dest='impersonate', default=None,"
b'-        help=('
b"-            'Client to impersonate for requests. E.g. chrome, chrome-110, chrome:windows-10. '"
b'-            \'Pass --impersonate="" to impersonate any client. Note that forcing impersonation \''
b"-            'for all requests may have a detrimental impact on download speed and stability'),"
b"+        u'--impersonate',"
b"+        metavar=u'CLIENT[:OS]', dest=u'impersonate', default=None,"
b'+        help=('
b"+            u'Client to impersonate for requests. E.g. chrome, chrome-110, chrome:windows-10. '"
b'+            u\'Pass --impersonate="" to impersonate any client. Note that forcing impersonation \''
b"+            u'for all requests may have a detrimental impact on download speed and stability'),"
b'     )'
b'     network.add_option('
b"-        '--list-impersonate-targets',"
b"-        dest='list_impersonate_targets', default=False, action='store_true',"
b"-        help='List available clients to impersonate.',"
b"+        u'--list-impersonate-targets',"
b"+        dest=u'list_impersonate_targets', default=False, action=u'store_true',"
b"+        help=u'List available clients to impersonate.',"
b'     )'
b'     network.add_option('
b"-        '-4', '--force-ipv4',"
b"-        action='store_const', const='0.0.0.0', dest='source_address',"
b"-        help='Make all connections via IPv4',"
b"+        u'-4', u'--force-ipv4',"
b"+        action=u'store_const', const=u'0.0.0.0', dest=u'source_address',"
b"+        help=u'Make all connections via IPv4',"
b'     )'
b'     network.add_option('
b"-        '-6', '--force-ipv6',"
b"-        action='store_const', const='::', dest='source_address',"
b"-        help='Make all connections via IPv6',"
b"+        u'-6', u'--force-ipv6',"
b"+        action=u'store_const', const=u'::', dest=u'source_address',"
b"+        help=u'Make all connections via IPv6',"
b'     )'
b'     network.add_option('
b"-        '--enable-file-urls', action='store_true',"
b"-        dest='enable_file_urls', default=False,"
b"-        help='Enable file:// URLs. This is disabled by default for security reasons.',"
b"+        u'--enable-file-urls', action=u'store_true',"
b"+        dest=u'enable_file_urls', default=False,"
b"+        help=u'Enable file:// URLs. This is disabled by default for security reasons.',"
b'     )'
b' '
b"-    geo = optparse.OptionGroup(parser, 'Geo-restriction')"
b"+    geo = optparse.OptionGroup(parser, u'Geo-restriction')"
b'     geo.add_option('
b"-        '--geo-verification-proxy',"
b"-        dest='geo_verification_proxy', default=None, metavar='URL',"
b'-        help=('
b"-            'Use this proxy to verify the IP address for some geo-restricted sites. '"
b"-            'The default proxy specified by --proxy (or none, if the option is not present) is used for the actual downloading'))"
b"+        u'--geo-verification-proxy',"
b"+        dest=u'geo_verification_proxy', default=None, metavar=u'URL',"
b'+        help=('
b"+            u'Use this proxy to verify the IP address for some geo-restricted sites. '"
b"+            u'The default proxy specified by --proxy (or none, if the option is not present) is used for the actual downloading'))"
b'     geo.add_option('
b"-        '--cn-verification-proxy',"
b"-        dest='cn_verification_proxy', default=None, metavar='URL',"
b"+        u'--cn-verification-proxy',"
b"+        dest=u'cn_verification_proxy', default=None, metavar=u'URL',"
b'         help=optparse.SUPPRESS_HELP)'
b'     geo.add_option('
b"-        '--xff', metavar='VALUE',"
b"-        dest='geo_bypass', default='default',"
b'-        help=('
b"-            'How to fake X-Forwarded-For HTTP header to try bypassing geographic restriction. '"
b'-            \'One of "default" (only when known to be useful), "never", \''
b"-            'an IP block in CIDR notation, or a two-letter ISO 3166-2 country code'))"
b"+        u'--xff', metavar=u'VALUE',"
b"+        dest=u'geo_bypass', default=u'default',"
b'+        help=('
b"+            u'How to fake X-Forwarded-For HTTP header to try bypassing geographic restriction. '"
b'+            u\'One of "default" (only when known to be useful), "never", \''
b"+            u'an IP block in CIDR notation, or a two-letter ISO 3166-2 country code'))"
b'     geo.add_option('
b"-        '--geo-bypass',"
b"-        action='store_const', dest='geo_bypass', const='default',"
b"+        u'--geo-bypass',"
b"+        action=u'store_const', dest=u'geo_bypass', const=u'default',"
b'         help=optparse.SUPPRESS_HELP)'
b'     geo.add_option('
b"-        '--no-geo-bypass',"
b"-        action='store_const', dest='geo_bypass', const='never',"
b"+        u'--no-geo-bypass',"
b"+        action=u'store_const', dest=u'geo_bypass', const=u'never',"
b'         help=optparse.SUPPRESS_HELP)'
b'     geo.add_option('
b"-        '--geo-bypass-country', metavar='CODE', dest='geo_bypass',"
b"+        u'--geo-bypass-country', metavar=u'CODE', dest=u'geo_bypass',"
b'         help=optparse.SUPPRESS_HELP)'
b'     geo.add_option('
b"-        '--geo-bypass-ip-block', metavar='IP_BLOCK', dest='geo_bypass',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-'
b"-    selection = optparse.OptionGroup(parser, 'Video Selection')"
b'-    selection.add_option('
b"-        '--playlist-start',"
b"-        dest='playliststart', metavar='NUMBER', default=1, type=int,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    selection.add_option('
b"-        '--playlist-end',"
b"-        dest='playlistend', metavar='NUMBER', default=None, type=int,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    selection.add_option('
b"-        '-I', '--playlist-items',"
b"-        dest='playlist_items', metavar='ITEM_SPEC', default=None,"
b'-        help=('
b"-            'Comma separated playlist_index of the items to download. '"
b'-            \'You can specify a range using "[START]:[STOP][:STEP]". For backward compatibility, START-STOP is also supported. \''
b"-            'Use negative indices to count from the right and negative STEP to download in reverse order. '"
b'-            \'E.g. "-I 1:3,7,-5::2" used on a playlist of size 15 will download the items at index 1,2,3,7,11,13,15\'))'
b'-    selection.add_option('
b"-        '--match-title',"
b"-        dest='matchtitle', metavar='REGEX',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    selection.add_option('
b"-        '--reject-title',"
b"-        dest='rejecttitle', metavar='REGEX',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    selection.add_option('
b"-        '--min-filesize',"
b"-        metavar='SIZE', dest='min_filesize', default=None,"
b"-        help='Abort download if filesize is smaller than SIZE, e.g. 50k or 44.6M')"
b'-    selection.add_option('
b"-        '--max-filesize',"
b"-        metavar='SIZE', dest='max_filesize', default=None,"
b"-        help='Abort download if filesize is larger than SIZE, e.g. 50k or 44.6M')"
b'-    selection.add_option('
b"-        '--date',"
b"-        metavar='DATE', dest='date', default=None,"
b'-        help=('
b"-            'Download only videos uploaded on this date. '"
b'-            \'The date can be "YYYYMMDD" or in the format [now|today|yesterday][-N[day|week|month|year]]. \''
b'-            \'E.g. "--date today-2weeks" downloads only videos uploaded on the same day two weeks ago\'))'
b'-    selection.add_option('
b"-        '--datebefore',"
b"-        metavar='DATE', dest='datebefore', default=None,"
b'-        help=('
b"-            'Download only videos uploaded on or before this date. '"
b"-            'The date formats accepted are the same as --date'))"
b'-    selection.add_option('
b"-        '--dateafter',"
b"-        metavar='DATE', dest='dateafter', default=None,"
b'-        help=('
b"-            'Download only videos uploaded on or after this date. '"
b"-            'The date formats accepted are the same as --date'))"
b'-    selection.add_option('
b"-        '--min-views',"
b"-        metavar='COUNT', dest='min_views', default=None, type=int,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    selection.add_option('
b"-        '--max-views',"
b"-        metavar='COUNT', dest='max_views', default=None, type=int,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    selection.add_option('
b"-        '--match-filters',"
b"-        metavar='FILTER', dest='match_filter', action='append',"
b'-        help=('
b'-            \'Generic video filter. Any "OUTPUT TEMPLATE" field can be compared with a \''
b'-            \'number or a string using the operators defined in "Filtering Formats". \''
b"-            'You can also simply specify a field to match if the field is present, '"
b'-            \'use "!field" to check if the field is not present, and "&" to check multiple conditions. \''
b'-            \'Use a "\\\\" to escape "&" or quotes if needed. If used multiple times, \''
b"-            'the filter matches if at least one of the conditions is met. E.g. --match-filters '"
b'-            \'!is_live --match-filters "like_count>?100 & description~=\\\'(?i)\\\\bcats \\\\& dogs\\\\b\\\'" \''
b"-            'matches only videos that are not live OR those that have a like count more than 100 '"
b"-            '(or the like field is not available) and also has a description '"
b'-            \'that contains the phrase "cats & dogs" (caseless). \''
b'-            \'Use "--match-filters -" to interactively ask whether to download each video\'))'
b'-    selection.add_option('
b"-        '--no-match-filters',"
b"-        dest='match_filter', action='store_const', const=None,"
b"-        help='Do not use any --match-filters (default)')"
b'-    selection.add_option('
b"-        '--break-match-filters',"
b"-        metavar='FILTER', dest='breaking_match_filter', action='append',"
b'-        help=\'Same as "--match-filters" but stops the download process when a video is rejected\')'
b'-    selection.add_option('
b"-        '--no-break-match-filters',"
b"-        dest='breaking_match_filter', action='store_const', const=None,"
b"-        help='Do not use any --break-match-filters (default)')"
b'-    selection.add_option('
b"-        '--no-playlist',"
b"-        action='store_true', dest='noplaylist', default=False,"
b"-        help='Download only the video, if the URL refers to a video and a playlist')"
b'-    selection.add_option('
b"-        '--yes-playlist',"
b"-        action='store_false', dest='noplaylist',"
b"-        help='Download the playlist, if the URL refers to a video and a playlist')"
b'-    selection.add_option('
b"-        '--age-limit',"
b"-        metavar='YEARS', dest='age_limit', default=None, type=int,"
b"-        help='Download only videos suitable for the given age')"
b'-    selection.add_option('
b"-        '--download-archive', metavar='FILE',"
b"-        dest='download_archive',"
b"-        help='Download only videos not listed in the archive file. Record the IDs of all downloaded videos in it')"
b'-    selection.add_option('
b"-        '--no-download-archive',"
b"-        dest='download_archive', action='store_const', const=None,"
b"-        help='Do not use archive file (default)')"
b'-    selection.add_option('
b"-        '--max-downloads',"
b"-        dest='max_downloads', metavar='NUMBER', type=int, default=None,"
b"-        help='Abort after downloading NUMBER files')"
b'-    selection.add_option('
b"-        '--break-on-existing',"
b"-        action='store_true', dest='break_on_existing', default=False,"
b"-        help='Stop the download process when encountering a file that is in the archive '"
b"-             'supplied with the --download-archive option')"
b'-    selection.add_option('
b"-        '--no-break-on-existing',"
b"-        action='store_false', dest='break_on_existing',"
b"-        help='Do not stop the download process when encountering a file that is in the archive (default)')"
b'-    selection.add_option('
b"-        '--break-on-reject',"
b"-        action='store_true', dest='break_on_reject', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    selection.add_option('
b"-        '--break-per-input',"
b"-        action='store_true', dest='break_per_url', default=False,"
b"-        help='Alters --max-downloads, --break-on-existing, --break-match-filters, and autonumber to reset per input URL')"
b'-    selection.add_option('
b"-        '--no-break-per-input',"
b"-        action='store_false', dest='break_per_url',"
b"-        help='--break-on-existing and similar options terminates the entire download queue')"
b'-    selection.add_option('
b"-        '--skip-playlist-after-errors', metavar='N',"
b"-        dest='skip_playlist_after_errors', default=None, type=int,"
b"-        help='Number of allowed failures until the rest of the playlist is skipped')"
b'-    selection.add_option('
b"-        '--include-ads',"
b"-        dest='include_ads', action='store_true',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    selection.add_option('
b"-        '--no-include-ads',"
b"-        dest='include_ads', action='store_false',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-'
b"-    authentication = optparse.OptionGroup(parser, 'Authentication Options')"
b"+        u'--geo-bypass-ip-block', metavar=u'IP_BLOCK', dest=u'geo_bypass',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+'
b"+    selection = optparse.OptionGroup(parser, u'Video Selection')"
b'+    selection.add_option('
b"+        u'--playlist-start',"
b"+        dest=u'playliststart', metavar=u'NUMBER', default=1, type=int,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    selection.add_option('
b"+        u'--playlist-end',"
b"+        dest=u'playlistend', metavar=u'NUMBER', default=None, type=int,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    selection.add_option('
b"+        u'-I', u'--playlist-items',"
b"+        dest=u'playlist_items', metavar=u'ITEM_SPEC', default=None,"
b'+        help=('
b"+            u'Comma separated playlist_index of the items to download. '"
b'+            u\'You can specify a range using "[START]:[STOP][:STEP]". For backward compatibility, START-STOP is also supported. \''
b"+            u'Use negative indices to count from the right and negative STEP to download in reverse order. '"
b'+            u\'E.g. "-I 1:3,7,-5::2" used on a playlist of size 15 will download the items at index 1,2,3,7,11,13,15\'))'
b'+    selection.add_option('
b"+        u'--match-title',"
b"+        dest=u'matchtitle', metavar=u'REGEX',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    selection.add_option('
b"+        u'--reject-title',"
b"+        dest=u'rejecttitle', metavar=u'REGEX',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    selection.add_option('
b"+        u'--min-filesize',"
b"+        metavar=u'SIZE', dest=u'min_filesize', default=None,"
b"+        help=u'Abort download if filesize is smaller than SIZE, e.g. 50k or 44.6M')"
b'+    selection.add_option('
b"+        u'--max-filesize',"
b"+        metavar=u'SIZE', dest=u'max_filesize', default=None,"
b"+        help=u'Abort download if filesize is larger than SIZE, e.g. 50k or 44.6M')"
b'+    selection.add_option('
b"+        u'--date',"
b"+        metavar=u'DATE', dest=u'date', default=None,"
b'+        help=('
b"+            u'Download only videos uploaded on this date. '"
b'+            u\'The date can be "YYYYMMDD" or in the format [now|today|yesterday][-N[day|week|month|year]]. \''
b'+            u\'E.g. "--date today-2weeks" downloads only videos uploaded on the same day two weeks ago\'))'
b'+    selection.add_option('
b"+        u'--datebefore',"
b"+        metavar=u'DATE', dest=u'datebefore', default=None,"
b'+        help=('
b"+            u'Download only videos uploaded on or before this date. '"
b"+            u'The date formats accepted are the same as --date'))"
b'+    selection.add_option('
b"+        u'--dateafter',"
b"+        metavar=u'DATE', dest=u'dateafter', default=None,"
b'+        help=('
b"+            u'Download only videos uploaded on or after this date. '"
b"+            u'The date formats accepted are the same as --date'))"
b'+    selection.add_option('
b"+        u'--min-views',"
b"+        metavar=u'COUNT', dest=u'min_views', default=None, type=int,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    selection.add_option('
b"+        u'--max-views',"
b"+        metavar=u'COUNT', dest=u'max_views', default=None, type=int,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    selection.add_option('
b"+        u'--match-filters',"
b"+        metavar=u'FILTER', dest=u'match_filter', action=u'append',"
b'+        help=('
b'+            u\'Generic video filter. Any "OUTPUT TEMPLATE" field can be compared with a \''
b'+            u\'number or a string using the operators defined in "Filtering Formats". \''
b"+            u'You can also simply specify a field to match if the field is present, '"
b'+            u\'use "!field" to check if the field is not present, and "&" to check multiple conditions. \''
b'+            u\'Use a "\\\\" to escape "&" or quotes if needed. If used multiple times, \''
b"+            u'the filter matches if at least one of the conditions is met. E.g. --match-filters '"
b'+            u\'!is_live --match-filters "like_count>?100 & description~=\\\'(?i)\\\\bcats \\\\& dogs\\\\b\\\'" \''
b"+            u'matches only videos that are not live OR those that have a like count more than 100 '"
b"+            u'(or the like field is not available) and also has a description '"
b'+            u\'that contains the phrase "cats & dogs" (caseless). \''
b'+            u\'Use "--match-filters -" to interactively ask whether to download each video\'))'
b'+    selection.add_option('
b"+        u'--no-match-filters',"
b"+        dest=u'match_filter', action=u'store_const', const=None,"
b"+        help=u'Do not use any --match-filters (default)')"
b'+    selection.add_option('
b"+        u'--break-match-filters',"
b"+        metavar=u'FILTER', dest=u'breaking_match_filter', action=u'append',"
b'+        help=u\'Same as "--match-filters" but stops the download process when a video is rejected\')'
b'+    selection.add_option('
b"+        u'--no-break-match-filters',"
b"+        dest=u'breaking_match_filter', action=u'store_const', const=None,"
b"+        help=u'Do not use any --break-match-filters (default)')"
b'+    selection.add_option('
b"+        u'--no-playlist',"
b"+        action=u'store_true', dest=u'noplaylist', default=False,"
b"+        help=u'Download only the video, if the URL refers to a video and a playlist')"
b'+    selection.add_option('
b"+        u'--yes-playlist',"
b"+        action=u'store_false', dest=u'noplaylist',"
b"+        help=u'Download the playlist, if the URL refers to a video and a playlist')"
b'+    selection.add_option('
b"+        u'--age-limit',"
b"+        metavar=u'YEARS', dest=u'age_limit', default=None, type=int,"
b"+        help=u'Download only videos suitable for the given age')"
b'+    selection.add_option('
b"+        u'--download-archive', metavar=u'FILE',"
b"+        dest=u'download_archive',"
b"+        help=u'Download only videos not listed in the archive file. Record the IDs of all downloaded videos in it')"
b'+    selection.add_option('
b"+        u'--no-download-archive',"
b"+        dest=u'download_archive', action=u'store_const', const=None,"
b"+        help=u'Do not use archive file (default)')"
b'+    selection.add_option('
b"+        u'--max-downloads',"
b"+        dest=u'max_downloads', metavar=u'NUMBER', type=int, default=None,"
b"+        help=u'Abort after downloading NUMBER files')"
b'+    selection.add_option('
b"+        u'--break-on-existing',"
b"+        action=u'store_true', dest=u'break_on_existing', default=False,"
b"+        help=u'Stop the download process when encountering a file that is in the archive '"
b"+             u'supplied with the --download-archive option')"
b'+    selection.add_option('
b"+        u'--no-break-on-existing',"
b"+        action=u'store_false', dest=u'break_on_existing',"
b"+        help=u'Do not stop the download process when encountering a file that is in the archive (default)')"
b'+    selection.add_option('
b"+        u'--break-on-reject',"
b"+        action=u'store_true', dest=u'break_on_reject', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    selection.add_option('
b"+        u'--break-per-input',"
b"+        action=u'store_true', dest=u'break_per_url', default=False,"
b"+        help=u'Alters --max-downloads, --break-on-existing, --break-match-filters, and autonumber to reset per input URL')"
b'+    selection.add_option('
b"+        u'--no-break-per-input',"
b"+        action=u'store_false', dest=u'break_per_url',"
b"+        help=u'--break-on-existing and similar options terminates the entire download queue')"
b'+    selection.add_option('
b"+        u'--skip-playlist-after-errors', metavar=u'N',"
b"+        dest=u'skip_playlist_after_errors', default=None, type=int,"
b"+        help=u'Number of allowed failures until the rest of the playlist is skipped')"
b'+    selection.add_option('
b"+        u'--include-ads',"
b"+        dest=u'include_ads', action=u'store_true',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    selection.add_option('
b"+        u'--no-include-ads',"
b"+        dest=u'include_ads', action=u'store_false',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+'
b"+    authentication = optparse.OptionGroup(parser, u'Authentication Options')"
b'     authentication.add_option('
b"-        '-u', '--username',"
b"-        dest='username', metavar='USERNAME',"
b"-        help='Login with this account ID')"
b"+        u'-u', u'--username',"
b"+        dest=u'username', metavar=u'USERNAME',"
b"+        help=u'Login with this account ID')"
b'     authentication.add_option('
b"-        '-p', '--password',"
b"-        dest='password', metavar='PASSWORD',"
b"-        help='Account password. If this option is left out, yt-dlp will ask interactively')"
b"+        u'-p', u'--password',"
b"+        dest=u'password', metavar=u'PASSWORD',"
b"+        help=u'Account password. If this option is left out, yt-dlp will ask interactively')"
b'     authentication.add_option('
b"-        '-2', '--twofactor',"
b"-        dest='twofactor', metavar='TWOFACTOR',"
b"-        help='Two-factor authentication code')"
b"+        u'-2', u'--twofactor',"
b"+        dest=u'twofactor', metavar=u'TWOFACTOR',"
b"+        help=u'Two-factor authentication code')"
b'     authentication.add_option('
b"-        '-n', '--netrc',"
b"-        action='store_true', dest='usenetrc', default=False,"
b"-        help='Use .netrc authentication data')"
b"+        u'-n', u'--netrc',"
b"+        action=u'store_true', dest=u'usenetrc', default=False,"
b"+        help=u'Use .netrc authentication data')"
b'     authentication.add_option('
b"-        '--netrc-location',"
b"-        dest='netrc_location', metavar='PATH',"
b"-        help='Location of .netrc authentication data; either the path or its containing directory. Defaults to ~/.netrc')"
b"+        u'--netrc-location',"
b"+        dest=u'netrc_location', metavar=u'PATH',"
b"+        help=u'Location of .netrc authentication data; either the path or its containing directory. Defaults to ~/.netrc')"
b'     authentication.add_option('
b"-        '--netrc-cmd',"
b"-        dest='netrc_cmd', metavar='NETRC_CMD',"
b"-        help='Command to execute to get the credentials for an extractor.')"
b"+        u'--netrc-cmd',"
b"+        dest=u'netrc_cmd', metavar=u'NETRC_CMD',"
b"+        help=u'Command to execute to get the credentials for an extractor.')"
b'     authentication.add_option('
b"-        '--video-password',"
b"-        dest='videopassword', metavar='PASSWORD',"
b"-        help='Video-specific password')"
b"+        u'--video-password',"
b"+        dest=u'videopassword', metavar=u'PASSWORD',"
b"+        help=u'Video-specific password')"
b'     authentication.add_option('
b"-        '--ap-mso',"
b"-        dest='ap_mso', metavar='MSO',"
b"-        help='Adobe Pass multiple-system operator (TV provider) identifier, use --ap-list-mso for a list of available MSOs')"
b"+        u'--ap-mso',"
b"+        dest=u'ap_mso', metavar=u'MSO',"
b"+        help=u'Adobe Pass multiple-system operator (TV provider) identifier, use --ap-list-mso for a list of available MSOs')"
b'     authentication.add_option('
b"-        '--ap-username',"
b"-        dest='ap_username', metavar='USERNAME',"
b"-        help='Multiple-system operator account login')"
b"+        u'--ap-username',"
b"+        dest=u'ap_username', metavar=u'USERNAME',"
b"+        help=u'Multiple-system operator account login')"
b'     authentication.add_option('
b"-        '--ap-password',"
b"-        dest='ap_password', metavar='PASSWORD',"
b"-        help='Multiple-system operator account password. If this option is left out, yt-dlp will ask interactively')"
b"+        u'--ap-password',"
b"+        dest=u'ap_password', metavar=u'PASSWORD',"
b"+        help=u'Multiple-system operator account password. If this option is left out, yt-dlp will ask interactively')"
b'     authentication.add_option('
b"-        '--ap-list-mso',"
b"-        action='store_true', dest='ap_list_mso', default=False,"
b"-        help='List all supported multiple-system operators')"
b"+        u'--ap-list-mso',"
b"+        action=u'store_true', dest=u'ap_list_mso', default=False,"
b"+        help=u'List all supported multiple-system operators')"
b'     authentication.add_option('
b"-        '--client-certificate',"
b"-        dest='client_certificate', metavar='CERTFILE',"
b"-        help='Path to client certificate file in PEM format. May include the private key')"
b"+        u'--client-certificate',"
b"+        dest=u'client_certificate', metavar=u'CERTFILE',"
b"+        help=u'Path to client certificate file in PEM format. May include the private key')"
b'     authentication.add_option('
b"-        '--client-certificate-key',"
b"-        dest='client_certificate_key', metavar='KEYFILE',"
b"-        help='Path to private key file for client certificate')"
b"+        u'--client-certificate-key',"
b"+        dest=u'client_certificate_key', metavar=u'KEYFILE',"
b"+        help=u'Path to private key file for client certificate')"
b'     authentication.add_option('
b"-        '--client-certificate-password',"
b"-        dest='client_certificate_password', metavar='PASSWORD',"
b"-        help='Password for client certificate private key, if encrypted. '"
b"-             'If not provided, and the key is encrypted, yt-dlp will ask interactively')"
b'-'
b"-    video_format = optparse.OptionGroup(parser, 'Video Format Options')"
b"+        u'--client-certificate-password',"
b"+        dest=u'client_certificate_password', metavar=u'PASSWORD',"
b"+        help=u'Password for client certificate private key, if encrypted. '"
b"+             u'If not provided, and the key is encrypted, yt-dlp will ask interactively')"
b'+'
b"+    video_format = optparse.OptionGroup(parser, u'Video Format Options')"
b'     video_format.add_option('
b"-        '-f', '--format',"
b"-        action='store', dest='format', metavar='FORMAT', default=None,"
b'-        help=\'Video format code, see "FORMAT SELECTION" for more details\')'
b"+        u'-f', u'--format',"
b"+        action=u'store', dest=u'format', metavar=u'FORMAT', default=None,"
b'+        help=u\'Video format code, see "FORMAT SELECTION" for more details\')'
b'     video_format.add_option('
b"-        '-S', '--format-sort', metavar='SORTORDER',"
b"-        dest='format_sort', default=[], type='str', action='callback',"
b"-        callback=_list_from_options_callback, callback_kwargs={'append': -1},"
b'-        help=\'Sort the formats by the fields given, see "Sorting Formats" for more details\')'
b"+        u'-S', u'--format-sort', metavar=u'SORTORDER',"
b"+        dest=u'format_sort', default=[], type=u'str', action=u'callback',"
b"+        callback=_list_from_options_callback, callback_kwargs={u'append': -1},"
b'+        help=u\'Sort the formats by the fields given, see "Sorting Formats" for more details\')'
b'     video_format.add_option('
b"-        '--format-sort-force', '--S-force',"
b"-        action='store_true', dest='format_sort_force', metavar='FORMAT', default=False,"
b'-        help=('
b"-            'Force user specified sort order to have precedence over all fields, '"
b'-            \'see "Sorting Formats" for more details (Alias: --S-force)\'))'
b"+        u'--format-sort-force', u'--S-force',"
b"+        action=u'store_true', dest=u'format_sort_force', metavar=u'FORMAT', default=False,"
b'+        help=('
b"+            u'Force user specified sort order to have precedence over all fields, '"
b'+            u\'see "Sorting Formats" for more details (Alias: --S-force)\'))'
b'     video_format.add_option('
b"-        '--no-format-sort-force',"
b"-        action='store_false', dest='format_sort_force', metavar='FORMAT', default=False,"
b"-        help='Some fields have precedence over the user specified sort order (default)')"
b"+        u'--no-format-sort-force',"
b"+        action=u'store_false', dest=u'format_sort_force', metavar=u'FORMAT', default=False,"
b"+        help=u'Some fields have precedence over the user specified sort order (default)')"
b'     video_format.add_option('
b"-        '--video-multistreams',"
b"-        action='store_true', dest='allow_multiple_video_streams', default=None,"
b"-        help='Allow multiple video streams to be merged into a single file')"
b"+        u'--video-multistreams',"
b"+        action=u'store_true', dest=u'allow_multiple_video_streams', default=None,"
b"+        help=u'Allow multiple video streams to be merged into a single file')"
b'     video_format.add_option('
b"-        '--no-video-multistreams',"
b"-        action='store_false', dest='allow_multiple_video_streams',"
b"-        help='Only one video stream is downloaded for each output file (default)')"
b"+        u'--no-video-multistreams',"
b"+        action=u'store_false', dest=u'allow_multiple_video_streams',"
b"+        help=u'Only one video stream is downloaded for each output file (default)')"
b'     video_format.add_option('
b"-        '--audio-multistreams',"
b"-        action='store_true', dest='allow_multiple_audio_streams', default=None,"
b"-        help='Allow multiple audio streams to be merged into a single file')"
b"+        u'--audio-multistreams',"
b"+        action=u'store_true', dest=u'allow_multiple_audio_streams', default=None,"
b"+        help=u'Allow multiple audio streams to be merged into a single file')"
b'     video_format.add_option('
b"-        '--no-audio-multistreams',"
b"-        action='store_false', dest='allow_multiple_audio_streams',"
b"-        help='Only one audio stream is downloaded for each output file (default)')"
b"+        u'--no-audio-multistreams',"
b"+        action=u'store_false', dest=u'allow_multiple_audio_streams',"
b"+        help=u'Only one audio stream is downloaded for each output file (default)')"
b'     video_format.add_option('
b"-        '--all-formats',"
b"-        action='store_const', dest='format', const='all',"
b"+        u'--all-formats',"
b"+        action=u'store_const', dest=u'format', const=u'all',"
b'         help=optparse.SUPPRESS_HELP)'
b'     video_format.add_option('
b"-        '--prefer-free-formats',"
b"-        action='store_true', dest='prefer_free_formats', default=False,"
b'-        help=('
b"-            'Prefer video formats with free containers over non-free ones of the same quality. '"
b'-            \'Use with "-S ext" to strictly prefer free containers irrespective of quality\'))'
b"+        u'--prefer-free-formats',"
b"+        action=u'store_true', dest=u'prefer_free_formats', default=False,"
b'+        help=('
b"+            u'Prefer video formats with free containers over non-free ones of the same quality. '"
b'+            u\'Use with "-S ext" to strictly prefer free containers irrespective of quality\'))'
b'     video_format.add_option('
b"-        '--no-prefer-free-formats',"
b"-        action='store_false', dest='prefer_free_formats', default=False,"
b'-        help="Don\'t give any special preference to free containers (default)")'
b"+        u'--no-prefer-free-formats',"
b"+        action=u'store_false', dest=u'prefer_free_formats', default=False,"
b'+        help=u"Don\'t give any special preference to free containers (default)")'
b'     video_format.add_option('
b"-        '--check-formats',"
b"-        action='store_const', const='selected', dest='check_formats', default=None,"
b"-        help='Make sure formats are selected only from those that are actually downloadable')"
b"+        u'--check-formats',"
b"+        action=u'store_const', const=u'selected', dest=u'check_formats', default=None,"
b"+        help=u'Make sure formats are selected only from those that are actually downloadable')"
b'     video_format.add_option('
b"-        '--check-all-formats',"
b"-        action='store_true', dest='check_formats',"
b"-        help='Check all formats for whether they are actually downloadable')"
b"+        u'--check-all-formats',"
b"+        action=u'store_true', dest=u'check_formats',"
b"+        help=u'Check all formats for whether they are actually downloadable')"
b'     video_format.add_option('
b"-        '--no-check-formats',"
b"-        action='store_false', dest='check_formats',"
b"-        help='Do not check that the formats are actually downloadable')"
b"+        u'--no-check-formats',"
b"+        action=u'store_false', dest=u'check_formats',"
b"+        help=u'Do not check that the formats are actually downloadable')"
b'     video_format.add_option('
b"-        '-F', '--list-formats',"
b"-        action='store_true', dest='listformats',"
b"-        help='List available formats of each video. Simulate unless --no-simulate is used')"
b"+        u'-F', u'--list-formats',"
b"+        action=u'store_true', dest=u'listformats',"
b"+        help=u'List available formats of each video. Simulate unless --no-simulate is used')"
b'     video_format.add_option('
b"-        '--list-formats-as-table',"
b"-        action='store_true', dest='listformats_table', default=True,"
b"+        u'--list-formats-as-table',"
b"+        action=u'store_true', dest=u'listformats_table', default=True,"
b'         help=optparse.SUPPRESS_HELP)'
b'     video_format.add_option('
b"-        '--list-formats-old', '--no-list-formats-as-table',"
b"-        action='store_false', dest='listformats_table',"
b"+        u'--list-formats-old', u'--no-list-formats-as-table',"
b"+        action=u'store_false', dest=u'listformats_table',"
b'         help=optparse.SUPPRESS_HELP)'
b'     video_format.add_option('
b"-        '--merge-output-format',"
b"-        action='store', dest='merge_output_format', metavar='FORMAT', default=None,"
b'-        help=('
b'-            \'Containers that may be used when merging formats, separated by "/", e.g. "mp4/mkv". \''
b"-            'Ignored if no merge is required. '"
b"+        u'--merge-output-format',"
b"+        action=u'store', dest=u'merge_output_format', metavar=u'FORMAT', default=None,"
b'+        help=('
b'+            u\'Containers that may be used when merging formats, separated by "/", e.g. "mp4/mkv". \''
b"+            u'Ignored if no merge is required. '"
b'             f\'(currently supported: {", ".join(sorted(FFmpegMergerPP.SUPPORTED_EXTS))})\'))'
b'     video_format.add_option('
b"-        '--allow-unplayable-formats',"
b"-        action='store_true', dest='allow_unplayable_formats', default=False,"
b"+        u'--allow-unplayable-formats',"
b"+        action=u'store_true', dest=u'allow_unplayable_formats', default=False,"
b'         help=optparse.SUPPRESS_HELP)'
b'     video_format.add_option('
b"-        '--no-allow-unplayable-formats',"
b"-        action='store_false', dest='allow_unplayable_formats',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-'
b"-    subtitles = optparse.OptionGroup(parser, 'Subtitle Options')"
b"+        u'--no-allow-unplayable-formats',"
b"+        action=u'store_false', dest=u'allow_unplayable_formats',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+'
b"+    subtitles = optparse.OptionGroup(parser, u'Subtitle Options')"
b'     subtitles.add_option('
b"-        '--write-subs', '--write-srt',"
b"-        action='store_true', dest='writesubtitles', default=False,"
b"-        help='Write subtitle file')"
b"+        u'--write-subs', u'--write-srt',"
b"+        action=u'store_true', dest=u'writesubtitles', default=False,"
b"+        help=u'Write subtitle file')"
b'     subtitles.add_option('
b"-        '--no-write-subs', '--no-write-srt',"
b"-        action='store_false', dest='writesubtitles',"
b"-        help='Do not write subtitle file (default)')"
b"+        u'--no-write-subs', u'--no-write-srt',"
b"+        action=u'store_false', dest=u'writesubtitles',"
b"+        help=u'Do not write subtitle file (default)')"
b'     subtitles.add_option('
b"-        '--write-auto-subs', '--write-automatic-subs',"
b"-        action='store_true', dest='writeautomaticsub', default=False,"
b"-        help='Write automatically generated subtitle file (Alias: --write-automatic-subs)')"
b"+        u'--write-auto-subs', u'--write-automatic-subs',"
b"+        action=u'store_true', dest=u'writeautomaticsub', default=False,"
b"+        help=u'Write automatically generated subtitle file (Alias: --write-automatic-subs)')"
b'     subtitles.add_option('
b"-        '--no-write-auto-subs', '--no-write-automatic-subs',"
b"-        action='store_false', dest='writeautomaticsub', default=False,"
b"-        help='Do not write auto-generated subtitles (default) (Alias: --no-write-automatic-subs)')"
b"+        u'--no-write-auto-subs', u'--no-write-automatic-subs',"
b"+        action=u'store_false', dest=u'writeautomaticsub', default=False,"
b"+        help=u'Do not write auto-generated subtitles (default) (Alias: --no-write-automatic-subs)')"
b'     subtitles.add_option('
b"-        '--all-subs',"
b"-        action='store_true', dest='allsubtitles', default=False,"
b"+        u'--all-subs',"
b"+        action=u'store_true', dest=u'allsubtitles', default=False,"
b'         help=optparse.SUPPRESS_HELP)'
b'     subtitles.add_option('
b"-        '--list-subs',"
b"-        action='store_true', dest='listsubtitles', default=False,"
b"-        help='List available subtitles of each video. Simulate unless --no-simulate is used')"
b"+        u'--list-subs',"
b"+        action=u'store_true', dest=u'listsubtitles', default=False,"
b"+        help=u'List available subtitles of each video. Simulate unless --no-simulate is used')"
b'     subtitles.add_option('
b"-        '--sub-format',"
b"-        action='store', dest='subtitlesformat', metavar='FORMAT', default='best',"
b'-        help=\'Subtitle format; accepts formats preference separated by "/", e.g. "srt" or "ass/srt/best"\')'
b"+        u'--sub-format',"
b"+        action=u'store', dest=u'subtitlesformat', metavar=u'FORMAT', default=u'best',"
b'+        help=u\'Subtitle format; accepts formats preference separated by "/", e.g. "srt" or "ass/srt/best"\')'
b'     subtitles.add_option('
b"-        '--sub-langs', '--srt-langs',"
b"-        action='callback', dest='subtitleslangs', metavar='LANGS', type='str',"
b"+        u'--sub-langs', u'--srt-langs',"
b"+        action=u'callback', dest=u'subtitleslangs', metavar=u'LANGS', type=u'str',"
b'         default=[], callback=_list_from_options_callback,'
b'         help=('
b'-            \'Languages of the subtitles to download (can be regex) or "all" separated by commas, e.g. --sub-langs "en.*,ja" \''
b'-            \'(where "en.*" is a regex pattern that matches "en" followed by 0 or more of any character). \''
b'-            \'You can prefix the language code with a "-" to exclude it from the requested languages, e.g. --sub-langs all,-live_chat. \''
b"-            'Use --list-subs for a list of available language tags'))"
b'-'
b"-    downloader = optparse.OptionGroup(parser, 'Download Options')"
b'-    downloader.add_option('
b"-        '-N', '--concurrent-fragments',"
b"-        dest='concurrent_fragment_downloads', metavar='N', default=1, type=int,"
b"-        help='Number of fragments of a dash/hlsnative video that should be downloaded concurrently (default is %default)')"
b'-    downloader.add_option('
b"-        '-r', '--limit-rate', '--rate-limit',"
b"-        dest='ratelimit', metavar='RATE',"
b"-        help='Maximum download rate in bytes per second, e.g. 50K or 4.2M')"
b'-    downloader.add_option('
b"-        '--throttled-rate',"
b"-        dest='throttledratelimit', metavar='RATE',"
b"-        help='Minimum download rate in bytes per second below which throttling is assumed and the video data is re-extracted, e.g. 100K')"
b'-    downloader.add_option('
b"-        '-R', '--retries',"
b"-        dest='retries', metavar='RETRIES', default=10,"
b'-        help=\'Number of retries (default is %default), or "infinite"\')'
b'-    downloader.add_option('
b"-        '--file-access-retries',"
b"-        dest='file_access_retries', metavar='RETRIES', default=3,"
b'-        help=\'Number of times to retry on file access error (default is %default), or "infinite"\')'
b'-    downloader.add_option('
b"-        '--fragment-retries',"
b"-        dest='fragment_retries', metavar='RETRIES', default=10,"
b'-        help=\'Number of retries for a fragment (default is %default), or "infinite" (DASH, hlsnative and ISM)\')'
b'-    downloader.add_option('
b"-        '--retry-sleep',"
b"-        dest='retry_sleep', metavar='[TYPE:]EXPR', default={}, type='str',"
b"-        action='callback', callback=_dict_from_options_callback,"
b'+            u\'Languages of the subtitles to download (can be regex) or "all" separated by commas, e.g. --sub-langs "en.*,ja" \''
b'+            u\'(where "en.*" is a regex pattern that matches "en" followed by 0 or more of any character). \''
b'+            u\'You can prefix the language code with a "-" to exclude it from the requested languages, e.g. --sub-langs all,-live_chat. \''
b"+            u'Use --list-subs for a list of available language tags'))"
b'+'
b"+    downloader = optparse.OptionGroup(parser, u'Download Options')"
b'+    downloader.add_option('
b"+        u'-N', u'--concurrent-fragments',"
b"+        dest=u'concurrent_fragment_downloads', metavar=u'N', default=1, type=int,"
b"+        help=u'Number of fragments of a dash/hlsnative video that should be downloaded concurrently (default is %default)')"
b'+    downloader.add_option('
b"+        u'-r', u'--limit-rate', u'--rate-limit',"
b"+        dest=u'ratelimit', metavar=u'RATE',"
b"+        help=u'Maximum download rate in bytes per second, e.g. 50K or 4.2M')"
b'+    downloader.add_option('
b"+        u'--throttled-rate',"
b"+        dest=u'throttledratelimit', metavar=u'RATE',"
b"+        help=u'Minimum download rate in bytes per second below which throttling is assumed and the video data is re-extracted, e.g. 100K')"
b'+    downloader.add_option('
b"+        u'-R', u'--retries',"
b"+        dest=u'retries', metavar=u'RETRIES', default=10,"
b'+        help=u\'Number of retries (default is %default), or "infinite"\')'
b'+    downloader.add_option('
b"+        u'--file-access-retries',"
b"+        dest=u'file_access_retries', metavar=u'RETRIES', default=3,"
b'+        help=u\'Number of times to retry on file access error (default is %default), or "infinite"\')'
b'+    downloader.add_option('
b"+        u'--fragment-retries',"
b"+        dest=u'fragment_retries', metavar=u'RETRIES', default=10,"
b'+        help=u\'Number of retries for a fragment (default is %default), or "infinite" (DASH, hlsnative and ISM)\')'
b'+    downloader.add_option('
b"+        u'--retry-sleep',"
b"+        dest=u'retry_sleep', metavar=u'[TYPE:]EXPR', default={}, type=u'str',"
b"+        action=u'callback', callback=_dict_from_options_callback,"
b'         callback_kwargs={'
b"-            'allowed_keys': 'http|fragment|file_access|extractor',"
b"-            'default_key': 'http',"
b"+            u'allowed_keys': u'http|fragment|file_access|extractor',"
b"+            u'default_key': u'http',"
b'         }, help=('
b"-            'Time to sleep between retries in seconds (optionally) prefixed by the type of retry '"
b"-            '(http (default), fragment, file_access, extractor) to apply the sleep to. '"
b"-            'EXPR can be a number, linear=START[:END[:STEP=1]] or exp=START[:END[:BASE=2]]. '"
b"-            'This option can be used multiple times to set the sleep for the different retry types, '"
b"-            'e.g. --retry-sleep linear=1::2 --retry-sleep fragment:exp=1:20'))"
b'-    downloader.add_option('
b"-        '--skip-unavailable-fragments', '--no-abort-on-unavailable-fragments',"
b"-        action='store_true', dest='skip_unavailable_fragments', default=True,"
b"-        help='Skip unavailable fragments for DASH, hlsnative and ISM downloads (default) (Alias: --no-abort-on-unavailable-fragments)')"
b'-    downloader.add_option('
b"-        '--abort-on-unavailable-fragments', '--no-skip-unavailable-fragments',"
b"-        action='store_false', dest='skip_unavailable_fragments',"
b"-        help='Abort download if a fragment is unavailable (Alias: --no-skip-unavailable-fragments)')"
b'-    downloader.add_option('
b"-        '--keep-fragments',"
b"-        action='store_true', dest='keep_fragments', default=False,"
b"-        help='Keep downloaded fragments on disk after downloading is finished')"
b'-    downloader.add_option('
b"-        '--no-keep-fragments',"
b"-        action='store_false', dest='keep_fragments',"
b"-        help='Delete downloaded fragments after downloading is finished (default)')"
b'-    downloader.add_option('
b"-        '--buffer-size',"
b"-        dest='buffersize', metavar='SIZE', default='1024',"
b"-        help='Size of download buffer, e.g. 1024 or 16K (default is %default)')"
b'-    downloader.add_option('
b"-        '--resize-buffer',"
b"-        action='store_false', dest='noresizebuffer',"
b"-        help='The buffer size is automatically resized from an initial value of --buffer-size (default)')"
b'-    downloader.add_option('
b"-        '--no-resize-buffer',"
b"-        action='store_true', dest='noresizebuffer', default=False,"
b"-        help='Do not automatically adjust the buffer size')"
b'-    downloader.add_option('
b"-        '--http-chunk-size',"
b"-        dest='http_chunk_size', metavar='SIZE', default=None,"
b'-        help=('
b"-            'Size of a chunk for chunk-based HTTP downloading, e.g. 10485760 or 10M (default is disabled). '"
b"-            'May be useful for bypassing bandwidth throttling imposed by a webserver (experimental)'))"
b'-    downloader.add_option('
b"-        '--test',"
b"-        action='store_true', dest='test', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    downloader.add_option('
b"-        '--playlist-reverse',"
b"-        action='store_true', dest='playlist_reverse',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    downloader.add_option('
b"-        '--no-playlist-reverse',"
b"-        action='store_false', dest='playlist_reverse',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    downloader.add_option('
b"-        '--playlist-random',"
b"-        action='store_true', dest='playlist_random',"
b"-        help='Download playlist videos in random order')"
b'-    downloader.add_option('
b"-        '--lazy-playlist',"
b"-        action='store_true', dest='lazy_playlist',"
b"-        help='Process entries in the playlist as they are received. This disables n_entries, --playlist-random and --playlist-reverse')"
b'-    downloader.add_option('
b"-        '--no-lazy-playlist',"
b"-        action='store_false', dest='lazy_playlist',"
b"-        help='Process videos in the playlist only after the entire playlist is parsed (default)')"
b'-    downloader.add_option('
b"-        '--xattr-set-filesize',"
b"-        dest='xattr_set_filesize', action='store_true',"
b"-        help='Set file xattribute ytdl.filesize with expected file size')"
b'-    downloader.add_option('
b"-        '--hls-prefer-native',"
b"-        dest='hls_prefer_native', action='store_true', default=None,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    downloader.add_option('
b"-        '--hls-prefer-ffmpeg',"
b"-        dest='hls_prefer_native', action='store_false', default=None,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    downloader.add_option('
b"-        '--hls-use-mpegts',"
b"-        dest='hls_use_mpegts', action='store_true', default=None,"
b'-        help=('
b"-            'Use the mpegts container for HLS videos; '"
b"-            'allowing some players to play the video while downloading, '"
b"-            'and reducing the chance of file corruption if download is interrupted. '"
b"-            'This is enabled by default for live streams'))"
b'-    downloader.add_option('
b"-        '--no-hls-use-mpegts',"
b"-        dest='hls_use_mpegts', action='store_false',"
b'-        help=('
b"-            'Do not use the mpegts container for HLS videos. '"
b"-            'This is default when not downloading live streams'))"
b'-    downloader.add_option('
b"-        '--download-sections',"
b"-        metavar='REGEX', dest='download_ranges', action='append',"
b'-        help=('
b"-            'Download only chapters that match the regular expression. '"
b'-            \'A "*" prefix denotes time-range instead of chapter. Negative timestamps are calculated from the end. \''
b'-            \'"*from-url" can be used to download between the "start_time" and "end_time" extracted from the URL. \''
b"-            'Needs ffmpeg. This option can be used multiple times to download multiple sections, '"
b'-            \'e.g. --download-sections "*10:15-inf" --download-sections "intro"\'))'
b'-    downloader.add_option('
b"-        '--downloader', '--external-downloader',"
b"-        dest='external_downloader', metavar='[PROTO:]NAME', default={}, type='str',"
b"-        action='callback', callback=_dict_from_options_callback,"
b"+            u'Time to sleep between retries in seconds (optionally) prefixed by the type of retry '"
b"+            u'(http (default), fragment, file_access, extractor) to apply the sleep to. '"
b"+            u'EXPR can be a number, linear=START[:END[:STEP=1]] or exp=START[:END[:BASE=2]]. '"
b"+            u'This option can be used multiple times to set the sleep for the different retry types, '"
b"+            u'e.g. --retry-sleep linear=1::2 --retry-sleep fragment:exp=1:20'))"
b'+    downloader.add_option('
b"+        u'--skip-unavailable-fragments', u'--no-abort-on-unavailable-fragments',"
b"+        action=u'store_true', dest=u'skip_unavailable_fragments', default=True,"
b"+        help=u'Skip unavailable fragments for DASH, hlsnative and ISM downloads (default) (Alias: --no-abort-on-unavailable-fragments)')"
b'+    downloader.add_option('
b"+        u'--abort-on-unavailable-fragments', u'--no-skip-unavailable-fragments',"
b"+        action=u'store_false', dest=u'skip_unavailable_fragments',"
b"+        help=u'Abort download if a fragment is unavailable (Alias: --no-skip-unavailable-fragments)')"
b'+    downloader.add_option('
b"+        u'--keep-fragments',"
b"+        action=u'store_true', dest=u'keep_fragments', default=False,"
b"+        help=u'Keep downloaded fragments on disk after downloading is finished')"
b'+    downloader.add_option('
b"+        u'--no-keep-fragments',"
b"+        action=u'store_false', dest=u'keep_fragments',"
b"+        help=u'Delete downloaded fragments after downloading is finished (default)')"
b'+    downloader.add_option('
b"+        u'--buffer-size',"
b"+        dest=u'buffersize', metavar=u'SIZE', default=u'1024',"
b"+        help=u'Size of download buffer, e.g. 1024 or 16K (default is %default)')"
b'+    downloader.add_option('
b"+        u'--resize-buffer',"
b"+        action=u'store_false', dest=u'noresizebuffer',"
b"+        help=u'The buffer size is automatically resized from an initial value of --buffer-size (default)')"
b'+    downloader.add_option('
b"+        u'--no-resize-buffer',"
b"+        action=u'store_true', dest=u'noresizebuffer', default=False,"
b"+        help=u'Do not automatically adjust the buffer size')"
b'+    downloader.add_option('
b"+        u'--http-chunk-size',"
b"+        dest=u'http_chunk_size', metavar=u'SIZE', default=None,"
b'+        help=('
b"+            u'Size of a chunk for chunk-based HTTP downloading, e.g. 10485760 or 10M (default is disabled). '"
b"+            u'May be useful for bypassing bandwidth throttling imposed by a webserver (experimental)'))"
b'+    downloader.add_option('
b"+        u'--test',"
b"+        action=u'store_true', dest=u'test', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    downloader.add_option('
b"+        u'--playlist-reverse',"
b"+        action=u'store_true', dest=u'playlist_reverse',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    downloader.add_option('
b"+        u'--no-playlist-reverse',"
b"+        action=u'store_false', dest=u'playlist_reverse',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    downloader.add_option('
b"+        u'--playlist-random',"
b"+        action=u'store_true', dest=u'playlist_random',"
b"+        help=u'Download playlist videos in random order')"
b'+    downloader.add_option('
b"+        u'--lazy-playlist',"
b"+        action=u'store_true', dest=u'lazy_playlist',"
b"+        help=u'Process entries in the playlist as they are received. This disables n_entries, --playlist-random and --playlist-reverse')"
b'+    downloader.add_option('
b"+        u'--no-lazy-playlist',"
b"+        action=u'store_false', dest=u'lazy_playlist',"
b"+        help=u'Process videos in the playlist only after the entire playlist is parsed (default)')"
b'+    downloader.add_option('
b"+        u'--xattr-set-filesize',"
b"+        dest=u'xattr_set_filesize', action=u'store_true',"
b"+        help=u'Set file xattribute ytdl.filesize with expected file size')"
b'+    downloader.add_option('
b"+        u'--hls-prefer-native',"
b"+        dest=u'hls_prefer_native', action=u'store_true', default=None,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    downloader.add_option('
b"+        u'--hls-prefer-ffmpeg',"
b"+        dest=u'hls_prefer_native', action=u'store_false', default=None,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    downloader.add_option('
b"+        u'--hls-use-mpegts',"
b"+        dest=u'hls_use_mpegts', action=u'store_true', default=None,"
b'+        help=('
b"+            u'Use the mpegts container for HLS videos; '"
b"+            u'allowing some players to play the video while downloading, '"
b"+            u'and reducing the chance of file corruption if download is interrupted. '"
b"+            u'This is enabled by default for live streams'))"
b'+    downloader.add_option('
b"+        u'--no-hls-use-mpegts',"
b"+        dest=u'hls_use_mpegts', action=u'store_false',"
b'+        help=('
b"+            u'Do not use the mpegts container for HLS videos. '"
b"+            u'This is default when not downloading live streams'))"
b'+    downloader.add_option('
b"+        u'--download-sections',"
b"+        metavar=u'REGEX', dest=u'download_ranges', action=u'append',"
b'+        help=('
b"+            u'Download only chapters that match the regular expression. '"
b'+            u\'A "*" prefix denotes time-range instead of chapter. Negative timestamps are calculated from the end. \''
b'+            u\'"*from-url" can be used to download between the "start_time" and "end_time" extracted from the URL. \''
b"+            u'Needs ffmpeg. This option can be used multiple times to download multiple sections, '"
b'+            u\'e.g. --download-sections "*10:15-inf" --download-sections "intro"\'))'
b'+    downloader.add_option('
b"+        u'--downloader', u'--external-downloader',"
b"+        dest=u'external_downloader', metavar=u'[PROTO:]NAME', default={}, type=u'str',"
b"+        action=u'callback', callback=_dict_from_options_callback,"
b'         callback_kwargs={'
b"-            'allowed_keys': 'http|ftp|m3u8|dash|rtsp|rtmp|mms',"
b"-            'default_key': 'default',"
b"-            'process': str.strip,"
b"+            u'allowed_keys': u'http|ftp|m3u8|dash|rtsp|rtmp|mms',"
b"+            u'default_key': u'default',"
b"+            u'process': unicode.strip,"
b'         }, help=('
b"-            'Name or path of the external downloader to use (optionally) prefixed by '"
b"-            'the protocols (http, ftp, m3u8, dash, rstp, rtmp, mms) to use it for. '"
b"+            u'Name or path of the external downloader to use (optionally) prefixed by '"
b"+            u'the protocols (http, ftp, m3u8, dash, rstp, rtmp, mms) to use it for. '"
b'             f\'Currently supports native, {", ".join(sorted(list_external_downloaders()))}. \''
b"-            'You can use this option multiple times to set different downloaders for different protocols. '"
b'-            \'E.g. --downloader aria2c --downloader "dash,m3u8:native" will use \''
b"-            'aria2c for http/ftp downloads, and the native downloader for dash/m3u8 downloads '"
b"-            '(Alias: --external-downloader)'))"
b'-    downloader.add_option('
b"-        '--downloader-args', '--external-downloader-args',"
b"-        metavar='NAME:ARGS', dest='external_downloader_args', default={}, type='str',"
b"-        action='callback', callback=_dict_from_options_callback,"
b"+            u'You can use this option multiple times to set different downloaders for different protocols. '"
b'+            u\'E.g. --downloader aria2c --downloader "dash,m3u8:native" will use \''
b"+            u'aria2c for http/ftp downloads, and the native downloader for dash/m3u8 downloads '"
b"+            u'(Alias: --external-downloader)'))"
b'+    downloader.add_option('
b"+        u'--downloader-args', u'--external-downloader-args',"
b"+        metavar=u'NAME:ARGS', dest=u'external_downloader_args', default={}, type=u'str',"
b"+        action=u'callback', callback=_dict_from_options_callback,"
b'         callback_kwargs={'
b"-            'allowed_keys': r'ffmpeg_[io]\\d*|{}'.format('|'.join(map(re.escape, list_external_downloaders()))),"
b"-            'default_key': 'default',"
b"-            'process': shlex.split,"
b"+            u'allowed_keys': ur'ffmpeg_[io]\\d*|{}'.format(u'|'.join(imap(re.escape, list_external_downloaders()))),"
b"+            u'default_key': u'default',"
b"+            u'process': shlex.split,"
b'         }, help=('
b"-            'Give these arguments to the external downloader. '"
b'-            \'Specify the downloader name and the arguments separated by a colon ":". \''
b"-            'For ffmpeg, arguments can be passed to different positions using the same syntax as --postprocessor-args. '"
b"-            'You can use this option multiple times to give different arguments to different downloaders '"
b"-            '(Alias: --external-downloader-args)'))"
b'-'
b"-    workarounds = optparse.OptionGroup(parser, 'Workarounds')"
b"+            u'Give these arguments to the external downloader. '"
b'+            u\'Specify the downloader name and the arguments separated by a colon ":". \''
b"+            u'For ffmpeg, arguments can be passed to different positions using the same syntax as --postprocessor-args. '"
b"+            u'You can use this option multiple times to give different arguments to different downloaders '"
b"+            u'(Alias: --external-downloader-args)'))"
b'+'
b"+    workarounds = optparse.OptionGroup(parser, u'Workarounds')"
b'     workarounds.add_option('
b"-        '--encoding',"
b"-        dest='encoding', metavar='ENCODING',"
b"-        help='Force the specified encoding (experimental)')"
b"+        u'--encoding',"
b"+        dest=u'encoding', metavar=u'ENCODING',"
b"+        help=u'Force the specified encoding (experimental)')"
b'     workarounds.add_option('
b"-        '--legacy-server-connect',"
b"-        action='store_true', dest='legacy_server_connect', default=False,"
b"-        help='Explicitly allow HTTPS connection to servers that do not support RFC 5746 secure renegotiation')"
b"+        u'--legacy-server-connect',"
b"+        action=u'store_true', dest=u'legacy_server_connect', default=False,"
b"+        help=u'Explicitly allow HTTPS connection to servers that do not support RFC 5746 secure renegotiation')"
b'     workarounds.add_option('
b"-        '--no-check-certificates',"
b"-        action='store_true', dest='no_check_certificate', default=False,"
b"-        help='Suppress HTTPS certificate validation')"
b"+        u'--no-check-certificates',"
b"+        action=u'store_true', dest=u'no_check_certificate', default=False,"
b"+        help=u'Suppress HTTPS certificate validation')"
b'     workarounds.add_option('
b"-        '--prefer-insecure', '--prefer-unsecure',"
b"-        action='store_true', dest='prefer_insecure',"
b"-        help='Use an unencrypted connection to retrieve information about the video (Currently supported only for YouTube)')"
b"+        u'--prefer-insecure', u'--prefer-unsecure',"
b"+        action=u'store_true', dest=u'prefer_insecure',"
b"+        help=u'Use an unencrypted connection to retrieve information about the video (Currently supported only for YouTube)')"
b'     workarounds.add_option('
b"-        '--user-agent',"
b"-        metavar='UA', dest='user_agent',"
b"+        u'--user-agent',"
b"+        metavar=u'UA', dest=u'user_agent',"
b'         help=optparse.SUPPRESS_HELP)'
b'     workarounds.add_option('
b"-        '--referer',"
b"-        metavar='URL', dest='referer', default=None,"
b"+        u'--referer',"
b"+        metavar=u'URL', dest=u'referer', default=None,"
b'         help=optparse.SUPPRESS_HELP)'
b'     workarounds.add_option('
b"-        '--add-headers',"
b"-        metavar='FIELD:VALUE', dest='headers', default={}, type='str',"
b"-        action='callback', callback=_dict_from_options_callback,"
b"-        callback_kwargs={'multiple_keys': False},"
b'-        help=\'Specify a custom HTTP header and its value, separated by a colon ":". You can use this option multiple times\','
b"+        u'--add-headers',"
b"+        metavar=u'FIELD:VALUE', dest=u'headers', default={}, type=u'str',"
b"+        action=u'callback', callback=_dict_from_options_callback,"
b"+        callback_kwargs={u'multiple_keys': False},"
b'+        help=u\'Specify a custom HTTP header and its value, separated by a colon ":". You can use this option multiple times\','
b'     )'
b'     workarounds.add_option('
b"-        '--bidi-workaround',"
b"-        dest='bidi_workaround', action='store_true',"
b"-        help='Work around terminals that lack bidirectional text support. Requires bidiv or fribidi executable in PATH')"
b"+        u'--bidi-workaround',"
b"+        dest=u'bidi_workaround', action=u'store_true',"
b"+        help=u'Work around terminals that lack bidirectional text support. Requires bidiv or fribidi executable in PATH')"
b'     workarounds.add_option('
b"-        '--sleep-requests', metavar='SECONDS',"
b"-        dest='sleep_interval_requests', type=float,"
b"-        help='Number of seconds to sleep between requests during data extraction')"
b"+        u'--sleep-requests', metavar=u'SECONDS',"
b"+        dest=u'sleep_interval_requests', type=float,"
b"+        help=u'Number of seconds to sleep between requests during data extraction')"
b'     workarounds.add_option('
b"-        '--sleep-interval', '--min-sleep-interval', metavar='SECONDS',"
b"-        dest='sleep_interval', type=float,"
b'-        help=('
b"-            'Number of seconds to sleep before each download. '"
b"-            'This is the minimum time to sleep when used along with --max-sleep-interval '"
b"-            '(Alias: --min-sleep-interval)'))"
b"+        u'--sleep-interval', u'--min-sleep-interval', metavar=u'SECONDS',"
b"+        dest=u'sleep_interval', type=float,"
b'+        help=('
b"+            u'Number of seconds to sleep before each download. '"
b"+            u'This is the minimum time to sleep when used along with --max-sleep-interval '"
b"+            u'(Alias: --min-sleep-interval)'))"
b'     workarounds.add_option('
b"-        '--max-sleep-interval', metavar='SECONDS',"
b"-        dest='max_sleep_interval', type=float,"
b"-        help='Maximum number of seconds to sleep. Can only be used along with --min-sleep-interval')"
b"+        u'--max-sleep-interval', metavar=u'SECONDS',"
b"+        dest=u'max_sleep_interval', type=float,"
b"+        help=u'Maximum number of seconds to sleep. Can only be used along with --min-sleep-interval')"
b'     workarounds.add_option('
b"-        '--sleep-subtitles', metavar='SECONDS',"
b"-        dest='sleep_interval_subtitles', default=0, type=int,"
b"-        help='Number of seconds to sleep before each subtitle download')"
b'-'
b"-    verbosity = optparse.OptionGroup(parser, 'Verbosity and Simulation Options')"
b'-    verbosity.add_option('
b"-        '-q', '--quiet',"
b"-        action='store_true', dest='quiet', default=None,"
b"-        help='Activate quiet mode. If used with --verbose, print the log to stderr')"
b'-    verbosity.add_option('
b"-        '--no-quiet',"
b"-        action='store_false', dest='quiet',"
b"-        help='Deactivate quiet mode. (Default)')"
b'-    verbosity.add_option('
b"-        '--no-warnings',"
b"-        dest='no_warnings', action='store_true', default=False,"
b"-        help='Ignore warnings')"
b'-    verbosity.add_option('
b"-        '-s', '--simulate',"
b"-        action='store_true', dest='simulate', default=None,"
b"-        help='Do not download the video and do not write anything to disk')"
b'-    verbosity.add_option('
b"-        '--no-simulate',"
b"-        action='store_false', dest='simulate',"
b"-        help='Download the video even if printing/listing options are used')"
b'-    verbosity.add_option('
b"-        '--ignore-no-formats-error',"
b"-        action='store_true', dest='ignore_no_formats_error', default=False,"
b'-        help=('
b'-            \'Ignore "No video formats" error. Useful for extracting metadata \''
b"-            'even if the videos are not actually available for download (experimental)'))"
b'-    verbosity.add_option('
b"-        '--no-ignore-no-formats-error',"
b"-        action='store_false', dest='ignore_no_formats_error',"
b"-        help='Throw error when no downloadable video formats are found (default)')"
b'-    verbosity.add_option('
b"-        '--skip-download', '--no-download',"
b"-        action='store_true', dest='skip_download', default=False,"
b"-        help='Do not download the video but write all related files (Alias: --no-download)')"
b'-    verbosity.add_option('
b"-        '-O', '--print',"
b"-        metavar='[WHEN:]TEMPLATE', dest='forceprint', **when_prefix('video'),"
b'-        help=('
b'-            \'Field name or output template to print to screen, optionally prefixed with when to print it, separated by a ":". \''
b'-            \'Supported values of "WHEN" are the same as that of --use-postprocessor (default: video). \''
b"-            'Implies --quiet. Implies --simulate unless --no-simulate or later stages of WHEN are used. '"
b"-            'This option can be used multiple times'))"
b'-    verbosity.add_option('
b"-        '--print-to-file',"
b"-        metavar='[WHEN:]TEMPLATE FILE', dest='print_to_file', nargs=2, **when_prefix('video'),"
b'-        help=('
b"-            'Append given template to the file. The values of WHEN and TEMPLATE are the same as that of --print. '"
b"-            'FILE uses the same syntax as the output template. This option can be used multiple times'))"
b'-    verbosity.add_option('
b"-        '-g', '--get-url',"
b"-        action='store_true', dest='geturl', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    verbosity.add_option('
b"-        '-e', '--get-title',"
b"-        action='store_true', dest='gettitle', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    verbosity.add_option('
b"-        '--get-id',"
b"-        action='store_true', dest='getid', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    verbosity.add_option('
b"-        '--get-thumbnail',"
b"-        action='store_true', dest='getthumbnail', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    verbosity.add_option('
b"-        '--get-description',"
b"-        action='store_true', dest='getdescription', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    verbosity.add_option('
b"-        '--get-duration',"
b"-        action='store_true', dest='getduration', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    verbosity.add_option('
b"-        '--get-filename',"
b"-        action='store_true', dest='getfilename', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    verbosity.add_option('
b"-        '--get-format',"
b"-        action='store_true', dest='getformat', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    verbosity.add_option('
b"-        '-j', '--dump-json',"
b"-        action='store_true', dest='dumpjson', default=False,"
b'-        help=('
b"-            'Quiet, but print JSON information for each video. Simulate unless --no-simulate is used. '"
b'-            \'See "OUTPUT TEMPLATE" for a description of available keys\'))'
b'-    verbosity.add_option('
b"-        '-J', '--dump-single-json',"
b"-        action='store_true', dest='dump_single_json', default=False,"
b'-        help=('
b"-            'Quiet, but print JSON information for each URL or infojson passed. Simulate unless --no-simulate is used. '"
b"-            'If the URL refers to a playlist, the whole playlist information is dumped in a single line'))"
b'-    verbosity.add_option('
b"-        '--print-json',"
b"-        action='store_true', dest='print_json', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    verbosity.add_option('
b"-        '--force-write-archive', '--force-write-download-archive', '--force-download-archive',"
b"-        action='store_true', dest='force_write_download_archive', default=False,"
b'-        help=('
b"-            'Force download archive entries to be written as far as no errors occur, '"
b"-            'even if -s or another simulation option is used (Alias: --force-download-archive)'))"
b'-    verbosity.add_option('
b"-        '--newline',"
b"-        action='store_true', dest='progress_with_newline', default=False,"
b"-        help='Output progress bar as new lines')"
b'-    verbosity.add_option('
b"-        '--no-progress',"
b"-        action='store_true', dest='noprogress', default=None,"
b"-        help='Do not print progress bar')"
b'-    verbosity.add_option('
b"-        '--progress',"
b"-        action='store_false', dest='noprogress',"
b"-        help='Show progress bar, even if in quiet mode')"
b'-    verbosity.add_option('
b"-        '--console-title',"
b"-        action='store_true', dest='consoletitle', default=False,"
b"-        help='Display progress in console titlebar')"
b'-    verbosity.add_option('
b"-        '--progress-template',"
b"-        metavar='[TYPES:]TEMPLATE', dest='progress_template', default={}, type='str',"
b"-        action='callback', callback=_dict_from_options_callback,"
b"+        u'--sleep-subtitles', metavar=u'SECONDS',"
b"+        dest=u'sleep_interval_subtitles', default=0, type=int,"
b"+        help=u'Number of seconds to sleep before each subtitle download')"
b'+'
b"+    verbosity = optparse.OptionGroup(parser, u'Verbosity and Simulation Options')"
b'+    verbosity.add_option('
b"+        u'-q', u'--quiet',"
b"+        action=u'store_true', dest=u'quiet', default=None,"
b"+        help=u'Activate quiet mode. If used with --verbose, print the log to stderr')"
b'+    verbosity.add_option('
b"+        u'--no-quiet',"
b"+        action=u'store_false', dest=u'quiet',"
b"+        help=u'Deactivate quiet mode. (Default)')"
b'+    verbosity.add_option('
b"+        u'--no-warnings',"
b"+        dest=u'no_warnings', action=u'store_true', default=False,"
b"+        help=u'Ignore warnings')"
b'+    verbosity.add_option('
b"+        u'-s', u'--simulate',"
b"+        action=u'store_true', dest=u'simulate', default=None,"
b"+        help=u'Do not download the video and do not write anything to disk')"
b'+    verbosity.add_option('
b"+        u'--no-simulate',"
b"+        action=u'store_false', dest=u'simulate',"
b"+        help=u'Download the video even if printing/listing options are used')"
b'+    verbosity.add_option('
b"+        u'--ignore-no-formats-error',"
b"+        action=u'store_true', dest=u'ignore_no_formats_error', default=False,"
b'+        help=('
b'+            u\'Ignore "No video formats" error. Useful for extracting metadata \''
b"+            u'even if the videos are not actually available for download (experimental)'))"
b'+    verbosity.add_option('
b"+        u'--no-ignore-no-formats-error',"
b"+        action=u'store_false', dest=u'ignore_no_formats_error',"
b"+        help=u'Throw error when no downloadable video formats are found (default)')"
b'+    verbosity.add_option('
b"+        u'--skip-download', u'--no-download',"
b"+        action=u'store_true', dest=u'skip_download', default=False,"
b"+        help=u'Do not download the video but write all related files (Alias: --no-download)')"
b'+    verbosity.add_option('
b"+        u'-O', u'--print',"
b"+        metavar=u'[WHEN:]TEMPLATE', dest=u'forceprint', **when_prefix(u'video'),"
b'+        help=('
b'+            u\'Field name or output template to print to screen, optionally prefixed with when to print it, separated by a ":". \''
b'+            u\'Supported values of "WHEN" are the same as that of --use-postprocessor (default: video). \''
b"+            u'Implies --quiet. Implies --simulate unless --no-simulate or later stages of WHEN are used. '"
b"+            u'This option can be used multiple times'))"
b'+    verbosity.add_option('
b"+        u'--print-to-file',"
b"+        metavar=u'[WHEN:]TEMPLATE FILE', dest=u'print_to_file', nargs=2, **when_prefix(u'video'),"
b'+        help=('
b"+            u'Append given template to the file. The values of WHEN and TEMPLATE are the same as that of --print. '"
b"+            u'FILE uses the same syntax as the output template. This option can be used multiple times'))"
b'+    verbosity.add_option('
b"+        u'-g', u'--get-url',"
b"+        action=u'store_true', dest=u'geturl', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    verbosity.add_option('
b"+        u'-e', u'--get-title',"
b"+        action=u'store_true', dest=u'gettitle', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    verbosity.add_option('
b"+        u'--get-id',"
b"+        action=u'store_true', dest=u'getid', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    verbosity.add_option('
b"+        u'--get-thumbnail',"
b"+        action=u'store_true', dest=u'getthumbnail', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    verbosity.add_option('
b"+        u'--get-description',"
b"+        action=u'store_true', dest=u'getdescription', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    verbosity.add_option('
b"+        u'--get-duration',"
b"+        action=u'store_true', dest=u'getduration', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    verbosity.add_option('
b"+        u'--get-filename',"
b"+        action=u'store_true', dest=u'getfilename', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    verbosity.add_option('
b"+        u'--get-format',"
b"+        action=u'store_true', dest=u'getformat', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    verbosity.add_option('
b"+        u'-j', u'--dump-json',"
b"+        action=u'store_true', dest=u'dumpjson', default=False,"
b'+        help=('
b"+            u'Quiet, but print JSON information for each video. Simulate unless --no-simulate is used. '"
b'+            u\'See "OUTPUT TEMPLATE" for a description of available keys\'))'
b'+    verbosity.add_option('
b"+        u'-J', u'--dump-single-json',"
b"+        action=u'store_true', dest=u'dump_single_json', default=False,"
b'+        help=('
b"+            u'Quiet, but print JSON information for each URL or infojson passed. Simulate unless --no-simulate is used. '"
b"+            u'If the URL refers to a playlist, the whole playlist information is dumped in a single line'))"
b'+    verbosity.add_option('
b"+        u'--print-json',"
b"+        action=u'store_true', dest=u'print_json', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    verbosity.add_option('
b"+        u'--force-write-archive', u'--force-write-download-archive', u'--force-download-archive',"
b"+        action=u'store_true', dest=u'force_write_download_archive', default=False,"
b'+        help=('
b"+            u'Force download archive entries to be written as far as no errors occur, '"
b"+            u'even if -s or another simulation option is used (Alias: --force-download-archive)'))"
b'+    verbosity.add_option('
b"+        u'--newline',"
b"+        action=u'store_true', dest=u'progress_with_newline', default=False,"
b"+        help=u'Output progress bar as new lines')"
b'+    verbosity.add_option('
b"+        u'--no-progress',"
b"+        action=u'store_true', dest=u'noprogress', default=None,"
b"+        help=u'Do not print progress bar')"
b'+    verbosity.add_option('
b"+        u'--progress',"
b"+        action=u'store_false', dest=u'noprogress',"
b"+        help=u'Show progress bar, even if in quiet mode')"
b'+    verbosity.add_option('
b"+        u'--console-title',"
b"+        action=u'store_true', dest=u'consoletitle', default=False,"
b"+        help=u'Display progress in console titlebar')"
b'+    verbosity.add_option('
b"+        u'--progress-template',"
b"+        metavar=u'[TYPES:]TEMPLATE', dest=u'progress_template', default={}, type=u'str',"
b"+        action=u'callback', callback=_dict_from_options_callback,"
b'         callback_kwargs={'
b"-            'allowed_keys': '(download|postprocess)(-title)?',"
b"-            'default_key': 'download',"
b"+            u'allowed_keys': u'(download|postprocess)(-title)?',"
b"+            u'default_key': u'download',"
b'         }, help=('
b'-            \'Template for progress outputs, optionally prefixed with one of "download:" (default), \''
b'-            \'"download-title:" (the console title), "postprocess:",  or "postprocess-title:". \''
b'-            \'The video\\\'s fields are accessible under the "info" key and \''
b'-            \'the progress attributes are accessible under "progress" key. E.g. \''
b'+            u\'Template for progress outputs, optionally prefixed with one of "download:" (default), \''
b'+            u\'"download-title:" (the console title), "postprocess:",  or "postprocess-title:". \''
b'+            u\'The video\\\'s fields are accessible under the "info" key and \''
b'+            u\'the progress attributes are accessible under "progress" key. E.g. \''
b'             # TODO: Document the fields inside "progress"'
b'-            \'--console-title --progress-template "download-title:%(info.id)s-%(progress.eta)s"\'))'
b'-    verbosity.add_option('
b"-        '--progress-delta',"
b"-        metavar='SECONDS', action='store', dest='progress_delta', type=float, default=0,"
b"-        help='Time between progress output (default: 0)')"
b'-    verbosity.add_option('
b"-        '-v', '--verbose',"
b"-        action='store_true', dest='verbose', default=False,"
b"-        help='Print various debugging information')"
b'-    verbosity.add_option('
b"-        '--dump-pages', '--dump-intermediate-pages',"
b"-        action='store_true', dest='dump_intermediate_pages', default=False,"
b"-        help='Print downloaded pages encoded using base64 to debug problems (very verbose)')"
b'-    verbosity.add_option('
b"-        '--write-pages',"
b"-        action='store_true', dest='write_pages', default=False,"
b"-        help='Write downloaded intermediary pages to files in the current directory to debug problems')"
b'-    verbosity.add_option('
b"-        '--load-pages',"
b"-        action='store_true', dest='load_pages', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    verbosity.add_option('
b"-        '--youtube-print-sig-code',"
b"-        action='store_true', dest='youtube_print_sig_code', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    verbosity.add_option('
b"-        '--print-traffic', '--dump-headers',"
b"-        dest='debug_printtraffic', action='store_true', default=False,"
b"-        help='Display sent and read HTTP traffic')"
b'-    verbosity.add_option('
b"-        '-C', '--call-home',"
b"-        dest='call_home', action='store_true', default=False,"
b'+            u\'--console-title --progress-template "download-title:%(info.id)s-%(progress.eta)s"\'))'
b'+    verbosity.add_option('
b"+        u'--progress-delta',"
b"+        metavar=u'SECONDS', action=u'store', dest=u'progress_delta', type=float, default=0,"
b"+        help=u'Time between progress output (default: 0)')"
b'+    verbosity.add_option('
b"+        u'-v', u'--verbose',"
b"+        action=u'store_true', dest=u'verbose', default=False,"
b"+        help=u'Print various debugging information')"
b'+    verbosity.add_option('
b"+        u'--dump-pages', u'--dump-intermediate-pages',"
b"+        action=u'store_true', dest=u'dump_intermediate_pages', default=False,"
b"+        help=u'Print downloaded pages encoded using base64 to debug problems (very verbose)')"
b'+    verbosity.add_option('
b"+        u'--write-pages',"
b"+        action=u'store_true', dest=u'write_pages', default=False,"
b"+        help=u'Write downloaded intermediary pages to files in the current directory to debug problems')"
b'+    verbosity.add_option('
b"+        u'--load-pages',"
b"+        action=u'store_true', dest=u'load_pages', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    verbosity.add_option('
b"+        u'--youtube-print-sig-code',"
b"+        action=u'store_true', dest=u'youtube_print_sig_code', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    verbosity.add_option('
b"+        u'--print-traffic', u'--dump-headers',"
b"+        dest=u'debug_printtraffic', action=u'store_true', default=False,"
b"+        help=u'Display sent and read HTTP traffic')"
b'+    verbosity.add_option('
b"+        u'-C', u'--call-home',"
b"+        dest=u'call_home', action=u'store_true', default=False,"
b"         # help='Contact the yt-dlp server for debugging')"
b'         help=optparse.SUPPRESS_HELP)'
b'     verbosity.add_option('
b"-        '--no-call-home',"
b"-        dest='call_home', action='store_false',"
b"+        u'--no-call-home',"
b"+        dest=u'call_home', action=u'store_false',"
b"         # help='Do not contact the yt-dlp server for debugging (default)')"
b'         help=optparse.SUPPRESS_HELP)'
b' '
b"-    filesystem = optparse.OptionGroup(parser, 'Filesystem Options')"
b'-    filesystem.add_option('
b"-        '-a', '--batch-file',"
b"-        dest='batchfile', metavar='FILE',"
b'-        help=('
b'-            \'File containing URLs to download ("-" for stdin), one URL per line. \''
b'-            \'Lines starting with "#", ";" or "]" are considered as comments and ignored\'))'
b'-    filesystem.add_option('
b"-        '--no-batch-file',"
b"-        dest='batchfile', action='store_const', const=None,"
b"-        help='Do not read URLs from batch file (default)')"
b'-    filesystem.add_option('
b"-        '--id', default=False,"
b"-        action='store_true', dest='useid', help=optparse.SUPPRESS_HELP)"
b'-    filesystem.add_option('
b"-        '-P', '--paths',"
b"-        metavar='[TYPES:]PATH', dest='paths', default={}, type='str',"
b"-        action='callback', callback=_dict_from_options_callback,"
b"+    filesystem = optparse.OptionGroup(parser, u'Filesystem Options')"
b'+    filesystem.add_option('
b"+        u'-a', u'--batch-file',"
b"+        dest=u'batchfile', metavar=u'FILE',"
b'+        help=('
b'+            u\'File containing URLs to download ("-" for stdin), one URL per line. \''
b'+            u\'Lines starting with "#", ";" or "]" are considered as comments and ignored\'))'
b'+    filesystem.add_option('
b"+        u'--no-batch-file',"
b"+        dest=u'batchfile', action=u'store_const', const=None,"
b"+        help=u'Do not read URLs from batch file (default)')"
b'+    filesystem.add_option('
b"+        u'--id', default=False,"
b"+        action=u'store_true', dest=u'useid', help=optparse.SUPPRESS_HELP)"
b'+    filesystem.add_option('
b"+        u'-P', u'--paths',"
b"+        metavar=u'[TYPES:]PATH', dest=u'paths', default={}, type=u'str',"
b"+        action=u'callback', callback=_dict_from_options_callback,"
b'         callback_kwargs={'
b"-            'allowed_keys': 'home|temp|{}'.format('|'.join(map(re.escape, OUTTMPL_TYPES.keys()))),"
b"-            'default_key': 'home',"
b"+            u'allowed_keys': u'home|temp|{}'.format(u'|'.join(imap(re.escape, OUTTMPL_TYPES.keys()))),"
b"+            u'default_key': u'home',"
b'         }, help=('
b"-            'The paths where the files should be downloaded. '"
b'-            \'Specify the type of file and the path separated by a colon ":". \''
b"-            'All the same TYPES as --output are supported. '"
b'-            \'Additionally, you can also provide "home" (default) and "temp" paths. \''
b"-            'All intermediary files are first downloaded to the temp path and '"
b"-            'then the final files are moved over to the home path after download is finished. '"
b"-            'This option is ignored if --output is an absolute path'))"
b'-    filesystem.add_option('
b"-        '-o', '--output',"
b"-        metavar='[TYPES:]TEMPLATE', dest='outtmpl', default={}, type='str',"
b"-        action='callback', callback=_dict_from_options_callback,"
b"+            u'The paths where the files should be downloaded. '"
b'+            u\'Specify the type of file and the path separated by a colon ":". \''
b"+            u'All the same TYPES as --output are supported. '"
b'+            u\'Additionally, you can also provide "home" (default) and "temp" paths. \''
b"+            u'All intermediary files are first downloaded to the temp path and '"
b"+            u'then the final files are moved over to the home path after download is finished. '"
b"+            u'This option is ignored if --output is an absolute path'))"
b'+    filesystem.add_option('
b"+        u'-o', u'--output',"
b"+        metavar=u'[TYPES:]TEMPLATE', dest=u'outtmpl', default={}, type=u'str',"
b"+        action=u'callback', callback=_dict_from_options_callback,"
b'         callback_kwargs={'
b"-            'allowed_keys': '|'.join(map(re.escape, OUTTMPL_TYPES.keys())),"
b"-            'default_key': 'default',"
b'-        }, help=\'Output filename template; see "OUTPUT TEMPLATE" for details\')'
b'-    filesystem.add_option('
b"-        '--output-na-placeholder',"
b"-        dest='outtmpl_na_placeholder', metavar='TEXT', default='NA',"
b'-        help=(\'Placeholder for unavailable fields in --output (default: "%default")\'))'
b'-    filesystem.add_option('
b"-        '--autonumber-size',"
b"-        dest='autonumber_size', metavar='NUMBER', type=int,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    filesystem.add_option('
b"-        '--autonumber-start',"
b"-        dest='autonumber_start', metavar='NUMBER', default=1, type=int,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    filesystem.add_option('
b"-        '--restrict-filenames',"
b"-        action='store_true', dest='restrictfilenames', default=False,"
b'-        help=\'Restrict filenames to only ASCII characters, and avoid "&" and spaces in filenames\')'
b'-    filesystem.add_option('
b"-        '--no-restrict-filenames',"
b"-        action='store_false', dest='restrictfilenames',"
b'-        help=\'Allow Unicode characters, "&" and spaces in filenames (default)\')'
b'-    filesystem.add_option('
b"-        '--windows-filenames',"
b"-        action='store_true', dest='windowsfilenames', default=None,"
b"-        help='Force filenames to be Windows-compatible')"
b'-    filesystem.add_option('
b"-        '--no-windows-filenames',"
b"-        action='store_false', dest='windowsfilenames',"
b"-        help='Sanitize filenames only minimally')"
b'-    filesystem.add_option('
b"-        '--trim-filenames', '--trim-file-names', metavar='LENGTH',"
b"-        dest='trim_file_name', default=0, type=int,"
b"-        help='Limit the filename length (excluding extension) to the specified number of characters')"
b'-    filesystem.add_option('
b"-        '-w', '--no-overwrites',"
b"-        action='store_false', dest='overwrites', default=None,"
b"-        help='Do not overwrite any files')"
b'-    filesystem.add_option('
b"-        '--force-overwrites', '--yes-overwrites',"
b"-        action='store_true', dest='overwrites',"
b"-        help='Overwrite all video and metadata files. This option includes --no-continue')"
b'-    filesystem.add_option('
b"-        '--no-force-overwrites',"
b"-        action='store_const', dest='overwrites', const=None,"
b"-        help='Do not overwrite the video, but overwrite related files (default)')"
b'-    filesystem.add_option('
b"-        '-c', '--continue',"
b"-        action='store_true', dest='continue_dl', default=True,"
b"-        help='Resume partially downloaded files/fragments (default)')"
b'-    filesystem.add_option('
b"-        '--no-continue',"
b"-        action='store_false', dest='continue_dl',"
b'-        help=('
b"-            'Do not resume partially downloaded fragments. '"
b"-            'If the file is not fragmented, restart download of the entire file'))"
b'-    filesystem.add_option('
b"-        '--part',"
b"-        action='store_false', dest='nopart', default=False,"
b"-        help='Use .part files instead of writing directly into output file (default)')"
b'-    filesystem.add_option('
b"-        '--no-part',"
b"-        action='store_true', dest='nopart',"
b"-        help='Do not use .part files - write directly into output file')"
b'-    filesystem.add_option('
b"-        '--mtime',"
b"-        action='store_true', dest='updatetime', default=None,"
b"-        help='Use the Last-modified header to set the file modification time')"
b'-    filesystem.add_option('
b"-        '--no-mtime',"
b"-        action='store_false', dest='updatetime',"
b"-        help='Do not use the Last-modified header to set the file modification time (default)')"
b'-    filesystem.add_option('
b"-        '--write-description',"
b"-        action='store_true', dest='writedescription', default=False,"
b"-        help='Write video description to a .description file')"
b'-    filesystem.add_option('
b"-        '--no-write-description',"
b"-        action='store_false', dest='writedescription',"
b"-        help='Do not write video description (default)')"
b'-    filesystem.add_option('
b"-        '--write-info-json',"
b"-        action='store_true', dest='writeinfojson', default=None,"
b"-        help='Write video metadata to a .info.json file (this may contain personal information)')"
b'-    filesystem.add_option('
b"-        '--no-write-info-json',"
b"-        action='store_false', dest='writeinfojson',"
b"-        help='Do not write video metadata (default)')"
b'-    filesystem.add_option('
b"-        '--write-annotations',"
b"-        action='store_true', dest='writeannotations', default=False,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    filesystem.add_option('
b"-        '--no-write-annotations',"
b"-        action='store_false', dest='writeannotations',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    filesystem.add_option('
b"-        '--write-playlist-metafiles',"
b"-        action='store_true', dest='allow_playlist_files', default=None,"
b'-        help=('
b"-            'Write playlist metadata in addition to the video metadata '"
b"-            'when using --write-info-json, --write-description etc. (default)'))"
b'-    filesystem.add_option('
b"-        '--no-write-playlist-metafiles',"
b"-        action='store_false', dest='allow_playlist_files',"
b"-        help='Do not write playlist metadata when using --write-info-json, --write-description etc.')"
b'-    filesystem.add_option('
b"-        '--clean-info-json', '--clean-infojson',"
b"-        action='store_true', dest='clean_infojson', default=None,"
b'-        help=('
b"-            'Remove some internal metadata such as filenames from the infojson (default)'))"
b'-    filesystem.add_option('
b"-        '--no-clean-info-json', '--no-clean-infojson',"
b"-        action='store_false', dest='clean_infojson',"
b"-        help='Write all fields to the infojson')"
b'-    filesystem.add_option('
b"-        '--write-comments', '--get-comments',"
b"-        action='store_true', dest='getcomments', default=False,"
b'-        help=('
b"-            'Retrieve video comments to be placed in the infojson. '"
b"-            'The comments are fetched even without this option if the extraction is known to be quick (Alias: --get-comments)'))"
b'-    filesystem.add_option('
b"-        '--no-write-comments', '--no-get-comments',"
b"-        action='store_false', dest='getcomments',"
b"-        help='Do not retrieve video comments unless the extraction is known to be quick (Alias: --no-get-comments)')"
b'-    filesystem.add_option('
b"-        '--load-info-json',"
b"-        dest='load_info_filename', metavar='FILE',"
b'-        help=\'JSON file containing the video information (created with the "--write-info-json" option)\')'
b'-    filesystem.add_option('
b"-        '--cookies',"
b"-        dest='cookiefile', metavar='FILE',"
b"-        help='Netscape formatted file to read cookies from and dump cookie jar in')"
b'-    filesystem.add_option('
b"-        '--no-cookies',"
b"-        action='store_const', const=None, dest='cookiefile', metavar='FILE',"
b"-        help='Do not read/dump cookies from/to file (default)')"
b'-    filesystem.add_option('
b"-        '--cookies-from-browser',"
b"-        dest='cookiesfrombrowser', metavar='BROWSER[+KEYRING][:PROFILE][::CONTAINER]',"
b'-        help=('
b"-            'The name of the browser to load cookies from. '"
b"+            u'allowed_keys': u'|'.join(imap(re.escape, OUTTMPL_TYPES.keys())),"
b"+            u'default_key': u'default',"
b'+        }, help=u\'Output filename template; see "OUTPUT TEMPLATE" for details\')'
b'+    filesystem.add_option('
b"+        u'--output-na-placeholder',"
b"+        dest=u'outtmpl_na_placeholder', metavar=u'TEXT', default=u'NA',"
b'+        help=(u\'Placeholder for unavailable fields in --output (default: "%default")\'))'
b'+    filesystem.add_option('
b"+        u'--autonumber-size',"
b"+        dest=u'autonumber_size', metavar=u'NUMBER', type=int,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    filesystem.add_option('
b"+        u'--autonumber-start',"
b"+        dest=u'autonumber_start', metavar=u'NUMBER', default=1, type=int,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    filesystem.add_option('
b"+        u'--restrict-filenames',"
b"+        action=u'store_true', dest=u'restrictfilenames', default=False,"
b'+        help=u\'Restrict filenames to only ASCII characters, and avoid "&" and spaces in filenames\')'
b'+    filesystem.add_option('
b"+        u'--no-restrict-filenames',"
b"+        action=u'store_false', dest=u'restrictfilenames',"
b'+        help=u\'Allow Unicode characters, "&" and spaces in filenames (default)\')'
b'+    filesystem.add_option('
b"+        u'--windows-filenames',"
b"+        action=u'store_true', dest=u'windowsfilenames', default=None,"
b"+        help=u'Force filenames to be Windows-compatible')"
b'+    filesystem.add_option('
b"+        u'--no-windows-filenames',"
b"+        action=u'store_false', dest=u'windowsfilenames',"
b"+        help=u'Sanitize filenames only minimally')"
b'+    filesystem.add_option('
b"+        u'--trim-filenames', u'--trim-file-names', metavar=u'LENGTH',"
b"+        dest=u'trim_file_name', default=0, type=int,"
b"+        help=u'Limit the filename length (excluding extension) to the specified number of characters')"
b'+    filesystem.add_option('
b"+        u'-w', u'--no-overwrites',"
b"+        action=u'store_false', dest=u'overwrites', default=None,"
b"+        help=u'Do not overwrite any files')"
b'+    filesystem.add_option('
b"+        u'--force-overwrites', u'--yes-overwrites',"
b"+        action=u'store_true', dest=u'overwrites',"
b"+        help=u'Overwrite all video and metadata files. This option includes --no-continue')"
b'+    filesystem.add_option('
b"+        u'--no-force-overwrites',"
b"+        action=u'store_const', dest=u'overwrites', const=None,"
b"+        help=u'Do not overwrite the video, but overwrite related files (default)')"
b'+    filesystem.add_option('
b"+        u'-c', u'--continue',"
b"+        action=u'store_true', dest=u'continue_dl', default=True,"
b"+        help=u'Resume partially downloaded files/fragments (default)')"
b'+    filesystem.add_option('
b"+        u'--no-continue',"
b"+        action=u'store_false', dest=u'continue_dl',"
b'+        help=('
b"+            u'Do not resume partially downloaded fragments. '"
b"+            u'If the file is not fragmented, restart download of the entire file'))"
b'+    filesystem.add_option('
b"+        u'--part',"
b"+        action=u'store_false', dest=u'nopart', default=False,"
b"+        help=u'Use .part files instead of writing directly into output file (default)')"
b'+    filesystem.add_option('
b"+        u'--no-part',"
b"+        action=u'store_true', dest=u'nopart',"
b"+        help=u'Do not use .part files - write directly into output file')"
b'+    filesystem.add_option('
b"+        u'--mtime',"
b"+        action=u'store_true', dest=u'updatetime', default=None,"
b"+        help=u'Use the Last-modified header to set the file modification time')"
b'+    filesystem.add_option('
b"+        u'--no-mtime',"
b"+        action=u'store_false', dest=u'updatetime',"
b"+        help=u'Do not use the Last-modified header to set the file modification time (default)')"
b'+    filesystem.add_option('
b"+        u'--write-description',"
b"+        action=u'store_true', dest=u'writedescription', default=False,"
b"+        help=u'Write video description to a .description file')"
b'+    filesystem.add_option('
b"+        u'--no-write-description',"
b"+        action=u'store_false', dest=u'writedescription',"
b"+        help=u'Do not write video description (default)')"
b'+    filesystem.add_option('
b"+        u'--write-info-json',"
b"+        action=u'store_true', dest=u'writeinfojson', default=None,"
b"+        help=u'Write video metadata to a .info.json file (this may contain personal information)')"
b'+    filesystem.add_option('
b"+        u'--no-write-info-json',"
b"+        action=u'store_false', dest=u'writeinfojson',"
b"+        help=u'Do not write video metadata (default)')"
b'+    filesystem.add_option('
b"+        u'--write-annotations',"
b"+        action=u'store_true', dest=u'writeannotations', default=False,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    filesystem.add_option('
b"+        u'--no-write-annotations',"
b"+        action=u'store_false', dest=u'writeannotations',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    filesystem.add_option('
b"+        u'--write-playlist-metafiles',"
b"+        action=u'store_true', dest=u'allow_playlist_files', default=None,"
b'+        help=('
b"+            u'Write playlist metadata in addition to the video metadata '"
b"+            u'when using --write-info-json, --write-description etc. (default)'))"
b'+    filesystem.add_option('
b"+        u'--no-write-playlist-metafiles',"
b"+        action=u'store_false', dest=u'allow_playlist_files',"
b"+        help=u'Do not write playlist metadata when using --write-info-json, --write-description etc.')"
b'+    filesystem.add_option('
b"+        u'--clean-info-json', u'--clean-infojson',"
b"+        action=u'store_true', dest=u'clean_infojson', default=None,"
b'+        help=('
b"+            u'Remove some internal metadata such as filenames from the infojson (default)'))"
b'+    filesystem.add_option('
b"+        u'--no-clean-info-json', u'--no-clean-infojson',"
b"+        action=u'store_false', dest=u'clean_infojson',"
b"+        help=u'Write all fields to the infojson')"
b'+    filesystem.add_option('
b"+        u'--write-comments', u'--get-comments',"
b"+        action=u'store_true', dest=u'getcomments', default=False,"
b'+        help=('
b"+            u'Retrieve video comments to be placed in the infojson. '"
b"+            u'The comments are fetched even without this option if the extraction is known to be quick (Alias: --get-comments)'))"
b'+    filesystem.add_option('
b"+        u'--no-write-comments', u'--no-get-comments',"
b"+        action=u'store_false', dest=u'getcomments',"
b"+        help=u'Do not retrieve video comments unless the extraction is known to be quick (Alias: --no-get-comments)')"
b'+    filesystem.add_option('
b"+        u'--load-info-json',"
b"+        dest=u'load_info_filename', metavar=u'FILE',"
b'+        help=u\'JSON file containing the video information (created with the "--write-info-json" option)\')'
b'+    filesystem.add_option('
b"+        u'--cookies',"
b"+        dest=u'cookiefile', metavar=u'FILE',"
b"+        help=u'Netscape formatted file to read cookies from and dump cookie jar in')"
b'+    filesystem.add_option('
b"+        u'--no-cookies',"
b"+        action=u'store_const', const=None, dest=u'cookiefile', metavar=u'FILE',"
b"+        help=u'Do not read/dump cookies from/to file (default)')"
b'+    filesystem.add_option('
b"+        u'--cookies-from-browser',"
b"+        dest=u'cookiesfrombrowser', metavar=u'BROWSER[+KEYRING][:PROFILE][::CONTAINER]',"
b'+        help=('
b"+            u'The name of the browser to load cookies from. '"
b'             f\'Currently supported browsers are: {", ".join(sorted(SUPPORTED_BROWSERS))}. \''
b"-            'Optionally, the KEYRING used for decrypting Chromium cookies on Linux, '"
b"-            'the name/path of the PROFILE to load cookies from, '"
b'-            \'and the CONTAINER name (if Firefox) ("none" for no container) \''
b"-            'can be given with their respective separators. '"
b"-            'By default, all containers of the most recently accessed profile are used. '"
b"+            u'Optionally, the KEYRING used for decrypting Chromium cookies on Linux, '"
b"+            u'the name/path of the PROFILE to load cookies from, '"
b'+            u\'and the CONTAINER name (if Firefox) ("none" for no container) \''
b"+            u'can be given with their respective separators. '"
b"+            u'By default, all containers of the most recently accessed profile are used. '"
b'             f\'Currently supported keyrings are: {", ".join(map(str.lower, sorted(SUPPORTED_KEYRINGS)))}\'))'
b'     filesystem.add_option('
b"-        '--no-cookies-from-browser',"
b"-        action='store_const', const=None, dest='cookiesfrombrowser',"
b"-        help='Do not load cookies from browser (default)')"
b'-    filesystem.add_option('
b"-        '--cache-dir', dest='cachedir', default=None, metavar='DIR',"
b'-        help=('
b"-            'Location in the filesystem where yt-dlp can store some downloaded information '"
b"-            '(such as client ids and signatures) permanently. By default ${XDG_CACHE_HOME}/yt-dlp'))"
b'-    filesystem.add_option('
b"-        '--no-cache-dir', action='store_false', dest='cachedir',"
b"-        help='Disable filesystem caching')"
b'-    filesystem.add_option('
b"-        '--rm-cache-dir',"
b"-        action='store_true', dest='rm_cachedir',"
b"-        help='Delete all filesystem cache files')"
b'-'
b"-    thumbnail = optparse.OptionGroup(parser, 'Thumbnail Options')"
b"+        u'--no-cookies-from-browser',"
b"+        action=u'store_const', const=None, dest=u'cookiesfrombrowser',"
b"+        help=u'Do not load cookies from browser (default)')"
b'+    filesystem.add_option('
b"+        u'--cache-dir', dest=u'cachedir', default=None, metavar=u'DIR',"
b'+        help=('
b"+            u'Location in the filesystem where yt-dlp can store some downloaded information '"
b"+            u'(such as client ids and signatures) permanently. By default ${XDG_CACHE_HOME}/yt-dlp'))"
b'+    filesystem.add_option('
b"+        u'--no-cache-dir', action=u'store_false', dest=u'cachedir',"
b"+        help=u'Disable filesystem caching')"
b'+    filesystem.add_option('
b"+        u'--rm-cache-dir',"
b"+        action=u'store_true', dest=u'rm_cachedir',"
b"+        help=u'Delete all filesystem cache files')"
b'+'
b"+    thumbnail = optparse.OptionGroup(parser, u'Thumbnail Options')"
b'     thumbnail.add_option('
b"-        '--write-thumbnail',"
b"-        action='callback', dest='writethumbnail', default=False,"
b"+        u'--write-thumbnail',"
b"+        action=u'callback', dest=u'writethumbnail', default=False,"
b'         # Should override --no-write-thumbnail, but not --write-all-thumbnail'
b'         callback=lambda option, _, __, parser: setattr('
b'             parser.values, option.dest, getattr(parser.values, option.dest) or True),'
b"-        help='Write thumbnail image to disk')"
b"+        help=u'Write thumbnail image to disk')"
b'     thumbnail.add_option('
b"-        '--no-write-thumbnail',"
b"-        action='store_false', dest='writethumbnail',"
b"-        help='Do not write thumbnail image to disk (default)')"
b"+        u'--no-write-thumbnail',"
b"+        action=u'store_false', dest=u'writethumbnail',"
b"+        help=u'Do not write thumbnail image to disk (default)')"
b'     thumbnail.add_option('
b"-        '--write-all-thumbnails',"
b"-        action='store_const', dest='writethumbnail', const='all',"
b"-        help='Write all thumbnail image formats to disk')"
b"+        u'--write-all-thumbnails',"
b"+        action=u'store_const', dest=u'writethumbnail', const=u'all',"
b"+        help=u'Write all thumbnail image formats to disk')"
b'     thumbnail.add_option('
b"-        '--list-thumbnails',"
b"-        action='store_true', dest='list_thumbnails', default=False,"
b"-        help='List available thumbnails of each video. Simulate unless --no-simulate is used')"
b'-'
b"-    link = optparse.OptionGroup(parser, 'Internet Shortcut Options')"
b"+        u'--list-thumbnails',"
b"+        action=u'store_true', dest=u'list_thumbnails', default=False,"
b"+        help=u'List available thumbnails of each video. Simulate unless --no-simulate is used')"
b'+'
b"+    link = optparse.OptionGroup(parser, u'Internet Shortcut Options')"
b'     link.add_option('
b"-        '--write-link',"
b"-        action='store_true', dest='writelink', default=False,"
b"-        help='Write an internet shortcut file, depending on the current platform (.url, .webloc or .desktop). The URL may be cached by the OS')"
b"+        u'--write-link',"
b"+        action=u'store_true', dest=u'writelink', default=False,"
b"+        help=u'Write an internet shortcut file, depending on the current platform (.url, .webloc or .desktop). The URL may be cached by the OS')"
b'     link.add_option('
b"-        '--write-url-link',"
b"-        action='store_true', dest='writeurllink', default=False,"
b"-        help='Write a .url Windows internet shortcut. The OS caches the URL based on the file path')"
b"+        u'--write-url-link',"
b"+        action=u'store_true', dest=u'writeurllink', default=False,"
b"+        help=u'Write a .url Windows internet shortcut. The OS caches the URL based on the file path')"
b'     link.add_option('
b"-        '--write-webloc-link',"
b"-        action='store_true', dest='writewebloclink', default=False,"
b"-        help='Write a .webloc macOS internet shortcut')"
b"+        u'--write-webloc-link',"
b"+        action=u'store_true', dest=u'writewebloclink', default=False,"
b"+        help=u'Write a .webloc macOS internet shortcut')"
b'     link.add_option('
b"-        '--write-desktop-link',"
b"-        action='store_true', dest='writedesktoplink', default=False,"
b"-        help='Write a .desktop Linux internet shortcut')"
b'-'
b"-    postproc = optparse.OptionGroup(parser, 'Post-Processing Options')"
b'-    postproc.add_option('
b"-        '-x', '--extract-audio',"
b"-        action='store_true', dest='extractaudio', default=False,"
b"-        help='Convert video files to audio-only files (requires ffmpeg and ffprobe)')"
b'-    postproc.add_option('
b"-        '--audio-format', metavar='FORMAT', dest='audioformat', default='best',"
b'-        help=('
b"-            'Format to convert the audio to when -x is used. '"
b"+        u'--write-desktop-link',"
b"+        action=u'store_true', dest=u'writedesktoplink', default=False,"
b"+        help=u'Write a .desktop Linux internet shortcut')"
b'+'
b"+    postproc = optparse.OptionGroup(parser, u'Post-Processing Options')"
b'+    postproc.add_option('
b"+        u'-x', u'--extract-audio',"
b"+        action=u'store_true', dest=u'extractaudio', default=False,"
b"+        help=u'Convert video files to audio-only files (requires ffmpeg and ffprobe)')"
b'+    postproc.add_option('
b"+        u'--audio-format', metavar=u'FORMAT', dest=u'audioformat', default=u'best',"
b'+        help=('
b"+            u'Format to convert the audio to when -x is used. '"
b'             f\'(currently supported: best (default), {", ".join(sorted(FFmpegExtractAudioPP.SUPPORTED_EXTS))}). \''
b"-            'You can specify multiple rules using similar syntax as --remux-video'))"
b'-    postproc.add_option('
b"-        '--audio-quality', metavar='QUALITY',"
b"-        dest='audioquality', default='5',"
b'-        help=('
b"-            'Specify ffmpeg audio quality to use when converting the audio with -x. '"
b"-            'Insert a value between 0 (best) and 10 (worst) for VBR or a specific bitrate like 128K (default %default)'))"
b'-    postproc.add_option('
b"-        '--remux-video',"
b"-        metavar='FORMAT', dest='remuxvideo', default=None,"
b'-        help=('
b"-            'Remux the video into another container if necessary '"
b"+            u'You can specify multiple rules using similar syntax as --remux-video'))"
b'+    postproc.add_option('
b"+        u'--audio-quality', metavar=u'QUALITY',"
b"+        dest=u'audioquality', default=u'5',"
b'+        help=('
b"+            u'Specify ffmpeg audio quality to use when converting the audio with -x. '"
b"+            u'Insert a value between 0 (best) and 10 (worst) for VBR or a specific bitrate like 128K (default %default)'))"
b'+    postproc.add_option('
b"+        u'--remux-video',"
b"+        metavar=u'FORMAT', dest=u'remuxvideo', default=None,"
b'+        help=('
b"+            u'Remux the video into another container if necessary '"
b'             f\'(currently supported: {", ".join(FFmpegVideoRemuxerPP.SUPPORTED_EXTS)}). \''
b"-            'If the target container does not support the video/audio codec, remuxing will fail. You can specify multiple rules; '"
b'-            \'e.g. "aac>m4a/mov>mp4/mkv" will remux aac to m4a, mov to mp4 and anything else to mkv\'))'
b'-    postproc.add_option('
b"-        '--recode-video',"
b"-        metavar='FORMAT', dest='recodevideo', default=None,"
b"-        help='Re-encode the video into another format if necessary. The syntax and supported formats are the same as --remux-video')"
b'-    postproc.add_option('
b"-        '--postprocessor-args', '--ppa',"
b"-        metavar='NAME:ARGS', dest='postprocessor_args', default={}, type='str',"
b"-        action='callback', callback=_dict_from_options_callback,"
b"+            u'If the target container does not support the video/audio codec, remuxing will fail. You can specify multiple rules; '"
b'+            u\'e.g. "aac>m4a/mov>mp4/mkv" will remux aac to m4a, mov to mp4 and anything else to mkv\'))'
b'+    postproc.add_option('
b"+        u'--recode-video',"
b"+        metavar=u'FORMAT', dest=u'recodevideo', default=None,"
b"+        help=u'Re-encode the video into another format if necessary. The syntax and supported formats are the same as --remux-video')"
b'+    postproc.add_option('
b"+        u'--postprocessor-args', u'--ppa',"
b"+        metavar=u'NAME:ARGS', dest=u'postprocessor_args', default={}, type=u'str',"
b"+        action=u'callback', callback=_dict_from_options_callback,"
b'         callback_kwargs={'
b"-            'allowed_keys': r'\\w+(?:\\+\\w+)?',"
b"-            'default_key': 'default-compat',"
b"-            'process': shlex.split,"
b"-            'multiple_keys': False,"
b"+            u'allowed_keys': ur'\\w+(?:\\+\\w+)?',"
b"+            u'default_key': u'default-compat',"
b"+            u'process': shlex.split,"
b"+            u'multiple_keys': False,"
b'         }, help=('
b"-            'Give these arguments to the postprocessors. '"
b'-            \'Specify the postprocessor/executable name and the arguments separated by a colon ":" \''
b"-            'to give the argument to the specified postprocessor/executable. Supported PP are: '"
b"-            'Merger, ModifyChapters, SplitChapters, ExtractAudio, VideoRemuxer, VideoConvertor, '"
b"-            'Metadata, EmbedSubtitle, EmbedThumbnail, SubtitlesConvertor, ThumbnailsConvertor, '"
b"-            'FixupStretched, FixupM4a, FixupM3u8, FixupTimestamp and FixupDuration. '"
b"-            'The supported executables are: AtomicParsley, FFmpeg and FFprobe. '"
b'-            \'You can also specify "PP+EXE:ARGS" to give the arguments to the specified executable \''
b"-            'only when being used by the specified postprocessor. Additionally, for ffmpeg/ffprobe, '"
b'-            \'"_i"/"_o" can be appended to the prefix optionally followed by a number to pass the argument \''
b'-            \'before the specified input/output file, e.g. --ppa "Merger+ffmpeg_i1:-v quiet". \''
b"-            'You can use this option multiple times to give different arguments to different '"
b"-            'postprocessors. (Alias: --ppa)'))"
b'-    postproc.add_option('
b"-        '-k', '--keep-video',"
b"-        action='store_true', dest='keepvideo', default=False,"
b"-        help='Keep the intermediate video file on disk after post-processing')"
b'-    postproc.add_option('
b"-        '--no-keep-video',"
b"-        action='store_false', dest='keepvideo',"
b"-        help='Delete the intermediate video file after post-processing (default)')"
b'-    postproc.add_option('
b"-        '--post-overwrites',"
b"-        action='store_false', dest='nopostoverwrites',"
b"-        help='Overwrite post-processed files (default)')"
b'-    postproc.add_option('
b"-        '--no-post-overwrites',"
b"-        action='store_true', dest='nopostoverwrites', default=False,"
b"-        help='Do not overwrite post-processed files')"
b'-    postproc.add_option('
b"-        '--embed-subs',"
b"-        action='store_true', dest='embedsubtitles', default=False,"
b"-        help='Embed subtitles in the video (only for mp4, webm and mkv videos)')"
b'-    postproc.add_option('
b"-        '--no-embed-subs',"
b"-        action='store_false', dest='embedsubtitles',"
b"-        help='Do not embed subtitles (default)')"
b'-    postproc.add_option('
b"-        '--embed-thumbnail',"
b"-        action='store_true', dest='embedthumbnail', default=False,"
b"-        help='Embed thumbnail in the video as cover art')"
b'-    postproc.add_option('
b"-        '--no-embed-thumbnail',"
b"-        action='store_false', dest='embedthumbnail',"
b"-        help='Do not embed thumbnail (default)')"
b'-    postproc.add_option('
b"-        '--embed-metadata', '--add-metadata',"
b"-        action='store_true', dest='addmetadata', default=False,"
b'-        help=('
b"-            'Embed metadata to the video file. Also embeds chapters/infojson if present '"
b"-            'unless --no-embed-chapters/--no-embed-info-json are used (Alias: --add-metadata)'))"
b'-    postproc.add_option('
b"-        '--no-embed-metadata', '--no-add-metadata',"
b"-        action='store_false', dest='addmetadata',"
b"-        help='Do not add metadata to file (default) (Alias: --no-add-metadata)')"
b'-    postproc.add_option('
b"-        '--embed-chapters', '--add-chapters',"
b"-        action='store_true', dest='addchapters', default=None,"
b"-        help='Add chapter markers to the video file (Alias: --add-chapters)')"
b'-    postproc.add_option('
b"-        '--no-embed-chapters', '--no-add-chapters',"
b"-        action='store_false', dest='addchapters',"
b"-        help='Do not add chapter markers (default) (Alias: --no-add-chapters)')"
b'-    postproc.add_option('
b"-        '--embed-info-json',"
b"-        action='store_true', dest='embed_infojson', default=None,"
b"-        help='Embed the infojson as an attachment to mkv/mka video files')"
b'-    postproc.add_option('
b"-        '--no-embed-info-json',"
b"-        action='store_false', dest='embed_infojson',"
b"-        help='Do not embed the infojson as an attachment to the video file')"
b'-    postproc.add_option('
b"-        '--metadata-from-title',"
b"-        metavar='FORMAT', dest='metafromtitle',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    postproc.add_option('
b"-        '--parse-metadata',"
b"-        metavar='[WHEN:]FROM:TO', dest='parse_metadata', **when_prefix('pre_process'),"
b'-        help=('
b'-            \'Parse additional metadata like title/artist from other fields; see "MODIFYING METADATA" for details. \''
b'-            \'Supported values of "WHEN" are the same as that of --use-postprocessor (default: pre_process)\'))'
b'-    postproc.add_option('
b"-        '--replace-in-metadata',"
b"-        dest='parse_metadata', metavar='[WHEN:]FIELDS REGEX REPLACE', nargs=3, **when_prefix('pre_process'),"
b'-        help=('
b"-            'Replace text in a metadata field using the given regex. This option can be used multiple times. '"
b'-            \'Supported values of "WHEN" are the same as that of --use-postprocessor (default: pre_process)\'))'
b'-    postproc.add_option('
b"-        '--xattrs', '--xattr',"
b"-        action='store_true', dest='xattrs', default=False,"
b"-        help='Write metadata to the video file\\'s xattrs (using Dublin Core and XDG standards)')"
b'-    postproc.add_option('
b"-        '--concat-playlist',"
b"-        metavar='POLICY', dest='concat_playlist', default='multi_video',"
b"-        choices=('never', 'always', 'multi_video'),"
b'-        help=('
b'-            \'Concatenate videos in a playlist. One of "never", "always", or \''
b'-            \'"multi_video" (default; only when the videos form a single show). \''
b"-            'All the video files must have the same codecs and number of streams to be concatenable. '"
b'-            \'The "pl_video:" prefix can be used with "--paths" and "--output" to \''
b'-            \'set the output filename for the concatenated files. See "OUTPUT TEMPLATE" for details\'))'
b'-    postproc.add_option('
b"-        '--fixup',"
b"-        metavar='POLICY', dest='fixup', default=None,"
b"-        choices=('never', 'ignore', 'warn', 'detect_or_warn', 'force'),"
b'-        help=('
b"-            'Automatically correct known faults of the file. '"
b"-            'One of never (do nothing), warn (only emit a warning), '"
b"-            'detect_or_warn (the default; fix the file if we can, warn otherwise), '"
b"-            'force (try fixing even if the file already exists)'))"
b'-    postproc.add_option('
b"-        '--prefer-avconv', '--no-prefer-ffmpeg',"
b"-        action='store_false', dest='prefer_ffmpeg',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    postproc.add_option('
b"-        '--prefer-ffmpeg', '--no-prefer-avconv',"
b"-        action='store_true', dest='prefer_ffmpeg', default=True,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    postproc.add_option('
b"-        '--ffmpeg-location', '--avconv-location', metavar='PATH',"
b"-        dest='ffmpeg_location',"
b"-        help='Location of the ffmpeg binary; either the path to the binary or its containing directory')"
b'-    postproc.add_option('
b"-        '--exec',"
b"-        metavar='[WHEN:]CMD', dest='exec_cmd', **when_prefix('after_move'),"
b'-        help=('
b'-            \'Execute a command, optionally prefixed with when to execute it, separated by a ":". \''
b'-            \'Supported values of "WHEN" are the same as that of --use-postprocessor (default: after_move). \''
b"-            'The same syntax as the output template can be used to pass any field as arguments to the command. '"
b"-            'If no fields are passed, %(filepath,_filename|)q is appended to the end of the command. '"
b"-            'This option can be used multiple times'))"
b'-    postproc.add_option('
b"-        '--no-exec',"
b"-        action='store_const', dest='exec_cmd', const={},"
b"-        help='Remove any previously defined --exec')"
b'-    postproc.add_option('
b"-        '--exec-before-download', metavar='CMD',"
b"-        action='append', dest='exec_before_dl_cmd',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    postproc.add_option('
b"-        '--no-exec-before-download',"
b"-        action='store_const', dest='exec_before_dl_cmd', const=None,"
b'-        help=optparse.SUPPRESS_HELP)'
b'-    postproc.add_option('
b"-        '--convert-subs', '--convert-sub', '--convert-subtitles',"
b"-        metavar='FORMAT', dest='convertsubtitles', default=None,"
b'-        help=('
b"-            'Convert the subtitles to another format '"
b"+            u'Give these arguments to the postprocessors. '"
b'+            u\'Specify the postprocessor/executable name and the arguments separated by a colon ":" \''
b"+            u'to give the argument to the specified postprocessor/executable. Supported PP are: '"
b"+            u'Merger, ModifyChapters, SplitChapters, ExtractAudio, VideoRemuxer, VideoConvertor, '"
b"+            u'Metadata, EmbedSubtitle, EmbedThumbnail, SubtitlesConvertor, ThumbnailsConvertor, '"
b"+            u'FixupStretched, FixupM4a, FixupM3u8, FixupTimestamp and FixupDuration. '"
b"+            u'The supported executables are: AtomicParsley, FFmpeg and FFprobe. '"
b'+            u\'You can also specify "PP+EXE:ARGS" to give the arguments to the specified executable \''
b"+            u'only when being used by the specified postprocessor. Additionally, for ffmpeg/ffprobe, '"
b'+            u\'"_i"/"_o" can be appended to the prefix optionally followed by a number to pass the argument \''
b'+            u\'before the specified input/output file, e.g. --ppa "Merger+ffmpeg_i1:-v quiet". \''
b"+            u'You can use this option multiple times to give different arguments to different '"
b"+            u'postprocessors. (Alias: --ppa)'))"
b'+    postproc.add_option('
b"+        u'-k', u'--keep-video',"
b"+        action=u'store_true', dest=u'keepvideo', default=False,"
b"+        help=u'Keep the intermediate video file on disk after post-processing')"
b'+    postproc.add_option('
b"+        u'--no-keep-video',"
b"+        action=u'store_false', dest=u'keepvideo',"
b"+        help=u'Delete the intermediate video file after post-processing (default)')"
b'+    postproc.add_option('
b"+        u'--post-overwrites',"
b"+        action=u'store_false', dest=u'nopostoverwrites',"
b"+        help=u'Overwrite post-processed files (default)')"
b'+    postproc.add_option('
b"+        u'--no-post-overwrites',"
b"+        action=u'store_true', dest=u'nopostoverwrites', default=False,"
b"+        help=u'Do not overwrite post-processed files')"
b'+    postproc.add_option('
b"+        u'--embed-subs',"
b"+        action=u'store_true', dest=u'embedsubtitles', default=False,"
b"+        help=u'Embed subtitles in the video (only for mp4, webm and mkv videos)')"
b'+    postproc.add_option('
b"+        u'--no-embed-subs',"
b"+        action=u'store_false', dest=u'embedsubtitles',"
b"+        help=u'Do not embed subtitles (default)')"
b'+    postproc.add_option('
b"+        u'--embed-thumbnail',"
b"+        action=u'store_true', dest=u'embedthumbnail', default=False,"
b"+        help=u'Embed thumbnail in the video as cover art')"
b'+    postproc.add_option('
b"+        u'--no-embed-thumbnail',"
b"+        action=u'store_false', dest=u'embedthumbnail',"
b"+        help=u'Do not embed thumbnail (default)')"
b'+    postproc.add_option('
b"+        u'--embed-metadata', u'--add-metadata',"
b"+        action=u'store_true', dest=u'addmetadata', default=False,"
b'+        help=('
b"+            u'Embed metadata to the video file. Also embeds chapters/infojson if present '"
b"+            u'unless --no-embed-chapters/--no-embed-info-json are used (Alias: --add-metadata)'))"
b'+    postproc.add_option('
b"+        u'--no-embed-metadata', u'--no-add-metadata',"
b"+        action=u'store_false', dest=u'addmetadata',"
b"+        help=u'Do not add metadata to file (default) (Alias: --no-add-metadata)')"
b'+    postproc.add_option('
b"+        u'--embed-chapters', u'--add-chapters',"
b"+        action=u'store_true', dest=u'addchapters', default=None,"
b"+        help=u'Add chapter markers to the video file (Alias: --add-chapters)')"
b'+    postproc.add_option('
b"+        u'--no-embed-chapters', u'--no-add-chapters',"
b"+        action=u'store_false', dest=u'addchapters',"
b"+        help=u'Do not add chapter markers (default) (Alias: --no-add-chapters)')"
b'+    postproc.add_option('
b"+        u'--embed-info-json',"
b"+        action=u'store_true', dest=u'embed_infojson', default=None,"
b"+        help=u'Embed the infojson as an attachment to mkv/mka video files')"
b'+    postproc.add_option('
b"+        u'--no-embed-info-json',"
b"+        action=u'store_false', dest=u'embed_infojson',"
b"+        help=u'Do not embed the infojson as an attachment to the video file')"
b'+    postproc.add_option('
b"+        u'--metadata-from-title',"
b"+        metavar=u'FORMAT', dest=u'metafromtitle',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    postproc.add_option('
b"+        u'--parse-metadata',"
b"+        metavar=u'[WHEN:]FROM:TO', dest=u'parse_metadata', **when_prefix(u'pre_process'),"
b'+        help=('
b'+            u\'Parse additional metadata like title/artist from other fields; see "MODIFYING METADATA" for details. \''
b'+            u\'Supported values of "WHEN" are the same as that of --use-postprocessor (default: pre_process)\'))'
b'+    postproc.add_option('
b"+        u'--replace-in-metadata',"
b"+        dest=u'parse_metadata', metavar=u'[WHEN:]FIELDS REGEX REPLACE', nargs=3, **when_prefix(u'pre_process'),"
b'+        help=('
b"+            u'Replace text in a metadata field using the given regex. This option can be used multiple times. '"
b'+            u\'Supported values of "WHEN" are the same as that of --use-postprocessor (default: pre_process)\'))'
b'+    postproc.add_option('
b"+        u'--xattrs', u'--xattr',"
b"+        action=u'store_true', dest=u'xattrs', default=False,"
b"+        help=u'Write metadata to the video file\\'s xattrs (using Dublin Core and XDG standards)')"
b'+    postproc.add_option('
b"+        u'--concat-playlist',"
b"+        metavar=u'POLICY', dest=u'concat_playlist', default=u'multi_video',"
b"+        choices=(u'never', u'always', u'multi_video'),"
b'+        help=('
b'+            u\'Concatenate videos in a playlist. One of "never", "always", or \''
b'+            u\'"multi_video" (default; only when the videos form a single show). \''
b"+            u'All the video files must have the same codecs and number of streams to be concatenable. '"
b'+            u\'The "pl_video:" prefix can be used with "--paths" and "--output" to \''
b'+            u\'set the output filename for the concatenated files. See "OUTPUT TEMPLATE" for details\'))'
b'+    postproc.add_option('
b"+        u'--fixup',"
b"+        metavar=u'POLICY', dest=u'fixup', default=None,"
b"+        choices=(u'never', u'ignore', u'warn', u'detect_or_warn', u'force'),"
b'+        help=('
b"+            u'Automatically correct known faults of the file. '"
b"+            u'One of never (do nothing), warn (only emit a warning), '"
b"+            u'detect_or_warn (the default; fix the file if we can, warn otherwise), '"
b"+            u'force (try fixing even if the file already exists)'))"
b'+    postproc.add_option('
b"+        u'--prefer-avconv', u'--no-prefer-ffmpeg',"
b"+        action=u'store_false', dest=u'prefer_ffmpeg',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    postproc.add_option('
b"+        u'--prefer-ffmpeg', u'--no-prefer-avconv',"
b"+        action=u'store_true', dest=u'prefer_ffmpeg', default=True,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    postproc.add_option('
b"+        u'--ffmpeg-location', u'--avconv-location', metavar=u'PATH',"
b"+        dest=u'ffmpeg_location',"
b"+        help=u'Location of the ffmpeg binary; either the path to the binary or its containing directory')"
b'+    postproc.add_option('
b"+        u'--exec',"
b"+        metavar=u'[WHEN:]CMD', dest=u'exec_cmd', **when_prefix(u'after_move'),"
b'+        help=('
b'+            u\'Execute a command, optionally prefixed with when to execute it, separated by a ":". \''
b'+            u\'Supported values of "WHEN" are the same as that of --use-postprocessor (default: after_move). \''
b"+            u'The same syntax as the output template can be used to pass any field as arguments to the command. '"
b"+            u'If no fields are passed, %(filepath,_filename|)q is appended to the end of the command. '"
b"+            u'This option can be used multiple times'))"
b'+    postproc.add_option('
b"+        u'--no-exec',"
b"+        action=u'store_const', dest=u'exec_cmd', const={},"
b"+        help=u'Remove any previously defined --exec')"
b'+    postproc.add_option('
b"+        u'--exec-before-download', metavar=u'CMD',"
b"+        action=u'append', dest=u'exec_before_dl_cmd',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    postproc.add_option('
b"+        u'--no-exec-before-download',"
b"+        action=u'store_const', dest=u'exec_before_dl_cmd', const=None,"
b'+        help=optparse.SUPPRESS_HELP)'
b'+    postproc.add_option('
b"+        u'--convert-subs', u'--convert-sub', u'--convert-subtitles',"
b"+        metavar=u'FORMAT', dest=u'convertsubtitles', default=None,"
b'+        help=('
b"+            u'Convert the subtitles to another format '"
b'             f\'(currently supported: {", ".join(sorted(FFmpegSubtitlesConvertorPP.SUPPORTED_EXTS))}). \''
b'-            \'Use "--convert-subs none" to disable conversion (default) (Alias: --convert-subtitles)\'))'
b'-    postproc.add_option('
b"-        '--convert-thumbnails',"
b"-        metavar='FORMAT', dest='convertthumbnails', default=None,"
b'-        help=('
b"-            'Convert the thumbnails to another format '"
b'+            u\'Use "--convert-subs none" to disable conversion (default) (Alias: --convert-subtitles)\'))'
b'+    postproc.add_option('
b"+        u'--convert-thumbnails',"
b"+        metavar=u'FORMAT', dest=u'convertthumbnails', default=None,"
b'+        help=('
b"+            u'Convert the thumbnails to another format '"
b'             f\'(currently supported: {", ".join(sorted(FFmpegThumbnailsConvertorPP.SUPPORTED_EXTS))}). \''
b'-            \'You can specify multiple rules using similar syntax as "--remux-video". \''
b'-            \'Use "--convert-thumbnails none" to disable conversion (default)\'))'
b'-    postproc.add_option('
b"-        '--split-chapters', '--split-tracks',"
b"-        dest='split_chapters', action='store_true', default=False,"
b'-        help=('
b"-            'Split video into multiple files based on internal chapters. '"
b'-            \'The "chapter:" prefix can be used with "--paths" and "--output" to \''
b'-            \'set the output filename for the split files. See "OUTPUT TEMPLATE" for details\'))'
b'-    postproc.add_option('
b"-        '--no-split-chapters', '--no-split-tracks',"
b"-        dest='split_chapters', action='store_false',"
b"-        help='Do not split video based on chapters (default)')"
b'-    postproc.add_option('
b"-        '--remove-chapters',"
b"-        metavar='REGEX', dest='remove_chapters', action='append',"
b'-        help=('
b"-            'Remove chapters whose title matches the given regular expression. '"
b"-            'The syntax is the same as --download-sections. This option can be used multiple times'))"
b'-    postproc.add_option('
b"-        '--no-remove-chapters', dest='remove_chapters', action='store_const', const=None,"
b"-        help='Do not remove any chapters from the file (default)')"
b'-    postproc.add_option('
b"-        '--force-keyframes-at-cuts',"
b"-        action='store_true', dest='force_keyframes_at_cuts', default=False,"
b'-        help=('
b"-            'Force keyframes at cuts when downloading/splitting/removing sections. '"
b"-            'This is slow due to needing a re-encode, but the resulting video may have fewer artifacts around the cuts'))"
b'-    postproc.add_option('
b"-        '--no-force-keyframes-at-cuts',"
b"-        action='store_false', dest='force_keyframes_at_cuts',"
b"-        help='Do not force keyframes around the chapters when cutting/splitting (default)')"
b"-    _postprocessor_opts_parser = lambda key, val='': ("
b"-        *(item.split('=', 1) for item in (val.split(';') if val else [])),"
b"-        ('key', remove_end(key, 'PP')))"
b'-    postproc.add_option('
b"-        '--use-postprocessor',"
b"-        metavar='NAME[:ARGS]', dest='add_postprocessors', default=[], type='str',"
b"-        action='callback', callback=_list_from_options_callback,"
b'+            u\'You can specify multiple rules using similar syntax as "--remux-video". \''
b'+            u\'Use "--convert-thumbnails none" to disable conversion (default)\'))'
b'+    postproc.add_option('
b"+        u'--split-chapters', u'--split-tracks',"
b"+        dest=u'split_chapters', action=u'store_true', default=False,"
b'+        help=('
b"+            u'Split video into multiple files based on internal chapters. '"
b'+            u\'The "chapter:" prefix can be used with "--paths" and "--output" to \''
b'+            u\'set the output filename for the split files. See "OUTPUT TEMPLATE" for details\'))'
b'+    postproc.add_option('
b"+        u'--no-split-chapters', u'--no-split-tracks',"
b"+        dest=u'split_chapters', action=u'store_false',"
b"+        help=u'Do not split video based on chapters (default)')"
b'+    postproc.add_option('
b"+        u'--remove-chapters',"
b"+        metavar=u'REGEX', dest=u'remove_chapters', action=u'append',"
b'+        help=('
b"+            u'Remove chapters whose title matches the given regular expression. '"
b"+            u'The syntax is the same as --download-sections. This option can be used multiple times'))"
b'+    postproc.add_option('
b"+        u'--no-remove-chapters', dest=u'remove_chapters', action=u'store_const', const=None,"
b"+        help=u'Do not remove any chapters from the file (default)')"
b'+    postproc.add_option('
b"+        u'--force-keyframes-at-cuts',"
b"+        action=u'store_true', dest=u'force_keyframes_at_cuts', default=False,"
b'+        help=('
b"+            u'Force keyframes at cuts when downloading/splitting/removing sections. '"
b"+            u'This is slow due to needing a re-encode, but the resulting video may have fewer artifacts around the cuts'))"
b'+    postproc.add_option('
b"+        u'--no-force-keyframes-at-cuts',"
b"+        action=u'store_false', dest=u'force_keyframes_at_cuts',"
b"+        help=u'Do not force keyframes around the chapters when cutting/splitting (default)')"
b"+    _postprocessor_opts_parser = lambda key, val=u'': ("
b"+        *(item.split(u'=', 1) for item in (val.split(u';') if val else [])),"
b"+        (u'key', remove_end(key, u'PP')))"
b'+    postproc.add_option('
b"+        u'--use-postprocessor',"
b"+        metavar=u'NAME[:ARGS]', dest=u'add_postprocessors', default=[], type=u'str',"
b"+        action=u'callback', callback=_list_from_options_callback,"
b'         callback_kwargs={'
b"-            'delim': None,"
b"-            'process': lambda val: dict(_postprocessor_opts_parser(*val.split(':', 1))),"
b"+            u'delim': None,"
b"+            u'process': lambda val: dict(_postprocessor_opts_parser(*val.split(u':', 1))),"
b'         }, help=('
b"-            'The (case-sensitive) name of plugin postprocessors to be enabled, '"
b'-            \'and (optionally) arguments to be passed to it, separated by a colon ":". \''
b'-            \'ARGS are a semicolon ";" delimited list of NAME=VALUE. \''
b'-            \'The "when" argument determines when the postprocessor is invoked. \''
b'-            \'It can be one of "pre_process" (after video extraction), "after_filter" (after video passes filter), \''
b'-            \'"video" (after --format; before --print/--output), "before_dl" (before each video download), \''
b'-            \'"post_process" (after each video download; default), \''
b'-            \'"after_move" (after moving the video file to its final location), \''
b'-            \'"after_video" (after downloading and processing all formats of a video), \''
b'-            \'or "playlist" (at end of playlist). \''
b"-            'This option can be used multiple times to add different postprocessors'))"
b'-'
b"-    sponsorblock = optparse.OptionGroup(parser, 'SponsorBlock Options', description=("
b"-        'Make chapter entries for, or remove various segments (sponsor, introductions, etc.) '"
b"-        'from downloaded YouTube videos using the SponsorBlock API (https://sponsor.ajay.app)'))"
b"+            u'The (case-sensitive) name of plugin postprocessors to be enabled, '"
b'+            u\'and (optionally) arguments to be passed to it, separated by a colon ":". \''
b'+            u\'ARGS are a semicolon ";" delimited list of NAME=VALUE. \''
b'+            u\'The "when" argument determines when the postprocessor is invoked. \''
b'+            u\'It can be one of "pre_process" (after video extraction), "after_filter" (after video passes filter), \''
b'+            u\'"video" (after --format; before --print/--output), "before_dl" (before each video download), \''
b'+            u\'"post_process" (after each video download; default), \''
b'+            u\'"after_move" (after moving the video file to its final location), \''
b'+            u\'"after_video" (after downloading and processing all formats of a video), \''
b'+            u\'or "playlist" (at end of playlist). \''
b"+            u'This option can be used multiple times to add different postprocessors'))"
b'+'
b"+    sponsorblock = optparse.OptionGroup(parser, u'SponsorBlock Options', description=("
b"+        u'Make chapter entries for, or remove various segments (sponsor, introductions, etc.) '"
b"+        u'from downloaded YouTube videos using the SponsorBlock API (https://sponsor.ajay.app)'))"
b'     sponsorblock.add_option('
b"-        '--sponsorblock-mark', metavar='CATS',"
b"-        dest='sponsorblock_mark', default=set(), action='callback', type='str',"
b"+        u'--sponsorblock-mark', metavar=u'CATS',"
b"+        dest=u'sponsorblock_mark', default=set(), action=u'callback', type=u'str',"
b'         callback=_set_from_options_callback, callback_kwargs={'
b"-            'allowed_values': SponsorBlockPP.CATEGORIES.keys(),"
b"-            'aliases': {'default': ['all']},"
b"+            u'allowed_values': SponsorBlockPP.CATEGORIES.keys(),"
b"+            u'aliases': {u'default': [u'all']},"
b'         }, help=('
b"-            'SponsorBlock categories to create chapters for, separated by commas. '"
b"+            u'SponsorBlock categories to create chapters for, separated by commas. '"
b'             f\'Available categories are {", ".join(SponsorBlockPP.CATEGORIES.keys())}, all and default (=all). \''
b'-            \'You can prefix the category with a "-" to exclude it. See [1] for descriptions of the categories. \''
b"-            'E.g. --sponsorblock-mark all,-preview [1] https://wiki.sponsor.ajay.app/w/Segment_Categories'))"
b'+            u\'You can prefix the category with a "-" to exclude it. See [1] for descriptions of the categories. \''
b"+            u'E.g. --sponsorblock-mark all,-preview [1] https://wiki.sponsor.ajay.app/w/Segment_Categories'))"
b'     sponsorblock.add_option('
b"-        '--sponsorblock-remove', metavar='CATS',"
b"-        dest='sponsorblock_remove', default=set(), action='callback', type='str',"
b"+        u'--sponsorblock-remove', metavar=u'CATS',"
b"+        dest=u'sponsorblock_remove', default=set(), action=u'callback', type=u'str',"
b'         callback=_set_from_options_callback, callback_kwargs={'
b"-            'allowed_values': set(SponsorBlockPP.CATEGORIES.keys()) - set(SponsorBlockPP.NON_SKIPPABLE_CATEGORIES.keys()),"
b"+            u'allowed_values': set(SponsorBlockPP.CATEGORIES.keys()) - set(SponsorBlockPP.NON_SKIPPABLE_CATEGORIES.keys()),"
b'             # Note: From https://wiki.sponsor.ajay.app/w/Types:'
b'             # The filler category is very aggressive.'
b'             # It is strongly recommended to not use this in a client by default.'
b"-            'aliases': {'default': ['all', '-filler']},"
b"+            u'aliases': {u'default': [u'all', u'-filler']},"
b'         }, help=('
b"-            'SponsorBlock categories to be removed from the video file, separated by commas. '"
b"-            'If a category is present in both mark and remove, remove takes precedence. '"
b"-            'The syntax and available categories are the same as for --sponsorblock-mark '"
b'-            \'except that "default" refers to "all,-filler" \''
b"+            u'SponsorBlock categories to be removed from the video file, separated by commas. '"
b"+            u'If a category is present in both mark and remove, remove takes precedence. '"
b"+            u'The syntax and available categories are the same as for --sponsorblock-mark '"
b'+            u\'except that "default" refers to "all,-filler" \''
b'             f\'and {", ".join(SponsorBlockPP.NON_SKIPPABLE_CATEGORIES.keys())} are not available\'))'
b'     sponsorblock.add_option('
b"-        '--sponsorblock-chapter-title', metavar='TEMPLATE',"
b"-        default=DEFAULT_SPONSORBLOCK_CHAPTER_TITLE, dest='sponsorblock_chapter_title',"
b'-        help=('
b"-            'An output template for the title of the SponsorBlock chapters created by --sponsorblock-mark. '"
b"-            'The only available fields are start_time, end_time, category, categories, name, category_names. '"
b'-            \'Defaults to "%default"\'))'
b"+        u'--sponsorblock-chapter-title', metavar=u'TEMPLATE',"
b"+        default=DEFAULT_SPONSORBLOCK_CHAPTER_TITLE, dest=u'sponsorblock_chapter_title',"
b'+        help=('
b"+            u'An output template for the title of the SponsorBlock chapters created by --sponsorblock-mark. '"
b"+            u'The only available fields are start_time, end_time, category, categories, name, category_names. '"
b'+            u\'Defaults to "%default"\'))'
b'     sponsorblock.add_option('
b"-        '--no-sponsorblock', default=False,"
b"-        action='store_true', dest='no_sponsorblock',"
b"-        help='Disable both --sponsorblock-mark and --sponsorblock-remove')"
b"+        u'--no-sponsorblock', default=False,"
b"+        action=u'store_true', dest=u'no_sponsorblock',"
b"+        help=u'Disable both --sponsorblock-mark and --sponsorblock-remove')"
b'     sponsorblock.add_option('
b"-        '--sponsorblock-api', metavar='URL',"
b"-        default='https://sponsor.ajay.app', dest='sponsorblock_api',"
b"-        help='SponsorBlock API location, defaults to %default')"
b"+        u'--sponsorblock-api', metavar=u'URL',"
b"+        default=u'https://sponsor.ajay.app', dest=u'sponsorblock_api',"
b"+        help=u'SponsorBlock API location, defaults to %default')"
b' '
b'     sponsorblock.add_option('
b"-        '--sponskrub',"
b"-        action='store_true', dest='sponskrub', default=False,"
b"+        u'--sponskrub',"
b"+        action=u'store_true', dest=u'sponskrub', default=False,"
b'         help=optparse.SUPPRESS_HELP)'
b'     sponsorblock.add_option('
b"-        '--no-sponskrub',"
b"-        action='store_false', dest='sponskrub',"
b"+        u'--no-sponskrub',"
b"+        action=u'store_false', dest=u'sponskrub',"
b'         help=optparse.SUPPRESS_HELP)'
b'     sponsorblock.add_option('
b"-        '--sponskrub-cut', default=False,"
b"-        action='store_true', dest='sponskrub_cut',"
b"+        u'--sponskrub-cut', default=False,"
b"+        action=u'store_true', dest=u'sponskrub_cut',"
b'         help=optparse.SUPPRESS_HELP)'
b'     sponsorblock.add_option('
b"-        '--no-sponskrub-cut',"
b"-        action='store_false', dest='sponskrub_cut',"
b"+        u'--no-sponskrub-cut',"
b"+        action=u'store_false', dest=u'sponskrub_cut',"
b'         help=optparse.SUPPRESS_HELP)'
b'     sponsorblock.add_option('
b"-        '--sponskrub-force', default=False,"
b"-        action='store_true', dest='sponskrub_force',"
b"+        u'--sponskrub-force', default=False,"
b"+        action=u'store_true', dest=u'sponskrub_force',"
b'         help=optparse.SUPPRESS_HELP)'
b'     sponsorblock.add_option('
b"-        '--no-sponskrub-force',"
b"-        action='store_true', dest='sponskrub_force',"
b"+        u'--no-sponskrub-force',"
b"+        action=u'store_true', dest=u'sponskrub_force',"
b'         help=optparse.SUPPRESS_HELP)'
b'     sponsorblock.add_option('
b"-        '--sponskrub-location', metavar='PATH',"
b"-        dest='sponskrub_path', default='',"
b"+        u'--sponskrub-location', metavar=u'PATH',"
b"+        dest=u'sponskrub_path', default=u'',"
b'         help=optparse.SUPPRESS_HELP)'
b'     sponsorblock.add_option('
b"-        '--sponskrub-args', dest='sponskrub_args', metavar='ARGS',"
b'-        help=optparse.SUPPRESS_HELP)'
b'-'
b"-    extractor = optparse.OptionGroup(parser, 'Extractor Options')"
b"+        u'--sponskrub-args', dest=u'sponskrub_args', metavar=u'ARGS',"
b'+        help=optparse.SUPPRESS_HELP)'
b'+'
b"+    extractor = optparse.OptionGroup(parser, u'Extractor Options')"
b'     extractor.add_option('
b"-        '--extractor-retries',"
b"-        dest='extractor_retries', metavar='RETRIES', default=3,"
b'-        help=\'Number of retries for known extractor errors (default is %default), or "infinite"\')'
b"+        u'--extractor-retries',"
b"+        dest=u'extractor_retries', metavar=u'RETRIES', default=3,"
b'+        help=u\'Number of retries for known extractor errors (default is %default), or "infinite"\')'
b'     extractor.add_option('
b"-        '--allow-dynamic-mpd', '--no-ignore-dynamic-mpd',"
b"-        action='store_true', dest='dynamic_mpd', default=True,"
b"-        help='Process dynamic DASH manifests (default) (Alias: --no-ignore-dynamic-mpd)')"
b"+        u'--allow-dynamic-mpd', u'--no-ignore-dynamic-mpd',"
b"+        action=u'store_true', dest=u'dynamic_mpd', default=True,"
b"+        help=u'Process dynamic DASH manifests (default) (Alias: --no-ignore-dynamic-mpd)')"
b'     extractor.add_option('
b"-        '--ignore-dynamic-mpd', '--no-allow-dynamic-mpd',"
b"-        action='store_false', dest='dynamic_mpd',"
b"-        help='Do not process dynamic DASH manifests (Alias: --no-allow-dynamic-mpd)')"
b"+        u'--ignore-dynamic-mpd', u'--no-allow-dynamic-mpd',"
b"+        action=u'store_false', dest=u'dynamic_mpd',"
b"+        help=u'Do not process dynamic DASH manifests (Alias: --no-allow-dynamic-mpd)')"
b'     extractor.add_option('
b"-        '--hls-split-discontinuity',"
b"-        dest='hls_split_discontinuity', action='store_true', default=False,"
b"-        help='Split HLS playlists to different formats at discontinuities such as ad breaks',"
b"+        u'--hls-split-discontinuity',"
b"+        dest=u'hls_split_discontinuity', action=u'store_true', default=False,"
b"+        help=u'Split HLS playlists to different formats at discontinuities such as ad breaks',"
b'     )'
b'     extractor.add_option('
b"-        '--no-hls-split-discontinuity',"
b"-        dest='hls_split_discontinuity', action='store_false',"
b"-        help='Do not split HLS playlists into different formats at discontinuities such as ad breaks (default)')"
b"-    _extractor_arg_parser = lambda key, vals='': (key.strip().lower().replace('-', '_'), ["
b"-        val.replace(r'\\,', ',').strip() for val in re.split(r'(?<!\\\\),', vals)])"
b"+        u'--no-hls-split-discontinuity',"
b"+        dest=u'hls_split_discontinuity', action=u'store_false',"
b"+        help=u'Do not split HLS playlists into different formats at discontinuities such as ad breaks (default)')"
b"+    _extractor_arg_parser = lambda key, vals=u'': (key.strip().lower().replace(u'-', u'_'), ["
b"+        val.replace(ur'\\,', u',').strip() for val in re.split(ur'(?<!\\\\),', vals)])"
b'     extractor.add_option('
b"-        '--extractor-args',"
b"-        metavar='IE_KEY:ARGS', dest='extractor_args', default={}, type='str',"
b"-        action='callback', callback=_dict_from_options_callback,"
b"+        u'--extractor-args',"
b"+        metavar=u'IE_KEY:ARGS', dest=u'extractor_args', default={}, type=u'str',"
b"+        action=u'callback', callback=_dict_from_options_callback,"
b'         callback_kwargs={'
b"-            'multiple_keys': False,"
b"-            'process': lambda val: dict("
b"-                _extractor_arg_parser(*arg.split('=', 1)) for arg in val.split(';')),"
b"+            u'multiple_keys': False,"
b"+            u'process': lambda val: dict("
b"+                _extractor_arg_parser(*arg.split(u'=', 1)) for arg in val.split(u';')),"
b'         }, help=('
b'-            \'Pass ARGS arguments to the IE_KEY extractor. See "EXTRACTOR ARGUMENTS" for details. \''
b"-            'You can use this option multiple times to give arguments for different extractors'))"
b'+            u\'Pass ARGS arguments to the IE_KEY extractor. See "EXTRACTOR ARGUMENTS" for details. \''
b"+            u'You can use this option multiple times to give arguments for different extractors'))"
b'     extractor.add_option('
b"-        '--youtube-include-dash-manifest', '--no-youtube-skip-dash-manifest',"
b"-        action='store_true', dest='youtube_include_dash_manifest', default=True,"
b"+        u'--youtube-include-dash-manifest', u'--no-youtube-skip-dash-manifest',"
b"+        action=u'store_true', dest=u'youtube_include_dash_manifest', default=True,"
b'         help=optparse.SUPPRESS_HELP)'
b'     extractor.add_option('
b"-        '--youtube-skip-dash-manifest', '--no-youtube-include-dash-manifest',"
b"-        action='store_false', dest='youtube_include_dash_manifest',"
b"+        u'--youtube-skip-dash-manifest', u'--no-youtube-include-dash-manifest',"
b"+        action=u'store_false', dest=u'youtube_include_dash_manifest',"
b'         help=optparse.SUPPRESS_HELP)'
b'     extractor.add_option('
b"-        '--youtube-include-hls-manifest', '--no-youtube-skip-hls-manifest',"
b"-        action='store_true', dest='youtube_include_hls_manifest', default=True,"
b"+        u'--youtube-include-hls-manifest', u'--no-youtube-skip-hls-manifest',"
b"+        action=u'store_true', dest=u'youtube_include_hls_manifest', default=True,"
b'         help=optparse.SUPPRESS_HELP)'
b'     extractor.add_option('
b"-        '--youtube-skip-hls-manifest', '--no-youtube-include-hls-manifest',"
b"-        action='store_false', dest='youtube_include_hls_manifest',"
b"+        u'--youtube-skip-hls-manifest', u'--no-youtube-include-hls-manifest',"
b"+        action=u'store_false', dest=u'youtube_include_hls_manifest',"
b'         help=optparse.SUPPRESS_HELP)'
b' '
b'     parser.add_option_group(general)'
b'@@ -2006,5 +2009,5 @@'
b' '
b' def _hide_login_info(opts):'
b'     deprecation_warning(f\'"{__name__}._hide_login_info" is deprecated and may be removed \''
b'-                        \'in a future version. Use "yt_dlp.utils.Config.hide_login_info" instead\')'
b'+                        u\'in a future version. Use "yt_dlp.utils.Config.hide_login_info" instead\')'
b'     return Config.hide_login_info(opts)'
