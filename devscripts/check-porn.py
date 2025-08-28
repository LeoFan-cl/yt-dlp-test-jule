b'--- ./devscripts/check-porn.py\t(original)'
b'+++ ./devscripts/check-porn.py\t(refactored)'
b'@@ -1,5 +1,5 @@'
b' #!/usr/bin/env python3'
b'-"""'
b'+u"""'
b" This script employs a VERY basic heuristic ('porn' in webpage.lower()) to check"
b" if we are not 'age_limit' tagging some porn site"
b' '
b'@@ -8,54 +8,56 @@'
b' """'
b' '
b' # Allow direct execution'
b'+from __future__ import absolute_import'
b' import os'
b' import sys'
b'+from io import open'
b' '
b' sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'
b' '
b' '
b'-import urllib.parse'
b'-import urllib.request'
b'+import urllib2, urllib, urlparse'
b'+import urllib2, urllib'
b' '
b' from test.helper import gettestcases'
b' '
b' if len(sys.argv) > 1:'
b"-    METHOD = 'LIST'"
b"-    LIST = open(sys.argv[1]).read().decode('utf8').strip()"
b"+    METHOD = u'LIST'"
b"+    LIST = open(sys.argv[1]).read().decode(u'utf8').strip()"
b' else:'
b"-    METHOD = 'EURISTIC'"
b"+    METHOD = u'EURISTIC'"
b' '
b' for test in gettestcases():'
b"-    if METHOD == 'EURISTIC':"
b"+    if METHOD == u'EURISTIC':"
b'         try:'
b"-            webpage = urllib.request.urlopen(test['url'], timeout=10).read()"
b"+            webpage = urllib2.urlopen(test[u'url'], timeout=10).read()"
b'         except Exception:'
b"-            print('\\nFail: {}'.format(test['name']))"
b"+            print u'\\nFail: {}'.format(test[u'name'])"
b'             continue'
b' '
b"-        webpage = webpage.decode('utf8', 'replace')"
b"+        webpage = webpage.decode(u'utf8', u'replace')"
b' '
b"-        RESULT = 'porn' in webpage.lower()"
b"+        RESULT = u'porn' in webpage.lower()"
b' '
b"-    elif METHOD == 'LIST':"
b"-        domain = urllib.parse.urlparse(test['url']).netloc"
b"+    elif METHOD == u'LIST':"
b"+        domain = urlparse.urlparse(test[u'url']).netloc"
b'         if not domain:'
b"-            print('\\nFail: {}'.format(test['name']))"
b"+            print u'\\nFail: {}'.format(test[u'name'])"
b'             continue'
b"-        domain = '.'.join(domain.split('.')[-2:])"
b"+        domain = u'.'.join(domain.split(u'.')[-2:])"
b' '
b"-        RESULT = ('.' + domain + '\\n' in LIST or '\\n' + domain + '\\n' in LIST)"
b"+        RESULT = (u'.' + domain + u'\\n' in LIST or u'\\n' + domain + u'\\n' in LIST)"
b' '
b"-    if RESULT and ('info_dict' not in test or 'age_limit' not in test['info_dict']"
b"-                   or test['info_dict']['age_limit'] != 18):"
b"-        print('\\nPotential missing age_limit check: {}'.format(test['name']))"
b"+    if RESULT and (u'info_dict' not in test or u'age_limit' not in test[u'info_dict']"
b"+                   or test[u'info_dict'][u'age_limit'] != 18):"
b"+        print u'\\nPotential missing age_limit check: {}'.format(test[u'name'])"
b' '
b"-    elif not RESULT and ('info_dict' in test and 'age_limit' in test['info_dict']"
b"-                         and test['info_dict']['age_limit'] == 18):"
b"-        print('\\nPotential false negative: {}'.format(test['name']))"
b"+    elif not RESULT and (u'info_dict' in test and u'age_limit' in test[u'info_dict']"
b"+                         and test[u'info_dict'][u'age_limit'] == 18):"
b"+        print u'\\nPotential false negative: {}'.format(test[u'name'])"
b' '
b'     else:'
b"-        sys.stdout.write('.')"
b"+        sys.stdout.write(u'.')"
b'     sys.stdout.flush()'
b' '
b'-print()'
b'+print'
