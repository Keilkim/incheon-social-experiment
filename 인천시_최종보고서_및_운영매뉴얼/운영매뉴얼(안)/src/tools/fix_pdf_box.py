#!/usr/bin/env python3
"""Chrome PDF의 판형을 B5(182×257mm = 515.91×728.50pt)로 맞춘다.

Chrome --print-to-pdf는 @page{size:182mm 257mm}를 516×729.12pt로 반올림해 내보내고,
남는 0.62pt(약 0.22mm)를 쪽 아래에 흰 띠로 둔다. 지면은 위·왼쪽에서 시작하므로
MediaBox·CropBox를 [0, 남는 높이, 515.91, 원래 높이]로 잘라 판형을 정확히 맞춘다(벡터 그대로).

사용: python3 tools/fix_pdf_box.py <pdf> [<pdf> ...]   (제자리 덮어쓰기)
"""
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

W = 182 / 25.4 * 72   # 515.906
H = 257 / 25.4 * 72   # 728.504


def fix(path):
    r = PdfReader(path)
    w = PdfWriter(clone_from=r)
    for p in w.pages:
        mb = p.mediabox
        x0, y0, x1, y1 = float(mb.left), float(mb.bottom), float(mb.right), float(mb.top)
        box = RectangleObject([x0, y1 - H, x0 + W, y1])
        p.mediabox = box
        p.cropbox = box
        p.trimbox = box
        p.bleedbox = box
    w.write(path)
    print(f'{path}: {len(w.pages)}쪽 → {W:.2f}×{H:.2f}pt')


if __name__ == '__main__':
    for f in sys.argv[1:]:
        fix(f)
