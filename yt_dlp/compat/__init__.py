b'--- ./yt_dlp/compat/__init__.py\t(original)'
b'+++ ./yt_dlp/compat/__init__.py\t(refactored)'
b'@@ -1,9 +1,10 @@'
b'+from __future__ import absolute_import'
b' import os'
b' import xml.etree.ElementTree as etree'
b' '
b' from .compat_utils import passthrough_module'
b' '
b"-passthrough_module(__name__, '._deprecated')"
b"+passthrough_module(__name__, u'._deprecated')"
b' del passthrough_module'
b' '
b' '
b'@@ -30,14 +31,14 @@'
b' # Python 3.8+ does not honor %HOME% on windows, but this breaks compatibility with youtube-dl'
b' # See https://github.com/yt-dlp/yt-dlp/issues/792'
b' # https://docs.python.org/3/library/os.path.html#os.path.expanduser'
b"-if os.name in ('nt', 'ce'):"
b"+if os.name in (u'nt', u'ce'):"
b'     def compat_expanduser(path):'
b"-        HOME = os.environ.get('HOME')"
b"+        HOME = os.environ.get(u'HOME')"
b'         if not HOME:'
b'             return os.path.expanduser(path)'
b"-        elif not path.startswith('~'):"
b"+        elif not path.startswith(u'~'):"
b'             return path'
b"-        i = path.replace('\\\\', '/', 1).find('/')  # ~user"
b"+        i = path.replace(u'\\\\', u'/', 1).find(u'/')  # ~user"
b'         if i < 0:'
b'             i = len(path)'
b'         userhome = os.path.join(os.path.dirname(HOME), path[1:i]) if i > 1 else HOME'
b'@@ -47,10 +48,10 @@'
b' '
b' '
b' def urllib_req_to_req(urllib_request):'
b'-    """Convert urllib Request to a networking Request"""'
b'+    u"""Convert urllib Request to a networking Request"""'
b'     from ..networking import Request'
b'     from ..utils.networking import HTTPHeaderDict'
b'     return Request('
b'         urllib_request.get_full_url(), data=urllib_request.data, method=urllib_request.get_method(),'
b'         headers=HTTPHeaderDict(urllib_request.headers, urllib_request.unredirected_hdrs),'
b"-        extensions={'timeout': urllib_request.timeout} if hasattr(urllib_request, 'timeout') else None)"
b"+        extensions={u'timeout': urllib_request.timeout} if hasattr(urllib_request, u'timeout') else None)"
