# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from ._base import YoutubeBaseInfoExtractor
from ...utils import ExtractorError


class YoutubeTruncatedURLIE(YoutubeBaseInfoExtractor):
    IE_NAME = u'youtube:truncated_url'
    IE_DESC = False  # Do not list
    _VALID_URL = ur'''(?x)
        (?:https?://)?
        (?:\w+\.)?[yY][oO][uU][tT][uU][bB][eE](?:-nocookie)?\.com/
        (?:watch\?(?:
            feature=[a-z_]+|
            annotation_id=annotation_[^&]+|
            x-yt-cl=[0-9]+|
            hl=[^&]*|
            t=[0-9]+
        )?
        |
            attribution_link\?a=[^&]+
        )
        $
    '''

    _TESTS = [{
        u'url': u'https://www.youtube.com/watch?annotation_id=annotation_3951667041',
        u'only_matching': True,
    }, {
        u'url': u'https://www.youtube.com/watch?',
        u'only_matching': True,
    }, {
        u'url': u'https://www.youtube.com/watch?x-yt-cl=84503534',
        u'only_matching': True,
    }, {
        u'url': u'https://www.youtube.com/watch?feature=foo',
        u'only_matching': True,
    }, {
        u'url': u'https://www.youtube.com/watch?hl=en-GB',
        u'only_matching': True,
    }, {
        u'url': u'https://www.youtube.com/watch?t=2372',
        u'only_matching': True,
    }]

    def _real_extract(self, url):
        raise ExtractorError(
            u'Did you forget to quote the URL? Remember that & is a meta '
            u'character in most shells, so you want to put the URL in quotes, '
            u'like  yt-dlp '
            u'"https://www.youtube.com/watch?feature=foo&v=BaW_jenozKc" '
            u' or simply  yt-dlp BaW_jenozKc  .',
            expected=True)


class YoutubeTruncatedIDIE(YoutubeBaseInfoExtractor):
    IE_NAME = u'youtube:truncated_id'
    IE_DESC = False  # Do not list
    _VALID_URL = ur'https?://(?:www\.)?youtube\.com/watch\?v=(?P<id>[0-9A-Za-z_-]{1,10})$'

    _TESTS = [{
        u'url': u'https://www.youtube.com/watch?v=N_708QY7Ob',
        u'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        raise ExtractorError(
            u'Incomplete YouTube ID {0}. URL {1} looks truncated.'.format(video_id, url),
            expected=True)
