from pathlib import Path
from html import escape
import json
import math
import os

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
import fitz

BASE=Path(__file__).resolve().parent
OUT=Path(os.environ.get('INCHEON_VISUAL_OUTPUT_DIR', str(BASE.parent)))
OUT.mkdir(parents=True, exist_ok=True)
ASSETS=BASE/'시각검토/assets_print'
PREVIEW=Path(os.environ.get('INCHEON_VISUAL_PREVIEW_DIR', str(BASE/'시각검토/시각화_완성본')))
PREVIEW.mkdir(parents=True, exist_ok=True)
DATA=json.loads((BASE/'visual_content.json').read_text())
W,H=A4
M=32
CW=W-2*M
GAP=9
COL=(CW-2*GAP)/3
FONTDIR=Path('/Users/chokogamja/Library/Fonts')
pdfmetrics.registerFont(TTFont('Ko',str(FONTDIR/'KoPubWorld Dotum Medium.ttf')))
pdfmetrics.registerFont(TTFont('KoB',str(FONTDIR/'KoPubWorld Dotum Bold.ttf')))
NAVY='#13384B'
INK='#203B49'
TEAL='#087D80'
BLUE='#286BB2'
MUTED='#5C6E79'
LIGHT='#F1F5F7'
LINE='#D7E2E7'
WHITE='#FFFFFF'
STAGE_COLORS=[MUTED,BLUE,TEAL]

pdf_path=OUT/'인천시_7개실험실_수집분석_시각화_A4.pdf'
pptx_path=OUT/'인천시_7개실험실_수집분석_시각화_A4_편집용.pptx'
c=canvas.Canvas(str(pdf_path),pagesize=A4)
c.setTitle('인천 창의디자인 사회실험 | 7개 실험실 수집·분석·디자인 도출')
c.setAuthor('')
prs=Presentation()
prs.slide_width=Pt(W);prs.slide_height=Pt(H)
prs.core_properties.title='인천 창의디자인 사회실험 | 수집·분석·디자인 도출'
prs.core_properties.author=''

def color(s):return RGBColor.from_string(s.lstrip('#'))

class Page:
    def __init__(self):self.slide=prs.slides.add_slide(prs.slide_layouts[6])

    def rect(self,x,y,w,h,fill,r=0,stroke=None):
        c.setFillColor(HexColor(fill))
        if stroke:c.setStrokeColor(HexColor(stroke));c.setLineWidth(.5)
        if r:c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
        else:c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))
        sh=self.slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE,Pt(x),Pt(y),Pt(w),Pt(h))
        sh.fill.solid();sh.fill.fore_color.rgb=color(fill)
        if stroke:sh.line.color.rgb=color(stroke);sh.line.width=Pt(.5)
        else:sh.line.fill.background()
        if r:
            try:sh.adjustments[0]=min(.1,r/min(w,h))
            except Exception:pass
        return sh

    def line(self,x1,y1,x2,y2,clr=LINE,width=.8):
        c.setStrokeColor(HexColor(clr));c.setLineWidth(width);c.line(x1,H-y1,x2,H-y2)
        s=self.slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Pt(x1),Pt(y1),Pt(x2),Pt(y2))
        s.line.color.rgb=color(clr);s.line.width=Pt(width)

    def text(self,text,x,y,w,h,size=10.7,bold=False,clr=INK,leading=None,align='left'):
        leading=leading or size*1.42
        sty=ParagraphStyle('p',fontName='KoB' if bold else 'Ko',fontSize=size,leading=leading,textColor=HexColor(clr),wordWrap='CJK',alignment={'left':0,'center':1,'right':2}[align])
        p=Paragraph(escape(text).replace('\n','<br/>'),sty)
        _,ph=p.wrap(w,h)
        if ph>h+.1:raise ValueError(f'Text overflow {ph:.1f}>{h:.1f} at {y}: {text}')
        p.drawOn(c,x,H-y-ph)
        shape=self.slide.shapes.add_textbox(Pt(x),Pt(y),Pt(w),Pt(h))
        tf=shape.text_frame
        tf.clear();tf.margin_left=0;tf.margin_right=0;tf.margin_top=0;tf.margin_bottom=0
        tf.word_wrap=True;tf.vertical_anchor=MSO_ANCHOR.TOP
        for i,line in enumerate(text.split('\n')):
            pp=tf.paragraphs[0] if i==0 else tf.add_paragraph()
            pp.text=line;pp.font.name='KoPubWorldDotum Bold' if bold else 'KoPubWorldDotum Medium'
            pp.font.size=Pt(size);pp.font.bold=bold;pp.font.color.rgb=color(clr)
            pp.space_before=Pt(0);pp.space_after=Pt(0);pp.line_spacing=Pt(leading)
            pp.alignment={'left':PP_ALIGN.LEFT,'center':PP_ALIGN.CENTER,'right':PP_ALIGN.RIGHT}[align]
            for run in pp.runs:
                rpr=run._r.get_or_add_rPr()
                ea=OxmlElement('a:ea');ea.set('typeface','KoPubWorld돋움체 Bold' if bold else 'KoPubWorld돋움체 Medium');rpr.append(ea)

    def image(self,path,x,y,w,h,contain=False):
        im=Image.open(path);iw,ih=im.size
        reader=ImageReader(str(path))
        if contain:
            ratio=min(w/iw,h/ih);rw=iw*ratio;rh=ih*ratio
            px=x+(w-rw)/2;py=y+(h-rh)/2
            c.drawImage(reader,px,H-py-rh,rw,rh,mask='auto')
            self.slide.shapes.add_picture(str(path),Pt(px),Pt(py),width=Pt(rw),height=Pt(rh))
        else:
            ratio=max(w/iw,h/ih);rw=iw*ratio;rh=ih*ratio
            c.saveState();p=c.beginPath();p.rect(x,H-y-h,w,h);c.clipPath(p,stroke=0)
            c.drawImage(reader,x+(w-rw)/2,H-y-h+(h-rh)/2,rw,rh,mask='auto');c.restoreState()
            pic=self.slide.shapes.add_picture(str(path),Pt(x),Pt(y),width=Pt(w),height=Pt(h))
            if rw>w:pic.crop_left=pic.crop_right=(rw-w)/(2*rw)
            if rh>h:pic.crop_top=pic.crop_bottom=(rh-h)/(2*rh)

    def down(self,x,y,clr=TEAL):
        self.line(x,y,x,y+9,clr,1.2)
        self.line(x-3,y+6,x,y+9,clr,1.2);self.line(x+3,y+6,x,y+9,clr,1.2)

for idx,d in enumerate(DATA,1):
    p=Page()
    p.rect(M,24,22,3,TEAL)
    p.text('인천 창의디자인 사회실험',M,34,CW-60,13,8.7,bold=True,clr=MUTED)
    p.text(f'{idx:02d}',W-M-48,31,48,32,27,bold=True,clr=TEAL,align='right',leading=32)
    p.text(d['category'],M,53,CW-60,15,9.4,clr=TEAL)
    p.text(d['name'],M,75,CW,26,18.5,bold=True,leading=24)
    p.text(d['headline'].replace('\n',' '),M,106,CW,25,15.5,bold=True,leading=21)
    p.text(d['background'],M,139,CW,33,10.7,clr=MUTED,leading=15)

    p.text(d.get('collection_title', '01   사전 · 1차 · 2차에서 무엇을 수집하나'),M,184,CW,20,12.5,bold=True,clr=NAVY)
    for j,s in enumerate(d['stages']):
        x=M+j*(COL+GAP);top=213;bottom=497
        p.rect(x,top,COL,bottom-top,LIGHT,r=5)
        p.rect(x,top,COL,3,STAGE_COLORS[j])
        p.text(s['title'],x+10,top+12,COL-20,20,12.4,bold=True,clr=STAGE_COLORS[j])
        asset=next(ASSETS.glob(s['image']+'.*'))
        p.image(asset,x+7,top+41,COL-14,88,contain=s['image'] in ['01_second','02_first_board','02_second_board','03_first','03_second','04_first','04_second'])
        # Titles can span two lines without changing the data alignment.
        p.text(s['subtitle'],x+10,top+139,COL-20,32,11.5,bold=True,leading=15)
        p.text(s['note'],x+10,top+173,COL-20,28,8.9,clr=MUTED,leading=12.2)
        p.line(x+10,top+204,x+COL-10,top+204,LINE,.65)
        p.text('수집·확인 항목',x+10,top+212,COL-20,14,8.9,bold=True,clr=MUTED)
        # The three phase columns retain the same item baseline.
        for k,item in enumerate(s['items']):
            p.rect(x+10,top+235+k*16.2,2.3,2.3,STAGE_COLORS[j])
            p.text(item,x+17,top+229.6+k*16.2,COL-25,16,9.8,leading=13.5)
    # Collection methods are kept directly under the phase columns.
    for j,s in enumerate(d['stages']):
        x=M+j*(COL+GAP)
        p.text(s['method'],x,504,COL,26,9.3,bold=True,clr=STAGE_COLORS[j],align='center',leading=12.5)

    p.text('02   수치 비교와 인터뷰를 어떻게 조합하나',M,543,CW,20,12.5,bold=True,clr=NAVY)
    bw=(CW-26)/2;by=574;bh=83
    for x,title,body,accent in [(M,'정량 | '+d['quant_title'],d['quant_body'],BLUE),(M+bw+26,'정성 | '+d['qual_title'],d['qual_body'],TEAL)]:
        p.rect(x,by,bw,bh,WHITE,r=4,stroke=LINE)
        p.rect(x+10,by+12,3,15,accent)
        p.text(title,x+20,by+11,bw-29,33,11.5,bold=True,clr=accent,leading=15)
        p.text(body,x+11,by+43,bw-22,34,9.8,leading=14.2)
    p.text('+',M+bw+5,by+27,16,25,18,bold=True,clr=MUTED,align='center',leading=25)
    mid=W/2
    p.down(mid,661)
    p.rect(M,677,CW,32,'#EAF4F3',r=4)
    p.text(d['combine'],M+12,685,CW-24,21,10.6,bold=True,clr=TEAL,align='center',leading=15)

    # Strong final panel makes the design output visible before fine detail.
    p.rect(M,724,CW,91,NAVY,r=5)
    p.text('03   얻고자 하는 디자인',M+13,735,CW-26,16,9.4,bold=True,clr='#A9D7D7')
    p.text(d['result'],M+13,756,CW-26,26,14.6,bold=True,clr=WHITE,leading=19)
    tagw=(CW-38)/3
    for j,tag in enumerate(d['tags']):
        x=M+13+j*(tagw+6)
        p.rect(x,787,tagw,18,'#245064',r=3)
        p.text(tag,x+2,789,tagw-4,15,9.4,bold=True,clr=WHITE,align='center',leading=13)
    p.text(d['scope'],M,824,CW-38,12,8.2,clr=MUTED)
    p.text(f'{idx} / 7',W-M-35,823,35,13,8.7,bold=True,clr=TEAL,align='right')
    c.showPage()

c.save();prs.save(pptx_path)
pdf=fitz.open(pdf_path)
assert len(pdf)==7
for page,d in zip(pdf,DATA):
    text=page.get_text()
    assert d['name'] in text
    for term in [d['stages'][0]['title'],'1차 실험','2차 실험','수치 비교','얻고자 하는 디자인']:
        assert term in text, (d['name'],term)
    for banned in ['출처','근거:','PDF','원문','미기재','McNemar','Fisher','Wilcoxon','신뢰구간']:
        assert banned not in text,(d['name'],banned)
    page.get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(PREVIEW/f'{page.number+1:02d}.png')
assert len(prs.slides)==7
print('PDF:',pdf_path)
print('PPTX:',pptx_path)
print('Verified seven portrait A4 pages and editable slides; no source labels or added tests.')
