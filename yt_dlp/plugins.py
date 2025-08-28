b'--- ./yt_dlp/plugins.py\t(original)'
b'+++ ./yt_dlp/plugins.py\t(refactored)'
b'@@ -1,3 +1,6 @@'
b'+from __future__ import division'
b'+from __future__ import with_statement'
b'+from __future__ import absolute_import'
b' import contextlib'
b' import dataclasses'
b' import functools'
b'@@ -30,9 +33,10 @@'
b'     orderedSet,'
b'     write_string,'
b' )'
b'-'
b"-PACKAGE_NAME = 'yt_dlp_plugins'"
b"-COMPAT_PACKAGE_NAME = 'ytdlp_plugins'"
b'+from itertools import imap'
b'+'
b"+PACKAGE_NAME = u'yt_dlp_plugins'"
b"+COMPAT_PACKAGE_NAME = u'ytdlp_plugins'"
b' _BASE_PACKAGE_PATH = Path(__file__).parent'
b' '
b' '
b'@@ -41,26 +45,25 @@'
b' # However, we will still try our best.'
b' '
b' __all__ = ['
b"-    'COMPAT_PACKAGE_NAME',"
b"-    'PACKAGE_NAME',"
b"-    'PluginSpec',"
b"-    'directories',"
b"-    'load_all_plugins',"
b"-    'load_plugins',"
b"-    'register_plugin_spec',"
b"+    u'COMPAT_PACKAGE_NAME',"
b"+    u'PACKAGE_NAME',"
b"+    u'PluginSpec',"
b"+    u'directories',"
b"+    u'load_all_plugins',"
b"+    u'load_plugins',"
b"+    u'register_plugin_spec',"
b' ]'
b' '
b' '
b'-@dataclasses.dataclass'
b'-class PluginSpec:'
b'-    module_name: str'
b'-    suffix: str'
b'+class PluginSpec(object):'
b'+    module_name: unicode'
b'+    suffix: unicode'
b'     destination: Indirect'
b'     plugin_destination: Indirect'
b'-'
b'+PluginSpec = dataclasses.dataclass(PluginSpec)'
b' '
b' class PluginLoader(importlib.abc.Loader):'
b'-    """Dummy loader for virtual namespace packages"""'
b'+    u"""Dummy loader for virtual namespace packages"""'
b' '
b'     def exec_module(self, module):'
b'         return None'
b'@@ -74,14 +77,15 @@'
b'                 Path(file).parents for file in zip_.namelist()))'
b'     except FileNotFoundError:'
b'         pass'
b'-    except Exception as e:'
b'+    except Exception, e:'
b"         write_string(f'WARNING: Could not read zip file {archive}: {e}\\n')"
b'     return ()'
b' '
b' '
b' def default_plugin_paths():'
b'-    def _get_package_paths(*root_paths, containing_folder):'
b'-        for config_dir in orderedSet(map(Path, root_paths), lazy=True):'
b'+    def _get_package_paths(*root_paths, **_3to2kwargs):'
b"+        containing_folder = _3to2kwargs['containing_folder']; del _3to2kwargs['containing_folder']"
b'+        for config_dir in orderedSet(imap(Path, root_paths), lazy=True):'
b'             # We need to filter the base path added when running __main__.py directly'
b'             if config_dir == _BASE_PACKAGE_PATH:'
b'                 continue'
b'@@ -90,21 +94,21 @@'
b' '
b'     # Load from yt-dlp config folders'
b'     yield from _get_package_paths('
b"-        *get_user_config_dirs('yt-dlp'),"
b"-        *get_system_config_dirs('yt-dlp'),"
b"-        containing_folder='plugins',"
b"+        *get_user_config_dirs(u'yt-dlp'),"
b"+        *get_system_config_dirs(u'yt-dlp'),"
b"+        containing_folder=u'plugins',"
b'     )'
b' '
b'     # Load from yt-dlp-plugins folders'
b'     yield from _get_package_paths('
b'         get_executable_path(),'
b"-        *get_user_config_dirs(''),"
b"-        *get_system_config_dirs(''),"
b"-        containing_folder='yt-dlp-plugins',"
b"+        *get_user_config_dirs(u''),"
b"+        *get_system_config_dirs(u''),"
b"+        containing_folder=u'yt-dlp-plugins',"
b'     )'
b' '
b'     # Load from PYTHONPATH directories'
b'-    yield from (path for path in map(Path, sys.path) if path != _BASE_PACKAGE_PATH)'
b'+    yield from (path for path in imap(Path, sys.path) if path != _BASE_PACKAGE_PATH)'
b' '
b' '
b' def candidate_plugin_paths(candidate):'
b'@@ -115,7 +119,7 @@'
b' '
b' '
b' class PluginFinder(importlib.abc.MetaPathFinder):'
b'-    """'
b'+    u"""'
b'     This class provides one or multiple namespace packages.'
b'     It searches in sys.path and yt-dlp config folders for'
b'     the existing subdirectories from which the modules can be imported'
b'@@ -125,32 +129,32 @@'
b'         self._zip_content_cache = {}'
b'         self.packages = set('
b'             itertools.chain.from_iterable('
b"-                itertools.accumulate(name.split('.'), lambda a, b: '.'.join((a, b)))"
b"+                itertools.accumulate(name.split(u'.'), lambda a, b: u'.'.join((a, b)))"
b'                 for name in packages))'
b' '
b'     def search_locations(self, fullname):'
b'         candidate_locations = itertools.chain.from_iterable('
b"-            default_plugin_paths() if candidate == 'default' else candidate_plugin_paths(candidate)"
b"+            default_plugin_paths() if candidate == u'default' else candidate_plugin_paths(candidate)"
b'             for candidate in plugin_dirs.value'
b'         )'
b' '
b"-        parts = Path(*fullname.split('.'))"
b"+        parts = Path(*fullname.split(u'.'))"
b'         for path in orderedSet(candidate_locations, lazy=True):'
b'             candidate = path / parts'
b'             try:'
b'                 if candidate.is_dir():'
b'                     yield candidate'
b"-                elif path.suffix in ('.zip', '.egg', '.whl') and path.is_file():"
b"+                elif path.suffix in (u'.zip', u'.egg', u'.whl') and path.is_file():"
b'                     if parts in dirs_in_zip(path):'
b'                         yield candidate'
b'-            except PermissionError as e:'
b'+            except PermissionError, e:'
b'                 write_string(f\'Permission error while accessing modules in "{e.filename}"\\n\')'
b' '
b'     def find_spec(self, fullname, path=None, target=None):'
b'         if fullname not in self.packages:'
b'             return None'
b' '
b'-        search_locations = list(map(str, self.search_locations(fullname)))'
b'+        search_locations = list(imap(unicode, self.search_locations(fullname)))'
b'         if not search_locations:'
b'             # Prevent using built-in meta finders for searching plugins.'
b'             raise ModuleNotFoundError(fullname)'
b'@@ -186,20 +190,20 @@'
b'         inspect.isclass(obj)'
b'         and obj.__name__.endswith(suffix)'
b'         and obj.__module__.startswith(module_name)'
b"-        and not obj.__name__.startswith('_')"
b"-        and obj.__name__ in getattr(module, '__all__', [obj.__name__])"
b"-        and getattr(obj, 'PLUGIN_NAME', None) is None"
b"+        and not obj.__name__.startswith(u'_')"
b"+        and obj.__name__ in getattr(module, u'__all__', [obj.__name__])"
b"+        and getattr(obj, u'PLUGIN_NAME', None) is None"
b'     ))'
b' '
b' '
b'-def load_plugins(plugin_spec: PluginSpec):'
b'+def load_plugins(plugin_spec):'
b'     name, suffix = plugin_spec.module_name, plugin_spec.suffix'
b'     regular_classes = {}'
b"-    if os.environ.get('YTDLP_NO_PLUGINS') or not plugin_dirs.value:"
b"+    if os.environ.get(u'YTDLP_NO_PLUGINS') or not plugin_dirs.value:"
b'         return regular_classes'
b' '
b'     for finder, module_name, _ in iter_modules(name):'
b"-        if any(x.startswith('_') for x in module_name.split('.')):"
b"+        if any(x.startswith(u'_') for x in module_name.split(u'.')):"
b'             continue'
b'         try:'
b'             if sys.version_info < (3, 10) and isinstance(finder, zipimport.zipimporter):'
b'@@ -222,11 +226,11 @@'
b'     # Compat: old plugin system using __init__.py'
b'     # Note: plugins imported this way do not show up in directories()'
b'     # nor are considered part of the yt_dlp_plugins namespace package'
b"-    if 'default' in plugin_dirs.value:"
b"+    if u'default' in plugin_dirs.value:"
b'         with contextlib.suppress(FileNotFoundError):'
b'             spec = importlib.util.spec_from_file_location('
b'                 name,'
b"-                Path(get_executable_path(), COMPAT_PACKAGE_NAME, name, '__init__.py'),"
b"+                Path(get_executable_path(), COMPAT_PACKAGE_NAME, name, u'__init__.py'),"
b'             )'
b'             plugins = importlib.util.module_from_spec(spec)'
b'             sys.modules[spec.name] = plugins'
b'@@ -247,7 +251,7 @@'
b'     all_plugins_loaded.value = True'
b' '
b' '
b'-def register_plugin_spec(plugin_spec: PluginSpec):'
b'+def register_plugin_spec(plugin_spec):'
b'     # If the plugin spec for a module is already registered, it will not be added again'
b'     if plugin_spec.module_name not in plugin_specs.value:'
b'         plugin_specs.value[plugin_spec.module_name] = plugin_spec'
