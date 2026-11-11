from pathlib import Path
from html import escape
import json
import math

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.colors import HexColor
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
import fitz
from seonin_diagram_layout import render_seonin

BASE=Path(__file__).resolve().parent
OUT=BASE/'강남양식_완성본'
OUT.mkdir(exist_ok=True)
PREVIEW=OUT/'미리보기'
PREVIEW.mkdir(exist_ok=True)
DATA=json.loads((BASE/'review_content.json').read_text())
W,H=A4
M=32
CW=W-2*M
GAP=9
COL=(CW-2*GAP)/3
FONTDIR=Path('/Users/chokogamja/Library/Fonts')
pdfmetrics.registerFont(TTFont('Ko',str(FONTDIR/'KoPubWorld Dotum Medium.ttf')))
pdfmetrics.registerFont(TTFont('KoB',str(FONTDIR/'KoPubWorld Dotum Bold.ttf')))
NAVY='#332C2B'
INK='#474443'
TEAL='#5500FF'
BLUE='#5500FF'
MUTED='#666666'
LIGHT='#F1EFF9'
LINE='#D3CFDE'
WHITE='#FFFFFF'
STAGE_COLORS=[MUTED,BLUE,TEAL]

pdf_path=OUT/'인천시_7개실험실_수집분석_다이어그램_A4.pdf'
pptx_path=OUT/'인천시_7개실험실_수집분석_다이어그램_A4_편집용.pptx'
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

    def down(self,x,y,clr=TEAL):
        self.line(x,y,x,y+9,clr,1.2)
        self.line(x-3,y+6,x,y+9,clr,1.2);self.line(x+3,y+6,x,y+9,clr,1.2)

    def circle(self,cx,cy,r,fill,stroke=None):
        c.setFillColor(HexColor(fill))
        if stroke:c.setStrokeColor(HexColor(stroke));c.setLineWidth(.6)
        c.circle(cx,H-cy,r,fill=1,stroke=bool(stroke))
        sh=self.slide.shapes.add_shape(MSO_SHAPE.OVAL,Pt(cx-r),Pt(cy-r),Pt(r*2),Pt(r*2))
        sh.fill.solid();sh.fill.fore_color.rgb=color(fill)
        if stroke:sh.line.color.rgb=color(stroke);sh.line.width=Pt(.6)
        else:sh.line.fill.background()

RECIPES=[
    ('색 + 형태 + 문구','동물 + 색 + 완충재','↔','시민안과 어린이안을 같은 사진·지도 문항과 위치 설명으로 비교'),
    ('학생 선호 + 바라는 것','거울 + 색 + 긍정 문구','→','1차 응답을 색·문구·높이에 반영한 뒤 거울나무 설치 반응 확인'),
    ('픽토그램 안내','영문 + 한국어 병기','↔','같은 경로에서 안내 방식별 이해도와 참여 의사 비교'),
    ('권유형 : 1컷·3컷','금지형 : 1컷·3컷','↔','같은 3개 주제·장소·배치·문항·척도로 표현 방식 비교'),
    ('그늘 + 자리 + 오감 요소','1차 유지 + 스툴 꾸미기','+','1차 시설물을 유지하고 청년작가·시민 참여 프로그램 추가'),
    ('흡연존 + 휴게존','1차 유지 + 시간·방향 안내','+','공간 구분을 유지하고 1분·30초·15초 유도사인 추가'),
    ('통합 바닥 안내','1차 유지 + 짐 정리공간','+','1차 사이니지를 유지하고 바닥 영역·벽면 안내·짐 정리공간 추가')
]

# Typography, purple label bars, ruled comparison fields, pale panels and yellow
# synthesis highlights follow the supplied Gangnam review pages, adapted to A4 portrait.
# The factual copy remains the Incheon content already checked against its source PDF.
PURPLE='#5500FF'
YELLOW='#FFFDA5'
M=35
CW=W-2*M
for idx,(d,r) in enumerate(zip(DATA,RECIPES),1):
    p=Page()
    if idx == 2:
        render_seonin(p, d, W, H, c)
        c.showPage()
        continue
    p.rect(M,29,133,15,PURPLE)
    p.text('인천 창의디자인 사회실험',M+4,30,125,14,8.4,clr=WHITE,leading=12)
    p.text('거점별 실험·분석 계획',M,51,CW,20,13.8,bold=True,clr=PURPLE,leading=18)
    p.text(d['category'],M,78,CW,15,9.6,clr=MUTED)
    p.text(f'{idx:02d}. {d["name"]}',M,101,CW,27,19,bold=True,clr=NAVY,leading=25)
    p.line(M,139,W-M,139,LINE,.6)

    p.text('실험배경',M,153,62,16,10,bold=True,clr=PURPLE)
    p.text(d['background'].replace(' → ','\n'),M+70,151,CW-70,38,10.3,leading=14.5)
    p.text(d['scope'],M+70,186,CW-70,13,8.7,clr=MUTED,leading=12)

    # The prior observation is its own evidence block, not an assumed test baseline.
    pre=d['stages'][0]
    p.rect(M,204,64,16,PURPLE)
    p.text('사전 조사',M+4,205,56,14,9.2,bold=True,clr=WHITE,leading=13)
    p.text(pre['method'],M+73,205,CW-73,15,9.4,clr=MUTED)
    p.rect(M,228,CW,42,LIGHT)
    cellw=CW/3
    for j,item in enumerate(pre['items']):
        x=M+j*cellw
        if j:p.line(x,235,x,263,LINE,.5)
        p.text(item,x+8,238,cellw-16,24,10,bold=True,clr=NAVY,leading=14,align='center')
    p.text(pre['note'].replace('사진: ',''),M,275,CW,12,8.5,clr=MUTED,leading=12)

    p.text('01  실험 구성 및 수집 항목',M,302,CW,18,11.8,bold=True,clr=PURPLE,leading=16)
    gap=24
    bw=(CW-gap)/2
    for j in [0,1]:
        x=M+j*(bw+gap)
        s=d['stages'][j+1]
        p.rect(x,328,bw,19,PURPLE)
        p.text(f'{j+1}차 실험',x+6,330,bw-12,16,10,bold=True,clr=WHITE,leading=14)
        p.text(s['subtitle'],x,357,bw,29,12,bold=True,clr=NAVY,leading=16)
        p.text(r[j],x,385,bw,30,10.5,bold=True,clr=PURPLE,leading=14)
        p.line(x,415,x+bw,415,LINE,.55)
        p.text('수집 항목',x,423,bw,14,9,bold=True,clr=MUTED,leading=13)
        for k,item in enumerate(s['items']):
            p.text('· '+item,x,443+k*17,bw,17,10.2,leading=14)
        p.text(s['method'],x,498,bw,15,9.1,bold=True,clr=MUTED,leading=13)
    p.circle(W/2,395,8,WHITE)
    p.text(r[2],W/2-10,383,20,25,18,bold=True,clr=PURPLE,leading=23,align='center')
    p.rect(M,525,CW,29,LIGHT,r=12)
    p.text(r[3],M+10,533,CW-20,18,10,bold=True,clr=NAVY,align='center',leading=14)

    p.text('02  정량·정성 결합 분석',M,577,CW,18,11.8,bold=True,clr=PURPLE,leading=16)
    p.rect(M,602,CW,87,LIGHT)
    aw=(CW-26)/2
    for j,(label,title,body) in enumerate([
        ('정량 비교',d['quant_title'],d['quant_body']),
        ('정성 해석',d['qual_title'],d['qual_body'])
    ]):
        x=M+j*(aw+26)
        p.text(label,x+9,612,aw-18,15,9.6,bold=True,clr=PURPLE,leading=13)
        p.text(title,x+9,632,aw-18,18,10,bold=True,clr=NAVY,leading=14)
        p.text(body,x+9,653,aw-18,31,9.2,clr=INK,leading=13.2)
    p.circle(W/2,646,6.5,PURPLE)
    p.text('+',W/2-6,637,12,17,12.7,bold=True,clr=WHITE,align='center',leading=17)
    p.down(W/2,694,clr=PURPLE)
    p.rect(M+12,711,CW-24,24,YELLOW)
    p.text(d['combine'],M+18,717,CW-36,17,10.2,bold=True,clr=PURPLE,align='center',leading=14)

    p.text('03  디자인 반영 및 결과물',M,756,CW,17,11.8,bold=True,clr=PURPLE,leading=16)
    p.text(d['result'],M,781,CW,24,13.4,bold=True,clr=PURPLE,align='center',leading=18)
    p.text('   |   '.join(d['tags']),M,806,CW,15,9.4,bold=True,clr=NAVY,align='center',leading=13)
    p.line(M,828,W-M-27,828,LINE,.5)
    p.text(f'{idx:02d}',W-M-20,821,20,15,10,bold=True,clr=NAVY,align='right',leading=14)
    c.showPage()

c.save();prs.save(pptx_path)
pdf=fitz.open(pdf_path)
assert len(pdf)==7
for pg,d in zip(pdf,DATA):
    txt=pg.get_text()
    assert d['name'] in txt
    assert len(pg.get_images())==0
    if pg.number == 1:
        assert all(s in txt for s in ['형성평가', '6문항', '통합표', 'Lundy', 'Moore', 'Fetters'])
        pg.get_pixmap(matrix=fitz.Matrix(1.65,1.65)).save(PREVIEW/'02.png')
        continue
    assert all(s in txt for s in ['사전 조사','1차 실험','2차 실험','수집 항목','정량 비교','정성 해석','디자인 반영'])
    assert all(s not in txt for s in ['출처','근거:','PDF','원문','McNemar','Fisher','Wilcoxon','신뢰구간'])
    pg.get_pixmap(matrix=fitz.Matrix(1.65,1.65)).save(PREVIEW/f'{pg.number+1:02d}.png')
assert len(prs.slides)==7
print('Draft PDF:',pdf_path)
print('Draft PPTX:',pptx_path)
print('Verified: seven A4 portrait pages, source-based content and editable diagrams.')

