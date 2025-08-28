b'--- ./test/test_youtube_lists.py\t(original)'
b'+++ ./test/test_youtube_lists.py\t(refactored)'
b'@@ -1,6 +1,8 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import with_statement'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' import unittest'
b'@@ -13,59 +15,60 @@'
b' from yt_dlp.utils import ExtractorError'
b' '
b' '
b'-@is_download_test'
b' class TestYoutubeLists(unittest.TestCase):'
b'     def assertIsPlaylist(self, info):'
b'-        """Make sure the info has \'_type\' set to \'playlist\'"""'
b"-        self.assertEqual(info['_type'], 'playlist')"
b'+        u"""Make sure the info has \'_type\' set to \'playlist\'"""'
b"+        self.assertEqual(info[u'_type'], u'playlist')"
b' '
b'     def test_youtube_playlist_noplaylist(self):'
b'         dl = FakeYDL()'
b"-        dl.params['noplaylist'] = True"
b"+        dl.params[u'noplaylist'] = True"
b'         ie = YoutubeTabIE(dl)'
b"-        result = ie.extract('https://www.youtube.com/watch?v=OmJ-4B-mS-Y&list=PLydZ2Hrp_gPRJViZjLFKaBMgCQOYEEkyp&index=2')"
b"-        self.assertEqual(result['_type'], 'url')"
b"-        self.assertEqual(result['ie_key'], YoutubeIE.ie_key())"
b"-        self.assertEqual(YoutubeIE.extract_id(result['url']), 'OmJ-4B-mS-Y')"
b"+        result = ie.extract(u'https://www.youtube.com/watch?v=OmJ-4B-mS-Y&list=PLydZ2Hrp_gPRJViZjLFKaBMgCQOYEEkyp&index=2')"
b"+        self.assertEqual(result[u'_type'], u'url')"
b"+        self.assertEqual(result[u'ie_key'], YoutubeIE.ie_key())"
b"+        self.assertEqual(YoutubeIE.extract_id(result[u'url']), u'OmJ-4B-mS-Y')"
b' '
b'     def test_youtube_mix(self):'
b'         dl = FakeYDL()'
b'         ie = YoutubeTabIE(dl)'
b"-        result = ie.extract('https://www.youtube.com/watch?v=tyITL_exICo&list=RDCLAK5uy_kLWIr9gv1XLlPbaDS965-Db4TrBoUTxQ8')"
b"-        entries = list(result['entries'])"
b"+        result = ie.extract(u'https://www.youtube.com/watch?v=tyITL_exICo&list=RDCLAK5uy_kLWIr9gv1XLlPbaDS965-Db4TrBoUTxQ8')"
b"+        entries = list(result[u'entries'])"
b'         self.assertTrue(len(entries) >= 50)'
b'         original_video = entries[0]'
b"-        self.assertEqual(original_video['id'], 'tyITL_exICo')"
b"+        self.assertEqual(original_video[u'id'], u'tyITL_exICo')"
b' '
b'     def test_youtube_flat_playlist_extraction(self):'
b'         dl = FakeYDL()'
b"-        dl.params['extract_flat'] = True"
b"+        dl.params[u'extract_flat'] = True"
b'         ie = YoutubeTabIE(dl)'
b"-        result = ie.extract('https://www.youtube.com/playlist?list=PL4lCao7KL_QFVb7Iudeipvc2BCavECqzc')"
b"+        result = ie.extract(u'https://www.youtube.com/playlist?list=PL4lCao7KL_QFVb7Iudeipvc2BCavECqzc')"
b'         self.assertIsPlaylist(result)'
b"-        entries = list(result['entries'])"
b"+        entries = list(result[u'entries'])"
b'         self.assertTrue(len(entries) == 1)'
b'         video = entries[0]'
b"-        self.assertEqual(video['_type'], 'url')"
b"-        self.assertEqual(video['ie_key'], 'Youtube')"
b"-        self.assertEqual(video['id'], 'BaW_jenozKc')"
b"-        self.assertEqual(video['url'], 'https://www.youtube.com/watch?v=BaW_jenozKc')"
b'-        self.assertEqual(video[\'title\'], \'youtube-dl test video "\\\'/\\\\\xc3\xa4\xe2\x86\xad\xf0\x9d\x95\x90\')'
b"-        self.assertEqual(video['duration'], 10)"
b"-        self.assertEqual(video['uploader'], 'Philipp Hagemeister')"
b"+        self.assertEqual(video[u'_type'], u'url')"
b"+        self.assertEqual(video[u'ie_key'], u'Youtube')"
b"+        self.assertEqual(video[u'id'], u'BaW_jenozKc')"
b"+        self.assertEqual(video[u'url'], u'https://www.youtube.com/watch?v=BaW_jenozKc')"
b'+        self.assertEqual(video[u\'title\'], u\'youtube-dl test video "\\\'/\\\\\xc3\xa4\xe2\x86\xad\xf0\x9d\x95\x90\')'
b"+        self.assertEqual(video[u'duration'], 10)"
b"+        self.assertEqual(video[u'uploader'], u'Philipp Hagemeister')"
b' '
b'     def test_youtube_channel_no_uploads(self):'
b'         dl = FakeYDL()'
b"-        dl.params['extract_flat'] = True"
b"+        dl.params[u'extract_flat'] = True"
b'         ie = YoutubeTabIE(dl)'
b'         # no uploads'
b"-        with self.assertRaisesRegex(ExtractorError, r'no uploads'):"
b"-            ie.extract('https://www.youtube.com/channel/UC2yXPzFejc422buOIzn_0CA')"
b"+        with self.assertRaisesRegex(ExtractorError, ur'no uploads'):"
b"+            ie.extract(u'https://www.youtube.com/channel/UC2yXPzFejc422buOIzn_0CA')"
b' '
b'         # no uploads and no UCID given'
b"-        with self.assertRaisesRegex(ExtractorError, r'no uploads'):"
b"-            ie.extract('https://www.youtube.com/news')"
b"+        with self.assertRaisesRegex(ExtractorError, ur'no uploads'):"
b"+            ie.extract(u'https://www.youtube.com/news')"
b' '
b' '
b"-if __name__ == '__main__':"
b'+TestYoutubeLists = is_download_test(TestYoutubeLists)'
b'+'
b"+if __name__ == u'__main__':"
b'     unittest.main()'
