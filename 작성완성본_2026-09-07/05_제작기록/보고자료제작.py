from pathlib import Path
import json, math, re
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.xmlchemy import OxmlElement
from pptx.enum.text import MSO_ANCHOR
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'05_제작기록'/'국장보고_구성데이터.json').read_text());S=data['sources'];SL=data['slides']
fontdir=Path('/Users/chokogamja/Library/Fonts')
for alias,name in [('Paper','Paperlogy-4Regular.ttf'),('PaperBold','Paperlogy-7Bold.ttf')]:pdfmetrics.registerFont(TTFont(alias,str(fontdir/name)))
W,H=960,540
NAVY='153C68';TEAL='009DAF';GRAY='536274';BG='F5F8FC';INK='233144'
all_layouts=[]
def wrap(s,w,size,bold=False):
 font='PaperBold' if bold else 'Paper';lines=[]
 for par in s.split('\n'):
  cur=''
  for ch in par:
   if cur and pdfmetrics.stringWidth(cur+ch,font,size)>w:
    # Use a recent word boundary when it does not leave most of the line empty.
    cut=cur.rfind(' ')
    if cut>0 and pdfmetrics.stringWidth(cur[:cut],font,size)>w*0.64:
     lines.append(cur[:cut]);cur=cur[cut+1:]+ch
    else:lines.append(cur);cur=ch
   else:cur+=ch
  lines.append(cur)
 return lines

def layout(s,idx):
 items=[]
 def rect(x,y,w,h,fill,radius=0):items.append(dict(type='rect',x=x,y=y,w=w,h=h,fill=fill,radius=radius))
 def txt(x,y,w,text,size=15,color=INK,bold=False,leading=None,maxh=None,link=None):
  leading=leading or size*1.45
  lines=wrap(text,w,size,bold)
  if maxh:
   while len(lines)*leading>maxh and size>10.5:
    size-=0.5;leading=size*1.4;lines=wrap(text,w,size,bold)
   if len(lines)*leading>maxh:raise ValueError(('overflow',idx,text,len(lines)*leading,maxh))
  items.append(dict(type='text',x=x,y=y,w=w,h=len(lines)*leading,lines=lines,size=size,color=color,bold=bold,leading=leading,link=link))
 rect(0,0,W,H,'FFFFFF');rect(0,0,12,H,TEAL)
 txt(42,23,840,'ACT Incheon  /  '+s['section'],9,GRAY,bold=True,leading=12)
 if idx==1:
  rect(590,62,330,267,'E5F4F5',18);rect(630,90,228,155,TEAL,12)
  txt(652,124,190,'ACT',56,'FFFFFF',True,leading=62)
  txt(650,207,220,'함께 만드는 도시의 변화',13,NAVY,True)
  txt(42,82,570,'인천 창의디자인\n사회실험 사업',36,NAVY,True,leading=50)
  txt(44,211,505,'시민이 사용하고,\n결과로 보완하는 도시디자인',21,GRAY,leading=32)
  txt(44,306,520,'국장보고  |  2026.09.07 회의 반영 작성안',12,NAVY,True)
  for j,(h,t) in enumerate(s['blocks']):
   x=42+j*299;rect(x,371,280,100,BG,8);txt(x+16,386,248,h,11,TEAL,True);txt(x+16,412,248,t,12,INK,maxh=48)
 else:
  txt(42,61,875,s['title'],25,NAVY,True,leading=33,maxh=67)
  txt(44,133,870,s['lead'],16.5,GRAY,leading=24,maxh=50)
  n=len(s['blocks'])
  if n==3:
   for j,(h,t) in enumerate(s['blocks']):
    x=42+j*299;rect(x,202,280,251,BG,9);txt(x+18,218,240,f'{j+1:02d}',10,TEAL,True,leading=13)
    nh=len(wrap(h,244,16.5,True));txt(x+18,246,244,h,16.5,NAVY,True,leading=22,maxh=48)
    bodyy=246+nh*22+14;txt(x+18,bodyy,244,t,14.5,INK,leading=21.5,maxh=438-bodyy)
  else:
   for j,(h,t) in enumerate(s['blocks']):
    x=42+(j%2)*449;y=191+(j//2)*143;rect(x,y,430,132,BG,8);txt(x+17,y+14,396,h,14,NAVY,True,leading=18,maxh=38)
    nh=len(wrap(h,396,14,True));bodyy=y+14+nh*18+8;txt(x+17,bodyy,396,t,12.5,INK,leading=18,maxh=y+120-bodyy)
  if s['refs']:
   yy=472 if n==3 else 482
   for ref in s['refs']:
    title,url=S[ref];txt(44,yy,870,'출처  '+ref+'  '+title,8,GRAY,leading=11,link=url);yy+=12
  else:txt(44,479 if n==3 else 486,868,'작성 근거: 제공자료·2026.09.07 내부회의·조사표  |  상세 근거와 측정 규칙은 별첨 참조',8,GRAY,leading=11)
 rect(42,506,876,0.8,'D9E3EB');txt(44,516,780,'인천 창의디자인 사회실험  ·  위즈플러스  ·  검증 계획',7.5,GRAY,leading=10);txt(877,514,45,f'{idx:02d}',10,TEAL,True,leading=12)
 for e in items:
  if e['type']=='text':
   assert e['y']+e['h']<=H+1,(idx,e)
 all_layouts.append({'page':idx,'items':items})
 return items

def render_pdf(ss,path,indices):
 c=canvas.Canvas(str(path),pagesize=(W,H));c.setTitle('인천 창의디자인 사회실험 | 국장보고');c.setAuthor('위즈플러스')
 for s,idx in zip(ss,indices):
  items=layout(s,idx)
  for e in items:
   if e['type']=='rect':
    c.setFillColor(colors.HexColor('#'+e['fill']));c.setStrokeColor(colors.HexColor('#'+e['fill']));c.roundRect(e['x'],H-e['y']-e['h'],e['w'],e['h'],e['radius'],fill=1,stroke=0)
   else:
    c.setFillColor(colors.HexColor('#'+e['color']));c.setFont('PaperBold' if e['bold'] else 'Paper',e['size'])
    for j,line in enumerate(e['lines']):c.drawString(e['x'],H-e['y']-e['size']-j*e['leading'],line)
    if e['link']:c.linkURL(e['link'],(e['x'],H-e['y']-e['h'],e['x']+e['w'],H-e['y']),relative=0)
  c.showPage()
 c.save()

def render_pptx(ss,path,indices):
 prs=Presentation();prs.slide_width=Pt(W);prs.slide_height=Pt(H)
 for s,idx in zip(ss,indices):
  slide=prs.slides.add_slide(prs.slide_layouts[6]);items=layout(s,idx)
  for e in items:
   if e['type']=='rect':
    sh=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if e['radius'] else MSO_SHAPE.RECTANGLE,Pt(e['x']),Pt(e['y']),Pt(e['w']),Pt(e['h']));sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string(e['fill']);sh.line.fill.background()
    if e['radius']:sh.adjustments[0]=0.08
   else:
    sh=slide.shapes.add_textbox(Pt(e['x']),Pt(e['y']-1),Pt(e['w']+2),Pt(e['h']+4));tf=sh.text_frame;tf.clear();tf.word_wrap=False;tf.margin_left=0;tf.margin_right=0;tf.margin_top=0;tf.margin_bottom=0;tf.vertical_anchor=MSO_ANCHOR.TOP
    for j,line in enumerate(e['lines']):
     p=tf.paragraphs[0] if j==0 else tf.add_paragraph();p.space_before=Pt(0);p.space_after=Pt(0);p.line_spacing=Pt(e['leading'])
     run=p.add_run();run.text=line;run.font.name='페이퍼로지 7 Bold' if e['bold'] else '페이퍼로지 4 Regular';run.font.size=Pt(e['size']);run.font.bold=e['bold'];run.font.color.rgb=RGBColor.from_string(e['color'])
     rp=run._r.get_or_add_rPr();ea=OxmlElement('a:ea');ea.set('typeface',run.font.name);rp.append(ea)
     if e['link']:run.hyperlink.address=e['link']
  refs='\n'.join(k+' '+S[k][0]+'\n'+S[k][1] for k in s['refs'])
  slide.notes_slide.notes_text_frame.text=s['notes']+('\n\n출처\n'+refs if refs else '\n\n근거: 제공된 기존 문서·2026.09.07 내부회의·조사 방법표')
 prs.core_properties.title='인천 창의디자인 사회실험 국장보고';prs.core_properties.author='위즈플러스';prs.save(path)

out=ROOT/'02_국장보고';indices=list(range(1,len(SL)+1))
render_pdf(SL,out/'00_국장보고_40쪽.pdf',indices);render_pptx(SL,out/'00_국장보고_40쪽.pptx',indices)
for site in dict.fromkeys(s['site'] for s in SL if s['site']):
 ss=[s for s in SL if s['site']==site];ids=[SL.index(s)+1 for s in ss];base=out/'거점별'/f'{site}_국장보고_3쪽'
 render_pdf(ss,base.with_suffix('.pdf'),ids);render_pptx(ss,base.with_suffix('.pptx'),ids)
(ROOT/'05_제작기록'/'보고자료_레이아웃.json').write_text(json.dumps(all_layouts[:40],ensure_ascii=False,indent=2))
print('40-page report and 7 individual 3-page reports generated.')
