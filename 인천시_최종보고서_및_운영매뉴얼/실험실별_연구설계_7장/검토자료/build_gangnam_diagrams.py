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
OUT=BASE/'강남도해_적용본'
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


from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE

def polygon(p,pts,fill,stroke=None):
    path=c.beginPath();path.moveTo(pts[0][0],H-pts[0][1])
    for x,y in pts[1:]:path.lineTo(x,H-y)
    path.close();c.setFillColor(HexColor(fill))
    if stroke:c.setStrokeColor(HexColor(stroke));c.setLineWidth(.6)
    c.drawPath(path,fill=1,stroke=bool(stroke))
    fb=p.slide.shapes.build_freeform(pts[0][0],pts[0][1],scale=12700)
    fb.add_line_segments(pts[1:],close=True);sh=fb.convert_to_shape();sh.fill.solid();sh.fill.fore_color.rgb=color(fill)
    if stroke:sh.line.color.rgb=color(stroke);sh.line.width=Pt(.6)
    else:sh.line.fill.background()

def ellipse(p,cx,cy,rx,ry,fill,stroke=None,angle=0):
    a=math.radians(angle);pts=[]
    for j in range(121):
        t=j*math.tau/120;x=rx*math.cos(t);y=ry*math.sin(t)
        pts.append((cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a)))
    polygon(p,pts,fill,stroke)

def pill(p,t,x,y,w,h=20,fill=WHITE,stroke=None,size=9.4,clr=NAVY):
    p.rect(x,y,w,h,fill,r=h/2,stroke=stroke)
    p.text(t,x+5,y+3,w-10,h-3,size,bold=True,clr=clr,align='center',leading=size*1.25)

def phasecols(p,d,y):
    sw=(CW-24)/3
    for j,st in enumerate(d['stages']):
        xx=M+j*(sw+12);clr=[MUTED,BLUE,NAVY][j]
        p.line(xx,y,xx+sw,y,clr,1.2)
        p.text(['사전 조사','1차 실험','2차 실험'][j],xx,y+8,sw,16,10,bold=True,clr=clr,leading=14)
        bullets(p,st['items'],xx,y+37,sw,size=9.1,step=23)
        para(p,st['method'].replace(' + ','\n'),xx,y+112,sw,8.6,12,h=26,clr=MUTED)

def close_two(p,e,y=614):
    lw=320
    title(p,'수치와 인터뷰를 어떻게 함께 읽나',M,y,lw)
    para(p,e['analysis'],M,y+31,lw,10.5,16,h=133)
    x=M+346;p.line(x-15,y,x-15,770,LINE,.6)
    title(p,'차후 디자인에 반영',x,y,CW-346)
    para(p,e['extension'],x,y+31,CW-346,10.2,15.5,h=133)

# 1 — Gangnam PDF 44: diagonal transition between two conditions, with grouped input circles.
p,d,e=header(1)
title(p,'시민안과 어린이안을 같은 사진·지도 질문으로 비교',M,227)
p.rect(M,259,CW,123,PALE)
polygon(p,[(M,259),(M+232,259),(M+256,320),(M+232,382),(M,382)],GRAY)
p.text('1차 · 색연필 수비대',M+12,268,222,19,10.5,bold=True,clr=NAVY,leading=14)
p.text('2차 · 꿈꾸는 안전디자이너',M+278,268,236,19,10.5,bold=True,clr=NAVY,leading=14)
for j,(a,b) in enumerate(zip(['색','형태','문구'],['동물','색','완충재'])):
    x1=M+45+j*66;x2=M+312+j*66
    p.circle(x1,326,24,WHITE,LINE);p.text(a,x1-23,318,46,18,10.1,bold=True,clr=NAVY,align='center',leading=14)
    p.circle(x2,326,24,WHITE);p.text(b,x2-23,318,46,18,10.1,bold=True,clr=NAVY,align='center',leading=14)
p.text('인지·위치 선택·설명 단서',M+20,359,210,16,9.2,clr=MUTED,align='center',leading=12)
p.text('동물·색 단서·소재·통행 여건',M+279,359,236,16,9.2,clr=NAVY,align='center',leading=12)
phasecols(p,d,421)
close_two(p,e,605)
footer(p,d);c.showPage()

# 2 — Gangnam PDF 180: a central subject connects three linked kinds of evidence.
p,d,e=header(2)
ellipse(p,M+143,371,147,155,LIGHT,angle=19)
centers=[(M+142,282),(M+59,432),(M+224,432)]
for a,b in [(0,1),(0,2),(1,2)]:p.line(*centers[a],*centers[b],BLUE,.8)
for (cx,cy),t in zip(centers,['선호 응답','설치 반영','관찰·인터뷰']):
    p.circle(cx,cy,38,WHITE,BLUE);p.text(t,cx-36,cy-8,72,19,10.1,bold=True,clr=NAVY,align='center',leading=14)
p.circle(M+142,366,40,NAVY)
p.text('학생의\n실제 경험',M+105,350,74,38,11,bold=True,clr=WHITE,align='center',leading=16)
x=M+315;ww=CW-315
for j,st in enumerate(d['stages']):
    yy=234+j*105
    p.text(['사전 조사','1차 실험 · 마음, 바라봄','2차 실험 · 마음, 마주봄'][j],x,yy,ww,18,10,bold=True,clr=NAVY,leading=14)
    para(p,' · '.join(st['items']),x,yy+28,ww,9.7,14,h=57)
    para(p,st['method'],x,yy+84,ww,8.5,12,h=13,clr=MUTED)
p.text('사전 현장조사는 초기 후보지의 기록',M,546,280,16,8.8,clr=MUTED,leading=12)
title(p,'선호가 설치로 이어진 뒤, 경험과 반응을 함께 읽는다',M,583)
para(p,e['analysis'],M,616,CW,11.2,18,h=89)
para(p,e['extension'],M,718,CW,10.7,16.5,h=56)
footer(p,d);c.showPage()

# 3 — Gangnam PDF 185: two organic concept fields with aligned subordinate keywords.
p,d,e=header(3)
for j,(label,sub) in enumerate([('픽토그램','보고, 함께하다'),('영문·한국어','읽고, 연결하다')]):
    cx=M+120+j*286;ellipse(p,cx,293,117,72,LIGHT if j==0 else PALE,angle=-28 if j==0 else 28)
    p.text(['1차 실험','2차 실험'][j],cx-92,249,184,17,9.5,bold=True,clr=BLUE if j==0 else NAVY,align='center',leading=13)
    p.text(label,cx-92,278,184,22,15,bold=True,clr=NAVY,align='center',leading=20)
    p.text(sub,cx-92,309,184,18,9.4,clr=MUTED,align='center',leading=13)
    for k,t in enumerate(d['stages'][j+1]['items']):pill(p,t,cx-113,357+k*27,226,h=22,fill=WHITE,stroke=LINE,size=9.3)
    para(p,d['stages'][j+1]['method'],cx-113,449,226,8.8,12.5,h=26,clr=MUTED)
p.text('같은 러닝 경로',W/2-55,482,110,18,10.4,bold=True,clr=NAVY,align='center',leading=14)
p.line(M+90,490,W/2-60,490,BLUE,.8);p.line(W/2+60,490,W-M-90,490,BLUE,.8)
p.text('사전 조사',M,527,83,18,9.8,bold=True,clr=NAVY,leading=14)
para(p,' · '.join(d['stages'][0]['items']),M+93,526,CW-93,9.7,14,h=29)
p.text('현장 관찰·사진 기록 / 코스·안내·부착 위치 검토',M+93,560,CW-93,14,8.7,clr=MUTED,leading=12)
title(p,'안내를 이해하는 방식과 말하기·교류 경험을 연결',M,604)
para(p,e['analysis'],M,636,CW,11,17,h=73)
para(p,e['extension'],M,725,CW,10.6,16,h=49)
footer(p,d);c.showPage()

# 4 — Gangnam PDF 8: source -> grouped categories -> comparable variables -> common criteria.
p,d,e=header(4)
title(p,'표현과 컷 수, 두 조건을 나누어 읽는다',M,232,259)
para(p,e['analysis'],M,266,251,10.6,16,h=141)
x=M+278;ww=CW-278
p.rect(x,232,ww,29,WHITE,stroke=LINE)
p.text('변기 · 휴지 · 청결',x+5,241,ww-10,17,10,bold=True,clr=NAVY,align='center',leading=14)
for j in [0,1]:
    xx=x+j*(ww+8)/2;sw=(ww-8)/2
    p.rect(xx,276,sw,28,LIGHT if j==0 else PALE)
    p.text(['1차 · 권유형','2차 · 금지형'][j],xx+3,284,sw-6,17,9.4,bold=True,clr=NAVY,align='center',leading=13)
    for k,t in enumerate(['1컷','3컷']):
        tw=(sw-5)/2;p.rect(xx+k*(tw+5),319,tw,26,WHITE,stroke=LINE)
        p.text(t,xx+k*(tw+5)+2,327,tw-4,15,9.4,bold=True,clr=NAVY,align='center',leading=13)
arrow(p,x+ww/2,350,x+ww/2,362)
p.rect(x,367,ww,40,NAVY)
p.text('선택 수·비율\n이해도·경각심 5점 평가',x+5,375,ww-10,30,9.4,bold=True,clr=WHITE,align='center',leading=13)
para(p,'같은 장소·배치·문항·척도',x,420,ww,9.1,13,h=26,clr=MUTED)
title(p,'사전 · 1차 · 2차 수집 비교',M,470)
rows(p,d,501,rh=59,labelw=119)
title(p,'표현과 구성의 조합을 에티켓 안내에 연결',M,704)
para(p,e['extension'],M,735,CW,10.5,16,h=44)
footer(p,d);c.showPage()

# 5 — Gangnam PDF 3: an explicit addition equation, rather than three sequential boxes.
p,d,e=header(5)
for j,(lab,desc) in enumerate([('휴게환경','그늘·자리·오감'),('시민 참여','스툴 공동 제작'),('체류·참여 관찰','머무름·경험')]):
    cx=M+70+j*194
    p.circle(cx,302,59,LIGHT if j<2 else PALE,BLUE if j<2 else NAVY)
    p.text(lab,cx-56,277,112,22,12,bold=True,clr=NAVY,align='center',leading=17)
    p.text(desc,cx-56,311,112,30,9.7,clr=INK,align='center',leading=14)
    if j<2:p.text(['+','→'][j],cx+77,288,39,29,23,bold=True,clr=BLUE,align='center',leading=29)
p.text('1차 시설을 유지하고 2차에 시민·청년작가의 참여를 추가',M,382,CW,18,9.8,bold=True,clr=NAVY,align='center',leading=14)
# Actual baseline facts are stated as facts in the narrative; no decorative result chart is added.
title(p,'무엇을 어떻게 비교하나',M,434,276)
para(p,e['analysis'],M,468,278,10.6,16.5,h=174)
para(p,e['extension'],M,666,278,10.5,16,h=108)
x=M+303;ww=CW-303
for j,st in enumerate(d['stages']):
    yy=433+j*106
    p.line(x,yy,x+ww,yy,[MUTED,BLUE,NAVY][j],1.2)
    p.text(['사전 조사','1차 실험','2차 실험'][j],x,yy+9,ww,17,10,bold=True,clr=NAVY,leading=14)
    para(p,' · '.join(st['items']),x,yy+34,ww,9.4,13.8,h=55)
    para(p,st['method'],x,yy+88,ww,8.6,12,h=13,clr=MUTED)
footer(p,d);c.showPage()

# 6 — Gangnam PDF 47: row-based strategy -> intervention -> measurable response.
p,d,e=header(6)
for j in [0,1]:
    yy=251+j*100;p.circle(M+38,yy+25,36,WHITE,BLUE if j==0 else NAVY)
    p.text(['1차\n공간 구분','2차\n안내 추가'][j],M+4,yy+9,68,37,10.1,bold=True,clr=NAVY,align='center',leading=14)
    xx=M+94
    p.text(['흡연존 + 휴게존','같은 공간 + 시간·방향 사인'][j],xx,yy-5,269,19,11,bold=True,clr=NAVY,leading=15)
    para(p,' · '.join(d['stages'][j+1]['items']),xx,yy+25,251,9.8,14,h=44)
    for k,t in enumerate((['구역 인지','이용·편의·만족'] if j==0 else ['흡연존 유도','실제 행동·꽁초 처리'])):
        pill(p,t,M+370,yy+2+k*31,157,h=23,fill=LIGHT if j==0 else PALE,size=9.5)
p.text('수집 방법: 행태 관찰 + 5점 설문·이용자 인터뷰',M+94,457,CW-94,16,9.2,clr=MUTED,leading=13)
p.line(M,492,W-M,492,LINE,.6)
p.text('사전 조사',M,507,80,18,10,bold=True,clr=NAVY,leading=14)
para(p,' · '.join(d['stages'][0]['items']),M+93,507,CW-93,9.8,14,h=29)
p.text('현장 관찰·시민 의견 / 거리 흡연·꽁초 관련 민원',M+93,543,CW-93,14,8.8,clr=MUTED,leading=12)
close_two(p,e,597)
footer(p,d);c.showPage()

# 7 — Gangnam PDF 46: concept keywords cluster into a common direction and then spread into outputs.
p,d,e=header(7)
for j,(t,sub) in enumerate([('통합 길안내','1차 · 발걸음은 가볍게'),('보관·정리공간','2차 · 두 손은 자유롭게')]):
    cx=M+146+j*221
    ellipse(p,cx,275,117,43,LIGHT if j==0 else PALE,angle=-8 if j==0 else 8)
    p.text(t,cx-111,257,222,22,13,bold=True,clr=NAVY,align='center',leading=18)
    p.text(sub,cx-111,286,222,17,9.4,clr=MUTED,align='center',leading=13)
p.text('+',W/2-11,258,22,28,19,bold=True,clr=BLUE,align='center',leading=25)
pill(p,'기존 안내 유지 + 짐 정리 편의 추가',M+75,334,CW-150,h=25,fill=WHITE,stroke=BLUE,size=10)
for j,t in enumerate(d['tags']):
    xx=M+83+j*182;p.line(W/2,359,xx,385,BLUE,.65)
    p.circle(xx,403,28,WHITE,NAVY)
    p.text(t.replace('·','·\n',1),xx-34,390,68,31,9.2,bold=True,clr=NAVY,align='center',leading=12.5)
phasecols(p,d,460)
title(p,'시설을 알아보는 수치와 실제 사용하는 경험을 연결',M,631)
para(p,e['analysis'],M,662,CW,10.8,16.5,h=67)
para(p,e['extension'],M,738,CW,10.1,15,h=41)
footer(p,d);c.showPage()

c.save();prs.save(pptx_path)
pdf=fitz.open(pdf_path)
assert len(pdf)==7 and len(prs.slides)==7
for idx,pg in enumerate(pdf):
    txt=pg.get_text();assert DATA[idx]['name'] in txt
    assert all(t in txt for t in ['사전 조사','1차','2차','인터뷰'])
    assert not pg.get_images()
    assert not any(t in txt for t in ['출처','McNemar','Wilcoxon','6문항','100~200명','Lundy','Fetters'])
    for b in pg.get_text('blocks'):assert b[0]>=0 and b[1]>=0 and b[2]<=W+.5 and b[3]<=H+.5,(idx,b)
    pg.get_pixmap(matrix=fitz.Matrix(1.65,1.65)).save(PREVIEW/f'{idx+1:02d}.png')
print(pdf_path);print(pptx_path)
