# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from ._tab import YoutubeTabBaseInfoExtractor
from ..common import SearchInfoExtractor
from ...utils import join_nonempty, parse_qs
from ...compat._legacy import compat_urllib_parse as urllib_parse


class YoutubeSearchIE(YoutubeTabBaseInfoExtractor, SearchInfoExtractor):
    IE_DESC = u'YouTube search'
    IE_NAME = u'youtube:search'
    _SEARCH_KEY = u'ytsearch'
    _SEARCH_PARAMS = u'EgIQAfABAQ=='  # Videos only
    _TESTS = [{
        u'url': u'ytsearch5:youtube-dl test video',
        u'playlist_count': 5,
        u'info_dict': {
            u'id': u'youtube-dl test video',
            u'title': u'youtube-dl test video',
        },
    }, {
        u'note': u'Suicide/self-harm search warning',
        u'url': u'ytsearch1:i hate myself and i wanna die',
        u'playlist_count': 1,
        u'info_dict': {
            u'id': u'i hate myself and i wanna die',
            u'title': u'i hate myself and i wanna die',
        },
    }]


class YoutubeSearchDateIE(YoutubeTabBaseInfoExtractor, SearchInfoExtractor):
    IE_NAME = YoutubeSearchIE.IE_NAME + u':date'
    _SEARCH_KEY = u'ytsearchdate'
    IE_DESC = u'YouTube search, newest videos first'
    _SEARCH_PARAMS = u'CAISAhAB8AEB'  # Videos only, sorted by date
    _TESTS = [{
        u'url': u'ytsearchdate5:youtube-dl test video',
        u'playlist_count': 5,
        u'info_dict': {
            u'id': u'youtube-dl test video',
            u'title': u'youtube-dl test video',
        },
    }]


class YoutubeSearchURLIE(YoutubeTabBaseInfoExtractor):
    IE_DESC = u'YouTube search URLs with sorting and filter support'
    IE_NAME = YoutubeSearchIE.IE_NAME + u'_url'
    _VALID_URL = ur'https?://(?:www\.)?youtube\.com/(?:results|search)\?([^#]+&)?(?:search_query|q)=(?:[^&]+)(?:[&#]|$)'
    _TESTS = [{
        u'url': u'https://www.youtube.com/results?baz=bar&search_query=youtube-dl+test+video&filters=video&lclk=video',
        u'playlist_mincount': 5,
        u'info_dict': {
            u'id': u'youtube-dl test video',
            u'title': u'youtube-dl test video',
        },
    }, {
        u'url': u'https://www.youtube.com/results?search_query=python&sp=EgIQAg%253D%253D',
        u'playlist_mincount': 5,
        u'info_dict': {
            u'id': u'python',
            u'title': u'python',
        },
    }, {
        u'url': u'https://www.youtube.com/results?search_query=%23cats',
        u'playlist_mincount': 1,
        u'info_dict': {
            u'id': u'#cats',
            u'title': u'#cats',
            # The test suite does not have support for nested playlists
            # 'entries': [{
            #     'url': r're:https://(www\.)?youtube\.com/hashtag/cats',
            #     'title': '#cats',
            # }],
        },
    }, {
        # Channel results
        u'url': u'https://www.youtube.com/results?search_query=kurzgesagt&sp=EgIQAg%253D%253D',
        u'info_dict': {
            u'id': u'kurzgesagt',
            u'title': u'kurzgesagt',
        },
        u'playlist': [{
            u'info_dict': {
                u'_type': u'url',
                u'id': u'UCsXVk37bltHxD1rDPwtNM8Q',
                u'url': u'https://www.youtube.com/channel/UCsXVk37bltHxD1rDPwtNM8Q',
                u'ie_key': u'YoutubeTab',
                u'channel': u'Kurzgesagt – In a Nutshell',
                u'description': u'md5:4ae48dfa9505ffc307dad26342d06bfc',
                u'title': u'Kurzgesagt – In a Nutshell',
                u'channel_id': u'UCsXVk37bltHxD1rDPwtNM8Q',
                # No longer available for search as it is set to the handle.
                # 'playlist_count': int,
                u'channel_url': u'https://www.youtube.com/channel/UCsXVk37bltHxD1rDPwtNM8Q',
                u'thumbnails': list,
                u'uploader_id': u'@kurzgesagt',
                u'uploader_url': u'https://www.youtube.com/@kurzgesagt',
                u'uploader': u'Kurzgesagt – In a Nutshell',
                u'channel_is_verified': True,
                u'channel_follower_count': int,
            },
        }],
        u'params': {u'extract_flat': True, u'playlist_items': u'1'},
        u'playlist_mincount': 1,
    }, {
        u'url': u'https://www.youtube.com/results?q=test&sp=EgQIBBgB',
        u'only_matching': True,
    }]

    def _real_extract(self, url):
        qs = parse_qs(url)
        query = (qs.get(u'search_query') or qs.get(u'q'))[0]
        return self.playlist_result(self._search_results(query, qs.get(u'sp', (None,))[0]), query, query)


class YoutubeMusicSearchURLIE(YoutubeTabBaseInfoExtractor):
    IE_DESC = u'YouTube music search URLs with selectable sections, e.g. #songs'
    IE_NAME = u'youtube:music:search_url'
    _VALID_URL = ur'https?://music\.youtube\.com/search\?([^#]+&)?(?:search_query|q)=(?:[^&]+)(?:[&#]|$)'
    _TESTS = [{
        u'url': u'https://music.youtube.com/search?q=royalty+free+music',
        u'playlist_count': 16,
        u'info_dict': {
            u'id': u'royalty free music',
            u'title': u'royalty free music',
        },
    }, {
        u'url': u'https://music.youtube.com/search?q=royalty+free+music&sp=EgWKAQIIAWoKEAoQAxAEEAkQBQ%3D%3D',
        u'playlist_mincount': 30,
        u'info_dict': {
            u'id': u'royalty free music - songs',
            u'title': u'royalty free music - songs',
        },
        u'params': {u'extract_flat': u'in_playlist'},
    }, {
        u'url': u'https://music.youtube.com/search?q=royalty+free+music#community+playlists',
        u'playlist_mincount': 30,
        u'info_dict': {
            u'id': u'royalty free music - community playlists',
            u'title': u'royalty free music - community playlists',
        },
        u'params': {u'extract_flat': u'in_playlist'},
    }]

    _SECTIONS = {
        u'albums': u'EgWKAQIYAWoKEAoQAxAEEAkQBQ==',
        u'artists': u'EgWKAQIgAWoKEAoQAxAEEAkQBQ==',
        u'community playlists': u'EgeKAQQoAEABagoQChADEAQQCRAF',
        u'featured playlists': u'EgeKAQQoADgBagwQAxAJEAQQDhAKEAU==',
        u'songs': u'EgWKAQIIAWoKEAoQAxAEEAkQBQ==',
        u'videos': u'EgWKAQIQAWoKEAoQAxAEEAkQBQ==',
    }

    def _real_extract(self, url):
        qs = parse_qs(url)
        query = (qs.get(u'search_query') or qs.get(u'q'))[0]
        params = qs.get(u'sp', (None,))[0]
        if params:
            section = (k for k, v in self._SECTIONS.items() if v == params), params.next()
        else:
            section = urllib_parse.unquote_plus((url.split(u'#') + [u''])[1]).lower()
            params = self._SECTIONS.get(section)
            if not params:
                section = None
        title = join_nonempty(query, section, delim=u' - ')
        return self.playlist_result(self._search_results(query, params, default_client=u'web_music'), title, title)
