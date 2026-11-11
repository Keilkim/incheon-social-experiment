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

BASE=Path(__file__).resolve().parent
OUT=BASE/'해설형_완성본'
OUT.mkdir(exist_ok=True)
PREVIEW=OUT/'미리보기'
PREVIEW.mkdir(exist_ok=True)
DATA=json.loads((BASE/'infographic_content.json').read_text())
W,H=A4
M=32
CW=W-2*M
GAP=9
COL=(CW-2*GAP)/3
FONTDIR=Path('/Users/chokogamja/Library/Fonts')
pdfmetrics.registerFont(TTFont('Ko',str(FONTDIR/'KoPubWorld Dotum Medium.ttf')))
pdfmetrics.registerFont(TTFont('KoB',str(FONTDIR/'KoPubWorld Dotum Bold.ttf')))
NAVY='#3B5094'
INK='#333333'
TEAL='#55ADD0'
BLUE='#55ADD0'
MUTED='#666666'
LIGHT='#E8F3F9'
LINE='#DCE3EB'
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


COPY=json.loads((BASE/'editorial_copy.json').read_text())
M=33;CW=W-2*M
PALE='#EAEFF7';GRAY='#F5F6F8'

def para(p,t,x,y,w,size=11.2,leading=18,h=None,clr=INK,bold=False):
    sty=ParagraphStyle('measure',fontName='KoB' if bold else 'Ko',fontSize=size,leading=leading,wordWrap='CJK')
    pp=Paragraph(escape(t).replace('\n','<br/>'),sty);_,hh=pp.wrap(w,1000)
    if h is not None and hh>h+.1:raise ValueError(f'Paragraph overflow {hh}>{h}: {t}')
    p.text(t,x,y,w,hh+.2,size,bold=bold,clr=clr,leading=leading)
    return y+hh

def title(p,t,x,y,w=CW):
    p.text(t,x,y,w,20,11.4,bold=True,clr=NAVY,leading=16)

def header(idx):
    d=DATA[idx-1];e=COPY[idx-1];p=Page()
    p.text('인천 창의디자인 사회실험',M,26,300,14,9,bold=True,clr=BLUE,leading=12)
    p.text(d['category'],M,45,400,14,9,clr=MUTED,leading=12)
    p.text(f'{idx:02d}',W-M-37,24,37,35,25,bold=True,clr=NAVY,align='right',leading=31)
    p.text(d['name'],M,71,CW,28,19,bold=True,clr=NAVY,leading=25)
    p.text(e['lead'],M,108,CW,26,13.7,bold=True,clr=INK,leading=20)
    para(p,e['intro'],M,147,CW,h=65)
    return p,d,e

def footer(p,d):
    p.line(M,783,W-M,783,NAVY,1)
    p.text(d['result'],M,796,CW,21,12,bold=True,clr=NAVY,leading=17)
    p.text(d['scope'],M,824,CW,13,8.3,clr=MUTED,leading=11)

def arrow(p,x1,y1,x2,y2,clr=BLUE):
    p.line(x1,y1,x2,y2,clr,.9)
    aa=math.atan2(y2-y1,x2-x1)
    for dt in [-.5,.5]:p.line(x2,y2,x2-3.8*math.cos(aa+dt),y2-3.8*math.sin(aa+dt),clr,.9)

def bullets(p,items,x,y,w,size=9.6,step=25):
    for k,it in enumerate(items):
        p.text('·',x,y+k*step,w=8,h=17,size=size,bold=True,clr=BLUE,leading=14)
        para(p,it,x+11,y+k*step,w-11,size=size,leading=13.8,h=step)

def columns(p,d,y,h=176):
    sw=(CW-24)/3
    for j,st in enumerate(d['stages']):
        xx=M+j*(sw+12);clr=[MUTED,BLUE,NAVY][j]
        p.line(xx,y,xx+sw,y,clr,1.8)
        p.text(['사전 조사','1차 실험','2차 실험'][j],xx,y+9,sw,16,10,bold=True,clr=clr,leading=14)
        para(p,st['subtitle'],xx,y+34,sw,9.7,14,h=29,bold=True,clr=NAVY)
        bullets(p,st['items'],xx,y+66,sw,size=9.3,step=25)
        para(p,st['method'].replace(' + ','\n'),xx,y+148,sw,8.8,12.5,h=27,clr=MUTED)

def rows(p,d,y,rh=72,labelw=125):
    for j,st in enumerate(d['stages']):
        yy=y+j*rh
        p.line(M,yy,W-M,yy,LINE,.6)
        p.text(['사전 조사','1차 실험','2차 실험'][j],M,yy+10,labelw-12,16,10,bold=True,clr=[MUTED,BLUE,NAVY][j],leading=14)
        para(p,st['subtitle'],M,yy+31,labelw-12,9.1,13,h=rh-32,clr=NAVY)
        xx=M+labelw
        para(p,' · '.join(st['items']),xx,yy+9,CW-labelw,9.7,14,h=rh-29)
        para(p,st['method'],xx,yy+rh-21,CW-labelw,8.8,12,h=13,clr=MUTED)
    p.line(M,y+3*rh,W-M,y+3*rh,LINE,.6)

# 1. Comparative report: a full-width phase comparison and an editorial side rail.
p,d,e=header(1)
title(p,'시민안과 어린이안을 같은 질문으로 읽기',M,227)
p.text('시민안  색·형태·문구',M,260,245,18,10.5,bold=True,clr=BLUE,leading=15)
p.text('어린이안  동물·색·완충재',W/2+13,260,245,18,10.5,bold=True,clr=NAVY,leading=15)
p.text('↔',W/2-10,256,20,23,16,bold=True,clr=BLUE,align='center',leading=21)
p.text('사진·지도 문항과 위치 설명을 공통 틀로 비교',M,288,CW,17,9.8,clr=MUTED,leading=14)
columns(p,d,326)
title(p,'수치와 설명 단서를 함께 해석한다',M,536,331)
para(p,e['analysis'],M,568,329,h=112)
title(p,'어린이 제안을 디자인으로 연결',M,676,331)
para(p,e['extension'],M,706,329,size=10.4,leading=16,h=68)
p.line(M+351,537,M+351,770,LINE,.7)
p.text('추출할 요소',M+368,538,160,18,10,bold=True,clr=NAVY,leading=14)
for j,t in enumerate(d['tags']):
    yy=580+j*62;p.text(f'0{j+1}',M+368,yy,30,18,10,bold=True,clr=BLUE,leading=14)
    para(p,t,M+368,yy+23,160,10.2,15,h=31,bold=True,clr=NAVY)
footer(p,d);c.showPage()

# 2. Sequential account: phase-specific evidence followed by preference -> design -> experience.
p,d,e=header(2)
title(p,'조사에서 설치 경험까지, 단계별로 수집하는 내용',M,229)
p.line(M+7,269,M+7,510,BLUE,1)
for j,st in enumerate(d['stages']):
    yy=267+j*83;p.circle(M+7,yy+7,3,WHITE,BLUE)
    p.text(['사전 조사','1차 실험','2차 실험'][j],M+24,yy,132,17,10.3,bold=True,clr=NAVY,leading=14)
    para(p,st['subtitle'],M+24,yy+25,132,9.4,13,h=28,clr=MUTED)
    para(p,' · '.join(st['items']),M+168,yy,CW-168,9.9,14.5,h=44)
    para(p,st['method'],M+168,yy+51,CW-168,9,13,h=14,clr=MUTED)
p.text('초기 후보지의 경사·휴식 여건 조사와 현재 설치 후 반응을 구분해 기록',M+24,519,CW-24,15,8.7,clr=MUTED,leading=12)
for j,t in enumerate(['학생 선호','색·문구·높이에 반영','거울나무 경험']):
    xx=M+j*183;p.text(t,xx,559,164,18,10.3,bold=True,clr=BLUE if j<2 else NAVY,align='center',leading=14)
    p.line(xx,582,xx+164,582,BLUE if j<2 else NAVY,1.5)
    if j<2:arrow(p,xx+167,568,xx+179,568)
title(p,'선호의 집계와 경험의 해석을 이어서 본다',M,605)
para(p,e['analysis'],M,635,CW,h=76)
para(p,e['extension'],M,721,CW,size=10.8,leading=17,h=51)
footer(p,d);c.showPage()

# 3. Parallel reading: site context in the margin, two guidance formats alongside it.
p,d,e=header(3)
p.rect(M,231,146,286,LIGHT)
p.text('사전 조사',M+12,244,122,18,10.5,bold=True,clr=NAVY,leading=15)
bullets(p,d['stages'][0]['items'],M+12,279,122,9.5,step=43)
para(p,d['stages'][0]['method'],M+12,432,122,9,13,h=29,clr=MUTED)
para(p,d['stages'][0]['note'],M+12,474,122,9.4,14,h=29,clr=NAVY)
xx=M+168;rw=CW-168;sw=(rw-18)/2
for j in [0,1]:
    x=xx+j*(sw+18);st=d['stages'][j+1]
    p.text(['1차 실험','2차 실험'][j],x,234,sw,17,10,bold=True,clr=BLUE if j==0 else NAVY,leading=14)
    p.text(['픽토그램 안내','영문·한국어 병기'][j],x,264,sw,19,11.3,bold=True,clr=NAVY,leading=16)
    para(p,st['subtitle'],x,292,sw,9.6,14,h=28,clr=MUTED)
    bullets(p,st['items'],x,329,sw,9.5,step=37)
    para(p,st['method'].replace(' + ','\n'),x,456,sw,9,13,h=29,clr=MUTED)
p.line(xx,503,W-M,503,BLUE,1.3)
p.text('같은 경로 · 정보 이해도와 참여 의사 5점 평가',xx,513,rw,17,9.3,bold=True,clr=NAVY,leading=13)
title(p,'경로를 아는 것과 함께 달리는 경험을 연결',M,560)
para(p,e['analysis'],M,593,CW,h=80)
title(p,'안내 방식의 차이를 보행안내 디자인에 반영',M,690)
para(p,e['extension'],M,718,CW,h=60)
footer(p,d);c.showPage()

# 4. Two-dimensional comparison: narrative on the left, expression x frame count on the right.
p,d,e=header(4)
title(p,'표현 방식과 컷 수를 함께 비교',M,230,246)
para(p,e['analysis'],M,264,246,size=10.8,leading=17,h=142)
x=M+274;qw=(CW-274-8)/2
p.text('1컷',x,231,qw,16,9.6,bold=True,clr=NAVY,align='center',leading=13)
p.text('3컷',x+qw+8,231,qw,16,9.6,bold=True,clr=NAVY,align='center',leading=13)
for row in range(2):
    for col in range(2):
        xx=x+col*(qw+8);yy=258+row*68
        p.rect(xx,yy,qw,59,LIGHT if row==0 else PALE)
        p.text(['1차 · 권유','2차 · 금지'][row],xx+5,yy+11,qw-10,16,10,bold=True,clr=NAVY,align='center',leading=14)
        p.text(['단일 장면','연속 장면'][col],xx+5,yy+34,qw-10,15,9,align='center',leading=12)
para(p,'같은 3개 주제\n같은 장소·배치·문항·척도',x,404,CW-274,9.3,14,h=29,clr=MUTED)
title(p,'사전 · 1차 · 2차의 수집 항목과 방법',M,454)
rows(p,d,484,rh=67,labelw=119)
title(p,'선택 수치에 의미 해석을 붙여 디자인으로 연결',M,701)
para(p,e['extension'],M,730,CW,size=10.5,leading=16,h=49)
footer(p,d);c.showPage()

# 5. A site-led feature: actual baseline figures, additive interventions, a small observation timeline.
p,d,e=header(5)
p.text('35%',M,232,110,39,28,bold=True,clr=BLUE,leading=36)
p.text('사전 방문 목적: 휴식',M+112,247,156,16,9.7,clr=MUTED,leading=13)
p.text('약 20분',M+282,232,125,39,25,bold=True,clr=NAVY,leading=36)
p.text('사전 휴식 체류',M+411,247,118,16,9.7,clr=MUTED,leading=13)
for j,st in enumerate(d['stages'][1:]):
    yy=291+j*88
    p.rect(M,yy,5,70,BLUE if j==0 else NAVY)
    p.text(['1차 실험 · 흐르는 인천','2차 실험 · 함께 만드는 인천'][j],M+16,yy+1,CW-16,18,11.2,bold=True,clr=NAVY,leading=15)
    para(p,st['note'],M+16,yy+26,187,9.5,14,h=29,clr=MUTED)
    para(p,' · '.join(st['items']),M+224,yy+25,CW-224,9.8,14,h=29)
    para(p,st['method'],M+224,yy+60,CW-224,8.8,12,h=13,clr=MUTED)
p.text('사전 조사',M,479,74,17,9.8,bold=True,clr=NAVY,leading=14)
para(p,'현장 관찰·보행자 설문으로 교량 하부의 휴식 집중과 그늘·자리·쾌적성 문제 기록',M+82,478,CW-82,9.5,14,h=30)
title(p,'체류의 변화에 머무는 이유를 함께 읽는다',M,537,335)
para(p,e['analysis'],M,570,333,size=11,leading=18,h=127)
p.line(M+355,540,M+355,697,LINE,.7)
p.text('2차 체류 기록',M+374,539,150,18,10,bold=True,clr=NAVY,leading=14)
for j,t in enumerate(['행사 전','행사 중','행사 후']):
    yy=578+j*41;p.circle(M+381,yy+6,2.7,BLUE);p.text(t,M+394,yy,124,17,10,bold=True,clr=NAVY,leading=14)
    if j<2:p.line(M+381,yy+11,M+381,yy+36,BLUE,.8)
para(p,e['extension'],M,721,CW,size=10.8,leading=17,h=51)
footer(p,d);c.showPage()

# 6. Behavioral lens: a compact action chain, phase bands, and a two-column commentary.
p,d,e=header(6)
for j,t in enumerate(['구역 구분','시간·방향 안내','이동·이용·꽁초 처리']):
    xx=M+j*181;p.text(t,xx,237,166,19,10.6,bold=True,clr=BLUE if j<2 else NAVY,leading=15)
    p.line(xx,263,xx+162,263,BLUE if j<2 else NAVY,1.5)
    if j<2:arrow(p,xx+166,246,xx+176,246)
rows(p,d,290,rh=73,labelw=126)
title(p,'평가와 실제 행동을 함께 해석한다',M,548,322)
para(p,e['analysis'],M,582,318,size=11.2,leading=18,h=152)
p.line(M+340,549,M+340,766,LINE,.7)
title(p,'디자인에 남길 요소',M+360,549,168)
para(p,e['extension'],M+360,583,168,size=10.8,leading=17,h=180)
footer(p,d);c.showPage()

# 7. Service sequence: wayfinding and storage are two connected layers, with narrative closing the page.
p,d,e=header(7)
p.text('1차  길찾기 안내',M,238,242,19,11.5,bold=True,clr=BLUE,leading=16)
p.text('2차  보관·정리 편의',W/2+15,238,242,19,11.5,bold=True,clr=NAVY,leading=16)
arrow(p,W/2-12,248,W/2+6,248)
p.text('통합 바닥 사이니지',M,266,242,17,9.8,clr=MUTED,leading=14)
p.text('기존 안내 유지 + 정리공간 추가',W/2+15,266,242,17,9.8,clr=MUTED,leading=14)
sw=(CW-24)/2
for j,st in enumerate(d['stages'][1:]):
    xx=M+j*(sw+24);p.line(xx,307,xx+sw,307,BLUE if j==0 else NAVY,1.5)
    p.text(['1차 실험 · 발걸음은 가볍게','2차 실험 · 두 손은 자유롭게'][j],xx,321,sw,18,10.5,bold=True,clr=NAVY,leading=15)
    bullets(p,st['items'],xx,358,sw,10,step=29)
    para(p,st['method'],xx,455,sw,9,13,h=28,clr=MUTED)
p.rect(M,493,CW,55,GRAY)
p.text('사전 조사',M+10,502,73,17,9.8,bold=True,clr=NAVY,leading=14)
para(p,'1층 대기·수하물 집중 · 기존 안내환경·이동 여건 · 2층 휴게공간 저이용',M+90,502,CW-101,9.6,14,h=28)
p.text('현장 관찰·기관 의견 / 현재 실험 범위는 1층',M+90,532,CW-101,13,8.7,clr=MUTED,leading=12)
title(p,'안내의 인지와 실제 보관·정리 이용을 연결한다',M,575)
para(p,e['analysis'],M,608,CW,h=82)
para(p,e['extension'],M,712,CW,size=10.8,leading=17,h=65)
footer(p,d);c.showPage()

c.save();prs.save(pptx_path)
pdf=fitz.open(pdf_path)
assert len(pdf)==7 and len(prs.slides)==7
for idx,pg in enumerate(pdf):
    txt=pg.get_text()
    assert DATA[idx]['name'] in txt
    assert not pg.get_images()
    assert all(t in txt for t in ['사전 조사','1차','2차','인터뷰'])
    assert not any(t in txt for t in ['출처','McNemar','Fisher','Wilcoxon','6문항','100~200명','Lundy','Fetters'])
    for b in pg.get_text('blocks'):
        assert b[0]>=0 and b[1]>=0 and b[2]<=W+.5 and b[3]<=H+.5,(idx,b)
    pg.get_pixmap(matrix=fitz.Matrix(1.65,1.65)).save(PREVIEW/f'{idx+1:02d}.png')
print(pdf_path);print(pptx_path)
