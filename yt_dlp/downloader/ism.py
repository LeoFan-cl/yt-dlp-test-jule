from __future__ import absolute_import
import binascii
import io
import struct
import time

from .fragment import FragmentFD
from ..networking.exceptions import HTTPError
from ..utils import RetryManager

u8 = struct.Struct(u'>B')
u88 = struct.Struct(u'>Bx')
u16 = struct.Struct(u'>H')
u1616 = struct.Struct(u'>Hxx')
u32 = struct.Struct(u'>I')
u64 = struct.Struct(u'>Q')

s88 = struct.Struct(u'>bx')
s16 = struct.Struct(u'>h')
s1616 = struct.Struct(u'>hxx')
s32 = struct.Struct(u'>i')

unity_matrix = (s32.pack(0x10000) + s32.pack(0) * 3) * 2 + s32.pack(0x40000000)

TRACK_ENABLED = 0x1
TRACK_IN_MOVIE = 0x2
TRACK_IN_PREVIEW = 0x4

SELF_CONTAINED = 0x1


def box(box_type, payload):
    return u32.pack(8 + len(payload)) + box_type + payload


def full_box(box_type, version, flags, payload):
    return box(box_type, u8.pack(version) + u32.pack(flags)[1:] + payload)


def write_piff_header(stream, params):
    track_id = params[u'track_id']
    fourcc = params[u'fourcc']
    duration = params[u'duration']
    timescale = params.get(u'timescale', 10000000)
    language = params.get(u'language', u'und')
    height = params.get(u'height', 0)
    width = params.get(u'width', 0)
    stream_type = params[u'stream_type']
    creation_time = modification_time = int(time.time())

    ftyp_payload = 'isml'  # major brand
    ftyp_payload += u32.pack(1)  # minor version
    ftyp_payload += 'piff' + 'iso2'  # compatible brands
    stream.write(box('ftyp', ftyp_payload))  # File Type Box

    mvhd_payload = u64.pack(creation_time)
    mvhd_payload += u64.pack(modification_time)
    mvhd_payload += u32.pack(timescale)
    mvhd_payload += u64.pack(duration)
    mvhd_payload += s1616.pack(1)  # rate
    mvhd_payload += s88.pack(1)  # volume
    mvhd_payload += u16.pack(0)  # reserved
    mvhd_payload += u32.pack(0) * 2  # reserved
    mvhd_payload += unity_matrix
    mvhd_payload += u32.pack(0) * 6  # pre defined
    mvhd_payload += u32.pack(0xffffffff)  # next track id
    moov_payload = full_box('mvhd', 1, 0, mvhd_payload)  # Movie Header Box

    tkhd_payload = u64.pack(creation_time)
    tkhd_payload += u64.pack(modification_time)
    tkhd_payload += u32.pack(track_id)  # track id
    tkhd_payload += u32.pack(0)  # reserved
    tkhd_payload += u64.pack(duration)
    tkhd_payload += u32.pack(0) * 2  # reserved
    tkhd_payload += s16.pack(0)  # layer
    tkhd_payload += s16.pack(0)  # alternate group
    tkhd_payload += s88.pack(1 if stream_type == u'audio' else 0)  # volume
    tkhd_payload += u16.pack(0)  # reserved
    tkhd_payload += unity_matrix
    tkhd_payload += u1616.pack(width)
    tkhd_payload += u1616.pack(height)
    trak_payload = full_box('tkhd', 1, TRACK_ENABLED | TRACK_IN_MOVIE | TRACK_IN_PREVIEW, tkhd_payload)  # Track Header Box

    mdhd_payload = u64.pack(creation_time)
    mdhd_payload += u64.pack(modification_time)
    mdhd_payload += u32.pack(timescale)
    mdhd_payload += u64.pack(duration)
    mdhd_payload += u16.pack(((ord(language[0]) - 0x60) << 10) | ((ord(language[1]) - 0x60) << 5) | (ord(language[2]) - 0x60))
    mdhd_payload += u16.pack(0)  # pre defined
    mdia_payload = full_box('mdhd', 1, 0, mdhd_payload)  # Media Header Box

    hdlr_payload = u32.pack(0)  # pre defined
    if stream_type == u'audio':  # handler type
        hdlr_payload += 'soun'
        hdlr_payload += u32.pack(0) * 3  # reserved
        hdlr_payload += 'SoundHandler\0'  # name
    elif stream_type == u'video':
        hdlr_payload += 'vide'
        hdlr_payload += u32.pack(0) * 3  # reserved
        hdlr_payload += 'VideoHandler\0'  # name
    elif stream_type == u'text':
        hdlr_payload += 'subt'
        hdlr_payload += u32.pack(0) * 3  # reserved
        hdlr_payload += 'SubtitleHandler\0'  # name
    else:
        assert False
    mdia_payload += full_box('hdlr', 0, 0, hdlr_payload)  # Handler Reference Box

    if stream_type == u'audio':
        smhd_payload = s88.pack(0)  # balance
        smhd_payload += u16.pack(0)  # reserved
        media_header_box = full_box('smhd', 0, 0, smhd_payload)  # Sound Media Header
    elif stream_type == u'video':
        vmhd_payload = u16.pack(0)  # graphics mode
        vmhd_payload += u16.pack(0) * 3  # opcolor
        media_header_box = full_box('vmhd', 0, 1, vmhd_payload)  # Video Media Header
    elif stream_type == u'text':
        media_header_box = full_box('sthd', 0, 0, '')  # Subtitle Media Header
    else:
        assert False
    minf_payload = media_header_box

    dref_payload = u32.pack(1)  # entry count
    dref_payload += full_box('url ', 0, SELF_CONTAINED, '')  # Data Entry URL Box
    dinf_payload = full_box('dref', 0, 0, dref_payload)  # Data Reference Box
    minf_payload += box('dinf', dinf_payload)  # Data Information Box

    stsd_payload = u32.pack(1)  # entry count

    sample_entry_payload = u8.pack(0) * 6  # reserved
    sample_entry_payload += u16.pack(1)  # data reference index
    if stream_type == u'audio':
        sample_entry_payload += u32.pack(0) * 2  # reserved
        sample_entry_payload += u16.pack(params.get(u'channels', 2))
        sample_entry_payload += u16.pack(params.get(u'bits_per_sample', 16))
        sample_entry_payload += u16.pack(0)  # pre defined
        sample_entry_payload += u16.pack(0)  # reserved
        sample_entry_payload += u1616.pack(params[u'sampling_rate'])

        if fourcc == u'AACL':
            sample_entry_box = box('mp4a', sample_entry_payload)
        if fourcc == u'EC-3':
            sample_entry_box = box('ec-3', sample_entry_payload)
    elif stream_type == u'video':
        sample_entry_payload += u16.pack(0)  # pre defined
        sample_entry_payload += u16.pack(0)  # reserved
        sample_entry_payload += u32.pack(0) * 3  # pre defined
        sample_entry_payload += u16.pack(width)
        sample_entry_payload += u16.pack(height)
        sample_entry_payload += u1616.pack(0x48)  # horiz resolution 72 dpi
        sample_entry_payload += u1616.pack(0x48)  # vert resolution 72 dpi
        sample_entry_payload += u32.pack(0)  # reserved
        sample_entry_payload += u16.pack(1)  # frame count
        sample_entry_payload += u8.pack(0) * 32  # compressor name
        sample_entry_payload += u16.pack(0x18)  # depth
        sample_entry_payload += s16.pack(-1)  # pre defined

        codec_private_data = binascii.unhexlify(params[u'codec_private_data'].encode())
        if fourcc in (u'H264', u'AVC1'):
            sps, pps = codec_private_data.split(u32.pack(1))[1:]
            avcc_payload = u8.pack(1)  # configuration version
            avcc_payload += sps[1:4]  # avc profile indication + profile compatibility + avc level indication
            avcc_payload += u8.pack(0xfc | (params.get(u'nal_unit_length_field', 4) - 1))  # complete representation (1) + reserved (11111) + length size minus one
            avcc_payload += u8.pack(1)  # reserved (0) + number of sps (0000001)
            avcc_payload += u16.pack(len(sps))
            avcc_payload += sps
            avcc_payload += u8.pack(1)  # number of pps
            avcc_payload += u16.pack(len(pps))
            avcc_payload += pps
            sample_entry_payload += box('avcC', avcc_payload)  # AVC Decoder Configuration Record
            sample_entry_box = box('avc1', sample_entry_payload)  # AVC Simple Entry
        else:
            assert False
    elif stream_type == u'text':
        if fourcc == u'TTML':
            sample_entry_payload += 'http://www.w3.org/ns/ttml\0'  # namespace
            sample_entry_payload += '\0'  # schema location
            sample_entry_payload += '\0'  # auxilary mime types(??)
            sample_entry_box = box('stpp', sample_entry_payload)
        else:
            assert False
    else:
        assert False
    stsd_payload += sample_entry_box

    stbl_payload = full_box('stsd', 0, 0, stsd_payload)  # Sample Description Box

    stts_payload = u32.pack(0)  # entry count
    stbl_payload += full_box('stts', 0, 0, stts_payload)  # Decoding Time to Sample Box

    stsc_payload = u32.pack(0)  # entry count
    stbl_payload += full_box('stsc', 0, 0, stsc_payload)  # Sample To Chunk Box

    stco_payload = u32.pack(0)  # entry count
    stbl_payload += full_box('stco', 0, 0, stco_payload)  # Chunk Offset Box

    minf_payload += box('stbl', stbl_payload)  # Sample Table Box

    mdia_payload += box('minf', minf_payload)  # Media Information Box

    trak_payload += box('mdia', mdia_payload)  # Media Box

    moov_payload += box('trak', trak_payload)  # Track Box

    mehd_payload = u64.pack(duration)
    mvex_payload = full_box('mehd', 1, 0, mehd_payload)  # Movie Extends Header Box

    trex_payload = u32.pack(track_id)  # track id
    trex_payload += u32.pack(1)  # default sample description index
    trex_payload += u32.pack(0)  # default sample duration
    trex_payload += u32.pack(0)  # default sample size
    trex_payload += u32.pack(0)  # default sample flags
    mvex_payload += full_box('trex', 0, 0, trex_payload)  # Track Extends Box

    moov_payload += box('mvex', mvex_payload)  # Movie Extends Box
    stream.write(box('moov', moov_payload))  # Movie Box


def extract_box_data(data, box_sequence):
    data_reader = io.BytesIO(data)
    while True:
        box_size = u32.unpack(data_reader.read(4))[0]
        box_type = data_reader.read(4)
        if box_type == box_sequence[0]:
            box_data = data_reader.read(box_size - 8)
            if len(box_sequence) == 1:
                return box_data
            return extract_box_data(box_data, box_sequence[1:])
        data_reader.seek(box_size - 8, 1)


class IsmFD(FragmentFD):
    u"""
    Download segments in a ISM manifest
    """

    def real_download(self, filename, info_dict):
        segments = info_dict[u'fragments'][:1] if self.params.get(
            u'test', False) else info_dict[u'fragments']

        ctx = {
            u'filename': filename,
            u'total_frags': len(segments),
        }

        self._prepare_and_start_frag_download(ctx, info_dict)

        extra_state = ctx.setdefault(u'extra_state', {
            u'ism_track_written': False,
        })

        skip_unavailable_fragments = self.params.get(u'skip_unavailable_fragments', True)

        frag_index = 0
        for segment in segments:
            frag_index += 1
            if frag_index <= ctx[u'fragment_index']:
                continue

            retry_manager = RetryManager(self.params.get(u'fragment_retries'), self.report_retry,
                                         frag_index=frag_index, fatal=not skip_unavailable_fragments)
            for retry in retry_manager:
                try:
                    success = self._download_fragment(ctx, segment[u'url'], info_dict)
                    if not success:
                        return False
                    frag_content = self._read_fragment(ctx)

                    if not extra_state[u'ism_track_written']:
                        tfhd_data = extract_box_data(frag_content, ['moof', 'traf', 'tfhd'])
                        info_dict[u'_download_params'][u'track_id'] = u32.unpack(tfhd_data[4:8])[0]
                        write_piff_header(ctx[u'dest_stream'], info_dict[u'_download_params'])
                        extra_state[u'ism_track_written'] = True
                    self._append_fragment(ctx, frag_content)
                except HTTPError, err:
                    retry.error = err
                    continue

            if retry_manager.error:
                if not skip_unavailable_fragments:
                    return False
                self.report_skip_fragment(frag_index)

        return self._finish_frag_download(ctx, info_dict)
