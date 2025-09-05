# flake8: noqa: F401, F403
u"""
A compatibility layer for Python 2 and 3.
This is a heavily modified version of the youtube-dl compat module.
Do not use!
"""
from __future__ import absolute_import

import base64
import collections
import ctypes
import getpass
import itertools
import os
import shlex
import shutil
import socket
import struct
import subprocess
import sys
import tokenize
import xml.etree.ElementTree as etree

from ..dependencies import websockets as compat_websockets
from ..dependencies.Cryptodome import AES as compat_pycrypto_AES
from ..networking.exceptions import HTTPError as compat_HTTPError
from .compat_utils import passthrough_module

passthrough_module(__name__, u'...utils', (u'windows_enable_vt_mode',))

if sys.version_info[0] >= 3:
    # Python 3
    import html.entities as compat_html_entities
    from html.parser import HTMLParser as compat_HTMLParser
    import http.client as compat_http_client
    import http.cookiejar as compat_cookiejar
    import http.cookies as compat_cookies
    import http.server as compat_http_server
    import urllib.error as compat_urllib_error
    import urllib.parse as compat_urllib_parse
    import urllib.request as compat_urllib_request
    import urllib.response as compat_urllib_response

    compat_basestring = str
    compat_chr = chr
    compat_input = input
    compat_str = str
    compat_urllib_parse_urlparse = compat_urllib_parse.urlparse
    compat_urllib_parse_urlencode = compat_urllib_parse.urlencode
    compat_urllib_parse_unquote = compat_urllib_parse.unquote
    compat_urllib_parse_unquote_plus = compat_urllib_parse.unquote_plus
    compat_urllib_parse_parse_qs = compat_urllib_parse.parse_qs
    compat_urllib_request_urlretrieve = compat_urllib_request.urlretrieve
    compat_cookiejar_Cookie = compat_cookiejar.Cookie
    compat_cookies_SimpleCookie = compat_cookies.SimpleCookie
    compat_http_client_HTTPException = compat_http_client.HTTPException
    compat_get_terminal_size = shutil.get_terminal_size

else:
    # Python 2
    import BaseHTTPServer as compat_http_server
    import Cookie as compat_cookies
    import cookielib as compat_cookiejar
    import htmlentitydefs as compat_html_entities
    from HTMLParser import HTMLParser as compat_HTMLParser
    import httplib as compat_http_client
    import urllib
    import urllib2
    import urlparse

    compat_urllib_error = urllib2
    compat_urllib_parse = urlparse
    compat_urllib_request = urllib2
    compat_urllib_response = urllib

    compat_basestring = basestring
    compat_chr = unichr
    compat_input = raw_input
    compat_str = unicode
    compat_urllib_parse_urlparse = urlparse.urlparse
    compat_urllib_parse_urlencode = urllib.urlencode
    compat_urllib_parse_unquote = urllib.unquote
    compat_urllib_parse_unquote_plus = urllib.unquote_plus
    compat_urllib_parse_parse_qs = urlparse.parse_qs
    compat_urllib_request_urlretrieve = urllib.urlretrieve
    compat_cookiejar_Cookie = compat_cookiejar.Cookie
    compat_cookies_SimpleCookie = compat_cookies.SimpleCookie
    compat_http_client_HTTPException = compat_http_client.HTTPException

    def compat_get_terminal_size(fallback=(80, 24)):
        try:
            import fcntl, termios
            # STDOUT_FILENO = 1
            hw = struct.unpack('hh', fcntl.ioctl(1, termios.TIOCGWINSZ, '1234'))
            return hw[1], hw[0]
        except:
            return fallback


compat_casefold = compat_str.casefold
compat_collections_abc = collections
compat_getenv = os.getenv
compat_getpass = compat_getpass_getpass = getpass.getpass
compat_html_entities_html5 = compat_html_entities.html5
compat_integer_types = (int, long) if sys.version_info[0] == 2 else (int,)
compat_kwargs = lambda kwargs: kwargs
compat_numeric_types = (int, long, float, complex) if sys.version_info[0] == 2 else (int, float, complex)
compat_os_name = os.name
compat_shlex_quote = shlex.quote
compat_socket_create_connection = socket.create_connection
compat_struct_pack = struct.pack
compat_struct_unpack = struct.unpack
compat_subprocess_getoutput = subprocess.getoutput
compat_tokenize_tokenize = tokenize.tokenize
compat_etree_Element = etree.Element
compat_etree_register_namespace = etree.register_namespace
compat_xml_parse_error = etree.ParseError
compat_xpath = lambda xpath: xpath
compat_zip = zip
workaround_optparse_bug9161 = lambda: None
compat_b64decode = base64.b64decode
compat_urlparse = compat_urllib_parse
compat_parse_qs = compat_urllib_parse_parse_qs

legacy = []
