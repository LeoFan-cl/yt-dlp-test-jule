b'--- ./devscripts/make_contributing.py\t(original)'
b'+++ ./devscripts/make_contributing.py\t(refactored)'
b'@@ -1,32 +1,35 @@'
b' #!/usr/bin/env python3'
b' '
b'+from __future__ import with_statement'
b'+from __future__ import absolute_import'
b' import optparse'
b' import re'
b'+from io import open'
b' '
b' '
b' def main():'
b'     return  # This is unused in yt-dlp'
b' '
b"-    parser = optparse.OptionParser(usage='%prog INFILE OUTFILE')"
b"+    parser = optparse.OptionParser(usage=u'%prog INFILE OUTFILE')"
b'     options, args = parser.parse_args()'
b'     if len(args) != 2:'
b"-        parser.error('Expected an input and an output filename')"
b"+        parser.error(u'Expected an input and an output filename')"
b' '
b'     infile, outfile = args'
b' '
b"-    with open(infile, encoding='utf-8') as inf:"
b"+    with open(infile, encoding=u'utf-8') as inf:"
b'         readme = inf.read()'
b' '
b'     bug_text = re.search('
b"-        r'(?s)#\\s*BUGS\\s*[^\\n]*\\s*(.*?)#\\s*COPYRIGHT', readme).group(1)"
b"+        ur'(?s)#\\s*BUGS\\s*[^\\n]*\\s*(.*?)#\\s*COPYRIGHT', readme).group(1)"
b'     dev_text = re.search('
b"-        r'(?s)(#\\s*DEVELOPER INSTRUCTIONS.*?)#\\s*EMBEDDING yt-dlp', readme).group(1)"
b"+        ur'(?s)(#\\s*DEVELOPER INSTRUCTIONS.*?)#\\s*EMBEDDING yt-dlp', readme).group(1)"
b' '
b'     out = bug_text + dev_text'
b' '
b"-    with open(outfile, 'w', encoding='utf-8') as outf:"
b"+    with open(outfile, u'w', encoding=u'utf-8') as outf:"
b'         outf.write(out)'
b' '
b' '
b"-if __name__ == '__main__':"
b"+if __name__ == u'__main__':"
b'     main()'
