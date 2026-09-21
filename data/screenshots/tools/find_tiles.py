"""스크린샷에서 아이콘 타일의 정확한 경계를 찾아 sips 크롭 명령을 뽑아준다.

    python3 find_tiles.py ../원본/083_iolin_class.jpg
    python3 find_tiles.py ../원본/138_iolin_skill.jpg

배경(양피지색)이 아닌 구간을 픽셀 단위로 훑어서 아이콘 타일의 x/y 범위를 찾고,
가로세로 비율이 정사각형에 가까운 것만 남긴다. 눈대중으로 자르지 않아도 된다.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bmp import load
from tiles import tiles, vtiles

BANDS = [
    # 라벨,               x 검색 범위(화면 비율), y 검색 범위
    ('클래스 탭 · 획득 스킬 줄', 0.50, 1.00, 335, 485),
    ('스킬 탭 · 액티브/초필살기 줄', 0.35, 1.00, 620, 780),
    ('스킬 탭 · 패시브 줄',        0.35, 1.00, 790, 960),
]

def run(path):
    w, h, px = load(path)
    print(f'\n=== {os.path.basename(path)}  {w}x{h} ===')
    for label, fx0, fx1, y0, y1 in BANDS:
        x0, x1 = int(w * fx0), int(w * fx1) - 8
        ys = list(range(y0 + 15, y1 - 15, 10))
        xs = [t for t in tiles(px, x0, x1, ys) if t[1] - t[0] + 1 <= 200]
        if not xs:
            continue
        found = []
        for (tx0, tx1) in xs:
            tw = tx1 - tx0 + 1
            mid = [(tx0 + tx1) // 2]
            for (ty0, ty1) in vtiles(px, y0, y1, mid):
                th = ty1 - ty0 + 1
                if 0.75 * tw <= th <= 1.35 * tw:      # 정사각형에 가까운 것만
                    found.append((tx0, ty0, tw, th))
        if not found:
            continue
        print(f'\n[{label}]')
        for (tx0, ty0, tw, th) in found:
            print(f'  x {tx0}  y {ty0}  {tw}x{th}')
            print(f'    sips -c {th} {tw} --cropOffset {ty0} {tx0} "{path}" --out icon.png')

for p in sys.argv[1:]:
    run(p)
