from __future__ import absolute_import
import re

from .common import PostProcessor
from ..utils import (
    PostProcessingError,
    traverse_obj,
)


class MetadataParserPP(PostProcessor):
    def __init__(self, downloader, actions):
        super(MetadataParserPP, self).__init__(downloader)
        self._actions = []
        for f in actions:
            action = f[0]
            args = f[1:]
            assert action in self.Actions
            self._actions.append(action(self, *args))

    @classmethod
    def validate_action(cls, action, *data):
        u"""Each action can be:
                (Actions.INTERPRET, from, to) OR
                (Actions.REPLACE, field, search, replace)
        """
        assert action in cls.Actions
        assert len(data) == cls.Actions(action).value

    @staticmethod
    def field_to_template(tmpl):
        if re.match(ur'[a-zA-Z_]+$', tmpl):
            return u'%({tmpl})s'.format(tmpl=tmpl)

        from ..YoutubeDL import YoutubeDL
        return YoutubeDL.escape_outtmpl(tmpl)

    @staticmethod
    def format_to_regex(fmt):
        ur"""
        Converts a string like
           '%(title)s - %(artist)s'
        to a regex like
           '(?P<title>.+)\ \-\ (?P<artist>.+)'
        """
        if not re.search(ur'%\\(\\w+\\)s', fmt):
            return fmt
        lastpos = 0
        regex = u''
        # replace %(..)s with regex group and escape other string parts
        for match in re.finditer(ur'%\\((\\w+)\\)s', fmt):
            regex += re.escape(fmt[lastpos:match.start()])
            regex += ur'(?P<{group}>.+)'.format(group=match.group(1))
            lastpos = match.end()
        regex += re.escape(fmt[lastpos:])
        return regex

    def run(self, info):
        for action in self._actions:
            action(info)
        return [], info

    class Actions:
        class INTERPRET:
            value = 2
            def __init__(self, pp, outtmpl, intmpl):
                self.pp = pp
                self.outtmpl = pp.field_to_template(outtmpl)
                self.regex = pp.format_to_regex(intmpl)

            def __call__(self, info):
                match = re.match(self.regex, self.pp.get_param('from', info))
                if match is None:
                    self.pp.report_warning('could not interpret "%s" as "%s"' % (
                        self.pp.get_param('from', info), self.pp.get_param('to', info)))
                    return
                for key, value in match.groupdict().items():
                    info[key] = value

        class REPLACE:
            value = 3
            def __init__(self, pp, field, search, replace):
                self.pp, self.field, self.search, self.replace = pp, field, search, replace

            def __call__(self, info):
                val = traverse_obj(info, self.field, casesense=False)
                if val is None:
                    self.pp.to_screen('Video does not have a %s' % self.field)
                    return
                elif not isinstance(val, (str, unicode)):
                    self.pp.report_warning('Cannot replace in field %s since it is a %s' % (
                        self.field, type(val).__name__))
                    return
                self.pp.write_debug('Replacing all %r in %s with %r' % (
                    self.search, self.field, self.replace))
                info[self.field] = val.replace(self.search, self.replace)


class MetadataFromFieldPP(MetadataParserPP):
    @classmethod
    def to_action(cls, f):
        match = re.match(ur'(?s)(?P<in>.*?)(?<!\\):(?P<out>.+)$', f)
        if match is None:
            raise ValueError('it should be FROM:TO, not %r' % f)
        return (
            cls.Actions.INTERPRET,
            match.group(u'in').replace(u'\\:', u':'),
            match.group(u'out'),
        )

    def __init__(self, downloader, formats):
        super(MetadataFromFieldPP, self).__init__(downloader, [self.to_action(f) for f in formats])


# Deprecated
class MetadataFromTitlePP(MetadataParserPP):
    def __init__(self, downloader, titleformat):
        super(MetadataFromTitlePP, self).__init__(downloader, [(self.Actions.INTERPRET, u'title', titleformat)])
        self.deprecation_warning(
            u'yt_dlp.postprocessor.MetadataFromTitlePP is deprecated '
            u'and may be removed in a future version. Use yt_dlp.postprocessor.MetadataFromFieldPP instead')
