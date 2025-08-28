from __future__ import absolute_import
import os
import subprocess

from .common import FileDownloader
from ..utils import check_executable


class RtspFD(FileDownloader):
    def real_download(self, filename, info_dict):
        url = info_dict[u'url']
        self.report_destination(filename)
        tmpfilename = self.temp_name(filename)

        if check_executable(u'mplayer', [u'-h']):
            args = [
                u'mplayer', u'-really-quiet', u'-vo', u'null', u'-vc', u'dummy',
                u'-dumpstream', u'-dumpfile', tmpfilename, url]
        elif check_executable(u'mpv', [u'-h']):
            args = [
                u'mpv', u'-really-quiet', u'--vo=null', u'--stream-dump=' + tmpfilename, url]
        else:
            self.report_error(u'MMS or RTSP download detected but neither "mplayer" nor "mpv" could be run. Please install one')
            return False

        self._debug_cmd(args)

        retval = subprocess.call(args)
        if retval == 0:
            fsize = os.path.getsize(tmpfilename)
            self.to_screen(f'\r[{args[0]}] {fsize} bytes')
            self.try_rename(tmpfilename, filename)
            self._hook_progress({
                u'downloaded_bytes': fsize,
                u'total_bytes': fsize,
                u'filename': filename,
                u'status': u'finished',
            }, info_dict)
            return True
        else:
            self.to_stderr(u'\n')
            self.report_error(u'%s exited with code %d' % (args[0], retval))
            return False
