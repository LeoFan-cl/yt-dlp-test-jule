# coding: utf-8
from __future__ import with_statement
from __future__ import absolute_import, division, print_function, unicode_literals

import binascii
import io
import re

from . import get_suitable_downloader
from .external import FFmpegFD
from .fragment import FragmentFD
from .. import webvtt
from ..dependencies import Cryptodome
from ..utils import (
    bug_reports_message,
    parse_m3u8_attributes,
    remove_start,
    traverse_obj,
    update_url_query,
    urljoin,
)
from ..utils._utils import _request_dump_filename
from ..compat._legacy import compat_urllib_parse as urllib_parse
from io import open


class HlsFD(FragmentFD):
    u"""
    Download segments in a m3u8 manifest. External downloaders can take over
    the fragment downloads by supporting the 'm3u8_frag_urls' protocol and
    re-defining 'supports_manifest' function
    """

    FD_NAME = u'hlsnative'

    @staticmethod
    def _has_drm(manifest):  # TODO: https://github.com/yt-dlp/yt-dlp/pull/5039
        return bool(re.search(u'|'.join((
            ur'#EXT-X-(?:SESSION-)?KEY:.*?URI="skd://',  # Apple FairPlay
            ur'#EXT-X-(?:SESSION-)?KEY:.*?KEYFORMAT="com\.apple\.streamingkeydelivery"',  # Apple FairPlay
            ur'#EXT-X-(?:SESSION-)?KEY:.*?KEYFORMAT="com\.microsoft\.playready"',  # Microsoft PlayReady
            ur'#EXT-X-FAXS-CM:',  # Adobe Flash Access
        )), manifest))

    @classmethod
    def can_download(cls, manifest, info_dict, allow_unplayable_formats=False):
        UNSUPPORTED_FEATURES = []
        if not allow_unplayable_formats:
            UNSUPPORTED_FEATURES += [
                ur'#EXT-X-KEY:METHOD=(?!NONE|AES-128)',  # encrypted streams [1], but not necessarily DRM
            ]

        def check_results():
            yield not info_dict.get(u'is_live')
            for feature in UNSUPPORTED_FEATURES:
                yield not re.search(feature, manifest)
            if not allow_unplayable_formats:
                yield not cls._has_drm(manifest)
        return all(check_results())

    def real_download(self, filename, info_dict):
        man_url = info_dict[u'url']

        s = info_dict.get(u'hls_media_playlist_data')
        if s:
            self.to_screen(u'[{0}] Using m3u8 manifest from extracted info'.format(self.FD_NAME))
        else:
            self.to_screen(u'[{0}] Downloading m3u8 manifest'.format(self.FD_NAME))
            urlh = self.ydl.urlopen(self._prepare_url(info_dict, man_url))
            man_url = urlh.geturl()
            s_bytes = urlh.read()
            if self.params.get(u'write_pages'):
                dump_filename = _request_dump_filename(
                    man_url, info_dict[u'id'], None,
                    trim_length=self.params.get(u'trim_file_name'))
                self.to_screen(u'[{0}] Saving request to {1}'.format(self.FD_NAME, dump_filename))
                with open(dump_filename, u'wb') as outf:
                    outf.write(s_bytes)
            s = s_bytes.decode(u'utf-8', u'ignore')

        can_download, message = self.can_download(s, info_dict, self.params.get(u'allow_unplayable_formats')), None
        if can_download:
            has_ffmpeg = FFmpegFD.available()
            if not Cryptodome.AES and u'#EXT-X-KEY:METHOD=AES-128' in s:
                # Even if pycryptodomex isn't available, force HlsFD for m3u8s that won't work with ffmpeg
                ffmpeg_can_dl = not traverse_obj(info_dict, ((
                    u'extra_param_to_segment_url', u'extra_param_to_key_url',
                    u'hls_media_playlist_data', (u'hls_aes', (u'uri', u'key', u'iv')),
                ), any))
                message = u'The stream has AES-128 encryption and {0} available'.format(
                    u'neither ffmpeg nor pycryptodomex are' if ffmpeg_can_dl and not has_ffmpeg else
                    u'pycryptodomex is not')
                if has_ffmpeg and ffmpeg_can_dl:
                    can_download = False
                else:
                    message += u'; decryption will be performed natively, but will be extremely slow'
            elif info_dict.get(u'extractor_key') == u'Generic' and re.search(ur'(?m)#EXT-X-MEDIA-SEQUENCE:(?!0$)', s):
                install_ffmpeg = u'' if has_ffmpeg else u'install ffmpeg and '
                message = (u'Live HLS streams are not supported by the native downloader. If this is a livestream, '
                           u'please {0}add "--downloader ffmpeg --hls-use-mpegts" to your command'.format(install_ffmpeg))
        if not can_download:
            if self._has_drm(s) and not self.params.get(u'allow_unplayable_formats'):
                if info_dict.get(u'has_drm') and self.params.get(u'test'):
                    self.to_screen(u'[{0}] This format is DRM protected'.format(self.FD_NAME), skip_eol=True)
                else:
                    self.report_error(
                        u'This format is DRM protected; Try selecting another format with --format or '
                        u'add --check-formats to automatically fallback to the next best format', tb=False)
                return False
            message = message or u'Unsupported features have been detected'
            fd = FFmpegFD(self.ydl, self.params)
            self.report_warning(u'{0}; extraction will be delegated to {1}'.format(message, fd.get_basename()))
            return fd.real_download(filename, info_dict)
        elif message:
            self.report_warning(message)

        is_webvtt = info_dict[u'ext'] == u'vtt'
        if is_webvtt:
            real_downloader = None  # Packing the fragments is not currently supported for external downloader
        else:
            real_downloader = get_suitable_downloader(
                info_dict, self.params, None, protocol=u'm3u8_frag_urls', to_stdout=(filename == u'-'))
        if real_downloader and not real_downloader.supports_manifest(s):
            real_downloader = None
        if real_downloader:
            self.to_screen(u'[{0}] Fragment downloads will be delegated to {1}'.format(self.FD_NAME, real_downloader.get_basename()))

        def is_ad_fragment_start(s):
            return ((s.startswith(u'#ANVATO-SEGMENT-INFO') and u'type=ad' in s)
                    or (s.startswith(u'#UPLYNK-SEGMENT') and s.endswith(u',ad')))

        def is_ad_fragment_end(s):
            return ((s.startswith(u'#ANVATO-SEGMENT-INFO') and u'type=master' in s)
                    or (s.startswith(u'#UPLYNK-SEGMENT') and s.endswith(u',segment')))

        fragments = []

        media_frags = 0
        ad_frags = 0
        ad_frag_next = False
        for line in s.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith(u'#'):
                if is_ad_fragment_start(line):
                    ad_frag_next = True
                elif is_ad_fragment_end(line):
                    ad_frag_next = False
                continue
            if ad_frag_next:
                ad_frags += 1
                continue
            media_frags += 1

        ctx = {
            u'filename': filename,
            u'total_frags': media_frags,
            u'ad_frags': ad_frags,
        }

        if real_downloader:
            self._prepare_external_frag_download(ctx)
        else:
            self._prepare_and_start_frag_download(ctx, info_dict)

        extra_state = ctx.setdefault(u'extra_state', {})

        format_index = info_dict.get(u'format_index')
        extra_segment_query = None
        if info_dict.get(u'extra_param_to_segment_url'):
            extra_segment_query = urllib_parse.parse_qs(info_dict.get(u'extra_param_to_segment_url'))
        extra_key_query = None
        if info_dict.get(u'extra_param_to_key_url'):
            extra_key_query = urllib_parse.parse_qs(info_dict.get(u'extra_param_to_key_url'))
        i = 0
        media_sequence = 0
        decrypt_info = {u'METHOD': u'NONE'}
        external_aes_key = traverse_obj(info_dict, (u'hls_aes', u'key'))
        if external_aes_key:
            external_aes_key = binascii.unhexlify(remove_start(external_aes_key, u'0x'))
            assert len(external_aes_key) in (16, 24, 32), u'Invalid length for HLS AES-128 key'
        external_aes_iv = traverse_obj(info_dict, (u'hls_aes', u'iv'))
        if external_aes_iv:
            external_aes_iv = binascii.unhexlify(remove_start(external_aes_iv, u'0x').zfill(32))
        byte_range = {}
        byte_range_offset = 0
        discontinuity_count = 0
        frag_index = 0
        ad_frag_next = False
        for line in s.splitlines():
            line = line.strip()
            if line:
                if not line.startswith(u'#'):
                    if format_index is not None and discontinuity_count != format_index:
                        continue
                    if ad_frag_next:
                        continue
                    frag_index += 1
                    if frag_index <= ctx[u'fragment_index']:
                        continue
                    frag_url = urljoin(man_url, line)
                    if extra_segment_query:
                        frag_url = update_url_query(frag_url, extra_segment_query)

                    fragments.append({
                        u'frag_index': frag_index,
                        u'url': frag_url,
                        u'decrypt_info': decrypt_info,
                        u'byte_range': byte_range,
                        u'media_sequence': media_sequence,
                    })
                    media_sequence += 1

                    # If the byte_range is truthy, reset it after appending a fragment that uses it
                    if byte_range:
                        byte_range_offset = byte_range[u'end']
                        byte_range = {}

                elif line.startswith(u'#EXT-X-MAP'):
                    if format_index is not None and discontinuity_count != format_index:
                        continue
                    if frag_index > 0:
                        self.report_error(
                            u'Initialization fragment found after media fragments, unable to download')
                        return False
                    frag_index += 1
                    map_info = parse_m3u8_attributes(line[11:])
                    frag_url = urljoin(man_url, map_info.get(u'URI'))
                    if extra_segment_query:
                        frag_url = update_url_query(frag_url, extra_segment_query)

                    map_byte_range = {}

                    if map_info.get(u'BYTERANGE'):
                        splitted_byte_range = map_info.get(u'BYTERANGE').split(u'@')
                        sub_range_start = int(splitted_byte_range[1]) if len(splitted_byte_range) == 2 else 0
                        map_byte_range = {
                            u'start': sub_range_start,
                            u'end': sub_range_start + int(splitted_byte_range[0]),
                        }

                    fragments.append({
                        u'frag_index': frag_index,
                        u'url': frag_url,
                        u'decrypt_info': decrypt_info,
                        u'byte_range': map_byte_range,
                        u'media_sequence': media_sequence,
                    })
                    media_sequence += 1

                elif line.startswith(u'#EXT-X-KEY'):
                    decrypt_url = decrypt_info.get(u'URI')
                    decrypt_info = parse_m3u8_attributes(line[11:])
                    if decrypt_info[u'METHOD'] == u'AES-128':
                        if external_aes_iv:
                            decrypt_info[u'IV'] = external_aes_iv
                        elif u'IV' in decrypt_info:
                            decrypt_info[u'IV'] = binascii.unhexlify(decrypt_info[u'IV'][2:].zfill(32))
                        if external_aes_key:
                            decrypt_info[u'KEY'] = external_aes_key
                        else:
                            decrypt_info[u'URI'] = urljoin(man_url, decrypt_info[u'URI'])
                            if extra_key_query or extra_segment_query:
                                # Fall back to extra_segment_query to key for backwards compat
                                decrypt_info[u'URI'] = update_url_query(
                                    decrypt_info[u'URI'], extra_key_query or extra_segment_query)
                            if decrypt_url != decrypt_info[u'URI']:
                                decrypt_info[u'KEY'] = None

                elif line.startswith(u'#EXT-X-MEDIA-SEQUENCE'):
                    media_sequence = int(line[22:])
                elif line.startswith(u'#EXT-X-BYTERANGE'):
                    splitted_byte_range = line[17:].split(u'@')
                    sub_range_start = int(splitted_byte_range[1]) if len(splitted_byte_range) == 2 else byte_range_offset
                    byte_range = {
                        u'start': sub_range_start,
                        u'end': sub_range_start + int(splitted_byte_range[0]),
                    }
                elif is_ad_fragment_start(line):
                    ad_frag_next = True
                elif is_ad_fragment_end(line):
                    ad_frag_next = False
                elif line.startswith(u'#EXT-X-DISCONTINUITY'):
                    discontinuity_count += 1
                i += 1

        # We only download the first fragment during the test
        if self.params.get(u'test', False):
            fragments = [fragments[0] if fragments else None]

        if real_downloader:
            info_dict[u'fragments'] = fragments
            fd = real_downloader(self.ydl, self.params)
            # TODO: Make progress updates work without hooking twice
            # for ph in self._progress_hooks:
            #     fd.add_progress_hook(ph)
            return fd.real_download(filename, info_dict)

        if is_webvtt:
            def pack_fragment(frag_content, frag_index):
                output = io.StringIO()
                adjust = 0
                overflow = False
                mpegts_last = None
                for block in webvtt.parse_fragment(frag_content):
                    if isinstance(block, webvtt.CueBlock):
                        extra_state[u'webvtt_mpegts_last'] = mpegts_last
                        if overflow:
                            extra_state[u'webvtt_mpegts_adjust'] += 1
                            overflow = False
                        block.start += adjust
                        block.end += adjust

                        dedup_window = extra_state.setdefault(u'webvtt_dedup_window', [])

                        ready = []

                        i = 0
                        is_new = True
                        while i < len(dedup_window):
                            wcue = dedup_window[i]
                            wblock = webvtt.CueBlock.from_json(wcue)
                            i += 1
                            if wblock.hinges(block):
                                wcue[u'end'] = block.end
                                is_new = False
                                continue
                            if wblock == block:
                                is_new = False
                                continue
                            if wblock.end > block.start:
                                continue
                            ready.append(wblock)
                            i -= 1
                            del dedup_window[i]

                        if is_new:
                            dedup_window.append(block.as_json)
                        for block in ready:
                            block.write_into(output)

                        # we only emit cues once they fall out of the duplicate window
                        continue
                    elif isinstance(block, webvtt.Magic):
                        # take care of MPEG PES timestamp overflow
                        if block.mpegts is None:
                            block.mpegts = 0
                        extra_state.setdefault(u'webvtt_mpegts_adjust', 0)
                        block.mpegts += extra_state[u'webvtt_mpegts_adjust'] << 33
                        if block.mpegts < extra_state.get(u'webvtt_mpegts_last', 0):
                            overflow = True
                            block.mpegts += 1 << 33
                        mpegts_last = block.mpegts

                        if frag_index == 1:
                            extra_state[u'webvtt_mpegts'] = block.mpegts or 0
                            extra_state[u'webvtt_local'] = block.local or 0
                            # XXX: block.local = block.mpegts = None ?
                        else:
                            if block.mpegts is not None and block.local is not None:
                                adjust = (
                                    (block.mpegts - extra_state.get(u'webvtt_mpegts', 0))
                                    - (block.local - extra_state.get(u'webvtt_local', 0))
                                )
                            continue
                    elif isinstance(block, webvtt.HeaderBlock):
                        if frag_index != 1:
                            # XXX: this should probably be silent as well
                            # or verify that all segments contain the same data
                            self.report_warning(bug_reports_message(
                                u'Discarding a {0} block found in the middle of the stream; if the subtitles display incorrectly,'.format(type(block).__name__)))
                            continue
                    block.write_into(output)

                return output.getvalue().encode()

            def fin_fragments():
                dedup_window = extra_state.get(u'webvtt_dedup_window')
                if not dedup_window:
                    return ''

                output = io.StringIO()
                for cue in dedup_window:
                    webvtt.CueBlock.from_json(cue).write_into(output)

                return output.getvalue().encode()

            if len(fragments) == 1:
                self.download_and_append_fragments(ctx, fragments, info_dict)
            else:
                self.download_and_append_fragments(
                    ctx, fragments, info_dict, pack_func=pack_fragment, finish_func=fin_fragments)
        else:
            return self.download_and_append_fragments(ctx, fragments, info_dict)
