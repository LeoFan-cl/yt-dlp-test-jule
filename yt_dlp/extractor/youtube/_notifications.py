# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import itertools
import re

from ._tab import YoutubeTabBaseInfoExtractor, YoutubeTabIE
from ._video import YoutubeIE
from ...utils import traverse_obj


class YoutubeNotificationsIE(YoutubeTabBaseInfoExtractor):
    IE_NAME = u'youtube:notif'
    IE_DESC = u'YouTube notifications; ":ytnotif" keyword (requires cookies)'
    _VALID_URL = ur':ytnotif(?:ication)?s?'
    _LOGIN_REQUIRED = True
    _TESTS = [{
        u'url': u':ytnotif',
        u'only_matching': True,
    }, {
        u'url': u':ytnotifications',
        u'only_matching': True,
    }]

    def _extract_notification_menu(self, response, continuation_list):
        notification_list = traverse_obj(
            response,
            (u'actions', 0, u'openPopupAction', u'popup', u'multiPageMenuRenderer', u'sections', 0, u'multiPageMenuNotificationSectionRenderer', u'items'),
            (u'actions', 0, u'appendContinuationItemsAction', u'continuationItems'),
            expected_type=list) or []
        continuation_list[0] = None
        for item in notification_list:
            entry = self._extract_notification_renderer(item.get(u'notificationRenderer'))
            if entry:
                yield entry
            continuation = item.get(u'continuationItemRenderer')
            if continuation:
                continuation_list[0] = continuation

    def _extract_notification_renderer(self, notification):
        video_id = traverse_obj(
            notification, (u'navigationEndpoint', u'watchEndpoint', u'videoId'), expected_type=unicode)
        url = u'https://www.youtube.com/watch?v={0}'.format(video_id)
        channel_id = None
        if not video_id:
            browse_ep = traverse_obj(
                notification, (u'navigationEndpoint', u'browseEndpoint'), expected_type=dict)
            channel_id = self.ucid_or_none(traverse_obj(browse_ep, u'browseId', expected_type=unicode))
            post_id = self._search_regex(
                ur'/post/(.+)', traverse_obj(browse_ep, u'canonicalBaseUrl', expected_type=unicode),
                u'post id', default=None)
            if not channel_id or not post_id:
                return
            # The direct /post url redirects to this in the browser
            url = u'https://www.youtube.com/channel/{0}/community?lb={1}'.format(channel_id, post_id)

        channel = traverse_obj(
            notification, (u'contextualMenu', u'menuRenderer', u'items', 1, u'menuServiceItemRenderer', u'text', u'runs', 1, u'text'),
            expected_type=unicode)
        notification_title = self._get_text(notification, u'shortMessage')
        if notification_title:
            notification_title = notification_title.replace(u'\xad', u'')  # remove soft hyphens
        # TODO: handle recommended videos
        title = self._search_regex(
            ur'{0}[^:]+: (.+)'.format(re.escape(channel or u"")), notification_title,
            u'video title', default=None)
        timestamp = (self._parse_time_text(self._get_text(notification, u'sentTimeText'))
                     if self._configuration_arg(u'approximate_date', ie_key=YoutubeTabIE)
                     else None)
        return {
            u'_type': u'url',
            u'url': url,
            u'ie_key': (YoutubeIE if video_id else YoutubeTabIE).ie_key(),
            u'video_id': video_id,
            u'title': title,
            u'channel_id': channel_id,
            u'channel': channel,
            u'uploader': channel,
            u'thumbnails': self._extract_thumbnails(notification, u'videoThumbnail'),
            u'timestamp': timestamp,
        }

    def _notification_menu_entries(self, ytcfg):
        continuation_list = [None]
        response = None
        for page in itertools.count(1):
            ctoken = traverse_obj(
                continuation_list, (0, u'continuationEndpoint', u'getNotificationMenuEndpoint', u'ctoken'), expected_type=unicode)
            response = self._extract_response(
                item_id=u'page {0}'.format(page), query={u'ctoken': ctoken} if ctoken else {}, ytcfg=ytcfg,
                ep=u'notification/get_notification_menu', check_get_keys=u'actions',
                headers=self.generate_api_headers(ytcfg=ytcfg, visitor_data=self._extract_visitor_data(response)))
            for item in self._extract_notification_menu(response, continuation_list):
                yield item
            if not continuation_list[0]:
                break

    def _real_extract(self, url):
        display_id = u'notifications'
        ytcfg = self._download_ytcfg(u'web', display_id) if not self.skip_webpage else {}
        self._report_playlist_authcheck(ytcfg)
        return self.playlist_result(self._notification_menu_entries(ytcfg), display_id, display_id)
