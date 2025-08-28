b'--- ./test/test_YoutubeDLCookieJar.py\t(original)'
b'+++ ./test/test_YoutubeDLCookieJar.py\t(refactored)'
b'@@ -1,6 +1,7 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' import unittest'
b'@@ -16,51 +17,51 @@'
b' '
b' class TestYoutubeDLCookieJar(unittest.TestCase):'
b'     def test_keep_session_cookies(self):'
b"-        cookiejar = YoutubeDLCookieJar('./test/testdata/cookies/session_cookies.txt')"
b"+        cookiejar = YoutubeDLCookieJar(u'./test/testdata/cookies/session_cookies.txt')"
b'         cookiejar.load()'
b'         tf = tempfile.NamedTemporaryFile(delete=False)'
b'         try:'
b'             cookiejar.save(filename=tf.name)'
b'             temp = tf.read().decode()'
b'             self.assertTrue(re.search('
b"-                r'www\\.foobar\\.foobar\\s+FALSE\\s+/\\s+TRUE\\s+0\\s+YoutubeDLExpiresEmpty\\s+YoutubeDLExpiresEmptyValue', temp))"
b"+                ur'www\\.foobar\\.foobar\\s+FALSE\\s+/\\s+TRUE\\s+0\\s+YoutubeDLExpiresEmpty\\s+YoutubeDLExpiresEmptyValue', temp))"
b'             self.assertTrue(re.search('
b"-                r'www\\.foobar\\.foobar\\s+FALSE\\s+/\\s+TRUE\\s+0\\s+YoutubeDLExpires0\\s+YoutubeDLExpires0Value', temp))"
b"+                ur'www\\.foobar\\.foobar\\s+FALSE\\s+/\\s+TRUE\\s+0\\s+YoutubeDLExpires0\\s+YoutubeDLExpires0Value', temp))"
b'         finally:'
b'             tf.close()'
b'             os.remove(tf.name)'
b' '
b'     def test_strip_httponly_prefix(self):'
b"-        cookiejar = YoutubeDLCookieJar('./test/testdata/cookies/httponly_cookies.txt')"
b"+        cookiejar = YoutubeDLCookieJar(u'./test/testdata/cookies/httponly_cookies.txt')"
b'         cookiejar.load()'
b' '
b'         def assert_cookie_has_value(key):'
b"-            self.assertEqual(cookiejar._cookies['www.foobar.foobar']['/'][key].value, key + '_VALUE')"
b"+            self.assertEqual(cookiejar._cookies[u'www.foobar.foobar'][u'/'][key].value, key + u'_VALUE')"
b' '
b"-        assert_cookie_has_value('HTTPONLY_COOKIE')"
b"-        assert_cookie_has_value('JS_ACCESSIBLE_COOKIE')"
b"+        assert_cookie_has_value(u'HTTPONLY_COOKIE')"
b"+        assert_cookie_has_value(u'JS_ACCESSIBLE_COOKIE')"
b' '
b'     def test_malformed_cookies(self):'
b"-        cookiejar = YoutubeDLCookieJar('./test/testdata/cookies/malformed_cookies.txt')"
b"+        cookiejar = YoutubeDLCookieJar(u'./test/testdata/cookies/malformed_cookies.txt')"
b'         cookiejar.load()'
b'         # Cookies should be empty since all malformed cookie file entries'
b'         # will be ignored'
b'         self.assertFalse(cookiejar._cookies)'
b' '
b'     def test_get_cookie_header(self):'
b"-        cookiejar = YoutubeDLCookieJar('./test/testdata/cookies/httponly_cookies.txt')"
b"+        cookiejar = YoutubeDLCookieJar(u'./test/testdata/cookies/httponly_cookies.txt')"
b'         cookiejar.load()'
b"-        header = cookiejar.get_cookie_header('https://www.foobar.foobar')"
b"-        self.assertIn('HTTPONLY_COOKIE', header)"
b"+        header = cookiejar.get_cookie_header(u'https://www.foobar.foobar')"
b"+        self.assertIn(u'HTTPONLY_COOKIE', header)"
b' '
b'     def test_get_cookies_for_url(self):'
b"-        cookiejar = YoutubeDLCookieJar('./test/testdata/cookies/session_cookies.txt')"
b"+        cookiejar = YoutubeDLCookieJar(u'./test/testdata/cookies/session_cookies.txt')"
b'         cookiejar.load()'
b"-        cookies = cookiejar.get_cookies_for_url('https://www.foobar.foobar/')"
b"+        cookies = cookiejar.get_cookies_for_url(u'https://www.foobar.foobar/')"
b'         self.assertEqual(len(cookies), 2)'
b"-        cookies = cookiejar.get_cookies_for_url('https://foobar.foobar/')"
b"+        cookies = cookiejar.get_cookies_for_url(u'https://foobar.foobar/')"
b'         self.assertFalse(cookies)'
b' '
b' '
b"-if __name__ == '__main__':"
b"+if __name__ == u'__main__':"
b'     unittest.main()'
