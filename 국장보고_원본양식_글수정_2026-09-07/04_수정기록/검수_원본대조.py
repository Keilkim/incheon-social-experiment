# -*- coding: utf-8 -*-
from pathlib import Path
import json, re, math, unicodedata, itertools
import fitz
from PIL import Image,ImageDraw,ImageChops
from pptx import Presentation
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT.parent
SOURCES={unicodedata.normalize('NFC',p.name):p for p in WORK.glob('*.pdf')}
def norm(t):return re.sub(r'\s+','',t)
errors=[];checks=[]

def check_pages(pdfpath,pptpath,records):
 doc=fitz.open(pdfpath);ppt=Presentation(pptpath)
 assert len(doc)==len(records)==len(ppt.slides)
 for i,(page,rec) in enumerate(zip(doc,records)):
  text=norm(page.get_text());ptxt=norm(''.join(s.text for s in ppt.slides[i].shapes if s.has_text_frame))
  for t in rec['text']:
   wanted=norm(t['text'])
   if wanted not in text:errors.append([rec['label'],'PDF missing',t['text']])
   if wanted not in ptxt:errors.append([rec['label'],'PPTX missing',t['text']])
  if '\ufffd' in page.get_text():errors.append([rec['label'],'replacement glyph'])
  with fitz.open(SOURCES[rec['source']]) as src:
   op=src[rec['page']-1]
   assert tuple(page.rect)==tuple(op.rect)
   originals=[x for x in op.get_image_info() if x['width'] and x['height']];current=[x for x in page.get_image_info() if x['width'] and x['height']]
   def imdesc(im):return [im['width'],im['height'],*[round(n,3) for n in im['bbox']],*[round(n,3) for n in im['transform']]]
   if [imdesc(x) for x in originals]!=[imdesc(x) for x in current]:errors.append([rec['label'],'image position / size mismatch'])
   a=op.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);b=page.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
   a=Image.frombytes('RGB',(a.width,a.height),a.samples);b=Image.frombytes('RGB',(b.width,b.height),b.samples)
   diff=ImageChops.difference(a,b);mask=Image.new('L',a.size,255);draw=ImageDraw.Draw(mask)
   # Allow a two-point fringe around declared text regions for glyph antialiasing.
   for r in rec['clear']+[t['rect'] for t in rec['text']]:draw.rectangle((math.floor(r[0]-2),math.floor(r[1]-2),math.ceil(r[2]+2),math.ceil(r[3]+2)),fill=0)
   outside=ImageChops.multiply(diff,Image.merge('RGB',(mask,mask,mask)))
   hist=outside.convert('L').histogram();outside_fields=sum(hist[3:])
   # PDF redaction reserializes retained text runs. Separate small glyph-rendering
   # differences inside original text bounds from changes to artwork or layout.
   for bl in op.get_text('dict')['blocks']:
    if bl['type']!=0:continue
    for ln in bl['lines']:
     for sp in ln['spans']:
      rr=sp['bbox'];draw.rectangle((math.floor(rr[0]-2),math.floor(rr[1]-2),math.ceil(rr[2]+2),math.ceil(rr[3]+2)),fill=0)
   outside=ImageChops.multiply(diff,Image.merge('RGB',(mask,mask,mask)))
   hist=outside.convert('L').histogram();changed=sum(hist[3:])
   if changed:errors.append([rec['label'],'nontext pixels changed',changed])
  # Detect overlapping new text lines; images of the original page are excluded.
  lines=[]
  for j,t in enumerate(rec['text']):
   if t.get('role')=='original_restore':continue
   for k,l in enumerate(t['placed']):
    if not l['text'].strip():continue
    fs=t['actual_size'];r=fitz.Rect(l['x'],l['baseline']-fs*.95,l['x']+l['width'],l['baseline']+fs*.15)
    lines.append((j,k,r,l['text']))
  overlaps=[]
  for a,b in itertools.combinations(lines,2):
   if a[0]==b[0]:continue
   inter=a[2]&b[2]
   if not inter.is_empty and inter.width>1.2 and inter.height>1.2 and inter.get_area()>5:overlaps.append([a[3],b[3],list(inter)])
  if overlaps:errors.append([rec['label'],'new text overlap',overlaps])
  checks.append({'page':i+1,'label':rec['label'],'source':rec['source'],'original_page':rec['page'],'original_images':len(originals),'nontext_changed_pixels':changed,'retained_text_rendering_difference_pixels':outside_fields,'new_text_fields':len(rec['text'])})
 doc.close()

def main():
 full=ROOT/'04_수정기록/통합43쪽_변경영역.json'
 if full.exists():
  check_pages(ROOT/'02_통합/00_국장보고_전체43쪽_원본양식.pdf',ROOT/'02_통합/00_국장보고_전체43쪽_원본양식.pptx',json.loads(full.read_text()))
 else:
  r=json.loads((ROOT/'04_수정기록/변경영역.json').read_text())
  check_pages(ROOT/'02_통합/01_7개거점_21쪽_원본양식.pdf',ROOT/'02_통합/01_7개거점_21쪽_원본양식.pptx',r)
  c=json.loads((ROOT/'04_수정기록/공통변경영역.json').read_text())
  check_pages(ROOT/'03_원본문서별/01_공통사업설명_15쪽_원본양식.pdf',ROOT/'03_원본문서별/01_공통사업설명_15쪽_원본양식.pptx',c[:15])
  check_pages(ROOT/'03_원본문서별/02_대상지와향후계획_7쪽_원본양식.pdf',ROOT/'03_원본문서별/02_대상지와향후계획_7쪽_원본양식.pptx',c[15:])
 report={'status':'PASS' if not errors else 'REVIEW','pages':len(checks),'checks':checks,'errors':errors,'scope':['PDF와 PPTX 교체 문구 누락 대조','유효한 원본 이미지 수·위치·크기·변환 일치 검사','교체 영역과 원본 글자 영역을 제외한 비문자 영역의 픽셀 대조','새 글상자 간 겹침 검사'],'limitations':['PPTX는 PDF 원본의 배경과 교체 글상자로 구성됨. 사진·도형은 배경에 포함되며 교체한 글은 편집 가능.','PDF 텍스트 재생성에 따른 일부 글자 렌더링 차이는 원본 글자 영역에서 별도 분리함.','PDF와 PPTX 내부 구조를 확인했으며 PowerPoint 앱 렌더링 검사는 별도 수행하지 않음.','원본에 미제작된 이미지 영역은 위치를 유지한 채 최신 시안 설명으로 바꾸었음.']}
 (ROOT/'04_수정기록/검수결과.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'status':report['status'],'pages':len(checks),'errors':errors},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
