from __future__ import division
from __future__ import with_statement
from __future__ import absolute_import
import collections
import functools
import json
import os
import re
import subprocess
import time
import threading

from .common import PostProcessor
from ..compat import compat_os_name
from ..utils import (
    MEDIA_EXTENSIONS,
    PostProcessingError,
    RetryManager,
    detect_exe_version,
    determine_ext,
    dfxp2srt,
    encodeArgument,
    float_or_none,
    get_exe_version as _get_exe_version_output,
    ISO639Utils,
    is_outdated_version,
    join_nonempty,
    orderedSet,
    Popen,
    prepend_extension,
    replace_extension,
    shell_quote,
    traverse_obj,
    variadic,
    write_json_file,
)
from itertools import ifilter
from io import open
from itertools import izip
from itertools import imap


EXT_TO_OUT_FORMATS = {
    u'aac': u'adts',
    u'flac': u'flac',
    u'm4a': u'ipod',
    u'mka': u'matroska',
    u'mkv': u'matroska',
    u'mpg': u'mpeg',
    u'ogv': u'ogg',
    u'ts': u'mpegts',
    u'wma': u'asf',
    u'wmv': u'asf',
    u'weba': u'webm',
    u'vtt': u'webvtt',
}
ACODECS = {
    # name: (ext, encoder, opts)
    u'mp3': (u'mp3', u'libmp3lame', ()),
    u'aac': (u'm4a', u'aac', (u'-f', u'adts')),
    u'm4a': (u'm4a', u'aac', (u'-bsf:a', u'aac_adtstoasc')),
    u'opus': (u'opus', u'libopus', ()),
    u'vorbis': (u'ogg', u'libvorbis', ()),
    u'flac': (u'flac', u'flac', ()),
    u'alac': (u'm4a', None, (u'-acodec', u'alac')),
    u'wav': (u'wav', None, (u'-f', u'wav')),
}


def create_mapping_re(supported):
    return re.compile(ur'{0}(?:/{0})*$'.format(ur'(?:\s*\w+\s*>)?\s*(?:{})\s*'.format(u'|'.join(supported))))


def resolve_mapping(source, mapping):
    u"""
    Get corresponding item from a mapping string like 'A>B/C>D/E'
    @returns    (target, error_message)
    """
    for pair in mapping.lower().split(u'/'):
        kv = pair.split(u'>', 1)
        if len(kv) == 1 or kv[0].strip() == source:
            target = kv[-1].strip()
            if target == source:
                return None, u'the file is already in the target format'
            return target, None
    return None, u'the format is not selected for conversion'


class _ContextVar(object):
    def __init__(self, name, default=None):
        self._name = name
        self._default = default
        self._local = threading.local()

    def get(self):
        return getattr(self._local, self._name, self._default)

    def set(self, value):
        old_value = self.get()
        setattr(self._local, self._name, value)
        return old_value

    def reset(self, token):
        setattr(self._local, self._name, token)


class cached_property(object):
    def __init__(self, func):
        self.func = func
        self.__doc__ = getattr(func, u'__doc__')

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.func(instance)
        setattr(instance, self.func.__name__, value)
        return value


class FFmpegPostProcessor(PostProcessor):
    _ffmpeg_location = _ContextVar(u'ffmpeg_location', default=None)

    def __init__(self, downloader=None):
        PostProcessor.__init__(self, downloader)
        self._prefer_ffmpeg = self.get_param(u'prefer_ffmpeg', True)
        self._paths = self._determine_executables()
        self._version_cache = {}
        self._features_cache = {}

    @staticmethod
    def get_versions_and_features(downloader=None):
        return FFmpegPostProcessor(downloader)._get_versions_and_features()

    @staticmethod
    def get_versions(downloader=None):
        return FFmpegPostProcessor.get_versions_and_features(downloader)[0]

    _ffmpeg_to_avconv = {u'ffmpeg': u'avconv', u'ffprobe': u'avprobe'}

    def _determine_executables(self):
        programs = list(self._ffmpeg_to_avconv.keys()) + list(self._ffmpeg_to_avconv.values())

        location = self.get_param(u'ffmpeg_location', self._ffmpeg_location.get())
        if location is None:
            return dict((p, p) for p in programs)

        if not os.path.exists(location):
            self.report_warning(
                u'ffmpeg-location %s does not exist. Ignoring.' % location)
            return dict((p, p) for p in programs)
        if os.path.isdir(location):
            dirname, basename, filename = location, None, None
        else:
            filename = os.path.basename(location)
            try:
                basename = p for p in programs if p in filename.next()
            except StopIteration:
                basename = u'ffmpeg'
            dirname = os.path.dirname(os.path.abspath(location))
            if basename in self._ffmpeg_to_avconv:
                self._prefer_ffmpeg = True

        paths = dict((p, os.path.join(dirname, p)) for p in programs)
        if basename and basename in filename:
            for p in programs:
                path = os.path.join(dirname, filename.replace(basename, p))
                if os.path.exists(path):
                    paths[p] = path
        return paths

    def _get_ffmpeg_version(self, prog):
        path = self._paths.get(prog)
        if path in self._version_cache:
            return self._version_cache[path], self._features_cache.get(path, {})
        out = _get_exe_version_output(path, [u'-bsfs'])
        ver = detect_exe_version(out) if out else False
        if ver:
            regexs = [
                ur'(?:\d+:)?([0-9.]+)-[0-9]+ubuntu[0-9.]+$',  # Ubuntu, see [1]
                ur'n([0-9.]+)$',  # Arch Linux
                # 1. http://www.ducea.com/2006/06/17/ubuntu-package-version-naming-explanation/
            ]
            for regex in regexs:
                mobj = re.search(regex, ver)
                if mobj:
                    ver = mobj.group(1)
        self._version_cache[path] = ver
        if prog != u'ffmpeg' or not out:
            return ver, {}

        mobj = re.search(ur'(?m)^\s+libavformat\s+(?:[0-9. ]+)\s+/\s+(?P<runtime>[0-9. ]+)', out)
        lavf_runtime_version = mobj.group(u'runtime').replace(u' ', u'') if mobj else None
        self._features_cache[path] = features = {
            u'fdk': u'--enable-libfdk-aac' in out,
            u'setts': u'setts' in out.splitlines(),
            u'needs_adtstoasc': is_outdated_version(lavf_runtime_version, u'57.56.100', False),
        }
        return ver, features

    def _get_versions_and_features(self):
        return dict((
            p, self._get_ffmpeg_version(p)[0]) for p in self._paths), dict((
            p, self._get_ffmpeg_version(p)[1]) for p in self._paths if self._get_ffmpeg_version(p)[1])

    def _get_version(self, kind):
        executables = (kind, )
        if not self._prefer_ffmpeg:
            executables = (kind, self._ffmpeg_to_avconv[kind])
        try:
            basename, version, features = ifilter(
                lambda x: x[1], ((p, self._get_ffmpeg_version(p)[0], self._get_ffmpeg_version(p)[1]) for p in executables)).next()
        except StopIteration:
            basename, version, features = None, None, {}

        if kind == u'ffmpeg':
            self.basename, self._features = basename, features
        else:
            self.probe_basename = basename
        return version

    @cached_property
    def _version(self):
        return self._get_version(u'ffmpeg')

    @cached_property
    def _probe_version(self):
        return self._get_version(u'ffprobe')

    @property
    def available(self):
        return bool(self._version)

    @property
    def probe_available(self):
        return bool(self._probe_version)

    @property
    def executable(self):
        return self._paths.get(self.basename)

    @property
    def probe_executable(self):
        return self._paths.get(self.probe_basename)

    @staticmethod
    def stream_copy_opts(copy=True, **_3to2kwargs):
        if u'ext' in _3to2kwargs: ext = _3to2kwargs[u'ext']; del _3to2kwargs[u'ext']
        else: ext = None
        for i in (u'-map', u'0'): yield i
        # Don't copy Apple TV chapters track, bin_data
        # See https://github.com/yt-dlp/yt-dlp/issues/2, #19042, #19024, https://trac.ffmpeg.org/ticket/6016
        for i in (u'-dn', u'-ignore_unknown'): yield i
        if copy:
            for i in (u'-c', u'copy'): yield i
        if ext in (u'mp4', u'mov', u'm4a'):
            for i in (u'-c:s', u'mov_text'): yield i

    def check_version(self):
        if not self.available:
            raise FFmpegPostProcessorError(u'ffmpeg not found. Please install or provide the path using --ffmpeg-location')

        required_version = u'10-0' if self.basename == u'avconv' else u'1.0'
        if is_outdated_version(self._version, required_version):
            self.report_warning(u'Your copy of %s is outdated, update %s to version %s or newer if you encounter any errors' % (
                self.basename, self.basename, required_version))

    def get_audio_codec(self, path):
        if not self.probe_available and not self.available:
            raise PostProcessingError(u'ffprobe and ffmpeg not found. Please install or provide the path using --ffmpeg-location')
        try:
            if self.probe_available:
                cmd = [
                    self.probe_executable,
                    encodeArgument(u'-show_streams')]
            else:
                cmd = [
                    self.executable,
                    encodeArgument(u'-i')]
            cmd.append(self._ffmpeg_filename_argument(path))
            self.write_debug(u'%s command line: %s' % (self.basename, shell_quote(cmd)))
            stdout, stderr, returncode = Popen.run(
                cmd, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (IOError, OSError), err:
            raise PostProcessingError(u'Cannot run %s: %s' % (self.basename, unicode(err)))
        if returncode != 0:
            raise PostProcessingError(u'%s returned error code %d' % (self.basename, returncode))
        output = stdout if self.probe_available else stderr
        if self.probe_available:
            audio_codec = None
            for line in output.split(u'\n'):
                if line.startswith(u'codec_name='):
                    audio_codec = line.split(u'=')[1].strip()
                elif line.strip() == u'codec_type=audio' and audio_codec is not None:
                    return audio_codec
        else:
            # Stream #FILE_INDEX:STREAM_INDEX[STREAM_ID](LANGUAGE): CODEC_TYPE: CODEC_NAME
            mobj = re.search(
                ur'Stream\s*#\d+:\d+(?:\[0x[0-9a-f]+\])?(?:\([a-z]{3}\))?:\s*Audio:\s*([0-9a-z]+)',
                output)
            if mobj:
                return mobj.group(1)
        return None

    def get_metadata_object(self, path, opts=[]):
        if self.probe_basename != u'ffprobe':
            if self.probe_available:
                self.report_warning(u'Only ffprobe is supported for metadata extraction')
            raise PostProcessingError(u'ffprobe not found. Please install or provide the path using --ffmpeg-location')
        self.check_version()

        cmd = [
            self.probe_executable,
            encodeArgument(u'-hide_banner'),
            encodeArgument(u'-show_format'),
            encodeArgument(u'-show_streams'),
            encodeArgument(u'-print_format'),
            encodeArgument(u'json'),
        ]

        cmd += opts
        cmd.append(self._ffmpeg_filename_argument(path))
        stdout = self.run_ffmpeg_probe(cmd)
        return json.loads(stdout)

    def get_stream_number(self, path, keys, value):
        streams = self.get_metadata_object(path)[u'streams']
        try:
            num =
                (i for i, stream in enumerate(streams) if traverse_obj(stream, keys, casesense=False) == value).next()
        except StopIteration:
            num = None
        return num, len(streams)

    def _fixup_chapters(self, info):
        last_chapter = traverse_obj(info, (u'chapters', -1))
        if last_chapter and not last_chapter.get(u'end_time'):
            last_chapter[u'end_time'] = self._get_real_video_duration(info[u'filepath'])

    def _get_real_video_duration(self, filepath, fatal=True):
        try:
            duration = float_or_none(
                traverse_obj(self.get_metadata_object(filepath), (u'format', u'duration')))
            if not duration:
                raise PostProcessingError(u'ffprobe returned empty duration')
            return duration
        except PostProcessingError, e:
            if fatal:
                raise PostProcessingError(u'Unable to determine video duration: %s' % e.msg)

    def run_ffmpeg(self, input_path, out_path, opts, **kwargs):
        self.real_run_ffmpeg([(input_path, opts)], [(out_path, [])], **kwargs)

    def run_ffmpeg_multiple_files(self, input_paths, out_path, opts, **kwargs):
        self.real_run_ffmpeg(
            [(path, []) for path in input_paths],
            [(out_path, opts)], **kwargs)

    def real_run_ffmpeg(self, input_path_opts, output_path_opts, **_3to2kwargs):
        if u'expected_retcodes' in _3to2kwargs: expected_retcodes = _3to2kwargs[u'expected_retcodes']; del _3to2kwargs[u'expected_retcodes']
        else: expected_retcodes = (0,)
        self.check_version()

        oldest_mtime = min(
            os.stat(path).st_mtime for path, _ in input_path_opts if path)

        cmd = [self.executable, encodeArgument(u'-y')]
        # avconv does not have repeat option
        if self.basename == u'ffmpeg':
            cmd += [encodeArgument(u'-loglevel'), encodeArgument(u'repeat+info')]

        def make_args(file, args, name, number):
            keys = [u'_%s%d' % (name, number), u'_%s' % name]
            if name == u'o':
                args += [u'-movflags', u'+faststart']
                if number == 1:
                    keys.append(u'')
            args += self._configuration_args(self.basename, keys)
            if name == u'i':
                args.append(u'-i')
            return (
                [encodeArgument(arg) for arg in args]
                + [self._ffmpeg_filename_argument(file)])

        for arg_type, path_opts in ((u'i', input_path_opts), (u'o', output_path_opts)):
            cmd += itertools.chain.from_iterable(
                make_args(path, list(opts), arg_type, i + 1)
                for i, (path, opts) in enumerate(path_opts) if path)

        self.write_debug(u'%s command line: %s' % (self.basename, shell_quote(cmd)))
        stdout, stderr, returncode = Popen.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if returncode not in expected_retcodes:
            raise FFmpegPostProcessorError(stderr)

        for path, _ in output_path_opts:
            if path:
                self.try_utime(path, oldest_mtime, oldest_mtime)
        return stderr

    @staticmethod
    def _ffmpeg_filename_argument(fn):
        # In order to pass string with spaces to ffmpeg, we can't just quote it.
        # It must be prepended with 'file:'
        # (This is not required for other executables)
        # Another problem is that both ffmpeg and ffprobe interpret backslash as
        # an escape character, so we must escaped that.
        # (This is not required for other executables)
        # And if the path starts with "http" or "https" we must not prepend "file:".
        # And if the path is '-', we must not prepend "file:".
        # And if the path starts with a drive letter, we must not prepend "file:"
        # if the OS is not Windows.
        # And if the path contains a colon, we must not prepend "file:" if it
        # is not a drive letter on Windows (ffmpeg thinks it's a protocol)
        # Another problem is that ffmpeg does not support UNC paths
        # (e.g. \\server\share\file) so we must not prepend "file:" to them.
        # Another problem is that ffprobe may not support relative paths
        # (e.g. ..\file) so we must not prepend "file:" to them.
        # Another problem is that ffmpeg may not support paths with special
        # characters (e.g. %) so we must not prepend "file:" to them.
        # Another problem is that ffmpeg may not support paths with spaces
        # if they are not quoted and prepended with "file:".
        # Another problem is that ffmpeg may not support paths with spaces
        # if they are quoted but not prepended with "file:".
        # Another problem is that ffmpeg may not support paths with spaces
        # if they are not quoted but prepended with "file:".
        # Another problem is that ffmpeg may not support paths with spaces
        # if they are quoted and prepended with "file:".
        if compat_os_name == u'nt' and re.match(ur'^[a-zA-Z]:\\', fn):
            return fn.replace(u'\\', u'\\\\')
        # On Windows, ffmpeg fails with "Protocol not found" if the path starts
        # with a drive letter and a colon (e.g. "C:").
        # See https://trac.ffmpeg.org/ticket/4243
        if re.match(ur'^[a-zA-Z]:', fn):
            return fn.replace(u'\\', u'/')
        if fn.startswith((u'http://', u'https://')):
            return fn
        return u'file:' + fn if fn != u'-' else fn

    @staticmethod
    def _quote_for_ffmpeg(string):
        # See https://ffmpeg.org/ffmpeg-utils.html#toc-Quoting-and-escaping
        # A sequence of '' produces '\\'''\\'';
        # final replace removes the empty '' between \\' \\'.
        string = string.replace(u"\'", ur"\'\\\'\'").replace(u"\'\'\'", u"\'")
        # Handle potential ' at string boundaries.
        string = string[1:] if string[0] == u"\'" else u"\'" + string
        return string[:-1] if string[-1] == u"\'" else string + u"\'"

    def force_keyframes(self, filename, timestamps):
        timestamps = orderedSet(timestamps)
        if timestamps[0] == 0:
            timestamps = timestamps[1:]
        keyframe_file = prepend_extension(filename, u'keyframes.temp')
        self.to_screen(u'Re-encoding "%s" with appropriate keyframes' % filename)
        self.run_ffmpeg(filename, keyframe_file, [
            self.stream_copy_opts(False, ext=determine_ext(filename)),
            u'-force_key_frames', u','.join(u'%f' % t for t in timestamps)])
        return keyframe_file

    def concat_files(self, in_files, out_file, concat_opts=None):
        u"""
        Use concat demuxer to concatenate multiple files having identical streams.

        Only inpoint, outpoint, and duration concat options are supported.
        See: https://ffmpeg.org/ffmpeg-formats.html#concat
        """
        concat_file = u'%s.concat' % out_file
        self.write_debug(u'Writing concat spec to %s' % concat_file)
        with open(concat_file, u'w', encoding=u'utf-8') as f:
            f.writelines(self._concat_spec(in_files, concat_opts))

        out_flags = list(self.stream_copy_opts(ext=determine_ext(out_file)))

        self.real_run_ffmpeg(
            [(concat_file, [u'-hide_banner', u'-nostdin', u'-f', u'concat', u'-safe', u'0'])],
            [(out_file, out_flags)])
        self._delete_downloaded_files(concat_file)

    @classmethod
    def _concat_spec(cls, in_files, concat_opts=None):
        if concat_opts is None:
            concat_opts = [{}] * len(in_files)
        yield u'ffconcat version 1.0\n'
        for file, opts in izip(in_files, concat_opts):
            yield u'file %s\n' % cls._quote_for_ffmpeg(cls._ffmpeg_filename_argument(file))
            # Iterate explicitly to yield the following directives in order, ignoring the rest.
            for directive in u'inpoint', u'outpoint', u'duration':
                if directive in opts:
                    yield u'%s %s\n' % (directive, opts[directive])


class FFmpegExtractAudioPP(FFmpegPostProcessor):
    COMMON_AUDIO_EXTS = MEDIA_EXTENSIONS.common_audio + (u'wma',)
    SUPPORTED_EXTS = tuple(ACODECS.keys())
    FORMAT_RE = create_mapping_re((u'best',) + SUPPORTED_EXTS)

    def __init__(self, downloader=None, preferredcodec=None, preferredquality=None, nopostoverwrites=False):
        FFmpegPostProcessor.__init__(self, downloader)
        self.mapping = preferredcodec or u'best'
        self._preferredquality = float_or_none(preferredquality)
        self._nopostoverwrites = nopostoverwrites

    def _quality_args(self, codec):
        if self._preferredquality is None:
            return []
        elif self._preferredquality > 10:
            return [u'-b:a', u'%sk' % self._preferredquality]

        limits = {
            u'libmp3lame': (10, 0),
            u'libvorbis': (0, 10),
            # FFmpeg's AAC encoder does not have an upper limit for the value of -q:a.
            # Experimentally, with values over 4, bitrate changes were minimal or non-existent
            u'aac': (0.1, 4),
            u'libfdk_aac': (1, 5),
        }.get(codec)
        if not limits:
            return []

        q = limits[1] + (limits[0] - limits[1]) * (self._preferredquality / 10)
        if codec == u'libfdk_aac':
            return [u'-vbr', u'%d' % int(q)]
        return [u'-q:a', u'%f' % q]

    def run_ffmpeg(self, path, out_path, codec, more_opts):
        if codec is None:
            acodec_opts = []
        else:
            acodec_opts = [u'-acodec', codec]
        opts = [u'-vn'] + acodec_opts + more_opts
        try:
            FFmpegPostProcessor.run_ffmpeg(self, path, out_path, opts)
        except FFmpegPostProcessorError, err:
            raise PostProcessingError(u'audio conversion failed: %s' % err.msg)

    @PostProcessor._restrict_to(images=False)
    def run(self, information):
        orig_path = path = information[u'filepath']
        target_format, _skip_msg = resolve_mapping(information[u'ext'], self.mapping)
        if target_format == u'best' and information[u'ext'] in self.COMMON_AUDIO_EXTS:
            target_format, _skip_msg = None, u'the file is already in a common audio format'
        if not target_format:
            self.to_screen(u'Not converting audio %s; %s' % (orig_path, _skip_msg))
            return [], information

        filecodec = self.get_audio_codec(path)
        if filecodec is None:
            raise PostProcessingError(u'WARNING: unable to obtain file audio codec with ffprobe')

        if filecodec == u'aac' and target_format in (u'm4a', u'best'):
            # Lossless, but in another container
            val = ACODECS[u'm4a'] + (u'copy',)
            extension, _, more_opts, acodec = val
        elif target_format == u'best' or target_format == filecodec:
            # Lossless if possible
            try:
                val = ACODECS[filecodec] + (u'copy',)
                extension, _, more_opts, acodec = val
            except KeyError:
                extension, acodec, more_opts = ACODECS[u'mp3']
        else:
            # We convert the audio (lossy if codec is lossy)
            extension, acodec, more_opts = ACODECS[target_format]
            if acodec == u'aac' and self._features.get(u'fdk'):
                acodec, more_opts = u'libfdk_aac', []

        more_opts = list(more_opts)
        if acodec != u'copy':
            more_opts = self._quality_args(acodec)

        temp_path = new_path = replace_extension(path, extension, information[u'ext'])

        if new_path == path:
            if acodec == u'copy':
                self.to_screen(u'Not converting audio %s; file is already in target format %s' % (orig_path, target_format))
                return [], information
            orig_path = prepend_extension(path, u'orig')
            temp_path = prepend_extension(path, u'temp')
        if (self._nopostoverwrites and os.path.exists(new_path)
                and os.path.exists(orig_path)):
            self.to_screen(u'Post-process file %s exists, skipping' % new_path)
            self._delete_downloaded_files(path)
            return [], information

        self.to_screen(u'Destination: %s' % new_path)
        self.run_ffmpeg(path, temp_path, acodec, more_opts)

        os.replace(path, orig_path)
        os.replace(temp_path, new_path)
        information[u'filepath'] = new_path
        information[u'ext'] = extension

        # Try to update the date time for extracted audio file.
        if information.get(u'filetime') is not None:
            self.try_utime(
                new_path, time.time(), information[u'filetime'], errnote=u'Cannot update utime of audio file')

        return [orig_path], information


class FFmpegVideoConvertorPP(FFmpegPostProcessor):
    SUPPORTED_EXTS = (
        tuple(sorted(MEDIA_EXTENSIONS.common_video + (u'gif',))) +
        tuple(sorted(MEDIA_EXTENSIONS.common_audio + (u'aac', u'vorbis')))
    )
    FORMAT_RE = create_mapping_re(SUPPORTED_EXTS)
    _ACTION = u'converting'

    def __init__(self, downloader=None, preferedformat=None):
        super(FFmpegVideoConvertorPP, self).__init__(downloader)
        self.mapping = preferedformat

    @staticmethod
    def _options(target_ext):
        for i in FFmpegPostProcessor.stream_copy_opts(False):
            yield i
        if target_ext == u'avi':
            for i in (u'-c:v', u'libxvid', u'-vtag', u'XVID'):
                yield i

    @PostProcessor._restrict_to(images=False)
    def run(self, info):
        filename, source_ext = info[u'filepath'], info[u'ext'].lower()
        target_ext, _skip_msg = resolve_mapping(source_ext, self.mapping)
        if _skip_msg:
            self.to_screen(u'Not %s media file "%s"; %s' % (self._ACTION, filename, _skip_msg))
            return [], info

        outpath = replace_extension(filename, target_ext, source_ext)
        self.to_screen(u'%s video from %s to %s; Destination: %s' % (
            self._ACTION.title(), source_ext, target_ext, outpath))
        self.run_ffmpeg(filename, outpath, self._options(target_ext))

        info[u'filepath'] = outpath
        info[u'format'] = info[u'ext'] = target_ext
        return [filename], info


class FFmpegVideoRemuxerPP(FFmpegVideoConvertorPP):
    _ACTION = u'remuxing'

    @staticmethod
    def _options(target_ext):
        for i in FFmpegPostProcessor.stream_copy_opts(True):
            yield i


class FFmpegEmbedSubtitlePP(FFmpegPostProcessor):
    SUPPORTED_EXTS = (u'mp4', u'mov', u'm4a', u'webm', u'mkv', u'mka')

    def __init__(self, downloader=None, already_have_subtitle=False):
        super(FFmpegEmbedSubtitlePP, self).__init__(downloader)
        self._already_have_subtitle = already_have_subtitle

    @PostProcessor._restrict_to(images=False)
    def run(self, info):
        if info[u'ext'] not in self.SUPPORTED_EXTS:
            self.to_screen(u'Subtitles can only be embedded in %s files' % u", ".join(self.SUPPORTED_EXTS))
            return [], info
        subtitles = info.get(u'requested_subtitles')
        if not subtitles:
            self.to_screen(u'There aren\'t any subtitles to embed')
            return [], info

        filename = info[u'filepath']

        # Disabled temporarily. There needs to be a way to override this
        # in case of duration actually mismatching in extractor
        # See: https://github.com/yt-dlp/yt-dlp/issues/1870, https://github.com/yt-dlp/yt-dlp/issues/1385
        u'''
        if info.get('duration') and not info.get('__real_download') and self._duration_mismatch(
                self._get_real_video_duration(filename, False), info['duration']):
            self.to_screen('Skipping %s since the real and expected durations mismatch' % self.pp_key())
            return [], info
        '''

        ext = info[u'ext']
        sub_langs, sub_names, sub_filenames = [], [], []
        webm_vtt_warn = False
        mp4_ass_warn = False

        for lang, sub_info in subtitles.items():
            if not os.path.exists(sub_info.get(u'filepath', u'')):
                self.report_warning(u'Skipping embedding %s subtitle because the file is missing' % lang)
                continue
            sub_ext = sub_info[u'ext']
            if sub_ext == u'json':
                self.report_warning(u'JSON subtitles cannot be embedded')
            elif ext != u'webm' or (ext == u'webm' and sub_ext == u'vtt'):
                sub_langs.append(lang)
                sub_names.append(sub_info.get(u'name'))
                sub_filenames.append(sub_info[u'filepath'])
            else:
                if not webm_vtt_warn and ext == u'webm' and sub_ext != u'vtt':
                    webm_vtt_warn = True
                    self.report_warning(u'Only WebVTT subtitles can be embedded in webm files')
            if not mp4_ass_warn and ext == u'mp4' and sub_ext == u'ass':
                mp4_ass_warn = True
                self.report_warning(u'ASS subtitles cannot be properly embedded in mp4 files; expect issues')

        if not sub_langs:
            return [], info

        input_files = [filename] + sub_filenames

        opts = list(self.stream_copy_opts(ext=info[u'ext'])) + [
            # Don't copy the existing subtitles, we may be running the
            # postprocessor a second time
            u'-map', u'-0:s',
        ]
        for i, (lang, name) in enumerate(izip(sub_langs, sub_names)):
            opts.extend([u'-map', u'%d:0' % (i + 1)])
            lang_code = ISO639Utils.short2long(lang) or lang
            opts.extend([u'-metadata:s:s:%d' % i, u'language=%s' % lang_code])
            if name:
                opts.extend([u'-metadata:s:s:%d' % i, u'handler_name=%s' % name,
                             u'-metadata:s:s:%d' % i, u'title=%s' % name])

        temp_filename = prepend_extension(filename, u'temp')
        self.to_screen(u'Embedding subtitles in "%s"' % filename)
        self.run_ffmpeg_multiple_files(input_files, temp_filename, opts)
        os.replace(temp_filename, filename)

        return [], info


class FFmpegMetadataPP(FFmpegPostProcessor):

    def __init__(self, downloader, add_metadata=True, add_chapters=True, add_infojson=u'if_exists'):
        FFmpegPostProcessor.__init__(self, downloader)
        self._add_metadata = add_metadata
        self._add_chapters = add_chapters
        self._add_infojson = add_infojson

    @staticmethod
    def _options(target_ext):
        audio_only = target_ext == u'm4a'
        for i in FFmpegPostProcessor.stream_copy_opts(not audio_only):
            yield i
        if audio_only:
            for i in (u'-vn', u'-acodec', u'copy'):
                yield i

    @PostProcessor._restrict_to(images=False)
    def run(self, info):
        self._fixup_chapters(info)
        filename, metadata_filename = info[u'filepath'], None
        files_to_delete, options = [], []
        if self._add_chapters and info.get(u'chapters'):
            metadata_filename = replace_extension(filename, u'meta')
            options.extend(self._get_chapter_opts(info[u'chapters'], metadata_filename))
            files_to_delete.append(metadata_filename)
        if self._add_metadata:
            options.extend(self._get_metadata_opts(info))

        if self._add_infojson:
            if info[u'ext'] in (u'mkv', u'mka'):
                infojson_filename = info.get(u'infojson_filename')
                options.extend(self._get_infojson_opts(info, infojson_filename))
                if not infojson_filename:
                    files_to_delete.append(info.get(u'infojson_filename'))
            elif self._add_infojson is True:
                self.to_screen(u'The info-json can only be attached to mkv/mka files')

        if not options:
            self.to_screen(u'There isn\'t any metadata to add')
            return [], info

        temp_filename = prepend_extension(filename, u'temp')
        self.to_screen(u'Adding metadata to "%s"' % filename)
        self.run_ffmpeg_multiple_files(
            (filename, metadata_filename), temp_filename,
            itertools.chain(self._options(info[u'ext']), *options))
        self._delete_downloaded_files(*files_to_delete)
        os.replace(temp_filename, filename)
        return [], info

    @staticmethod
    def _get_chapter_opts(chapters, metadata_filename):
        with open(metadata_filename, u'w', encoding=u'utf-8') as f:
            def ffmpeg_escape(text):
                return re.sub(ur'([\\=;#\n])', ur'\\\1', text)

            metadata_file_content = u';FFMETADATA1\n'
            for chapter in chapters:
                metadata_file_content += u'[CHAPTER]\nTIMEBASE=1/1000\n'
                metadata_file_content += u'START=%d\n' % (chapter[u'start_time'] * 1000)
                metadata_file_content += u'END=%d\n' % (chapter[u'end_time'] * 1000)
                chapter_title = chapter.get(u'title')
                if chapter_title:
                    metadata_file_content += u'title=%s\n' % ffmpeg_escape(chapter_title)
            f.write(metadata_file_content)
        yield (u'-map_metadata', u'1')

    def _get_metadata_opts(self, info):
        meta_prefix = u'meta'
        metadata = collections.defaultdict(dict)

        def add(meta_list, info_list=None):
            try:
                value =
                    info[key] for key in [meta_prefix + u'_'] + list(variadic(info_list or meta_list))
                    if info.get(key) is not None.next()
            except StopIteration:
                value = None
            if value not in (u'', None):
                value = u', '.join(imap(unicode, variadic(value)))
                value = value.replace(u'\0', u'')  # nul character cannot be passed in command line
                metadata[u'common'].update(dict.fromkeys(variadic(meta_list), value))

        # Info on media metadata/metadata supported by ffmpeg:
        # https://wiki.multimedia.cx/index.php/FFmpeg_Metadata
        # https://kdenlive.org/en/project/adding-meta-data-to-mp4-video/
        # https://kodi.wiki/view/Video_file_tagging

        add(u'title', (u'track', u'title'))
        add(u'date', u'upload_date')
        add((u'description', u'synopsis'), u'description')
        add((u'purl', u'comment'), u'webpage_url')
        add(u'track', u'track_number')
        add(u'artist', (u'artist', u'artists', u'creator', u'creators', u'uploader', u'uploader_id'))
        add(u'composer', (u'composer', u'composers'))
        add(u'genre', (u'genre', u'genres'))
        add(u'album')
        add(u'album_artist', (u'album_artist', u'album_artists'))
        add(u'disc', u'disc_number')
        add(u'show', u'series')
        add(u'season_number')
        add(u'episode_id', (u'episode', u'episode_id'))
        add(u'episode_sort', u'episode_number')
        if u'embed-metadata' in self.get_param(u'compat_opts', []):
            add(u'comment', u'description')
            metadata[u'common'].pop(u'synopsis', None)

        meta_regex = ur'%s(?P<i>\d+)?_(?P<key>.+)' % re.escape(meta_prefix)
        for key, value in info.items():
            mobj = re.fullmatch(meta_regex, key)
            if value is not None and mobj:
                metadata[mobj.group(u'i') or u'common'][mobj.group(u'key')] = value.replace(u'\0', u'')

        # Write id3v1 metadata also since Windows Explorer can't handle id3v2 tags
        yield (u'-write_id3v1', u'1')

        for name, value in metadata[u'common'].items():
            yield (u'-metadata', u'%s=%s' % (name, value))

        stream_idx = 0
        for fmt in info.get(u'requested_formats') or [info]:
            stream_count = 2 if u'none' not in (fmt.get(u'vcodec'), fmt.get(u'acodec')) else 1
            lang = ISO639Utils.short2long(fmt.get(u'language') or u'') or fmt.get(u'language')
            for i in xrange(stream_idx, stream_idx + stream_count):
                if lang:
                    metadata[unicode(i)].setdefault(u'language', lang)
                for name, value in metadata[unicode(i)].items():
                    yield (u'-metadata:s:%d' % i, u'%s=%s' % (name, value))
            stream_idx += stream_count

    def _get_infojson_opts(self, info, infofn):
        if not infofn or not os.path.exists(infofn):
            if self._add_infojson is not True:
                return
            infofn = infofn or u'%s.temp' % (
                self._downloader.prepare_filename(info, u'infojson')
                or replace_extension(self._downloader.prepare_filename(info), u'info.json', info[u'ext']))
            if not self._downloader._ensure_dir_exists(infofn):
                return
            self.write_debug(u'Writing info-json to: %s' % infofn)
            write_json_file(self._downloader.sanitize_info(info, self.get_param(u'clean_infojson', True)), infofn)
            info[u'infojson_filename'] = infofn

        old_stream, new_stream = self.get_stream_number(info[u'filepath'], (u'tags', u'mimetype'), u'application/json')
        if old_stream is not None:
            yield (u'-map', u'-0:%d' % old_stream)
            new_stream -= 1

        yield (
            u'-attach', self._ffmpeg_filename_argument(infofn),
            u'-metadata:s:%d' % new_stream, u'mimetype=application/json',
            u'-metadata:s:%d' % new_stream, u'filename=info.json',
        )


class FFmpegMergerPP(FFmpegPostProcessor):

    @PostProcessor._restrict_to(images=False)
    def run(self, info):
        filename = info[u'filepath']
        temp_filename = prepend_extension(filename, u'temp')
        args = [u'-c', u'copy']
        audio_streams = 0
        for (i, fmt) in enumerate(info[u'requested_formats']):
            if fmt.get(u'acodec') != u'none':
                args.extend([u'-map', u'%d:a:0' % i])
                aac_fixup = fmt[u'protocol'].startswith(u'm3u8') and self.get_audio_codec(fmt[u'filepath']) == u'aac'
                if aac_fixup:
                    args.extend([u'-bsf:a:%d' % audio_streams, u'aac_adtstoasc'])
                audio_streams += 1
            if fmt.get(u'vcodec') != u'none':
                args.extend([u'-map', u'%d:v:0' % i])
        self.to_screen(u'Merging formats into "%s"' % filename)
        self.run_ffmpeg_multiple_files(info[u'__files_to_merge'], temp_filename, args)
        os.rename(temp_filename, filename)
        return info[u'__files_to_merge'], info

    def can_merge(self):
        # TODO: figure out merge-capable ffmpeg version
        if self.basename != u'avconv':
            return True

        required_version = u'10-0'
        if is_outdated_version(
                self._versions[self.basename], required_version):
            warning = (u'Your copy of %s is outdated and unable to properly mux separate video and audio files, '
                       u'yt-dlp will download single file media. '
                       u'Update %s to version %s or newer to fix this.' % (self.basename, self.basename, required_version))
            self.report_warning(warning)
            return False
        return True


class FFmpegFixupPostProcessor(FFmpegPostProcessor):
    def _fixup(self, msg, filename, options):
        temp_filename = prepend_extension(filename, u'temp')

        self.to_screen(u'%s of "%s"' % (msg, filename))
        self.run_ffmpeg(filename, temp_filename, options)
        os.replace(temp_filename, filename)
        return [], info


class FFmpegFixupStretchedPP(FFmpegFixupPostProcessor):
    @PostProcessor._restrict_to(images=False, audio=False)
    def run(self, info):
        stretched_ratio = info.get(u'stretched_ratio')
        if stretched_ratio not in (None, 1):
            self._fixup(u'Fixing aspect ratio', info[u'filepath'],
                        list(self.stream_copy_opts()) + [u'-aspect', u'%f' % stretched_ratio])
        return [], info


class FFmpegFixupM4aPP(FFmpegFixupPostProcessor):
    @PostProcessor._restrict_to(images=False, video=False)
    def run(self, info):
        if info.get(u'container') == u'm4a_dash':
            self._fixup(u'Correcting container', info[u'filepath'], list(self.stream_copy_opts()) + [u'-f', u'mp4'])
        return [], info


class FFmpegFixupM3u8PP(FFmpegFixupPostProcessor):
    def _needs_fixup(self, info):
        yield info[u'ext'] in (u'mp4', u'm4a')
        yield info[u'protocol'].startswith(u'm3u8')
        try:
            metadata = self.get_metadata_object(info[u'filepath'])
        except PostProcessingError, e:
            self.report_warning(u'Unable to extract metadata: %s' % e.msg)
            yield True
        else:
            yield traverse_obj(metadata, (u'format', u'format_name'), casesense=False) == u'mpegts'

    @PostProcessor._restrict_to(images=False)
    def run(self, info):
        if all(self._needs_fixup(info)):
            args = [u'-f', u'mp4']
            if self.get_audio_codec(info[u'filepath']) == u'aac':
                args.extend([u'-bsf:a', u'aac_adtstoasc'])
            self._fixup(u'Fixing MPEG-TS in MP4 container', info[u'filepath'],
                        list(self.stream_copy_opts()) + args)
        return [], info


class FFmpegFixupTimestampPP(FFmpegFixupPostProcessor):

    def __init__(self, downloader=None, trim=0.001):
        # "trim" should be used when the video contains unintended packets
        super(FFmpegFixupTimestampPP, self).__init__(downloader)
        assert isinstance(trim, (int, float))
        self.trim = unicode(trim)

    @PostProcessor._restrict_to(images=False)
    def run(self, info):
        if not self._features.get(u'setts'):
            self.report_warning(
                u'A re-encode is needed to fix timestamps in older versions of ffmpeg. '
                u'Please install ffmpeg 4.4 or later to fixup without re-encoding')
            opts = [u'-vf', u'setpts=PTS-STARTPTS']
        else:
            opts = [u'-c', u'copy', u'-bsf', u'setts=ts=TS-STARTPTS']
        self._fixup(u'Fixing frame timestamp', info[u'filepath'], opts + list(self.stream_copy_opts(False)) + [u'-ss', self.trim])
        return [], info


class FFmpegCopyStreamPP(FFmpegFixupPostProcessor):
    MESSAGE = u'Copying stream'

    @PostProcessor._restrict_to(images=False)
    def run(self, info):
        self._fixup(self.MESSAGE, info[u'filepath'], self.stream_copy_opts())
        return [], info


class FFmpegFixupDurationPP(FFmpegCopyStreamPP):
    MESSAGE = u'Fixing video duration'


class FFmpegFixupDuplicateMoovPP(FFmpegCopyStreamPP):
    MESSAGE = u'Fixing duplicate MOOV atoms'


class FFmpegSubtitlesConvertorPP(FFmpegPostProcessor):
    SUPPORTED_EXTS = MEDIA_EXTENSIONS.subtitles

    def __init__(self, downloader=None, format=None):
        super(FFmpegSubtitlesConvertorPP, self).__init__(downloader)
        self.format = format

    def run(self, info):
        subs = info.get(u'requested_subtitles')
        new_ext = self.format
        new_format = new_ext
        if new_format == u'vtt':
            new_format = u'webvtt'
        if subs is None:
            self.to_screen(u'There aren\'t any subtitles to convert')
            return [], info
        self.to_screen(u'Converting subtitles')
        sub_filenames = []
        for lang, sub in subs.items():
            if not os.path.exists(sub.get(u'filepath', u'')):
                self.report_warning(u'Skipping embedding %s subtitle because the file is missing' % lang)
                continue
            ext = sub[u'ext']
            if ext == new_ext:
                self.to_screen(u'Subtitle file for %s is already in the requested format' % new_ext)
                continue
            elif ext == u'json':
                self.to_screen(
                    u'You have requested to convert json subtitles into another format, '
                    u'which is currently not possible')
                continue
            old_file = sub[u'filepath']
            sub_filenames.append(old_file)
            new_file = replace_extension(old_file, new_ext)

            if ext in (u'dfxp', u'ttml', u'tt'):
                self.report_warning(
                    u'You have requested to convert dfxp (TTML) subtitles into another format, '
                    u'which results in style information loss')

                dfxp_file = old_file
                srt_file = replace_extension(old_file, u'srt')

                with open(dfxp_file, u'rb') as f:
                    srt_data = dfxp2srt(f.read())

                with open(srt_file, u'w', encoding=u'utf-8') as f:
                    f.write(srt_data)
                old_file = srt_file

                subs[lang] = {
                    u'ext': u'srt',
                    u'data': srt_data,
                    u'filepath': srt_file,
                }

                if new_ext == u'srt':
                    continue
                else:
                    sub_filenames.append(srt_file)

            self.run_ffmpeg(old_file, new_file, [u'-f', new_format])

            with open(new_file, encoding=u'utf-8') as f:
                subs[lang] = {
                    u'ext': new_ext,
                    u'data': f.read(),
                    u'filepath': new_file,
                }

            info[u'__files_to_move'][new_file] = replace_extension(
                info[u'__files_to_move'][sub[u'filepath']], new_ext)

        return sub_filenames, info


class FFmpegSplitChaptersPP(FFmpegPostProcessor):
    def __init__(self, downloader=None, force_keyframes=False):
        self._force_keyframes = force_keyframes
        super(FFmpegSplitChaptersPP, self).__init__(downloader)

    def _prepare_filename(self, number, chapter, info):
        info = info.copy()
        info.update({
            u'section_number': number,
            u'section_title': chapter.get(u'title'),
            u'section_start': chapter.get(u'start_time'),
            u'section_end': chapter.get(u'end_time'),
        })
        return self._downloader.prepare_filename(info, u'chapter')

    def _ffmpeg_args_for_chapter(self, number, chapter, info):
        destination = self._prepare_filename(number, chapter, info)
        if not self._downloader._ensure_dir_exists(destination):
            return

        chapter[u'filepath'] = destination
        self.to_screen(u'Chapter %03d; Destination: %s' % (number, destination))
        return (
            destination,
            [u'-ss', unicode(chapter[u'start_time']),
             u'-t', unicode(chapter[u'end_time'] - chapter[u'start_time'])])

    @PostProcessor._restrict_to(images=False)
    def run(self, info):
        self._fixup_chapters(info)
        chapters = info.get(u'chapters') or []
        if not chapters:
            self.to_screen(u'Chapter information is unavailable')
            return [], info

        in_file = info[u'filepath']
        if self._force_keyframes and len(chapters) > 1:
            in_file = self.force_keyframes(in_file, (c[u'start_time'] for c in chapters))
        self.to_screen(u'Splitting video by chapters; %d chapters found' % len(chapters))
        for idx, chapter in enumerate(chapters):
            destination, opts = self._ffmpeg_args_for_chapter(idx + 1, chapter, info)
            self.real_run_ffmpeg([(in_file, opts)], [(destination, self.stream_copy_opts())])
        if in_file != info[u'filepath']:
            self._delete_downloaded_files(in_file, msg=None)
        return [], info


class FFmpegThumbnailsConvertorPP(FFmpegPostProcessor):
    SUPPORTED_EXTS = (u'jpg', u'png', u'webp')
    FORMAT_RE = create_mapping_re(SUPPORTED_EXTS)

    def __init__(self, downloader=None, format=None):
        super(FFmpegThumbnailsConvertorPP, self).__init__(downloader)
        self.mapping = format

    @classmethod
    def is_webp(cls, path):
        deprecation_warning(u'%s.%s.is_webp is deprecated' % (cls.__module__, cls.__name__))
        return imghdr.what(path) == u'webp'

    def fixup_webp(self, info, idx=-1):
        thumbnail_filename = info[u'thumbnails'][idx][u'filepath']
        _, thumbnail_ext = os.path.splitext(thumbnail_filename)
        if thumbnail_ext:
            if thumbnail_ext.lower() != u'.webp' and imghdr.what(thumbnail_filename) == u'webp':
                self.to_screen(u'Correcting thumbnail "%s" extension to webp' % thumbnail_filename)
                webp_filename = replace_extension(thumbnail_filename, u'webp')
                os.replace(thumbnail_filename, webp_filename)
                info[u'thumbnails'][idx][u'filepath'] = webp_filename
                info[u'__files_to_move'][webp_filename] = replace_extension(
                    info[u'__files_to_move'].pop(thumbnail_filename), u'webp')

    @staticmethod
    def _options(target_ext):
        yield (u'-update', u'1')
        if target_ext == u'jpg':
            yield (u'-bsf:v', u'mjpeg2jpeg')

    def convert_thumbnail(self, thumbnail_filename, target_ext):
        thumbnail_conv_filename = replace_extension(thumbnail_filename, target_ext)
        self.to_screen(u'Converting thumbnail "%s" to %s' % (thumbnail_filename, target_ext))
        _, source_ext = os.path.splitext(thumbnail_filename)
        self.real_run_ffmpeg(
            [(thumbnail_filename, [] if source_ext == u'.gif' else [u'-f', u'image2', u'-pattern_type', u'none'])],
            [(thumbnail_conv_filename, self._options(target_ext))])
        return thumbnail_conv_filename

    @PostProcessor._restrict_to(video=False, audio=False)
    def run(self, info):
        files_to_delete = []
        has_thumbnail = False

        for idx, thumbnail_dict in enumerate(info.get(u'thumbnails') or []):
            original_thumbnail = thumbnail_dict.get(u'filepath')
            if not original_thumbnail:
                continue
            has_thumbnail = True
            self.fixup_webp(info, idx)
            original_thumbnail = thumbnail_dict[u'filepath']  # Path can change during fixup
            thumbnail_ext = os.path.splitext(original_thumbnail)[1][1:].lower()
            if thumbnail_ext == u'jpeg':
                thumbnail_ext = u'jpg'
            target_ext, _skip_msg = resolve_mapping(thumbnail_ext, self.mapping)
            if _skip_msg:
                self.to_screen(u'Not converting thumbnail "%s"; %s' % (original_thumbnail, _skip_msg))
                continue
            thumbnail_dict[u'filepath'] = self.convert_thumbnail(original_thumbnail, target_ext)
            files_to_delete.append(original_thumbnail)
            info[u'__files_to_move'][thumbnail_dict[u'filepath']] = replace_extension(
                info[u'__files_to_move'][original_thumbnail], target_ext)

        if not has_thumbnail:
            self.to_screen(u'There aren\'t any thumbnails to convert')
        return files_to_delete, info


class FFmpegConcatPP(FFmpegPostProcessor):
    def __init__(self, downloader, only_multi_video=False):
        self._only_multi_video = only_multi_video
        super(FFmpegConcatPP, self).__init__(downloader)

    def _get_codecs(self, file):
        codecs = traverse_obj(self.get_metadata_object(file), (u'streams', ..., u'codec_name'))
        self.write_debug(u'Codecs = %s' % u", ".join(codecs))
        return tuple(codecs)

    def concat_files(self, in_files, out_file):
        if len(in_files) == 1:
            self.to_screen(u'Only one file to concatenate')
            os.replace(in_files[0], out_file)
            return []

        if len(set(imap(self._get_codecs, in_files))) > 1:
            raise PostProcessingError(
                u'The files have different streams/codecs and cannot be concatenated. '
                u'Either select different formats or --recode-video them to a common format')

        self.to_screen(u'Concatenating %d files; Destination: %s' % (len(in_files), out_file))
        super(FFmpegConcatPP, self).concat_files(in_files, out_file)
        return in_files

    @PostProcessor._restrict_to(images=False, simulated=False)
    def run(self, info):
        entries = info.get(u'entries') or []
        if not any(entries) or (self._only_multi_video and info[u'_type'] != u'multi_video'):
            return [], info
        elif traverse_obj(entries, (..., lambda k, v: k == u'requested_downloads' and len(v) > 1)):
            raise PostProcessingError(u'Concatenation is not supported when downloading multiple separate formats')

        in_files = traverse_obj(entries, (..., u'requested_downloads', 0, u'filepath')) or []
        if len(in_files) < len(entries):
            raise PostProcessingError(u'Aborting concatenation because some downloads failed')

        exts = traverse_obj(entries, (..., u'requested_downloads', 0, u'ext'), (..., u'ext'))
        ie_copy = collections.ChainMap({u'ext': exts[0] if len(set(exts)) == 1 else u'mkv'},
                                       info, self._downloader._playlist_infodict(info))
        out_file = self._downloader.prepare_filename(ie_copy, u'pl_video')

        files_to_delete = self.concat_files(in_files, out_file)

        info[u'requested_downloads'] = [{
            u'filepath': out_file,
            u'ext': ie_copy[u'ext'],
        }]
        return files_to_delete, info
