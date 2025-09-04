# flake8: noqa: F405
from __future__ import absolute_import

import sys

if sys.version_info[0] == 2:
    from urllib2 import *
else:
    from urllib import *
    from urllib2 import *
