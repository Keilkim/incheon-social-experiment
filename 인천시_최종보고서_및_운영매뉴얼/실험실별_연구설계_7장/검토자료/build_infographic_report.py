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
OUT=BASE/'인포그래픽_완성본'
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
LINE='#DCE4EC'
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


from PIL import ImageColor

def solid(value):
    if not value or value=='none':return None
    if value.startswith('url'):return BLUE
    try:
        if value.startswith('rgba'):
            vals=value[value.index('(')+1:value.index(')')].split(',');r,g,b=map(float,vals[:3]);a=float(vals[3]);return '#%02X%02X%02X'%tuple(round(v*a+255*(1-a)) for v in (r,g,b))
        rgb=ImageColor.getrgb(value)
        if len(rgb)==4:
            a=rgb[3]/255;rgb=tuple(round(v*a+255*(1-a)) for v in rgb[:3])
        return '#%02X%02X%02X'%rgb
    except Exception:return BLUE

def graph(p,idx,x,y,w,h,top=False):
    data=json.loads((BASE/'인포그래픽'/f'{idx:02d}.json').read_text())
    vx,vy,vw,vh=data['viewBox'];s=min(w/vw,h/vh)
    dx=x+(w-vw*s)/2-vx*s;dy=y+(0 if top else (h-vh*s)/2)-vy*s
    for el in data['elements']:
        if el['kind']=='text':
            tx=dx+el['x']*s;ty=dy+el['y']*s
            p.text(el['text'],tx,ty,max(el['w']*s+8,25),el['size']*s*1.5,size=el['size']*s,bold=el['bold'],clr=solid(el['color']),leading=el['size']*s*1.15)
        else:
            pts=[(dx+xx*s,dy+yy*s) for xx,yy in el['points']]
            if not pts:continue
            fill=solid(el['fill']);stroke=solid(el['stroke']);sw=el['strokeWidth']*s
            path=c.beginPath();path.moveTo(pts[0][0],H-pts[0][1])
            for xx,yy in pts[1:]:path.lineTo(xx,H-yy)
            if el['closed']:path.close()
            if fill:c.setFillColor(HexColor(fill))
            if stroke:c.setStrokeColor(HexColor(stroke));c.setLineWidth(sw)
            c.drawPath(path,fill=bool(fill),stroke=bool(stroke))
            builder=p.slide.shapes.build_freeform(pts[0][0],pts[0][1],scale=12700)
            builder.add_line_segments(pts[1:],close=el['closed'])
            sh=builder.convert_to_shape()
            if fill:sh.fill.solid();sh.fill.fore_color.rgb=color(fill)
            else:sh.fill.background()
            if stroke:sh.line.color.rgb=color(stroke);sh.line.width=Pt(sw)
            else:sh.line.fill.background()
    return s,dx,dy

def arrow(p,x1,y1,x2,y2,clr=BLUE):
    p.line(x1,y1,x2,y2,clr,1)
    a=math.atan2(y2-y1,x2-x1)
    for delta in [-.55,.55]:p.line(x2,y2,x2-4*math.cos(a+delta),y2-4*math.sin(a+delta),clr,1)

M=35;CW=W-2*M
KINDS=['같은 질문으로 두 안 비교','선호 → 설치 → 경험 확인','같은 경로에서 안내 방식 비교','표현 방식 × 컷 수 비교','기존 환경 + 시민 참여','공간 구분 + 유도사인','통합 안내 + 정리공간']
QUANT=[
 ('인지 응답 비율 · 위치 정답률','같은 사진·지도 문항의 1·2차 응답 비교'),
 ('선호 응답 집계 · 이용 행동 비교','1차 선호 집계 + 2차 멈춤·시선·체류 확인'),
 ('인지율 · 경로 정확도 · 5점 평가','안내 방식별 이해도·러닝 참여 의사 비교'),
 ('선택 수·비율 · 5점 평가','권유·금지 / 1컷·3컷의 이해도·경각심 비교'),
 ('체류 인원·시간 · 멈춤률 · 변화율','교량 하부와 비교 + 참여 전·중·후 체류 비교'),
 ('이용률 · 행태 변화 · 5점 평가','구역 구분 뒤 안내를 더했을 때의 변화 확인'),
 ('인지율 · 이용률 · 정확도 · 만족도','1차 길찾기와 2차 보관·정리 이용 확인')]
QUAL=[
 ('위치 설명 단서 · 워크숍 의견','동물·색·문구를 기억하고 설명하는 방식'),
 ('선호 이유 · 설치 후 학생 인터뷰','편안함·안정감·자기수용감의 경험'),
 ('현장 인터뷰 · 러닝크루 자문','그림·문자 이해와 말하기·교류 경험'),
 ('선택 후 심층 인터뷰','선호 이유와 그림의 의미 해석·개선 의견'),
 ('시민·작가 인터뷰 · 학생 설문','그늘 체감·머무는 이유와 공동 제작 경험'),
 ('이용자 인터뷰 · 실제 행동 기록','구역·사인 개선 의견과 꽁초 처리 행동'),
 ('이용자 인터뷰 · 이동행태 관찰','쉬운 길찾기·짐 보관 의사·편의 경험')]
for idx,d in enumerate(DATA,1):
    p=Page()
    p.rect(M,28,3,29,BLUE)
    p.text('인천 창의디자인 사회실험',M+12,28,300,14,9.3,bold=True,clr=NAVY,leading=13)
    p.text(d['category'],M+12,46,300,14,8.8,clr=MUTED,leading=12)
    p.text(f'{idx:02d}',W-M-45,25,45,40,29,bold=True,clr=BLUE,align='right',leading=37)
    p.text(d['name'],M,77,CW,30,21,bold=True,clr=NAVY,leading=28)
    p.text(d['background'].replace(' → ','\n→ '),M,119,CW,34,10.3,leading=15)

    p.text('실험 설계',M,174,100,18,12,bold=True,clr=NAVY,leading=17)
    p.text(KINDS[idx-1],M+125,177,CW-125,15,9.5,bold=True,clr=BLUE,leading=13,align='right')
    # Real AntV Infographic graph, converted into editable native shapes and text.
    if idx==2:
        ss,ddx,ddy=graph(p,idx,M,211,CW,100,top=True)
        branchx=ddx+697*ss;branchy=ddy+106*ss
        # Branches show the two sources of experience evidence after the mirror-tree installation.
        p.line(branchx,branchy,branchx,314,BLUE,1)
        p.line(M+118,314,branchx,314,BLUE,1)
        arrow(p,M+118,314,M+118,328)
        arrow(p,W-M-118,314,W-M-118,328)
        for x,t,b in [(M,'행동 관찰','접근 · 시선 · 멈춤 · 체류시간'),(W/2+12,'학생 인터뷰','편안함 · 안정감 · 자기수용감')]:
            p.rect(x,333,(CW-24)/2,57,LIGHT,r=6)
            p.text(t,x+8,344,(CW-24)/2-16,17,11,bold=True,clr=NAVY,align='center',leading=15)
            p.text(b,x+8,368,(CW-24)/2-16,14,9.3,align='center',leading=12)
    elif idx==4:
        sq,xq,yq=graph(p,idx,M+58,199,CW-116,216)
        # One frame and a linked sequence of three frames encode the second comparison axis.
        for col in range(2):
            for row in range(2):
                count=1 if col==0 else 3
                xx=xq+(135+col*270)*sq-(21 if col==0 else 77)/2
                yy=yq+(105+row*155)*sq
                for k in range(count):
                    fx=xx+k*28
                    p.rect(fx,yy,21,16,WHITE,r=2,stroke=BLUE if col==0 else NAVY)
                    if k< count-1:arrow(p,fx+22,yy+8,fx+27,yy+8,NAVY)
        p.text('같은 3개 주제 · 장소 · 배치 · 문항 · 척도',M,415,CW,13,9,clr=MUTED,align='center',leading=12)
    else:
        s,dx,dy=graph(p,idx,M-6,201,CW+12,218)
        if idx>=5:
            p.circle(W/2,dy+68*s,10,WHITE)
            p.text('+',W/2-10,dy+68*s-13,20,27,21,bold=True,clr=BLUE,align='center',leading=26)

    p.text('수집 항목 비교',M,444,140,18,12,bold=True,clr=NAVY,leading=17)
    # Three phases are adjacent; observational prior work remains explicitly identified.
    p.rect(M,469,CW,19,NAVY)
    p.text('구분',M+7,471,43,15,9,bold=True,clr=WHITE,leading=13)
    p.text('무엇을 수집하나',M+61,471,327,15,9,bold=True,clr=WHITE,leading=13)
    p.text('어떻게 수집하나',W-M-128,471,120,15,9,bold=True,clr=WHITE,leading=13)
    for j,st in enumerate(d['stages']):
        yy=488+j*35
        p.rect(M,yy,CW,35,'#F8FAFC' if j%2==0 else WHITE)
        p.rect(M,yy,51,35,'#ECEEF2' if j==0 else ('#E8F3F9' if j==1 else '#EAEFF7'))
        p.text(['사전','1차','2차'][j],M+5,yy+10,41,17,10,bold=True,clr=NAVY,align='center',leading=14)
        # Keep three fields, arranged as two clear lines without new measurements.
        content=' · '.join(st['items'][:2])+'\n'+st['items'][2]
        p.text(content,M+61,yy+4,CW-201,29,8.8,leading=12.5)
        method=st['method'].replace(' + ','\n').replace('사진·지도 문항','사진·지도 문항').replace('행태 관찰','행태 관찰')
        p.text(method,W-M-128,yy+5,120,29,8.3,clr=MUTED,leading=12)
    p.text(d['stages'][0]['note'],M+4,598,CW-8,13,8.2,clr=MUTED,leading=12)

    p.text('분석을 디자인 판단으로 연결',M,623,CW,18,12,bold=True,clr=NAVY,leading=17)
    gap=30;aw=(CW-gap)/2
    for j,(lab,stuff,fill,clr) in enumerate([('수치 비교',QUANT[idx-1],LIGHT,BLUE),('인터뷰·경험 해석',QUAL[idx-1],'#EAEFF7',NAVY)]):
        xx=M+j*(aw+gap)
        p.rect(xx,650,aw,64,fill,r=5)
        p.text(lab,xx+10,658,aw-20,15,9.5,bold=True,clr=clr,leading=13)
        p.text(stuff[0],xx+10,679,aw-20,15,9.4,bold=True,clr=INK,leading=13)
        p.text(stuff[1],xx+10,698,aw-20,13,8.1,clr=MUTED,leading=11)
    # Convergence: each evidence source contributes to the same design decision.
    p.line(M+aw/2,714,M+aw/2,726,BLUE,1)
    p.line(W-M-aw/2,714,W-M-aw/2,726,NAVY,1)
    p.line(M+aw/2,726,W-M-aw/2,726,BLUE,1)
    p.circle(W/2,726,8,WHITE)
    p.text('+',W/2-8,716,16,20,16,bold=True,clr=BLUE,align='center',leading=20)
    arrow(p,W/2,735,W/2,748,NAVY)
    p.rect(M,753,CW,57,'#E8F3F9',r=5)
    p.text(d['result'],M+10,762,CW-20,20,13,bold=True,clr=NAVY,align='center',leading=18)
    p.text('  ·  '.join(d['tags']),M+10,788,CW-20,15,9.5,bold=True,clr=NAVY,align='center',leading=13)
    p.text(d['scope'],M,820,CW,13,8.2,clr=MUTED,leading=11)
    c.showPage()

c.save();prs.save(pptx_path)
pdf=fitz.open(pdf_path)
for i,pg in enumerate(pdf):
    assert abs(pg.rect.width-W)<.1 and abs(pg.rect.height-H)<.1
    assert DATA[i]['name'] in pg.get_text()
    assert not pg.get_images()
    assert not any(term in pg.get_text() for term in ['출처','근거:','McNemar','Fisher','Wilcoxon'])
    pg.get_pixmap(matrix=fitz.Matrix(1.65,1.65)).save(PREVIEW/f'{i+1:02d}.png')
assert len(pdf)==7 and len(prs.slides)==7
print(pdf_path);print(pptx_path)
print('Seven portrait A4 pages; AntV diagrams and native editable text/shapes; zero raster images.')
