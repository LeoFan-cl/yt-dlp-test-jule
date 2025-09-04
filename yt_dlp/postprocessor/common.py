from __future__ import absolute_import
import functools
import json
import os

from ..utils import (
    RetryManager,
    PostProcessingError,
    network_exceptions,
    HTTPError,
    deprecation_warning,
)
from ..utils._utils import _ProgressState
from itertools import ifilter


class PostProcessorMetaClass(type):
    @staticmethod
    def run_wrapper(func):
        @functools.wraps(func)
        def run(self, info, *args, **kwargs):
            info_copy = self._copy_infodict(info)
            self._hook_progress({u'status': u'started'}, info_copy)
            ret = func(self, info, *args, **kwargs)
            if ret is not None:
                _, info = ret
            self._hook_progress({u'status': u'finished'}, info_copy)
            return ret
        return run

    def __new__(cls, name, bases, attrs):
        if u'run' in attrs:
            attrs[u'run'] = cls.run_wrapper(attrs[u'run'])
        return type.__new__(cls, name, bases, attrs)


class PostProcessor(object):
    __metaclass__ = PostProcessorMetaClass
    u"""Post Processor class.

    PostProcessor objects can be added to downloaders with their
    add_post_processor() method. When the downloader has finished a
    download, it will call the PostProcessor's run() method.

    The PostProcessor arguments are the following:
    - The PostProcessor is initialized with the Downloader object.
    - The run() method is called with a dictionary with
      information about the downloaded file.

    The dictionary passed to run() is guaranteed to contain
    the following fields:
    - filepath: The path to the downloaded file.
    - info_dict: The InfoExtractor's dictionary.

    The run() method must return a tuple with the list of files
    that can be deleted by the Downloader, and the information
    dictionary. The list of files to delete can be empty.
    """

    _downloader = None
    _progress_hooks = None

    def __init__(self, downloader=None):
        self._downloader = downloader
        self._progress_hooks = []

    @classproperty
    def PP_NAME(cls):
        return cls.__name__[:-2]

    @classmethod
    def pp_key(cls):
        name = cls.__name__[:-2]
        return name[6:] if name[:6].lower() == u'ffmpeg' else name

    def to_screen(self, text, prefix=True, *args, **kwargs):
        if self._downloader:
            tag = u'[%s] ' % self.PP_NAME if prefix else u''
            return self._downloader.to_screen(u'%s%s' % (tag, text), *args, **kwargs)

    def report_warning(self, text, *args, **kwargs):
        if self._downloader:
            return self._downloader.report_warning(text, *args, **kwargs)

    def deprecation_warning(self, msg):
        warn = getattr(self._downloader, u'deprecation_warning', deprecation_warning)
        return warn(msg, stacklevel=1)

    def deprecated_feature(self, msg):
        # TODO: Add a warning class for this
        self.deprecation_warning(msg)
        return deprecation_warning(msg, stacklevel=1)

    def report_error(self, text, *args, **kwargs):
        self.deprecation_warning(u'"yt_dlp.postprocessor.PostProcessor.report_error" is deprecated. '
                                 u'raise "yt_dlp.utils.PostProcessingError" instead')
        if self._downloader:
            return self._downloader.report_error(text, *args, **kwargs)

    def write_debug(self, text, *args, **kwargs):
        if self._downloader:
            return self._downloader.write_debug(text, *args, **kwargs)

    def _delete_downloaded_files(self, *files_to_delete, **kwargs):
        if self._downloader:
            return self._downloader._delete_downloaded_files(*files_to_delete, **kwargs)
        for filename in set(ifilter(None, files_to_delete)):
            os.remove(filename)

    def get_param(self, name, default=None, *args, **kwargs):
        if self._downloader:
            return self._downloader.params.get(name, default, *args, **kwargs)
        return default

    def set_downloader(self, downloader):
        u"""Sets the downloader for this PP."""
        self._downloader = downloader
        for ph in getattr(downloader, u'_postprocessor_hooks', []):
            self.add_progress_hook(ph)

    def _copy_infodict(self, info_dict):
        return getattr(self._downloader, u'_copy_infodict', dict)(info_dict)

    @staticmethod
    def _restrict_to(**_3to2kwargs):
        if u'simulated' in _3to2kwargs: simulated = _3to2kwargs[u'simulated']; del _3to2kwargs[u'simulated']
        else: simulated = True
        if u'images' in _3to2kwargs: images = _3to2kwargs[u'images']; del _3to2kwargs[u'images']
        else: images = True
        if u'audio' in _3to2kwargs: audio = _3to2kwargs[u'audio']; del _3to2kwargs[u'audio']
        else: audio = True
        if u'video' in _3to2kwargs: video = _3to2kwargs[u'video']; del _3to2kwargs[u'video']
        else: video = True
        allowed = {u'video': video, u'audio': audio, u'images': images}

        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, info):
                if not simulated and (self.get_param(u'simulate') or self.get_param(u'skip_download')):
                    return [], info
                format_type = (
                    u'video' if info.get(u'vcodec') != u'none'
                    else u'audio' if info.get(u'acodec') != u'none'
                    else u'images')
                if allowed[format_type]:
                    return func(self, info)
                else:
                    self.to_screen(u'Skipping %s format' % format_type)
                    return [], info
            return wrapper
        return decorator

    def run(self, information):
        u"""Run the PostProcessor.

        The "information" argument is a dictionary like the ones
        composed by InfoExtractors. The only difference is that this
        one is guaranteed to have the "filepath" field with the path
        to the downloaded file.

        This method must return a tuple, the first element is a list of
        files that can be deleted and the second of which is the
        information dictionary that may have been modified. The list
        of files to delete can be empty.
        """
        return [], information  # by default, keep file and do nothing

    def try_utime(self, path, atime, mtime, errnote=u'Cannot update utime of file'):
        try:
            os.utime(path, (atime, mtime))
        except Exception:
            self.report_warning(errnote)

    def _configuration_args(self, exe, *args, **kwargs):
        from ..utils import _configuration_args
        return _configuration_args(
            self.pp_key(), self.get_param(u'postprocessor_args'), exe, *args, **kwargs)

    def _hook_progress(self, status, info_dict):
        if not self._progress_hooks:
            return
        status.update({
            u'info_dict': info_dict,
            u'postprocessor': self.pp_key(),
        })
        for ph in self._progress_hooks:
            ph(status)
        self.report_progress(status)

    def add_progress_hook(self, ph):
        self._progress_hooks.append(ph)

    def report_progress(self, s):
        s[u'_default_template'] = u'%(postprocessor)s %(status)s' % s  # noqa: UP031
        if not self._downloader:
            return

        progress_dict = s.copy()
        progress_dict.pop(u'info_dict')
        progress_dict = {u'info': s[u'info_dict'], u'progress': progress_dict}

        progress_template = self.get_param(u'progress_template', {})
        tmpl = progress_template.get(u'postprocess')
        if tmpl:
            self._downloader.to_screen(
                self._downloader.evaluate_outtmpl(tmpl, progress_dict), quiet=False)

        self._downloader.to_console_title(self._downloader.evaluate_outtmpl(
            progress_template.get(u'postprocess-title') or u'yt-dlp %(progress._default_template)s',
            progress_dict), _ProgressState.from_dict(s), s.get(u'_percent'))

    def _retry_download(self, err, count, retries):
        # While this is not an extractor, it behaves similar to one and
        # so obey extractor_retries and "--retry-sleep extractor"
        RetryManager.report_retry(err, count, retries, info=self.to_screen, warn=self.report_warning,
                                  sleep_func=self.get_param(u'retry_sleep_functions', {}).get(u'extractor'))

    def _download_json(self, url, **_3to2kwargs):
        if u'expected_http_errors' in _3to2kwargs: expected_http_errors = _3to2kwargs[u'expected_http_errors']; del _3to2kwargs[u'expected_http_errors']
        else: expected_http_errors = (404,)
        from ..networking import Request
        self.write_debug(u'%s query: %s' % (self.PP_NAME, url))
        for retry in RetryManager(self.get_param(u'extractor_retries', 3), self._retry_download):
            try:
                rsp = self._downloader.urlopen(Request(url))
            except network_exceptions, e:
                if isinstance(e, HTTPError) and e.status in expected_http_errors:
                    return None
                retry.error = PostProcessingError(u'Unable to communicate with %s API: %s' % (self.PP_NAME, e))
                continue
        return json.loads(rsp.read().decode(rsp.headers.get_param(u'charset') or u'utf-8'))


class AudioConversionError(PostProcessingError):  # Deprecated
    pass
