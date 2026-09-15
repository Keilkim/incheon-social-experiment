# -*- coding: utf-8 -*-
from pathlib import Path
import json, unicodedata, re, io, math, hashlib
import fitz
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
from lxml import etree
from 거점내용 import SITES

ROOT=Path(__file__).resolve().parents[1]; WORK=ROOT.parent
FONTDIR=Path('/Users/chokogamja/Library/Fonts')
FONTS={n:FONTDIR/f'Paperlogy-{v}.ttf' for n,v in [('R','4Regular'),('B','7Bold'),('M','5Medium'),('L','3Light'),('T','1Thin'),('K','9Black')]}
FF={n:fitz.Font(fontfile=str(p)) for n,p in FONTS.items()}
FACES={'R':'페이퍼로지 4 Regular','B':'페이퍼로지 7 Bold','M':'페이퍼로지 5 Medium','L':'페이퍼로지 3 Light','T':'페이퍼로지 1 Thin','K':'페이퍼로지 9 Black'}
SOURCE={unicodedata.normalize('NFC',p.name):p for p in WORK.glob('*.pdf')}
GRAY='444A51'; NAVY='231F20'; WHITE='FFFFFF'
def color(v):
 if isinstance(v,int):v=f'{v:06X}'
 return tuple(int(v[i:i+2],16)/255 for i in (0,2,4))
def norm(t):return re.sub(r'\s+','',t)
def lines_of(page):
 return [l for b in page.get_text('dict')['blocks'] if b['type']==0 for l in b['lines']]
def ltext(l):return ''.join(s['text'] for s in l['spans'])
def wrap(t,font,size,width):
 result=[]
 for para in t.split('\n'):
  if not para:result.append('');continue
  line=''
  for tok in re.findall(r'\S+\s*',para):
   if line and FF[font].text_length((line+tok).rstrip(),fontsize=size)>width:result.append(line.rstrip());line=''
   if FF[font].text_length(tok.rstrip(),fontsize=size)>width:
    for c in tok:
     if line and FF[font].text_length(line+c,fontsize=size)>width:result.append(line.rstrip());line=''
     line+=c
   else:line+=tok
  result.append(line.rstrip())
 return result

class Editor:
 def __init__(self,src,pn,label):
  self.source=src;self.pn=pn;self.label=label
  self.doc=fitz.open();original=fitz.open(SOURCE[src]);self.doc.insert_pdf(original,from_page=pn-1,to_page=pn-1);original.close()
  self.page=self.doc[0];self.original_lines=lines_of(self.page)
  self.off=(self.page.rect.width-841.8900146484375)/2
  self.clear=[];self.text=[];self.covers=[];self.background=None
 def r(self,rect):return fitz.Rect(*(v+self.off for v in rect))
 def wipe(self,rect,absolute=False):
  r=fitz.Rect(rect) if absolute else self.r(rect);self.clear.append(list(r));self.page.add_redact_annot(r,fill=False,cross_out=False)
 def put(self,rect,text,size=10,font='R',ink=GRAY,align='left',absolute=False,minsize=None):
  r=fitz.Rect(rect) if absolute else self.r(rect)
  self.text.append({'rect':list(r),'text':text,'size':size,'font':font,'color':ink,'align':align,'minsize':minsize or size*.78})
 def field(self,rect,text,**kw):self.wipe(rect);self.put(rect,text,**kw)
 def cover(self,rect,fill,absolute=True):
  r=fitz.Rect(rect) if absolute else self.r(rect);self.clear.append(list(r));self.covers.append((r,fill))
 def restore(self,text,origin,size,font,ink):
  f=FF[font];top=origin[1]-f.ascender*size;w=f.text_length(text,fontsize=size)
  self.put((origin[0],top,origin[0]+w+.1,origin[1]-f.descender*size+.1),text,size=size,font=font,ink=ink,absolute=True,minsize=size)
  self.text[-1]['role']='original_restore'
 def finish(self):
  if any('인천 창의디자인 사회실험 사업' in ltext(l) for l in self.original_lines):
   self.wipe((805,557,829,578))
   self.put((806.6,560.5,819,574),str(self.pn),size=8.4,font='M',ink='818587',align='center')
   self.text[-1]['role']='page_number'
  self.page.apply_redactions(images=0,graphics=0,text=0)
  for rect,fill in self.covers:self.page.draw_rect(rect,color=None,fill=color(fill),overlay=True)
  self.background=self.page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).tobytes('png')
  for key,p in FONTS.items():self.page.insert_font(fontname='New'+key,fontfile=str(p))
  for t in self.text:
   r=fitz.Rect(t['rect']);fs=t['size'];font=t['font'];f=FF[font]
   while True:
    lines=wrap(t['text'],font,fs,r.width)
    lh=fs*1.28
    height=(len(lines)-1)*lh+(f.ascender-f.descender)*fs
    if height<=r.height+.01:break
    fs-=.1
    if fs<t['minsize']-.05:raise ValueError(('text does not fit',self.label,t['text'],r,fs,height))
   y=r.y0+f.ascender*fs;placed=[]
   for line in lines:
    width=f.text_length(line,fontsize=fs);x=r.x0
    if t['align']=='center':x+=(r.width-width)/2
    if t['align']=='right':x+=r.width-width
    if line:self.page.insert_text((x,y),line,fontname='New'+font,fontsize=fs,color=color(t['color']))
    placed.append({'text':line,'x':x,'baseline':y,'width':width});y+=lh
   t.update({'actual_size':round(fs,3),'placed':placed})
  self.page.clean_contents()
  return self

def overview(site):
 e=Editor(site['src'],site['pages'][0],site['key']+' 개요');c=site['color'];o=e.off
 # The main headline starts exactly at the original first headline position.
 ls=[l for l in e.original_lines if l['bbox'][0]>150+o and 65+o<l['bbox'][1]<140+o and any(s['size']>16 for s in l['spans'])]
 if not ls:raise ValueError(('headline',site['key']))
 x=min(l['bbox'][0] for l in ls)-o;y=min(l['bbox'][1] for l in ls)-o
 e.wipe((155,67,829,143));e.put((x,y,820,143),site['title'],size=18,font='B',ink=c,minsize=12)
 # Sidebar numbers are made consistent across all seven sites.
 e.field((58,191,70,212),str(site['num']),size=13.3,font='B',ink=WHITE,align='center')
 e.field((29.9,191,56.5,212),site['category'],size=13.3,font='B',ink=('31509E' if site['num'] in [1,4] else c))
 if site['key']=='송도캠퍼스타운역':e.field((29,210,149,237),'캠퍼스타운역',size=18,font='B',ink=c)
 for i,p in enumerate(site['phases']):
  dy=0 if i==0 else (202.56 if site['key']=='선인재단' else 212.13)
  # Preserve the two original horizontal dividers and their three-column arrangement.
  def shift(r):return (r[0]+(1.25 if i else 0),r[1]+dy,r[2],r[3]+dy)
  e.field(shift((187,142,400,160)),f'{site["category"]}-{site["num"]}  {i+1}차 「{p["name"]}」',size=11,font='B',ink=c,minsize=8)
  e.field(shift((187,172,391,186)),'문제 인식 / 측정 항목',size=8,font='B',ink=c)
  e.wipe(shift((187,192,399,264)))
  e.put(shift((188,193,390,206)),'핵심 지표 :',size=8,font='M')
  e.put(shift((188,202,396,232)),p['metric'],size=24,font='B',ink=c)
  e.put(shift((188,234,395,263)),p['metric_desc'],size=10.5,font='B',ink=c)
  e.wipe(shift((187,268,400,333)))
  e.put(shift((188,270,395,282)),'집중 데이터 :',size=8,font='M')
  e.put(shift((188,282,395,330)),p['focus'],size=10.5,font='B',ink=c)
  e.wipe(shift((629,192,829,263)))
  e.put(shift((635.8,194.4,813,262)),p['place'],size=10.5,font='M')
  # The lower right design-description blocks have different original vertical positions.
  design_y=(302.9 if i==0 else (478.6 if site['key']=='선인재단' else 488.1))
  e.wipe((629,design_y-1,830,(370 if i==0 else 550)))
  e.put((635.8,design_y,814,design_y+18),'「'+p['name']+'」',size=11.5,font='B',ink=NAVY,minsize=8)
  e.put((635.8,design_y+19,816,(369 if i==0 else 550)),p['design'],size=9.5,font='M',ink=GRAY,minsize=8)
  # Replace individual colored/thin segments on the old hypothesis lines;
  # retain every original colored highlight rectangle and its position.
  lo=188+dy+o;hi=(346 if i==0 else 566)+o
  hs=sorted([l for l in e.original_lines if 403+o<l['bbox'][0]<625+o and lo<l['bbox'][1]<hi and max(s['size'] for s in l['spans'])>12],key=lambda l:l['bbox'][1])
  assert len(hs)==len(p['hyp']),(site['key'],i,len(hs),len(p['hyp']))
  for line,repls in zip(hs,p['hyp']):
   spans=line['spans']
   if len(spans)!=len(repls):
    spans=[s for s in spans if s['text'].strip()];repls=[t for t in repls if t.strip()]
   assert len(spans)==len(repls),(site['key'],i,ltext(line),len(spans),repls)
   e.wipe((line['bbox'][0]-.6,line['bbox'][1]-.5,629+o,line['bbox'][3]+.5),absolute=True)
   for j,(s,txt) in enumerate(zip(spans,repls)):
    if not txt.strip():continue
    light=s['color'] in [0xffffff,0xf6f6f6]
    # Blank separators remain blank; subsequent spans retain their original x position.
    right=(spans[j+1]['bbox'][0]-.25) if j<len(spans)-1 else min(629+o,max(s['bbox'][2],s['bbox'][0]+FF['M' if light else 'T'].text_length(txt,fontsize=15)))
    if light:right=min(right,s['bbox'][2]+.1)
    left=s['bbox'][0];top=s['bbox'][1];bottom=s['bbox'][3]+.5
    maxfs=min(15,(right-left)/max(FF['M' if light else 'T'].text_length(txt,fontsize=1),.1))
    e.put((left,top,right,bottom),txt,size=maxfs,font='M' if light else 'T',ink=WHITE if light else NAVY,absolute=True,minsize=maxfs*.8)
 return e.finish()

def detail(site,i):
 p=site['phases'][i];e=Editor(site['src'],site['pages'][i+1],site['key']+f' {i+1}차');c=site['color'];o=e.off
 title_y=62.65 if site['key']=='선인재단' and i==1 else 72.65
 lead_y=88.5 if site['key']=='선인재단' and i==1 else 98.5
 e.field((160,title_y-1,822,title_y+22),f'{i+1}차 실험 「{p["name"]}」',size=15.3,font='B',ink=c)
 e.field((160,lead_y-1,825,124),p['lead'],size=12.5,font='L',ink=c,minsize=10)
 e.field((533,124,815,138),'조 사 설 계 · 현 장 질 문',size=8,font='B',ink='80848A')
 e.field((541,144,806,216),p['question'],size=9.3,font='M',ink=GRAY,minsize=8)
 # Three original numbered boxes; leave their circle numbers and outlines intact.
 for j,(head,desc) in enumerate(p['tests']):
  y=[259.5,300.5,343.3][j]
  e.wipe((564,y-1,809,y+29))
  e.put((565.5,y,806,y+14.2),head,size=9.7,font='B',ink=NAVY,minsize=8.2)
  e.put((565.5,y+14,806,y+28.8),desc,size=8.8,font='M',ink=c,minsize=7.7)
 e.field((542,416,808,440),p['keyword'],size=14.3,font='B',ink=WHITE,minsize=11)
 e.field((542,439.5,808,458),p['tags'],size=9.5,font='M',ink=WHITE,minsize=8)
 for j,(label,body) in enumerate(p['gov']):
  y=[496.4,514.9,534.5][j]
  e.wipe((540,y-1,810,y+15))
  e.put((542.3,y,603.7,y+14.2),label,size=8.4,font='B',ink=c,minsize=7)
  e.put((610,y,806,y+14.2),body,size=8.0,font='M',ink=GRAY,minsize=7)
 # Update text-only placeholders in their existing image panels; do not invent images.
 if 'placeholders' in p:
  for rect,t in zip([(162,126,507,382),(162,392,329,552),(339,392,507,552)],p['placeholders']):
   e.wipe(rect)
   mid=(rect[1]+rect[3])/2
   e.put((rect[0]+8,mid-22,rect[2]-8,mid+35),t,size=12.5,font='M',ink=GRAY,align='center',minsize=10)
 # Keep local site identifiers where the original template contains them.
 if any(l['bbox'][0]<120+o and 190+o<l['bbox'][1]<215+o for l in e.original_lines):
  e.field((58,191,70,212),str(site['num']),size=13.3,font='B',ink=WHITE,align='center')
  e.field((29.9,191,56.5,212),site['category'],size=13.3,font='B',ink=('31509E' if site['num'] in [1,4] else c))
  if site['key']=='송도캠퍼스타운역':e.field((29,210,149,237),'캠퍼스타운역',size=18,font='B',ink=c)
 # Existing Gulpo site diagram has an unconfirmed seat count: update those captions only.
 if site['key']=='굴포천' and i==0:
  ls=[l for l in e.original_lines if any(s in ltext(l) for s in ['벤치 양쪽','한쪽(2개','도시재생 홍보관 기준'])]
  repl=['후보 위치 · 현장 협의','좌석 수·배치 실측 후 확정','한쪽 전시·반대편 감상 관찰']
  for l,t in zip(sorted(ls,key=lambda l:l['bbox'][1]),repl):
   b=fitz.Rect(l['bbox']);e.wipe(b+(-.3,-.1,.3,.1),absolute=True);e.put((b.x0,b.y0,min(523+o,b.x0+90),b.y1+.2),t,size=min(s['size'] for s in l['spans']),font='M',absolute=True,minsize=2.5)
 return e.finish()

def write_pptx(edits,path):
 prs=Presentation();prs.slide_width=Pt(853.228);prs.slide_height=Pt(606.614)
 for e in edits:
  sl=prs.slides.add_slide(prs.slide_layouts[6]);dx=(853.228-e.page.rect.width)/2;dy=(606.614-e.page.rect.height)/2
  sl.shapes.add_picture(io.BytesIO(e.background),Pt(dx),Pt(dy),width=Pt(e.page.rect.width),height=Pt(e.page.rect.height))
  for t in e.text:
   font=FF[t['font']];fs=t['actual_size']
   for line in t['placed']:
    if not line['text']:continue
    top=line['baseline']-font.ascender*fs
    sh=sl.shapes.add_textbox(Pt(line['x']+dx),Pt(top+dy),Pt(max(line['width']+2,4)),Pt((font.ascender-font.descender)*fs+3))
    if t.get('role'):sh.name=t['role']
    tf=sh.text_frame;tf.clear();tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0;tf.word_wrap=False;tf.vertical_anchor=MSO_ANCHOR.TOP
    para=tf.paragraphs[0];para.space_before=para.space_after=Pt(0);para.line_spacing=1
    run=para.add_run();run.text=line['text'];run.font.name=FACES[t['font']];run.font.size=Pt(fs);run.font.color.rgb=RGBColor.from_string(t['color']);run.font.bold=t['font']=='B'
    rp=run._r.get_or_add_rPr()
    for tag in ['ea','cs']:
     f=etree.SubElement(rp,'{http://schemas.openxmlformats.org/drawingml/2006/main}'+tag);f.set('typeface',FACES[t['font']])
  sl.notes_slide.notes_text_frame.text=f'原本: {e.source} {e.pn}쪽\n원본의 비문자 요소와 위치를 유지하고 표시한 텍스트만 교체했습니다.\n\n'+ '\n\n'.join(t['text'] for t in e.text)
 prs.save(path)

def save_pdf(edits,path):
 doc=fitz.open()
 for e in edits:doc.insert_pdf(e.doc)
 doc.set_metadata({'title':path.stem,'subject':'2026.09.07 회의 반영 · 원본 양식의 글 수정','author':'위즈플러스'})
 doc.subset_fonts();doc.save(path,garbage=4,deflate=True);doc.close()

def main():
 edits=[];manifest=[]
 for i,s in enumerate(SITES,1):
  print('WORK',s['key'],flush=True)
  es=[overview(s),detail(s,0),detail(s,1)]
  base=ROOT/'01_거점별'/f'{i:02}_{s["key"]}_원본양식_글수정'
  save_pdf(es,base.with_suffix('.pdf'));write_pptx(es,base.with_suffix('.pptx'))
  for j,e in enumerate(es):
   e.page.get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(ROOT/'04_수정기록'/f'{i:02}_{j+1:02}_검토.png')
  edits.extend(es)
  manifest.append({'site':s['key'],'source':s['src'],'pages':s['pages'],'output':str(base.relative_to(ROOT))})
 save_pdf(edits,ROOT/'02_통합/01_7개거점_21쪽_원본양식.pdf')
 write_pptx(edits,ROOT/'02_통합/01_7개거점_21쪽_원본양식.pptx')
 (ROOT/'04_수정기록/변경영역.json').write_text(json.dumps([{'source':e.source,'page':e.pn,'label':e.label,'clear':e.clear,'text':e.text} for e in edits],ensure_ascii=False,indent=2))
 (ROOT/'04_수정기록/문서대응.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 return edits
if __name__=='__main__':main()
