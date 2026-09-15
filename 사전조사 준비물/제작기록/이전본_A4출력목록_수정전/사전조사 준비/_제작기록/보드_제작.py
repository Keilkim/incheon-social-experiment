# -*- coding: utf-8 -*-
"""A3 손잡이 없는 휴대용 폼보드 출력 목록과 미리보기."""
from pathlib import Path
import shutil, subprocess, sys
sys.path.insert(0, str(Path(__file__).parent))
import docx_공통 as W
from docx.shared import Cm

ROOT=W.ROOT
SOURCE=ROOT.parent/'사전조사 준비물'
OUT=ROOT/'보드_출력파일'
PV=Path(__file__).parent/'미리보기'
OUT.mkdir(exist_ok=True);PV.mkdir(exist_ok=True)
BOARDS=[
 ('B1','굴포천 사전판','05_굴포천_폼보드.pdf','B1_굴포천_스티커판_사전_A3.pdf','A3 세로 · 297×420mm'),
 ('B4','차이나타운 보드','04_차이나타운_폼보드.pdf','B4_차이나타운_스티커보드_A3.pdf','A3 가로 · 420×297mm'),
]
d=W.new(header='보드 · 출력물 목록 · 2026.09.13')
W.title(d,'A3 폼보드 · 출력물 목록','폼보드는 사람이 들고 이동합니다. 인쇄용 PDF는 같은 폴더의 「보드_출력파일」에 있습니다.')
W.table(d,[['구분','크기','수량','인쇄 파일']]+[[title,size,'폼보드 1판',name] for code,title,source,name,size in BOARDS],[3.2,4,2.2,8.4],size=9)
W.h1(d,'준비 · 사용')
W.bullets(d,[
 'PDF를 **A3 실제 크기(100%)**로 출력해 같은 크기의 폼보드에 붙입니다.',
 '굴포천은 **카메라 1대 + 삼각대 1개**를 함께 준비합니다.',
 '굴포천 200명×4문항 = 스티커 800개. 차이나타운도 4문항 800개에 여분 200개를 더해 1,000개를 준비합니다.',
 '응답칸이 차면 판을 사진으로 남기고 스티커를 집계한 뒤, 같은 A3 출력지를 덧붙여 계속 사용합니다. 집계할 때는 교체한 종이별 응답을 합산합니다.',
 '차이나타운 그림 A·B는 실제 안내 그림을 넣습니다. Q2 응답칸은 불투명 덮개로 가려 안내합니다.',
 '시간 확인과 기록에는 **핸드폰**을 사용합니다. 송도는 **이미 구매한 A4 받침대**를 가져갑니다.',
],9.5)
for code,title,source,name,size in BOARDS:
 dest=OUT/name;shutil.copy2(SOURCE/source,dest)
 image=PV/(dest.stem+'.png')
 subprocess.run(['pdftoppm','-scale-to','1500','-png','-singlefile',str(dest),str(image.with_suffix(''))],check=True)
 W.page_break(d);W.h1(d,f'{code}  {title} · {size}')
 d.add_paragraph().add_run().add_picture(str(image),width=Cm(17 if '가로' in size else 15))
d.save(ROOT/'04_보드 출력물 목록.docx')
print('A3 보드 2종과 출력물 목록 갱신')
