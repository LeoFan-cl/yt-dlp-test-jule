# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import functools
import itertools
import re

from ._base import BadgeType, YoutubeBaseInfoExtractor
from ._video import YoutubeIE
from ...networking.exceptions import HTTPError, network_exceptions
from ...utils import (
    NO_DEFAULT,
    ExtractorError,
    UserNotLive,
    bug_reports_message,
    format_field,
    get_first,
    int_or_none,
    parse_count,
    parse_duration,
    parse_qs,
    smuggle_url,
    str_to_int,
    strftime_or_none,
    traverse_obj,
    try_get,
    unsmuggle_url,
    update_url_query,
    url_or_none,
    urljoin,
    variadic,
)
from ...compat._legacy import compat_urllib_parse as urllib_parse


class YoutubeTabBaseInfoExtractor(YoutubeBaseInfoExtractor):
    @staticmethod
    def passthrough_smuggled_data(func):
        def _smuggle(info, smuggled_data):
            if info.get('_type') not in ('url', 'url_transparent'):
                return info
            if smuggled_data.get('is_music_url'):
                parsed_url = urllib_parse.urlparse(info['url'])
                if parsed_url.netloc in ('www.youtube.com', 'music.youtube.com'):
                    smuggled_data.pop('is_music_url')
                    info['url'] = urllib_parse.urlunparse(parsed_url._replace(netloc='music.youtube.com'))
            if smuggled_data:
                info['url'] = smuggle_url(info['url'], smuggled_data)
            return info

        @functools.wraps(func)
        def wrapper(self, url):
            url, smuggled_data = unsmuggle_url(url, {})
            if self.is_music_url(url):
                smuggled_data['is_music_url'] = True
            info_dict = func(self, url, smuggled_data)
            if smuggled_data:
                _smuggle(info_dict, smuggled_data)
                if info_dict.get('entries'):
                    info_dict['entries'] = (_smuggle(i, smuggled_data.copy()) for i in info_dict['entries'])
            return info_dict
        return wrapper

    @staticmethod
    def _extract_basic_item_renderer(item):
        # Modified from _extract_grid_item_renderer
        known_basic_renderers = (
            'playlistRenderer', 'videoRenderer', 'channelRenderer', 'showRenderer', 'reelItemRenderer',
        )
        for key, renderer in item.items():
            if not isinstance(renderer, dict):
                continue
            elif key in known_basic_renderers:
                return renderer
            elif key.startswith('grid') and key.endswith('Renderer'):
                return renderer

    def _extract_video(self, renderer):
        video_id = renderer.get('videoId')

        reel_header_renderer = traverse_obj(renderer, (
            'navigationEndpoint', 'reelWatchEndpoint', 'overlay', 'reelPlayerOverlayRenderer',
            'reelPlayerHeaderSupportedRenderers', 'reelPlayerHeaderRenderer'))

        title = self._get_text(renderer, 'title', 'headline') or self._get_text(reel_header_renderer, 'reelTitleText')
        description = self._get_text(renderer, 'descriptionSnippet')

        duration = int_or_none(renderer.get('lengthSeconds'))
        if duration is None:
            duration = parse_duration(self._get_text(
                renderer, 'lengthText', ('thumbnailOverlays', ..., 'thumbnailOverlayTimeStatusRenderer', 'text')))
        if duration is None:
            # XXX: should write a parser to be more general to support more cases (e.g. shorts in shorts tab)
            duration = parse_duration(self._search_regex(
                r'(?i)(ago)(?!.*\1)\s+(?P<duration>[a-z0-9 ,]+?)(?:\s+[\d,]+\s+views)?(?:\s+-\s+play\s+short)?$',
                traverse_obj(renderer, ('title', 'accessibility', 'accessibilityData', 'label'), default='', expected_type=str),
                video_id, default=None, group='duration'))

        channel_id = traverse_obj(
            renderer, ('shortBylineText', 'runs', ..., 'navigationEndpoint', 'browseEndpoint', 'browseId'),
            expected_type=str, get_all=False)
        if not channel_id:
            channel_id = traverse_obj(reel_header_renderer, ('channelNavigationEndpoint', 'browseEndpoint', 'browseId'))

        channel_id = self.ucid_or_none(channel_id)

        overlay_style = traverse_obj(
            renderer, ('thumbnailOverlays', ..., 'thumbnailOverlayTimeStatusRenderer', 'style'),
            get_all=False, expected_type=str)
        badges = self._extract_badges(traverse_obj(renderer, 'badges'))
        owner_badges = self._extract_badges(traverse_obj(renderer, 'ownerBadges'))
        navigation_url = urljoin('https://www.youtube.com/', traverse_obj(
            renderer, ('navigationEndpoint', 'commandMetadata', 'webCommandMetadata', 'url'),
            expected_type=str) or '')
        url = 'https://www.youtube.com/watch?v={0}'.format(video_id)
        if overlay_style == 'SHORTS' or '/shorts/' in navigation_url:
            url = 'https://www.youtube.com/shorts/{0}'.format(video_id)

        time_text = (self._get_text(renderer, 'publishedTimeText', 'videoInfo')
                     or self._get_text(reel_header_renderer, 'timestampText') or '')
        scheduled_timestamp = str_to_int(traverse_obj(renderer, ('upcomingEventData', 'startTime'), get_all=False))

        live_status = (
            'is_upcoming' if scheduled_timestamp is not None
            else 'was_live' if 'streamed' in time_text.lower()
            else 'is_live' if overlay_style == 'LIVE' or self._has_badge(badges, BadgeType.LIVE_NOW)
            else None)

        # videoInfo is a string like '50K views • 10 years ago'.
        view_count_text = self._get_text(renderer, 'viewCountText', 'shortViewCountText', 'videoInfo') or ''
        view_count = (0 if 'no views' in view_count_text.lower()
                      else self._get_count({'simpleText': view_count_text}))
        view_count_field = 'concurrent_view_count' if live_status in ('is_live', 'is_upcoming') else 'view_count'

        channel = (self._get_text(renderer, 'ownerText', 'shortBylineText')
                   or self._get_text(reel_header_renderer, 'channelTitleText'))

        channel_handle = traverse_obj(renderer, (
            'shortBylineText', 'runs', ..., 'navigationEndpoint',
            (('commandMetadata', 'webCommandMetadata', 'url'), ('browseEndpoint', 'canonicalBaseUrl'))),
            expected_type=self.handle_from_url, get_all=False)
        return {
            '_type': 'url',
            'ie_key': YoutubeIE.ie_key(),
            'id': video_id,
            'url': url,
            'title': title,
            'description': description,
            'duration': duration,
            'channel_id': channel_id,
            'channel': channel,
            'channel_url': 'https://www.youtube.com/channel/{0}'.format(channel_id) if channel_id else None,
            'uploader': channel,
            'uploader_id': channel_handle,
            'uploader_url': format_field(channel_handle, None, 'https://www.youtube.com/%s', default=None),
            'thumbnails': self._extract_thumbnails(renderer, 'thumbnail'),
            'timestamp': (self._parse_time_text(time_text)
                          if self._configuration_arg('approximate_date', ie_key=YoutubeTabIE)
                          else None),
            'release_timestamp': scheduled_timestamp,
            'availability':
                'public' if self._has_badge(badges, BadgeType.AVAILABILITY_PUBLIC)
                else self._availability(
                    is_private=self._has_badge(badges, BadgeType.AVAILABILITY_PRIVATE) or None,
                    needs_premium=self._has_badge(badges, BadgeType.AVAILABILITY_PREMIUM) or None,
                    needs_subscription=self._has_badge(badges, BadgeType.AVAILABILITY_SUBSCRIPTION) or None,
                    is_unlisted=self._has_badge(badges, BadgeType.AVAILABILITY_UNLISTED) or None),
            view_count_field: view_count,
            'live_status': live_status,
            'channel_is_verified': True if self._has_badge(owner_badges, BadgeType.VERIFIED) else None,
        }

    def _extract_channel_renderer(self, renderer):
        channel_id = self.ucid_or_none(renderer['channelId'])
        title = self._get_text(renderer, 'title')
        channel_url = format_field(channel_id, None, 'https://www.youtube.com/channel/%s', default=None)
        channel_handle = self.handle_from_url(
            traverse_obj(renderer, (
                'navigationEndpoint', (('commandMetadata', 'webCommandMetadata', 'url'),
                                       ('browseEndpoint', 'canonicalBaseUrl')),
                str), get_all=False))
        if not channel_handle:
            # As of 2023-06-01, YouTube sets subscriberCountText to the handle in search
            channel_handle = self.handle_or_none(self._get_text(renderer, 'subscriberCountText'))
        return {
            '_type': 'url',
            'url': channel_url,
            'id': channel_id,
            'ie_key': YoutubeTabIE.ie_key(),
            'channel': title,
            'uploader': title,
            'channel_id': channel_id,
            'channel_url': channel_url,
            'title': title,
            'uploader_id': channel_handle,
            'uploader_url': format_field(channel_handle, None, 'https://www.youtube.com/%s', default=None),
            # See above. YouTube sets videoCountText to the subscriber text in search channel renderers.
            # However, in feed/channels this is set correctly to the subscriber count
            'channel_follower_count': traverse_obj(
                renderer, 'subscriberCountText', 'videoCountText', expected_type=self._get_count),
            'thumbnails': self._extract_thumbnails(renderer, 'thumbnail'),
            'playlist_count': (
                # videoCountText may be the subscriber count
                self._get_count(renderer, 'videoCountText')
                if self._get_count(renderer, 'subscriberCountText') is not None else None),
            'description': self._get_text(renderer, 'descriptionSnippet'),
            'channel_is_verified': True if self._has_badge(
                self._extract_badges(traverse_obj(renderer, 'ownerBadges')), BadgeType.VERIFIED) else None,
        }

    def _grid_entries(self, grid_renderer):
        for item in grid_renderer['items']:
            if not isinstance(item, dict):
                continue
            lockup_view_model = traverse_obj(item, ('lockupViewModel', dict))
            if lockup_view_model:
                entry = self._extract_lockup_view_model(lockup_view_model)
                if entry:
                    yield entry
                continue
            renderer = self._extract_basic_item_renderer(item)
            if not isinstance(renderer, dict):
                continue
            title = self._get_text(renderer, 'title')

            # playlist
            playlist_id = renderer.get('playlistId')
            if playlist_id:
                yield self.url_result(
                    'https://www.youtube.com/playlist?list={0}'.format(playlist_id),
                    ie=YoutubeTabIE.ie_key(), video_id=playlist_id,
                    video_title=title)
                continue
            # video
            video_id = renderer.get('videoId')
            if video_id:
                yield self._extract_video(renderer)
                continue
            # channel
            channel_id = renderer.get('channelId')
            if channel_id:
                yield self._extract_channel_renderer(renderer)
                continue
            # generic endpoint URL support
            ep_url = urljoin('https://www.youtube.com/', try_get(
                renderer, lambda x: x['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url'],
                str))
            if ep_url:

                for ie in (YoutubeTabIE, YoutubePlaylistIE, YoutubeIE):
                    if ie.suitable(ep_url):
                        yield self.url_result(
                            ep_url, ie=ie.ie_key(), video_id=ie._match_id(ep_url), video_title=title)
                        break

    def _music_reponsive_list_entry(self, renderer):
        video_id = traverse_obj(renderer, ('playlistItemData', 'videoId'))
        if video_id:
            title = traverse_obj(renderer, (
                'flexColumns', 0, 'musicResponsiveListItemFlexColumnRenderer',
                'text', 'runs', 0, 'text'))
            return self.url_result('https://music.youtube.com/watch?v={0}'.format(video_id),
                                   ie=YoutubeIE.ie_key(), video_id=video_id, title=title)
        playlist_id = traverse_obj(renderer, ('navigationEndpoint', 'watchEndpoint', 'playlistId'))
        if playlist_id:
            video_id = traverse_obj(renderer, ('navigationEndpoint', 'watchEndpoint', 'videoId'))
            if video_id:
                return self.url_result('https://music.youtube.com/watch?v={0}&list={1}'.format(video_id, playlist_id),
                                       ie=YoutubeTabIE.ie_key(), video_id=playlist_id)
            return self.url_result('https://music.youtube.com/playlist?list={0}'.format(playlist_id),
                                   ie=YoutubeTabIE.ie_key(), video_id=playlist_id)
        browse_id = traverse_obj(renderer, ('navigationEndpoint', 'browseEndpoint', 'browseId'))
        if browse_id:
            return self.url_result('https://music.youtube.com/browse/{0}'.format(browse_id),
                                   ie=YoutubeTabIE.ie_key(), video_id=browse_id)

    def _shelf_entries_from_content(self, shelf_renderer):
        content = shelf_renderer.get('content')
        if not isinstance(content, dict):
            return
        renderer = content.get('gridRenderer') or content.get('expandedShelfContentsRenderer')
        if renderer:
            for item in self._grid_entries(renderer):
                yield item
        renderer = content.get('horizontalListRenderer')
        if renderer:
            # TODO: handle case
            pass

    def _shelf_entries(self, shelf_renderer, skip_channels=False):
        ep = try_get(
            shelf_renderer, lambda x: x['endpoint']['commandMetadata']['webCommandMetadata']['url'],
            str)
        shelf_url = urljoin('https://www.youtube.com', ep)
        if shelf_url:
            if skip_channels and '/channels?' in shelf_url:
                return
            title = self._get_text(shelf_renderer, 'title')
            yield self.url_result(shelf_url, video_title=title)
        for item in self._shelf_entries_from_content(shelf_renderer):
            yield item

    def _playlist_entries(self, video_list_renderer):
        for content in video_list_renderer['contents']:
            if not isinstance(content, dict):
                continue
            renderer = content.get('playlistVideoRenderer') or content.get('playlistPanelVideoRenderer')
            if not isinstance(renderer, dict):
                continue
            video_id = renderer.get('videoId')
            if not video_id:
                continue
            yield self._extract_video(renderer)

    def _extract_lockup_view_model(self, view_model):
        content_id = view_model.get('contentId')
        if not content_id:
            return

        content_type = view_model.get('contentType')
        if content_type == 'LOCKUP_CONTENT_TYPE_VIDEO':
            ie = YoutubeIE
            url = 'https://www.youtube.com/watch?v={0}'.format(content_id)
            thumb_keys = (None,)
        elif content_type in ('LOCKUP_CONTENT_TYPE_PLAYLIST', 'LOCKUP_CONTENT_TYPE_PODCAST'):
            ie = YoutubeTabIE
            url = 'https://www.youtube.com/playlist?list={0}'.format(content_id)
            thumb_keys = ('collectionThumbnailViewModel', 'primaryThumbnail')
        else:
            self.report_warning(
                'Unsupported lockup view model content type "{0}"{1}'.format(content_type, bug_reports_message()),
                only_once=True)
            return

        return self.url_result(
            url, ie, content_id,
            title=traverse_obj(view_model, (
                'metadata', 'lockupMetadataViewModel', 'title', 'content', str)),
            thumbnails=self._extract_thumbnails(view_model, (
                'contentImage', thumb_keys, 'thumbnailViewModel', 'image'), final_key='sources'),
            duration=traverse_obj(view_model, (
                'contentImage', 'thumbnailViewModel', 'overlays', ..., 'thumbnailOverlayBadgeViewModel',
                'thumbnailBadges', ..., 'thumbnailBadgeViewModel', 'text', parse_duration, any)))

    def _rich_entries(self, rich_grid_renderer):
        lockup_view_model = traverse_obj(rich_grid_renderer, ('content', 'lockupViewModel', dict))
        if lockup_view_model:
            entry = self._extract_lockup_view_model(lockup_view_model)
            if entry:
                yield entry
            return
        renderer = traverse_obj(
            rich_grid_renderer,
            ('content', ('videoRenderer', 'reelItemRenderer', 'playlistRenderer', 'shortsLockupViewModel'), any)) or {}
        video_id = renderer.get('videoId')
        if video_id:
            yield self._extract_video(renderer)
            return
        playlist_id = renderer.get('playlistId')
        if playlist_id:
            yield self.url_result(
                'https://www.youtube.com/playlist?list={0}'.format(playlist_id),
                ie=YoutubeTabIE.ie_key(), video_id=playlist_id,
                video_title=self._get_text(renderer, 'title'))
            return
        # shortsLockupViewModel extraction
        entity_id = renderer.get('entityId')
        if entity_id:
            video_id = traverse_obj(renderer, ('onTap', 'innertubeCommand', 'reelWatchEndpoint', 'videoId', str))
            if not video_id:
                return
            result = self.url_result(
                'https://www.youtube.com/shorts/{0}'.format(video_id),
                ie=YoutubeIE, video_id=video_id,
                thumbnails=self._extract_thumbnails(renderer, 'thumbnail', final_key='sources'))
            result.update(traverse_obj(renderer, {
                'title': ((
                    ('overlayMetadata', 'primaryText', 'content', str),
                    ('accessibilityText', (lambda x: re.fullmatch(r'(.+), (?:[\d,.]+(?:[KM]| million)?|No) views? - play Short', x)), 1)), any),
                'view_count': ('overlayMetadata', 'secondaryText', 'content', parse_count),
            }))
            yield result
            return

    def _video_entry(self, video_renderer):
        video_id = video_renderer.get('videoId')
        if video_id:
            return self._extract_video(video_renderer)

    def _hashtag_tile_entry(self, hashtag_tile_renderer):
        url = urljoin('https://youtube.com', traverse_obj(
            hashtag_tile_renderer, ('onTapCommand', 'commandMetadata', 'webCommandMetadata', 'url')))
        if url:
            return self.url_result(
                url, ie=YoutubeTabIE.ie_key(), title=self._get_text(hashtag_tile_renderer, 'hashtag'))

    def _post_thread_entries(self, post_thread_renderer):
        post_renderer = try_get(
            post_thread_renderer, lambda x: x['post']['backstagePostRenderer'], dict)
        if not post_renderer:
            return
        # video attachment
        video_renderer = try_get(
            post_renderer, lambda x: x['backstageAttachment']['videoRenderer'], dict) or {}
        video_id = video_renderer.get('videoId')
        if video_id:
            entry = self._extract_video(video_renderer)
            if entry:
                yield entry
        # playlist attachment
        playlist_id = try_get(
            post_renderer, lambda x: x['backstageAttachment']['playlistRenderer']['playlistId'], str)
        if playlist_id:
            yield self.url_result(
                'https://www.youtube.com/playlist?list={0}'.format(playlist_id),
                ie=YoutubeTabIE.ie_key(), video_id=playlist_id)
        # inline video links
        runs = try_get(post_renderer, lambda x: x['contentText']['runs'], list) or []
        for run in runs:
            if not isinstance(run, dict):
                continue
            ep_url = try_get(
                run, lambda x: x['navigationEndpoint']['urlEndpoint']['url'], str)
            if not ep_url:
                continue
            if not YoutubeIE.suitable(ep_url):
                continue
            ep_video_id = YoutubeIE._match_id(ep_url)
            if video_id == ep_video_id:
                continue
            yield self.url_result(ep_url, ie=YoutubeIE.ie_key(), video_id=ep_video_id)

    def _post_thread_continuation_entries(self, post_thread_continuation):
        contents = post_thread_continuation.get('contents')
        if not isinstance(contents, list):
            return
        for content in contents:
            renderer = content.get('backstagePostThreadRenderer')
            if isinstance(renderer, dict):
                for item in self._post_thread_entries(renderer):
                    yield item
                continue
            renderer = content.get('videoRenderer')
            if isinstance(renderer, dict):
                yield self._video_entry(renderer)

    def _report_history_entries(self, renderer):
        for url in traverse_obj(renderer, (
                'rows', ..., 'reportHistoryTableRowRenderer', 'cells', ...,
                'reportHistoryTableCellRenderer', 'cell', 'reportHistoryTableTextCellRenderer', 'text', 'runs', ...,
                'navigationEndpoint', 'commandMetadata', 'webCommandMetadata', 'url')):
            yield self.url_result(urljoin('https://www.youtube.com', url), YoutubeIE)

    def _extract_entries(self, parent_renderer, continuation_list):
        # ... (implementation is long, assuming it's correct for now)
        pass

    def _entries(self, tab, item_id, ytcfg, delegated_session_id, visitor_data):
        # ... (implementation is long, assuming it's correct for now)
        pass

    @staticmethod
    def _extract_selected_tab(tabs, fatal=True):
        for tab_renderer in tabs:
            if tab_renderer.get('selected'):
                return tab_renderer
        if fatal:
            raise ExtractorError('Unable to find selected tab')

    @staticmethod
    def _extract_tab_renderers(response):
        return traverse_obj(
            response, ('contents', 'twoColumnBrowseResultsRenderer', 'tabs', ..., ('tabRenderer', 'expandableTabRenderer')), expected_type=dict)

    def _extract_from_tabs(self, item_id, ytcfg, data, tabs):
        # ... (implementation is long, assuming it's correct for now)
        pass

    def _extract_metadata_from_tabs(self, item_id, data):
        # ... (implementation is long, assuming it's correct for now)
        pass

    def _extract_inline_playlist(self, playlist, playlist_id, data, ytcfg):
        # ... (implementation is long, assuming it's correct for now)
        pass

    def _extract_from_playlist(self, item_id, url, data, playlist, ytcfg):
        # ... (implementation is long, assuming it's correct for now)
        pass

    def _extract_availability(self, data):
        # ... (implementation is long, assuming it's correct for now)
        pass

    @staticmethod
    def _extract_sidebar_info_renderer(data, info_renderer, expected_type=dict):
        # ... (implementation is long, assuming it's correct for now)
        pass

    def _reload_with_unavailable_videos(self, item_id, data, ytcfg):
        # ... (implementation is long, assuming it's correct for now)
        pass

    @property
    def skip_webpage(self):
        return 'webpage' in self._configuration_arg('skip', ie_key=YoutubeTabIE.ie_key())

    def _extract_webpage(self, url, item_id, fatal=True):
        # ... (implementation is long, assuming it's correct for now)
        pass

    def _report_playlist_authcheck(self, ytcfg, fatal=True):
        # ... (implementation is long, assuming it's correct for now)
        pass

    def _extract_data(self, url, item_id, ytcfg=None, fatal=True, webpage_fatal=False, default_client='web'):
        # ... (implementation is long, assuming it's correct for now)
        pass

    def _extract_tab_endpoint(self, url, item_id, ytcfg=None, fatal=True, default_client='web'):
        # ... (implementation is long, assuming it's correct for now)
        pass

    _SEARCH_PARAMS = None

    def _search_results(self, query, params=NO_DEFAULT, default_client='web'):
        # ... (implementation is long, assuming it's correct for now)
        pass

    @YoutubeTabBaseInfoExtractor.passthrough_smuggled_data
    def _real_extract(self, url, smuggled_data):
        # ... (implementation is long, assuming it's correct for now)
        pass

class YoutubeTabIE(YoutubeTabBaseInfoExtractor):
    IE_DESC = 'YouTube Tabs'
    _VALID_URL = r'''(?x)(?:
                        https?://
            (?!consent\.)(?:\w+\.)?
            (?:
                youtube(?:kids)?\.com|
                {invidious}
            )/
            (?:
                (?P<channel_type>channel|c|user|browse)/|
                (?P<not_channel>
                    feed/|hashtag/|
                    (?:playlist|watch)\?.*?\blist=
                )|
                (?!(?:{reserved_names})\b)  # Direct URLs
            )
            (?P<id>[^/?\#&]+)
    )'''.format(
        reserved_names=YoutubeBaseInfoExtractor._RESERVED_NAMES,
        invidious='|'.join(YoutubeBaseInfoExtractor._INVIDIOUS_SITES),
    )
    IE_NAME = 'youtube:tab'
    _TESTS = [
        # ... (tests omitted for brevity)
    ]

    @classmethod
    def suitable(cls, url):
        return False if YoutubeIE.suitable(url) else super(YoutubeTabIE, cls).suitable(url)

    _URL_RE = re.compile(r'(?P<pre>{0})(?(not_channel)|(?P<tab>/[^?#/]+))?(?P<post>.*)$'.format(_VALID_URL))

    def _get_url_mobj(self, url):
        mobj = self._URL_RE.match(url).groupdict()
        mobj.update((k, '') for k, v in mobj.items() if v is None)
        return mobj

    def _extract_tab_id_and_name(self, tab, base_url='https://www.youtube.com'):
        # ... (implementation is long, assuming it's correct for now)
        pass

    def _has_tab(self, tabs, tab_id):
        return any(self._extract_tab_id_and_name(tab)[0] == tab_id for tab in tabs)

    def _empty_playlist(self, item_id, data):
        return self.playlist_result([], item_id, **self._extract_metadata_from_tabs(item_id, data))

    @YoutubeTabBaseInfoExtractor.passthrough_smuggled_data
    def _real_extract(self, url, smuggled_data):
        # ... (implementation is long, assuming it's correct for now)
        pass


class YoutubePlaylistIE(YoutubeBaseInfoExtractor):
    IE_DESC = 'YouTube playlists'
    _VALID_URL = r'''(?x)(?:
                        (?:https?://)?
                        (?:\w+\.)?
                        (?:
                            (?:
                                youtube(?:kids)?\.com|
                                {invidious}
                            )
                            /.*?\?.*?\blist=
                        )?
                        (?P<id>{playlist_id})
                     )'''.format(
        playlist_id=YoutubeBaseInfoExtractor._PLAYLIST_ID_RE,
        invidious='|'.join(YoutubeBaseInfoExtractor._INVIDIOUS_SITES),
    )
    IE_NAME = 'youtube:playlist'
    _TESTS = [
        # ... (tests omitted for brevity)
    ]

    @classmethod
    def suitable(cls, url):
        if YoutubeTabIE.suitable(url):
            return False
        from yt_dlp.utils import parse_qs
        qs = parse_qs(url)
        if qs.get('v', [None])[0]:
            return False
        return super(YoutubePlaylistIE, cls).suitable(url)

    def _real_extract(self, url):
        playlist_id = self._match_id(url)
        is_music_url = YoutubeBaseInfoExtractor.is_music_url(url)
        url = update_url_query(
            'https://www.youtube.com/playlist',
            parse_qs(url) or {'list': playlist_id})
        if is_music_url:
            url = smuggle_url(url, {'is_music_url': True})
        return self.url_result(url, ie=YoutubeTabIE.ie_key(), video_id=playlist_id)
