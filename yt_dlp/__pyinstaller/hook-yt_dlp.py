from __future__ import print_function, unicode_literals
import sys

from PyInstaller.utils.hooks import collect_submodules, collect_data_files


def pycryptodome_module():
    try:
        import Cryptodome  # noqa: F401
    except ImportError:
        try:
            import Crypto  # noqa: F401
            print('WARNING: Using Crypto since Cryptodome is not available. '
                  'Install with: python -m pip install pycryptodomex', file=sys.stderr)
            return 'Crypto'
        except ImportError:
            pass
    return 'Cryptodome'


def get_hidden_imports():
    for i in ('yt_dlp.compat._legacy', 'yt_dlp.compat._deprecated'):
        yield i
    for i in ('yt_dlp.utils._legacy', 'yt_dlp.utils._deprecated'):
        yield i
    yield pycryptodome_module()
    # Only `websockets` is required, others are collected just in case
    for module in ('websockets', 'requests', 'urllib3'):
        for i in collect_submodules(module):
            yield i
    # These are auto-detected, but explicitly add them just in case
    for i in ('mutagen', 'brotli', 'certifi', 'secretstorage', 'curl_cffi'):
        yield i


hiddenimports = list(get_hidden_imports())
print('Adding imports: {0}'.format(hiddenimports))

excludedimports = ['youtube_dl', 'youtube_dlc', 'test', 'ytdlp_plugins', 'devscripts', 'bundle']

datas = collect_data_files('curl_cffi', includes=['cacert.pem'])
