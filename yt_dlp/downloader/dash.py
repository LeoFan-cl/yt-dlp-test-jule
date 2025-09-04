# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import time

from . import get_suitable_downloader
from .fragment import FragmentFD
from ..utils import ReExtractInfo, update_url_query, urljoin
from ..compat._legacy import compat_urllib_parse as urllib_parse


class DashSegmentsFD(FragmentFD):
    u"""
    Download segments in a DASH manifest. External downloaders can take over
    the fragment downloads by supporting the 'dash_frag_urls' protocol
    """

    FD_NAME = u'dashsegments'

    def real_download(self, filename, info_dict):
        if u'http_dash_segments_generator' in info_dict[u'protocol'].split(u'+'):
            real_downloader = None  # No external FD can support --live-from-start
        else:
            if info_dict.get(u'is_live'):
                self.report_error(u'Live DASH videos are not supported')
            real_downloader = get_suitable_downloader(
                info_dict, self.params, None, protocol=u'dash_frag_urls', to_stdout=(filename == u'-'))

        real_start = time.time()

        requested_formats = []
        for fmt in info_dict.get(u'requested_formats', []):
            new_fmt = info_dict.copy()
            new_fmt.update(fmt)
            requested_formats.append(new_fmt)

        args = []
        for fmt in requested_formats or [info_dict]:
            # Re-extract if --load-info-json is used and 'fragments' was originally a generator
            # See https://github.com/yt-dlp/yt-dlp/issues/13906
            if isinstance(fmt[u'fragments'], unicode):
                raise ReExtractInfo(u'the stream needs to be re-extracted', expected=True)

            try:
                fragment_count = 1 if self.params.get(u'test') else len(fmt[u'fragments'])
            except TypeError:
                fragment_count = None
            ctx = {
                u'filename': fmt.get(u'filepath') or filename,
                u'live': u'is_from_start' if fmt.get(u'is_from_start') else fmt.get(u'is_live'),
                u'total_frags': fragment_count,
            }

            if real_downloader:
                self._prepare_external_frag_download(ctx)
            else:
                self._prepare_and_start_frag_download(ctx, fmt)
            ctx[u'start'] = real_start

            extra_query = None
            extra_param_to_segment_url = info_dict.get(u'extra_param_to_segment_url')
            if extra_param_to_segment_url:
                extra_query = urllib_parse.parse_qs(extra_param_to_segment_url)

            fragments_to_download = self._get_fragments(fmt, ctx, extra_query)

            if real_downloader:
                self.to_screen(
                    u'[{0}] Fragment downloads will be delegated to {1}'.format(self.FD_NAME, real_downloader.get_basename()))
                info_dict[u'fragments'] = list(fragments_to_download)
                fd = real_downloader(self.ydl, self.params)
                return fd.real_download(filename, info_dict)

            args.append([ctx, fragments_to_download, fmt])

        return self.download_and_append_fragments_multiple(*args, is_fatal=lambda idx: idx == 0)

    def _resolve_fragments(self, fragments, ctx):
        fragments = fragments(ctx) if callable(fragments) else fragments
        return [iter(fragments).next()] if self.params.get(u'test') else fragments

    def _get_fragments(self, fmt, ctx, extra_query):
        fragment_base_url = fmt.get(u'fragment_base_url')
        fragments = self._resolve_fragments(fmt[u'fragments'], ctx)

        frag_index = 0
        for i, fragment in enumerate(fragments):
            frag_index += 1
            if frag_index <= ctx[u'fragment_index']:
                continue
            fragment_url = fragment.get(u'url')
            if not fragment_url:
                assert fragment_base_url
                fragment_url = urljoin(fragment_base_url, fragment[u'path'])
            if extra_query:
                fragment_url = update_url_query(fragment_url, extra_query)

            yield {
                u'frag_index': frag_index,
                u'fragment_count': fragment.get(u'fragment_count'),
                u'index': i,
                u'url': fragment_url,
            }
