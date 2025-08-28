# flake8: noqa: F401
"""Imports all optional dependencies for the project.
An attribute "_yt_dlp__identifier" may be inserted into the module if it uses an ambiguous namespace"""
from __future__ import unicode_literals

try:
    import brotlicffi as brotli
except ImportError:
    try:
        import brotli
    except ImportError:
        brotli = None


try:
    import certifi
except ImportError:
    certifi = None
else:
    from os.path import exists as _path_exists

    # The certificate may not be bundled in executable
    if not _path_exists(certifi.where()):
        certifi = None


try:
    import mutagen
except ImportError:
    mutagen = None


secretstorage = None
try:
    import secretstorage
    _SECRETSTORAGE_UNAVAILABLE_REASON = None
except ImportError:
    _SECRETSTORAGE_UNAVAILABLE_REASON = (
        'as the `secretstorage` module is not installed. '
        'Please install by running `python -m pip install secretstorage`')
except Exception as _err:
    _SECRETSTORAGE_UNAVAILABLE_REASON = 'as the `secretstorage` module could not be initialized. {0}'.format(_err)


try:
    import sqlite3
    # We need to get the underlying `sqlite` version, see https://github.com/yt-dlp/yt-dlp/issues/8152
    sqlite3._yt_dlp__version = sqlite3.sqlite_version
except ImportError:
    # although sqlite3 is part of the standard library, it is possible to compile Python without
    # sqlite support. See: https://github.com/yt-dlp/yt-dlp/issues/544
    sqlite3 = None


try:
    import websocket
except ImportError:
    websocket = None

try:
    import urllib3
except ImportError:
    urllib3 = None

try:
    import requests
except ImportError:
    requests = None

try:
    import xattr  # xattr or pyxattr
except ImportError:
    xattr = None
else:
    if hasattr(xattr, 'set'):  # pyxattr
        xattr._yt_dlp__identifier = 'pyxattr'

try:
    import curl_cffi
except ImportError:
    curl_cffi = None

from . import Cryptodome

all_dependencies = dict((k, v) for k, v in globals().items() if not k.startswith('_'))
available_dependencies = dict((k, v) for k, v in all_dependencies.items() if v)


# Deprecated
Cryptodome_AES = Cryptodome.AES


__all__ = [
    'all_dependencies',
    'available_dependencies',
] + list(all_dependencies.keys())
