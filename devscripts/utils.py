b'--- ./devscripts/utils.py\t(original)'
b'+++ ./devscripts/utils.py\t(refactored)'
b'@@ -1,31 +1,34 @@'
b'+from __future__ import with_statement'
b'+from __future__ import absolute_import'
b' import argparse'
b' import functools'
b' import subprocess'
b'+from io import open'
b' '
b' '
b' def read_file(fname):'
b"-    with open(fname, encoding='utf-8') as f:"
b"+    with open(fname, encoding=u'utf-8') as f:"
b'         return f.read()'
b' '
b' '
b"-def write_file(fname, content, mode='w'):"
b"-    with open(fname, mode, encoding='utf-8') as f:"
b"+def write_file(fname, content, mode=u'w'):"
b"+    with open(fname, mode, encoding=u'utf-8') as f:"
b'         return f.write(content)'
b' '
b' '
b"-def read_version(fname='yt_dlp/version.py', varname='__version__'):"
b'-    """Get the version without importing the package"""'
b"+def read_version(fname=u'yt_dlp/version.py', varname=u'__version__'):"
b'+    u"""Get the version without importing the package"""'
b'     items = {}'
b"-    exec(compile(read_file(fname), fname, 'exec'), items)"
b"+    exec(compile(read_file(fname), fname, u'exec'), items)"
b'     return items[varname]'
b' '
b' '
b' def get_filename_args(has_infile=False, default_outfile=None):'
b'     parser = argparse.ArgumentParser()'
b'     if has_infile:'
b"-        parser.add_argument('infile', help='Input file')"
b"-    kwargs = {'nargs': '?', 'default': default_outfile} if default_outfile else {}"
b"-    parser.add_argument('outfile', **kwargs, help='Output file')"
b"+        parser.add_argument(u'infile', help=u'Input file')"
b"+    kwargs = {u'nargs': u'?', u'default': default_outfile} if default_outfile else {}"
b"+    parser.add_argument(u'outfile', **kwargs, help=u'Output file')"
b' '
b'     opts = parser.parse_args()'
b'     if has_infile:'
b'@@ -34,14 +37,14 @@'
b' '
b' '
b' def compose_functions(*functions):'
b'-    return lambda x: functools.reduce(lambda y, f: f(y), functions, x)'
b'+    return lambda x: reduce(lambda y, f: f(y), functions, x)'
b' '
b' '
b' def run_process(*args, **kwargs):'
b"-    kwargs.setdefault('text', True)"
b"-    kwargs.setdefault('check', True)"
b"-    kwargs.setdefault('capture_output', True)"
b"-    if kwargs['text']:"
b"-        kwargs.setdefault('encoding', 'utf-8')"
b"-        kwargs.setdefault('errors', 'replace')"
b"+    kwargs.setdefault(u'text', True)"
b"+    kwargs.setdefault(u'check', True)"
b"+    kwargs.setdefault(u'capture_output', True)"
b"+    if kwargs[u'text']:"
b"+        kwargs.setdefault(u'encoding', u'utf-8')"
b"+        kwargs.setdefault(u'errors', u'replace')"
b'     return subprocess.run(args, **kwargs)'
