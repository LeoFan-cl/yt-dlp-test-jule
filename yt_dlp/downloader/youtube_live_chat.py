b'--- ./yt_dlp/downloader/youtube_live_chat.py\t(original)'
b'+++ ./yt_dlp/downloader/youtube_live_chat.py\t(refactored)'
b'@@ -51,7 +51,7 @@'
b"                     replay_chat_item_action = action[u'replayChatItemAction']"
b"                     offset = int(replay_chat_item_action[u'videoOffsetTimeMsec'])"
b'                 processed_fragment.extend('
b"-                    json.dumps(action, ensure_ascii=False).encode() + '\\n')"
b"+                    json.dumps(action, ensure_ascii=False).encode() + u'\\n')"
b'             if offset is not None:'
b'                 continuation = try_get('
b'                     live_chat_continuation,'
b'@@ -69,7 +69,7 @@'
b"                 lambda x: x[u'header'][u'liveChatHeaderRenderer'][u'viewSelector'][u'sortFilterSubMenuRenderer'][u'subMenuItems'][1][u'continuation'][u'reloadContinuationData'], dict)"
b'             if refresh_continuation:'
b'                 # no data yet but required to call _append_fragment'
b"-                self._append_fragment(ctx, '')"
b"+                self._append_fragment(ctx, u'')"
b"                 refresh_continuation_id = refresh_continuation.get(u'continuation')"
b'                 offset = 0'
b"                 click_tracking_params = refresh_continuation.get(u'trackingParams')"
b'@@ -93,7 +93,7 @@'
b"                     u'isLive': True,"
b'                 }'
b'                 processed_fragment.extend('
b"-                    json.dumps(pseudo_action, ensure_ascii=False).encode() + '\\n')"
b"+                    json.dumps(pseudo_action, ensure_ascii=False).encode() + u'\\n')"
b'             continuation_data_getters = ['
b"                 lambda x: x[u'continuations'][0][u'invalidationContinuationData'],"
b"                 lambda x: x[u'continuations'][0][u'timedContinuationData'],"
b'@@ -148,7 +148,7 @@'
b'             data,'
b"             lambda x: x[u'contents'][u'twoColumnWatchNextResults'][u'conversationBar'][u'liveChatRenderer'][u'continuations'][0][u'reloadContinuationData'][u'continuation'])"
b'         # no data yet but required to call _append_fragment'
b"-        self._append_fragment(ctx, '')"
b"+        self._append_fragment(ctx, u'')"
b' '
b"         ytcfg = ie.extract_ytcfg(video_id, raw_fragment.decode(u'utf-8', u'replace'))"
b' '
b'@@ -180,7 +180,7 @@'
b"                     request_data[u'context'][u'clickTracking'] = {u'clickTrackingParams': click_tracking_params}"
b'                 headers = ie.generate_api_headers(ytcfg=ytcfg, visitor_data=visitor_data)'
b"                 headers.update({u'content-type': u'application/json'})"
b"-                fragment_request_data = json.dumps(request_data, ensure_ascii=False).encode() + '\\n'"
b"+                fragment_request_data = json.dumps(request_data, ensure_ascii=False).encode() + u'\\n'"
b'                 success, continuation_id, offset, click_tracking_params = download_and_parse_fragment('
b'                     url, frag_index, fragment_request_data, headers)'
b'             else:'
