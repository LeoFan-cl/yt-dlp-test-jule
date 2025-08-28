b'--- ./yt_dlp/webvtt.py\t(original)'
b'+++ ./yt_dlp/webvtt.py\t(refactored)'
b'@@ -1,4 +1,4 @@'
b'-"""'
b'+u"""'
b' A partial parser for WebVTT segments. Interprets enough of the WebVTT stream'
b' to be able to assemble a single stand-alone subtitle file, suitably adjusting'
b' timestamps on the way, while everything else is passed through unmodified.'
b'@@ -8,14 +8,16 @@'
b' in RFC 8216 \xc2\xa73.5 <https://tools.ietf.org/html/rfc8216#section-3.5>.'
b' """'
b' '
b'+from __future__ import absolute_import'
b' import io'
b' import re'
b' '
b' from .utils import int_or_none, timetuple_from_msec'
b'-'
b'-'
b'-class _MatchParser:'
b'-    """'
b'+from itertools import izip'
b'+'
b'+'
b'+class _MatchParser(object):'
b'+    u"""'
b'     An object that maintains the current parsing position and allows'
b'     conveniently advancing it as syntax elements are successfully parsed.'
b'     """'
b'@@ -27,7 +29,7 @@'
b'     def match(self, r):'
b'         if isinstance(r, re.Pattern):'
b'             return r.match(self._data, self._pos)'
b'-        if isinstance(r, str):'
b'+        if isinstance(r, unicode):'
b'             if self._data.startswith(r, self._pos):'
b'                 return len(r)'
b'             return None'
b'@@ -38,7 +40,7 @@'
b'             amt = 0'
b'         elif isinstance(by, re.Match):'
b'             amt = len(by.group(0))'
b'-        elif isinstance(by, str):'
b'+        elif isinstance(by, unicode):'
b'             amt = len(by)'
b'         elif isinstance(by, int):'
b'             amt = by'
b'@@ -55,7 +57,7 @@'
b' '
b' '
b' class _MatchChildParser(_MatchParser):'
b'-    """'
b'+    u"""'
b'     A child parser state, which advances through the same data as'
b'     its parent, but has an independent position. This is useful when'
b'     advancing through syntax elements we might later want to backtrack'
b'@@ -63,12 +65,12 @@'
b'     """'
b' '
b'     def __init__(self, parent):'
b'-        super().__init__(parent._data)'
b'+        super(_MatchChildParser, self).__init__(parent._data)'
b'         self.__parent = parent'
b'         self._pos = parent._pos'
b' '
b'     def commit(self):'
b'-        """'
b'+        u"""'
b'         Advance the parent state to the current position of this child state.'
b'         """'
b'         self.__parent._pos = self._pos'
b'@@ -78,44 +80,44 @@'
b' class ParseError(Exception):'
b'     def __init__(self, parser):'
b'         data = parser._data[parser._pos:parser._pos + 100]'
b"-        super().__init__(f'Parse error at position {parser._pos} (near {data!r})')"
b"+        super(ParseError, self).__init__(f'Parse error at position {parser._pos} (near {data!r})')"
b' '
b' '
b' # While the specification <https://www.w3.org/TR/webvtt1/#webvtt-timestamp>'
b' # prescribes that hours must be *2 or more* digits, timestamps with a single'
b' # digit for the hour part has been seen in the wild.'
b' # See https://github.com/yt-dlp/yt-dlp/issues/921'
b"-_REGEX_TS = re.compile(r'''(?x)"
b"+_REGEX_TS = re.compile(ur'''(?x)"
b'     (?:([0-9]{1,}):)?'
b'     ([0-9]{2}):'
b'     ([0-9]{2})\\.'
b'     ([0-9]{3})?'
b" ''')"
b"-_REGEX_EOF = re.compile(r'\\Z')"
b"-_REGEX_NL = re.compile(r'(?:\\r\\n|[\\r\\n]|$)')"
b"-_REGEX_BLANK = re.compile(r'(?:\\r\\n|[\\r\\n])+')"
b"-_REGEX_OPTIONAL_WHITESPACE = re.compile(r'[ \\t]*')"
b"+_REGEX_EOF = re.compile(ur'\\Z')"
b"+_REGEX_NL = re.compile(ur'(?:\\r\\n|[\\r\\n]|$)')"
b"+_REGEX_BLANK = re.compile(ur'(?:\\r\\n|[\\r\\n])+')"
b"+_REGEX_OPTIONAL_WHITESPACE = re.compile(ur'[ \\t]*')"
b' '
b' '
b' def _parse_ts(ts):'
b'-    """'
b'+    u"""'
b'     Convert a parsed WebVTT timestamp (a re.Match obtained from _REGEX_TS)'
b'     into an MPEG PES timestamp: a tick counter at 90 kHz resolution.'
b'     """'
b'     return 90 * sum('
b'-        int(part or 0) * mult for part, mult in zip(ts.groups(), (3600_000, 60_000, 1000, 1)))'
b'+        int(part or 0) * mult for part, mult in izip(ts.groups(), (3600_000, 60_000, 1000, 1)))'
b' '
b' '
b' def _format_ts(ts):'
b'-    """'
b'+    u"""'
b'     Convert an MPEG PES timestamp into a WebVTT timestamp.'
b'     This will lose sub-millisecond precision.'
b'     """'
b"-    return '%02u:%02u:%02u.%03u' % timetuple_from_msec(int((ts + 45) // 90))"
b'-'
b'-'
b'-class Block:'
b'-    """'
b"+    return u'%02u:%02u:%02u.%03u' % timetuple_from_msec(int((ts + 45) // 90))"
b'+'
b'+'
b'+class Block(object):'
b'+    u"""'
b'     An abstract WebVTT block.'
b'     """'
b' '
b'@@ -136,7 +138,7 @@'
b' '
b' '
b' class HeaderBlock(Block):'
b'-    """'
b'+    u"""'
b'     A WebVTT block that may only appear in the header part of the file,'
b'     i.e. before any cue blocks.'
b'     """'
b'@@ -144,7 +146,7 @@'
b' '
b' '
b' class Magic(HeaderBlock):'
b"-    _REGEX = re.compile(r'\\ufeff?WEBVTT([ \\t][^\\r\\n]*)?(?:\\r\\n|[\\r\\n])')"
b"+    _REGEX = re.compile(ur'\\ufeff?WEBVTT([ \\t][^\\r\\n]*)?(?:\\r\\n|[\\r\\n])')"
b' '
b'     # XXX: The X-TIMESTAMP-MAP extension is described in RFC 8216 \xc2\xa73.5'
b'     # <https://tools.ietf.org/html/rfc8216#section-3.5>, but the RFC'
b'@@ -155,16 +157,16 @@'
b'     # And strictly speaking, the presence of this extension violates'
b'     # the W3C WebVTT spec. Oh well.'
b' '
b"-    _REGEX_TSMAP = re.compile(r'X-TIMESTAMP-MAP=')"
b"-    _REGEX_TSMAP_LOCAL = re.compile(r'LOCAL:')"
b"-    _REGEX_TSMAP_MPEGTS = re.compile(r'MPEGTS:([0-9]+)')"
b"-    _REGEX_TSMAP_SEP = re.compile(r'[ \\t]*,[ \\t]*')"
b"+    _REGEX_TSMAP = re.compile(ur'X-TIMESTAMP-MAP=')"
b"+    _REGEX_TSMAP_LOCAL = re.compile(ur'LOCAL:')"
b"+    _REGEX_TSMAP_MPEGTS = re.compile(ur'MPEGTS:([0-9]+)')"
b"+    _REGEX_TSMAP_SEP = re.compile(ur'[ \\t]*,[ \\t]*')"
b' '
b'     # This was removed from the spec in the 2017 revision;'
b'     # the last spec draft to describe this syntax element is'
b'     # <https://www.w3.org/TR/2015/WD-webvtt1-20151208/#webvtt-metadata-header>.'
b'     # Nevertheless, YouTube keeps serving those'
b"-    _REGEX_META = re.compile(r'(?:(?!-->)[^\\r\\n])+:(?:(?!-->)[^\\r\\n])+(?:\\r\\n|[\\r\\n])')"
b"+    _REGEX_META = re.compile(ur'(?:(?!-->)[^\\r\\n])+:(?:(?!-->)[^\\r\\n])+(?:\\r\\n|[\\r\\n])')"
b' '
b'     @classmethod'
b'     def __parse_tsmap(cls, parser):'
b'@@ -205,7 +207,7 @@'
b'             raise ParseError(parser)'
b' '
b'         extra = m.group(1)'
b"-        local, mpegts, meta = None, None, ''"
b"+        local, mpegts, meta = None, None, u''"
b'         while not parser.consume(_REGEX_NL):'
b'             if parser.consume(cls._REGEX_TSMAP):'
b'                 local, mpegts = cls.__parse_tsmap(parser)'
b'@@ -219,23 +221,23 @@'
b'         return cls(extra=extra, mpegts=mpegts, local=local, meta=meta)'
b' '
b'     def write_into(self, stream):'
b"-        stream.write('WEBVTT')"
b"+        stream.write(u'WEBVTT')"
b'         if self.extra is not None:'
b'             stream.write(self.extra)'
b"-        stream.write('\\n')"
b"+        stream.write(u'\\n')"
b'         if self.local or self.mpegts:'
b"-            stream.write('X-TIMESTAMP-MAP=LOCAL:')"
b"+            stream.write(u'X-TIMESTAMP-MAP=LOCAL:')"
b'             stream.write(_format_ts(self.local if self.local is not None else 0))'
b"-            stream.write(',MPEGTS:')"
b'-            stream.write(str(self.mpegts if self.mpegts is not None else 0))'
b"-            stream.write('\\n')"
b"+            stream.write(u',MPEGTS:')"
b'+            stream.write(unicode(self.mpegts if self.mpegts is not None else 0))'
b"+            stream.write(u'\\n')"
b'         if self.meta:'
b'             stream.write(self.meta)'
b"-        stream.write('\\n')"
b"+        stream.write(u'\\n')"
b' '
b' '
b' class StyleBlock(HeaderBlock):'
b"-    _REGEX = re.compile(r'''(?x)"
b"+    _REGEX = re.compile(ur'''(?x)"
b'         STYLE[\\ \\t]*(?:\\r\\n|[\\r\\n])'
b'         ((?:(?!-->)[^\\r\\n])+(?:\\r\\n|[\\r\\n]))*'
b'         (?:\\r\\n|[\\r\\n])'
b'@@ -243,7 +245,7 @@'
b' '
b' '
b' class RegionBlock(HeaderBlock):'
b"-    _REGEX = re.compile(r'''(?x)"
b"+    _REGEX = re.compile(ur'''(?x)"
b'         REGION[\\ \\t]*'
b'         ((?:(?!-->)[^\\r\\n])+(?:\\r\\n|[\\r\\n]))*'
b'         (?:\\r\\n|[\\r\\n])'
b'@@ -251,7 +253,7 @@'
b' '
b' '
b' class CommentBlock(Block):'
b"-    _REGEX = re.compile(r'''(?x)"
b"+    _REGEX = re.compile(ur'''(?x)"
b'         NOTE(?:\\r\\n|[\\ \\t\\r\\n])'
b'         ((?:(?!-->)[^\\r\\n])+(?:\\r\\n|[\\r\\n]))*'
b'         (?:\\r\\n|[\\r\\n])'
b'@@ -259,14 +261,14 @@'
b' '
b' '
b' class CueBlock(Block):'
b'-    """'
b'+    u"""'
b'     A cue block. The payload is not interpreted.'
b'     """'
b' '
b"-    _REGEX_ID = re.compile(r'((?:(?!-->)[^\\r\\n])+)(?:\\r\\n|[\\r\\n])')"
b"-    _REGEX_ARROW = re.compile(r'[ \\t]+-->[ \\t]+')"
b"-    _REGEX_SETTINGS = re.compile(r'[ \\t]+((?:(?!-->)[^\\r\\n])+)')"
b"-    _REGEX_PAYLOAD = re.compile(r'[^\\r\\n]+(?:\\r\\n|[\\r\\n])?')"
b"+    _REGEX_ID = re.compile(ur'((?:(?!-->)[^\\r\\n])+)(?:\\r\\n|[\\r\\n])')"
b"+    _REGEX_ARROW = re.compile(ur'[ \\t]+-->[ \\t]+')"
b"+    _REGEX_SETTINGS = re.compile(ur'[ \\t]+((?:(?!-->)[^\\r\\n])+)')"
b"+    _REGEX_PAYLOAD = re.compile(ur'[^\\r\\n]+(?:\\r\\n|[\\r\\n])?')"
b' '
b'     @classmethod'
b'     def parse(cls, parser):'
b'@@ -311,25 +313,25 @@'
b'     def write_into(self, stream):'
b'         if self.id is not None:'
b'             stream.write(self.id)'
b"-            stream.write('\\n')"
b"+            stream.write(u'\\n')"
b'         stream.write(_format_ts(self.start))'
b"-        stream.write(' --> ')"
b"+        stream.write(u' --> ')"
b'         stream.write(_format_ts(self.end))'
b'         if self.settings is not None:'
b"-            stream.write(' ')"
b"+            stream.write(u' ')"
b'             stream.write(self.settings)'
b"-        stream.write('\\n')"
b"+        stream.write(u'\\n')"
b'         stream.write(self.text)'
b"-        stream.write('\\n')"
b"+        stream.write(u'\\n')"
b' '
b'     @property'
b'     def as_json(self):'
b'         return {'
b"-            'id': self.id,"
b"-            'start': self.start,"
b"-            'end': self.end,"
b"-            'text': self.text,"
b"-            'settings': self.settings,"
b"+            u'id': self.id,"
b"+            u'start': self.start,"
b"+            u'end': self.end,"
b"+            u'text': self.text,"
b"+            u'settings': self.settings,"
b'         }'
b' '
b'     def __eq__(self, other):'
b'@@ -338,11 +340,11 @@'
b'     @classmethod'
b'     def from_json(cls, json):'
b'         return cls('
b"-            id=json['id'],"
b"-            start=json['start'],"
b"-            end=json['end'],"
b"-            text=json['text'],"
b"-            settings=json['settings'],"
b"+            id=json[u'id'],"
b"+            start=json[u'start'],"
b"+            end=json[u'end'],"
b"+            text=json[u'text'],"
b"+            settings=json[u'settings'],"
b'         )'
b' '
b'     def hinges(self, other):'
b'@@ -354,7 +356,7 @@'
b' '
b' '
b' def parse_fragment(frag_content):'
b'-    """'
b'+    u"""'
b'     A generator that yields (partially) parsed WebVTT blocks when given'
b'     a bytes object containing the raw contents of a WebVTT file.'
b'     """'
