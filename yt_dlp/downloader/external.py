b'--- ./yt_dlp/downloader/external.py\t(original)'
b'+++ ./yt_dlp/downloader/external.py\t(refactored)'
b'@@ -393,7 +393,7 @@'
b'         self._hook_progress(status, info_dict)'
b' '
b'         def get_stat(key, *obj, **_3to2kwargs):'
b"-            if 'average' in _3to2kwargs: average = _3to2kwargs['average']; del _3to2kwargs['average']"
b"+            if u'average' in _3to2kwargs: average = _3to2kwargs[u'average']; del _3to2kwargs[u'average']"
b'             else: average = False'
b'             val = tuple(ifilter(None, imap(float, traverse_obj(obj, (..., ..., key))))) or [0]'
b'             return sum(val) / (len(val) if average else 1)'
b'@@ -654,7 +654,7 @@'
b'                 # streams). Note that Windows is not affected and produces playable'
b'                 # files (see https://github.com/ytdl-org/youtube-dl/issues/8300).'
b"                 if isinstance(e, KeyboardInterrupt) and sys.platform != u'win32' and not piped:"
b"-                    proc.communicate_or_kill('q')"
b"+                    proc.communicate_or_kill(u'q')"
b'                 else:'
b'                     proc.kill(timeout=None)'
b'                 raise'
