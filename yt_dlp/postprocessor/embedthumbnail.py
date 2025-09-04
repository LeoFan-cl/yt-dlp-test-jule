from __future__ import with_statement
from __future__ import absolute_import
import base64
import os
import re
import subprocess
from io import open

from .ffmpeg import FFmpegPostProcessor, FFmpegThumbnailsConvertorPP
from ..compat import compat_os_name
from ..dependencies import mutagen, imghdr
from ..utils import (
    check_executable,
    encodeArgument,
    get_exe_version,
    prepend_extension,
    shell_quote,
    Popen,
    PostProcessingError,
)

if mutagen:
    from mutagen.flac import FLAC, Picture
    from mutagen.id3 import APIC, ID3, ID3NoHeaderError
    from mutagen.mp3 import MP3
    from mutagen.mp4 import MP4, MP4Cover
    from mutagen.oggopus import OggOpus
    from mutagen.oggvorbis import OggVorbis


class EmbedThumbnailPPError(PostProcessingError):
    pass


class EmbedThumbnailPP(FFmpegPostProcessor):
    def __init__(self, downloader=None, already_have_thumbnail=False):
        super(EmbedThumbnailPP, self).__init__(downloader)
        self._already_have_thumbnail = already_have_thumbnail

    def _get_thumbnail_resolution(self, filename, thumbnail_dict):
        def guess():
            width, height = thumbnail_dict.get(u'width'), thumbnail_dict.get(u'height')
            if width and height:
                return width, height

        try:
            size_regex = ur',\s*(?P<w>\d+)x(?P<h>\d+)\s*[,\['
            size_result = self.run_ffmpeg(filename, None, [u'-hide_banner'], expected_retcodes=(1,))
            mobj = re.search(size_regex, size_result)
            if mobj is None:
                return guess()
        except PostProcessingError, err:
            self.report_warning(u'unable to find the thumbnail resolution; %s' % err)
            return guess()
        return int(mobj.group(u'w')), int(mobj.group(u'h'))

    def _report_run(self, exe, filename):
        self.to_screen(u'%s: Adding thumbnail to "%s"' % (exe, filename))

    @PostProcessor._restrict_to(images=False)
    def run(self, info):
        filename = info[u'filepath']
        temp_filename = prepend_extension(filename, u'temp')

        if not info.get(u'thumbnails'):
            self.to_screen(u'There aren\'t any thumbnails to embed')
            return [], info

        try:
            idx = -i for i, t in enumerate(info[u'thumbnails'][::-1], 1) if t.get(u'filepath').next()
        except StopIteration:
            idx = None

        if idx is None:
            self.to_screen(u'There are no thumbnails on disk')
            return [], info
        thumbnail_filename = info[u'thumbnails'][idx][u'filepath']
        if not os.path.exists(thumbnail_filename):
            self.report_warning(u'Skipping embedding the thumbnail because the file is missing.')
            return [], info

        # Correct extension for WebP file with wrong extension (see #25687, #25717)
        convertor = FFmpegThumbnailsConvertorPP(self._downloader)
        convertor.fixup_webp(info, idx)

        original_thumbnail = thumbnail_filename = info[u'thumbnails'][idx][u'filepath']

        # Convert unsupported thumbnail formats (see #25687, #25717)
        # PNG is preferred since JPEG is lossy
        thumbnail_ext = os.path.splitext(thumbnail_filename)[1][1:]
        if info[u'ext'] not in (u'mkv', u'mka') and thumbnail_ext not in (u'jpg', u'jpeg', u'png'):
            thumbnail_filename = convertor.convert_thumbnail(thumbnail_filename, u'png')
            thumbnail_ext = u'png'

        mtime = os.stat(filename).st_mtime

        success = True
        if info[u'ext'] == u'mp3':
            options = [
                u'-c', u'copy', u'-map', u'0:0', u'-map', u'1:0', u'-write_id3v1', u'1', u'-id3v2_version', u'3',
                u'-metadata:s:v', u'title=Album cover', u'-metadata:s:v', u'comment=Cover (front)']

            self._report_run(u'ffmpeg', filename)
            self.run_ffmpeg_multiple_files([filename, thumbnail_filename], temp_filename, options)

        elif info[u'ext'] in [u'mkv', u'mka']:
            options = list(self.stream_copy_opts())

            mimetype = u'image/%s' % thumbnail_ext.replace(u"jpg", u"jpeg")
            old_stream, new_stream = self.get_stream_number(
                filename, (u'tags', u'mimetype'), mimetype)
            if old_stream is not None:
                options.extend([u'-map', u'-0:%s' % old_stream])
                new_stream -= 1
            options.extend([
                u'-attach', self._ffmpeg_filename_argument(thumbnail_filename),
                u'-metadata:s:%d' % new_stream, u'mimetype=%s' % mimetype,
                u'-metadata:s:%d' % new_stream, u'filename=cover.%s' % thumbnail_ext])

            self._report_run(u'ffmpeg', filename)
            self.run_ffmpeg(filename, temp_filename, options)

        elif info[u'ext'] in [u'm4a', u'mp4', u'm4v', u'mov']:
            prefer_atomicparsley = u'embed-thumbnail-atomicparsley' in self.get_param(u'compat_opts', [])
            # Method 1: Use mutagen
            if not mutagen or prefer_atomicparsley:
                success = False
            else:
                self._report_run(u'mutagen', filename)
                f = {u'jpeg': MP4Cover.FORMAT_JPEG, u'png': MP4Cover.FORMAT_PNG}
                try:
                    with open(thumbnail_filename, u'rb') as thumbfile:
                        thumb_data = thumbfile.read()

                    type_ = imghdr.what(h=thumb_data)
                    if not type_:
                        raise ValueError(u'could not determine image type')
                    elif type_ not in f:
                        raise ValueError(u'incompatible image type: %s' % type_)

                    meta = MP4(filename)
                    # NOTE: the 'covr' atom is a non-standard MPEG-4 atom,
                    # Apple iTunes 'M4A' files include the 'moov.udta.meta.ilst' atom.
                    meta.tags[u'covr'] = [MP4Cover(data=thumb_data, imageformat=f[type_])]
                    meta.save()
                    temp_filename = filename
                except Exception, err:
                    self.report_warning(u'unable to embed using mutagen; %s' % err)
                    success = False

            # Method 2: Use AtomicParsley
            if not success:
                success = True
                try:
                    atomicparsley = x for x in [u'AtomicParsley', u'atomicparsley', u'libatomicparsley.so'] if check_executable(x, [u'-v']).next()
                except StopIteration:
                    atomicparsley = None

                if atomicparsley is None:
                    self.to_screen(u'Neither mutagen nor AtomicParsley was found. Falling back to ffmpeg')
                    success = False
                else:
                    if not prefer_atomicparsley:
                        self.to_screen(u'mutagen was not found. Falling back to AtomicParsley')
                    cmd = [atomicparsley,
                           filename,
                           encodeArgument(u'--artwork'),
                           thumbnail_filename,
                           encodeArgument(u'-o'),
                           temp_filename]
                    cmd += [encodeArgument(o) for o in self._configuration_args(u'AtomicParsley')]

                    self._report_run(u'atomicparsley', filename)
                    self.write_debug(u'AtomicParsley command line: %s' % shell_quote(cmd))
                    stdout, stderr, returncode = Popen.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if returncode:
                        self.report_warning(u'AtomicParsley failed: %s' % stderr)
                        success = False
                    # for formats that don't support thumbnails (like 3gp) AtomicParsley
                    # won't create to the temporary file
                    elif u'No changes' in stdout:
                        self.report_warning(u'The file format doesn\'t support embedding a thumbnail')
                        success = False

            # Method 3: Use ffmpeg+ffprobe
            # Better than mutagen because it can handle more file types
            if not success:
                success = True
                try:
                    options = list(self.stream_copy_opts()) + [u'-map', u'1']

                    old_stream, new_stream = self.get_stream_number(
                        filename, (u'disposition', u'attached_pic'), 1)
                    if old_stream is not None:
                        options.extend([u'-map', u'-0:%d' % old_stream])
                        new_stream -= 1
                    options.extend([u'-disposition:%d' % new_stream, u'attached_pic'])

                    self._report_run(u'ffmpeg', filename)
                    self.run_ffmpeg_multiple_files([filename, thumbnail_filename], temp_filename, options)
                except PostProcessingError, err:
                    success = False
                    raise EmbedThumbnailPPError(u'Unable to embed using ffprobe & ffmpeg; %s' % err)

        elif info[u'ext'] in [u'ogg', u'opus', u'flac']:
            if not mutagen:
                raise EmbedThumbnailPPError(u'module mutagen was not found. Please install using `python -m pip install mutagen`')

            self._report_run(u'mutagen', filename)
            f = {u'opus': OggOpus, u'flac': FLAC, u'ogg': OggVorbis}[info[u'ext']](filename)

            pic = Picture()
            pic.mime = u'image/%s' % imghdr.what(thumbnail_filename)
            with open(thumbnail_filename, u'rb') as thumbfile:
                pic.data = thumbfile.read()
            pic.type = 3  # front cover
            res = self._get_thumbnail_resolution(thumbnail_filename, info[u'thumbnails'][idx])
            if res is not None:
                pic.width, pic.height = res

            if info[u'ext'] == u'flac':
                f.add_picture(pic)
            else:
                # https://wiki.xiph.org/VorbisComment#METADATA_BLOCK_PICTURE
                f[u'METADATA_BLOCK_PICTURE'] = base64.b64encode(pic.write()).decode(u'ascii')
            f.save()
            temp_filename = filename

        else:
            raise EmbedThumbnailPPError(u'Supported filetypes for thumbnail embedding are: mp3, mkv/mka, ogg/opus/flac, m4a/mp4/m4v/mov')

        if success and temp_filename != filename:
            os.replace(temp_filename, filename)

        if os.path.exists(original_thumbnail):
            self.try_utime(filename, os.stat(original_thumbnail).st_atime, mtime)

        if thumbnail_filename != original_thumbnail:
            os.remove(thumbnail_filename)

        return [], info
