from __future__ import absolute_import
import os
import shutil

from .common import PostProcessor
from ..utils import PostProcessingError


class MoveFilesAfterDownloadPP(PostProcessor):
    def __init__(self, downloader, downloaded=True):
        super(MoveFilesAfterDownloadPP, self).__init__(downloader)
        self._downloaded = downloaded

    @classmethod
    def pp_key(cls):
        return u'MoveFiles'

    def run(self, info):
        dl_path, dl_name = os.path.split(info[u'filepath'])
        finaldir = info.get(u'__finaldir', dl_path)
        finalpath = os.path.join(finaldir, dl_name)
        if self._downloaded:
            info[u'__files_to_move'][info[u'filepath']] = finalpath

        make_newfilename = lambda old: os.path.join(finaldir, os.path.basename(old))
        for oldfile, newfile in info[u'__files_to_move'].items():
            if not newfile:
                newfile = make_newfilename(oldfile)
            if os.path.abspath(oldfile) == os.path.abspath(newfile):
                continue

            if not os.path.exists(oldfile):
                self.report_warning(u'File "%s" cannot be found' % oldfile)
                continue
            if os.path.exists(newfile):
                if self.get_param(u'overwrites', True):
                    self.report_warning(u'Replacing existing file "%s"' % newfile)
                    os.remove(newfile)
                else:
                    raise PostProcessingError(u'Destination file "%s" already exists' % newfile)

            self.to_screen(u'Moving file "%s" to "%s"' % (oldfile, newfile))
            shutil.move(oldfile, newfile)  # os.rename cannot move between volumes

        info[u'filepath'] = finalpath
        return [], info
