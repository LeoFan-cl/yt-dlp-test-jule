from __future__ import absolute_import
import os
import shlex
import subprocess

from .common import PostProcessor
from ..utils import (
    check_executable,
    cli_option,
    encodeArgument,
    PostProcessingError,
    prepend_extension,
    shell_quote,
    str_or_none,
    Popen,
)

# Deprecated in favor of the native implementation
class SponSkrubPP(PostProcessor):
    _temp_ext = u'spons'
    _exe_name = u'sponskrub'

    def __init__(self, downloader, path=u'', args=None, ignoreerror=False, cut=False, force=False, _from_cli=False):
        PostProcessor.__init__(self, downloader)
        self.force = force
        self.cutout = cut
        self.args = str_or_none(args) or u''  # For backward compatibility
        self.path = self.get_exe(path)

        if not _from_cli:
            self.deprecation_warning(
                u'yt_dlp.postprocessor.SponSkrubPP support is deprecated and may be removed in a future version. '
                u'Use yt_dlp.postprocessor.SponsorBlock and yt_dlp.postprocessor.ModifyChaptersPP instead')

        if not ignoreerror and self.path is None:
            if path:
                raise PostProcessingError('sponskrub not found in "%s"' % path)
            else:
                raise PostProcessingError(u'sponskrub not found. Please install or provide the path using --sponskrub-path')

    def get_exe(self, path=u''):
        if not path or not check_executable(path, [u'-h']):
            path = os.path.join(path, self._exe_name)
            if not check_executable(path, [u'-h']):
                return None
        return path

    @PostProcessor._restrict_to(images=False)
    def run(self, information):
        if self.path is None:
            return [], information

        filename = information[u'filepath']
        if not os.path.exists(filename):  # no download
            return [], information

        if information[u'extractor_key'].lower() != u'youtube':
            self.to_screen(u'Skipping sponskrub since it is not a YouTube video')
            return [], information
        if self.cutout and not self.force and not information.get(u'__real_download', False):
            self.report_warning(
                u'Skipping sponskrub since the video was already downloaded. '
                u'Use --sponskrub-force to run sponskrub anyway')
            return [], information

        self.to_screen('Trying to %s sponsor sections' % (u'remove' if self.cutout else u'mark'))
        if self.cutout:
            self.report_warning(u'Cutting out sponsor segments will cause the subtitles to go out of sync.')
            if not information.get(u'__real_download', False):
                self.report_warning(u'If sponskrub is run multiple times, unintended parts of the video could be cut out.')

        temp_filename = prepend_extension(filename, self._temp_ext)
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        cmd = [self.path]
        if not self.cutout:
            cmd += [u'-chapter']
        cmd += cli_option(self._downloader.params, u'-proxy', u'proxy')
        cmd += shlex.split(self.args)  # For backward compatibility
        cmd += self._configuration_args(self._exe_name, use_compat=False)
        cmd += [u'--', information[u'id'], filename, temp_filename]
        cmd = [encodeArgument(i) for i in cmd]

        self.write_debug('sponskrub command line: %s' % shell_quote(cmd))
        stdout, _, returncode = Popen.run(cmd, text=True, stdout=None if self.get_param(u'verbose') else subprocess.PIPE)

        if not returncode:
            os.replace(temp_filename, filename)
            self.to_screen('Sponsor sections have been %s' % (u'removed' if self.cutout else u'marked'))
        elif returncode == 3:
            self.to_screen(u'No segments in the SponsorBlock database')
        else:
            raise PostProcessingError(
                stdout.strip().splitlines()[0 if stdout.strip().lower().startswith(u'unrecognised') else -1]
                or 'sponskrub failed with error code %d' % returncode)
        return [], information
