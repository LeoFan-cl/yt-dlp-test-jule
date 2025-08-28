b'--- ./yt_dlp/downloader/mhtml.py\t(original)'
b'+++ ./yt_dlp/downloader/mhtml.py\t(refactored)'
b'@@ -52,8 +52,8 @@'
b' '
b'     @staticmethod'
b'     def _escape_mime(s):'
b"-        return u'=?utf-8?Q?' + (''.join("
b"-            str((b,)) if b >= 0x20 else '=%02X' % b"
b"+        return u'=?utf-8?Q?' + (u''.join("
b"+            unicode((b,)) if b >= 0x20 else u'=%02X' % b"
b'             for b in quopri.encodestring(s.encode(), header=True)'
b"         )).decode(u'us-ascii') + u'?='"
b' '
b'@@ -61,9 +61,9 @@'
b"         return f'{i}.{frag_boundary}@yt-dlp.github.io.invalid'"
b' '
b'     def _gen_stub(self, **_3to2kwargs):'
b"-        title = _3to2kwargs['title']; del _3to2kwargs['title']"
b"-        frag_boundary = _3to2kwargs['frag_boundary']; del _3to2kwargs['frag_boundary']"
b"-        fragments = _3to2kwargs['fragments']; del _3to2kwargs['fragments']"
b"+        title = _3to2kwargs[u'title']; del _3to2kwargs[u'title']"
b"+        frag_boundary = _3to2kwargs[u'frag_boundary']; del _3to2kwargs[u'frag_boundary']"
b"+        fragments = _3to2kwargs[u'fragments']; del _3to2kwargs[u'fragments']"
b'         output = io.StringIO()'
b' '
b'         output.write('
b'@@ -158,21 +158,21 @@'
b' '
b'             frag_header = io.BytesIO()'
b'             frag_header.write('
b"-                '--%b\\r\\n' % frag_boundary.encode(u'us-ascii'))"
b"+                u'--%b\\r\\n' % frag_boundary.encode(u'us-ascii'))"
b'             frag_header.write('
b"-                'Content-ID: <%b>\\r\\n' % self._gen_cid(i, fragment, frag_boundary).encode(u'us-ascii'))"
b"+                u'Content-ID: <%b>\\r\\n' % self._gen_cid(i, fragment, frag_boundary).encode(u'us-ascii'))"
b'             frag_header.write('
b'-                \'Content-type: %b\\r\\n\' % f\'image/{imghdr.what(h=frag_content) or "jpeg"}\'.encode())'
b'+                u\'Content-type: %b\\r\\n\' % f\'image/{imghdr.what(h=frag_content) or "jpeg"}\'.encode())'
b'             frag_header.write('
b"-                'Content-length: %u\\r\\n' % len(frag_content))"
b"+                u'Content-length: %u\\r\\n' % len(frag_content))"
b'             frag_header.write('
b"-                'Content-location: %b\\r\\n' % fragment_url.encode(u'us-ascii'))"
b"+                u'Content-location: %b\\r\\n' % fragment_url.encode(u'us-ascii'))"
b'             frag_header.write('
b"-                'X.yt-dlp.Duration: %f\\r\\n' % fragment[u'duration'])"
b"-            frag_header.write('\\r\\n')"
b"+                u'X.yt-dlp.Duration: %f\\r\\n' % fragment[u'duration'])"
b"+            frag_header.write(u'\\r\\n')"
b'             self._append_fragment('
b"-                ctx, frag_header.getvalue() + frag_content + '\\r\\n')"
b"+                ctx, frag_header.getvalue() + frag_content + u'\\r\\n')"
b' '
b"         ctx[u'dest_stream'].write("
b"-            '--%b--\\r\\n\\r\\n' % frag_boundary.encode(u'us-ascii'))"
b"+            u'--%b--\\r\\n\\r\\n' % frag_boundary.encode(u'us-ascii'))"
b'         return self._finish_frag_download(ctx, info_dict)'
