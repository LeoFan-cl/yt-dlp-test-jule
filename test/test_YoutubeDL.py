b'--- ./test/test_YoutubeDL.py\t(original)'
b'+++ ./test/test_YoutubeDL.py\t(refactored)'
b'@@ -1,12 +1,17 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import with_statement'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' import unittest'
b' from unittest.mock import patch'
b' '
b' from yt_dlp.globals import all_plugins_loaded'
b'+from itertools import izip'
b'+from io import open'
b'+from itertools import imap'
b' '
b' sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'
b' '
b'@@ -29,12 +34,12 @@'
b' )'
b' from yt_dlp.utils.traversal import traverse_obj'
b' '
b"-TEST_URL = 'http://localhost/sample.mp4'"
b"+TEST_URL = u'http://localhost/sample.mp4'"
b' '
b' '
b' class YDL(FakeYDL):'
b'     def __init__(self, *args, **kwargs):'
b'-        super().__init__(*args, **kwargs)'
b'+        super(YDL, self).__init__(*args, **kwargs)'
b'         self.downloaded_info_dicts = []'
b'         self.msgs = []'
b' '
b'@@ -45,17 +50,17 @@'
b'         self.msgs.append(msg)'
b' '
b'     def dl(self, *args, **kwargs):'
b"-        assert False, 'Downloader must not be invoked for test_YoutubeDL'"
b"+        assert False, u'Downloader must not be invoked for test_YoutubeDL'"
b' '
b' '
b' def _make_result(formats, **kwargs):'
b'     res = {'
b"-        'formats': formats,"
b"-        'id': 'testid',"
b"-        'title': 'testttitle',"
b"-        'extractor': 'testex',"
b"-        'extractor_key': 'TestEx',"
b"-        'webpage_url': 'http://example.com/watch?v=shenanigans',"
b"+        u'formats': formats,"
b"+        u'id': u'testid',"
b"+        u'title': u'testttitle',"
b"+        u'extractor': u'testex',"
b"+        u'extractor_key': u'TestEx',"
b"+        u'webpage_url': u'http://example.com/watch?v=shenanigans',"
b'     }'
b'     res.update(**kwargs)'
b'     return res'
b'@@ -65,275 +70,277 @@'
b'     def test_prefer_free_formats(self):'
b'         # Same resolution => download webm'
b'         ydl = YDL()'
b"-        ydl.params['prefer_free_formats'] = True"
b'-        formats = ['
b"-            {'ext': 'webm', 'height': 460, 'url': TEST_URL},"
b"-            {'ext': 'mp4', 'height': 460, 'url': TEST_URL},"
b"+        ydl.params[u'prefer_free_formats'] = True"
b'+        formats = ['
b"+            {u'ext': u'webm', u'height': 460, u'url': TEST_URL},"
b"+            {u'ext': u'mp4', u'height': 460, u'url': TEST_URL},"
b'         ]'
b'         info_dict = _make_result(formats)'
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(info_dict)'
b'         downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['ext'], 'webm')"
b"+        self.assertEqual(downloaded[u'ext'], u'webm')"
b' '
b'         # Different resolution => download best quality (mp4)'
b'         ydl = YDL()'
b"-        ydl.params['prefer_free_formats'] = True"
b'-        formats = ['
b"-            {'ext': 'webm', 'height': 720, 'url': TEST_URL},"
b"-            {'ext': 'mp4', 'height': 1080, 'url': TEST_URL},"
b'-        ]'
b"-        info_dict['formats'] = formats"
b"+        ydl.params[u'prefer_free_formats'] = True"
b'+        formats = ['
b"+            {u'ext': u'webm', u'height': 720, u'url': TEST_URL},"
b"+            {u'ext': u'mp4', u'height': 1080, u'url': TEST_URL},"
b'+        ]'
b"+        info_dict[u'formats'] = formats"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(info_dict)'
b'         downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['ext'], 'mp4')"
b"+        self.assertEqual(downloaded[u'ext'], u'mp4')"
b' '
b'         # No prefer_free_formats => prefer mp4 and webm'
b'         ydl = YDL()'
b"-        ydl.params['prefer_free_formats'] = False"
b'-        formats = ['
b"-            {'ext': 'webm', 'height': 720, 'url': TEST_URL},"
b"-            {'ext': 'mp4', 'height': 720, 'url': TEST_URL},"
b"-            {'ext': 'flv', 'height': 720, 'url': TEST_URL},"
b'-        ]'
b"-        info_dict['formats'] = formats"
b"+        ydl.params[u'prefer_free_formats'] = False"
b'+        formats = ['
b"+            {u'ext': u'webm', u'height': 720, u'url': TEST_URL},"
b"+            {u'ext': u'mp4', u'height': 720, u'url': TEST_URL},"
b"+            {u'ext': u'flv', u'height': 720, u'url': TEST_URL},"
b'+        ]'
b"+        info_dict[u'formats'] = formats"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(info_dict)'
b'         downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['ext'], 'mp4')"
b"+        self.assertEqual(downloaded[u'ext'], u'mp4')"
b' '
b'         ydl = YDL()'
b"-        ydl.params['prefer_free_formats'] = False"
b'-        formats = ['
b"-            {'ext': 'flv', 'height': 720, 'url': TEST_URL},"
b"-            {'ext': 'webm', 'height': 720, 'url': TEST_URL},"
b'-        ]'
b"-        info_dict['formats'] = formats"
b"+        ydl.params[u'prefer_free_formats'] = False"
b'+        formats = ['
b"+            {u'ext': u'flv', u'height': 720, u'url': TEST_URL},"
b"+            {u'ext': u'webm', u'height': 720, u'url': TEST_URL},"
b'+        ]'
b"+        info_dict[u'formats'] = formats"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(info_dict)'
b'         downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['ext'], 'webm')"
b"+        self.assertEqual(downloaded[u'ext'], u'webm')"
b' '
b'     def test_format_selection(self):'
b'         formats = ['
b"-            {'format_id': '35', 'ext': 'mp4', 'preference': 0, 'url': TEST_URL},"
b"-            {'format_id': 'example-with-dashes', 'ext': 'webm', 'preference': 1, 'url': TEST_URL},"
b"-            {'format_id': '45', 'ext': 'webm', 'preference': 2, 'url': TEST_URL},"
b"-            {'format_id': '47', 'ext': 'webm', 'preference': 3, 'url': TEST_URL},"
b"-            {'format_id': '2', 'ext': 'flv', 'preference': 4, 'url': TEST_URL},"
b"+            {u'format_id': u'35', u'ext': u'mp4', u'preference': 0, u'url': TEST_URL},"
b"+            {u'format_id': u'example-with-dashes', u'ext': u'webm', u'preference': 1, u'url': TEST_URL},"
b"+            {u'format_id': u'45', u'ext': u'webm', u'preference': 2, u'url': TEST_URL},"
b"+            {u'format_id': u'47', u'ext': u'webm', u'preference': 3, u'url': TEST_URL},"
b"+            {u'format_id': u'2', u'ext': u'flv', u'preference': 4, u'url': TEST_URL},"
b'         ]'
b'         info_dict = _make_result(formats)'
b' '
b'-        def test(inp, *expected, multi=False):'
b'+        def test(inp, *expected, **_3to2kwargs):'
b"+            if 'multi' in _3to2kwargs: multi = _3to2kwargs['multi']; del _3to2kwargs['multi']"
b'+            else: multi = False'
b'             ydl = YDL({'
b"-                'format': inp,"
b"-                'allow_multiple_video_streams': multi,"
b"-                'allow_multiple_audio_streams': multi,"
b"+                u'format': inp,"
b"+                u'allow_multiple_video_streams': multi,"
b"+                u'allow_multiple_audio_streams': multi,"
b'             })'
b'             ydl.process_ie_result(info_dict.copy())'
b"-            downloaded = [x['format_id'] for x in ydl.downloaded_info_dicts]"
b"+            downloaded = [x[u'format_id'] for x in ydl.downloaded_info_dicts]"
b'             self.assertEqual(downloaded, list(expected))'
b' '
b"-        test('20/47', '47')"
b"-        test('20/71/worst', '35')"
b"-        test(None, '2')"
b"-        test('webm/mp4', '47')"
b"-        test('3gp/40/mp4', '35')"
b"-        test('example-with-dashes', 'example-with-dashes')"
b"-        test('all', '2', '47', '45', 'example-with-dashes', '35')"
b"-        test('mergeall', '2+47+45+example-with-dashes+35', multi=True)"
b"+        test(u'20/47', u'47')"
b"+        test(u'20/71/worst', u'35')"
b"+        test(None, u'2')"
b"+        test(u'webm/mp4', u'47')"
b"+        test(u'3gp/40/mp4', u'35')"
b"+        test(u'example-with-dashes', u'example-with-dashes')"
b"+        test(u'all', u'2', u'47', u'45', u'example-with-dashes', u'35')"
b"+        test(u'mergeall', u'2+47+45+example-with-dashes+35', multi=True)"
b'         # See: https://github.com/yt-dlp/yt-dlp/pulls/8797'
b"-        test('7_a/worst', '35')"
b"+        test(u'7_a/worst', u'35')"
b' '
b'     def test_format_selection_audio(self):'
b'         formats = ['
b"-            {'format_id': 'audio-low', 'ext': 'webm', 'preference': 1, 'vcodec': 'none', 'url': TEST_URL},"
b"-            {'format_id': 'audio-mid', 'ext': 'webm', 'preference': 2, 'vcodec': 'none', 'url': TEST_URL},"
b"-            {'format_id': 'audio-high', 'ext': 'flv', 'preference': 3, 'vcodec': 'none', 'url': TEST_URL},"
b"-            {'format_id': 'vid', 'ext': 'mp4', 'preference': 4, 'url': TEST_URL},"
b"+            {u'format_id': u'audio-low', u'ext': u'webm', u'preference': 1, u'vcodec': u'none', u'url': TEST_URL},"
b"+            {u'format_id': u'audio-mid', u'ext': u'webm', u'preference': 2, u'vcodec': u'none', u'url': TEST_URL},"
b"+            {u'format_id': u'audio-high', u'ext': u'flv', u'preference': 3, u'vcodec': u'none', u'url': TEST_URL},"
b"+            {u'format_id': u'vid', u'ext': u'mp4', u'preference': 4, u'url': TEST_URL},"
b'         ]'
b'         info_dict = _make_result(formats)'
b' '
b"-        ydl = YDL({'format': 'bestaudio'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'audio-high')"
b'-'
b"-        ydl = YDL({'format': 'worstaudio'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'audio-low')"
b'-'
b'-        formats = ['
b"-            {'format_id': 'vid-low', 'ext': 'mp4', 'preference': 1, 'url': TEST_URL},"
b"-            {'format_id': 'vid-high', 'ext': 'mp4', 'preference': 2, 'url': TEST_URL},"
b"+        ydl = YDL({u'format': u'bestaudio'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'audio-high')"
b'+'
b"+        ydl = YDL({u'format': u'worstaudio'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'audio-low')"
b'+'
b'+        formats = ['
b"+            {u'format_id': u'vid-low', u'ext': u'mp4', u'preference': 1, u'url': TEST_URL},"
b"+            {u'format_id': u'vid-high', u'ext': u'mp4', u'preference': 2, u'url': TEST_URL},"
b'         ]'
b'         info_dict = _make_result(formats)'
b' '
b"-        ydl = YDL({'format': 'bestaudio/worstaudio/best'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'vid-high')"
b"+        ydl = YDL({u'format': u'bestaudio/worstaudio/best'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'vid-high')"
b' '
b'     def test_format_selection_audio_exts(self):'
b'         formats = ['
b"-            {'format_id': 'mp3-64', 'ext': 'mp3', 'abr': 64, 'url': 'http://_', 'vcodec': 'none'},"
b"-            {'format_id': 'ogg-64', 'ext': 'ogg', 'abr': 64, 'url': 'http://_', 'vcodec': 'none'},"
b"-            {'format_id': 'aac-64', 'ext': 'aac', 'abr': 64, 'url': 'http://_', 'vcodec': 'none'},"
b"-            {'format_id': 'mp3-32', 'ext': 'mp3', 'abr': 32, 'url': 'http://_', 'vcodec': 'none'},"
b"-            {'format_id': 'aac-32', 'ext': 'aac', 'abr': 32, 'url': 'http://_', 'vcodec': 'none'},"
b"+            {u'format_id': u'mp3-64', u'ext': u'mp3', u'abr': 64, u'url': u'http://_', u'vcodec': u'none'},"
b"+            {u'format_id': u'ogg-64', u'ext': u'ogg', u'abr': 64, u'url': u'http://_', u'vcodec': u'none'},"
b"+            {u'format_id': u'aac-64', u'ext': u'aac', u'abr': 64, u'url': u'http://_', u'vcodec': u'none'},"
b"+            {u'format_id': u'mp3-32', u'ext': u'mp3', u'abr': 32, u'url': u'http://_', u'vcodec': u'none'},"
b"+            {u'format_id': u'aac-32', u'ext': u'aac', u'abr': 32, u'url': u'http://_', u'vcodec': u'none'},"
b'         ]'
b' '
b'         info_dict = _make_result(formats)'
b"-        ydl = YDL({'format': 'best', 'format_sort': ['abr', 'ext']})"
b"+        ydl = YDL({u'format': u'best', u'format_sort': [u'abr', u'ext']})"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(copy.deepcopy(info_dict))'
b'         downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'aac-64')"
b'-'
b"-        ydl = YDL({'format': 'mp3'})"
b"+        self.assertEqual(downloaded[u'format_id'], u'aac-64')"
b'+'
b"+        ydl = YDL({u'format': u'mp3'})"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(copy.deepcopy(info_dict))'
b'         downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'mp3-64')"
b'-'
b"-        ydl = YDL({'prefer_free_formats': True, 'format_sort': ['abr', 'ext']})"
b"+        self.assertEqual(downloaded[u'format_id'], u'mp3-64')"
b'+'
b"+        ydl = YDL({u'prefer_free_formats': True, u'format_sort': [u'abr', u'ext']})"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(copy.deepcopy(info_dict))'
b'         downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'ogg-64')"
b"+        self.assertEqual(downloaded[u'format_id'], u'ogg-64')"
b' '
b'     def test_format_selection_video(self):'
b'         formats = ['
b"-            {'format_id': 'dash-video-low', 'ext': 'mp4', 'preference': 1, 'acodec': 'none', 'url': TEST_URL},"
b"-            {'format_id': 'dash-video-high', 'ext': 'mp4', 'preference': 2, 'acodec': 'none', 'url': TEST_URL},"
b"-            {'format_id': 'vid', 'ext': 'mp4', 'preference': 3, 'url': TEST_URL},"
b"+            {u'format_id': u'dash-video-low', u'ext': u'mp4', u'preference': 1, u'acodec': u'none', u'url': TEST_URL},"
b"+            {u'format_id': u'dash-video-high', u'ext': u'mp4', u'preference': 2, u'acodec': u'none', u'url': TEST_URL},"
b"+            {u'format_id': u'vid', u'ext': u'mp4', u'preference': 3, u'url': TEST_URL},"
b'         ]'
b'         info_dict = _make_result(formats)'
b' '
b"-        ydl = YDL({'format': 'bestvideo'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'dash-video-high')"
b'-'
b"-        ydl = YDL({'format': 'worstvideo'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'dash-video-low')"
b'-'
b"-        ydl = YDL({'format': 'bestvideo[format_id^=dash][format_id$=low]'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'dash-video-low')"
b'-'
b'-        formats = ['
b"-            {'format_id': 'vid-vcodec-dot', 'ext': 'mp4', 'preference': 1, 'vcodec': 'avc1.123456', 'acodec': 'none', 'url': TEST_URL},"
b"+        ydl = YDL({u'format': u'bestvideo'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'dash-video-high')"
b'+'
b"+        ydl = YDL({u'format': u'worstvideo'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'dash-video-low')"
b'+'
b"+        ydl = YDL({u'format': u'bestvideo[format_id^=dash][format_id$=low]'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'dash-video-low')"
b'+'
b'+        formats = ['
b"+            {u'format_id': u'vid-vcodec-dot', u'ext': u'mp4', u'preference': 1, u'vcodec': u'avc1.123456', u'acodec': u'none', u'url': TEST_URL},"
b'         ]'
b'         info_dict = _make_result(formats)'
b' '
b"-        ydl = YDL({'format': 'bestvideo[vcodec=avc1.123456]'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'vid-vcodec-dot')"
b"+        ydl = YDL({u'format': u'bestvideo[vcodec=avc1.123456]'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'vid-vcodec-dot')"
b' '
b'     def test_format_selection_by_vcodec_sort(self):'
b'         formats = ['
b"-            {'format_id': 'av1-format', 'ext': 'mp4', 'vcodec': 'av1', 'acodec': 'none', 'url': TEST_URL},"
b"-            {'format_id': 'vp9-hdr-format', 'ext': 'mp4', 'vcodec': 'vp09.02.50.10.01.09.18.09.00', 'acodec': 'none', 'url': TEST_URL},"
b"-            {'format_id': 'vp9-sdr-format', 'ext': 'mp4', 'vcodec': 'vp09.00.50.08', 'acodec': 'none', 'url': TEST_URL},"
b"-            {'format_id': 'h265-format', 'ext': 'mp4', 'vcodec': 'h265', 'acodec': 'none', 'url': TEST_URL},"
b"+            {u'format_id': u'av1-format', u'ext': u'mp4', u'vcodec': u'av1', u'acodec': u'none', u'url': TEST_URL},"
b"+            {u'format_id': u'vp9-hdr-format', u'ext': u'mp4', u'vcodec': u'vp09.02.50.10.01.09.18.09.00', u'acodec': u'none', u'url': TEST_URL},"
b"+            {u'format_id': u'vp9-sdr-format', u'ext': u'mp4', u'vcodec': u'vp09.00.50.08', u'acodec': u'none', u'url': TEST_URL},"
b"+            {u'format_id': u'h265-format', u'ext': u'mp4', u'vcodec': u'h265', u'acodec': u'none', u'url': TEST_URL},"
b'         ]'
b'         info_dict = _make_result(formats)'
b' '
b"-        ydl = YDL({'format': 'bestvideo', 'format_sort': ['vcodec:vp9.2']})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'vp9-hdr-format')"
b'-'
b"-        ydl = YDL({'format': 'bestvideo', 'format_sort': ['vcodec:vp9']})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'vp9-sdr-format')"
b'-'
b"-        ydl = YDL({'format': 'bestvideo', 'format_sort': ['+vcodec:vp9.2']})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'vp9-hdr-format')"
b'-'
b"-        ydl = YDL({'format': 'bestvideo', 'format_sort': ['+vcodec:vp9']})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'vp9-sdr-format')"
b"+        ydl = YDL({u'format': u'bestvideo', u'format_sort': [u'vcodec:vp9.2']})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'vp9-hdr-format')"
b'+'
b"+        ydl = YDL({u'format': u'bestvideo', u'format_sort': [u'vcodec:vp9']})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'vp9-sdr-format')"
b'+'
b"+        ydl = YDL({u'format': u'bestvideo', u'format_sort': [u'+vcodec:vp9.2']})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'vp9-hdr-format')"
b'+'
b"+        ydl = YDL({u'format': u'bestvideo', u'format_sort': [u'+vcodec:vp9']})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'vp9-sdr-format')"
b' '
b'     def test_format_selection_string_ops(self):'
b'         formats = ['
b"-            {'format_id': 'abc-cba', 'ext': 'mp4', 'url': TEST_URL},"
b"-            {'format_id': 'zxc-cxz', 'ext': 'webm', 'url': TEST_URL},"
b"+            {u'format_id': u'abc-cba', u'ext': u'mp4', u'url': TEST_URL},"
b"+            {u'format_id': u'zxc-cxz', u'ext': u'webm', u'url': TEST_URL},"
b'         ]'
b'         info_dict = _make_result(formats)'
b' '
b'         # equals (=)'
b"-        ydl = YDL({'format': '[format_id=abc-cba]'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'abc-cba')"
b"+        ydl = YDL({u'format': u'[format_id=abc-cba]'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'abc-cba')"
b' '
b'         # does not equal (!=)'
b"-        ydl = YDL({'format': '[format_id!=abc-cba]'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'zxc-cxz')"
b'-'
b"-        ydl = YDL({'format': '[format_id!=abc-cba][format_id!=zxc-cxz]'})"
b"+        ydl = YDL({u'format': u'[format_id!=abc-cba]'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'zxc-cxz')"
b'+'
b"+        ydl = YDL({u'format': u'[format_id!=abc-cba][format_id!=zxc-cxz]'})"
b'         self.assertRaises(ExtractorError, ydl.process_ie_result, info_dict.copy())'
b' '
b'         # starts with (^=)'
b"-        ydl = YDL({'format': '[format_id^=abc]'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'abc-cba')"
b"+        ydl = YDL({u'format': u'[format_id^=abc]'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'abc-cba')"
b' '
b'         # does not start with (!^=)'
b"-        ydl = YDL({'format': '[format_id!^=abc]'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'zxc-cxz')"
b'-'
b"-        ydl = YDL({'format': '[format_id!^=abc][format_id!^=zxc]'})"
b"+        ydl = YDL({u'format': u'[format_id!^=abc]'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'zxc-cxz')"
b'+'
b"+        ydl = YDL({u'format': u'[format_id!^=abc][format_id!^=zxc]'})"
b'         self.assertRaises(ExtractorError, ydl.process_ie_result, info_dict.copy())'
b' '
b'         # ends with ($=)'
b"-        ydl = YDL({'format': '[format_id$=cba]'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'abc-cba')"
b"+        ydl = YDL({u'format': u'[format_id$=cba]'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'abc-cba')"
b' '
b'         # does not end with (!$=)'
b"-        ydl = YDL({'format': '[format_id!$=cba]'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'zxc-cxz')"
b'-'
b"-        ydl = YDL({'format': '[format_id!$=cba][format_id!$=cxz]'})"
b"+        ydl = YDL({u'format': u'[format_id!$=cba]'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'zxc-cxz')"
b'+'
b"+        ydl = YDL({u'format': u'[format_id!$=cba][format_id!$=cxz]'})"
b'         self.assertRaises(ExtractorError, ydl.process_ie_result, info_dict.copy())'
b' '
b'         # contains (*=)'
b"-        ydl = YDL({'format': '[format_id*=bc-cb]'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'abc-cba')"
b"+        ydl = YDL({u'format': u'[format_id*=bc-cb]'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'abc-cba')"
b' '
b'         # does not contain (!*=)'
b"-        ydl = YDL({'format': '[format_id!*=bc-cb]'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'zxc-cxz')"
b'-'
b"-        ydl = YDL({'format': '[format_id!*=abc][format_id!*=zxc]'})"
b"+        ydl = YDL({u'format': u'[format_id!*=bc-cb]'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'zxc-cxz')"
b'+'
b"+        ydl = YDL({u'format': u'[format_id!*=abc][format_id!*=zxc]'})"
b'         self.assertRaises(ExtractorError, ydl.process_ie_result, info_dict.copy())'
b' '
b"-        ydl = YDL({'format': '[format_id!*=-]'})"
b"+        ydl = YDL({u'format': u'[format_id!*=-]'})"
b'         self.assertRaises(ExtractorError, ydl.process_ie_result, info_dict.copy())'
b' '
b'     def test_youtube_format_selection(self):'
b'@@ -341,16 +348,16 @@'
b'         return'
b' '
b'         order = ['
b"-            '38', '37', '46', '22', '45', '35', '44', '18', '34', '43', '6', '5', '17', '36', '13',"
b"+            u'38', u'37', u'46', u'22', u'45', u'35', u'44', u'18', u'34', u'43', u'6', u'5', u'17', u'36', u'13',"
b'             # Apple HTTP Live Streaming'
b"-            '96', '95', '94', '93', '92', '132', '151',"
b"+            u'96', u'95', u'94', u'93', u'92', u'132', u'151',"
b'             # 3D'
b"-            '85', '84', '102', '83', '101', '82', '100',"
b"+            u'85', u'84', u'102', u'83', u'101', u'82', u'100',"
b'             # Dash video'
b"-            '137', '248', '136', '247', '135', '246',"
b"-            '245', '244', '134', '243', '133', '242', '160',"
b"+            u'137', u'248', u'136', u'247', u'135', u'246',"
b"+            u'245', u'244', u'134', u'243', u'133', u'242', u'160',"
b'             # Dash audio'
b"-            '141', '172', '140', '171', '139',"
b"+            u'141', u'172', u'140', u'171', u'139',"
b'         ]'
b' '
b'         def format_info(f_id):'
b'@@ -361,73 +368,73 @@'
b'             # commit a6c2c24479e5f4827ceb06f64d855329c0a6f593'
b'             # test_YoutubeDL.test_youtube_format_selection is broken without'
b'             # this fix'
b"-            if 'acodec' in info and 'vcodec' not in info:"
b"-                info['vcodec'] = 'none'"
b"-            elif 'vcodec' in info and 'acodec' not in info:"
b"-                info['acodec'] = 'none'"
b'-'
b"-            info['format_id'] = f_id"
b"-            info['url'] = 'url:' + f_id"
b"+            if u'acodec' in info and u'vcodec' not in info:"
b"+                info[u'vcodec'] = u'none'"
b"+            elif u'vcodec' in info and u'acodec' not in info:"
b"+                info[u'acodec'] = u'none'"
b'+'
b"+            info[u'format_id'] = f_id"
b"+            info[u'url'] = u'url:' + f_id"
b'             return info'
b'         formats_order = [format_info(f_id) for f_id in order]'
b' '
b"-        info_dict = _make_result(list(formats_order), extractor='youtube')"
b"-        ydl = YDL({'format': 'bestvideo+bestaudio'})"
b"+        info_dict = _make_result(list(formats_order), extractor=u'youtube')"
b"+        ydl = YDL({u'format': u'bestvideo+bestaudio'})"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(info_dict)'
b'         downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], '248+172')"
b"-        self.assertEqual(downloaded['ext'], 'mp4')"
b'-'
b"-        info_dict = _make_result(list(formats_order), extractor='youtube')"
b"-        ydl = YDL({'format': 'bestvideo[height>=999999]+bestaudio/best'})"
b"+        self.assertEqual(downloaded[u'format_id'], u'248+172')"
b"+        self.assertEqual(downloaded[u'ext'], u'mp4')"
b'+'
b"+        info_dict = _make_result(list(formats_order), extractor=u'youtube')"
b"+        ydl = YDL({u'format': u'bestvideo[height>=999999]+bestaudio/best'})"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(info_dict)'
b'         downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], '38')"
b'-'
b"-        info_dict = _make_result(list(formats_order), extractor='youtube')"
b"-        ydl = YDL({'format': 'bestvideo/best,bestaudio'})"
b"+        self.assertEqual(downloaded[u'format_id'], u'38')"
b'+'
b"+        info_dict = _make_result(list(formats_order), extractor=u'youtube')"
b"+        ydl = YDL({u'format': u'bestvideo/best,bestaudio'})"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(info_dict)'
b"-        downloaded_ids = [info['format_id'] for info in ydl.downloaded_info_dicts]"
b"-        self.assertEqual(downloaded_ids, ['137', '141'])"
b'-'
b"-        info_dict = _make_result(list(formats_order), extractor='youtube')"
b"-        ydl = YDL({'format': '(bestvideo[ext=mp4],bestvideo[ext=webm])+bestaudio'})"
b"+        downloaded_ids = [info[u'format_id'] for info in ydl.downloaded_info_dicts]"
b"+        self.assertEqual(downloaded_ids, [u'137', u'141'])"
b'+'
b"+        info_dict = _make_result(list(formats_order), extractor=u'youtube')"
b"+        ydl = YDL({u'format': u'(bestvideo[ext=mp4],bestvideo[ext=webm])+bestaudio'})"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(info_dict)'
b"-        downloaded_ids = [info['format_id'] for info in ydl.downloaded_info_dicts]"
b"-        self.assertEqual(downloaded_ids, ['137+141', '248+141'])"
b'-'
b"-        info_dict = _make_result(list(formats_order), extractor='youtube')"
b"-        ydl = YDL({'format': '(bestvideo[ext=mp4],bestvideo[ext=webm])[height<=720]+bestaudio'})"
b"+        downloaded_ids = [info[u'format_id'] for info in ydl.downloaded_info_dicts]"
b"+        self.assertEqual(downloaded_ids, [u'137+141', u'248+141'])"
b'+'
b"+        info_dict = _make_result(list(formats_order), extractor=u'youtube')"
b"+        ydl = YDL({u'format': u'(bestvideo[ext=mp4],bestvideo[ext=webm])[height<=720]+bestaudio'})"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(info_dict)'
b"-        downloaded_ids = [info['format_id'] for info in ydl.downloaded_info_dicts]"
b"-        self.assertEqual(downloaded_ids, ['136+141', '247+141'])"
b'-'
b"-        info_dict = _make_result(list(formats_order), extractor='youtube')"
b"-        ydl = YDL({'format': '(bestvideo[ext=none]/bestvideo[ext=webm])+bestaudio'})"
b"+        downloaded_ids = [info[u'format_id'] for info in ydl.downloaded_info_dicts]"
b"+        self.assertEqual(downloaded_ids, [u'136+141', u'247+141'])"
b'+'
b"+        info_dict = _make_result(list(formats_order), extractor=u'youtube')"
b"+        ydl = YDL({u'format': u'(bestvideo[ext=none]/bestvideo[ext=webm])+bestaudio'})"
b'         ydl.sort_formats(info_dict)'
b'         ydl.process_ie_result(info_dict)'
b"-        downloaded_ids = [info['format_id'] for info in ydl.downloaded_info_dicts]"
b"-        self.assertEqual(downloaded_ids, ['248+141'])"
b'-'
b'-        for f1, f2 in zip(formats_order, formats_order[1:]):'
b"-            info_dict = _make_result([f1, f2], extractor='youtube')"
b"-            ydl = YDL({'format': 'best/bestvideo'})"
b"+        downloaded_ids = [info[u'format_id'] for info in ydl.downloaded_info_dicts]"
b"+        self.assertEqual(downloaded_ids, [u'248+141'])"
b'+'
b'+        for f1, f2 in izip(formats_order, formats_order[1:]):'
b"+            info_dict = _make_result([f1, f2], extractor=u'youtube')"
b"+            ydl = YDL({u'format': u'best/bestvideo'})"
b'             ydl.sort_formats(info_dict)'
b'             ydl.process_ie_result(info_dict)'
b'             downloaded = ydl.downloaded_info_dicts[0]'
b"-            self.assertEqual(downloaded['format_id'], f1['format_id'])"
b'-'
b"-            info_dict = _make_result([f2, f1], extractor='youtube')"
b"-            ydl = YDL({'format': 'best/bestvideo'})"
b"+            self.assertEqual(downloaded[u'format_id'], f1[u'format_id'])"
b'+'
b"+            info_dict = _make_result([f2, f1], extractor=u'youtube')"
b"+            ydl = YDL({u'format': u'best/bestvideo'})"
b'             ydl.sort_formats(info_dict)'
b'             ydl.process_ie_result(info_dict)'
b'             downloaded = ydl.downloaded_info_dicts[0]'
b"-            self.assertEqual(downloaded['format_id'], f1['format_id'])"
b"+            self.assertEqual(downloaded[u'format_id'], f1[u'format_id'])"
b' '
b'     def test_audio_only_extractor_format_selection(self):'
b'         # For extractors with incomplete formats (all formats are audio-only or'
b'@@ -435,311 +442,313 @@'
b'         # video-only or audio-only formats (as per'
b'         # https://github.com/ytdl-org/youtube-dl/pull/5556)'
b'         formats = ['
b"-            {'format_id': 'low', 'ext': 'mp3', 'preference': 1, 'vcodec': 'none', 'url': TEST_URL},"
b"-            {'format_id': 'high', 'ext': 'mp3', 'preference': 2, 'vcodec': 'none', 'url': TEST_URL},"
b"+            {u'format_id': u'low', u'ext': u'mp3', u'preference': 1, u'vcodec': u'none', u'url': TEST_URL},"
b"+            {u'format_id': u'high', u'ext': u'mp3', u'preference': 2, u'vcodec': u'none', u'url': TEST_URL},"
b'         ]'
b'         info_dict = _make_result(formats)'
b' '
b"-        ydl = YDL({'format': 'best'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'high')"
b'-'
b"-        ydl = YDL({'format': 'worst'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'low')"
b"+        ydl = YDL({u'format': u'best'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'high')"
b'+'
b"+        ydl = YDL({u'format': u'worst'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'low')"
b' '
b'     def test_format_not_available(self):'
b'         formats = ['
b"-            {'format_id': 'regular', 'ext': 'mp4', 'height': 360, 'url': TEST_URL},"
b"-            {'format_id': 'video', 'ext': 'mp4', 'height': 720, 'acodec': 'none', 'url': TEST_URL},"
b"+            {u'format_id': u'regular', u'ext': u'mp4', u'height': 360, u'url': TEST_URL},"
b"+            {u'format_id': u'video', u'ext': u'mp4', u'height': 720, u'acodec': u'none', u'url': TEST_URL},"
b'         ]'
b'         info_dict = _make_result(formats)'
b' '
b'         # This must fail since complete video-audio format does not match filter'
b'         # and extractor does not provide incomplete only formats (i.e. only'
b'         # video-only or audio-only).'
b"-        ydl = YDL({'format': 'best[height>360]'})"
b"+        ydl = YDL({u'format': u'best[height>360]'})"
b'         self.assertRaises(ExtractorError, ydl.process_ie_result, info_dict.copy())'
b' '
b'     def test_format_selection_issue_10083(self):'
b'         # See https://github.com/ytdl-org/youtube-dl/issues/10083'
b'         formats = ['
b"-            {'format_id': 'regular', 'height': 360, 'url': TEST_URL},"
b"-            {'format_id': 'video', 'height': 720, 'acodec': 'none', 'url': TEST_URL},"
b"-            {'format_id': 'audio', 'vcodec': 'none', 'url': TEST_URL},"
b"+            {u'format_id': u'regular', u'height': 360, u'url': TEST_URL},"
b"+            {u'format_id': u'video', u'height': 720, u'acodec': u'none', u'url': TEST_URL},"
b"+            {u'format_id': u'audio', u'vcodec': u'none', u'url': TEST_URL},"
b'         ]'
b'         info_dict = _make_result(formats)'
b' '
b"-        ydl = YDL({'format': 'best[height>360]/bestvideo[height>360]+bestaudio'})"
b'-        ydl.process_ie_result(info_dict.copy())'
b"-        self.assertEqual(ydl.downloaded_info_dicts[0]['format_id'], 'video+audio')"
b"+        ydl = YDL({u'format': u'best[height>360]/bestvideo[height>360]+bestaudio'})"
b'+        ydl.process_ie_result(info_dict.copy())'
b"+        self.assertEqual(ydl.downloaded_info_dicts[0][u'format_id'], u'video+audio')"
b' '
b'     def test_invalid_format_specs(self):'
b'         def assert_syntax_error(format_spec):'
b"-            self.assertRaises(SyntaxError, YDL, {'format': format_spec})"
b'-'
b"-        assert_syntax_error('bestvideo,,best')"
b"-        assert_syntax_error('+bestaudio')"
b"-        assert_syntax_error('bestvideo+')"
b"-        assert_syntax_error('/')"
b"-        assert_syntax_error('[720<height]')"
b"+            self.assertRaises(SyntaxError, YDL, {u'format': format_spec})"
b'+'
b"+        assert_syntax_error(u'bestvideo,,best')"
b"+        assert_syntax_error(u'+bestaudio')"
b"+        assert_syntax_error(u'bestvideo+')"
b"+        assert_syntax_error(u'/')"
b"+        assert_syntax_error(u'[720<height]')"
b' '
b'     def test_format_filtering(self):'
b'         formats = ['
b"-            {'format_id': 'A', 'filesize': 500, 'width': 1000, 'aspect_ratio': 1.0},"
b"-            {'format_id': 'B', 'filesize': 1000, 'width': 500, 'aspect_ratio': 1.33},"
b"-            {'format_id': 'C', 'filesize': 1000, 'width': 400, 'aspect_ratio': 1.5},"
b"-            {'format_id': 'D', 'filesize': 2000, 'width': 600, 'aspect_ratio': 1.78},"
b"-            {'format_id': 'E', 'filesize': 3000, 'aspect_ratio': 0.56},"
b"-            {'format_id': 'F'},"
b"-            {'format_id': 'G', 'filesize': 1000000},"
b"+            {u'format_id': u'A', u'filesize': 500, u'width': 1000, u'aspect_ratio': 1.0},"
b"+            {u'format_id': u'B', u'filesize': 1000, u'width': 500, u'aspect_ratio': 1.33},"
b"+            {u'format_id': u'C', u'filesize': 1000, u'width': 400, u'aspect_ratio': 1.5},"
b"+            {u'format_id': u'D', u'filesize': 2000, u'width': 600, u'aspect_ratio': 1.78},"
b"+            {u'format_id': u'E', u'filesize': 3000, u'aspect_ratio': 0.56},"
b"+            {u'format_id': u'F'},"
b"+            {u'format_id': u'G', u'filesize': 1000000},"
b'         ]'
b'         for f in formats:'
b"-            f['url'] = 'http://_/'"
b"-            f['ext'] = 'unknown'"
b"-        info_dict = _make_result(formats, _format_sort_fields=('id', ))"
b'-'
b"-        ydl = YDL({'format': 'best[filesize<3000]'})"
b'-        ydl.process_ie_result(info_dict)'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'D')"
b'-'
b"-        ydl = YDL({'format': 'best[filesize<=3000]'})"
b'-        ydl.process_ie_result(info_dict)'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'E')"
b'-'
b"-        ydl = YDL({'format': 'best[filesize <= ? 3000]'})"
b'-        ydl.process_ie_result(info_dict)'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'F')"
b'-'
b"-        ydl = YDL({'format': 'best [filesize = 1000] [width>450]'})"
b'-        ydl.process_ie_result(info_dict)'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'B')"
b'-'
b"-        ydl = YDL({'format': 'best [filesize = 1000] [width!=450]'})"
b'-        ydl.process_ie_result(info_dict)'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'C')"
b'-'
b"-        ydl = YDL({'format': '[filesize>?1]'})"
b'-        ydl.process_ie_result(info_dict)'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'G')"
b'-'
b"-        ydl = YDL({'format': '[filesize<1M]'})"
b'-        ydl.process_ie_result(info_dict)'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'E')"
b'-'
b"-        ydl = YDL({'format': '[filesize<1MiB]'})"
b'-        ydl.process_ie_result(info_dict)'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'G')"
b'-'
b"-        ydl = YDL({'format': 'all[width>=400][width<=600]'})"
b'-        ydl.process_ie_result(info_dict)'
b"-        downloaded_ids = [info['format_id'] for info in ydl.downloaded_info_dicts]"
b"-        self.assertEqual(downloaded_ids, ['D', 'C', 'B'])"
b'-'
b"-        ydl = YDL({'format': 'best[height<40]'})"
b"+            f[u'url'] = u'http://_/'"
b"+            f[u'ext'] = u'unknown'"
b"+        info_dict = _make_result(formats, _format_sort_fields=(u'id', ))"
b'+'
b"+        ydl = YDL({u'format': u'best[filesize<3000]'})"
b'+        ydl.process_ie_result(info_dict)'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'D')"
b'+'
b"+        ydl = YDL({u'format': u'best[filesize<=3000]'})"
b'+        ydl.process_ie_result(info_dict)'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'E')"
b'+'
b"+        ydl = YDL({u'format': u'best[filesize <= ? 3000]'})"
b'+        ydl.process_ie_result(info_dict)'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'F')"
b'+'
b"+        ydl = YDL({u'format': u'best [filesize = 1000] [width>450]'})"
b'+        ydl.process_ie_result(info_dict)'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'B')"
b'+'
b"+        ydl = YDL({u'format': u'best [filesize = 1000] [width!=450]'})"
b'+        ydl.process_ie_result(info_dict)'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'C')"
b'+'
b"+        ydl = YDL({u'format': u'[filesize>?1]'})"
b'+        ydl.process_ie_result(info_dict)'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'G')"
b'+'
b"+        ydl = YDL({u'format': u'[filesize<1M]'})"
b'+        ydl.process_ie_result(info_dict)'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'E')"
b'+'
b"+        ydl = YDL({u'format': u'[filesize<1MiB]'})"
b'+        ydl.process_ie_result(info_dict)'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'G')"
b'+'
b"+        ydl = YDL({u'format': u'all[width>=400][width<=600]'})"
b'+        ydl.process_ie_result(info_dict)'
b"+        downloaded_ids = [info[u'format_id'] for info in ydl.downloaded_info_dicts]"
b"+        self.assertEqual(downloaded_ids, [u'D', u'C', u'B'])"
b'+'
b"+        ydl = YDL({u'format': u'best[height<40]'})"
b'         with contextlib.suppress(ExtractorError):'
b'             ydl.process_ie_result(info_dict)'
b'         self.assertEqual(ydl.downloaded_info_dicts, [])'
b' '
b"-        ydl = YDL({'format': 'best[aspect_ratio=1]'})"
b'-        ydl.process_ie_result(info_dict)'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'A')"
b'-'
b"-        ydl = YDL({'format': 'all[aspect_ratio > 1.00]'})"
b'-        ydl.process_ie_result(info_dict)'
b"-        downloaded_ids = [info['format_id'] for info in ydl.downloaded_info_dicts]"
b"-        self.assertEqual(downloaded_ids, ['D', 'C', 'B'])"
b'-'
b"-        ydl = YDL({'format': 'all[aspect_ratio < 1.00]'})"
b'-        ydl.process_ie_result(info_dict)'
b"-        downloaded_ids = [info['format_id'] for info in ydl.downloaded_info_dicts]"
b"-        self.assertEqual(downloaded_ids, ['E'])"
b'-'
b"-        ydl = YDL({'format': 'best[aspect_ratio=1.5]'})"
b'-        ydl.process_ie_result(info_dict)'
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['format_id'], 'C')"
b'-'
b"-        ydl = YDL({'format': 'all[aspect_ratio!=1]'})"
b'-        ydl.process_ie_result(info_dict)'
b"-        downloaded_ids = [info['format_id'] for info in ydl.downloaded_info_dicts]"
b"-        self.assertEqual(downloaded_ids, ['E', 'D', 'C', 'B'])"
b'-'
b"-    @patch('yt_dlp.postprocessor.ffmpeg.FFmpegMergerPP.available', False)"
b"+        ydl = YDL({u'format': u'best[aspect_ratio=1]'})"
b'+        ydl.process_ie_result(info_dict)'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'A')"
b'+'
b"+        ydl = YDL({u'format': u'all[aspect_ratio > 1.00]'})"
b'+        ydl.process_ie_result(info_dict)'
b"+        downloaded_ids = [info[u'format_id'] for info in ydl.downloaded_info_dicts]"
b"+        self.assertEqual(downloaded_ids, [u'D', u'C', u'B'])"
b'+'
b"+        ydl = YDL({u'format': u'all[aspect_ratio < 1.00]'})"
b'+        ydl.process_ie_result(info_dict)'
b"+        downloaded_ids = [info[u'format_id'] for info in ydl.downloaded_info_dicts]"
b"+        self.assertEqual(downloaded_ids, [u'E'])"
b'+'
b"+        ydl = YDL({u'format': u'best[aspect_ratio=1.5]'})"
b'+        ydl.process_ie_result(info_dict)'
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'format_id'], u'C')"
b'+'
b"+        ydl = YDL({u'format': u'all[aspect_ratio!=1]'})"
b'+        ydl.process_ie_result(info_dict)'
b"+        downloaded_ids = [info[u'format_id'] for info in ydl.downloaded_info_dicts]"
b"+        self.assertEqual(downloaded_ids, [u'E', u'D', u'C', u'B'])"
b'+'
b"+    @patch(u'yt_dlp.postprocessor.ffmpeg.FFmpegMergerPP.available', False)"
b'     def test_default_format_spec_without_ffmpeg(self):'
b'         ydl = YDL({})'
b"-        self.assertEqual(ydl._default_format_spec({}), 'best/bestvideo+bestaudio')"
b'-'
b"-        ydl = YDL({'simulate': True})"
b"-        self.assertEqual(ydl._default_format_spec({}), 'best/bestvideo+bestaudio')"
b"+        self.assertEqual(ydl._default_format_spec({}), u'best/bestvideo+bestaudio')"
b'+'
b"+        ydl = YDL({u'simulate': True})"
b"+        self.assertEqual(ydl._default_format_spec({}), u'best/bestvideo+bestaudio')"
b' '
b'         ydl = YDL({})'
b"-        self.assertEqual(ydl._default_format_spec({'is_live': True}), 'best/bestvideo+bestaudio')"
b'-'
b"-        ydl = YDL({'simulate': True})"
b"-        self.assertEqual(ydl._default_format_spec({'is_live': True}), 'best/bestvideo+bestaudio')"
b'-'
b"-        ydl = YDL({'outtmpl': '-'})"
b"-        self.assertEqual(ydl._default_format_spec({}), 'best/bestvideo+bestaudio')"
b"+        self.assertEqual(ydl._default_format_spec({u'is_live': True}), u'best/bestvideo+bestaudio')"
b'+'
b"+        ydl = YDL({u'simulate': True})"
b"+        self.assertEqual(ydl._default_format_spec({u'is_live': True}), u'best/bestvideo+bestaudio')"
b'+'
b"+        ydl = YDL({u'outtmpl': u'-'})"
b"+        self.assertEqual(ydl._default_format_spec({}), u'best/bestvideo+bestaudio')"
b' '
b'         ydl = YDL({})'
b"-        self.assertEqual(ydl._default_format_spec({}), 'best/bestvideo+bestaudio')"
b"-        self.assertEqual(ydl._default_format_spec({'is_live': True}), 'best/bestvideo+bestaudio')"
b'-'
b"-    @patch('yt_dlp.postprocessor.ffmpeg.FFmpegMergerPP.available', True)"
b"-    @patch('yt_dlp.postprocessor.ffmpeg.FFmpegMergerPP.can_merge', lambda _: True)"
b"+        self.assertEqual(ydl._default_format_spec({}), u'best/bestvideo+bestaudio')"
b"+        self.assertEqual(ydl._default_format_spec({u'is_live': True}), u'best/bestvideo+bestaudio')"
b'+'
b"+    @patch(u'yt_dlp.postprocessor.ffmpeg.FFmpegMergerPP.available', True)"
b"+    @patch(u'yt_dlp.postprocessor.ffmpeg.FFmpegMergerPP.can_merge', lambda _: True)"
b'     def test_default_format_spec_with_ffmpeg(self):'
b'         ydl = YDL({})'
b"-        self.assertEqual(ydl._default_format_spec({}), 'bestvideo*+bestaudio/best')"
b'-'
b"-        ydl = YDL({'simulate': True})"
b"-        self.assertEqual(ydl._default_format_spec({}), 'bestvideo*+bestaudio/best')"
b"+        self.assertEqual(ydl._default_format_spec({}), u'bestvideo*+bestaudio/best')"
b'+'
b"+        ydl = YDL({u'simulate': True})"
b"+        self.assertEqual(ydl._default_format_spec({}), u'bestvideo*+bestaudio/best')"
b' '
b'         ydl = YDL({})'
b"-        self.assertEqual(ydl._default_format_spec({'is_live': True}), 'best/bestvideo+bestaudio')"
b'-'
b"-        ydl = YDL({'simulate': True})"
b"-        self.assertEqual(ydl._default_format_spec({'is_live': True}), 'best/bestvideo+bestaudio')"
b'-'
b"-        ydl = YDL({'outtmpl': '-'})"
b"-        self.assertEqual(ydl._default_format_spec({}), 'best/bestvideo+bestaudio')"
b"+        self.assertEqual(ydl._default_format_spec({u'is_live': True}), u'best/bestvideo+bestaudio')"
b'+'
b"+        ydl = YDL({u'simulate': True})"
b"+        self.assertEqual(ydl._default_format_spec({u'is_live': True}), u'best/bestvideo+bestaudio')"
b'+'
b"+        ydl = YDL({u'outtmpl': u'-'})"
b"+        self.assertEqual(ydl._default_format_spec({}), u'best/bestvideo+bestaudio')"
b' '
b'         ydl = YDL({})'
b"-        self.assertEqual(ydl._default_format_spec({}), 'bestvideo*+bestaudio/best')"
b"-        self.assertEqual(ydl._default_format_spec({'is_live': True}), 'best/bestvideo+bestaudio')"
b"+        self.assertEqual(ydl._default_format_spec({}), u'bestvideo*+bestaudio/best')"
b"+        self.assertEqual(ydl._default_format_spec({u'is_live': True}), u'best/bestvideo+bestaudio')"
b' '
b' '
b' class TestYoutubeDL(unittest.TestCase):'
b'     def test_subtitles(self):'
b'         def s_formats(lang, autocaption=False):'
b'             return [{'
b"-                'ext': ext,"
b"-                'url': f'http://localhost/video.{lang}.{ext}',"
b"-                '_auto': autocaption,"
b"-            } for ext in ['vtt', 'srt', 'ass']]"
b"-        subtitles = {l: s_formats(l) for l in ['en', 'fr', 'es']}"
b"-        auto_captions = {l: s_formats(l, True) for l in ['it', 'pt', 'es']}"
b"+                u'ext': ext,"
b"+                u'url': f'http://localhost/video.{lang}.{ext}',"
b"+                u'_auto': autocaption,"
b"+            } for ext in [u'vtt', u'srt', u'ass']]"
b"+        subtitles = dict((l, s_formats(l)) for l in [u'en', u'fr', u'es'])"
b"+        auto_captions = dict((l, s_formats(l, True)) for l in [u'it', u'pt', u'es'])"
b'         info_dict = {'
b"-            'id': 'test',"
b"-            'title': 'Test',"
b"-            'url': 'http://localhost/video.mp4',"
b"-            'subtitles': subtitles,"
b"-            'automatic_captions': auto_captions,"
b"-            'extractor': 'TEST',"
b"-            'webpage_url': 'http://example.com/watch?v=shenanigans',"
b"+            u'id': u'test',"
b"+            u'title': u'Test',"
b"+            u'url': u'http://localhost/video.mp4',"
b"+            u'subtitles': subtitles,"
b"+            u'automatic_captions': auto_captions,"
b"+            u'extractor': u'TEST',"
b"+            u'webpage_url': u'http://example.com/watch?v=shenanigans',"
b'         }'
b' '
b'         def get_info(params={}):'
b"-            params.setdefault('simulate', True)"
b"+            params.setdefault(u'simulate', True)"
b'             ydl = YDL(params)'
b'             ydl.report_warning = lambda *args, **kargs: None'
b'             return ydl.process_video_result(info_dict, download=False)'
b' '
b'         result = get_info()'
b"-        self.assertFalse(result.get('requested_subtitles'))"
b"-        self.assertEqual(result['subtitles'], subtitles)"
b"-        self.assertEqual(result['automatic_captions'], auto_captions)"
b'-'
b"-        result = get_info({'writesubtitles': True})"
b"-        subs = result['requested_subtitles']"
b"+        self.assertFalse(result.get(u'requested_subtitles'))"
b"+        self.assertEqual(result[u'subtitles'], subtitles)"
b"+        self.assertEqual(result[u'automatic_captions'], auto_captions)"
b'+'
b"+        result = get_info({u'writesubtitles': True})"
b"+        subs = result[u'requested_subtitles']"
b'         self.assertTrue(subs)'
b"-        self.assertEqual(set(subs.keys()), {'en'})"
b"-        self.assertTrue(subs['en'].get('data') is None)"
b"-        self.assertEqual(subs['en']['ext'], 'ass')"
b'-'
b"-        result = get_info({'writesubtitles': True, 'subtitlesformat': 'foo/srt'})"
b"-        subs = result['requested_subtitles']"
b"-        self.assertEqual(subs['en']['ext'], 'srt')"
b'-'
b"-        result = get_info({'writesubtitles': True, 'subtitleslangs': ['es', 'fr', 'it']})"
b"-        subs = result['requested_subtitles']"
b"+        self.assertEqual(set(subs.keys()), set([u'en']))"
b"+        self.assertTrue(subs[u'en'].get(u'data') is None)"
b"+        self.assertEqual(subs[u'en'][u'ext'], u'ass')"
b'+'
b"+        result = get_info({u'writesubtitles': True, u'subtitlesformat': u'foo/srt'})"
b"+        subs = result[u'requested_subtitles']"
b"+        self.assertEqual(subs[u'en'][u'ext'], u'srt')"
b'+'
b"+        result = get_info({u'writesubtitles': True, u'subtitleslangs': [u'es', u'fr', u'it']})"
b"+        subs = result[u'requested_subtitles']"
b'         self.assertTrue(subs)'
b"-        self.assertEqual(set(subs.keys()), {'es', 'fr'})"
b'-'
b"-        result = get_info({'writesubtitles': True, 'subtitleslangs': ['all', '-en']})"
b"-        subs = result['requested_subtitles']"
b"+        self.assertEqual(set(subs.keys()), set([u'es', u'fr']))"
b'+'
b"+        result = get_info({u'writesubtitles': True, u'subtitleslangs': [u'all', u'-en']})"
b"+        subs = result[u'requested_subtitles']"
b'         self.assertTrue(subs)'
b"-        self.assertEqual(set(subs.keys()), {'es', 'fr'})"
b'-'
b"-        result = get_info({'writesubtitles': True, 'subtitleslangs': ['en', 'fr', '-en']})"
b"-        subs = result['requested_subtitles']"
b"+        self.assertEqual(set(subs.keys()), set([u'es', u'fr']))"
b'+'
b"+        result = get_info({u'writesubtitles': True, u'subtitleslangs': [u'en', u'fr', u'-en']})"
b"+        subs = result[u'requested_subtitles']"
b'         self.assertTrue(subs)'
b"-        self.assertEqual(set(subs.keys()), {'fr'})"
b'-'
b"-        result = get_info({'writesubtitles': True, 'subtitleslangs': ['-en', 'en']})"
b"-        subs = result['requested_subtitles']"
b"+        self.assertEqual(set(subs.keys()), set([u'fr']))"
b'+'
b"+        result = get_info({u'writesubtitles': True, u'subtitleslangs': [u'-en', u'en']})"
b"+        subs = result[u'requested_subtitles']"
b'         self.assertTrue(subs)'
b"-        self.assertEqual(set(subs.keys()), {'en'})"
b'-'
b"-        result = get_info({'writesubtitles': True, 'subtitleslangs': ['e.+']})"
b"-        subs = result['requested_subtitles']"
b"+        self.assertEqual(set(subs.keys()), set([u'en']))"
b'+'
b"+        result = get_info({u'writesubtitles': True, u'subtitleslangs': [u'e.+']})"
b"+        subs = result[u'requested_subtitles']"
b'         self.assertTrue(subs)'
b"-        self.assertEqual(set(subs.keys()), {'es', 'en'})"
b'-'
b"-        result = get_info({'writesubtitles': True, 'writeautomaticsub': True, 'subtitleslangs': ['es', 'pt']})"
b"-        subs = result['requested_subtitles']"
b"+        self.assertEqual(set(subs.keys()), set([u'es', u'en']))"
b'+'
b"+        result = get_info({u'writesubtitles': True, u'writeautomaticsub': True, u'subtitleslangs': [u'es', u'pt']})"
b"+        subs = result[u'requested_subtitles']"
b'         self.assertTrue(subs)'
b"-        self.assertEqual(set(subs.keys()), {'es', 'pt'})"
b"-        self.assertFalse(subs['es']['_auto'])"
b"-        self.assertTrue(subs['pt']['_auto'])"
b'-'
b"-        result = get_info({'writeautomaticsub': True, 'subtitleslangs': ['es', 'pt']})"
b"-        subs = result['requested_subtitles']"
b"+        self.assertEqual(set(subs.keys()), set([u'es', u'pt']))"
b"+        self.assertFalse(subs[u'es'][u'_auto'])"
b"+        self.assertTrue(subs[u'pt'][u'_auto'])"
b'+'
b"+        result = get_info({u'writeautomaticsub': True, u'subtitleslangs': [u'es', u'pt']})"
b"+        subs = result[u'requested_subtitles']"
b'         self.assertTrue(subs)'
b"-        self.assertEqual(set(subs.keys()), {'es', 'pt'})"
b"-        self.assertTrue(subs['es']['_auto'])"
b"-        self.assertTrue(subs['pt']['_auto'])"
b"+        self.assertEqual(set(subs.keys()), set([u'es', u'pt']))"
b"+        self.assertTrue(subs[u'es'][u'_auto'])"
b"+        self.assertTrue(subs[u'pt'][u'_auto'])"
b' '
b'     def test_add_extra_info(self):'
b'         test_dict = {'
b"-            'extractor': 'Foo',"
b"+            u'extractor': u'Foo',"
b'         }'
b'         extra_info = {'
b"-            'extractor': 'Bar',"
b"-            'playlist': 'funny videos',"
b"+            u'extractor': u'Bar',"
b"+            u'playlist': u'funny videos',"
b'         }'
b'         YDL.add_extra_info(test_dict, extra_info)'
b"-        self.assertEqual(test_dict['extractor'], 'Foo')"
b"-        self.assertEqual(test_dict['playlist'], 'funny videos')"
b"+        self.assertEqual(test_dict[u'extractor'], u'Foo')"
b"+        self.assertEqual(test_dict[u'playlist'], u'funny videos')"
b' '
b'     outtmpl_info = {'
b"-        'id': '1234',"
b"-        'ext': 'mp4',"
b"-        'width': None,"
b"-        'height': 1080,"
b"-        'filesize': 1024,"
b"-        'title1': '$PATH',"
b"-        'title2': '%PATH%',"
b"-        'title3': 'foo/bar\\\\test',"
b'-        \'title4\': \'foo "bar" test\','
b"-        'title5': '\xc3\xa1\xc3\xa9\xc3\xad \xf0\x9d\x90\x80',"
b"-        'timestamp': 1618488000,"
b"-        'duration': 100000,"
b"-        'playlist_index': 1,"
b"-        'playlist_autonumber': 2,"
b"-        '__last_playlist_index': 100,"
b"-        'n_entries': 10,"
b"-        'formats': ["
b"-            {'id': 'id 1', 'height': 1080, 'width': 1920},"
b"-            {'id': 'id 2', 'height': 720},"
b"-            {'id': 'id 3'},"
b"+        u'id': u'1234',"
b"+        u'ext': u'mp4',"
b"+        u'width': None,"
b"+        u'height': 1080,"
b"+        u'filesize': 1024,"
b"+        u'title1': u'$PATH',"
b"+        u'title2': u'%PATH%',"
b"+        u'title3': u'foo/bar\\\\test',"
b'+        u\'title4\': u\'foo "bar" test\','
b"+        u'title5': u'\xc3\xa1\xc3\xa9\xc3\xad \xf0\x9d\x90\x80',"
b"+        u'timestamp': 1618488000,"
b"+        u'duration': 100000,"
b"+        u'playlist_index': 1,"
b"+        u'playlist_autonumber': 2,"
b"+        u'__last_playlist_index': 100,"
b"+        u'n_entries': 10,"
b"+        u'formats': ["
b"+            {u'id': u'id 1', u'height': 1080, u'width': 1920},"
b"+            {u'id': u'id 2', u'height': 720},"
b"+            {u'id': u'id 3'},"
b'         ],'
b'     }'
b' '
b'     def test_prepare_outtmpl_and_filename(self):'
b'-        def test(tmpl, expected, *, info=None, **params):'
b"-            params['outtmpl'] = tmpl"
b'+        def test(tmpl, expected, **params):'
b"+            if 'info' in params: info = params['info']; del params['info']"
b'+            else: info = None'
b"+            params[u'outtmpl'] = tmpl"
b'             ydl = FakeYDL(params)'
b'             ydl._num_downloads = 1'
b'             self.assertEqual(ydl.validate_outtmpl(tmpl), None)'
b'@@ -749,7 +758,7 @@'
b' '
b'             if not isinstance(expected, (list, tuple)):'
b'                 expected = (expected, expected)'
b"-            for (name, got), expect in zip((('outtmpl', out), ('filename', fname)), expected):"
b"+            for (name, got), expect in izip(((u'outtmpl', out), (u'filename', fname)), expected):"
b'                 if callable(expect):'
b"                     self.assertTrue(expect(got), f'Wrong {name} from {tmpl}')"
b'                 elif expect is not None:'
b'@@ -757,59 +766,59 @@'
b' '
b'         # Side-effects'
b'         original_infodict = dict(self.outtmpl_info)'
b"-        test('foo.bar', 'foo.bar')"
b"-        original_infodict['epoch'] = self.outtmpl_info.get('epoch')"
b"-        self.assertTrue(isinstance(original_infodict['epoch'], int))"
b"-        test('%(epoch)d', int_or_none)"
b"+        test(u'foo.bar', u'foo.bar')"
b"+        original_infodict[u'epoch'] = self.outtmpl_info.get(u'epoch')"
b"+        self.assertTrue(isinstance(original_infodict[u'epoch'], int))"
b"+        test(u'%(epoch)d', int_or_none)"
b'         self.assertEqual(original_infodict, self.outtmpl_info)'
b' '
b'         # Auto-generated fields'
b"-        test('%(id)s.%(ext)s', '1234.mp4')"
b"-        test('%(duration_string)s', ('27:46:40', '27-46-40'))"
b"-        test('%(resolution)s', '1080p')"
b"-        test('%(playlist_index|)s', '001')"
b"-        test('%(playlist_index&{}!)s', '1!')"
b"-        test('%(playlist_autonumber)s', '02')"
b"-        test('%(autonumber)s', '00001')"
b"-        test('%(autonumber+2)03d', '005', autonumber_start=3)"
b"-        test('%(autonumber)s', '001', autonumber_size=3)"
b"+        test(u'%(id)s.%(ext)s', u'1234.mp4')"
b"+        test(u'%(duration_string)s', (u'27:46:40', u'27-46-40'))"
b"+        test(u'%(resolution)s', u'1080p')"
b"+        test(u'%(playlist_index|)s', u'001')"
b"+        test(u'%(playlist_index&{}!)s', u'1!')"
b"+        test(u'%(playlist_autonumber)s', u'02')"
b"+        test(u'%(autonumber)s', u'00001')"
b"+        test(u'%(autonumber+2)03d', u'005', autonumber_start=3)"
b"+        test(u'%(autonumber)s', u'001', autonumber_size=3)"
b' '
b'         # Escaping %'
b"-        test('%', '%')"
b"-        test('%%', '%')"
b"-        test('%%%%', '%%')"
b"-        test('%s', '%s')"
b"-        test('%%%s', '%%s')"
b"-        test('%d', '%d')"
b"-        test('%abc%', '%abc%')"
b"-        test('%%(width)06d.%(ext)s', '%(width)06d.mp4')"
b"-        test('%%%(height)s', '%1080')"
b"-        test('%(width)06d.%(ext)s', 'NA.mp4')"
b"-        test('%(width)06d.%%(ext)s', 'NA.%(ext)s')"
b"-        test('%%(width)06d.%(ext)s', '%(width)06d.mp4')"
b"+        test(u'%', u'%')"
b"+        test(u'%%', u'%')"
b"+        test(u'%%%%', u'%%')"
b"+        test(u'%s', u'%s')"
b"+        test(u'%%%s', u'%%s')"
b"+        test(u'%d', u'%d')"
b"+        test(u'%abc%', u'%abc%')"
b"+        test(u'%%(width)06d.%(ext)s', u'%(width)06d.mp4')"
b"+        test(u'%%%(height)s', u'%1080')"
b"+        test(u'%(width)06d.%(ext)s', u'NA.mp4')"
b"+        test(u'%(width)06d.%%(ext)s', u'NA.%(ext)s')"
b"+        test(u'%%(width)06d.%(ext)s', u'%(width)06d.mp4')"
b' '
b'         # Sanitization options'
b"-        test('%(title3)s', (None, 'foo\xe2\xa7\xb8bar\xe2\xa7\xb9test'))"
b"-        test('%(title5)s', (None, 'aei_A'), restrictfilenames=True)"
b"-        test('%(title3)s', (None, 'foo_bar_test'), windowsfilenames=False, restrictfilenames=True)"
b"-        if sys.platform != 'win32':"
b"-            test('%(title3)s', (None, 'foo\xe2\xa7\xb8bar\\\\test'), windowsfilenames=False)"
b"+        test(u'%(title3)s', (None, u'foo\xe2\xa7\xb8bar\xe2\xa7\xb9test'))"
b"+        test(u'%(title5)s', (None, u'aei_A'), restrictfilenames=True)"
b"+        test(u'%(title3)s', (None, u'foo_bar_test'), windowsfilenames=False, restrictfilenames=True)"
b"+        if sys.platform != u'win32':"
b"+            test(u'%(title3)s', (None, u'foo\xe2\xa7\xb8bar\\\\test'), windowsfilenames=False)"
b' '
b'         # ID sanitization'
b"-        test('%(id)s', '_abcd', info={'id': '_abcd'})"
b"-        test('%(some_id)s', '_abcd', info={'some_id': '_abcd'})"
b"-        test('%(formats.0.id)s', '_abcd', info={'formats': [{'id': '_abcd'}]})"
b"-        test('%(id)s', '-abcd', info={'id': '-abcd'})"
b"-        test('%(id)s', '.abcd', info={'id': '.abcd'})"
b"-        test('%(id)s', 'ab__cd', info={'id': 'ab__cd'})"
b"-        test('%(id)s', ('ab:cd', 'ab\xef\xbc\x9acd'), info={'id': 'ab:cd'})"
b"-        test('%(id.0)s', '-', info={'id': '--'})"
b"+        test(u'%(id)s', u'_abcd', info={u'id': u'_abcd'})"
b"+        test(u'%(some_id)s', u'_abcd', info={u'some_id': u'_abcd'})"
b"+        test(u'%(formats.0.id)s', u'_abcd', info={u'formats': [{u'id': u'_abcd'}]})"
b"+        test(u'%(id)s', u'-abcd', info={u'id': u'-abcd'})"
b"+        test(u'%(id)s', u'.abcd', info={u'id': u'.abcd'})"
b"+        test(u'%(id)s', u'ab__cd', info={u'id': u'ab__cd'})"
b"+        test(u'%(id)s', (u'ab:cd', u'ab\xef\xbc\x9acd'), info={u'id': u'ab:cd'})"
b"+        test(u'%(id.0)s', u'-', info={u'id': u'--'})"
b' '
b'         # Invalid templates'
b"-        self.assertTrue(isinstance(YoutubeDL.validate_outtmpl('%(title)'), ValueError))"
b"-        test('%(invalid@tmpl|def)s', 'none', outtmpl_na_placeholder='none')"
b"-        test('%(..)s', 'NA')"
b"-        test('%(formats.{id)s', 'NA')"
b"+        self.assertTrue(isinstance(YoutubeDL.validate_outtmpl(u'%(title)'), ValueError))"
b"+        test(u'%(invalid@tmpl|def)s', u'none', outtmpl_na_placeholder=u'none')"
b"+        test(u'%(..)s', u'NA')"
b"+        test(u'%(formats.{id)s', u'NA')"
b' '
b'         # Entire info_dict'
b'         def expect_same_infodict(out):'
b'@@ -818,280 +827,280 @@'
b'                 self.assertEqual(got_dict.get(info_field), expected, info_field)'
b'             return True'
b' '
b"-        test('%()j', (expect_same_infodict, None))"
b"+        test(u'%()j', (expect_same_infodict, None))"
b' '
b'         # NA placeholder'
b"-        NA_TEST_OUTTMPL = '%(uploader_date)s-%(width)d-%(x|def)s-%(id)s.%(ext)s'"
b"-        test(NA_TEST_OUTTMPL, 'NA-NA-def-1234.mp4')"
b"-        test(NA_TEST_OUTTMPL, 'none-none-def-1234.mp4', outtmpl_na_placeholder='none')"
b"-        test(NA_TEST_OUTTMPL, '--def-1234.mp4', outtmpl_na_placeholder='')"
b"-        test('%(non_existent.0)s', 'NA')"
b"+        NA_TEST_OUTTMPL = u'%(uploader_date)s-%(width)d-%(x|def)s-%(id)s.%(ext)s'"
b"+        test(NA_TEST_OUTTMPL, u'NA-NA-def-1234.mp4')"
b"+        test(NA_TEST_OUTTMPL, u'none-none-def-1234.mp4', outtmpl_na_placeholder=u'none')"
b"+        test(NA_TEST_OUTTMPL, u'--def-1234.mp4', outtmpl_na_placeholder=u'')"
b"+        test(u'%(non_existent.0)s', u'NA')"
b' '
b'         # String formatting'
b"-        FMT_TEST_OUTTMPL = '%%(height)%s.%%(ext)s'"
b"-        test(FMT_TEST_OUTTMPL % 's', '1080.mp4')"
b"-        test(FMT_TEST_OUTTMPL % 'd', '1080.mp4')"
b"-        test(FMT_TEST_OUTTMPL % '6d', '  1080.mp4')"
b"-        test(FMT_TEST_OUTTMPL % '-6d', '1080  .mp4')"
b"-        test(FMT_TEST_OUTTMPL % '06d', '001080.mp4')"
b"-        test(FMT_TEST_OUTTMPL % ' 06d', ' 01080.mp4')"
b"-        test(FMT_TEST_OUTTMPL % '   06d', ' 01080.mp4')"
b"-        test(FMT_TEST_OUTTMPL % '0 6d', ' 01080.mp4')"
b"-        test(FMT_TEST_OUTTMPL % '0   6d', ' 01080.mp4')"
b"-        test(FMT_TEST_OUTTMPL % '   0   6d', ' 01080.mp4')"
b"+        FMT_TEST_OUTTMPL = u'%%(height)%s.%%(ext)s'"
b"+        test(FMT_TEST_OUTTMPL % u's', u'1080.mp4')"
b"+        test(FMT_TEST_OUTTMPL % u'd', u'1080.mp4')"
b"+        test(FMT_TEST_OUTTMPL % u'6d', u'  1080.mp4')"
b"+        test(FMT_TEST_OUTTMPL % u'-6d', u'1080  .mp4')"
b"+        test(FMT_TEST_OUTTMPL % u'06d', u'001080.mp4')"
b"+        test(FMT_TEST_OUTTMPL % u' 06d', u' 01080.mp4')"
b"+        test(FMT_TEST_OUTTMPL % u'   06d', u' 01080.mp4')"
b"+        test(FMT_TEST_OUTTMPL % u'0 6d', u' 01080.mp4')"
b"+        test(FMT_TEST_OUTTMPL % u'0   6d', u' 01080.mp4')"
b"+        test(FMT_TEST_OUTTMPL % u'   0   6d', u' 01080.mp4')"
b' '
b'         # Type casting'
b"-        test('%(id)d', '1234')"
b"-        test('%(height)c', '1')"
b"-        test('%(ext)c', 'm')"
b'-        test(\'%(id)d %(id)r\', "1234 \'1234\'")'
b'-        test(\'%(id)r %(height)r\', "\'1234\' 1080")'
b'-        test(\'%(title5)a %(height)a\', (R"\'\\xe1\\xe9\\xed \\U0001d400\' 1080", None))'
b"-        test('%(ext)s-%(ext|def)d', 'mp4-def')"
b"-        test('%(width|0)04d', '0')"
b"-        test('a%(width|b)d', 'ab', outtmpl_na_placeholder='none')"
b'-'
b"-        FORMATS = self.outtmpl_info['formats']"
b"+        test(u'%(id)d', u'1234')"
b"+        test(u'%(height)c', u'1')"
b"+        test(u'%(ext)c', u'm')"
b'+        test(u\'%(id)d %(id)r\', u"1234 \'1234\'")'
b'+        test(u\'%(id)r %(height)r\', u"\'1234\' 1080")'
b'+        test(u\'%(title5)a %(height)a\', (uR"\'\\xe1\\xe9\\xed \\U0001d400\' 1080", None))'
b"+        test(u'%(ext)s-%(ext|def)d', u'mp4-def')"
b"+        test(u'%(width|0)04d', u'0')"
b"+        test(u'a%(width|b)d', u'ab', outtmpl_na_placeholder=u'none')"
b'+'
b"+        FORMATS = self.outtmpl_info[u'formats']"
b' '
b'         # Custom type casting'
b"-        test('%(formats.:.id)l', 'id 1, id 2, id 3')"
b"-        test('%(formats.:.id)#l', ('id 1\\nid 2\\nid 3', 'id 1 id 2 id 3'))"
b"-        test('%(ext)l', 'mp4')"
b"-        test('%(formats.:.id) 18l', '  id 1, id 2, id 3')"
b"-        test('%(formats)j', (json.dumps(FORMATS), None))"
b"-        test('%(formats)#j', ("
b"+        test(u'%(formats.:.id)l', u'id 1, id 2, id 3')"
b"+        test(u'%(formats.:.id)#l', (u'id 1\\nid 2\\nid 3', u'id 1 id 2 id 3'))"
b"+        test(u'%(ext)l', u'mp4')"
b"+        test(u'%(formats.:.id) 18l', u'  id 1, id 2, id 3')"
b"+        test(u'%(formats)j', (json.dumps(FORMATS), None))"
b"+        test(u'%(formats)#j', ("
b'             json.dumps(FORMATS, indent=4),'
b'-            json.dumps(FORMATS, indent=4).replace(\':\', \'\xef\xbc\x9a\').replace(\'"\', \'\xef\xbc\x82\').replace(\'\\n\', \' \'),'
b'+            json.dumps(FORMATS, indent=4).replace(u\':\', u\'\xef\xbc\x9a\').replace(u\'"\', u\'\xef\xbc\x82\').replace(u\'\\n\', u\' \'),'
b'         ))'
b"-        test('%(title5).3B', '\xc3\xa1')"
b"-        test('%(title5)U', '\xc3\xa1\xc3\xa9\xc3\xad \xf0\x9d\x90\x80')"
b"-        test('%(title5)#U', 'a\\u0301e\\u0301i\\u0301 \xf0\x9d\x90\x80')"
b"-        test('%(title5)+U', '\xc3\xa1\xc3\xa9\xc3\xad A')"
b"-        test('%(title5)+#U', 'a\\u0301e\\u0301i\\u0301 A')"
b"-        test('%(height)D', '1k')"
b"-        test('%(filesize)#D', '1Ki')"
b"-        test('%(height)5.2D', ' 1.08k')"
b"-        test('%(title4)#S', 'foo_bar_test')"
b"-        test('%(title4).10S', ('foo \xef\xbc\x82bar\xef\xbc\x82 ', 'foo \xef\xbc\x82bar\xef\xbc\x82' + ('#' if os.name == 'nt' else ' ')))"
b"-        if os.name == 'nt':"
b'-            test(\'%(title4)q\', (\'"foo ""bar"" test"\', None))'
b'-            test(\'%(formats.:.id)#q\', (\'"id 1" "id 2" "id 3"\', None))'
b'-            test(\'%(formats.0.id)#q\', (\'"id 1"\', None))'
b"+        test(u'%(title5).3B', u'\xc3\xa1')"
b"+        test(u'%(title5)U', u'\xc3\xa1\xc3\xa9\xc3\xad \xf0\x9d\x90\x80')"
b"+        test(u'%(title5)#U', u'a\\u0301e\\u0301i\\u0301 \xf0\x9d\x90\x80')"
b"+        test(u'%(title5)+U', u'\xc3\xa1\xc3\xa9\xc3\xad A')"
b"+        test(u'%(title5)+#U', u'a\\u0301e\\u0301i\\u0301 A')"
b"+        test(u'%(height)D', u'1k')"
b"+        test(u'%(filesize)#D', u'1Ki')"
b"+        test(u'%(height)5.2D', u' 1.08k')"
b"+        test(u'%(title4)#S', u'foo_bar_test')"
b"+        test(u'%(title4).10S', (u'foo \xef\xbc\x82bar\xef\xbc\x82 ', u'foo \xef\xbc\x82bar\xef\xbc\x82' + (u'#' if os.name == u'nt' else u' ')))"
b"+        if os.name == u'nt':"
b'+            test(u\'%(title4)q\', (u\'"foo ""bar"" test"\', None))'
b'+            test(u\'%(formats.:.id)#q\', (u\'"id 1" "id 2" "id 3"\', None))'
b'+            test(u\'%(formats.0.id)#q\', (u\'"id 1"\', None))'
b'         else:'
b'-            test(\'%(title4)q\', (\'\\\'foo "bar" test\\\'\', \'\\\'foo \xef\xbc\x82bar\xef\xbc\x82 test\\\'\'))'
b'-            test(\'%(formats.:.id)#q\', "\'id 1\' \'id 2\' \'id 3\'")'
b'-            test(\'%(formats.0.id)#q\', "\'id 1\'")'
b'+            test(u\'%(title4)q\', (u\'\\\'foo "bar" test\\\'\', u\'\\\'foo \xef\xbc\x82bar\xef\xbc\x82 test\\\'\'))'
b'+            test(u\'%(formats.:.id)#q\', u"\'id 1\' \'id 2\' \'id 3\'")'
b'+            test(u\'%(formats.0.id)#q\', u"\'id 1\'")'
b' '
b'         # Internal formatting'
b"-        test('%(timestamp-1000>%H-%M-%S)s', '11-43-20')"
b"-        test('%(title|%)s %(title|%%)s', '% %%')"
b"-        test('%(id+1-height+3)05d', '00158')"
b"-        test('%(width+100)05d', 'NA')"
b"-        test('%(filesize*8)d', '8192')"
b"-        test('%(formats.0) 15s', ('% 15s' % FORMATS[0], None))"
b"-        test('%(formats.0)r', (repr(FORMATS[0]), None))"
b"-        test('%(height.0)03d', '001')"
b"-        test('%(-height.0)04d', '-001')"
b"-        test('%(formats.-1.id)s', FORMATS[-1]['id'])"
b"-        test('%(formats.0.id.-1)d', FORMATS[0]['id'][-1])"
b"-        test('%(formats.3)s', 'NA')"
b"-        test('%(formats.:2:-1)r', repr(FORMATS[:2:-1]))"
b"-        test('%(formats.0.id.-1+id)f', '1235.000000')"
b"-        test('%(formats.0.id.-1+formats.1.id.-1)d', '3')"
b"-        out = json.dumps([{'id': f['id'], 'height.:2': str(f['height'])[:2]}"
b"-                          if 'height' in f else {'id': f['id']}"
b"+        test(u'%(timestamp-1000>%H-%M-%S)s', u'11-43-20')"
b"+        test(u'%(title|%)s %(title|%%)s', u'% %%')"
b"+        test(u'%(id+1-height+3)05d', u'00158')"
b"+        test(u'%(width+100)05d', u'NA')"
b"+        test(u'%(filesize*8)d', u'8192')"
b"+        test(u'%(formats.0) 15s', (u'% 15s' % FORMATS[0], None))"
b"+        test(u'%(formats.0)r', (repr(FORMATS[0]), None))"
b"+        test(u'%(height.0)03d', u'001')"
b"+        test(u'%(-height.0)04d', u'-001')"
b"+        test(u'%(formats.-1.id)s', FORMATS[-1][u'id'])"
b"+        test(u'%(formats.0.id.-1)d', FORMATS[0][u'id'][-1])"
b"+        test(u'%(formats.3)s', u'NA')"
b"+        test(u'%(formats.:2:-1)r', repr(FORMATS[:2:-1]))"
b"+        test(u'%(formats.0.id.-1+id)f', u'1235.000000')"
b"+        test(u'%(formats.0.id.-1+formats.1.id.-1)d', u'3')"
b"+        out = json.dumps([{u'id': f[u'id'], u'height.:2': unicode(f[u'height'])[:2]}"
b"+                          if u'height' in f else {u'id': f[u'id']}"
b'                           for f in FORMATS])'
b"-        test('%(formats.:.{id,height.:2})j', (out, None))"
b"-        test('%(formats.:.{id,height}.id)l', ', '.join(f['id'] for f in FORMATS))"
b'-        test(\'%(.{id,title})j\', (\'{"id": "1234"}\', \'{\xef\xbc\x82id\xef\xbc\x82\xef\xbc\x9a \xef\xbc\x821234\xef\xbc\x82}\'))'
b"+        test(u'%(formats.:.{id,height.:2})j', (out, None))"
b"+        test(u'%(formats.:.{id,height}.id)l', u', '.join(f[u'id'] for f in FORMATS))"
b'+        test(u\'%(.{id,title})j\', (u\'{"id": "1234"}\', u\'{\xef\xbc\x82id\xef\xbc\x82\xef\xbc\x9a \xef\xbc\x821234\xef\xbc\x82}\'))'
b' '
b'         # Alternates'
b"-        test('%(title,id)s', '1234')"
b"-        test('%(width-100,height+20|def)d', '1100')"
b"-        test('%(width-100,height+width|def)s', 'def')"
b"-        test('%(timestamp-x>%H\\\\,%M\\\\,%S,timestamp>%H\\\\,%M\\\\,%S)s', '12,00,00')"
b"+        test(u'%(title,id)s', u'1234')"
b"+        test(u'%(width-100,height+20|def)d', u'1100')"
b"+        test(u'%(width-100,height+width|def)s', u'def')"
b"+        test(u'%(timestamp-x>%H\\\\,%M\\\\,%S,timestamp>%H\\\\,%M\\\\,%S)s', u'12,00,00')"
b' '
b'         # Replacement'
b"-        test('%(id&foo)s.bar', 'foo.bar')"
b"-        test('%(title&foo)s.bar', 'NA.bar')"
b"-        test('%(title&foo|baz)s.bar', 'baz.bar')"
b"-        test('%(x,id&foo|baz)s.bar', 'foo.bar')"
b"-        test('%(x,title&foo|baz)s.bar', 'baz.bar')"
b"-        test('%(id&a\\nb|)s', ('a\\nb', 'a b'))"
b"-        test('%(id&hi {:>10} {}|)s', 'hi       1234 1234')"
b"-        test(R'%(id&{0} {}|)s', 'NA')"
b"-        test(R'%(id&{0.1}|)s', 'NA')"
b"-        test('%(height&{:,d})S', '1,080')"
b"+        test(u'%(id&foo)s.bar', u'foo.bar')"
b"+        test(u'%(title&foo)s.bar', u'NA.bar')"
b"+        test(u'%(title&foo|baz)s.bar', u'baz.bar')"
b"+        test(u'%(x,id&foo|baz)s.bar', u'foo.bar')"
b"+        test(u'%(x,title&foo|baz)s.bar', u'baz.bar')"
b"+        test(u'%(id&a\\nb|)s', (u'a\\nb', u'a b'))"
b"+        test(u'%(id&hi {:>10} {}|)s', u'hi       1234 1234')"
b"+        test(uR'%(id&{0} {}|)s', u'NA')"
b"+        test(uR'%(id&{0.1}|)s', u'NA')"
b"+        test(u'%(height&{:,d})S', u'1,080')"
b' '
b'         # Laziness'
b'         def gen():'
b'-            yield from range(5)'
b"-            raise self.assertTrue(False, 'LazyList should not be evaluated till here')"
b"-        test('%(key.4)s', '4', info={'key': LazyList(gen())})"
b'+            yield from xrange(5)'
b"+            raise self.assertTrue(False, u'LazyList should not be evaluated till here')"
b"+        test(u'%(key.4)s', u'4', info={u'key': LazyList(gen())})"
b' '
b'         # Empty filename'
b"-        test('%(foo|)s-%(bar|)s.%(ext)s', '-.mp4')"
b"+        test(u'%(foo|)s-%(bar|)s.%(ext)s', u'-.mp4')"
b"         # test('%(foo|)s.%(ext)s', ('.mp4', '_.mp4'))  # FIXME: ?"
b"         # test('%(foo|)s', ('', '_'))  # FIXME: ?"
b' '
b'         # Environment variable expansion for prepare_filename'
b"-        os.environ['__yt_dlp_var'] = 'expanded'"
b"-        envvar = '%__yt_dlp_var%' if os.name == 'nt' else '$__yt_dlp_var'"
b"-        test(envvar, (envvar, 'expanded'))"
b"-        if os.name == 'nt':"
b"-            test('%s%', ('%s%', '%s%'))"
b"-            os.environ['s'] = 'expanded'"
b"-            test('%s%', ('%s%', 'expanded'))  # %s% should be expanded before escaping %s"
b"-            os.environ['(test)s'] = 'expanded'"
b"-            test('%(test)s%', ('NA%', 'expanded'))  # Environment should take priority over template"
b"+        os.environ[u'__yt_dlp_var'] = u'expanded'"
b"+        envvar = u'%__yt_dlp_var%' if os.name == u'nt' else u'$__yt_dlp_var'"
b"+        test(envvar, (envvar, u'expanded'))"
b"+        if os.name == u'nt':"
b"+            test(u'%s%', (u'%s%', u'%s%'))"
b"+            os.environ[u's'] = u'expanded'"
b"+            test(u'%s%', (u'%s%', u'expanded'))  # %s% should be expanded before escaping %s"
b"+            os.environ[u'(test)s'] = u'expanded'"
b"+            test(u'%(test)s%', (u'NA%', u'expanded'))  # Environment should take priority over template"
b' '
b'         # Path expansion and escaping'
b"-        test('Hello %(title1)s', 'Hello $PATH')"
b"-        test('Hello %(title2)s', 'Hello %PATH%')"
b"-        test('%(title3)s', ('foo/bar\\\\test', 'foo\xe2\xa7\xb8bar\xe2\xa7\xb9test'))"
b"-        test('folder/%(title3)s', ('folder/foo/bar\\\\test', f'folder{os.path.sep}foo\xe2\xa7\xb8bar\xe2\xa7\xb9test'))"
b"+        test(u'Hello %(title1)s', u'Hello $PATH')"
b"+        test(u'Hello %(title2)s', u'Hello %PATH%')"
b"+        test(u'%(title3)s', (u'foo/bar\\\\test', u'foo\xe2\xa7\xb8bar\xe2\xa7\xb9test'))"
b"+        test(u'folder/%(title3)s', (u'folder/foo/bar\\\\test', f'folder{os.path.sep}foo\xe2\xa7\xb8bar\xe2\xa7\xb9test'))"
b' '
b'     def test_format_note(self):'
b'         ydl = YoutubeDL()'
b"-        self.assertEqual(ydl._format_note({}), '')"
b"+        self.assertEqual(ydl._format_note({}), u'')"
b'         assertRegexpMatches(self, ydl._format_note({'
b"-            'vbr': 10,"
b"-        }), r'^\\s*10k$')"
b"+            u'vbr': 10,"
b"+        }), ur'^\\s*10k$')"
b'         assertRegexpMatches(self, ydl._format_note({'
b"-            'fps': 30,"
b"-        }), r'^30fps$')"
b"+            u'fps': 30,"
b"+        }), ur'^30fps$')"
b' '
b'     def test_postprocessors(self):'
b"-        filename = 'post-processor-testfile.mp4'"
b"-        audiofile = filename + '.mp3'"
b"+        filename = u'post-processor-testfile.mp4'"
b"+        audiofile = filename + u'.mp3'"
b' '
b'         class SimplePP(PostProcessor):'
b'             def run(self, info):'
b"-                with open(audiofile, 'w') as f:"
b"-                    f.write('EXAMPLE')"
b"-                return [info['filepath']], info"
b"+                with open(audiofile, u'w') as f:"
b"+                    f.write(u'EXAMPLE')"
b"+                return [info[u'filepath']], info"
b' '
b'         def run_pp(params, pp):'
b"-            with open(filename, 'w') as f:"
b"-                f.write('EXAMPLE')"
b"+            with open(filename, u'w') as f:"
b"+                f.write(u'EXAMPLE')"
b'             ydl = YoutubeDL(params)'
b'             ydl.add_post_processor(pp())'
b"-            ydl.post_process(filename, {'filepath': filename})"
b'-'
b"-        run_pp({'keepvideo': True}, SimplePP)"
b"+            ydl.post_process(filename, {u'filepath': filename})"
b'+'
b"+        run_pp({u'keepvideo': True}, SimplePP)"
b"         self.assertTrue(os.path.exists(filename), f'{filename} doesn\\'t exist')"
b"         self.assertTrue(os.path.exists(audiofile), f'{audiofile} doesn\\'t exist')"
b'         os.unlink(filename)'
b'         os.unlink(audiofile)'
b' '
b"-        run_pp({'keepvideo': False}, SimplePP)"
b"+        run_pp({u'keepvideo': False}, SimplePP)"
b"         self.assertFalse(os.path.exists(filename), f'{filename} exists')"
b"         self.assertTrue(os.path.exists(audiofile), f'{audiofile} doesn\\'t exist')"
b'         os.unlink(audiofile)'
b' '
b'         class ModifierPP(PostProcessor):'
b'             def run(self, info):'
b"-                with open(info['filepath'], 'w') as f:"
b"-                    f.write('MODIFIED')"
b"+                with open(info[u'filepath'], u'w') as f:"
b"+                    f.write(u'MODIFIED')"
b'                 return [], info'
b' '
b"-        run_pp({'keepvideo': False}, ModifierPP)"
b"+        run_pp({u'keepvideo': False}, ModifierPP)"
b"         self.assertTrue(os.path.exists(filename), f'{filename} doesn\\'t exist')"
b'         os.unlink(filename)'
b' '
b'     def test_match_filter(self):'
b'         first = {'
b"-            'id': '1',"
b"-            'url': TEST_URL,"
b"-            'title': 'one',"
b"-            'extractor': 'TEST',"
b"-            'duration': 30,"
b"-            'filesize': 10 * 1024,"
b"-            'playlist_id': '42',"
b"-            'uploader': '\xe8\xae\x8a\xe6\x85\x8b\xe5\xa6\x8d\xe5\xad\x97\xe5\xb9\x95\xe7\x89\x88 \xe5\xa4\xaa\xe5\xa6\x8d \xd1\x82\xd0\xb5\xd1\x81\xd1\x82',"
b'-            \'creator\': "\xd1\x82\xd0\xb5\xd1\x81\xd1\x82 \' 123 \' \xd1\x82\xd0\xb5\xd1\x81\xd1\x82--",'
b"-            'webpage_url': 'http://example.com/watch?v=shenanigans',"
b"+            u'id': u'1',"
b"+            u'url': TEST_URL,"
b"+            u'title': u'one',"
b"+            u'extractor': u'TEST',"
b"+            u'duration': 30,"
b"+            u'filesize': 10 * 1024,"
b"+            u'playlist_id': u'42',"
b"+            u'uploader': u'\xe8\xae\x8a\xe6\x85\x8b\xe5\xa6\x8d\xe5\xad\x97\xe5\xb9\x95\xe7\x89\x88 \xe5\xa4\xaa\xe5\xa6\x8d \xd1\x82\xd0\xb5\xd1\x81\xd1\x82',"
b'+            u\'creator\': u"\xd1\x82\xd0\xb5\xd1\x81\xd1\x82 \' 123 \' \xd1\x82\xd0\xb5\xd1\x81\xd1\x82--",'
b"+            u'webpage_url': u'http://example.com/watch?v=shenanigans',"
b'         }'
b'         second = {'
b"-            'id': '2',"
b"-            'url': TEST_URL,"
b"-            'title': 'two',"
b"-            'extractor': 'TEST',"
b"-            'duration': 10,"
b"-            'description': 'foo',"
b"-            'filesize': 5 * 1024,"
b"-            'playlist_id': '43',"
b"-            'uploader': '\xd1\x82\xd0\xb5\xd1\x81\xd1\x82 123',"
b"-            'webpage_url': 'http://example.com/watch?v=SHENANIGANS',"
b"+            u'id': u'2',"
b"+            u'url': TEST_URL,"
b"+            u'title': u'two',"
b"+            u'extractor': u'TEST',"
b"+            u'duration': 10,"
b"+            u'description': u'foo',"
b"+            u'filesize': 5 * 1024,"
b"+            u'playlist_id': u'43',"
b"+            u'uploader': u'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82 123',"
b"+            u'webpage_url': u'http://example.com/watch?v=SHENANIGANS',"
b'         }'
b'         videos = [first, second]'
b' '
b'         def get_videos(filter_=None):'
b"-            ydl = YDL({'match_filter': filter_, 'simulate': True})"
b"+            ydl = YDL({u'match_filter': filter_, u'simulate': True})"
b'             for v in videos:'
b'                 ydl.process_ie_result(v.copy(), download=True)'
b"-            return [v['id'] for v in ydl.downloaded_info_dicts]"
b"+            return [v[u'id'] for v in ydl.downloaded_info_dicts]"
b' '
b'         res = get_videos()'
b"-        self.assertEqual(res, ['1', '2'])"
b"+        self.assertEqual(res, [u'1', u'2'])"
b' '
b'         def f(v, incomplete):'
b"-            if v['id'] == '1':"
b"+            if v[u'id'] == u'1':"
b'                 return None'
b'             else:'
b"-                return 'Video id is not 1'"
b"+                return u'Video id is not 1'"
b'         res = get_videos(f)'
b"-        self.assertEqual(res, ['1'])"
b'-'
b"-        f = match_filter_func('duration < 30')"
b"+        self.assertEqual(res, [u'1'])"
b'+'
b"+        f = match_filter_func(u'duration < 30')"
b'         res = get_videos(f)'
b"-        self.assertEqual(res, ['2'])"
b'-'
b"-        f = match_filter_func('description = foo')"
b"+        self.assertEqual(res, [u'2'])"
b'+'
b"+        f = match_filter_func(u'description = foo')"
b'         res = get_videos(f)'
b"-        self.assertEqual(res, ['2'])"
b'-'
b"-        f = match_filter_func('description =? foo')"
b"+        self.assertEqual(res, [u'2'])"
b'+'
b"+        f = match_filter_func(u'description =? foo')"
b'         res = get_videos(f)'
b"-        self.assertEqual(res, ['1', '2'])"
b'-'
b"-        f = match_filter_func('filesize > 5KiB')"
b"+        self.assertEqual(res, [u'1', u'2'])"
b'+'
b"+        f = match_filter_func(u'filesize > 5KiB')"
b'         res = get_videos(f)'
b"-        self.assertEqual(res, ['1'])"
b'-'
b"-        f = match_filter_func('playlist_id = 42')"
b"+        self.assertEqual(res, [u'1'])"
b'+'
b"+        f = match_filter_func(u'playlist_id = 42')"
b'         res = get_videos(f)'
b"-        self.assertEqual(res, ['1'])"
b'-'
b'-        f = match_filter_func(\'uploader = "\xe8\xae\x8a\xe6\x85\x8b\xe5\xa6\x8d\xe5\xad\x97\xe5\xb9\x95\xe7\x89\x88 \xe5\xa4\xaa\xe5\xa6\x8d \xd1\x82\xd0\xb5\xd1\x81\xd1\x82"\')'
b"+        self.assertEqual(res, [u'1'])"
b'+'
b'+        f = match_filter_func(u\'uploader = "\xe8\xae\x8a\xe6\x85\x8b\xe5\xa6\x8d\xe5\xad\x97\xe5\xb9\x95\xe7\x89\x88 \xe5\xa4\xaa\xe5\xa6\x8d \xd1\x82\xd0\xb5\xd1\x81\xd1\x82"\')'
b'         res = get_videos(f)'
b"-        self.assertEqual(res, ['1'])"
b'-'
b'-        f = match_filter_func(\'uploader != "\xe8\xae\x8a\xe6\x85\x8b\xe5\xa6\x8d\xe5\xad\x97\xe5\xb9\x95\xe7\x89\x88 \xe5\xa4\xaa\xe5\xa6\x8d \xd1\x82\xd0\xb5\xd1\x81\xd1\x82"\')'
b"+        self.assertEqual(res, [u'1'])"
b'+'
b'+        f = match_filter_func(u\'uploader != "\xe8\xae\x8a\xe6\x85\x8b\xe5\xa6\x8d\xe5\xad\x97\xe5\xb9\x95\xe7\x89\x88 \xe5\xa4\xaa\xe5\xa6\x8d \xd1\x82\xd0\xb5\xd1\x81\xd1\x82"\')'
b'         res = get_videos(f)'
b"-        self.assertEqual(res, ['2'])"
b'-'
b'-        f = match_filter_func(\'creator = "\xd1\x82\xd0\xb5\xd1\x81\xd1\x82 \\\' 123 \\\' \xd1\x82\xd0\xb5\xd1\x81\xd1\x82--"\')'
b"+        self.assertEqual(res, [u'2'])"
b'+'
b'+        f = match_filter_func(u\'creator = "\xd1\x82\xd0\xb5\xd1\x81\xd1\x82 \\\' 123 \\\' \xd1\x82\xd0\xb5\xd1\x81\xd1\x82--"\')'
b'         res = get_videos(f)'
b"-        self.assertEqual(res, ['1'])"
b'-'
b'-        f = match_filter_func("creator = \'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82 \\\\\' 123 \\\\\' \xd1\x82\xd0\xb5\xd1\x81\xd1\x82--\'")'
b"+        self.assertEqual(res, [u'1'])"
b'+'
b'+        f = match_filter_func(u"creator = \'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82 \\\\\' 123 \\\\\' \xd1\x82\xd0\xb5\xd1\x81\xd1\x82--\'")'
b'         res = get_videos(f)'
b"-        self.assertEqual(res, ['1'])"
b'-'
b'-        f = match_filter_func(r"creator = \'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82 \\\' 123 \\\' \xd1\x82\xd0\xb5\xd1\x81\xd1\x82--\' & duration > 30")'
b"+        self.assertEqual(res, [u'1'])"
b'+'
b'+        f = match_filter_func(ur"creator = \'\xd1\x82\xd0\xb5\xd1\x81\xd1\x82 \\\' 123 \\\' \xd1\x82\xd0\xb5\xd1\x81\xd1\x82--\' & duration > 30")'
b'         res = get_videos(f)'
b'         self.assertEqual(res, [])'
b' '
b'     def test_playlist_items_selection(self):'
b'-        INDICES, PAGE_SIZE = list(range(1, 11)), 3'
b'+        INDICES, PAGE_SIZE = xrange(1, 11), 3'
b' '
b'         def entry(i, evaluated):'
b'             evaluated.append(i)'
b'             return {'
b"-                'id': str(i),"
b"-                'title': str(i),"
b"-                'url': TEST_URL,"
b"+                u'id': unicode(i),"
b"+                u'title': unicode(i),"
b"+                u'url': TEST_URL,"
b'             }'
b' '
b'         def pagedlist_entries(evaluated):'
b'@@ -1117,12 +1126,12 @@'
b'         def get_downloaded_info_dicts(params, entries):'
b'             ydl = YDL(params)'
b'             ydl.process_ie_result({'
b"-                '_type': 'playlist',"
b"-                'id': 'test',"
b"-                'extractor': 'test:playlist',"
b"-                'extractor_key': 'test:playlist',"
b"-                'webpage_url': 'http://example.com',"
b"-                'entries': entries,"
b"+                u'_type': u'playlist',"
b"+                u'id': u'test',"
b"+                u'extractor': u'test:playlist',"
b"+                u'extractor_key': u'test:playlist',"
b"+                u'webpage_url': u'http://example.com',"
b"+                u'entries': entries,"
b'             })'
b'             return ydl.downloaded_info_dicts'
b' '
b'@@ -1138,152 +1147,152 @@'
b'                                          PAGE_SIZE * page_num(max(expected_ids))]'
b' '
b'             for name, func, expected_eval in ('
b"-                ('list', list_entries, INDICES),"
b"-                ('Generator', generator_entries, generator_eval),"
b"+                (u'list', list_entries, INDICES),"
b"+                (u'Generator', generator_entries, generator_eval),"
b"                 # ('LazyList', lazylist_entries, generator_eval),  # Generator and LazyList follow the exact same code path"
b"-                ('PagedList', pagedlist_entries, pagedlist_eval),"
b"+                (u'PagedList', pagedlist_entries, pagedlist_eval),"
b'             ):'
b'                 evaluated = []'
b'                 entries = func(evaluated)'
b"-                results = [(v['playlist_autonumber'] - 1, (int(v['id']), v['playlist_index']))"
b"+                results = [(v[u'playlist_autonumber'] - 1, (int(v[u'id']), v[u'playlist_index']))"
b'                            for v in get_downloaded_info_dicts(params, entries)]'
b"-                self.assertEqual(results, list(enumerate(zip(expected_ids, expected_ids))), f'Entries of {name} for {params}')"
b"+                self.assertEqual(results, list(enumerate(izip(expected_ids, expected_ids))), f'Entries of {name} for {params}')"
b"                 self.assertEqual(sorted(evaluated), expected_eval, f'Evaluation of {name} for {params}')"
b' '
b'         test_selection({}, INDICES)'
b"-        test_selection({'playlistend': 20}, INDICES, True)"
b"-        test_selection({'playlistend': 2}, INDICES[:2])"
b"-        test_selection({'playliststart': 11}, [], True)"
b"-        test_selection({'playliststart': 2}, INDICES[1:])"
b"-        test_selection({'playlist_items': '2-4'}, INDICES[1:4])"
b"-        test_selection({'playlist_items': '2,4'}, [2, 4])"
b"-        test_selection({'playlist_items': '20'}, [], True)"
b"-        test_selection({'playlist_items': '0'}, [])"
b"+        test_selection({u'playlistend': 20}, INDICES, True)"
b"+        test_selection({u'playlistend': 2}, INDICES[:2])"
b"+        test_selection({u'playliststart': 11}, [], True)"
b"+        test_selection({u'playliststart': 2}, INDICES[1:])"
b"+        test_selection({u'playlist_items': u'2-4'}, INDICES[1:4])"
b"+        test_selection({u'playlist_items': u'2,4'}, [2, 4])"
b"+        test_selection({u'playlist_items': u'20'}, [], True)"
b"+        test_selection({u'playlist_items': u'0'}, [])"
b' '
b'         # Tests for https://github.com/ytdl-org/youtube-dl/issues/10591'
b"-        test_selection({'playlist_items': '2-4,3-4,3'}, [2, 3, 4])"
b"-        test_selection({'playlist_items': '4,2'}, [4, 2])"
b"+        test_selection({u'playlist_items': u'2-4,3-4,3'}, [2, 3, 4])"
b"+        test_selection({u'playlist_items': u'4,2'}, [4, 2])"
b' '
b'         # Tests for https://github.com/yt-dlp/yt-dlp/issues/720'
b'         # https://github.com/yt-dlp/yt-dlp/issues/302'
b"-        test_selection({'playlistreverse': True}, INDICES[::-1])"
b"-        test_selection({'playliststart': 2, 'playlistreverse': True}, INDICES[:0:-1])"
b"-        test_selection({'playlist_items': '2,4', 'playlistreverse': True}, [4, 2])"
b"-        test_selection({'playlist_items': '4,2'}, [4, 2])"
b"+        test_selection({u'playlistreverse': True}, INDICES[::-1])"
b"+        test_selection({u'playliststart': 2, u'playlistreverse': True}, INDICES[:0:-1])"
b"+        test_selection({u'playlist_items': u'2,4', u'playlistreverse': True}, [4, 2])"
b"+        test_selection({u'playlist_items': u'4,2'}, [4, 2])"
b' '
b'         # Tests for --playlist-items start:end:step'
b"-        test_selection({'playlist_items': ':'}, INDICES, True)"
b"-        test_selection({'playlist_items': '::1'}, INDICES, True)"
b"-        test_selection({'playlist_items': '::-1'}, INDICES[::-1], True)"
b"-        test_selection({'playlist_items': ':6'}, INDICES[:6])"
b"-        test_selection({'playlist_items': ':-6'}, INDICES[:-5], True)"
b"-        test_selection({'playlist_items': '-1:6:-2'}, INDICES[:4:-2], True)"
b"-        test_selection({'playlist_items': '9:-6:-2'}, INDICES[8:3:-2], True)"
b'-'
b"-        test_selection({'playlist_items': '1:inf:2'}, INDICES[::2], True)"
b"-        test_selection({'playlist_items': '-2:inf'}, INDICES[-2:], True)"
b"-        test_selection({'playlist_items': ':inf:-1'}, [], True)"
b"-        test_selection({'playlist_items': '0-2:2'}, [2])"
b"-        test_selection({'playlist_items': '1-:2'}, INDICES[::2], True)"
b"-        test_selection({'playlist_items': '0--2:2'}, INDICES[1:-1:2], True)"
b'-'
b"-        test_selection({'playlist_items': '10::3'}, [10], True)"
b"-        test_selection({'playlist_items': '-1::3'}, [10], True)"
b"-        test_selection({'playlist_items': '11::3'}, [], True)"
b"-        test_selection({'playlist_items': '-15::2'}, INDICES[1::2], True)"
b"-        test_selection({'playlist_items': '-15::15'}, [], True)"
b"+        test_selection({u'playlist_items': u':'}, INDICES, True)"
b"+        test_selection({u'playlist_items': u'::1'}, INDICES, True)"
b"+        test_selection({u'playlist_items': u'::-1'}, INDICES[::-1], True)"
b"+        test_selection({u'playlist_items': u':6'}, INDICES[:6])"
b"+        test_selection({u'playlist_items': u':-6'}, INDICES[:-5], True)"
b"+        test_selection({u'playlist_items': u'-1:6:-2'}, INDICES[:4:-2], True)"
b"+        test_selection({u'playlist_items': u'9:-6:-2'}, INDICES[8:3:-2], True)"
b'+'
b"+        test_selection({u'playlist_items': u'1:inf:2'}, INDICES[::2], True)"
b"+        test_selection({u'playlist_items': u'-2:inf'}, INDICES[-2:], True)"
b"+        test_selection({u'playlist_items': u':inf:-1'}, [], True)"
b"+        test_selection({u'playlist_items': u'0-2:2'}, [2])"
b"+        test_selection({u'playlist_items': u'1-:2'}, INDICES[::2], True)"
b"+        test_selection({u'playlist_items': u'0--2:2'}, INDICES[1:-1:2], True)"
b'+'
b"+        test_selection({u'playlist_items': u'10::3'}, [10], True)"
b"+        test_selection({u'playlist_items': u'-1::3'}, [10], True)"
b"+        test_selection({u'playlist_items': u'11::3'}, [], True)"
b"+        test_selection({u'playlist_items': u'-15::2'}, INDICES[1::2], True)"
b"+        test_selection({u'playlist_items': u'-15::15'}, [], True)"
b' '
b'     def test_do_not_override_ie_key_in_url_transparent(self):'
b'         ydl = YDL()'
b' '
b'         class Foo1IE(InfoExtractor):'
b"-            _VALID_URL = r'foo1:'"
b"+            _VALID_URL = ur'foo1:'"
b' '
b'             def _real_extract(self, url):'
b'                 return {'
b"-                    '_type': 'url_transparent',"
b"-                    'url': 'foo2:',"
b"-                    'ie_key': 'Foo2',"
b"-                    'title': 'foo1 title',"
b"-                    'id': 'foo1_id',"
b"+                    u'_type': u'url_transparent',"
b"+                    u'url': u'foo2:',"
b"+                    u'ie_key': u'Foo2',"
b"+                    u'title': u'foo1 title',"
b"+                    u'id': u'foo1_id',"
b'                 }'
b' '
b'         class Foo2IE(InfoExtractor):'
b"-            _VALID_URL = r'foo2:'"
b"+            _VALID_URL = ur'foo2:'"
b' '
b'             def _real_extract(self, url):'
b'                 return {'
b"-                    '_type': 'url',"
b"-                    'url': 'foo3:',"
b"-                    'ie_key': 'Foo3',"
b"+                    u'_type': u'url',"
b"+                    u'url': u'foo3:',"
b"+                    u'ie_key': u'Foo3',"
b'                 }'
b' '
b'         class Foo3IE(InfoExtractor):'
b"-            _VALID_URL = r'foo3:'"
b"+            _VALID_URL = ur'foo3:'"
b' '
b'             def _real_extract(self, url):'
b"-                return _make_result([{'url': TEST_URL}], title='foo3 title')"
b"+                return _make_result([{u'url': TEST_URL}], title=u'foo3 title')"
b' '
b'         ydl.add_info_extractor(Foo1IE(ydl))'
b'         ydl.add_info_extractor(Foo2IE(ydl))'
b'         ydl.add_info_extractor(Foo3IE(ydl))'
b"-        ydl.extract_info('foo1:')"
b'-        downloaded = ydl.downloaded_info_dicts[0]'
b"-        self.assertEqual(downloaded['url'], TEST_URL)"
b"-        self.assertEqual(downloaded['title'], 'foo1 title')"
b"-        self.assertEqual(downloaded['id'], 'testid')"
b"-        self.assertEqual(downloaded['extractor'], 'testex')"
b"-        self.assertEqual(downloaded['extractor_key'], 'TestEx')"
b"+        ydl.extract_info(u'foo1:')"
b'+        downloaded = ydl.downloaded_info_dicts[0]'
b"+        self.assertEqual(downloaded[u'url'], TEST_URL)"
b"+        self.assertEqual(downloaded[u'title'], u'foo1 title')"
b"+        self.assertEqual(downloaded[u'id'], u'testid')"
b"+        self.assertEqual(downloaded[u'extractor'], u'testex')"
b"+        self.assertEqual(downloaded[u'extractor_key'], u'TestEx')"
b' '
b'     # Test case for https://github.com/ytdl-org/youtube-dl/issues/27064'
b'     def test_ignoreerrors_for_playlist_with_url_transparent_iterable_entries(self):'
b' '
b'         class _YDL(YDL):'
b'             def __init__(self, *args, **kwargs):'
b'-                super().__init__(*args, **kwargs)'
b'+                super(_YDL, self).__init__(*args, **kwargs)'
b' '
b'             def trouble(self, s, tb=None):'
b'                 pass'
b' '
b'         ydl = _YDL({'
b"-            'format': 'extra',"
b"-            'ignoreerrors': True,"
b"+            u'format': u'extra',"
b"+            u'ignoreerrors': True,"
b'         })'
b' '
b'         class VideoIE(InfoExtractor):'
b"-            _VALID_URL = r'video:(?P<id>\\d+)'"
b"+            _VALID_URL = ur'video:(?P<id>\\d+)'"
b' '
b'             def _real_extract(self, url):'
b'                 video_id = self._match_id(url)'
b'                 formats = [{'
b"-                    'format_id': 'default',"
b"-                    'url': 'url:',"
b"+                    u'format_id': u'default',"
b"+                    u'url': u'url:',"
b'                 }]'
b"-                if video_id == '0':"
b"-                    raise ExtractorError('foo')"
b"-                if video_id == '2':"
b"+                if video_id == u'0':"
b"+                    raise ExtractorError(u'foo')"
b"+                if video_id == u'2':"
b'                     formats.append({'
b"-                        'format_id': 'extra',"
b"-                        'url': TEST_URL,"
b"+                        u'format_id': u'extra',"
b"+                        u'url': TEST_URL,"
b'                     })'
b'                 return {'
b"-                    'id': video_id,"
b"-                    'title': f'Video {video_id}',"
b"-                    'formats': formats,"
b"+                    u'id': video_id,"
b"+                    u'title': f'Video {video_id}',"
b"+                    u'formats': formats,"
b'                 }'
b' '
b'         class PlaylistIE(InfoExtractor):'
b"-            _VALID_URL = r'playlist:'"
b"+            _VALID_URL = ur'playlist:'"
b' '
b'             def _entries(self):'
b'-                for n in range(3):'
b'-                    video_id = str(n)'
b'+                for n in xrange(3):'
b'+                    video_id = unicode(n)'
b'                     yield {'
b"-                        '_type': 'url_transparent',"
b"-                        'ie_key': VideoIE.ie_key(),"
b"-                        'id': video_id,"
b"-                        'url': f'video:{video_id}',"
b"-                        'title': f'Video Transparent {video_id}',"
b"+                        u'_type': u'url_transparent',"
b"+                        u'ie_key': VideoIE.ie_key(),"
b"+                        u'id': video_id,"
b"+                        u'url': f'video:{video_id}',"
b"+                        u'title': f'Video Transparent {video_id}',"
b'                     }'
b' '
b'             def _real_extract(self, url):'
b'@@ -1291,51 +1300,57 @@'
b' '
b'         ydl.add_info_extractor(VideoIE(ydl))'
b'         ydl.add_info_extractor(PlaylistIE(ydl))'
b"-        info = ydl.extract_info('playlist:')"
b"-        entries = info['entries']"
b"+        info = ydl.extract_info(u'playlist:')"
b"+        entries = info[u'entries']"
b'         self.assertEqual(len(entries), 3)'
b'         self.assertTrue(entries[0] is None)'
b'         self.assertTrue(entries[1] is None)'
b'         self.assertEqual(len(ydl.downloaded_info_dicts), 1)'
b'         downloaded = ydl.downloaded_info_dicts[0]'
b"-        entries[2].pop('requested_downloads', None)"
b"+        entries[2].pop(u'requested_downloads', None)"
b'         self.assertEqual(entries[2], downloaded)'
b"-        self.assertEqual(downloaded['url'], TEST_URL)"
b"-        self.assertEqual(downloaded['title'], 'Video Transparent 2')"
b"-        self.assertEqual(downloaded['id'], '2')"
b"-        self.assertEqual(downloaded['extractor'], 'Video')"
b"-        self.assertEqual(downloaded['extractor_key'], 'Video')"
b"+        self.assertEqual(downloaded[u'url'], TEST_URL)"
b"+        self.assertEqual(downloaded[u'title'], u'Video Transparent 2')"
b"+        self.assertEqual(downloaded[u'id'], u'2')"
b"+        self.assertEqual(downloaded[u'extractor'], u'Video')"
b"+        self.assertEqual(downloaded[u'extractor_key'], u'Video')"
b' '
b'     def test_header_cookies(self):'
b'-        from http.cookiejar import Cookie'
b'+        from cookielib import Cookie'
b' '
b'         ydl = FakeYDL()'
b'         ydl.report_warning = lambda *_, **__: None'
b' '
b"-        def cookie(name, value, version=None, domain='', path='', secure=False, expires=None):"
b"+        def cookie(name, value, version=None, domain=u'', path=u'', secure=False, expires=None):"
b'             return Cookie('
b'                 version or 0, name, value, None, False,'
b'                 domain, bool(domain), bool(domain), path, bool(path),'
b'                 secure, expires, False, None, None, rest={})'
b' '
b"-        _test_url = 'https://yt.dlp/test'"
b'-'
b'-        def test(encoded_cookies, cookies, *, headers=False, round_trip=None, error_re=None):'
b"+        _test_url = u'https://yt.dlp/test'"
b'+'
b'+        def test(encoded_cookies, cookies, **_3to2kwargs):'
b"+            if 'error_re' in _3to2kwargs: error_re = _3to2kwargs['error_re']; del _3to2kwargs['error_re']"
b'+            else: error_re = None'
b"+            if 'round_trip' in _3to2kwargs: round_trip = _3to2kwargs['round_trip']; del _3to2kwargs['round_trip']"
b'+            else: round_trip = None'
b"+            if 'headers' in _3to2kwargs: headers = _3to2kwargs['headers']; del _3to2kwargs['headers']"
b'+            else: headers = False'
b'             def _test():'
b'                 ydl.cookiejar.clear()'
b'                 ydl._load_cookies(encoded_cookies, autoscope=headers)'
b'                 if headers:'
b'                     ydl._apply_header_cookies(_test_url)'
b"-                data = {'url': _test_url}"
b"+                data = {u'url': _test_url}"
b'                 ydl._calc_headers(data)'
b'                 self.assertCountEqual('
b'-                    map(vars, ydl.cookiejar), map(vars, cookies),'
b"-                    'Extracted cookiejar.Cookie is not the same')"
b'+                    imap(vars, ydl.cookiejar), imap(vars, cookies),'
b"+                    u'Extracted cookiejar.Cookie is not the same')"
b'                 if not headers:'
b'                     self.assertEqual('
b"-                        data.get('cookies'), round_trip or encoded_cookies,"
b"-                        'Cookie is not the same as round trip')"
b"-                ydl.__dict__['_YoutubeDL__header_cookies'] = []"
b"+                        data.get(u'cookies'), round_trip or encoded_cookies,"
b"+                        u'Cookie is not the same as round trip')"
b"+                ydl.__dict__[u'_YoutubeDL__header_cookies'] = []"
b' '
b'             with self.subTest(msg=encoded_cookies):'
b'                 if not error_re:'
b'@@ -1344,90 +1359,90 @@'
b'                 with self.assertRaisesRegex(Exception, error_re):'
b'                     _test()'
b' '
b"-        test('test=value; Domain=.yt.dlp', [cookie('test', 'value', domain='.yt.dlp')])"
b"-        test('test=value', [cookie('test', 'value')], error_re=r'Unscoped cookies are not allowed')"
b"-        test('cookie1=value1; Domain=.yt.dlp; Path=/test; cookie2=value2; Domain=.yt.dlp; Path=/', ["
b"-            cookie('cookie1', 'value1', domain='.yt.dlp', path='/test'),"
b"-            cookie('cookie2', 'value2', domain='.yt.dlp', path='/')])"
b"-        test('test=value; Domain=.yt.dlp; Path=/test; Secure; Expires=9999999999', ["
b"-            cookie('test', 'value', domain='.yt.dlp', path='/test', secure=True, expires=9999999999)])"
b'-        test(\'test="value; "; path=/test; domain=.yt.dlp\', ['
b"-            cookie('test', 'value; ', domain='.yt.dlp', path='/test')],"
b'-            round_trip=\'test="value\\\\073 "; Domain=.yt.dlp; Path=/test\')'
b"-        test('name=; Domain=.yt.dlp', [cookie('name', '', domain='.yt.dlp')],"
b'-             round_trip=\'name=""; Domain=.yt.dlp\')'
b'-'
b"-        test('test=value', [cookie('test', 'value', domain='.yt.dlp')], headers=True)"
b"-        test('cookie1=value; Domain=.yt.dlp; cookie2=value', [], headers=True, error_re=r'Invalid syntax')"
b"+        test(u'test=value; Domain=.yt.dlp', [cookie(u'test', u'value', domain=u'.yt.dlp')])"
b"+        test(u'test=value', [cookie(u'test', u'value')], error_re=ur'Unscoped cookies are not allowed')"
b"+        test(u'cookie1=value1; Domain=.yt.dlp; Path=/test; cookie2=value2; Domain=.yt.dlp; Path=/', ["
b"+            cookie(u'cookie1', u'value1', domain=u'.yt.dlp', path=u'/test'),"
b"+            cookie(u'cookie2', u'value2', domain=u'.yt.dlp', path=u'/')])"
b"+        test(u'test=value; Domain=.yt.dlp; Path=/test; Secure; Expires=9999999999', ["
b"+            cookie(u'test', u'value', domain=u'.yt.dlp', path=u'/test', secure=True, expires=9999999999)])"
b'+        test(u\'test="value; "; path=/test; domain=.yt.dlp\', ['
b"+            cookie(u'test', u'value; ', domain=u'.yt.dlp', path=u'/test')],"
b'+            round_trip=u\'test="value\\\\073 "; Domain=.yt.dlp; Path=/test\')'
b"+        test(u'name=; Domain=.yt.dlp', [cookie(u'name', u'', domain=u'.yt.dlp')],"
b'+             round_trip=u\'name=""; Domain=.yt.dlp\')'
b'+'
b"+        test(u'test=value', [cookie(u'test', u'value', domain=u'.yt.dlp')], headers=True)"
b"+        test(u'cookie1=value; Domain=.yt.dlp; cookie2=value', [], headers=True, error_re=ur'Invalid syntax')"
b'         ydl.deprecated_feature = ydl.report_error'
b"-        test('test=value', [], headers=True, error_re=r'Passing cookies as a header is a potential security risk')"
b"+        test(u'test=value', [], headers=True, error_re=ur'Passing cookies as a header is a potential security risk')"
b' '
b'     def test_infojson_cookies(self):'
b"-        TEST_FILE = 'test_infojson_cookies.info.json'"
b"-        TEST_URL = 'https://example.com/example.mp4'"
b"-        COOKIES = 'a=b; Domain=.example.com; c=d; Domain=.example.com'"
b"-        COOKIE_HEADER = {'Cookie': 'a=b; c=d'}"
b"+        TEST_FILE = u'test_infojson_cookies.info.json'"
b"+        TEST_URL = u'https://example.com/example.mp4'"
b"+        COOKIES = u'a=b; Domain=.example.com; c=d; Domain=.example.com'"
b"+        COOKIE_HEADER = {u'Cookie': u'a=b; c=d'}"
b' '
b'         ydl = FakeYDL()'
b"-        ydl.process_info = lambda x: ydl._write_info_json('test', x, TEST_FILE)"
b"+        ydl.process_info = lambda x: ydl._write_info_json(u'test', x, TEST_FILE)"
b' '
b'         def make_info(info_header_cookies=False, fmts_header_cookies=False, cookies_field=False):'
b"-            fmt = {'url': TEST_URL}"
b"+            fmt = {u'url': TEST_URL}"
b'             if fmts_header_cookies:'
b"-                fmt['http_headers'] = COOKIE_HEADER"
b"+                fmt[u'http_headers'] = COOKIE_HEADER"
b'             if cookies_field:'
b"-                fmt['cookies'] = COOKIES"
b"+                fmt[u'cookies'] = COOKIES"
b'             return _make_result([fmt], http_headers=COOKIE_HEADER if info_header_cookies else None)'
b' '
b'         def test(initial_info, note):'
b'             result = {}'
b"-            result['processed'] = ydl.process_ie_result(initial_info)"
b"+            result[u'processed'] = ydl.process_ie_result(initial_info)"
b'             self.assertTrue(ydl.cookiejar.get_cookies_for_url(TEST_URL),'
b"                             msg=f'No cookies set in cookiejar after initial process when {note}')"
b'             ydl.cookiejar.clear()'
b'             with open(TEST_FILE) as infojson:'
b"-                result['loaded'] = ydl.sanitize_info(json.load(infojson), True)"
b"-            result['final'] = ydl.process_ie_result(result['loaded'].copy(), download=False)"
b"+                result[u'loaded'] = ydl.sanitize_info(json.load(infojson), True)"
b"+            result[u'final'] = ydl.process_ie_result(result[u'loaded'].copy(), download=False)"
b'             self.assertTrue(ydl.cookiejar.get_cookies_for_url(TEST_URL),'
b"                             msg=f'No cookies set in cookiejar after final process when {note}')"
b'             ydl.cookiejar.clear()'
b"-            for key in ('processed', 'loaded', 'final'):"
b"+            for key in (u'processed', u'loaded', u'final'):"
b'                 info = result[key]'
b'                 self.assertIsNone('
b"-                    traverse_obj(info, ((None, ('formats', 0)), 'http_headers', 'Cookie'), casesense=False, get_all=False),"
b"+                    traverse_obj(info, ((None, (u'formats', 0)), u'http_headers', u'Cookie'), casesense=False, get_all=False),"
b"                     msg=f'Cookie header not removed in {key} result when {note}')"
b'                 self.assertEqual('
b"-                    traverse_obj(info, ((None, ('formats', 0)), 'cookies'), get_all=False), COOKIES,"
b"+                    traverse_obj(info, ((None, (u'formats', 0)), u'cookies'), get_all=False), COOKIES,"
b"                     msg=f'No cookies field found in {key} result when {note}')"
b' '
b"-        test({'url': TEST_URL, 'http_headers': COOKIE_HEADER, 'id': '1', 'title': 'x'}, 'no formats field')"
b"-        test(make_info(info_header_cookies=True), 'info_dict header cokies')"
b"-        test(make_info(fmts_header_cookies=True), 'format header cookies')"
b"-        test(make_info(info_header_cookies=True, fmts_header_cookies=True), 'info_dict and format header cookies')"
b"-        test(make_info(info_header_cookies=True, fmts_header_cookies=True, cookies_field=True), 'all cookies fields')"
b"-        test(make_info(cookies_field=True), 'cookies format field')"
b"-        test({'url': TEST_URL, 'cookies': COOKIES, 'id': '1', 'title': 'x'}, 'info_dict cookies field only')"
b"+        test({u'url': TEST_URL, u'http_headers': COOKIE_HEADER, u'id': u'1', u'title': u'x'}, u'no formats field')"
b"+        test(make_info(info_header_cookies=True), u'info_dict header cokies')"
b"+        test(make_info(fmts_header_cookies=True), u'format header cookies')"
b"+        test(make_info(info_header_cookies=True, fmts_header_cookies=True), u'info_dict and format header cookies')"
b"+        test(make_info(info_header_cookies=True, fmts_header_cookies=True, cookies_field=True), u'all cookies fields')"
b"+        test(make_info(cookies_field=True), u'cookies format field')"
b"+        test({u'url': TEST_URL, u'cookies': COOKIES, u'id': u'1', u'title': u'x'}, u'info_dict cookies field only')"
b' '
b'         try_rm(TEST_FILE)'
b' '
b'     def test_add_headers_cookie(self):'
b'         def check_for_cookie_header(result):'
b"-            return traverse_obj(result, ((None, ('formats', 0)), 'http_headers', 'Cookie'), casesense=False, get_all=False)"
b'-'
b"-        ydl = FakeYDL({'http_headers': {'Cookie': 'a=b'}})"
b"-        ydl._apply_header_cookies(_make_result([])['webpage_url'])  # Scope to input webpage URL: .example.com"
b'-'
b"-        fmt = {'url': 'https://example.com/video.mp4'}"
b"+            return traverse_obj(result, ((None, (u'formats', 0)), u'http_headers', u'Cookie'), casesense=False, get_all=False)"
b'+'
b"+        ydl = FakeYDL({u'http_headers': {u'Cookie': u'a=b'}})"
b"+        ydl._apply_header_cookies(_make_result([])[u'webpage_url'])  # Scope to input webpage URL: .example.com"
b'+'
b"+        fmt = {u'url': u'https://example.com/video.mp4'}"
b'         result = ydl.process_ie_result(_make_result([fmt]), download=False)'
b"-        self.assertIsNone(check_for_cookie_header(result), msg='http_headers cookies in result info_dict')"
b"-        self.assertEqual(result.get('cookies'), 'a=b; Domain=.example.com', msg='No cookies were set in cookies field')"
b"-        self.assertIn('a=b', ydl.cookiejar.get_cookie_header(fmt['url']), msg='No cookies were set in cookiejar')"
b'-'
b"-        fmt = {'url': 'https://wrong.com/video.mp4'}"
b"+        self.assertIsNone(check_for_cookie_header(result), msg=u'http_headers cookies in result info_dict')"
b"+        self.assertEqual(result.get(u'cookies'), u'a=b; Domain=.example.com', msg=u'No cookies were set in cookies field')"
b"+        self.assertIn(u'a=b', ydl.cookiejar.get_cookie_header(fmt[u'url']), msg=u'No cookies were set in cookiejar')"
b'+'
b"+        fmt = {u'url': u'https://wrong.com/video.mp4'}"
b'         result = ydl.process_ie_result(_make_result([fmt]), download=False)'
b"-        self.assertIsNone(check_for_cookie_header(result), msg='http_headers cookies for wrong domain')"
b"-        self.assertFalse(result.get('cookies'), msg='Cookies set in cookies field for wrong domain')"
b"-        self.assertFalse(ydl.cookiejar.get_cookie_header(fmt['url']), msg='Cookies set in cookiejar for wrong domain')"
b"+        self.assertIsNone(check_for_cookie_header(result), msg=u'http_headers cookies for wrong domain')"
b"+        self.assertFalse(result.get(u'cookies'), msg=u'Cookies set in cookies field for wrong domain')"
b"+        self.assertFalse(ydl.cookiejar.get_cookie_header(fmt[u'url']), msg=u'Cookies set in cookiejar for wrong domain')"
b' '
b'     def test_load_plugins_compat(self):'
b"         # Should try to reload plugins if they haven't already been loaded"
b'@@ -1453,9 +1468,9 @@'
b'         ydl.add_close_hook(close_hook_two)'
b' '
b'         ydl.close()'
b"-        self.assertTrue(close_hook_called, 'Close hook was not called')"
b"-        self.assertTrue(close_hook_two_called, 'Close hook two was not called')"
b'-'
b'-'
b"-if __name__ == '__main__':"
b"+        self.assertTrue(close_hook_called, u'Close hook was not called')"
b"+        self.assertTrue(close_hook_two_called, u'Close hook two was not called')"
b'+'
b'+'
b"+if __name__ == u'__main__':"
b'     unittest.main()'
