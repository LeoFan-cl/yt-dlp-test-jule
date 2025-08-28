b'--- ./yt_dlp/downloader/ism.py\t(original)'
b'+++ ./yt_dlp/downloader/ism.py\t(refactored)'
b'@@ -48,10 +48,10 @@'
b"     stream_type = params[u'stream_type']"
b'     creation_time = modification_time = int(time.time())'
b' '
b"-    ftyp_payload = 'isml'  # major brand"
b"+    ftyp_payload = u'isml'  # major brand"
b'     ftyp_payload += u32.pack(1)  # minor version'
b"-    ftyp_payload += 'piff' + 'iso2'  # compatible brands"
b"-    stream.write(box('ftyp', ftyp_payload))  # File Type Box"
b"+    ftyp_payload += u'piff' + u'iso2'  # compatible brands"
b"+    stream.write(box(u'ftyp', ftyp_payload))  # File Type Box"
b' '
b'     mvhd_payload = u64.pack(creation_time)'
b'     mvhd_payload += u64.pack(modification_time)'
b'@@ -64,7 +64,7 @@'
b'     mvhd_payload += unity_matrix'
b'     mvhd_payload += u32.pack(0) * 6  # pre defined'
b'     mvhd_payload += u32.pack(0xffffffff)  # next track id'
b"-    moov_payload = full_box('mvhd', 1, 0, mvhd_payload)  # Movie Header Box"
b"+    moov_payload = full_box(u'mvhd', 1, 0, mvhd_payload)  # Movie Header Box"
b' '
b'     tkhd_payload = u64.pack(creation_time)'
b'     tkhd_payload += u64.pack(modification_time)'
b'@@ -79,7 +79,7 @@'
b'     tkhd_payload += unity_matrix'
b'     tkhd_payload += u1616.pack(width)'
b'     tkhd_payload += u1616.pack(height)'
b"-    trak_payload = full_box('tkhd', 1, TRACK_ENABLED | TRACK_IN_MOVIE | TRACK_IN_PREVIEW, tkhd_payload)  # Track Header Box"
b"+    trak_payload = full_box(u'tkhd', 1, TRACK_ENABLED | TRACK_IN_MOVIE | TRACK_IN_PREVIEW, tkhd_payload)  # Track Header Box"
b' '
b'     mdhd_payload = u64.pack(creation_time)'
b'     mdhd_payload += u64.pack(modification_time)'
b'@@ -87,43 +87,43 @@'
b'     mdhd_payload += u64.pack(duration)'
b'     mdhd_payload += u16.pack(((ord(language[0]) - 0x60) << 10) | ((ord(language[1]) - 0x60) << 5) | (ord(language[2]) - 0x60))'
b'     mdhd_payload += u16.pack(0)  # pre defined'
b"-    mdia_payload = full_box('mdhd', 1, 0, mdhd_payload)  # Media Header Box"
b"+    mdia_payload = full_box(u'mdhd', 1, 0, mdhd_payload)  # Media Header Box"
b' '
b'     hdlr_payload = u32.pack(0)  # pre defined'
b"     if stream_type == u'audio':  # handler type"
b"-        hdlr_payload += 'soun'"
b"+        hdlr_payload += u'soun'"
b'         hdlr_payload += u32.pack(0) * 3  # reserved'
b"-        hdlr_payload += 'SoundHandler\\0'  # name"
b"+        hdlr_payload += u'SoundHandler\\0'  # name"
b"     elif stream_type == u'video':"
b"-        hdlr_payload += 'vide'"
b"+        hdlr_payload += u'vide'"
b'         hdlr_payload += u32.pack(0) * 3  # reserved'
b"-        hdlr_payload += 'VideoHandler\\0'  # name"
b"+        hdlr_payload += u'VideoHandler\\0'  # name"
b"     elif stream_type == u'text':"
b"-        hdlr_payload += 'subt'"
b"+        hdlr_payload += u'subt'"
b'         hdlr_payload += u32.pack(0) * 3  # reserved'
b"-        hdlr_payload += 'SubtitleHandler\\0'  # name"
b"+        hdlr_payload += u'SubtitleHandler\\0'  # name"
b'     else:'
b'         assert False'
b"-    mdia_payload += full_box('hdlr', 0, 0, hdlr_payload)  # Handler Reference Box"
b"+    mdia_payload += full_box(u'hdlr', 0, 0, hdlr_payload)  # Handler Reference Box"
b' '
b"     if stream_type == u'audio':"
b'         smhd_payload = s88.pack(0)  # balance'
b'         smhd_payload += u16.pack(0)  # reserved'
b"-        media_header_box = full_box('smhd', 0, 0, smhd_payload)  # Sound Media Header"
b"+        media_header_box = full_box(u'smhd', 0, 0, smhd_payload)  # Sound Media Header"
b"     elif stream_type == u'video':"
b'         vmhd_payload = u16.pack(0)  # graphics mode'
b'         vmhd_payload += u16.pack(0) * 3  # opcolor'
b"-        media_header_box = full_box('vmhd', 0, 1, vmhd_payload)  # Video Media Header"
b"+        media_header_box = full_box(u'vmhd', 0, 1, vmhd_payload)  # Video Media Header"
b"     elif stream_type == u'text':"
b"-        media_header_box = full_box('sthd', 0, 0, '')  # Subtitle Media Header"
b"+        media_header_box = full_box(u'sthd', 0, 0, u'')  # Subtitle Media Header"
b'     else:'
b'         assert False'
b'     minf_payload = media_header_box'
b' '
b'     dref_payload = u32.pack(1)  # entry count'
b"-    dref_payload += full_box('url ', 0, SELF_CONTAINED, '')  # Data Entry URL Box"
b"-    dinf_payload = full_box('dref', 0, 0, dref_payload)  # Data Reference Box"
b"-    minf_payload += box('dinf', dinf_payload)  # Data Information Box"
b"+    dref_payload += full_box(u'url ', 0, SELF_CONTAINED, u'')  # Data Entry URL Box"
b"+    dinf_payload = full_box(u'dref', 0, 0, dref_payload)  # Data Reference Box"
b"+    minf_payload += box(u'dinf', dinf_payload)  # Data Information Box"
b' '
b'     stsd_payload = u32.pack(1)  # entry count'
b' '
b'@@ -138,9 +138,9 @@'
b"         sample_entry_payload += u1616.pack(params[u'sampling_rate'])"
b' '
b"         if fourcc == u'AACL':"
b"-            sample_entry_box = box('mp4a', sample_entry_payload)"
b"+            sample_entry_box = box(u'mp4a', sample_entry_payload)"
b"         if fourcc == u'EC-3':"
b"-            sample_entry_box = box('ec-3', sample_entry_payload)"
b"+            sample_entry_box = box(u'ec-3', sample_entry_payload)"
b"     elif stream_type == u'video':"
b'         sample_entry_payload += u16.pack(0)  # pre defined'
b'         sample_entry_payload += u16.pack(0)  # reserved'
b'@@ -167,53 +167,53 @@'
b'             avcc_payload += u8.pack(1)  # number of pps'
b'             avcc_payload += u16.pack(len(pps))'
b'             avcc_payload += pps'
b"-            sample_entry_payload += box('avcC', avcc_payload)  # AVC Decoder Configuration Record"
b"-            sample_entry_box = box('avc1', sample_entry_payload)  # AVC Simple Entry"
b"+            sample_entry_payload += box(u'avcC', avcc_payload)  # AVC Decoder Configuration Record"
b"+            sample_entry_box = box(u'avc1', sample_entry_payload)  # AVC Simple Entry"
b'         else:'
b'             assert False'
b"     elif stream_type == u'text':"
b"         if fourcc == u'TTML':"
b"-            sample_entry_payload += 'http://www.w3.org/ns/ttml\\0'  # namespace"
b"-            sample_entry_payload += '\\0'  # schema location"
b"-            sample_entry_payload += '\\0'  # auxilary mime types(??)"
b"-            sample_entry_box = box('stpp', sample_entry_payload)"
b"+            sample_entry_payload += u'http://www.w3.org/ns/ttml\\0'  # namespace"
b"+            sample_entry_payload += u'\\0'  # schema location"
b"+            sample_entry_payload += u'\\0'  # auxilary mime types(??)"
b"+            sample_entry_box = box(u'stpp', sample_entry_payload)"
b'         else:'
b'             assert False'
b'     else:'
b'         assert False'
b'     stsd_payload += sample_entry_box'
b' '
b"-    stbl_payload = full_box('stsd', 0, 0, stsd_payload)  # Sample Description Box"
b"+    stbl_payload = full_box(u'stsd', 0, 0, stsd_payload)  # Sample Description Box"
b' '
b'     stts_payload = u32.pack(0)  # entry count'
b"-    stbl_payload += full_box('stts', 0, 0, stts_payload)  # Decoding Time to Sample Box"
b"+    stbl_payload += full_box(u'stts', 0, 0, stts_payload)  # Decoding Time to Sample Box"
b' '
b'     stsc_payload = u32.pack(0)  # entry count'
b"-    stbl_payload += full_box('stsc', 0, 0, stsc_payload)  # Sample To Chunk Box"
b"+    stbl_payload += full_box(u'stsc', 0, 0, stsc_payload)  # Sample To Chunk Box"
b' '
b'     stco_payload = u32.pack(0)  # entry count'
b"-    stbl_payload += full_box('stco', 0, 0, stco_payload)  # Chunk Offset Box"
b'-'
b"-    minf_payload += box('stbl', stbl_payload)  # Sample Table Box"
b'-'
b"-    mdia_payload += box('minf', minf_payload)  # Media Information Box"
b'-'
b"-    trak_payload += box('mdia', mdia_payload)  # Media Box"
b'-'
b"-    moov_payload += box('trak', trak_payload)  # Track Box"
b"+    stbl_payload += full_box(u'stco', 0, 0, stco_payload)  # Chunk Offset Box"
b'+'
b"+    minf_payload += box(u'stbl', stbl_payload)  # Sample Table Box"
b'+'
b"+    mdia_payload += box(u'minf', minf_payload)  # Media Information Box"
b'+'
b"+    trak_payload += box(u'mdia', mdia_payload)  # Media Box"
b'+'
b"+    moov_payload += box(u'trak', trak_payload)  # Track Box"
b' '
b'     mehd_payload = u64.pack(duration)'
b"-    mvex_payload = full_box('mehd', 1, 0, mehd_payload)  # Movie Extends Header Box"
b"+    mvex_payload = full_box(u'mehd', 1, 0, mehd_payload)  # Movie Extends Header Box"
b' '
b'     trex_payload = u32.pack(track_id)  # track id'
b'     trex_payload += u32.pack(1)  # default sample description index'
b'     trex_payload += u32.pack(0)  # default sample duration'
b'     trex_payload += u32.pack(0)  # default sample size'
b'     trex_payload += u32.pack(0)  # default sample flags'
b"-    mvex_payload += full_box('trex', 0, 0, trex_payload)  # Track Extends Box"
b'-'
b"-    moov_payload += box('mvex', mvex_payload)  # Movie Extends Box"
b"-    stream.write(box('moov', moov_payload))  # Movie Box"
b"+    mvex_payload += full_box(u'trex', 0, 0, trex_payload)  # Track Extends Box"
b'+'
b"+    moov_payload += box(u'mvex', mvex_payload)  # Movie Extends Box"
b"+    stream.write(box(u'moov', moov_payload))  # Movie Box"
b' '
b' '
b' def extract_box_data(data, box_sequence):'
b'@@ -267,7 +267,7 @@'
b'                     frag_content = self._read_fragment(ctx)'
b' '
b"                     if not extra_state[u'ism_track_written']:"
b"-                        tfhd_data = extract_box_data(frag_content, ['moof', 'traf', 'tfhd'])"
b"+                        tfhd_data = extract_box_data(frag_content, [u'moof', u'traf', u'tfhd'])"
b"                         info_dict[u'_download_params'][u'track_id'] = u32.unpack(tfhd_data[4:8])[0]"
b"                         write_piff_header(ctx[u'dest_stream'], info_dict[u'_download_params'])"
b"                         extra_state[u'ism_track_written'] = True"
