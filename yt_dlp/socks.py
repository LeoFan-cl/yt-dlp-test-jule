b'--- ./yt_dlp/socks.py\t(original)'
b'+++ ./yt_dlp/socks.py\t(refactored)'
b'@@ -6,13 +6,14 @@'
b' # SOCKS5 protocol https://tools.ietf.org/html/rfc1928'
b' # SOCKS5 username/password authentication https://tools.ietf.org/html/rfc1929'
b' '
b'+from __future__ import absolute_import'
b' import collections'
b' import socket'
b' import struct'
b' '
b' from .compat import compat_ord'
b' '
b"-__author__ = 'Timo Schmid <coding@timoschmid.de>'"
b"+__author__ = u'Timo Schmid <coding@timoschmid.de>'"
b' '
b' SOCKS4_VERSION = 4'
b' SOCKS4_REPLY_VERSION = 0x00'
b'@@ -20,14 +21,14 @@'
b" # if the client cannot resolve the destination host's domain name to find its"
b' # IP address, it should set the first three bytes of DSTIP to NULL and the last'
b' # byte to a non-zero value.'
b"-SOCKS4_DEFAULT_DSTIP = struct.pack('!BBBB', 0, 0, 0, 0xFF)"
b"+SOCKS4_DEFAULT_DSTIP = struct.pack(u'!BBBB', 0, 0, 0, 0xFF)"
b' '
b' SOCKS5_VERSION = 5'
b' SOCKS5_USER_AUTH_VERSION = 0x01'
b' SOCKS5_USER_AUTH_SUCCESS = 0x00'
b' '
b' '
b'-class Socks4Command:'
b'+class Socks4Command(object):'
b'     CMD_CONNECT = 0x01'
b'     CMD_BIND = 0x02'
b' '
b'@@ -36,14 +37,14 @@'
b'     CMD_UDP_ASSOCIATE = 0x03'
b' '
b' '
b'-class Socks5Auth:'
b'+class Socks5Auth(object):'
b'     AUTH_NONE = 0x00'
b'     AUTH_GSSAPI = 0x01'
b'     AUTH_USER_PASS = 0x02'
b'     AUTH_NO_ACCEPTABLE = 0xFF  # For server response'
b' '
b' '
b'-class Socks5AddressType:'
b'+class Socks5AddressType(object):'
b'     ATYP_IPV4 = 0x01'
b'     ATYP_DOMAINNAME = 0x03'
b'     ATYP_IPV6 = 0x04'
b'@@ -54,24 +55,24 @@'
b' '
b'     def __init__(self, code=None, msg=None):'
b'         if code is not None and msg is None:'
b"-            msg = self.CODES.get(code) or 'unknown error'"
b'-        super().__init__(code, msg)'
b"+            msg = self.CODES.get(code) or u'unknown error'"
b'+        super(ProxyError, self).__init__(code, msg)'
b' '
b' '
b' class InvalidVersionError(ProxyError):'
b'     def __init__(self, expected_version, got_version):'
b"         msg = (f'Invalid response version from server. Expected {expected_version:02x} got '"
b"                f'{got_version:02x}')"
b'-        super().__init__(0, msg)'
b'+        super(InvalidVersionError, self).__init__(0, msg)'
b' '
b' '
b' class Socks4Error(ProxyError):'
b'     ERR_SUCCESS = 90'
b' '
b'     CODES = {'
b"-        91: 'request rejected or failed',"
b"-        92: 'request rejected because SOCKS server cannot connect to identd on the client',"
b"-        93: 'request rejected because the client program and identd report different user-ids',"
b"+        91: u'request rejected or failed',"
b"+        92: u'request rejected because SOCKS server cannot connect to identd on the client',"
b"+        93: u'request rejected because the client program and identd report different user-ids',"
b'     }'
b' '
b' '
b'@@ -79,33 +80,33 @@'
b'     ERR_GENERAL_FAILURE = 0x01'
b' '
b'     CODES = {'
b"-        0x01: 'general SOCKS server failure',"
b"-        0x02: 'connection not allowed by ruleset',"
b"-        0x03: 'Network unreachable',"
b"-        0x04: 'Host unreachable',"
b"-        0x05: 'Connection refused',"
b"-        0x06: 'TTL expired',"
b"-        0x07: 'Command not supported',"
b"-        0x08: 'Address type not supported',"
b"-        0xFE: 'unknown username or invalid password',"
b"-        0xFF: 'all offered authentication methods were rejected',"
b"+        0x01: u'general SOCKS server failure',"
b"+        0x02: u'connection not allowed by ruleset',"
b"+        0x03: u'Network unreachable',"
b"+        0x04: u'Host unreachable',"
b"+        0x05: u'Connection refused',"
b"+        0x06: u'TTL expired',"
b"+        0x07: u'Command not supported',"
b"+        0x08: u'Address type not supported',"
b"+        0xFE: u'unknown username or invalid password',"
b"+        0xFF: u'all offered authentication methods were rejected',"
b'     }'
b' '
b' '
b'-class ProxyType:'
b'+class ProxyType(object):'
b'     SOCKS4 = 0'
b'     SOCKS4A = 1'
b'     SOCKS5 = 2'
b' '
b' '
b"-Proxy = collections.namedtuple('Proxy', ("
b"-    'type', 'host', 'port', 'username', 'password', 'remote_dns'))"
b"+Proxy = collections.namedtuple(u'Proxy', ("
b"+    u'type', u'host', u'port', u'username', u'password', u'remote_dns'))"
b' '
b' '
b' class sockssocket(socket.socket):'
b'     def __init__(self, *args, **kwargs):'
b'         self._proxy = None'
b'-        super().__init__(*args, **kwargs)'
b'+        super(sockssocket, self).__init__(*args, **kwargs)'
b' '
b'     def setproxy(self, proxytype, addr, port, rdns=True, username=None, password=None):'
b'         assert proxytype in (ProxyType.SOCKS4, ProxyType.SOCKS4A, ProxyType.SOCKS5)'
b'@@ -113,7 +114,7 @@'
b'         self._proxy = Proxy(proxytype, addr, port, username, password, rdns)'
b' '
b'     def recvall(self, cnt):'
b"-        data = b''"
b"+        data = ''"
b'         while len(data) < cnt:'
b'             cur = self.recv(cnt - len(data))'
b'             if not cur:'
b'@@ -127,7 +128,7 @@'
b' '
b'     @staticmethod'
b'     def _len_and_data(data):'
b"-        return struct.pack('!B', len(data)) + data"
b"+        return struct.pack(u'!B', len(data)) + data"
b' '
b'     def _check_response_version(self, expected_version, got_version):'
b'         if got_version != expected_version:'
b'@@ -153,17 +154,17 @@'
b' '
b'         _, ipaddr = self._resolve_address(destaddr, SOCKS4_DEFAULT_DSTIP, use_remote_dns=is_4a, family=socket.AF_INET)'
b' '
b"-        packet = struct.pack('!BBH', SOCKS4_VERSION, Socks4Command.CMD_CONNECT, port) + ipaddr"
b'-'
b"-        username = (self._proxy.username or '').encode()"
b"-        packet += username + b'\\x00'"
b"+        packet = struct.pack(u'!BBH', SOCKS4_VERSION, Socks4Command.CMD_CONNECT, port) + ipaddr"
b'+'
b"+        username = (self._proxy.username or u'').encode()"
b"+        packet += username + '\\x00'"
b' '
b'         if is_4a and self._proxy.remote_dns and ipaddr == SOCKS4_DEFAULT_DSTIP:'
b"-            packet += destaddr.encode() + b'\\x00'"
b"+            packet += destaddr.encode() + '\\x00'"
b' '
b'         self.sendall(packet)'
b' '
b"-        version, resp_code, dstport, dsthost = struct.unpack('!BBHI', self.recvall(8))"
b"+        version, resp_code, dstport, dsthost = struct.unpack(u'!BBHI', self.recvall(8))"
b' '
b'         self._check_response_version(SOCKS4_REPLY_VERSION, version)'
b' '
b'@@ -177,13 +178,13 @@'
b'         self._setup_socks4(address, is_4a=True)'
b' '
b'     def _socks5_auth(self):'
b"-        packet = struct.pack('!B', SOCKS5_VERSION)"
b"+        packet = struct.pack(u'!B', SOCKS5_VERSION)"
b' '
b'         auth_methods = [Socks5Auth.AUTH_NONE]'
b'         if self._proxy.username and self._proxy.password:'
b'             auth_methods.append(Socks5Auth.AUTH_USER_PASS)'
b' '
b"-        packet += struct.pack('!B', len(auth_methods))"
b"+        packet += struct.pack(u'!B', len(auth_methods))"
b"         packet += struct.pack(f'!{len(auth_methods)}B', *auth_methods)"
b' '
b'         self.sendall(packet)'
b'@@ -200,7 +201,7 @@'
b'         if method == Socks5Auth.AUTH_USER_PASS:'
b'             username = self._proxy.username.encode()'
b'             password = self._proxy.password.encode()'
b"-            packet = struct.pack('!B', SOCKS5_USER_AUTH_VERSION)"
b"+            packet = struct.pack(u'!B', SOCKS5_USER_AUTH_VERSION)"
b'             packet += self._len_and_data(username) + self._len_and_data(password)'
b'             self.sendall(packet)'
b' '
b'@@ -220,16 +221,16 @@'
b'         self._socks5_auth()'
b' '
b'         reserved = 0'
b"-        packet = struct.pack('!BBB', SOCKS5_VERSION, Socks5Command.CMD_CONNECT, reserved)"
b"+        packet = struct.pack(u'!BBB', SOCKS5_VERSION, Socks5Command.CMD_CONNECT, reserved)"
b'         if ipaddr is None:'
b'             destaddr = destaddr.encode()'
b"-            packet += struct.pack('!B', Socks5AddressType.ATYP_DOMAINNAME)"
b"+            packet += struct.pack(u'!B', Socks5AddressType.ATYP_DOMAINNAME)"
b'             packet += self._len_and_data(destaddr)'
b'         elif family == socket.AF_INET:'
b"-            packet += struct.pack('!B', Socks5AddressType.ATYP_IPV4) + ipaddr"
b"+            packet += struct.pack(u'!B', Socks5AddressType.ATYP_IPV4) + ipaddr"
b'         elif family == socket.AF_INET6:'
b"-            packet += struct.pack('!B', Socks5AddressType.ATYP_IPV6) + ipaddr"
b"-        packet += struct.pack('!H', port)"
b"+            packet += struct.pack(u'!B', Socks5AddressType.ATYP_IPV6) + ipaddr"
b"+        packet += struct.pack(u'!H', port)"
b' '
b'         self.sendall(packet)'
b' '
b'@@ -248,7 +249,7 @@'
b'             destaddr = self.recvall(alen)'
b'         elif atype == Socks5AddressType.ATYP_IPV6:'
b'             destaddr = self.recvall(16)'
b"-        destport = struct.unpack('!H', self.recvall(2))[0]"
b"+        destport = struct.unpack(u'!H', self.recvall(2))[0]"
b' '
b'         return (destaddr, destport)'
b' '
