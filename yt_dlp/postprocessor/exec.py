from __future__ import absolute_import
from .common import PostProcessor
from ..utils import Popen, PostProcessingError, shell_quote, variadic


class ExecPP(PostProcessor):
    def __init__(self, downloader, exec_cmd):
        super(ExecPP, self).__init__(downloader)
        self.exec_cmd = exec_cmd

    def run_on_all(self, tmpl, info):
        for exec_cmd in variadic(self.exec_cmd):
            self.run_cmd(self.format_cmd(exec_cmd, info, tmpl))
        return [], info

    def format_cmd(self, cmd, info, tmpl_dict):
        if tmpl_dict:  # if there are no replacements, tmpl_dict = {}
            return self._downloader.escape_outtmpl(cmd) % tmpl_dict

        filepath = info.get(u'filepath', info.get(u'_filename'))
        # If video, and no replacements are found, replace {} for backard compatibility
        if filepath:
            if u'{}' not in cmd:
                cmd += u' {}'
            cmd = cmd.replace(u'{}', shell_quote(filepath, shell=True))
        return cmd

    def run(self, info):
        self.run_cmd(self.format_cmd(self.exec_cmd, info, info))
        return [], info

    def run_cmd(self, cmd):
        self.to_screen(u'Executing command: %s' % cmd)
        ret = Popen.run(cmd, shell=True)
        if ret.returncode != 0:
            raise PostProcessingError(
                u'Command returned error code %d' % ret.returncode)


# Deprecated
class ExecAfterDownloadPP(ExecPP):
    def __init__(self, *args, **kwargs):
        super(ExecAfterDownloadPP, self).__init__(*args, **kwargs)
        self.deprecation_warning(
            u'yt_dlp.postprocessor.ExecAfterDownloadPP is deprecated '
            u'and may be removed in a future version. Use yt_dlp.postprocessor.ExecPP instead')
