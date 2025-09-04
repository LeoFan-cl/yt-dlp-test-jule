# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from ._tab import YoutubeTabBaseInfoExtractor
from ._video import YoutubeIE
from ...utils import ExtractorError, traverse_obj


class YoutubeClipIE(YoutubeTabBaseInfoExtractor):
    IE_NAME = u'youtube:clip'
    _VALID_URL = ur'https?://(?:www\.)?youtube\.com/clip/(?P<id>[^/?#]+)'
    _TESTS = [{
        # FIXME: Other metadata should be extracted from the clip, not from the base video
        u'url': u'https://www.youtube.com/clip/UgytZKpehg-hEMBSn3F4AaABCQ',
        u'info_dict': {
            u'id': u'UgytZKpehg-hEMBSn3F4AaABCQ',
            u'ext': u'mp4',
            u'section_start': 29.0,
            u'section_end': 39.7,
            u'duration': 10.7,
            u'age_limit': 0,
            u'availability': u'public',
            u'categories': [u'Gaming'],
            u'channel': u'Scott The Woz',
            u'channel_id': u'UC4rqhyiTs7XyuODcECvuiiQ',
            u'channel_url': u'https://www.youtube.com/channel/UC4rqhyiTs7XyuODcECvuiiQ',
            u'description': u'md5:7a4517a17ea9b4bd98996399d8bb36e7',
            u'like_count': int,
            u'playable_in_embed': True,
            u'tags': u'count:17',
            u'thumbnail': u'https://i.ytimg.com/vi_webp/ScPX26pdQik/maxresdefault.webp',
            u'title': u'Mobile Games on Console - Scott The Woz',
            u'upload_date': u'20210920',
            u'uploader': u'Scott The Woz',
            u'uploader_id': u'@ScottTheWoz',
            u'uploader_url': u'https://www.youtube.com/@ScottTheWoz',
            u'view_count': int,
            u'live_status': u'not_live',
            u'channel_follower_count': int,
            u'chapters': u'count:20',
            u'comment_count': int,
            u'heatmap': u'count:100',
            u'media_type': u'clip',
        },
    }]

    def _real_extract(self, url):
        clip_id = self._match_id(url)
        _, data = self._extract_webpage(url, clip_id)

        video_id = traverse_obj(data, (u'currentVideoEndpoint', u'watchEndpoint', u'videoId'))
        if not video_id:
            raise ExtractorError(u'Unable to find video ID')

        clip_data = traverse_obj(data, (
            u'engagementPanels', ..., u'engagementPanelSectionListRenderer', u'content', u'clipSectionRenderer',
            u'contents', ..., u'clipAttributionRenderer', u'onScrubExit', u'commandExecutorCommand', u'commands', ...,
            u'openPopupAction', u'popup', u'notificationActionRenderer', u'actionButton', u'buttonRenderer', u'command',
            u'commandExecutorCommand', u'commands', ..., u'loopCommand'), get_all=False)

        return {
            u'_type': u'url_transparent',
            u'url': u'https://www.youtube.com/watch?v={0}'.format(video_id),
            u'ie_key': YoutubeIE.ie_key(),
            u'id': clip_id,
            u'media_type': u'clip',
            u'section_start': int(clip_data[u'startTimeMs']) / 1000,
            u'section_end': int(clip_data[u'endTimeMs']) / 1000,
            u'_format_sort_fields': (
                u'proto:https', u'quality', u'res', u'fps', u'hdr:12', u'source', u'vcodec', u'channels', u'acodec', u'lang'),
        }
