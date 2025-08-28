b'--- ./test/test_youtube_misc.py\t(original)'
b'+++ ./test/test_youtube_misc.py\t(refactored)'
b'@@ -1,6 +1,7 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' import unittest'
b'@@ -14,13 +15,13 @@'
b' class TestYoutubeMisc(unittest.TestCase):'
b'     def test_youtube_extract(self):'
b'         assertExtractId = lambda url, video_id: self.assertEqual(YoutubeIE.extract_id(url), video_id)'
b"-        assertExtractId('http://www.youtube.com/watch?&v=BaW_jenozKc', 'BaW_jenozKc')"
b"-        assertExtractId('https://www.youtube.com/watch?&v=BaW_jenozKc', 'BaW_jenozKc')"
b"-        assertExtractId('https://www.youtube.com/watch?feature=player_embedded&v=BaW_jenozKc', 'BaW_jenozKc')"
b"-        assertExtractId('https://www.youtube.com/watch_popup?v=BaW_jenozKc', 'BaW_jenozKc')"
b"-        assertExtractId('http://www.youtube.com/watch?v=BaW_jenozKcsharePLED17F32AD9753930', 'BaW_jenozKc')"
b"-        assertExtractId('BaW_jenozKc', 'BaW_jenozKc')"
b"+        assertExtractId(u'http://www.youtube.com/watch?&v=BaW_jenozKc', u'BaW_jenozKc')"
b"+        assertExtractId(u'https://www.youtube.com/watch?&v=BaW_jenozKc', u'BaW_jenozKc')"
b"+        assertExtractId(u'https://www.youtube.com/watch?feature=player_embedded&v=BaW_jenozKc', u'BaW_jenozKc')"
b"+        assertExtractId(u'https://www.youtube.com/watch_popup?v=BaW_jenozKc', u'BaW_jenozKc')"
b"+        assertExtractId(u'http://www.youtube.com/watch?v=BaW_jenozKcsharePLED17F32AD9753930', u'BaW_jenozKc')"
b"+        assertExtractId(u'BaW_jenozKc', u'BaW_jenozKc')"
b' '
b' '
b"-if __name__ == '__main__':"
b"+if __name__ == u'__main__':"
b'     unittest.main()'
