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
import pymupdf as fitz

BASE=Path(__file__).resolve().parent
OUT=BASE.parent
OUT.mkdir(exist_ok=True)
PREVIEW=BASE/'수정본_20261110'/'미리보기'
PREVIEW.mkdir(parents=True,exist_ok=True)
DATA=json.loads((BASE/'수정본_20261110'/'content.json').read_text())
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

pdf_path=OUT/'인천시_7개실험실_수집분석_다이어그램_A4_수정본.pdf'
pptx_path=OUT/'인천시_7개실험실_수집분석_다이어그램_A4_수정본_편집용.pptx'
c=canvas.Canvas(str(pdf_path),pagesize=A4)
c.setTitle('인천 창의디자인 사회실험 | 7개 실험실 수집·분석·디자인 도출 | 수정본')
c.setAuthor('')
prs=Presentation()
prs.slide_width=Pt(W);prs.slide_height=Pt(H)
prs.core_properties.title='인천 창의디자인 사회실험 | 수집·분석·디자인 도출 | 수정본'
prs.core_properties.author=''

def color(s):return RGBColor.from_string(s.lstrip('#'))

TEXT_BOXES=[]

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
        TEXT_BOXES.append(dict(page=len(prs.slides),text=text,x=x,y=y,w=w,height=ph,size=size))
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


# Retain the original blue palette and page-specific diagram forms.
M=33
CW=W-2*M
PALE='#EAEFF7'
GRAY='#F5F6F8'

def para(p,t,x,y,w,size=11.2,leading=18,h=None,clr=INK,bold=False):
    sty=ParagraphStyle('measure',fontName='KoB' if bold else 'Ko',fontSize=size,leading=leading,wordWrap='CJK')
    pp=Paragraph(escape(t).replace('\n','<br/>'),sty)
    _,hh=pp.wrap(w,1000)
    if h is not None and hh>h+.1:
        raise ValueError(f'Paragraph overflow {hh}>{h}: {t}')
    p.text(t,x,y,w,hh+.2,size,bold=bold,clr=clr,leading=leading)
    return y+hh

def title(p,t,x,y,w=CW,size=11.4):
    p.text(t,x,y,w,20,size,bold=True,clr=NAVY,leading=16)

def header(idx):
    d=DATA[idx-1]
    p=Page()
    p.text('인천 창의디자인 사회실험',M,26,300,14,9,bold=True,clr=BLUE,leading=12)
    p.text('수정본 · 2026.11.10',W-M-160,29,113,14,8.3,bold=True,clr=BLUE,align='right',leading=11)
    p.text(d['category'],M,45,400,14,9,clr=MUTED,leading=12)
    p.text(f'{idx:02d}',W-M-37,24,37,35,25,bold=True,clr=NAVY,align='right',leading=31)
    p.text(d['name'],M,71,CW,28,19,bold=True,clr=NAVY,leading=25)
    p.text(d['lead'],M,108,CW,26,13.7,bold=True,clr=INK,leading=20)
    para(p,d['intro'],M,147,CW,h=65)
    return p,d

def footer(p,d):
    p.line(M,758,W-M,758,NAVY,1)
    p.text(d['result'],M,769,CW,21,12,bold=True,clr=NAVY,leading=17)
    p.text(d['scope'],M,791,CW,13,8.2,clr=MUTED,leading=11)
    p.rect(M-4,806,CW+8,31,GRAY,r=3)
    p.text('공통 모집 기준: 최소 100명 · 문항 수×20명(5문항 기준 100명)',M+2,809,CW-4,13,8.3,bold=True,clr=NAVY,leading=11)
    p.text('송도 예외: 최대 20명 · 외국인 2~3명 가능 / 설치형 카메라는 굴포천에만 설치',M+2,822,CW-4,12,8.1,clr=MUTED,leading=11)

def arrow(p,x1,y1,x2,y2,clr=BLUE):
    p.line(x1,y1,x2,y2,clr,.9)
    aa=math.atan2(y2-y1,x2-x1)
    for dt in [-.5,.5]:
        p.line(x2,y2,x2-3.8*math.cos(aa+dt),y2-3.8*math.sin(aa+dt),clr,.9)

def bullets(p,items,x,y,w,size=9.6,step=25):
    for k,it in enumerate(items):
        p.text('·',x,y+k*step,w=8,h=17,size=size,bold=True,clr=BLUE,leading=14)
        para(p,it,x+11,y+k*step,w-11,size=size,leading=13.8,h=step)

def polygon(p,pts,fill,stroke=None):
    path=c.beginPath()
    path.moveTo(pts[0][0],H-pts[0][1])
    for x,y in pts[1:]:
        path.lineTo(x,H-y)
    path.close()
    c.setFillColor(HexColor(fill))
    if stroke:c.setStrokeColor(HexColor(stroke));c.setLineWidth(.6)
    c.drawPath(path,fill=1,stroke=bool(stroke))
    fb=p.slide.shapes.build_freeform(pts[0][0],pts[0][1],scale=12700)
    fb.add_line_segments(pts[1:],close=True)
    sh=fb.convert_to_shape()
    sh.fill.solid();sh.fill.fore_color.rgb=color(fill)
    if stroke:sh.line.color.rgb=color(stroke);sh.line.width=Pt(.6)
    else:sh.line.fill.background()

def ellipse(p,cx,cy,rx,ry,fill,stroke=None,angle=0):
    a=math.radians(angle)
    pts=[]
    for j in range(121):
        t=j*math.tau/120
        x=rx*math.cos(t);y=ry*math.sin(t)
        pts.append((cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a)))
    polygon(p,pts,fill,stroke)

def pill(p,t,x,y,w,h=20,fill=WHITE,stroke=None,size=9.4,clr=NAVY):
    p.rect(x,y,w,h,fill,r=h/2,stroke=stroke)
    p.text(t,x+5,y+3,w-10,h-3,size,bold=True,clr=clr,align='center',leading=size*1.25)

def phasecols(p,d,y):
    sw=(CW-24)/3
    for j,st in enumerate(d['stages']):
        xx=M+j*(sw+12)
        clr=[MUTED,BLUE,NAVY][j]
        p.line(xx,y,xx+sw,y,clr,1.2)
        p.text(['사전 조사','1차 실험','2차 실험'][j],xx,y+8,sw,16,10,bold=True,clr=clr,leading=14)
        bullets(p,st['items'],xx,y+37,sw,size=9.1,step=23)
        para(p,st['method'],xx,y+112,sw,8.4,12,h=36,clr=MUTED)

def rows(p,d,y,rh=59,labelw=119):
    for j,st in enumerate(d['stages']):
        yy=y+j*rh
        p.line(M,yy,W-M,yy,LINE,.6)
        p.text(['사전 조사','1차 실험','2차 실험'][j],M,yy+8,labelw-12,16,10,bold=True,clr=[MUTED,BLUE,NAVY][j],leading=14)
        para(p,st['subtitle'],M,yy+29,labelw-12,9.1,13,h=rh-30,clr=NAVY)
        xx=M+labelw
        para(p,' · '.join(st['items']),xx,yy+8,CW-labelw,9.7,14,h=rh-29)
        para(p,st['method'],xx,yy+rh-18,CW-labelw,8.6,12,h=13,clr=MUTED)
    p.line(M,y+3*rh,W-M,y+3*rh,LINE,.6)

def close_two(p,d,y=605):
    lw=320
    title(p,'수치와 인터뷰를 어떻게 함께 읽나',M,y,lw)
    para(p,d['analysis'],M,y+29,lw,10.2,15.5,h=120)
    x=M+346
    p.line(x-15,y,x-15,746,LINE,.6)
    title(p,'차후 디자인에 반영',x,y,CW-346)
    para(p,d['extension'],x,y+29,CW-346,9.8,15,h=120)


# 1. The original comparison of citizen and child designs.
p,d=header(1)
title(p,'시민안과 어린이안을 같은 사진·지도 질문으로 비교',M,227)
p.rect(M,259,CW,123,PALE)
polygon(p,[(M,259),(M+232,259),(M+256,320),(M+232,382),(M,382)],GRAY)
p.text('1차 · 색연필 수비대',M+12,268,222,19,10.5,bold=True,clr=NAVY,leading=14)
p.text('2차 · 꿈꾸는 안전디자이너',M+278,268,236,19,10.5,bold=True,clr=NAVY,leading=14)
for j,(a,b) in enumerate(zip(['색','형태','문구'],['동물','색','완충재'])):
    x1=M+45+j*66;x2=M+312+j*66
    p.circle(x1,326,24,WHITE,LINE)
    p.text(a,x1-23,318,46,18,10.1,bold=True,clr=NAVY,align='center',leading=14)
    p.circle(x2,326,24,WHITE)
    p.text(b,x2-23,318,46,18,10.1,bold=True,clr=NAVY,align='center',leading=14)
p.text('인지·위치 선택·설명 단서',M+20,359,210,16,9.2,clr=MUTED,align='center',leading=12)
p.text('동물·색 단서·소재·통행 여건',M+279,359,236,16,9.2,clr=NAVY,align='center',leading=12)
phasecols(p,d,410)
close_two(p,d,592)
footer(p,d);c.showPage()

# 2. Preferences feed into an integrated sculpture, followed by experience and place feedback.
p,d=header(2)
ellipse(p,M+143,371,147,155,LIGHT,angle=19)
centers=[(M+142,282),(M+59,432),(M+224,432)]
for a,b in [(0,1),(0,2),(1,2)]:
    p.line(*centers[a],*centers[b],BLUE,.8)
for (cx,cy),t in zip(centers,['요소별 선호','조형물로 조합','경험·장소 의견']):
    p.circle(cx,cy,38,WHITE,BLUE)
    p.text(t,cx-36,cy-8,72,19,9.1,bold=True,clr=NAVY,align='center',leading=14)
p.circle(M+142,366,40,NAVY)
p.text('학생의\n정서 경험',M+105,350,74,38,11,bold=True,clr=WHITE,align='center',leading=16)
x=M+315;ww=CW-315
for j,st in enumerate(d['stages']):
    yy=234+j*105
    p.text(['사전 조사','1차 실험 · 마음, 바라봄','2차 실험 · 마음, 마주봄'][j],x,yy,ww,18,10,bold=True,clr=NAVY,leading=14)
    para(p,' · '.join(st['items']),x,yy+27,ww,9.7,14,h=44)
    para(p,st['method'],x,yy+72,ww,8.5,12,h=26,clr=MUTED)
p.text('현장 관찰: 접근·시선·멈춤·체류시간 기록',M,546,300,16,8.8,clr=MUTED,leading=12)
title(p,'요소별 선호 → 조형물 경험 → 설치 장소와 디자인',M,578)
para(p,d['analysis'],M,609,CW,10.5,16,h=81)
para(p,d['extension'],M,705,CW,10.5,16,h=48)
footer(p,d);c.showPage()

# 3. The comparison concerns interaction prompts. Route guidance is secondary.
p,d=header(3)
for j,(label,sub) in enumerate([('교류 그림 안내','주먹 인사·하이파이브 등'),('교류 문자 안내','같은 행동을 영문·한국어로')]):
    cx=M+120+j*286
    ellipse(p,cx,287,117,67,LIGHT if j==0 else PALE,angle=-28 if j==0 else 28)
    p.text(['1차 실험','2차 실험'][j],cx-92,246,184,17,9.5,bold=True,clr=BLUE if j==0 else NAVY,align='center',leading=13)
    p.text(label,cx-92,274,184,22,14,bold=True,clr=NAVY,align='center',leading=20)
    p.text(sub,cx-102,306,204,18,9.4,clr=MUTED,align='center',leading=13)
    for k,t in enumerate(d['stages'][j+1]['items']):
        pill(p,t,cx-113,350+k*26,226,h=22,fill=WHITE,stroke=LINE,size=9.3)
    para(p,d['stages'][j+1]['method'],cx-113,435,226,8.8,12.5,h=26,clr=MUTED)
p.text('같은 경로 · 같은 교류 행동',M,479,CW,18,10.4,bold=True,clr=NAVY,align='center',leading=14)
for j,lab in enumerate(['시작점','중간 지점 1','중간 지점 2','끝점']):
    xx=M+74+j*126
    p.circle(xx,523,17,WHITE,BLUE)
    p.text(lab,xx-48,548,96,17,9.2,bold=True,clr=NAVY,align='center',leading=13)
    p.text(str(j+1),xx-10,516,20,17,10,bold=True,clr=BLUE,align='center',leading=13)
    if j<3:arrow(p,xx+22,523,xx+104,523)
p.text('관찰: 시작점·끝점 포함 4개 지점에서 실제 교류 행동 수행 여부 기록',M,574,CW,16,9.2,bold=True,clr=NAVY,leading=13)
p.text('사전 조사: 현장 관찰로 코스·교류 행동·안내 부착 위치 확인(정성)',M,594,CW,16,8.7,clr=MUTED,leading=12)
title(p,'기억·부담·효과의 응답을 실제 교류 행동과 함께 해석',M,622)
para(p,d['analysis'],M,651,CW,10.1,15.5,h=66)
para(p,d['extension'],M,716,CW,9.8,14.5,h=35)
footer(p,d);c.showPage()

# 4. The original expression-by-frame comparison and interview interpretation.
p,d=header(4)
title(p,'표현과 컷 수, 두 조건을 나누어 읽는다',M,232,259)
para(p,d['analysis'],M,266,251,10.4,16,h=144)
x=M+278;ww=CW-278
p.rect(x,232,ww,29,WHITE,stroke=LINE)
p.text('변기 · 휴지 · 청결',x+5,241,ww-10,17,10,bold=True,clr=NAVY,align='center',leading=14)
for j in [0,1]:
    xx=x+j*(ww+8)/2;sw=(ww-8)/2
    p.rect(xx,276,sw,28,LIGHT if j==0 else PALE)
    p.text(['1차 · 권유형','2차 · 금지형'][j],xx+3,284,sw-6,17,9.4,bold=True,clr=NAVY,align='center',leading=13)
    for k,t in enumerate(['1컷','3컷']):
        tw=(sw-5)/2
        p.rect(xx+k*(tw+5),319,tw,26,WHITE,stroke=LINE)
        p.text(t,xx+k*(tw+5)+2,327,tw-4,15,9.4,bold=True,clr=NAVY,align='center',leading=13)
arrow(p,x+ww/2,350,x+ww/2,362)
p.rect(x,367,ww,40,NAVY)
p.text('선택 수·비율\n이해도·경각심 5점 평가',x+5,375,ww-10,30,9.4,bold=True,clr=WHITE,align='center',leading=13)
para(p,'같은 장소·배치·문항·척도',x,420,ww,9.1,13,h=26,clr=MUTED)
title(p,'사전 · 1차 · 2차 수집 비교',M,459)
rows(p,d,487,rh=59,labelw=119)
title(p,'표현과 구성의 조합을 에티켓 안내에 연결',M,690)
para(p,d['extension'],M,720,CW,10.3,15.5,h=33)
footer(p,d);c.showPage()

# 5. Hardware remains in place; the program is across from it. Record hardware use.
p,d=header(5)
for j,(lab,desc) in enumerate([('1차 하드웨어','그늘·자리·오감 요소'),('2차 소프트웨어','맞은편 스툴 꾸미기'),('이용·체류 비교','하드웨어 이용 변화')]):
    cx=M+70+j*194
    p.circle(cx,295,59,LIGHT if j<2 else PALE,BLUE if j<2 else NAVY)
    p.text(lab,cx-56,270,112,22,11,bold=True,clr=NAVY,align='center',leading=17)
    p.text(desc,cx-56,304,112,30,9.2,clr=INK,align='center',leading=14)
    if j<2:
        p.text(['+','→'][j],cx+77,281,39,29,23,bold=True,clr=BLUE,align='center',leading=29)
p.text('1차 시설 유지 + 맞은편 프로그램 운영 → 프로그램 중 시설 이용·1·2차 체류 비교',M,375,CW,18,9.5,bold=True,clr=NAVY,align='center',leading=14)
p.rect(M,411,CW,62,GRAY,r=4)
title(p,'촬영 계획 | 담장 위 좌·우 2곳 + 굴포천 하단부',M+10,422,CW-20,size=10.7)
para(p,'외부: 담장 위쪽 좌·우 각 1곳에 카메라 설치\n하단부: 카메라 줌아웃 한계로 스마트폰 촬영',M+10,446,CW-20,9.4,12.5,h=26)
title(p,'정량 | 1·2차 이용·체류 비교',M,495,278)
para(p,d['analysis'],M,526,278,10.4,16,h=99)
title(p,'정성 | 머무름·참여 이유',M,642,278)
para(p,d['extension'],M,673,278,10.1,15.5,h=78)
x=M+303;ww=CW-303
for j,st in enumerate(d['stages']):
    yy=495+j*84
    p.line(x,yy,x+ww,yy,[MUTED,BLUE,NAVY][j],1.2)
    p.text(['사전 조사','1차 실험','2차 실험'][j],x,yy+7,ww,17,10,bold=True,clr=NAVY,leading=14)
    para(p,' · '.join(st['items']),x,yy+28,ww,9.2,13,h=29)
    para(p,st['method'],x,yy+58,ww,8.4,11.5,h=24,clr=MUTED)
footer(p,d);c.showPage()

# 6. Landscape and plaza smoking facility, then directional signs.
p,d=header(6)
for j in [0,1]:
    yy=249+j*100
    p.circle(M+38,yy+25,36,WHITE,BLUE if j==0 else NAVY)
    p.text(['1차\n환경 조성','2차\n안내 추가'][j],M+4,yy+9,68,37,10.1,bold=True,clr=NAVY,align='center',leading=14)
    xx=M+94
    p.text(['거리 바이오필릭 + 광장 흡연공간','1차 환경 유지 + 안내사인 추가'][j],xx,yy-5,269,19,10.5,bold=True,clr=NAVY,leading=15)
    para(p,' · '.join(d['stages'][j+1]['items']),xx,yy+25,251,9.6,14,h=44)
    for k,t in enumerate((['거리 흡연자 수','광장 흡연공간 이용'] if j==0 else ['사인 인지·공간 유도','시설물 안·밖 흡연'])):
        pill(p,t,M+370,yy+2+k*31,157,h=23,fill=LIGHT if j==0 else PALE,size=9.1)
para(p,d['stages'][1]['method'],M+94,452,CW-94,9.0,13,h=27,clr=MUTED)
p.line(M,487,W-M,487,LINE,.6)
p.text('사전 조사',M,502,80,18,10,bold=True,clr=NAVY,leading=14)
para(p,' · '.join(d['stages'][0]['items']),M+93,502,CW-93,9.8,14,h=29)
p.text(d['stages'][0]['method'],M+93,538,CW-93,14,8.8,clr=MUTED,leading=12)
title(p,'정량 | 흡연자 수와 공간 경험',M,584,320)
para(p,d['analysis'],M,615,320,10.2,15.5,h=132)
x=M+346
p.line(x-15,584,x-15,746,LINE,.6)
title(p,'정성 | 이유·개선 의견',x,584,CW-346,size=10.7)
para(p,d['extension'],x,615,CW-346,9.8,15,h=132)
footer(p,d);c.showPage()

# 7. The original integrated guidance plus luggage organization experiment.
p,d=header(7)
for j,(t,sub) in enumerate([('통합 길안내','1차 · 발걸음은 가볍게'),('보관·정리공간','2차 · 두 손은 자유롭게')]):
    cx=M+146+j*221
    ellipse(p,cx,266,117,43,LIGHT if j==0 else PALE,angle=-8 if j==0 else 8)
    p.text(t,cx-90,248,180,22,13,bold=True,clr=NAVY,align='center',leading=18)
    p.text(sub,cx-90,277,180,17,9.4,clr=MUTED,align='center',leading=13)
p.text('+',W/2-11,249,22,28,19,bold=True,clr=BLUE,align='center',leading=25)
pill(p,'기존 안내 유지 + 짐 정리 편의 추가',M+75,324,CW-150,h=25,fill=WHITE,stroke=BLUE,size=10)
for j,t in enumerate(d['tags']):
    xx=M+83+j*182
    p.line(W/2,349,xx,375,BLUE,.65)
    p.circle(xx,393,28,WHITE,NAVY)
    p.text(t.replace('·','·\n',1),xx-34,380,68,31,9.2,bold=True,clr=NAVY,align='center',leading=12.5)
phasecols(p,d,435)
title(p,'시설을 알아보는 수치와 실제 사용하는 경험을 연결',M,606)
para(p,d['analysis'],M,637,CW,10.5,16,h=66)
para(p,d['extension'],M,711,CW,10.0,15,h=41)
footer(p,d);c.showPage()

c.save()
prs.save(pptx_path)

# Check every deliverable, actual glyph bounds and preservation of both source files.
import hashlib
import zipfile
from PIL import Image,ImageOps,ImageDraw

work=BASE/'수정본_20261110'
original_hashes=json.loads((work/'original_hashes.json').read_text())
for name,digest in original_hashes.items():
    assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest,('Original changed',name)
pdf=fitz.open(pdf_path)
assert len(pdf)==7 and len(prs.slides)==7
required={
    2:['심리치료','응원받는 느낌','설치 희망 장소','스트레스를 가장 많이 받는 장소'],
    3:['교류 행동','주먹 인사','하이파이브','치얼업','보조 기능','4개 지점','한국인'],
    5:['맞은편','줌아웃','스마트폰 촬영','좌·우 각 1곳','하드웨어 이용','체류'],
    6:['바이오필릭','로데오광장','안쪽·바깥쪽','답답함','호기심','높이의 적정성','추가 질문'],
}
for idx,pg in enumerate(pdf,1):
    txt=pg.get_text()
    normalized=''.join(txt.split())
    for term in [DATA[idx-1]['name'],'수정본','사전 조사','1차','2차','정량','정성','인터뷰','최소 100명','문항 수×20명','5문항 기준 100명','송도 예외']+required.get(idx,[]):
        assert ''.join(term.split()) in normalized,(idx,term)
    slide_text=''.join(''.join(sh.text.split()) for sh in prs.slides[idx-1].shapes if sh.has_text_frame)
    for term in required.get(idx,[]):
        assert ''.join(term.split()) in slide_text,('Missing from editable slide',idx,term)
    if idx!=5:
        assert '카메라' not in txt.replace('설치형 카메라는 굴포천에만 설치','')
    assert abs(pg.rect.width-W)<.1 and abs(pg.rect.height-H)<.1
    assert not pg.get_images()
    assert '각 50명' not in txt
    assert not (idx==3 and '각 30명' in txt)
    for block in pg.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                x0,y0,x1,y1=span['bbox']
                assert 0<=x0<x1<=W+.2 and 0<=y0<y1<=H+.2,(idx,span)
    used={span['font'] for block in pg.get_text('dict')['blocks'] for line in block.get('lines',[]) for span in line['spans']}
    for font in pg.get_fonts():
        if font[3].split('+')[-1] in used:
            assert pdf.extract_font(font[0])[3],('Font not embedded',idx,font)
    pg.get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(PREVIEW/f'{idx:02d}.png')

with zipfile.ZipFile(pptx_path) as z:
    assert z.testzip() is None
assert len(Presentation(pptx_path).slides)==7
assert not any(sh.shape_type==13 for sl in prs.slides for sh in sl.shapes)

# Broad text-box overlap check, followed by visual inspection of all seven pages.
overlaps=[]
for i,a in enumerate(TEXT_BOXES):
    for b in TEXT_BOXES[i+1:]:
        if a['page']!=b['page']:continue
        dx=min(a['x']+a['w'],b['x']+b['w'])-max(a['x'],b['x'])
        dy=min(a['y']+a['height'],b['y']+b['height'])-max(a['y'],b['y'])
        if dx>.5 and dy>.5:
            overlaps.append(dict(page=a['page'],first=a['text'],second=b['text'],overlap=[dx,dy]))
assert not overlaps,overlaps

thumbs=[]
for i in range(1,8):
    im=Image.open(PREVIEW/f'{i:02d}.png').convert('RGB')
    im.thumbnail((397,562))
    thumbs.append(im)
sheet=Image.new('RGB',(4*417,2*597),'#dfe3e8')
draw=ImageDraw.Draw(sheet)
for i,im in enumerate(thumbs):
    xx=(i%4)*417+10;yy=(i//4)*597+25
    sheet.paste(im,(xx,yy))
    draw.text((xx,yy-17),f'{i+1:02d}',fill='black')
sheet.save(work/'전체7쪽_검토.png')

verification={
    'date':'2026-11-10','pages':7,'slides':7,'page_size':'A4 portrait',
    'original_files_preserved':True,'fonts_embedded':True,'images_in_deliverables':0,
    'text_bounds_checked':True,'text_box_overlaps':overlaps,
    'pdf_sha256':hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
    'pptx_sha256':hashlib.sha256(pptx_path.read_bytes()).hexdigest(),
}
(work/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
print('PDF:',pdf_path)
print('PPTX:',pptx_path)
print('Verified: seven A4 pages, original preservation, required content, embedded fonts, editable vector diagrams.')
print('Text-box overlap candidates:',json.dumps(overlaps,ensure_ascii=False))


