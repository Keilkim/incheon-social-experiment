# -*- coding: utf-8 -*-
"""최신 시간표·준비물 제작기로 PDF, DOCX, 일정 엑셀을 함께 갱신."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '사전조사 준비물' / '제작기록'))
from 시간표_준비물_제작 import build

if __name__ == '__main__':
    build()
