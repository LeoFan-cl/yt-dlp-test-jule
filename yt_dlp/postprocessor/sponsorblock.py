from __future__ import division
from __future__ import absolute_import
import hashlib
import json
import re
import urllib

from .ffmpeg import FFmpegPostProcessor


class SponsorBlockPP(FFmpegPostProcessor):
    # https://wiki.sponsor.ajay.app/w/Types
    EXTRACTORS = {
        u'Youtube': u'YouTube',
    }
    POI_CATEGORIES = {
        u'poi_highlight': u'Highlight',
    }
    NON_SKIPPABLE_CATEGORIES = POI_CATEGORIES.copy()
    NON_SKIPPABLE_CATEGORIES.update({
        u'chapter': u'Chapter',
    })
    CATEGORIES = {
        u'sponsor': u'Sponsor',
        u'intro': u'Intermission/Intro Animation',
        u'outro': u'Endcards/Credits',
        u'selfpromo': u'Unpaid/Self Promotion',
        u'preview': u'Preview/Recap',
        u'filler': u'Filler Tangent',
        u'interaction': u'Interaction Reminder',
        u'music_offtopic': u'Non-Music Section',
    }
    CATEGORIES.update(NON_SKIPPABLE_CATEGORIES)

    def __init__(self, downloader, categories=None, api=u'https://sponsor.ajay.app'):
        FFmpegPostProcessor.__init__(self, downloader)
        self._categories = tuple(categories or self.CATEGORIES.keys())
        self._API_URL = api if re.match(u'https?://', api) else u'https://' + api

    def run(self, info):
        extractor = info[u'extractor_key']
        if extractor not in self.EXTRACTORS:
            self.to_screen('SponsorBlock is not supported for %s' % extractor)
            return [], info

        self.to_screen(u'Fetching SponsorBlock segments')
        info[u'sponsorblock_chapters'] = self._get_sponsor_chapters(info, info.get(u'duration'))
        return [], info

    def _get_sponsor_chapters(self, info, duration):
        segments = self._get_sponsor_segments(info[u'id'], self.EXTRACTORS[info[u'extractor_key']])

        def duration_filter(s):
            start_end = s[u'segment']
            # Ignore entire video segments (https://wiki.sponsor.ajay.app/w/Types).
            if start_end == (0, 0):
                return False
            # Segments that are less than a second are likely mistakes
            if start_end[1] - start_end[0] < 1:
                return False
            # Ignore milliseconds difference at the beginning.
            if start_end[0] <= 1:
                start_end[0] = 0
            # Make POI chapters 1 sec so that we can properly mark them
            if s[u'category'] in self.POI_CATEGORIES:
                start_end[1] += 1
            # Ignore milliseconds difference at the end.
            # Never allow the segment to exceed the video.
            if duration and duration - start_end[1] <= 1:
                start_end[1] = duration
            # SponsorBlock duration may be absent or it may deviate from the real one.
            diff = abs(duration - s[u'videoDuration']) if s[u'videoDuration'] else 0
            return diff < 1 or (diff < 5 and diff / (start_end[1] - start_end[0]) < 0.05)

        duration_match = [s for s in segments if duration_filter(s)]
        if len(duration_match) != len(segments):
            self.report_warning(u'Some SponsorBlock segments are from a video of different duration, maybe from an old version of this video')

        def to_chapter(s):
            (start, end), cat = s[u'segment'], s[u'category']
            title = s[u'description'] if cat == u'chapter' else self.CATEGORIES[cat]
            return {
                u'start_time': start,
                u'end_time': end,
                u'category': cat,
                u'title': title,
                u'type': s[u'actionType'],
                u'_categories': [(cat, start, end, title)],
            }

        sponsor_chapters = [to_chapter(s) for s in duration_match]
        if not sponsor_chapters:
            self.to_screen(u'No matching segments were found in the SponsorBlock database')
        else:
            self.to_screen('Found %d segments in the SponsorBlock database' % len(sponsor_chapters))
        return sponsor_chapters

    def _get_sponsor_segments(self, video_id, service):
        video_hash = hashlib.sha256(video_id.encode(u'ascii')).hexdigest()
        # SponsorBlock API recommends using first 4 hash characters.
        url = '%s/api/skipSegments/%s?' % (self._API_URL, video_hash[:4]) + urllib.urlencode({
            u'service': service,
            u'categories': json.dumps(self._categories),
            u'actionTypes': json.dumps([u'skip', u'poi', u'chapter']),
        })
        for d in self._download_json(url) or []:
            if d[u'videoID'] == video_id:
                return d[u'segments']
        return []
