#!/usr/bin/env python3
"""Synthetic browser-Presentation-Video-Maker-style H.264 MP4 fixture.

A WebCodecs + ISO-BMFF mux path can store sparse VFR samples with long
explicit per-sample STTS durations instead of repeating 30 decoded frames
per second. This fixture encodes 39 real H.264 High frames, then changes
ONLY their MP4 sample-duration table and track/movie duration fields.
The encoded bitstream/mdat and chunk offsets remain untouched.

Intended for reproducing Reverse Clip decoder/fps behavior, not replacing
the user's actual media or claiming a byte-for-byte source match.
"""
from pathlib import Path
import struct
import subprocess

# 39 frames, 37.8060889 seconds, average fps 877500/850637 exactly.
# 34 short transition samples plus five long static slide spans.
TRANSITION_TICKS=27692
DURATIONS=(
    [216000] + [TRANSITION_TICKS]*8
    + [540000] + [TRANSITION_TICKS]*8
    + [630000] + [TRANSITION_TICKS]*8
    + [540000] + [TRANSITION_TICKS]*10
    + [535020]
)
assert len(DURATIONS)==39 and sum(DURATIONS)==3402548
TRACK_TIMESCALE=90000

def boxes(data: bytes):
    i=0
    while i<len(data):
        if i+8>len(data):
            raise ValueError("Truncated MP4 box")
        size=struct.unpack_from(">I",data,i)[0]
        kind=data[i+4:i+8]
        if size<8 or i+size>len(data):
            raise ValueError(f"Invalid MP4 box {kind!r} size={size}")
        yield kind,data[i+8:i+size]
        i+=size
    if i!=len(data):
        raise ValueError("Trailing box data")

def pack(kind: bytes, payload: bytes):
    return struct.pack(">I",len(payload)+8)+kind+payload

def rewrite(kind: bytes,payload: bytes):
    if kind in (b"moov",b"trak",b"mdia",b"minf",b"stbl"):
        return pack(kind,b"".join(rewrite(t,p) for t,p in boxes(payload)))
    if kind==b"stts":
        # version/flags retained; every sample gets its explicit duration.
        return pack(kind,payload[:4]+struct.pack(">I",len(DURATIONS))+
                    b"".join(struct.pack(">II",1,int(d)) for d in DURATIONS))
    if kind in (b"mdhd",b"tkhd",b"mvhd"):
        p=bytearray(payload)
        if p[0]!=0:
            raise ValueError("Expected non-extended synthetic duration header")
        if kind==b"mdhd":
            assert struct.unpack_from(">I",p,12)[0]==TRACK_TIMESCALE
            struct.pack_into(">I",p,16,sum(DURATIONS))
        elif kind==b"tkhd":
            struct.pack_into(">I",p,20,round(sum(DURATIONS)/TRACK_TIMESCALE*1000))
        else:
            assert struct.unpack_from(">I",p,12)[0]==1000
            struct.pack_into(">I",p,16,round(sum(DURATIONS)/TRACK_TIMESCALE*1000))
        return pack(kind,bytes(p))
    return pack(kind,payload)

def make_presentation_vfr_fixture(directory: Path,size: str="320x180") -> Path:
    source=directory/f"webcodecs-base-{size}.mp4"
    target=directory/f"presentation-vfr-{size}.mp4"
    subprocess.run([
        "ffmpeg","-hide_banner","-loglevel","error","-y","-threads","2",
        "-f","lavfi","-i",f"testsrc2=size={size}:rate=13/4:duration=12",
        "-frames:v","39","-c:v","libx264","-preset","veryfast","-crf","32",
        "-profile:v","high","-bf","0","-g","1","-pix_fmt","yuv420p",
        "-video_track_timescale","90000","-use_editlist","0",
        str(source)
    ],check=True,timeout=130)
    data=source.read_bytes()
    top=list(boxes(data))
    # mdat must precede moov so growing the moov box cannot relocate the
    # encoded NAL bytes pointed to by original stco chunk offsets.
    kinds=[t for t,_ in top]
    assert kinds.count(b"moov")==1 and kinds.count(b"mdat")==1, kinds
    assert kinds.index(b"mdat")<kinds.index(b"moov"), kinds
    target.write_bytes(b"".join(rewrite(t,p) for t,p in top))
    return target
