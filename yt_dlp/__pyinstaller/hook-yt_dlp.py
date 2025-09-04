from __future__ import absolute_import
from __future__ import print_function, unicode_literals
import sys

from PyInstaller.utils.hooks import collect_submodules, collect_data_files


def pycryptodome_module():
    try:
        import Cryptodome  # noqa: F401
    except ImportError:
        try:
            import Crypto  # noqa: F401
            print >>sys.stderr, u'WARNING: Using Crypto since Cryptodome is not available. '
                  u'Install with: python -m pip install pycryptodomex'
            return u'Crypto'
        except ImportError:
            pass
    return u'Cryptodome'


def get_hidden_imports():
    for i in (u'yt_dlp.compat._legacy', u'yt_dlp.compat._deprecated'):
        yield i
    for i in (u'yt_dlp.utils._legacy', u'yt_dlp.utils._deprecated'):
        yield i
    yield pycryptodome_module()
    # Only `websockets` is required, others are collected just in case
    for module in (u'websockets', u'requests', u'urllib3'):
        for i in collect_submodules(module):
            yield i
    # These are auto-detected, but explicitly add them just in case
    for i in (u'mutagen', u'brotli', u'certifi', u'secretstorage', u'curl_cffi'):
        yield i


hiddenimports = list(get_hidden_imports())
print u'Adding imports: {0}'.format(hiddenimports)

excludedimports = [u'youtube_dl', u'youtube_dlc', u'test', u'ytdlp_plugins', u'devscripts', u'bundle']

datas = collect_data_files(u'curl_cffi', includes=[u'cacert.pem'])
