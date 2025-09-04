from __future__ import with_statement
from __future__ import absolute_import
from __future__ import print_function, unicode_literals
import contextlib
import json
import os
import re
import shutil
import traceback
import urllib

from .utils import expand_path, traverse_obj, version_tuple, write_json_file
from .version import __version__
from io import open


class Cache(object):
    def __init__(self, ydl):
        self._ydl = ydl

    def _get_root_dir(self):
        res = self._ydl.params.get(u'cachedir')
        if res is None:
            cache_root = os.getenv(u'XDG_CACHE_HOME', u'~/.cache')
            res = os.path.join(cache_root, u'yt-dlp')
        return expand_path(res)

    def _get_cache_fn(self, section, key, dtype):
        assert re.match(ur'^[\w.-]+$', section), u'invalid section {0!r}'.format(section)
        key = urllib.quote(key.encode(u'utf-8'), safe='').replace(u'%', u',')  # encode non-ascii characters
        return os.path.join(self._get_root_dir(), section, u'{0}.{1}'.format(key, dtype))

    @property
    def enabled(self):
        return self._ydl.params.get(u'cachedir') is not False

    def store(self, section, key, data, dtype=u'json'):
        assert dtype in (u'json',)

        if not self.enabled:
            return

        fn = self._get_cache_fn(section, key, dtype)
        try:
            try:
                os.makedirs(os.path.dirname(fn))
            except OSError:
                pass
            self._ydl.write_debug(u'Saving {0}.{1} to cache'.format(section, key))
            write_json_file({u'yt-dlp_version': __version__, u'data': data}, fn)
        except Exception:
            tb = traceback.format_exc()
            self._ydl.report_warning(u'Writing cache to {0!r} failed: {1}'.format(fn, tb))

    def _validate(self, data, min_ver):
        version = traverse_obj(data, u'yt-dlp_version')
        if not version:  # Backward compatibility
            data, version = {u'data': data}, u'2022.08.19'
        if not min_ver or version_tuple(version) >= version_tuple(min_ver):
            return data[u'data']
        self._ydl.write_debug(u'Discarding old cache from version {0} (needs {1})'.format(version, min_ver))

    def load(self, section, key, dtype=u'json', default=None, **kwargs):
        min_ver = kwargs.pop(u'min_ver', None)
        assert dtype in (u'json',)

        if not self.enabled:
            return default

        cache_fn = self._get_cache_fn(section, key, dtype)
        with contextlib.suppress(OSError):
            try:
                with open(cache_fn, encoding=u'utf-8') as cachef:
                    self._ydl.write_debug(u'Loading {0}.{1} from cache'.format(section, key))
                    return self._validate(json.load(cachef), min_ver)
            except (ValueError, KeyError):
                try:
                    file_size = os.path.getsize(cache_fn)
                except OSError, oe:
                    file_size = unicode(oe)
                self._ydl.report_warning(u'Cache retrieval from {0} failed ({1})'.format(cache_fn, file_size))

        return default

    def remove(self):
        if not self.enabled:
            self._ydl.to_screen(u'Cache is disabled (Did you combine --no-cache-dir and --rm-cache-dir?)')
            return

        cachedir = self._get_root_dir()
        if not any((term in cachedir) for term in (u'cache', u'tmp')):
            raise Exception(u'Not removing directory {0} - this does not look like a cache dir'.format(cachedir))

        self._ydl.to_screen(
            u'Removing cache dir {0} .'.format(cachedir), skip_eol=True)
        if os.path.exists(cachedir):
            self._ydl.to_screen(u'.', skip_eol=True)
            shutil.rmtree(cachedir)
        self._ydl.to_screen(u'.')
