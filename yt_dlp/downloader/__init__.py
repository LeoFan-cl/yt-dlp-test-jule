from __future__ import absolute_import
from ..utils import NO_DEFAULT, determine_protocol


def get_suitable_downloader(info_dict, params={}, default=NO_DEFAULT, protocol=None, to_stdout=False):
    info_dict[u'protocol'] = determine_protocol(info_dict)
    info_copy = info_dict.copy()
    info_copy[u'to_stdout'] = to_stdout

    protocols = (protocol or info_copy[u'protocol']).split(u'+')
    downloaders = [_get_suitable_downloader(info_copy, proto, params, default) for proto in protocols]

    if set(downloaders) == set([FFmpegFD]) and FFmpegFD.can_merge_formats(info_copy, params):
        return FFmpegFD
    elif (set(downloaders) == set([DashSegmentsFD])
          and not (to_stdout and len(protocols) > 1)
          and set(protocols) == set([u'http_dash_segments_generator'])):
        return DashSegmentsFD
    elif len(downloaders) == 1:
        return downloaders[0]
    return None


# Some of these require get_suitable_downloader
from .common import FileDownloader
from .dash import DashSegmentsFD
from .external import FFmpegFD, get_external_downloader
from .f4m import F4mFD
from .fc2 import FC2LiveFD
from .hls import HlsFD
from .http import HttpFD
from .ism import IsmFD
from .mhtml import MhtmlFD
from .niconico import NiconicoLiveFD
from .rtmp import RtmpFD
from .rtsp import RtspFD
from .websocket import WebSocketFragmentFD
from .youtube_live_chat import YoutubeLiveChatFD
from .bunnycdn import BunnyCdnFD

PROTOCOL_MAP = {
    u'rtmp': RtmpFD,
    u'rtmpe': RtmpFD,
    u'rtmp_ffmpeg': FFmpegFD,
    u'm3u8_native': HlsFD,
    u'm3u8': FFmpegFD,
    u'mms': RtspFD,
    u'rtsp': RtspFD,
    u'f4m': F4mFD,
    u'http_dash_segments': DashSegmentsFD,
    u'http_dash_segments_generator': DashSegmentsFD,
    u'ism': IsmFD,
    u'mhtml': MhtmlFD,
    u'niconico_live': NiconicoLiveFD,
    u'fc2_live': FC2LiveFD,
    u'websocket_frag': WebSocketFragmentFD,
    u'youtube_live_chat': YoutubeLiveChatFD,
    u'youtube_live_chat_replay': YoutubeLiveChatFD,
    u'bunnycdn': BunnyCdnFD,
}


def shorten_protocol_name(proto, simplify=False):
    short_protocol_names = {
        u'm3u8_native': u'm3u8',
        u'm3u8': u'm3u8F',
        u'rtmp_ffmpeg': u'rtmpF',
        u'http_dash_segments': u'dash',
        u'http_dash_segments_generator': u'dashG',
        u'websocket_frag': u'WSfrag',
    }
    if simplify:
        short_protocol_names.update({
            u'https': u'http',
            u'ftps': u'ftp',
            u'm3u8': u'm3u8',  # Reverse above m3u8 mapping
            u'm3u8_native': u'm3u8',
            u'http_dash_segments_generator': u'dash',
            u'rtmp_ffmpeg': u'rtmp',
            u'm3u8_frag_urls': u'm3u8',
            u'dash_frag_urls': u'dash',
        })
    return short_protocol_names.get(proto, proto)


def _get_suitable_downloader(info_dict, protocol, params, default):
    u"""Get the downloader class that can handle the info dict."""
    if default is NO_DEFAULT:
        default = HttpFD

    if (info_dict.get(u'section_start') or info_dict.get(u'section_end')) and FFmpegFD.can_download(info_dict):
        return FFmpegFD

    info_dict[u'protocol'] = protocol
    downloaders = params.get(u'external_downloader')
    external_downloader = (
        downloaders if isinstance(downloaders, unicode) or downloaders is None
        else downloaders.get(shorten_protocol_name(protocol, True), downloaders.get(u'default')))

    if external_downloader is None:
        if info_dict[u'to_stdout'] and FFmpegFD.can_merge_formats(info_dict, params):
            return FFmpegFD
    elif external_downloader.lower() != u'native' and info_dict.get(u'impersonate') is None:
        ed = get_external_downloader(external_downloader)
        if ed.can_download(info_dict, external_downloader):
            return ed

    if protocol == u'http_dash_segments':
        if info_dict.get(u'is_live') and (external_downloader or u'').lower() != u'native':
            return FFmpegFD

    if protocol in (u'm3u8', u'm3u8_native'):
        if info_dict.get(u'is_live'):
            return FFmpegFD
        elif (external_downloader or u'').lower() == u'native':
            return HlsFD
        elif protocol == u'm3u8_native' and get_suitable_downloader(
                info_dict, params, None, protocol=u'm3u8_frag_urls', to_stdout=info_dict[u'to_stdout']):
            return HlsFD
        elif params.get(u'hls_prefer_native') is True:
            return HlsFD
        elif params.get(u'hls_prefer_native') is False:
            return FFmpegFD

    return PROTOCOL_MAP.get(protocol, default)


__all__ = [
    u'FileDownloader',
    u'get_suitable_downloader',
    u'shorten_protocol_name',
]
