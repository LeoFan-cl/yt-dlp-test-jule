b'--- ./devscripts/lazy_load_template.py\t(original)'
b'+++ ./devscripts/lazy_load_template.py\t(refactored)'
b'@@ -1,3 +1,4 @@'
b'+from __future__ import absolute_import'
b' import importlib'
b' import random'
b' import re'
b'@@ -11,25 +12,26 @@'
b' )'
b' '
b' # These bloat the lazy_extractors, so allow them to passthrough silently'
b"-ALLOWED_CLASSMETHODS = {'extract_from_webpage', 'get_testcases', 'get_webpage_testcases'}"
b"+ALLOWED_CLASSMETHODS = set([u'extract_from_webpage', u'get_testcases', u'get_webpage_testcases'])"
b' _WARNED = False'
b' '
b' '
b' class LazyLoadMetaClass(type):'
b'     def __getattr__(cls, name):'
b'         global _WARNED'
b"-        if ('_real_class' not in cls.__dict__"
b"+        if (u'_real_class' not in cls.__dict__"
b'                 and name not in ALLOWED_CLASSMETHODS and not _WARNED):'
b'             _WARNED = True'
b"-            write_string('WARNING: Falling back to normal extractor since lazy extractor '"
b"+            write_string(u'WARNING: Falling back to normal extractor since lazy extractor '"
b"                          f'{cls.__name__} does not have attribute {name}{bug_reports_message()}\\n')"
b'         return getattr(cls.real_class, name)'
b' '
b' '
b'-class LazyLoadExtractor(metaclass=LazyLoadMetaClass):'
b'+class LazyLoadExtractor(object):'
b'+    __metaclass__ = LazyLoadMetaClass'
b'     @classproperty'
b'     def real_class(cls):'
b"-        if '_real_class' not in cls.__dict__:"
b"+        if u'_real_class' not in cls.__dict__:"
b'             cls._real_class = getattr(importlib.import_module(cls._module), cls.__name__)'
b'         return cls._real_class'
b' '
