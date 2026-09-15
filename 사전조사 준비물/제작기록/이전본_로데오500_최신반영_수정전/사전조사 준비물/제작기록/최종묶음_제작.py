"""현재 조사용 파일을 모아 최종 폴더를 갱신한다. 이전 보고서와 제작 이력은 제외."""
from pathlib import Path
import shutil,re

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'최종_현장조사'
OUT.mkdir(exist_ok=True)
for folder in ['사전조사 준비물','1차 실험','2차 실험']:
 src=BASE/folder;dest=OUT/folder;dest.mkdir(exist_ok=True)
 for f in src.iterdir():
  if f.is_file() and not f.name.startswith('~$') and f.suffix in ['.pdf','.xlsx','.docx','.md']:
   shutil.copy2(f,dest/f.name)
  elif f.is_dir() and f.name in ['표정아이콘','약산초_지도','약산초_사진','차이나타운_그림']:
   shutil.copytree(f,dest/f.name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.DS_Store','__pycache__'))
 readme=dest/'00_먼저읽어주세요.md'
 if readme.exists():
  content=readme.read_text()
  content=re.sub(r'재생성:.*?이번 수정 전 파일.*?\n','',content,flags=re.S)
  readme.write_text(content)
prep=OUT/'사전조사 준비';prep.mkdir(exist_ok=True)
for name in ['02_사전조사 일정.xlsx','03_거점별 준비물.docx','04_전체 출력물 목록.docx','04_전체 출력물 목록.pdf']:
 shutil.copy2(BASE/'사전조사 준비'/name,prep/name)
shutil.copytree(BASE/'사전조사 준비/A4_출력파일',prep/'A4_출력파일',dirs_exist_ok=True)
boards=prep/'보드_출력파일';boards.mkdir(exist_ok=True)
for f in (BASE/'사전조사 준비/보드_출력파일').glob('*_A3.pdf'):shutil.copy2(f,boards/f.name)
shutil.copy2(BASE/'사전조사 준비물/00_시간표와_준비물.pdf',OUT/'00_시간표와_준비물.pdf')
(OUT/'00_읽어주세요.md').write_text('''# 현장조사 최종 폴더

2026.09.13 요청사항 반영본입니다.

- [시간표와 준비물 — A4 한 장](00_시간표와_준비물.pdf)
- [수정용 일정 엑셀](사전조사%20준비/02_사전조사%20일정.xlsx)
- [거점별 준비물](사전조사%20준비/03_거점별%20준비물.docx)
- [A4·A3 전체 출력물 목록](사전조사%20준비/04_전체%20출력물%20목록.pdf)
- [A4 출력파일 — 회차별 일괄·개별 PDF](사전조사%20준비/A4_출력파일)
- [사전조사 자료](사전조사%20준비물) · [1차 실험 자료](1차%20실험) · [2차 실험 자료](2차%20실험)
- [사전조사 A3 폼보드 출력파일](사전조사%20준비/보드_출력파일)
- [투명 배경 표정 아이콘 5종](사전조사%20준비물/표정아이콘)

목요일은 주호·은영·지윤·성훈입니다. 선인재단은 4명이며 1번 출발, 2~3번 중간, 4번 도착입니다. 출발코드 칸은 삭제했고 번호 뒤에 옷·가방 특징을 짧게 적습니다.

기록표는 기본 001~200, 25줄×8장입니다. 선인재단은 4개 위치별 8장, 총 32장입니다. 송도 인터뷰만 001~050, 25줄×2장이며 송도 관찰은 200건입니다.

시간 확인은 핸드폰으로 합니다. 폼보드는 A3로 사람이 들고 이동합니다. 굴포천은 A3 세로, 차이나타운은 A3 가로이며 굴포천 카메라 1대·삼각대 1개를 포함합니다. 송도는 이미 구매한 A4 받침대를 사용합니다.

폼보드 PDF는 A3 실제 크기(100%)로 출력합니다. 응답칸이 차면 사진·집계 후 같은 A3 출력지를 덧붙여 계속 사용합니다. 차이나타운은 4문항용 스티커 800개와 여분 200개를 준비합니다.

표정은 빨강·주황·노랑(보통)·초록·파랑 순서입니다. 만족도 등 적합한 문항에만 적용했으며, 관찰 위치 번호와 다른 종류의 원래 보기는 유지합니다.

그림 A·B나 지도·사진을 넣는 자리는 기존 자료 상태를 유지합니다. 빈 프레임은 해당 현장 원본 이미지를 넣어 사용합니다.
''')
print(OUT)
