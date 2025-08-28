b'--- ./yt_dlp/downloader/rtmp.py\t(original)'
b'+++ ./yt_dlp/downloader/rtmp.py\t(refactored)'
b'@@ -37,7 +37,7 @@'
b'                         if not char:'
b'                             proc_stderr_closed = True'
b'                             break'
b"-                        if char in ['\\r', '\\n']:"
b"+                        if char in [u'\\r', u'\\n']:"
b'                             break'
b"                         line += char.decode(u'ascii', u'replace')"
b'                     if not line:'
