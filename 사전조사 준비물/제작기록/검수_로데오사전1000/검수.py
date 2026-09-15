"""2026.09.13 로데오 사전 1000명·실험 500명 및 최신본 반영 대조 기록."""
from pathlib import Path
from urllib.parse import unquote
import json, re
from pypdf import PdfReader
from openpyxl import load_workbook
from docx import Document
from PIL import Image

B = Path(__file__).resolve().parents[3]
F = B / '최종_현장조사'
P = B / '사전조사 준비'
BACK = B / '사전조사 준비물/제작기록/이전본_로데오1000_최신반영_수정전'
PHASES = ['사전조사 준비물', '1차 실험', '2차 실험']
COUNTS = [99, 87, 80]
checks = []

def check(label, condition):
    assert condition, label
    checks.append(label)

def contents(page):
    return page.get_contents().get_data()

for folder, n in zip(PHASES, COUNTS):
    capacity = 1000 if folder == PHASES[0] else 500
    src = B / folder
    pdf = PdfReader(src / '06_로데오거리.pdf')
    check(folder + f' 로데오 {capacity//25}장', len(pdf.pages) == capacity//25)
    for i, page in enumerate(pdf.pages):
        numbers = list(map(int, re.findall(r'(?m)^(\d{3,4})\s', page.extract_text())))
        check(f'{folder} 로데오 {i+1}쪽 번호', numbers == list(range(i*25+1, i*25+26)))
    wb = load_workbook(src / '08_입력용_기록부.xlsx')
    before = load_workbook(BACK / folder / '08_입력용_기록부.xlsx')
    sheet = wb['로데오_사람']
    check(folder + f' 엑셀 {capacity}행', sheet.max_row == capacity+1 and [sheet.cell(i,2).value for i in range(2,capacity+2)] == list(range(1,capacity+1)))
    check(folder + ' 송도 50행·선인 800행', wb['송도_인터뷰'].max_row == 51 and wb['선인재단_기록'].max_row == 801)
    for name in before.sheetnames:
        if name != '사용법':
            check(folder + ' 기존 입력 보존 ' + name, all(c.value == wb[name].cell(c.row,c.column).value for row in before[name] for c in row))
    dest = P / 'A4_출력파일' / folder
    bundles = list(dest.glob('00_현장기록지_일괄_*장_단면1부.pdf'))
    check(folder + ' 최신 일괄 1개', len(bundles) == 1 and bundles[0].name == f'00_현장기록지_일괄_{n}장_단면1부.pdf')
    bundle = PdfReader(bundles[0])
    names = (['07_약산초_워크숍기록.pdf'] if folder == '1차 실험' else []) + ['08_선인재단_기록지.pdf','09_송도_관찰기록지.pdf','10_송도_인터뷰기록표.pdf','12_굴포천_기록지.pdf','13_로데오거리_기록지.pdf','14_터미널_2층기록지.pdf','15_터미널_캐리어시간표.pdf'] + (['16_차이나타운_웹집계.pdf'] if folder == '2차 실험' else [])
    pages = [p for name in names for p in PdfReader(dest / name).pages]
    check(folder + ' 일괄·개별 모든 페이지 일치', len(bundle.pages) == len(pages) == n and all(contents(a) == contents(b) for a,b in zip(pages,bundle.pages)))
    for original, target, indices in [('06_로데오거리.pdf','13_로데오거리_기록지.pdf',range(capacity//25)),('07_연안여객터미널.pdf','14_터미널_2층기록지.pdf',range(8)),('03_송도.pdf','10_송도_인터뷰기록표.pdf',range(8,10))]:
        a, b = PdfReader(src / original), PdfReader(dest / target)
        check(folder + ' 원본·분리 PDF 일치 ' + target, len(b.pages) == len(indices) and all(contents(a.pages[i]) == contents(p) for i,p in zip(indices,b.pages)))

for a,b in [('05_굴포천_폼보드.pdf','B1_굴포천_스티커판_사전_A3.pdf'),('04_차이나타운_폼보드.pdf','B4_차이나타운_스티커보드_A3.pdf')]:
    check('사전 보드 최신 원본 일치 ' + a, (B / '사전조사 준비물' / a).read_bytes() == (P / '보드_출력파일' / b).read_bytes())
for f in (B / '사전조사 준비물/표정아이콘').glob('0*.png'):
    im = Image.open(f)
    check('스마일 투명 배경 ' + f.name, im.mode == 'RGBA' and im.getextrema()[3][0] == 0)

file_count = 0
for folder in PHASES + ['사전조사 준비']:
    for src in (B / folder).rglob('*'):
        rel = src.relative_to(B)
        if not src.is_file() or any('제작기록' in z or z.startswith(('~$','.')) for z in rel.parts):
            continue
        if src.name == '05_분석 방법 미리보기_가상데이터.docx':
            continue
        dst = F / rel
        if src.name == '00_먼저읽어주세요.md':
            expected = re.sub(r'재생성:.*?이번 수정 전 파일.*?\n', '', src.read_text(), flags=re.S)
            same = dst.exists() and dst.read_text() == expected
        else:
            same = dst.exists() and src.read_bytes() == dst.read_bytes()
        check('최종 파일 일치 ' + str(rel), same)
        file_count += 1

for root in [B,F]:
    for folder in PHASES + ['사전조사 준비']:
        for f in (root / folder).rglob('*.md'):
            if any('제작기록' in p for p in f.relative_to(root).parts):
                continue
            for target in re.findall(r'\]\(([^)]+)\)', f.read_text()):
                if not target.startswith(('http','mailto:','#')):
                    check('안내 링크 존재 ' + str(f.relative_to(root)) + ' ' + target, (f.parent / unquote(target)).exists())
    doc = Document(root / '사전조사 준비/01_조사 방법 및 내용_보완본.docx')
    text = '\n'.join([p.text for p in doc.paragraphs] + [c.text for table in doc.tables for row in table.rows for c in row.cells])
    check('보완본 최신 수량·표정·위치 ' + str(root.name), all(x in text for x in ['1000명','500명','50명','5색 표정','4 도착']) and '1~5가 인쇄된' not in text and '선인재단 (5명)' not in text)
    for folder in PHASES:
        check('이전 인쇄안내 없음 ' + str(root / folder), not (root / folder / '00_표정과_200건_인쇄안내.pdf').exists())

result = {'result':'PASS','check_count':len(checks),'source_final_file_count':file_count,'phase_bundle_pages':dict(zip(PHASES,COUNTS)),'rodeo_capacity':{'사전':1000,'1차':500,'2차':500},'visual_review':'로데오_사전_976_1000.png','checks':checks}
Path(__file__).with_name('검수결과.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(f'PASS: {len(checks)} checks; {file_count} source/final files checked')
