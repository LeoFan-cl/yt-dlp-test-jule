b'--- ./yt_dlp/downloader/f4m.py\t(original)'
b'+++ ./yt_dlp/downloader/f4m.py\t(refactored)'
b'@@ -42,10 +42,10 @@'
b"         return struct.unpack(u'!B', self.read_bytes(1))[0]"
b' '
b'     def read_string(self):'
b"-        res = ''"
b"+        res = u''"
b'         while True:'
b'             char = self.read_bytes(1)'
b"-            if char == '\\x00':"
b"+            if char == u'\\x00':"
b'                 break'
b'             res += char'
b'         return res'
b'@@ -152,14 +152,14 @@'
b'         segments = []'
b'         for _ in xrange(segments_count):'
b'             box_size, box_type, box_data = self.read_box_info()'
b"-            assert box_type == 'asrt'"
b"+            assert box_type == u'asrt'"
b'             segment = FlvReader(box_data).read_asrt()'
b'             segments.append(segment)'
b'         fragments_run_count = self.read_unsigned_char()'
b'         fragments = []'
b'         for _ in xrange(fragments_run_count):'
b'             box_size, box_type, box_data = self.read_box_info()'
b"-            assert box_type == 'afrt'"
b"+            assert box_type == u'afrt'"
b'             fragments.append(FlvReader(box_data).read_afrt())'
b' '
b'         return {'
b'@@ -170,7 +170,7 @@'
b' '
b'     def read_bootstrap_info(self):'
b'         total_size, box_type, box_data = self.read_box_info()'
b"-        assert box_type == 'abst'"
b"+        assert box_type == u'abst'"
b'         return FlvReader(box_data).read_abst()'
b' '
b' '
b'@@ -211,21 +211,21 @@'
b' def write_flv_header(stream):'
b'     u"""Writes the FLV header to stream"""'
b'     # FLV header'
b"-    stream.write('FLV\\x01')"
b"-    stream.write('\\x05')"
b"-    stream.write('\\x00\\x00\\x00\\x09')"
b"-    stream.write('\\x00\\x00\\x00\\x00')"
b"+    stream.write(u'FLV\\x01')"
b"+    stream.write(u'\\x05')"
b"+    stream.write(u'\\x00\\x00\\x00\\x09')"
b"+    stream.write(u'\\x00\\x00\\x00\\x00')"
b' '
b' '
b' def write_metadata_tag(stream, metadata):'
b'     u"""Writes optional metadata tag to stream"""'
b"-    SCRIPT_TAG = '\\x12'"
b"+    SCRIPT_TAG = u'\\x12'"
b'     FLV_TAG_HEADER_LEN = 11'
b' '
b'     if metadata:'
b'         stream.write(SCRIPT_TAG)'
b'         write_unsigned_int_24(stream, len(metadata))'
b"-        stream.write('\\x00\\x00\\x00\\x00\\x00\\x00\\x00')"
b"+        stream.write(u'\\x00\\x00\\x00\\x00\\x00\\x00\\x00')"
b'         stream.write(metadata)'
b'         write_unsigned_int(stream, FLV_TAG_HEADER_LEN + len(metadata))'
b' '
b'@@ -406,7 +406,7 @@'
b'                             dest_stream.write(down_data)'
b'                             break'
b'                         raise'
b"-                    if box_type == 'mdat':"
b"+                    if box_type == u'mdat':"
b'                         self._append_fragment(ctx, box_data)'
b'                         break'
b'             except HTTPError, err:'
