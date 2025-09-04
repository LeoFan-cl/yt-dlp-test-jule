# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import base64

from ._base import YoutubeBaseInfoExtractor
from ._tab import YoutubeTabIE
from ...utils import ExtractorError, classproperty, parse_qs, update_url_query, url_or_none
from ...compat._legacy import compat_urllib_parse as urllib_parse


class YoutubeYtBeIE(YoutubeBaseInfoExtractor):
    IE_DESC = u'youtu.be'
    _VALID_URL = ur'https?://youtu\.be/(?P<id>[0-9A-Za-z_-]{11})/*?.*?\blist=(?P<playlist_id>{0})'.format(YoutubeBaseInfoExtractor._PLAYLIST_ID_RE)
    _TESTS = [{
        u'url': u'https://youtu.be/yeWKywCrFtk?list=PL2qgrgXsNUG5ig9cat4ohreBjYLAPC0J5',
        u'info_dict': {
            u'id': u'yeWKywCrFtk',
            u'ext': u'mp4',
            u'title': u'Small Scale Baler and Braiding Rugs',
            u'uploader': u'Backus-Page House Museum',
            u'uploader_id': u'@backuspagemuseum',
            u'uploader_url': ur're:https?://(?:www\.)?youtube\.com/@backuspagemuseum',
            u'upload_date': u'20161008',
            u'description': u'md5:800c0c78d5eb128500bffd4f0b4f2e8a',
            u'categories': [u'Nonprofits & Activism'],
            u'tags': list,
            u'like_count': int,
            u'age_limit': 0,
            u'playable_in_embed': True,
            u'thumbnail': ur're:^https?://.*\.webp',
            u'channel': u'Backus-Page House Museum',
            u'channel_id': u'UCEfMCQ9bs3tjvjy1s451zaw',
            u'live_status': u'not_live',
            u'view_count': int,
            u'channel_url': u'https://www.youtube.com/channel/UCEfMCQ9bs3tjvjy1s451zaw',
            u'availability': u'public',
            u'duration': 59,
            u'comment_count': int,
            u'channel_follower_count': int,
            u'media_type': u'short',
        },
        u'params': {
            u'noplaylist': True,
            u'skip_download': True,
        },
    }, {
        u'url': u'https://youtu.be/uWyaPkt-VOI?list=PL9D9FC436B881BA21',
        u'only_matching': True,
    }]

    def _real_extract(self, url):
        mobj = self._match_valid_url(url)
        video_id = mobj.group(u'id')
        playlist_id = mobj.group(u'playlist_id')
        return self.url_result(
            update_url_query(u'https://www.youtube.com/watch', {
                u'v': video_id,
                u'list': playlist_id,
                u'feature': u'youtu.be',
            }), ie=YoutubeTabIE.ie_key(), video_id=playlist_id)


class YoutubeLivestreamEmbedIE(YoutubeBaseInfoExtractor):
    IE_DESC = u'YouTube livestream embeds'
    _VALID_URL = ur'https?://(?:\w+\.)?youtube\.com/embed/live_stream/?\?(?:[^#]+&)?channel=(?P<id>[^&#]+)'
    _TESTS = [{
        u'url': u'https://www.youtube.com/embed/live_stream?channel=UC2_KI6RB__jGdlnK6dvFEZA',
        u'only_matching': True,
    }]

    def _real_extract(self, url):
        channel_id = self._match_id(url)
        return self.url_result(
            u'https://www.youtube.com/channel/{0}/live'.format(channel_id),
            ie=YoutubeTabIE.ie_key(), video_id=channel_id)


class YoutubeYtUserIE(YoutubeBaseInfoExtractor):
    IE_DESC = u'YouTube user videos; "ytuser:" prefix'
    IE_NAME = u'youtube:user'
    _VALID_URL = ur'ytuser:(?P<id>.+)'
    _TESTS = [{
        u'url': u'ytuser:phihag',
        u'only_matching': True,
    }]

    def _real_extract(self, url):
        user_id = self._match_id(url)
        return self.url_result(u'https://www.youtube.com/user/{0}'.format(user_id), YoutubeTabIE, user_id)


class YoutubeFavouritesIE(YoutubeBaseInfoExtractor):
    IE_NAME = u'youtube:favorites'
    IE_DESC = u'YouTube liked videos; ":ytfav" keyword (requires cookies)'
    _VALID_URL = ur':ytfav(?:ou?rite)?s?'
    _LOGIN_REQUIRED = True
    _TESTS = [{
        u'url': u':ytfav',
        u'only_matching': True,
    }, {
        u'url': u':ytfavorites',
        u'only_matching': True,
    }]

    def _real_extract(self, url):
        return self.url_result(
            u'https://www.youtube.com/playlist?list=LL',
            ie=YoutubeTabIE.ie_key())


class YoutubeFeedsInfoExtractor(YoutubeBaseInfoExtractor):
    u"""
    Base class for feed extractors
    Subclasses must re-define the _FEED_NAME property.
    """
    _LOGIN_REQUIRED = True
    _FEED_NAME = u'feeds'

    @classproperty
    def IE_NAME(cls):
        return u'youtube:{0}'.format(cls._FEED_NAME)

    def _real_extract(self, url):
        return self.url_result(
            u'https://www.youtube.com/feed/{0}'.format(self._FEED_NAME), ie=YoutubeTabIE.ie_key())


class YoutubeWatchLaterIE(YoutubeBaseInfoExtractor):
    IE_NAME = u'youtube:watchlater'
    IE_DESC = u'Youtube watch later list; ":ytwatchlater" keyword (requires cookies)'
    _VALID_URL = ur':ytwatchlater'
    _TESTS = [{
        u'url': u':ytwatchlater',
        u'only_matching': True,
    }]

    def _real_extract(self, url):
        return self.url_result(
            u'https://www.youtube.com/playlist?list=WL', ie=YoutubeTabIE.ie_key())


class YoutubeRecommendedIE(YoutubeFeedsInfoExtractor):
    IE_DESC = u'YouTube recommended videos; ":ytrec" keyword'
    _VALID_URL = ur'https?://(?:www\.)?youtube\.com/?(?:[?#]|$)|:ytrec(?:ommended)?'
    _FEED_NAME = u'recommended'
    _LOGIN_REQUIRED = False
    _TESTS = [{
        u'url': u':ytrec',
        u'only_matching': True,
    }, {
        u'url': u':ytrecommended',
        u'only_matching': True,
    }, {
        u'url': u'https://youtube.com',
        u'only_matching': True,
    }]


class YoutubeSubscriptionsIE(YoutubeFeedsInfoExtractor):
    IE_DESC = u'YouTube subscriptions feed; ":ytsubs" keyword (requires cookies)'
    _VALID_URL = ur':ytsub(?:scription)?s?'
    _FEED_NAME = u'subscriptions'
    _TESTS = [{
        u'url': u':ytsubs',
        u'only_matching': True,
    }, {
        u'url': u':ytsubscriptions',
        u'only_matching': True,
    }]


class YoutubeHistoryIE(YoutubeFeedsInfoExtractor):
    IE_DESC = u'Youtube watch history; ":ythis" keyword (requires cookies)'
    _VALID_URL = ur':ythis(?:tory)?'
    _FEED_NAME = u'history'
    _TESTS = [{
        u'url': u':ythistory',
        u'only_matching': True,
    }]


class YoutubeShortsAudioPivotIE(YoutubeBaseInfoExtractor):
    IE_DESC = u'YouTube Shorts audio pivot (Shorts using audio of a given video)'
    IE_NAME = u'youtube:shorts:pivot:audio'
    _VALID_URL = ur'https?://(?:www\.)?youtube\.com/source/(?P<id>[\w-]{11})/shorts'
    _TESTS = [{
        u'url': u'https://www.youtube.com/source/Lyj-MZSAA9o/shorts',
        u'only_matching': True,
    }]

    @staticmethod
    def _generate_audio_pivot_params(video_id):
        u"""
        Generates sfv_audio_pivot browse params for this video id
        """
        pb_params = '\xf2\x05+\n)\x12\'\n\x0b%b\x12\x0b%b\x1a\x0b%b' % ((video_id.encode(),) * 3)
        return urllib_parse.quote(base64.b64encode(pb_params).decode())

    def _real_extract(self, url):
        video_id = self._match_id(url)
        return self.url_result(
            u'https://www.youtube.com/feed/sfv_audio_pivot?bp={0}'.format(self._generate_audio_pivot_params(video_id)),
            ie=YoutubeTabIE)


class YoutubeConsentRedirectIE(YoutubeBaseInfoExtractor):
    IE_NAME = u'youtube:consent'
    IE_DESC = False  # Do not list
    _VALID_URL = ur'https?://consent\.youtube\.com/m\?'
    _TESTS = [{
        u'url': u'https://consent.youtube.com/m?continue=https%3A%2F%2Fwww.youtube.com%2Flive%2FqVv6vCqciTM%3Fcbrd%3D1&gl=NL&m=0&pc=yt&hl=en&src=1',
        u'info_dict': {
            u'id': u'qVv6vCqciTM',
            u'ext': u'mp4',
            u'age_limit': 0,
            u'uploader_id': u'@sana_natori',
            u'comment_count': int,
            u'chapters': u'count:13',
            u'upload_date': u'20221223',
            u'thumbnail': u'https://i.ytimg.com/vi/qVv6vCqciTM/maxresdefault.jpg',
            u'channel_url': u'https://www.youtube.com/channel/UCIdEIHpS0TdkqRkHL5OkLtA',
            u'uploader_url': u'https://www.youtube.com/@sana_natori',
            u'like_count': int,
            u'release_date': u'20221223',
            u'tags': [u'Vtuber', u'月ノ美兎', u'名取さな', u'にじさんじ', u'クリスマス', u'3D配信'],
            u'title': u'【 #インターネット女クリスマス 】3Dで歌ってはしゃぐインターネットの女たち【月ノ美兎/名取さな】',
            u'view_count': int,
            u'playable_in_embed': True,
            u'duration': 4438,
            u'availability': u'public',
            u'channel_follower_count': int,
            u'channel_id': u'UCIdEIHpS0TdkqRkHL5OkLtA',
            u'categories': [u'Entertainment'],
            u'live_status': u'was_live',
            u'release_timestamp': 1671793345,
            u'channel': u'さなちゃんねる',
            u'description': u'md5:6aebf95cc4a1d731aebc01ad6cc9806d',
            u'uploader': u'さなちゃんねる',
            u'channel_is_verified': True,
            u'heatmap': u'count:100',
        },
        u'add_ie': [u'Youtube'],
        u'params': {u'skip_download': u'Youtube'},
    }]

    def _real_extract(self, url):
        redirect_url = url_or_none(parse_qs(url).get(u'continue', [None])[-1])
        if not redirect_url:
            raise ExtractorError(u'Invalid cookie consent redirect URL', expected=True)
        return self.url_result(redirect_url)
