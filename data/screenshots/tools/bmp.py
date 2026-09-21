"""JPEG를 BMP로 바꿔 픽셀을 읽고, 어두운 아이콘 타일의 경계를 찾는다 (PIL 없이)."""
import struct, subprocess, sys, tempfile, os

def load(path):
    tmp = tempfile.mktemp(suffix='.bmp')
    subprocess.run(['sips', '-s', 'format', 'bmp', path, '--out', tmp],
                   check=True, capture_output=True)
    data = open(tmp, 'rb').read()
    os.unlink(tmp)
    off = struct.unpack_from('<I', data, 10)[0]
    w, h = struct.unpack_from('<ii', data, 18)
    bpp = struct.unpack_from('<H', data, 28)[0]
    assert bpp in (24, 32), bpp
    stride = ((w * bpp // 8) + 3) // 4 * 4
    flip = h > 0
    h = abs(h)
    def px(x, y):
        row = (h - 1 - y) if flip else y
        i = off + row * stride + x * (bpp // 8)
        b, g, r = data[i], data[i+1], data[i+2]
        return r, g, b
    return w, h, px

def lum(p):
    r, g, b = p
    return 0.299*r + 0.587*g + 0.114*b

def dark_runs(px, y, x0, x1, thr=120, min_len=40):
    """y줄에서 어두운 구간(아이콘 타일)의 [시작, 끝] 목록"""
    runs, start = [], None
    for x in range(x0, x1):
        d = lum(px(x, y)) < thr
        if d and start is None:
            start = x
        elif not d and start is not None:
            if x - start >= min_len:
                runs.append((start, x - 1))
            start = None
    if start is not None and x1 - start >= min_len:
        runs.append((start, x1 - 1))
    return runs

def vertical_bounds(px, x, y0, y1, thr=120, min_len=40):
    runs, start = [], None
    for y in range(y0, y1):
        d = lum(px(x, y)) < thr
        if d and start is None:
            start = y
        elif not d and start is not None:
            if y - start >= min_len:
                runs.append((start, y - 1))
            start = None
    if start is not None and y1 - start >= min_len:
        runs.append((start, y1 - 1))
    return runs
