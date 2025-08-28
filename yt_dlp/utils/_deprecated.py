b'--- ./yt_dlp/utils/_deprecated.py\t(original)'
b'+++ ./yt_dlp/utils/_deprecated.py\t(refactored)'
b'@@ -1,4 +1,5 @@'
b'-"""Deprecated - New code should avoid these"""'
b'+u"""Deprecated - New code should avoid these"""'
b'+from __future__ import absolute_import'
b' import base64'
b' import hashlib'
b' import hmac'
b'@@ -8,7 +9,7 @@'
b' from ..compat.compat_utils import passthrough_module'
b' '
b' # XXX: Implement this the same way as other DeprecationWarnings without circular import'
b"-passthrough_module(__name__, '.._legacy', callback=lambda attr: warnings.warn("
b"+passthrough_module(__name__, u'.._legacy', callback=lambda attr: warnings.warn("
b"     DeprecationWarning(f'{__name__}.{attr} is deprecated'), stacklevel=6))"
b' del passthrough_module'
b' '
b'@@ -28,22 +29,22 @@'
b' '
b' def intlist_to_bytes(xs):'
b'     if not xs:'
b"-        return b''"
b"-    return struct.pack('%dB' % len(xs), *xs)"
b"+        return ''"
b"+    return struct.pack(u'%dB' % len(xs), *xs)"
b' '
b' '
b' def jwt_encode_hs256(payload_data, key, headers={}):'
b'     header_data = {'
b"-        'alg': 'HS256',"
b"-        'typ': 'JWT',"
b"+        u'alg': u'HS256',"
b"+        u'typ': u'JWT',"
b'     }'
b'     if headers:'
b'         header_data.update(headers)'
b'     header_b64 = base64.b64encode(json.dumps(header_data).encode())'
b'     payload_b64 = base64.b64encode(json.dumps(payload_data).encode())'
b"-    h = hmac.new(key.encode(), header_b64 + b'.' + payload_b64, hashlib.sha256)"
b"+    h = hmac.new(key.encode(), header_b64 + '.' + payload_b64, hashlib.sha256)"
b'     signature_b64 = base64.b64encode(h.digest())'
b"-    return header_b64 + b'.' + payload_b64 + b'.' + signature_b64"
b"+    return header_b64 + '.' + payload_b64 + '.' + signature_b64"
b' '
b' '
b"-compiled_regex_type = type(re.compile(''))"
b"+compiled_regex_type = type(re.compile(u''))"
