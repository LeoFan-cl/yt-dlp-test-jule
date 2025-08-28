b'--- ./devscripts/generate_aes_testdata.py\t(original)'
b'+++ ./devscripts/generate_aes_testdata.py\t(refactored)'
b'@@ -1,6 +1,7 @@'
b' #!/usr/bin/env python3'
b' '
b' # Allow direct execution'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b' '
b'@@ -12,15 +13,15 @@'
b' '
b' from yt_dlp.aes import aes_encrypt, key_expansion'
b' '
b"-secret_msg = b'Secret message goes here'"
b"+secret_msg = 'Secret message goes here'"
b' '
b' '
b' def hex_str(int_list):'
b"-    return codecs.encode(bytes(int_list), 'hex')"
b"+    return codecs.encode(str(int_list), u'hex')"
b' '
b' '
b' def openssl_encode(algo, key, iv):'
b"-    cmd = ['openssl', 'enc', '-e', '-' + algo, '-K', hex_str(key), '-iv', hex_str(iv)]"
b"+    cmd = [u'openssl', u'enc', u'-e', u'-' + algo, u'-K', hex_str(key), u'-iv', hex_str(iv)]"
b'     prog = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)'
b'     out, _ = prog.communicate(secret_msg)'
b'     return out'
b'@@ -28,18 +29,18 @@'
b' '
b' iv = key = [0x20, 0x15] + 14 * [0]'
b' '
b"-r = openssl_encode('aes-128-cbc', key, iv)"
b"-print('aes_cbc_decrypt')"
b'-print(repr(r))'
b"+r = openssl_encode(u'aes-128-cbc', key, iv)"
b"+print u'aes_cbc_decrypt'"
b'+print repr(r)'
b' '
b' password = key'
b' new_key = aes_encrypt(password, key_expansion(password))'
b"-r = openssl_encode('aes-128-ctr', new_key, iv)"
b"-print('aes_decrypt_text 16')"
b'-print(repr(r))'
b"+r = openssl_encode(u'aes-128-ctr', new_key, iv)"
b"+print u'aes_decrypt_text 16'"
b'+print repr(r)'
b' '
b' password = key + 16 * [0]'
b' new_key = aes_encrypt(password, key_expansion(password)) * (32 // 16)'
b"-r = openssl_encode('aes-256-ctr', new_key, iv)"
b"-print('aes_decrypt_text 32')"
b'-print(repr(r))'
b"+r = openssl_encode(u'aes-256-ctr', new_key, iv)"
b"+print u'aes_decrypt_text 32'"
b'+print repr(r)'
