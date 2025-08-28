b'--- ./test/testdata/netrc/print_netrc.py\t(original)'
b'+++ ./test/testdata/netrc/print_netrc.py\t(refactored)'
b'@@ -1,2 +1,5 @@'
b"-with open('./test/testdata/netrc/netrc', encoding='utf-8') as fp:"
b'-    print(fp.read())'
b'+from __future__ import absolute_import'
b'+from __future__ import with_statement'
b'+from io import open'
b"+with open(u'./test/testdata/netrc/netrc', encoding=u'utf-8') as fp:"
b'+    print fp.read()'
