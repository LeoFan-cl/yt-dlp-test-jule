# coding: utf-8
from __future__ import unicode_literals

import sys
import unittest

from yt_dlp.compat import (
    compat_basestring,
    compat_chr,
    compat_input,
    compat_str,
)


class TestCompat(unittest.TestCase):
    def test_compat_str_is_unicode(self):
        self.assertIs(compat_str, unicode)

    def test_compat_basestring_is_basestring(self):
        self.assertIs(compat_basestring, basestring)

    def test_compat_input_is_raw_input(self):
        self.assertIs(compat_input, raw_input)

    def test_compat_chr_is_unichr(self):
        self.assertIs(compat_chr, unichr)
