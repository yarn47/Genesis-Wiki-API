import sys; sys.path.insert(0,'.')
from bmp import load, lum

def is_bg(p):
    return lum(p) > 205 and (max(p) - min(p)) < 30

def tiles(px, x0, x1, ys, min_w=60):
    """여러 줄을 함께 보고 배경이 아닌 구간(아이콘 타일)을 찾는다"""
    runs, start = [], None
    for x in range(x0, x1):
        bg = all(is_bg(px(x, y)) for y in ys)
        if not bg and start is None:
            start = x
        elif bg and start is not None:
            if x - start >= min_w:
                runs.append((start, x - 1))
            start = None
    if start is not None and x1 - start >= min_w:
        runs.append((start, x1 - 1))
    return runs

def vtiles(px, y0, y1, xs, min_h=60):
    runs, start = [], None
    for y in range(y0, y1):
        bg = all(is_bg(px(x, y)) for x in xs)
        if not bg and start is None:
            start = y
        elif bg and start is not None:
            if y - start >= min_h:
                runs.append((start, y - 1))
            start = None
    if start is not None and y1 - start >= min_h:
        runs.append((start, y1 - 1))
    return runs
