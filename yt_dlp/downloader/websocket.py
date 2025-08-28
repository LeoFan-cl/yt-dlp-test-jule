from __future__ import with_statement
from __future__ import absolute_import
import asyncio
import contextlib
import os
import signal
import threading

from .common import FileDownloader
from .external import FFmpegFD
from ..dependencies import websockets


class FFmpegSinkFD(FileDownloader):
    u""" A sink to ffmpeg for downloading fragments in any form """

    def real_download(self, filename, info_dict):
        info_copy = info_dict.copy()
        info_copy[u'url'] = u'-'

        async def call_conn(proc, stdin):
            try:
                await self.real_connection(stdin, info_dict)
            except OSError:
                pass
            finally:
                with contextlib.suppress(OSError):
                    stdin.flush()
                    stdin.close()
                os.kill(os.getpid(), signal.SIGINT)

        class FFmpegStdinFD(FFmpegFD):
            @classmethod
            def get_basename(cls):
                return FFmpegFD.get_basename()

            def on_process_started(self, proc, stdin):
                thread = threading.Thread(target=asyncio.run, daemon=True, args=(call_conn(proc, stdin), ))
                thread.start()

        return FFmpegStdinFD(self.ydl, self.params or {}).download(filename, info_copy)

    async def real_connection(self, sink, info_dict):
        u""" Override this in subclasses """
        raise NotImplementedError(u'This method must be implemented by subclasses')


class WebSocketFragmentFD(FFmpegSinkFD):
    async def real_connection(self, sink, info_dict):
        async with websockets.connect(info_dict[u'url'], extra_headers=info_dict.get(u'http_headers', {})) as ws:
            while True:
                recv = await ws.recv()
                if isinstance(recv, unicode):
                    recv = recv.encode(u'utf8')
                sink.write(recv)
