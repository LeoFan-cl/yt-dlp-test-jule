b'--- ./test/helper.py\t(original)'
b'+++ ./test/helper.py\t(refactored)'
b'@@ -1,3 +1,5 @@'
b'+from __future__ import with_statement'
b'+from __future__ import absolute_import'
b' import errno'
b' import hashlib'
b' import json'
b'@@ -10,8 +12,10 @@'
b' import yt_dlp.extractor'
b' from yt_dlp import YoutubeDL'
b' from yt_dlp.utils import preferredencoding, try_call, write_string, find_available_port'
b'-'
b"-if 'pytest' in sys.modules:"
b'+from io import open'
b'+from itertools import izip'
b'+'
b"+if u'pytest' in sys.modules:"
b'     import pytest'
b'     is_download_test = pytest.mark.download'
b' else:'
b'@@ -21,13 +25,13 @@'
b' '
b' def get_params(override=None):'
b'     PARAMETERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),'
b"-                                   'parameters.json')"
b"+                                   u'parameters.json')"
b'     LOCAL_PARAMETERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),'
b"-                                         'local_parameters.json')"
b"-    with open(PARAMETERS_FILE, encoding='utf-8') as pf:"
b"+                                         u'local_parameters.json')"
b"+    with open(PARAMETERS_FILE, encoding=u'utf-8') as pf:"
b'         parameters = json.load(pf)'
b'     if os.path.exists(LOCAL_PARAMETERS_FILE):'
b"-        with open(LOCAL_PARAMETERS_FILE, encoding='utf-8') as pf:"
b"+        with open(LOCAL_PARAMETERS_FILE, encoding=u'utf-8') as pf:"
b'             parameters.update(json.load(pf))'
b'     if override:'
b'         parameters.update(override)'
b'@@ -35,25 +39,25 @@'
b' '
b' '
b' def try_rm(filename):'
b'-    """ Remove a file if it exists """'
b'+    u""" Remove a file if it exists """'
b'     try:'
b'         os.remove(filename)'
b'-    except OSError as ose:'
b'+    except OSError, ose:'
b'         if ose.errno != errno.ENOENT:'
b'             raise'
b' '
b' '
b' def report_warning(message, *args, **kwargs):'
b'-    """'
b'+    u"""'
b"     Print the message to stderr, it will be prefixed with 'WARNING:'"
b"     If stderr is a tty file the 'WARNING:' will be colored"
b'     """'
b"-    if sys.stderr.isatty() and os.name != 'nt':"
b"-        _msg_header = '\\033[0;33mWARNING:\\033[0m'"
b"+    if sys.stderr.isatty() and os.name != u'nt':"
b"+        _msg_header = u'\\033[0;33mWARNING:\\033[0m'"
b'     else:'
b"-        _msg_header = 'WARNING:'"
b"+        _msg_header = u'WARNING:'"
b"     output = f'{_msg_header} {message}\\n'"
b"-    if 'b' in getattr(sys.stderr, 'mode', ''):"
b"+    if u'b' in getattr(sys.stderr, u'mode', u''):"
b'         output = output.encode(preferredencoding())'
b'     sys.stderr.write(output)'
b' '
b'@@ -63,11 +67,11 @@'
b"         # Different instances of the downloader can't share the same dictionary"
b'         # some test set the "sublang" parameter, which would break the md5 checks.'
b'         params = get_params(override=override)'
b'-        super().__init__(params, auto_init=False)'
b'+        super(FakeYDL, self).__init__(params, auto_init=False)'
b'         self.result = []'
b' '
b'     def to_screen(self, s, *args, **kwargs):'
b'-        print(s)'
b'+        print s'
b' '
b'     def trouble(self, s, *args, **kwargs):'
b'         raise Exception(s)'
b'@@ -94,7 +98,7 @@'
b' def getwebpagetestcases():'
b'     for ie in yt_dlp.extractor.gen_extractors():'
b'         for tc in ie.get_webpage_testcases():'
b"-            tc.setdefault('add_ie', []).append('Generic')"
b"+            tc.setdefault(u'add_ie', []).append(u'Generic')"
b'             yield tc'
b' '
b' '
b'@@ -102,50 +106,50 @@'
b' '
b' '
b' def _iter_differences(got, expected, field):'
b'-    if isinstance(expected, str):'
b"-        op, _, val = expected.partition(':')"
b"-        if op in ('mincount', 'maxcount', 'count'):"
b'+    if isinstance(expected, unicode):'
b"+        op, _, val = expected.partition(u':')"
b"+        if op in (u'mincount', u'maxcount', u'count'):"
b'             if not isinstance(got, (list, dict)):'
b"                 yield field, f'expected either {list.__name__} or {dict.__name__}, got {type(got).__name__}'"
b'                 return'
b' '
b'             expected_num = int(val)'
b'             got_num = len(got)'
b"-            if op == 'mincount':"
b"+            if op == u'mincount':"
b'                 if got_num < expected_num:'
b"                     yield field, f'expected at least {val} items, got {got_num}'"
b'                 return'
b' '
b"-            if op == 'maxcount':"
b"+            if op == u'maxcount':"
b'                 if got_num > expected_num:'
b"                     yield field, f'expected at most {val} items, got {got_num}'"
b'                 return'
b' '
b"-            assert op == 'count'"
b"+            assert op == u'count'"
b'             if got_num != expected_num:'
b"                 yield field, f'expected exactly {val} items, got {got_num}'"
b'             return'
b' '
b'-        if not isinstance(got, str):'
b'+        if not isinstance(got, unicode):'
b"             yield field, f'expected {str.__name__}, got {type(got).__name__}'"
b'             return'
b' '
b"-        if op == 're':"
b"+        if op == u're':"
b'             if not re.match(val, got):'
b"                 yield field, f'should match {val!r}, got {got!r}'"
b'             return'
b' '
b"-        if op == 'startswith':"
b"+        if op == u'startswith':"
b'             if not got.startswith(val):'
b"                 yield field, f'should start with {val!r}, got {got!r}'"
b'             return'
b' '
b"-        if op == 'contains':"
b"+        if op == u'contains':"
b'             if not val.startswith(got):'
b"                 yield field, f'should contain {val!r}, got {got!r}'"
b'             return'
b' '
b"-        if op == 'md5':"
b"+        if op == u'md5':"
b'             hash_val = md5(got)'
b'             if hash_val != val:'
b"                 yield field, f'expected hash {val}, got {hash_val}'"
b'@@ -176,8 +180,8 @@'
b"             yield field, f'expected length of {len(expected)}, got {len(got)}'"
b'             return'
b' '
b'-        for index, (got_val, expected_val) in enumerate(zip(got, expected)):'
b"-            field_name = str(index) if field is None else f'{field}.{index}'"
b'+        for index, (got_val, expected_val) in enumerate(izip(got, expected)):'
b"+            field_name = unicode(index) if field is None else f'{field}.{index}'"
b'             yield from _iter_differences(got_val, expected_val, field_name)'
b'         return'
b' '
b'@@ -191,18 +195,18 @@'
b'         return'
b' '
b'     fields = [field for field, _ in mismatches if field is not None]'
b"-    return ''.join(("
b'-        message, f\' ({", ".join(fields)})\' if fields else \'\','
b"+    return u''.join(("
b'+        message, f\' ({", ".join(fields)})\' if fields else u\'\','
b"         *(f'\\n\\t{field}: {message}' for field, message in mismatches)))"
b' '
b' '
b' def expect_value(self, got, expected, field):'
b"-    if message := _expect_value('values differ', got, expected, field):"
b"+    if message := _expect_value(u'values differ', got, expected, field):"
b'         self.fail(message)'
b' '
b' '
b' def expect_dict(self, got_dict, expected_dict):'
b"-    if message := _expect_value('dictionaries differ', got_dict, expected_dict, None):"
b"+    if message := _expect_value(u'dictionaries differ', got_dict, expected_dict, None):"
b'         self.fail(message)'
b' '
b' '
b'@@ -211,49 +215,48 @@'
b'         *YoutubeDL._format_fields,'
b' '
b'         # Lists'
b"-        'formats', 'thumbnails', 'subtitles', 'automatic_captions', 'comments', 'entries',"
b"+        u'formats', u'thumbnails', u'subtitles', u'automatic_captions', u'comments', u'entries',"
b' '
b'         # Auto-generated'
b"-        'autonumber', 'playlist', 'format_index', 'video_ext', 'audio_ext', 'duration_string', 'epoch', 'n_entries',"
b"-        'fulltitle', 'extractor', 'extractor_key', 'filename', 'filepath', 'infojson_filename', 'original_url',"
b"+        u'autonumber', u'playlist', u'format_index', u'video_ext', u'audio_ext', u'duration_string', u'epoch', u'n_entries',"
b"+        u'fulltitle', u'extractor', u'extractor_key', u'filename', u'filepath', u'infojson_filename', u'original_url',"
b' '
b'         # Only live_status needs to be checked'
b"-        'is_live', 'was_live',"
b"+        u'is_live', u'was_live',"
b'     )'
b' '
b"-    IGNORED_PREFIXES = ('', 'playlist', 'requested', 'webpage')"
b"+    IGNORED_PREFIXES = (u'', u'playlist', u'requested', u'webpage')"
b' '
b'     def sanitize(key, value):'
b"-        if isinstance(value, str) and len(value) > 100 and key != 'thumbnail':"
b"+        if isinstance(value, unicode) and len(value) > 100 and key != u'thumbnail':"
b"             return f'md5:{md5(value)}'"
b'         elif isinstance(value, list) and len(value) > 10:'
b"             return f'count:{len(value)}'"
b"-        elif key.endswith('_count') and isinstance(value, int):"
b"+        elif key.endswith(u'_count') and isinstance(value, int):"
b'             return int'
b'         return value'
b' '
b'-    test_info_dict = {'
b'-        key: sanitize(key, value) for key, value in got_dict.items()'
b'+    test_info_dict = dict(('
b'+        key, sanitize(key, value)) for key, value in got_dict.items()'
b'         if value is not None and key not in IGNORED_FIELDS and ('
b"             not any(key.startswith(f'{prefix}_') for prefix in IGNORED_PREFIXES)"
b"-            or key == '_old_archive_ids')"
b'-    }'
b"+            or key == u'_old_archive_ids'))"
b' '
b'     # display_id may be generated from id'
b"-    if test_info_dict.get('display_id') == test_info_dict.get('id'):"
b"-        test_info_dict.pop('display_id')"
b"+    if test_info_dict.get(u'display_id') == test_info_dict.get(u'id'):"
b"+        test_info_dict.pop(u'display_id')"
b' '
b'     # Remove deprecated fields'
b'     for old in YoutubeDL._deprecated_multivalue_fields:'
b'         test_info_dict.pop(old, None)'
b' '
b'     # release_year may be generated from release_date'
b"-    if try_call(lambda: test_info_dict['release_year'] == int(test_info_dict['release_date'][:4])):"
b"-        test_info_dict.pop('release_year')"
b"+    if try_call(lambda: test_info_dict[u'release_year'] == int(test_info_dict[u'release_date'][:4])):"
b"+        test_info_dict.pop(u'release_year')"
b' '
b'     # Check url for flat entries'
b"-    if got_dict.get('_type', 'video') != 'video' and got_dict.get('url'):"
b"-        test_info_dict['url'] = got_dict['url']"
b"+    if got_dict.get(u'_type', u'video') != u'video' and got_dict.get(u'url'):"
b"+        test_info_dict[u'url'] = got_dict[u'url']"
b' '
b'     return test_info_dict'
b' '
b'@@ -261,29 +264,29 @@'
b' def expect_info_dict(self, got_dict, expected_dict):'
b'     ALLOWED_KEYS_SORT_ORDER = ('
b'         # NB: Keep in sync with the docstring of extractor/common.py'
b"-        'id', 'ext', 'direct', 'display_id', 'title', 'alt_title', 'description', 'media_type',"
b"-        'uploader', 'uploader_id', 'uploader_url', 'channel', 'channel_id', 'channel_url', 'channel_is_verified',"
b"-        'channel_follower_count', 'comment_count', 'view_count', 'concurrent_view_count',"
b"-        'like_count', 'dislike_count', 'repost_count', 'average_rating', 'age_limit', 'duration', 'thumbnail', 'heatmap',"
b"-        'chapters', 'chapter', 'chapter_number', 'chapter_id', 'start_time', 'end_time', 'section_start', 'section_end',"
b"-        'categories', 'tags', 'cast', 'composers', 'artists', 'album_artists', 'creators', 'genres',"
b"-        'track', 'track_number', 'track_id', 'album', 'album_type', 'disc_number',"
b"-        'series', 'series_id', 'season', 'season_number', 'season_id', 'episode', 'episode_number', 'episode_id',"
b"-        'timestamp', 'upload_date', 'release_timestamp', 'release_date', 'release_year', 'modified_timestamp', 'modified_date',"
b"-        'playable_in_embed', 'availability', 'live_status', 'location', 'license', '_old_archive_ids',"
b"+        u'id', u'ext', u'direct', u'display_id', u'title', u'alt_title', u'description', u'media_type',"
b"+        u'uploader', u'uploader_id', u'uploader_url', u'channel', u'channel_id', u'channel_url', u'channel_is_verified',"
b"+        u'channel_follower_count', u'comment_count', u'view_count', u'concurrent_view_count',"
b"+        u'like_count', u'dislike_count', u'repost_count', u'average_rating', u'age_limit', u'duration', u'thumbnail', u'heatmap',"
b"+        u'chapters', u'chapter', u'chapter_number', u'chapter_id', u'start_time', u'end_time', u'section_start', u'section_end',"
b"+        u'categories', u'tags', u'cast', u'composers', u'artists', u'album_artists', u'creators', u'genres',"
b"+        u'track', u'track_number', u'track_id', u'album', u'album_type', u'disc_number',"
b"+        u'series', u'series_id', u'season', u'season_number', u'season_id', u'episode', u'episode_number', u'episode_id',"
b"+        u'timestamp', u'upload_date', u'release_timestamp', u'release_date', u'release_year', u'modified_timestamp', u'modified_date',"
b"+        u'playable_in_embed', u'availability', u'live_status', u'location', u'license', u'_old_archive_ids',"
b'     )'
b' '
b'     expect_dict(self, got_dict, expected_dict)'
b'     # Check for the presence of mandatory fields'
b"-    if got_dict.get('_type') not in ('playlist', 'multi_video'):"
b"-        mandatory_fields = ['id', 'title']"
b"-        if expected_dict.get('ext'):"
b"-            mandatory_fields.extend(('url', 'ext'))"
b"+    if got_dict.get(u'_type') not in (u'playlist', u'multi_video'):"
b"+        mandatory_fields = [u'id', u'title']"
b"+        if expected_dict.get(u'ext'):"
b"+            mandatory_fields.extend((u'url', u'ext'))"
b'         for key in mandatory_fields:'
b"             self.assertTrue(got_dict.get(key), f'Missing mandatory field {key}')"
b'     # Check for mandatory fields that are automatically set by YoutubeDL'
b"-    if got_dict.get('_type', 'video') == 'video':"
b"-        for key in ['webpage_url', 'extractor', 'extractor_key']:"
b"+    if got_dict.get(u'_type', u'video') == u'video':"
b"+        for key in [u'webpage_url', u'extractor', u'extractor_key']:"
b"             self.assertTrue(got_dict.get(key), f'Missing field: {key}')"
b' '
b'     test_info_dict = sanitize_got_info_dict(got_dict)'
b'@@ -297,29 +300,29 @@'
b'         key=lambda x: ALLOWED_KEYS_SORT_ORDER.index(x))'
b'     if missing_keys:'
b'         def _repr(v):'
b'-            if isinstance(v, str):'
b'-                return "\'{}\'".format(v.replace(\'\\\\\', \'\\\\\\\\\').replace("\'", "\\\\\'").replace(\'\\n\', \'\\\\n\'))'
b'+            if isinstance(v, unicode):'
b'+                return u"\'{}\'".format(v.replace(u\'\\\\\', u\'\\\\\\\\\').replace(u"\'", u"\\\\\'").replace(u\'\\n\', u\'\\\\n\'))'
b'             elif isinstance(v, type):'
b'                 return v.__name__'
b'             else:'
b'                 return repr(v)'
b"-        info_dict_str = ''.join("
b"+        info_dict_str = u''.join("
b"             f'    {_repr(k)}: {_repr(v)},\\n'"
b'             for k, v in test_info_dict.items() if k not in missing_keys)'
b'         if info_dict_str:'
b"-            info_dict_str += '\\n'"
b"-        info_dict_str += ''.join("
b"+            info_dict_str += u'\\n'"
b"+        info_dict_str += u''.join("
b"             f'    {_repr(k)}: {_repr(test_info_dict[k])},\\n'"
b'             for k in missing_keys)'
b"-        info_dict_str = '\\n\\'info_dict\\': {\\n' + info_dict_str + '},\\n'"
b"-        write_string(info_dict_str.replace('\\n', '\\n        '), out=sys.stderr)"
b"+        info_dict_str = u'\\n\\'info_dict\\': {\\n' + info_dict_str + u'},\\n'"
b"+        write_string(info_dict_str.replace(u'\\n', u'\\n        '), out=sys.stderr)"
b'         self.assertFalse('
b'             missing_keys,'
b"-            'Missing keys in test definition: {}'.format(', '.join(sorted(missing_keys))))"
b"+            u'Missing keys in test definition: {}'.format(u', '.join(sorted(missing_keys))))"
b' '
b' '
b' def assertRegexpMatches(self, text, regexp, msg=None):'
b"-    if hasattr(self, 'assertRegexp'):"
b"+    if hasattr(self, u'assertRegexp'):"
b'         return self.assertRegexp(text, regexp, msg)'
b'     else:'
b'         m = re.match(regexp, text)'
b'@@ -330,7 +333,7 @@'
b'             if msg is None:'
b'                 msg = note'
b'             else:'
b"-                msg = note + ', ' + msg"
b"+                msg = note + u', ' + msg"
b'             self.assertTrue(m, msg)'
b' '
b' '
b'@@ -366,7 +369,7 @@'
b' '
b' '
b' def http_server_port(httpd):'
b"-    if os.name == 'java' and isinstance(httpd.socket, ssl.SSLSocket):"
b"+    if os.name == u'java' and isinstance(httpd.socket, ssl.SSLSocket):"
b'         # In Jython SSLSocket is not a subclass of socket.socket'
b'         sock = httpd.socket.sock'
b'     else:'
