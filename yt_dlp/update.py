b'--- ./yt_dlp/update.py\t(original)'
b'+++ ./yt_dlp/update.py\t(refactored)'
b'@@ -395,7 +395,7 @@'
b'         return a == b'
b' '
b'     def query_update(self, **_3to2kwargs):'
b"-        if '_output' in _3to2kwargs: _output = _3to2kwargs['_output']; del _3to2kwargs['_output']"
b"+        if u'_output' in _3to2kwargs: _output = _3to2kwargs[u'_output']; del _3to2kwargs[u'_output']"
b'         else: _output = False'
b'         u"""Fetches info about the available update'
b'         @returns   An `UpdateInfo` if there is an update available, else None'
