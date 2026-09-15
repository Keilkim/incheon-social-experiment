# -*- coding: utf-8 -*-
from pathlib import Path
import re, json, zipfile, importlib.util, hashlib
from lxml import etree as E
import fitz
from pptx import Presentation
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('docs',ROOT/'05_제작기록/문서제작.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def norm(s):return re.sub(r'\s+','',s)
def without_urls(s):return re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1',s).replace('**','')
checks=[];errors=[]
for p in sorted((ROOT/'04_편집원고').glob('*.md')):
 if p.name.startswith('00_'):continue
 md=p.read_text();b=m.output_for(p)
 expected=[]
 for k,v in m.blocks(md):
  if k=='table':expected.extend(cell for row in v for cell in row)
  else:expected.append(v)
 for suffix in ['.pdf','.docx','.hwpx']:
  q=b.with_suffix(suffix)
  if suffix=='.pdf':
   d=fitz.open(q);text=''.join(pg.get_text(clip=fitz.Rect(0,45,pg.rect.width,795)) for pg in d)
   for n,pg in enumerate(d):
    for bl in pg.get_text('blocks'):
     if bl[0]<-1 or bl[1]<-1 or bl[2]>pg.rect.width+1 or bl[3]>pg.rect.height+1:errors.append((str(q),'pagebounds',n+1,bl[:4]))
   d.close()
  else:
   with zipfile.ZipFile(q) as z:
    assert z.testzip() is None
    for n in z.namelist():
     if n.endswith(('.xml','.hpf','.rdf')):E.fromstring(z.read(n))
    if suffix=='.docx':
     r=E.fromstring(z.read('word/document.xml'));text=''.join(r.xpath('//w:t/text()',namespaces={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}))
    else:
     r=E.fromstring(z.read('Contents/section0.xml'));text=''.join(r.xpath('//hp:t/text()',namespaces={'hp':'http://www.hancom.co.kr/hwpml/2011/paragraph'}))
  for para in expected:
   # HWPX table headers are repeated as labels; body content is otherwise equivalent.
   wanted=m.plain(para) if suffix=='.hwpx' else without_urls(para)
   if norm(wanted) not in norm(text):errors.append((p.name,suffix,'missing',wanted[:100]))
  if '\ufffd' in text:errors.append((p.name,suffix,'replacement character'))
  checks.append({'file':str(q.relative_to(ROOT)),'type':suffix,'status':'checked'})
report=json.loads((ROOT/'05_제작기록/국장보고_구성데이터.json').read_text())
slides=report['slides'];ppt=Presentation(ROOT/'02_국장보고/00_국장보고_40쪽.pptx');pdf=fitz.open(ROOT/'02_국장보고/00_국장보고_40쪽.pdf')
assert len(ppt.slides)==len(pdf)==40
for i,s in enumerate(slides):
 ppttext=''.join(sh.text for sh in ppt.slides[i].shapes if sh.has_text_frame)
 pdftxt=pdf[i].get_text()
 req=[s['title']]+[x for block in s['blocks'] for x in block]
 if i: req.append(s['lead'])
 for v in req:
  for typ,txt in [('pptx',ppttext),('pdf',pdftxt)]:
   if norm(v) not in norm(txt):errors.append(('report',i+1,typ,v[:80]))
 if norm(s['notes']) not in norm(ppt.slides[i].notes_slide.notes_text_frame.text):errors.append(('report',i+1,'notes missing'))
 for bl in pdf[i].get_text('blocks'):
  if bl[0]<-1 or bl[1]<-1 or bl[2]>961 or bl[3]>541:errors.append(('report',i+1,'bounds',bl[:4]))
for p in (ROOT/'02_국장보고/거점별').glob('*_3쪽.pdf'):assert len(fitz.open(p))==3
for p in (ROOT/'02_국장보고/거점별').glob('*_3쪽.pptx'):assert len(Presentation(p).slides)==3
wb=load_workbook(ROOT/'03_분석과조사설계/22_현장조사_빈기록부.xlsx');assert len(wb.sheetnames)==18
for w in list(wb)[1:]:assert all(c.value is None for row in w.iter_rows(min_row=2) for c in row)
result={'status':'PASS' if not errors else 'REVIEW','document_files_checked':len(checks),'report_pages':40,'individual_report_sets':7,'workbook_sheets':len(wb.sheetnames),'errors':errors,'scope':['HWPX·DOCX ZIP/전체 XML 구조 및 본문 대조','PDF 전체 문단 누락·문자 깨짐·페이지 경계 검사','PPTX 40쪽 전체 본문·발표자 노트 대조','거점별 보고 각 3쪽 확인','엑셀 18개 시트 및 실측 데이터 없는 빈 양식 확인'],'limitations':['HWPX·DOCX는 구조와 본문을 대조했으며 한글·워드 앱에서 실제 열기·재저장 검사는 수행하지 않음.','PPTX는 구조와 본문을 대조하고 같은 배치로 만든 PDF를 시각 검수함. PowerPoint 앱 자체 렌더링은 별도 확인하지 않음.']}
(ROOT/'05_제작기록/검수결과.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
