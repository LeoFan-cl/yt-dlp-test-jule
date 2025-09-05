from __future__ import absolute_import
import os
import xml.etree.ElementTree as etree

from ._legacy import *

# HTMLParseError has been deprecated in Python 3.3 and removed in
# Python 3.5. Introducing dummy exception for Python >3.5 for compatible
# and uniform cross-version exception handling
class compat_HTMLParseError(ValueError):
    pass


class _TreeBuilder(etree.TreeBuilder):
    def doctype(self, name, pubid, system):
        pass


def compat_etree_fromstring(text):
    return etree.XML(text, parser=etree.XMLParser(target=_TreeBuilder()))


def compat_ord(c):
    return c if isinstance(c, int) else ord(c)


# Python 3.8+ does not honor %HOME% on windows, but this breaks compatibility with youtube-dl
# See https://github.com/yt-dlp/yt-dlp/issues/792
# https://docs.python.org/3/library/os.path.html#os.path.expanduser
if os.name in (u'nt', u'ce'):
    def compat_expanduser(path):
        HOME = os.environ.get(u'HOME')
        if not HOME:
            return os.path.expanduser(path)
        elif not path.startswith(u'~'):
            return path
        i = path.replace(u'\\', u'/', 1).find(u'/')  # ~user
        if i < 0:
            i = len(path)
        userhome = os.path.join(os.path.dirname(HOME), path[1:i]) if i > 1 else HOME
        return userhome + path[i:]
else:
    compat_expanduser = os.path.expanduser


def urllib_req_to_req(urllib_request):
    u"""Convert urllib Request to a networking Request"""
    from ..networking import Request
    from ..utils.networking import HTTPHeaderDict
    return Request(
        urllib_request.get_full_url(), data=urllib_request.data, method=urllib_request.get_method(),
        headers=HTTPHeaderDict(urllib_request.headers, urllib_request.unredirected_hdrs),
        extensions={u'timeout': urllib_request.timeout} if hasattr(urllib_request, u'timeout') else None)
