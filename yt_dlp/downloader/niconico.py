from __future__ import with_statement
from __future__ import absolute_import
import json
import threading
import time

from .common import FileDownloader
from .external import FFmpegFD
from ..networking import Request
from ..networking.websocket import WebSocketResponse
from ..utils import DownloadError, str_or_none, truncate_string
from ..utils.traversal import traverse_obj


class NiconicoLiveFD(FileDownloader):
    u""" Downloads niconico live without being stopped """

    def real_download(self, filename, info_dict):
        video_id = info_dict[u'id']
        opts = info_dict[u'downloader_options']
        quality, ws_extractor, ws_url = opts[u'max_quality'], opts[u'ws'], opts[u'ws_url']
        dl = FFmpegFD(self.ydl, self.params or {})

        new_info_dict = info_dict.copy()
        new_info_dict[u'protocol'] = u'm3u8'

        def communicate_ws(reconnect):
            # Support --load-info-json as if it is a reconnect attempt
            if reconnect or not isinstance(ws_extractor, WebSocketResponse):
                ws = self.ydl.urlopen(Request(
                    ws_url, headers={u'Origin': u'https://live.nicovideo.jp'}))
                if self.ydl.params.get(u'verbose', False):
                    self.write_debug(u'Sending startWatching request')
                ws.send(json.dumps({
                    u'data': {
                        u'reconnect': True,
                        u'room': {
                            u'commentable': True,
                            u'protocol': u'webSocket',
                        },
                        u'stream': {
                            u'accessRightMethod': u'single_cookie',
                            u'chasePlay': False,
                            u'latency': u'high',
                            u'protocol': u'hls',
                            u'quality': quality,
                        },
                    },
                    u'type': u'startWatching',
                }))
            else:
                ws = ws_extractor
            with ws:
                while True:
                    recv = ws.recv()
                    if not recv:
                        continue
                    data = json.loads(recv)
                    if not data or not isinstance(data, dict):
                        continue
                    if data.get(u'type') == u'ping':
                        ws.send(ur'{"type":"pong"}')
                        ws.send(ur'{"type":"keepSeat"}')
                    elif data.get(u'type') == u'disconnect':
                        self.write_debug(data)
                        return True
                    elif data.get(u'type') == u'error':
                        self.write_debug(data)
                        message = traverse_obj(data, (u'body', u'code', set([str_or_none])), default=recv)
                        return DownloadError(message)
                    elif self.ydl.params.get(u'verbose', False):
                        self.write_debug(f'Server response: {truncate_string(recv, 100)}')

        def ws_main():
            reconnect = False
            while True:
                try:
                    ret = communicate_ws(reconnect)
                    if ret is True:
                        return
                except BaseException, e:
                    self.to_screen(
                        f'[niconico:live] {video_id}: Connection error occured, reconnecting after 10 seconds: {e}')
                    time.sleep(10)
                    continue
                finally:
                    reconnect = True

        thread = threading.Thread(target=ws_main, daemon=True)
        thread.start()

        return dl.download(filename, new_info_dict)
