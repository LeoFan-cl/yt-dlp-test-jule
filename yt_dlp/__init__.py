from __future__ import with_statement
from __future__ import print_function, unicode_literals, absolute_import
import sys

if sys.version_info < (2, 7):
    raise ImportError(
        u'You are using an unsupported version of Python. Only Python versions 2.7 and above are supported by yt-dlp')

__license__ = u'The Unlicense'
import collections
import getpass
import itertools
import optparse
import os
import re
import traceback
from io import open

from .cookies import SUPPORTED_BROWSERS, SUPPORTED_KEYRINGS, CookieLoadError
from .downloader.external import get_external_downloader
from .extractor import list_extractor_classes
# from .extractor.adobepass import MSO_INFO
from .networking.impersonate import ImpersonateTarget
from .globals import IN_CLI, plugin_dirs
from .options import parseOpts
from .plugins import load_all_plugins as _load_all_plugins
from .postprocessor import (
    FFmpegExtractAudioPP,
    FFmpegMergerPP,
    FFmpegPostProcessor,
    FFmpegSubtitlesConvertorPP,
    FFmpegThumbnailsConvertorPP,
    FFmpegVideoConvertorPP,
    FFmpegVideoRemuxerPP,
    MetadataFromFieldPP,
    MetadataParserPP,
)
from .update import Updater
from .utils import (
    NO_DEFAULT,
    POSTPROCESS_WHEN,
    DateRange,
    DownloadCancelled,
    DownloadError,
    FormatSorter,
    GeoUtils,
    PlaylistEntries,
    SameFileError,
    download_range_func,
    expand_path,
    float_or_none,
    format_field,
    int_or_none,
    join_nonempty,
    match_filter_func,
    parse_bytes,
    parse_duration,
    preferredencoding,
    read_batch_urls,
    read_stdin,
    render_table,
    setproctitle,
    shell_quote,
    traverse_obj,
    variadic,
    write_string,
)
from .utils.networking import std_headers
from .utils._utils import _UnsafeExtensionError
from .YoutubeDL import YoutubeDL


def _exit(status=0, *args):
    for msg in args:
        sys.stderr.write(msg)
    raise SystemExit(status)


def get_urls(urls, batchfile, verbose):
    u"""
    @param verbose      -1: quiet, 0: normal, 1: verbose
    """
    batch_urls = []
    if batchfile is not None:
        try:
            batch_urls = read_batch_urls(
                read_stdin(None if verbose == -1 else u'URLs') if batchfile == u'-'
                else open(expand_path(batchfile), encoding=u'utf-8', errors=u'ignore'))
            if verbose == 1:
                write_string(u'[debug] Batch file urls: ' + repr(batch_urls) + u'\n')
        except OSError:
            _exit(u'ERROR: batch file {0} could not be read'.format(batchfile))
    _enc = preferredencoding()
    return [
        url.strip().decode(_enc, u'ignore') if isinstance(url, str) else url.strip()
        for url in batch_urls + urls]


def print_extractor_information(opts, urls):
    out = u''
    if opts.list_extractors:
        # Importing GenericIE is currently slow since it imports YoutubeIE
        from .extractor.generic import GenericIE

        urls = dict.fromkeys(urls, False)
        for ie in list_extractor_classes(opts.age_limit):
            out += ie.IE_NAME + (u' (CURRENTLY BROKEN)' if not ie.working() else u'') + u'\n'
            if ie == GenericIE:
                matched_urls = [url for url, matched in urls.items() if not matched]
            else:
                matched_urls = tuple(ifilter(ie.suitable, urls.keys()))
                urls.update(dict.fromkeys(matched_urls, True))
            out += u''.join(u'  {0}\n'.format(url) for url in matched_urls)
    elif opts.list_extractor_descriptions:
        _SEARCHES = (u'cute kittens', u'slithering pythons', u'falling cat', u'angry poodle', u'purple fish', u'running tortoise', u'sleeping bunny', u'burping cow')
        out = u'\n'.join(
            ie.description(markdown=False, search_examples=_SEARCHES)
            for ie in list_extractor_classes(opts.age_limit) if ie.working() and ie.IE_DESC is not False)
    # elif opts.ap_list_mso:
    #     out = 'Supported TV Providers:\n{0}\n'.format(render_table(
    #         ['mso', 'mso name'],
    #         [[mso_id, mso_info['name']] for mso_id, mso_info in MSO_INFO.items()]))
    else:
        return False
    write_string(out, out=sys.stdout)
    return True


def set_compat_opts(opts):
    def _unused_compat_opt(name):
        if name not in opts.compat_opts:
            return False
        opts.compat_opts.discard(name)
        opts.compat_opts.update([u'*{0}'.format(name)])
        return True

    def set_default_compat(compat_name, opt_name, default=True, remove_compat=True):
        attr = getattr(opts, opt_name)
        if compat_name in opts.compat_opts:
            if attr is None:
                setattr(opts, opt_name, not default)
                return True
            else:
                if remove_compat:
                    _unused_compat_opt(compat_name)
                return False
        elif attr is None:
            setattr(opts, opt_name, default)
        return None

    set_default_compat(u'abort-on-error', u'ignoreerrors', u'only_download')
    set_default_compat(u'no-playlist-metafiles', u'allow_playlist_files')
    set_default_compat(u'no-clean-infojson', u'clean_infojson')
    if u'no-attach-info-json' in opts.compat_opts:
        if opts.embed_infojson:
            _unused_compat_opt(u'no-attach-info-json')
        else:
            opts.embed_infojson = False
    if u'format-sort' in opts.compat_opts:
        opts.format_sort.extend(FormatSorter.ytdl_default)
    elif u'prefer-vp9-sort' in opts.compat_opts:
        opts.format_sort.extend(FormatSorter._prefer_vp9_sort)

    if u'mtime-by-default' in opts.compat_opts:
        if opts.updatetime is None:
            opts.updatetime = True
        else:
            _unused_compat_opt(u'mtime-by-default')

    _video_multistreams_set = set_default_compat(u'multistreams', u'allow_multiple_video_streams', False, remove_compat=False)
    _audio_multistreams_set = set_default_compat(u'multistreams', u'allow_multiple_audio_streams', False, remove_compat=False)
    if _video_multistreams_set is False and _audio_multistreams_set is False:
        _unused_compat_opt(u'multistreams')
    if u'filename' in opts.compat_opts:
        if opts.outtmpl.get(u'default') is None:
            opts.outtmpl.update({u'default': u'%(title)s-%(id)s.%(ext)s'})
        else:
            _unused_compat_opt(u'filename')


def validate_options(opts):
    def validate(cndn, name, value=None, msg=None):
        if cndn:
            return True
        raise ValueError((msg or u'invalid {name} "{value}" given').format(name=name, value=value))

    def validate_in(name, value, items, msg=None):
        return validate(value is None or value in items, name, value, msg)

    def validate_regex(name, value, regex):
        return validate(value is None or re.match(regex, value), name, value)

    def validate_positive(name, value, strict=False):
        return validate(value is None or value > 0 or (not strict and value == 0),
                        name, value, u'{{name}} "{0}" must be positive'.format(value) + (u'' if strict else u' or 0'))

    def validate_minmax(min_val, max_val, min_name, max_name=None):
        if max_val is None or min_val is None or max_val >= min_val:
            return
        if not max_name:
            min_name, max_name = u'min {0}'.format(min_name), u'max {0}'.format(min_name)
        raise ValueError(u'{0} "{1}" must be must be greater than or equal to {2} "{3}"'.format(
            max_name, max_val, min_name, min_val))

    # Usernames and passwords
    validate(sum(imap(bool, (opts.usenetrc, opts.netrc_cmd, opts.username))) <= 1, u'.netrc',
             msg=u'{name}, netrc command and username/password are mutually exclusive options')
    validate(opts.password is None or opts.username is not None, u'account username', msg=u'{name} missing')
    validate(opts.ap_password is None or opts.ap_username is not None,
             u'TV Provider account username', msg=u'{name} missing')
    # validate_in('TV Provider', opts.ap_mso, MSO_INFO,
    #             'Unsupported {name} "{value}", use --ap-list-mso to get a list of supported TV Providers')

    # Numbers
    validate_positive(u'autonumber start', opts.autonumber_start)
    validate_positive(u'autonumber size', opts.autonumber_size, True)
    validate_positive(u'concurrent fragments', opts.concurrent_fragment_downloads, True)
    validate_positive(u'playlist start', opts.playliststart, True)
    if opts.playlistend != -1:
        validate_minmax(opts.playliststart, opts.playlistend, u'playlist start', u'playlist end')

    # Time ranges
    validate_positive(u'subtitles sleep interval', opts.sleep_interval_subtitles)
    validate_positive(u'requests sleep interval', opts.sleep_interval_requests)
    validate_positive(u'sleep interval', opts.sleep_interval)
    validate_positive(u'max sleep interval', opts.max_sleep_interval)
    if opts.sleep_interval is None:
        validate(
            opts.max_sleep_interval is None, u'min sleep interval',
            msg=u'{name} must be specified; use --min-sleep-interval')
    elif opts.max_sleep_interval is None:
        opts.max_sleep_interval = opts.sleep_interval
    else:
        validate_minmax(opts.sleep_interval, opts.max_sleep_interval, u'sleep interval')

    if opts.wait_for_video is not None:
        parts = opts.wait_for_video.split(u'-', 1)
        min_wait, max_wait, _ = list(imap(parse_duration, parts + [None] if len(parts) == 2 else parts))
        validate(min_wait is not None and not (max_wait is None and u'-' in opts.wait_for_video),
                 u'time range to wait for video', opts.wait_for_video)
        validate_minmax(min_wait, max_wait, u'time range to wait for video')
        opts.wait_for_video = (min_wait, max_wait)

    # Format sort
    for f in opts.format_sort:
        validate_regex(u'format sorting', f, FormatSorter.regex)

    # Postprocessor formats
    if opts.convertsubtitles == u'none':
        opts.convertsubtitles = None
    if opts.convertthumbnails == u'none':
        opts.convertthumbnails = None

    validate_regex(u'merge output format', opts.merge_output_format,
                   ur'({0})(/({0}))*'.format(u'|'.join(imap(re.escape, FFmpegMergerPP.SUPPORTED_EXTS))))
    validate_regex(u'audio format', opts.audioformat, FFmpegExtractAudioPP.FORMAT_RE)
    validate_in(u'subtitle format', opts.convertsubtitles, FFmpegSubtitlesConvertorPP.SUPPORTED_EXTS)
    validate_regex(u'thumbnail format', opts.convertthumbnails, FFmpegThumbnailsConvertorPP.FORMAT_RE)
    validate_regex(u'recode video format', opts.recodevideo, FFmpegVideoConvertorPP.FORMAT_RE)
    validate_regex(u'remux video format', opts.remuxvideo, FFmpegVideoRemuxerPP.FORMAT_RE)
    if opts.audioquality:
        opts.audioquality = opts.audioquality.strip(u'k').strip(u'K')
        # int_or_none prevents inf, nan
        validate_positive(u'audio quality', int_or_none(float_or_none(opts.audioquality), default=0))

    # Retries
    def parse_retries(name, value):
        if value is None:
            return None
        elif value in (u'inf', u'infinite'):
            return float(u'inf')
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            validate(False, u'{0} retry count'.format(name), value)
        validate_positive(u'{0} retry count'.format(name), int_value)
        return int_value

    opts.retries = parse_retries(u'download', opts.retries)
    opts.fragment_retries = parse_retries(u'fragment', opts.fragment_retries)
    opts.extractor_retries = parse_retries(u'extractor', opts.extractor_retries)
    opts.file_access_retries = parse_retries(u'file access', opts.file_access_retries)

    # Retry sleep function
    def parse_sleep_func(expr):
        NUMBER_RE = ur'\d+(?:\.\d+)?'
        m = re.match(
            ur'(?:(linear|exp)=)?({0})(?::({0})?)?(?::({0}))?$'.format(NUMBER_RE),
            expr.strip())
        op, start, limit, step = (m.groups() + (None, None))[:4]

        if op == u'exp':
            return lambda n: min(float(start) * (float(step or 2) ** n), float(limit or u'inf'))
        else:
            default_step = start if op or limit else 0
            return lambda n: min(float(start) + float(step or default_step) * n, float(limit or u'inf'))

    for key, expr in opts.retry_sleep.items():
        if not expr:
            del opts.retry_sleep[key]
            continue
        try:
            opts.retry_sleep[key] = parse_sleep_func(expr)
        except AttributeError:
            raise ValueError(u'invalid {0} retry sleep expression {1!r}'.format(key, expr))

    # Bytes
    def validate_bytes(name, value, strict_positive=False):
        if value is None:
            return None
        numeric_limit = parse_bytes(value)
        validate(numeric_limit is not None, name, value)
        if strict_positive:
            validate_positive(name, numeric_limit, True)
        return numeric_limit

    opts.ratelimit = validate_bytes(u'rate limit', opts.ratelimit, True)
    opts.throttledratelimit = validate_bytes(u'throttled rate limit', opts.throttledratelimit)
    opts.min_filesize = validate_bytes(u'min filesize', opts.min_filesize)
    opts.max_filesize = validate_bytes(u'max filesize', opts.max_filesize)
    opts.buffersize = validate_bytes(u'buffer size', opts.buffersize, True)
    opts.http_chunk_size = validate_bytes(u'http chunk size', opts.http_chunk_size)

    # Output templates
    def validate_outtmpl(tmpl, msg):
        err = YoutubeDL.validate_outtmpl(tmpl)
        if err:
            raise ValueError(u'invalid {0} "{1}": {2}'.format(msg, tmpl, err))

    for k, tmpl in opts.outtmpl.items():
        validate_outtmpl(tmpl, u'{0} output template'.format(k))
    for type_, tmpl_list in opts.forceprint.items():
        for tmpl in tmpl_list:
            validate_outtmpl(tmpl, u'{0} print template'.format(type_))
    for type_, tmpl_list in opts.print_to_file.items():
        for tmpl, file in tmpl_list:
            validate_outtmpl(tmpl, u'{0} print to file template'.format(type_))
            validate_outtmpl(file, u'{0} print to file filename'.format(type_))
    validate_outtmpl(opts.sponsorblock_chapter_title, u'SponsorBlock chapter title')
    for k, tmpl in opts.progress_template.items():
        k = u'{0} console title'.format(k[:-6]) if u'-title' in k else u'{0} progress'.format(k)
        validate_outtmpl(tmpl, u'{0} template'.format(k))

    outtmpl_default = opts.outtmpl.get(u'default')
    if outtmpl_default == u'':
        opts.skip_download = None
        del opts.outtmpl[u'default']

    def parse_chapters(name, value, advanced=False):
        parse_timestamp = lambda x: float(u'inf') if x in (u'inf', u'infinite') else parse_duration(x)
        TIMESTAMP_RE = ur'''(?x)(?:
            (?P<start_sign>-?)(?P<start>[^-]+)
        )?\s*-\s*(?:
            (?P<end_sign>-?)(?P<end>[^-]+)
        )?'''

        chapters, ranges, from_url = [], [], False
        for regex in value or []:
            if advanced and regex == u'*from-url':
                from_url = True
                continue
            elif not regex.startswith(u'*'):
                try:
                    chapters.append(re.compile(regex))
                except re.error, err:
                    raise ValueError(u'invalid {0} regex "{1}" - {2}'.format(name, regex, err))
                continue

            for range_ in imap(unicode.strip, regex[1:].split(u',')):
                mobj = range_ != u'-' and re.match(TIMESTAMP_RE + u'$', range_)
                dur = mobj and [parse_timestamp(mobj.group(u'start') or u'0'), parse_timestamp(mobj.group(u'end') or u'inf')]
                signs = mobj and (mobj.group(u'start_sign'), mobj.group(u'end_sign'))

                err = None
                if None in (dur or [None]):
                    err = u'Must be of the form "*start-end"'
                elif not advanced and any(signs):
                    err = u'Negative timestamps are not allowed'
                else:
                    dur[0] *= -1 if signs[0] else 1
                    dur[1] *= -1 if signs[1] else 1
                    if dur[1] == float(u'-inf'):
                        err = u'"-inf" is not a valid end'
                if err:
                    raise ValueError(u'invalid {0} time range "{1}". {2}'.format(name, regex, err))
                ranges.append(dur)

        return chapters, ranges, from_url

    opts.remove_chapters, opts.remove_ranges, _ = parse_chapters(u'--remove-chapters', opts.remove_chapters)
    opts.download_ranges = download_range_func(*parse_chapters(u'--download-sections', opts.download_ranges, True))

    # Cookies from browser
    if opts.cookiesfrombrowser:
        container = None
        mobj = re.match(ur'''(?x)
            (?P<name>[^+:]+)
            (?:\s*\+\s*(?P<keyring>[^:]+))?
            (?:\s*:\s*(?!:)(?P<profile>.+?))?
            (?:\s*::\s*(?P<container>.+))?$
        ''', opts.cookiesfrombrowser)
        if mobj is None:
            raise ValueError(u'invalid cookies from browser arguments: {0}'.format(opts.cookiesfrombrowser))
        browser_name, keyring, profile, container = mobj.group(u'name', u'keyring', u'profile', u'container')
        browser_name = browser_name.lower()
        if browser_name not in SUPPORTED_BROWSERS:
            raise ValueError(u'unsupported browser specified for cookies: "{0}". '
                             u'Supported browsers are: {1}'.format(browser_name, u", ".join(sorted(SUPPORTED_BROWSERS))))
        if keyring is not None:
            keyring = keyring.upper()
            if keyring not in SUPPORTED_KEYRINGS:
                raise ValueError(u'unsupported keyring specified for cookies: "{0}". '
                                 u'Supported keyrings are: {1}'.format(keyring, u", ".join(sorted(SUPPORTED_KEYRINGS))))
        opts.cookiesfrombrowser = (browser_name, profile, keyring, container)

    if opts.impersonate is not None:
        opts.impersonate = ImpersonateTarget.from_str(opts.impersonate.lower())

    # MetadataParser
    def metadataparser_actions(f):
        if isinstance(f, unicode):
            cmd = u'--parse-metadata {0}'.format(shell_quote(f))
            try:
                actions = [MetadataFromFieldPP.to_action(f)]
            except Exception, err:
                raise ValueError(u'{0} is invalid; {1}'.format(cmd, err))
        else:
            cmd = u'--replace-in-metadata {0}'.format(shell_quote(f))
            actions = ((MetadataParserPP.Actions.REPLACE, x) + f[1:] for x in f[0].split(u','))

        for action in actions:
            try:
                MetadataParserPP.validate_action(*action)
            except Exception, err:
                raise ValueError(u'{0} is invalid; {1}'.format(cmd, err))
            yield action

    if opts.metafromtitle is not None:
        opts.parse_metadata.setdefault(u'pre_process', []).append(u'title:{0}'.format(opts.metafromtitle))
    opts.parse_metadata = dict(
        (k, list(itertools.chain(*imap(metadataparser_actions, v))))
        for k, v in opts.parse_metadata.items()
    )

    # Other options
    opts.plugin_dirs = opts.plugin_dirs
    if opts.plugin_dirs is None:
        opts.plugin_dirs = [u'default']

    if opts.playlist_items is not None:
        try:
            tuple(PlaylistEntries.parse_playlist_items(opts.playlist_items))
        except Exception, err:
            raise ValueError(u'Invalid playlist-items {0!r}: {1}'.format(opts.playlist_items, err))

    opts.geo_bypass_country, opts.geo_bypass_ip_block = None, None
    if opts.geo_bypass.lower() not in (u'default', u'never'):
        try:
            GeoUtils.random_ipv4(opts.geo_bypass)
        except Exception:
            raise ValueError(u'Unsupported --xff "{0}"'.format(opts.geo_bypass))
        if len(opts.geo_bypass) == 2:
            opts.geo_bypass_country = opts.geo_bypass
        else:
            opts.geo_bypass_ip_block = opts.geo_bypass
    opts.geo_bypass = opts.geo_bypass.lower() != u'never'

    opts.match_filter = match_filter_func(opts.match_filter, opts.breaking_match_filter)

    if opts.download_archive is not None:
        opts.download_archive = expand_path(opts.download_archive)

    if opts.ffmpeg_location is not None:
        opts.ffmpeg_location = expand_path(opts.ffmpeg_location)

    if opts.user_agent is not None:
        opts.headers.setdefault(u'User-Agent', opts.user_agent)
    if opts.referer is not None:
        opts.headers.setdefault(u'Referer', opts.referer)

    if opts.no_sponsorblock:
        opts.sponsorblock_mark = opts.sponsorblock_remove = set()

    default_downloader = None
    for proto, path in opts.external_downloader.items():
        if path == u'native':
            continue
        ed = get_external_downloader(path)
        if ed is None:
            raise ValueError(
                u'No such {0}external downloader "{1}"'.format(format_field(proto, None, u"%s ", ignore=u"default"), path))
        elif ed and proto == u'default':
            default_downloader = ed.get_basename()

    for policy in opts.color.values():
        if policy not in (u'always', u'auto', u'auto-tty', u'no_color', u'no_color-tty', u'never'):
            raise ValueError(u'"{0}" is not a valid color policy'.format(policy))

    warnings, deprecation_warnings = [], []

    # Common mistake: -f best
    if opts.format == u'best':
        warnings.append(u'.\n         '.join((
            u'"-f best" selects the best pre-merged format which is often not the best option',
            u'To let yt-dlp download and merge the best available formats, simply do not pass any format selection',
            u'If you know what you are doing and want only the best pre-merged format, use "-f b" instead to suppress this warning')))

    # Common mistake: -f mp4
    if opts.format == u'mp4':
        warnings.append(u'.\n         '.join((
            u'"-f mp4" selects the best pre-merged mp4 format which is often not what\'s intended',
            u'Pre-merged mp4 formats are not available from all sites, or may only be available in lower quality',
            u'To prioritize the best h264 video and aac audio in an mp4 container, use "-t mp4" instead',
            u'If you know what you are doing and want a pre-merged mp4 format, use "-f b[ext=mp4]" instead to suppress this warning')))

    # --(postprocessor/downloader)-args without name
    def report_args_compat(name, value, key1, key2=None, where=None):
        if key1 in value and key2 not in value:
            warnings.append(u'{0} arguments given without specifying name. '
                            u'The arguments will be given to {1}'.format(name.title(), where or u'all {0}'.format(name)))
            return True
        return False

    if report_args_compat(u'external downloader', opts.external_downloader_args,
                          u'default', where=default_downloader) and default_downloader:
        # Compat with youtube-dl's behavior. See https://github.com/ytdl-org/youtube-dl/commit/49c5293014bc11ec8c009856cd63cffa6296c1e1
        opts.external_downloader_args.setdefault(default_downloader, opts.external_downloader_args.pop(u'default'))

    if report_args_compat(u'post-processor', opts.postprocessor_args, u'default-compat', u'default'):
        opts.postprocessor_args[u'default'] = opts.postprocessor_args.pop(u'default-compat')
        opts.postprocessor_args.setdefault(u'sponskrub', [])

    def report_conflict(arg1, opt1, arg2=u'--allow-unplayable-formats', opt2=u'allow_unplayable_formats',
                        val1=NO_DEFAULT, val2=NO_DEFAULT, default=False):
        if val2 is NO_DEFAULT:
            val2 = getattr(opts, opt2)
        if not val2:
            return

        if val1 is NO_DEFAULT:
            val1 = getattr(opts, opt1)
        if val1:
            warnings.append(u'{0} is ignored since {1} was given'.format(arg1, arg2))
        setattr(opts, opt1, default)

    # Conflicting options
    report_conflict(u'--playlist-reverse', u'playlist_reverse', u'--playlist-random', u'playlist_random')
    report_conflict(u'--playlist-reverse', u'playlist_reverse', u'--lazy-playlist', u'lazy_playlist')
    report_conflict(u'--playlist-random', u'playlist_random', u'--lazy-playlist', u'lazy_playlist')
    report_conflict(u'--dateafter', u'dateafter', u'--date', u'date', default=None)
    report_conflict(u'--datebefore', u'datebefore', u'--date', u'date', default=None)
    report_conflict(u'--exec-before-download', u'exec_before_dl_cmd',
                    u'"--exec before_dl:"', u'exec_cmd', val2=opts.exec_cmd.get(u'before_dl'))
    report_conflict(u'--id', u'useid', u'--output', u'outtmpl', val2=opts.outtmpl.get(u'default'))
    report_conflict(u'--remux-video', u'remuxvideo', u'--recode-video', u'recodevideo')
    report_conflict(u'--sponskrub', u'sponskrub', u'--remove-chapters', u'remove_chapters')
    report_conflict(u'--sponskrub', u'sponskrub', u'--sponsorblock-mark', u'sponsorblock_mark')
    report_conflict(u'--sponskrub', u'sponskrub', u'--sponsorblock-remove', u'sponsorblock_remove')
    report_conflict(u'--sponskrub-cut', u'sponskrub_cut', u'--split-chapter', u'split_chapters',
                    val1=opts.sponskrub and opts.sponskrub_cut)

    # Conflicts with --allow-unplayable-formats
    report_conflict(u'--embed-metadata', u'addmetadata')
    report_conflict(u'--embed-chapters', u'addchapters')
    report_conflict(u'--embed-info-json', u'embed_infojson')
    report_conflict(u'--embed-subs', u'embedsubtitles')
    report_conflict(u'--embed-thumbnail', u'embedthumbnail')
    report_conflict(u'--extract-audio', u'extractaudio')
    report_conflict(u'--fixup', u'fixup', val1=opts.fixup not in (None, u'never', u'ignore'), default=u'never')
    report_conflict(u'--recode-video', u'recodevideo')
    report_conflict(u'--remove-chapters', u'remove_chapters', default=[])
    report_conflict(u'--remux-video', u'remuxvideo')
    report_conflict(u'--sponskrub', u'sponskrub')
    report_conflict(u'--sponsorblock-remove', u'sponsorblock_remove', default=set())
    report_conflict(u'--xattrs', u'xattrs')

    # Fully deprecated options
    def report_deprecation(val, old, new=None):
        if not val:
            return
        deprecation_warnings.append(
            u'{0} is deprecated and may be removed in a future version. Use {1} instead'.format(old, new) if new
            else u'{0} is deprecated and may not work as expected'.format(old))

    report_deprecation(opts.sponskrub, u'--sponskrub', u'--sponsorblock-mark or --sponsorblock-remove')
    report_deprecation(not opts.prefer_ffmpeg, u'--prefer-avconv', u'ffmpeg')
    # report_deprecation(opts.include_ads, '--include-ads')  # We may re-implement this in future
    # report_deprecation(opts.call_home, '--call-home')  # We may re-implement this in future
    # report_deprecation(opts.writeannotations, '--write-annotations')  # It's just that no website has it

    # Dependent options
    opts.date = DateRange.day(opts.date) if opts.date else DateRange(opts.dateafter, opts.datebefore)

    if opts.exec_before_dl_cmd:
        opts.exec_cmd[u'before_dl'] = opts.exec_before_dl_cmd

    if opts.useid:  # --id is not deprecated in youtube-dl
        opts.outtmpl[u'default'] = u'%(id)s.%(ext)s'

    if opts.overwrites:  # --force-overwrites implies --no-continue
        opts.continue_dl = False

    if (opts.addmetadata or opts.sponsorblock_mark) and opts.addchapters is None:
        # Add chapters when adding metadata or marking sponsors
        opts.addchapters = True

    if opts.extractaudio and not opts.keepvideo and opts.format is None:
        # Do not unnecessarily download audio
        opts.format = u'bestaudio/best'

    if opts.getcomments and opts.writeinfojson is None and not opts.embed_infojson:
        # If JSON is not printed anywhere, but comments are requested, save it to file
        if not opts.dumpjson or opts.print_json or opts.dump_single_json:
            opts.writeinfojson = True

    if opts.allsubtitles and not (opts.embedsubtitles or opts.writeautomaticsub):
        # --all-sub automatically sets --write-sub if --write-auto-sub is not given
        opts.writesubtitles = True

    if opts.addmetadata and opts.embed_infojson is None:
        # If embedding metadata and infojson is present, embed it
        opts.embed_infojson = u'if_exists'

    # Ask for passwords
    if opts.username is not None and opts.password is None:
        opts.password = getpass.getpass(u'Type account password and press [Return]: ')
    if opts.ap_username is not None and opts.ap_password is None:
        opts.ap_password = getpass.getpass(u'Type TV provider account password and press [Return]: ')

    # compat option changes global state destructively; only allow from cli
    if u'allow-unsafe-ext' in opts.compat_opts:
        warnings.append(
            u'Using allow-unsafe-ext opens you up to potential attacks. '
            u'Use with great care!')
        _UnsafeExtensionError.sanitize_extension = lambda x, prepend=False: x

    return warnings, deprecation_warnings


def get_postprocessors(opts):
    for pp in opts.add_postprocessors:
        yield pp

    for when, actions in opts.parse_metadata.items():
        yield {
            u'key': u'MetadataParser',
            u'actions': actions,
            u'when': when,
        }
    sponsorblock_query = opts.sponsorblock_mark | opts.sponsorblock_remove
    if sponsorblock_query:
        yield {
            u'key': u'SponsorBlock',
            u'categories': sponsorblock_query,
            u'api': opts.sponsorblock_api,
            u'when': u'after_filter',
        }
    if opts.convertsubtitles:
        yield {
            u'key': u'FFmpegSubtitlesConvertor',
            u'format': opts.convertsubtitles,
            u'when': u'before_dl',
        }
    if opts.convertthumbnails:
        yield {
            u'key': u'FFmpegThumbnailsConvertor',
            u'format': opts.convertthumbnails,
            u'when': u'before_dl',
        }
    if opts.extractaudio:
        yield {
            u'key': u'FFmpegExtractAudio',
            u'preferredcodec': opts.audioformat,
            u'preferredquality': opts.audioquality,
            u'nopostoverwrites': opts.nopostoverwrites,
        }
    if opts.remuxvideo:
        yield {
            u'key': u'FFmpegVideoRemuxer',
            u'preferedformat': opts.remuxvideo,
        }
    if opts.recodevideo:
        yield {
            u'key': u'FFmpegVideoConvertor',
            u'preferedformat': opts.recodevideo,
        }
    # If ModifyChapters is going to remove chapters, subtitles must already be in the container.
    if opts.embedsubtitles:
        keep_subs = u'no-keep-subs' not in opts.compat_opts
        yield {
            u'key': u'FFmpegEmbedSubtitle',
            # already_have_subtitle = True prevents the file from being deleted after embedding
            u'already_have_subtitle': opts.writesubtitles and keep_subs,
        }
        if not opts.writeautomaticsub and keep_subs:
            opts.writesubtitles = True

    # ModifyChapters must run before FFmpegMetadataPP
    if opts.remove_chapters or sponsorblock_query:
        yield {
            u'key': u'ModifyChapters',
            u'remove_chapters_patterns': opts.remove_chapters,
            u'remove_sponsor_segments': opts.sponsorblock_remove,
            u'remove_ranges': opts.remove_ranges,
            u'sponsorblock_chapter_title': opts.sponsorblock_chapter_title,
            u'force_keyframes': opts.force_keyframes_at_cuts,
        }
    # FFmpegMetadataPP should be run after FFmpegVideoConvertorPP and
    # FFmpegExtractAudioPP as containers before conversion may not support
    # metadata (3gp, webm, etc.)
    # By default ffmpeg preserves metadata applicable for both
    # source and target containers. From this point the container won't change,
    # so metadata can be added here.
    if opts.addmetadata or opts.addchapters or opts.embed_infojson:
        yield {
            u'key': u'FFmpegMetadata',
            u'add_chapters': opts.addchapters,
            u'add_metadata': opts.addmetadata,
            u'add_infojson': opts.embed_infojson,
        }
    # Deprecated
    # This should be above EmbedThumbnail since sponskrub removes the thumbnail attachment
    # but must be below EmbedSubtitle and FFmpegMetadata
    # See https://github.com/yt-dlp/yt-dlp/issues/204 , https://github.com/faissaloo/SponSkrub/issues/29
    # If opts.sponskrub is None, sponskrub is used, but it silently fails if the executable can't be found
    if opts.sponskrub is not False:
        yield {
            u'key': u'SponSkrub',
            u'path': opts.sponskrub_path,
            u'args': opts.sponskrub_args,
            u'cut': opts.sponskrub_cut,
            u'force': opts.sponskrub_force,
            u'ignoreerror': opts.sponskrub is None,
            u'_from_cli': True,
        }
    if opts.embedthumbnail:
        yield {
            u'key': u'EmbedThumbnail',
            # already_have_thumbnail = True prevents the file from being deleted after embedding
            u'already_have_thumbnail': opts.writethumbnail,
        }
        if not opts.writethumbnail:
            opts.writethumbnail = True
            opts.outtmpl[u'pl_thumbnail'] = u''
    if opts.split_chapters:
        yield {
            u'key': u'FFmpegSplitChapters',
            u'force_keyframes': opts.force_keyframes_at_cuts,
        }
    # XAttrMetadataPP should be run after post-processors that may change file contents
    if opts.xattrs:
        yield {u'key': u'XAttrMetadata'}
    if opts.concat_playlist != u'never':
        yield {
            u'key': u'FFmpegConcat',
            u'only_multi_video': opts.concat_playlist != u'always',
            u'when': u'playlist',
        }
    # Exec must be the last PP of each category
    for when, exec_cmd in opts.exec_cmd.items():
        yield {
            u'key': u'Exec',
            u'exec_cmd': exec_cmd,
            u'when': when,
        }


ParsedOptions = collections.namedtuple(u'ParsedOptions', (u'parser', u'options', u'urls', u'ydl_opts'))


def parse_options(argv=None):
    u"""@returns ParsedOptions(parser, opts, urls, ydl_opts)"""
    parser, opts, urls = parseOpts(argv)
    urls = get_urls(urls, opts.batchfile, -1 if opts.quiet and not opts.verbose else opts.verbose)

    set_compat_opts(opts)
    try:
        warnings, deprecation_warnings = validate_options(opts)
    except ValueError, err:
        parser.error(u'{0}\n'.format(err))

    postprocessors = list(get_postprocessors(opts))

    print_only = bool(opts.forceprint) and all(k not in opts.forceprint for k in POSTPROCESS_WHEN[3:])
    any_getting = any(getattr(opts, k) for k in (
        u'dumpjson', u'dump_single_json', u'getdescription', u'getduration', u'getfilename',
        u'getformat', u'getid', u'getthumbnail', u'gettitle', u'geturl',
    ))
    if opts.quiet is None:
        opts.quiet = any_getting or opts.print_json or bool(opts.forceprint)

    playlist_pps = [pp for pp in postprocessors if pp.get(u'when') == u'playlist']
    write_playlist_infojson = (opts.writeinfojson and not opts.clean_infojson
                               and opts.allow_playlist_files and opts.outtmpl.get(u'pl_infojson') != u'')
    if not any((
        opts.extract_flat,
        opts.dump_single_json,
        opts.forceprint.get(u'playlist'),
        opts.print_to_file.get(u'playlist'),
        write_playlist_infojson,
    )):
        if not playlist_pps:
            opts.extract_flat = u'discard'
        elif playlist_pps == [{u'key': u'FFmpegConcat', u'only_multi_video': True, u'when': u'playlist'}]:
            opts.extract_flat = u'discard_in_playlist'

    final_ext = (
        opts.recodevideo if opts.recodevideo in FFmpegVideoConvertorPP.SUPPORTED_EXTS
        else opts.remuxvideo if opts.remuxvideo in FFmpegVideoRemuxerPP.SUPPORTED_EXTS
        else opts.audioformat if (opts.extractaudio and opts.audioformat in FFmpegExtractAudioPP.SUPPORTED_EXTS)
        else None)

    return ParsedOptions(parser, opts, urls, {
        u'usenetrc': opts.usenetrc,
        u'netrc_location': opts.netrc_location,
        u'netrc_cmd': opts.netrc_cmd,
        u'username': opts.username,
        u'password': opts.password,
        u'twofactor': opts.twofactor,
        u'videopassword': opts.videopassword,
        u'ap_mso': opts.ap_mso,
        u'ap_username': opts.ap_username,
        u'ap_password': opts.ap_password,
        u'client_certificate': opts.client_certificate,
        u'client_certificate_key': opts.client_certificate_key,
        u'client_certificate_password': opts.client_certificate_password,
        u'quiet': opts.quiet,
        u'no_warnings': opts.no_warnings,
        u'forceurl': opts.geturl,
        u'forcetitle': opts.gettitle,
        u'forceid': opts.getid,
        u'forcethumbnail': opts.getthumbnail,
        u'forcedescription': opts.getdescription,
        u'forceduration': opts.getduration,
        u'forcefilename': opts.getfilename,
        u'forceformat': opts.getformat,
        u'forceprint': opts.forceprint,
        u'print_to_file': opts.print_to_file,
        u'forcejson': opts.dumpjson or opts.print_json,
        u'dump_single_json': opts.dump_single_json,
        u'force_write_download_archive': opts.force_write_download_archive,
        u'simulate': (print_only or any_getting or None) if opts.simulate is None else opts.simulate,
        u'skip_download': opts.skip_download,
        u'format': opts.format,
        u'allow_unplayable_formats': opts.allow_unplayable_formats,
        u'ignore_no_formats_error': opts.ignore_no_formats_error,
        u'format_sort': opts.format_sort,
        u'format_sort_force': opts.format_sort_force,
        u'allow_multiple_video_streams': opts.allow_multiple_video_streams,
        u'allow_multiple_audio_streams': opts.allow_multiple_audio_streams,
        u'check_formats': opts.check_formats,
        u'listformats': opts.listformats,
        u'listformats_table': opts.listformats_table,
        u'outtmpl': opts.outtmpl,
        u'outtmpl_na_placeholder': opts.outtmpl_na_placeholder,
        u'paths': opts.paths,
        u'autonumber_size': opts.autonumber_size,
        u'autonumber_start': opts.autonumber_start,
        u'restrictfilenames': opts.restrictfilenames,
        u'windowsfilenames': opts.windowsfilenames,
        u'ignoreerrors': opts.ignoreerrors,
        u'force_generic_extractor': opts.force_generic_extractor,
        u'allowed_extractors': opts.allowed_extractors or [u'default'],
        u'ratelimit': opts.ratelimit,
        u'throttledratelimit': opts.throttledratelimit,
        u'overwrites': opts.overwrites,
        u'retries': opts.retries,
        u'file_access_retries': opts.file_access_retries,
        u'fragment_retries': opts.fragment_retries,
        u'extractor_retries': opts.extractor_retries,
        u'retry_sleep_functions': opts.retry_sleep,
        u'skip_unavailable_fragments': opts.skip_unavailable_fragments,
        u'keep_fragments': opts.keep_fragments,
        u'concurrent_fragment_downloads': opts.concurrent_fragment_downloads,
        u'buffersize': opts.buffersize,
        u'noresizebuffer': opts.noresizebuffer,
        u'http_chunk_size': opts.http_chunk_size,
        u'continuedl': opts.continue_dl,
        u'noprogress': opts.quiet if opts.noprogress is None else opts.noprogress,
        u'progress_with_newline': opts.progress_with_newline,
        u'progress_template': opts.progress_template,
        u'progress_delta': opts.progress_delta,
        u'playliststart': opts.playliststart,
        u'playlistend': opts.playlistend,
        u'playlistreverse': opts.playlist_reverse,
        u'playlistrandom': opts.playlist_random,
        u'lazy_playlist': opts.lazy_playlist,
        u'noplaylist': opts.noplaylist,
        u'logtostderr': opts.outtmpl.get(u'default') == u'-',
        u'consoletitle': opts.consoletitle,
        u'nopart': opts.nopart,
        u'updatetime': opts.updatetime,
        u'writedescription': opts.writedescription,
        u'writeannotations': opts.writeannotations,
        u'writeinfojson': opts.writeinfojson,
        u'allow_playlist_files': opts.allow_playlist_files,
        u'clean_infojson': opts.clean_infojson,
        u'getcomments': opts.getcomments,
        u'writethumbnail': opts.writethumbnail is True,
        u'write_all_thumbnails': opts.writethumbnail == u'all',
        u'writelink': opts.writelink,
        u'writeurllink': opts.writeurllink,
        u'writewebloclink': opts.writewebloclink,
        u'writedesktoplink': opts.writedesktoplink,
        u'writesubtitles': opts.writesubtitles,
        u'writeautomaticsub': opts.writeautomaticsub,
        u'allsubtitles': opts.allsubtitles,
        u'listsubtitles': opts.listsubtitles,
        u'subtitlesformat': opts.subtitlesformat,
        u'subtitleslangs': opts.subtitleslangs,
        u'matchtitle': opts.matchtitle,
        u'rejecttitle': opts.rejecttitle,
        u'max_downloads': opts.max_downloads,
        u'prefer_free_formats': opts.prefer_free_formats,
        u'trim_file_name': opts.trim_file_name,
        u'verbose': opts.verbose,
        u'dump_intermediate_pages': opts.dump_intermediate_pages,
        u'write_pages': opts.write_pages,
        u'load_pages': opts.load_pages,
        u'test': opts.test,
        u'keepvideo': opts.keepvideo,
        u'min_filesize': opts.min_filesize,
        u'max_filesize': opts.max_filesize,
        u'min_views': opts.min_views,
        u'max_views': opts.max_views,
        u'daterange': opts.date,
        u'cachedir': opts.cachedir,
        u'youtube_print_sig_code': opts.youtube_print_sig_code,
        u'age_limit': opts.age_limit,
        u'download_archive': opts.download_archive,
        u'break_on_existing': opts.break_on_existing,
        u'break_on_reject': opts.break_on_reject,
        u'break_per_url': opts.break_per_url,
        u'skip_playlist_after_errors': opts.skip_playlist_after_errors,
        u'cookiefile': opts.cookiefile,
        u'cookiesfrombrowser': opts.cookiesfrombrowser,
        u'legacyserverconnect': opts.legacy_server_connect,
        u'nocheckcertificate': opts.no_check_certificate,
        u'prefer_insecure': opts.prefer_insecure,
        u'enable_file_urls': opts.enable_file_urls,
        u'http_headers': opts.headers,
        u'proxy': opts.proxy,
        u'socket_timeout': opts.socket_timeout,
        u'bidi_workaround': opts.bidi_workaround,
        u'debug_printtraffic': opts.debug_printtraffic,
        u'prefer_ffmpeg': opts.prefer_ffmpeg,
        u'include_ads': opts.include_ads,
        u'default_search': opts.default_search,
        u'dynamic_mpd': opts.dynamic_mpd,
        u'extractor_args': opts.extractor_args,
        u'youtube_include_dash_manifest': opts.youtube_include_dash_manifest,
        u'youtube_include_hls_manifest': opts.youtube_include_hls_manifest,
        u'encoding': opts.encoding,
        u'extract_flat': opts.extract_flat,
        u'live_from_start': opts.live_from_start,
        u'wait_for_video': opts.wait_for_video,
        u'mark_watched': opts.mark_watched,
        u'merge_output_format': opts.merge_output_format,
        u'final_ext': final_ext,
        u'postprocessors': postprocessors,
        u'fixup': opts.fixup,
        u'source_address': opts.source_address,
        u'impersonate': opts.impersonate,
        u'call_home': opts.call_home,
        u'sleep_interval_requests': opts.sleep_interval_requests,
        u'sleep_interval': opts.sleep_interval,
        u'max_sleep_interval': opts.max_sleep_interval,
        u'sleep_interval_subtitles': opts.sleep_interval_subtitles,
        u'external_downloader': opts.external_downloader,
        u'download_ranges': opts.download_ranges,
        u'force_keyframes_at_cuts': opts.force_keyframes_at_cuts,
        u'list_thumbnails': opts.list_thumbnails,
        u'playlist_items': opts.playlist_items,
        u'xattr_set_filesize': opts.xattr_set_filesize,
        u'match_filter': opts.match_filter,
        u'color': opts.color,
        u'ffmpeg_location': opts.ffmpeg_location,
        u'hls_prefer_native': opts.hls_prefer_native,
        u'hls_use_mpegts': opts.hls_use_mpegts,
        u'hls_split_discontinuity': opts.hls_split_discontinuity,
        u'external_downloader_args': opts.external_downloader_args,
        u'postprocessor_args': opts.postprocessor_args,
        u'cn_verification_proxy': opts.cn_verification_proxy,
        u'geo_verification_proxy': opts.geo_verification_proxy,
        u'geo_bypass': opts.geo_bypass,
        u'geo_bypass_country': opts.geo_bypass_country,
        u'geo_bypass_ip_block': opts.geo_bypass_ip_block,
        u'warn_when_outdated': opts.update_self is None,
        u'_warnings': warnings,
        u'_deprecation_warnings': deprecation_warnings,
        u'compat_opts': opts.compat_opts,
    })


def _real_main(argv=None):
    setproctitle(u'yt-dlp')

    parser, opts, all_urls, ydl_opts = parse_options(argv)

    # Dump user agent
    if opts.dump_user_agent:
        ua = traverse_obj(opts.headers, u'User-Agent', casesense=False, default=std_headers[u'User-Agent'])
        write_string(u'{0}\n'.format(ua), out=sys.stdout)
        return

    if print_extractor_information(opts, all_urls):
        return

    # We may need ffmpeg_location without having access to the YoutubeDL instance
    # See https://github.com/yt-dlp/yt-dlp/issues/2191
    if opts.ffmpeg_location:
        FFmpegPostProcessor._ffmpeg_location.set(opts.ffmpeg_location)

    # load all plugins into the global lookup
    plugin_dirs.value = opts.plugin_dirs
    if plugin_dirs.value:
        _load_all_plugins()

    with YoutubeDL(ydl_opts) as ydl:
        pre_process = opts.update_self or opts.rm_cachedir
        actual_use = all_urls or opts.load_info_filename

        if opts.rm_cachedir:
            ydl.cache.remove()

        try:
            updater = Updater(ydl, opts.update_self)
            if opts.update_self and updater.update() and actual_use:
                if updater.cmd:
                    return updater.restart()
                # This code is reachable only for zip variant in py < 3.10
                # It makes sense to exit here, but the old behavior is to continue
                ydl.report_warning(u'Restart yt-dlp to use the updated version')
                # return 100, 'ERROR: The program must exit for the update to complete'
        except Exception:
            traceback.print_exc()
            ydl._download_retcode = 100

        if opts.list_impersonate_targets:

            known_targets = [
                # List of simplified targets we know are supported,
                # to help users know what dependencies may be required.
                (ImpersonateTarget(u'chrome'), u'curl_cffi'),
                (ImpersonateTarget(u'safari'), u'curl_cffi'),
                (ImpersonateTarget(u'firefox'), u'curl_cffi>=0.10'),
                (ImpersonateTarget(u'edge'), u'curl_cffi'),
                (ImpersonateTarget(u'tor'), u'curl_cffi>=0.11'),
            ]

            available_targets = ydl._get_available_impersonate_targets()

            def make_row(target, handler):
                return [
                    join_nonempty(target.client.title(), target.version, delim=u'-') or u'-',
                    join_nonempty((target.os or u'').title(), target.os_version, delim=u'-') or u'-',
                    handler,
                ]

            rows = [make_row(target, handler) for target, handler in available_targets]

            for known_target, known_handler in known_targets:
                if not any(
                    known_target in target and known_handler.startswith(handler)
                    for target, handler in available_targets
                ):
                    rows.insert(0, [
                        ydl._format_out(text, ydl.Styles.SUPPRESS)
                        for text in make_row(known_target, u'{0} (unavailable)'.format(known_handler))
                    ])

            ydl.to_screen(u'[info] Available impersonate targets')
            ydl.to_stdout(render_table([u'Client', u'OS', u'Source'], rows, extra_gap=2, delim=u'-'))
            return

        if not actual_use:
            if pre_process:
                return ydl._download_retcode

            args = sys.argv[1:] if argv is None else argv
            ydl.warn_if_short_id(args)

            # Show a useful error message and wait for keypress if not launched from shell on Windows
            if not args and os.name == u'nt' and getattr(sys, u'frozen', False):
                import ctypes.wintypes
                import msvcrt

                kernel32 = ctypes.WinDLL(u'Kernel32')

                buffer = (1 * ctypes.wintypes.DWORD)()
                attached_processes = kernel32.GetConsoleProcessList(buffer, 1)
                # If we only have a single process attached, then the executable was double clicked
                # When using `pyinstaller` with `--onefile`, two processes get attached
                is_onefile = hasattr(sys, u'_MEIPASS') and os.path.basename(sys._MEIPASS).startswith(u'_MEI')
                if attached_processes == 1 or (is_onefile and attached_processes == 2):
                    print(parser._generate_error_message(
                        u'Do not double-click the executable, instead call it from a command line.\n'
                        u'Please read the README for further information on how to use yt-dlp: '
                        u'https://github.com/yt-dlp/yt-dlp#readme'))
                    msvcrt.getch()
                    _exit(2)
            parser.error(
                u'You must provide at least one URL.\n'
                u'Type yt-dlp --help to see a list of all options.')

        parser.destroy()
        try:
            if opts.load_info_filename is not None:
                if all_urls:
                    ydl.report_warning(u'URLs are ignored due to --load-info-json')
                return ydl.download_with_info_file(expand_path(opts.load_info_filename))
            else:
                return ydl.download(all_urls)
        except DownloadCancelled:
            ydl.to_screen(u'Aborting remaining downloads')
            return 101


def main(argv=None):
    IN_CLI.value = True
    try:
        _exit(*variadic(_real_main(argv)))
    except (CookieLoadError, DownloadError):
        _exit(1)
    except SameFileError, e:
        _exit(u'ERROR: {0}'.format(e))
    except KeyboardInterrupt:
        _exit(u'\nERROR: Interrupted by user')
    except IOError, e:
        if e.errno == 32:
            # https://docs.python.org/3/library/signal.html#note-on-sigpipe
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            _exit(u'\nERROR: {0}'.format(e))
        else:
            raise
    except optparse.OptParseError, e:
        _exit(2, u'\n{0}'.format(e))


from .extractor import gen_extractors, list_extractors

__all__ = [
    u'YoutubeDL',
    u'gen_extractors',
    u'list_extractors',
    u'main',
    u'parse_options',
]
