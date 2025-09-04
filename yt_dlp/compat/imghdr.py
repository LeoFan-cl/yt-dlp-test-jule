from __future__ import absolute_import
from __future__ import with_statement
from io import open

def what(file=None, h=None):
    u"""Detect format of image (Currently supports jpeg, png, webp, gif only)
    Ref: https://github.com/python/cpython/blob/3.11/Lib/imghdr.py
    Ref: https://www.w3.org/Graphics/JPEG/itu-t81.pdf
    """
    if h is None:
        with open(file, u'rb') as f:
            h = f.read(12)

    if h.startswith('RIFF') and h.startswith('WEBP', 8):
        return u'webp'

    if h.startswith('\\x89PNG'):
        return u'png'

    if h.startswith('\\xFF\\xD8\\xFF'):
        return u'jpeg'

    if h.startswith('GIF'):
        return u'gif'

    return None
