b'--- ./yt_dlp/utils/_legacy.py\t(original)'
b'+++ ./yt_dlp/utils/_legacy.py\t(refactored)'
b'@@ -1,12 +1,13 @@'
b'-"""No longer used and new code should not use. Exists only for API compat."""'
b'+u"""No longer used and new code should not use. Exists only for API compat."""'
b'+from __future__ import absolute_import'
b' import asyncio'
b' import atexit'
b' import platform'
b' import struct'
b' import sys'
b'-import urllib.error'
b'-import urllib.parse'
b'-import urllib.request'
b'+import urllib2, urllib'
b'+import urllib2, urllib, urlparse'
b'+import urllib2, urllib'
b' import zlib'
b' '
b' from ._utils import Popen, decode_base_n, preferredencoding'
b'@@ -34,8 +35,8 @@'
b' has_websockets = bool(websockets)'
b' '
b' '
b'-class WebSocketsWrapper:'
b'-    """Wraps websockets module to use in non-async scopes"""'
b'+class WebSocketsWrapper(object):'
b'+    u"""Wraps websockets module to use in non-async scopes"""'
b'     pool = None'
b' '
b'     def __init__(self, url, headers=None, connect=True, **ws_kwargs):'
b'@@ -43,7 +44,7 @@'
b'         # XXX: "loop" is deprecated'
b'         self.conn = websockets.connect('
b'             url, extra_headers=headers, ping_interval=None,'
b"-            close_timeout=float('inf'), loop=self.loop, ping_timeout=float('inf'), **ws_kwargs)"
b"+            close_timeout=float(u'inf'), loop=self.loop, ping_timeout=float(u'inf'), **ws_kwargs)"
b'         if connect:'
b'             self.__enter__()'
b'         atexit.register(self.__exit__, None, None, None)'
b'@@ -77,7 +78,7 @@'
b'             return loop.run_until_complete(main)'
b'         finally:'
b'             loop.run_until_complete(loop.shutdown_asyncgens())'
b"-            if hasattr(loop, 'shutdown_default_executor'):"
b"+            if hasattr(loop, u'shutdown_default_executor'):"
b'                 loop.run_until_complete(loop.shutdown_default_executor())'
b' '
b'     @staticmethod'
b'@@ -99,9 +100,9 @@'
b'                 continue'
b'             if task.exception() is not None:'
b'                 loop.call_exception_handler({'
b"-                    'message': 'unhandled exception during asyncio.run() shutdown',"
b"-                    'exception': task.exception(),"
b"-                    'task': task,"
b"+                    u'message': u'unhandled exception during asyncio.run() shutdown',"
b"+                    u'exception': task.exception(),"
b"+                    u'task': task,"
b'                 })'
b' '
b' '
b'@@ -121,19 +122,19 @@'
b' '
b' '
b' def platform_name():'
b'-    """ Returns the platform name as a str """'
b'+    u""" Returns the platform name as a str """'
b'     return platform.platform()'
b' '
b' '
b' def get_subprocess_encoding():'
b"-    if sys.platform == 'win32' and sys.getwindowsversion()[0] >= 5:"
b"+    if sys.platform == u'win32' and sys.getwindowsversion()[0] >= 5:"
b'         # For subprocess calls, encode with locale encoding'
b'         # Refer to http://stackoverflow.com/a/9951851/35070'
b'         encoding = preferredencoding()'
b'     else:'
b'         encoding = sys.getfilesystemencoding()'
b'     if encoding is None:'
b"-        encoding = 'utf-8'"
b"+        encoding = u'utf-8'"
b'     return encoding'
b' '
b' '
b'@@ -144,10 +145,10 @@'
b'     # Reference: https://www.w3.org/TR/PNG/'
b'     header = png_data[8:]'
b' '
b"-    if png_data[:8] != b'\\x89PNG\\x0d\\x0a\\x1a\\x0a' or header[4:8] != b'IHDR':"
b"-        raise OSError('Not a valid PNG file.')"
b'-'
b"-    int_map = {1: '>B', 2: '>H', 4: '>I'}"
b"+    if png_data[:8] != '\\x89PNG\\x0d\\x0a\\x1a\\x0a' or header[4:8] != 'IHDR':"
b"+        raise OSError(u'Not a valid PNG file.')"
b'+'
b"+    int_map = {1: u'>B', 2: u'>H', 4: u'>I'}"
b'     unpack_integer = lambda x: struct.unpack(int_map[len(x)], x)[0]'
b' '
b'     chunks = []'
b'@@ -165,24 +166,24 @@'
b'         header = header[4:]  # Skip CRC'
b' '
b'         chunks.append({'
b"-            'type': chunk_type,"
b"-            'length': length,"
b"-            'data': chunk_data,"
b"+            u'type': chunk_type,"
b"+            u'length': length,"
b"+            u'data': chunk_data,"
b'         })'
b' '
b"-    ihdr = chunks[0]['data']"
b"+    ihdr = chunks[0][u'data']"
b' '
b'     width = unpack_integer(ihdr[:4])'
b'     height = unpack_integer(ihdr[4:8])'
b' '
b"-    idat = b''"
b"+    idat = ''"
b' '
b'     for chunk in chunks:'
b"-        if chunk['type'] == b'IDAT':"
b"-            idat += chunk['data']"
b"+        if chunk[u'type'] == 'IDAT':"
b"+            idat += chunk[u'data']"
b' '
b'     if not idat:'
b"-        raise OSError('Unable to read PNG data.')"
b"+        raise OSError(u'Unable to read PNG data.')"
b' '
b'     decompressed_data = bytearray(zlib.decompress(idat))'
b' '
b'@@ -194,7 +195,7 @@'
b'         y = idx // stride'
b'         return pixels[y][x]'
b' '
b'-    for y in range(height):'
b'+    for y in xrange(height):'
b'         base_pos = y * (1 + stride)'
b'         filter_type = decompressed_data[base_pos]'
b' '
b'@@ -202,7 +203,7 @@'
b' '
b'         pixels.append(current_row)'
b' '
b'-        for x in range(stride):'
b'+        for x in xrange(stride):'
b'             color = decompressed_data[1 + base_pos + x]'
b'             basex = y * stride + x'
b'             left = 0'
b'@@ -249,7 +250,7 @@'
b'     # "Register" SOCKS protocols'
b'     # In Python < 2.6.5, urlsplit() suffers from bug https://bugs.python.org/issue7904'
b'     # URLs with protocols not in urlparse.uses_netloc are not handled correctly'
b"-    for scheme in ('socks', 'socks4', 'socks4a', 'socks5'):"
b"+    for scheme in (u'socks', u'socks4', u'socks4a', u'socks5'):"
b'         if scheme not in urllib.parse.uses_netloc:'
b'             urllib.parse.uses_netloc.append(scheme)'
b' '
b'@@ -257,15 +258,15 @@'
b' def handle_youtubedl_headers(headers):'
b'     filtered_headers = headers'
b' '
b"-    if 'Youtubedl-no-compression' in filtered_headers:"
b"-        filtered_headers = {k: v for k, v in filtered_headers.items() if k.lower() != 'accept-encoding'}"
b"-        del filtered_headers['Youtubedl-no-compression']"
b"+    if u'Youtubedl-no-compression' in filtered_headers:"
b"+        filtered_headers = dict((k, v) for k, v in filtered_headers.items() if k.lower() != u'accept-encoding')"
b"+        del filtered_headers[u'Youtubedl-no-compression']"
b' '
b'     return filtered_headers'
b' '
b' '
b' def request_to_url(req):'
b'-    if isinstance(req, urllib.request.Request):'
b'+    if isinstance(req, urllib2.Request):'
b'         return req.get_full_url()'
b'     else:'
b'         return req'
b'@@ -275,39 +276,39 @@'
b'     from ..utils import extract_basic_auth, sanitize_url'
b'     url, auth_header = extract_basic_auth(escape_url(sanitize_url(url)))'
b'     if auth_header is not None:'
b"-        headers = args[1] if len(args) >= 2 else kwargs.setdefault('headers', {})"
b"-        headers['Authorization'] = auth_header"
b'-    return urllib.request.Request(url, *args, **kwargs)'
b"+        headers = args[1] if len(args) >= 2 else kwargs.setdefault(u'headers', {})"
b"+        headers[u'Authorization'] = auth_header"
b'+    return urllib2.Request(url, *args, **kwargs)'
b' '
b' '
b' class YoutubeDLHandler(HTTPHandler):'
b'     def __init__(self, params, *args, **kwargs):'
b'         self._params = params'
b'-        super().__init__(*args, **kwargs)'
b'+        super(YoutubeDLHandler, self).__init__(*args, **kwargs)'
b' '
b' '
b' YoutubeDLHTTPSHandler = YoutubeDLHandler'
b' '
b' '
b'-class YoutubeDLCookieProcessor(urllib.request.HTTPCookieProcessor):'
b'+class YoutubeDLCookieProcessor(urllib2.HTTPCookieProcessor):'
b'     def __init__(self, cookiejar=None):'
b'-        urllib.request.HTTPCookieProcessor.__init__(self, cookiejar)'
b'+        urllib2.HTTPCookieProcessor.__init__(self, cookiejar)'
b' '
b'     def http_response(self, request, response):'
b'-        return urllib.request.HTTPCookieProcessor.http_response(self, request, response)'
b'-'
b'-    https_request = urllib.request.HTTPCookieProcessor.http_request'
b'+        return urllib2.HTTPCookieProcessor.http_response(self, request, response)'
b'+'
b'+    https_request = urllib2.HTTPCookieProcessor.http_request'
b'     https_response = http_response'
b' '
b' '
b' def make_HTTPS_handler(params, **kwargs):'
b'     return YoutubeDLHTTPSHandler(params, context=make_ssl_context('
b"-        verify=not params.get('nocheckcertificate'),"
b"-        client_certificate=params.get('client_certificate'),"
b"-        client_certificate_key=params.get('client_certificate_key'),"
b"-        client_certificate_password=params.get('client_certificate_password'),"
b"-        legacy_support=params.get('legacyserverconnect'),"
b"-        use_certifi='no-certifi' not in params.get('compat_opts', []),"
b"+        verify=not params.get(u'nocheckcertificate'),"
b"+        client_certificate=params.get(u'client_certificate'),"
b"+        client_certificate_key=params.get(u'client_certificate_key'),"
b"+        client_certificate_password=params.get(u'client_certificate_password'),"
b"+        legacy_support=params.get(u'legacyserverconnect'),"
b"+        use_certifi=u'no-certifi' not in params.get(u'compat_opts', []),"
b'     ), **kwargs)'
b' '
b' '
b'@@ -316,7 +317,7 @@'
b' '
b' '
b' def encodeFilename(s, for_subprocess=False):'
b'-    assert isinstance(s, str)'
b'+    assert isinstance(s, unicode)'
b'     return s'
b' '
b' '
b'@@ -331,12 +332,12 @@'
b' def decodeOption(optval):'
b'     if optval is None:'
b'         return optval'
b'-    if isinstance(optval, bytes):'
b'+    if isinstance(optval, str):'
b'         optval = optval.decode(preferredencoding())'
b' '
b'-    assert isinstance(optval, str)'
b'+    assert isinstance(optval, unicode)'
b'     return optval'
b' '
b' '
b' def error_to_compat_str(err):'
b'-    return str(err)'
b'+    return unicode(err)'
