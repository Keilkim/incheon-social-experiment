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
OUT=BASE/'밀도조정_완성본'
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


# Adopt the supplied Gangnam PDF's convergence diagram, keyword grouping,
# and step comparison matrix. The palette follows the supplied Jiyu report.
M=32;CW=W-2*M
PALE='#EAEFF7';GRAY='#F5F6F8'
MECHANISM=[
 [('1차 · 시민안','색 + 형태 + 문구'),('2차 · 어린이안','동물 + 색 + 완충재'),'동일 사진·지도 문항으로 인지·위치 설명 비교'],
 [('1차 · 선호 조사','색·문구·바라는 것'),('2차 · 거울나무','설치 후 행동·경험'),'학생 선호 → 색·문구·높이에 반영 → 설치 반응 확인'],
 [('1차 · 픽토그램형','그림 중심 러닝 안내'),('2차 · 영문형','영문 중심·한국어 병기'),'동일 경로에서 안내 방식별 이해·참여 비교'],
 [('1차 · 권유형','1컷 ↔ 3컷'),('2차 · 금지형','1컷 ↔ 3컷'),'변기·휴지·청결 3개 주제 / 같은 장소·배치·문항·척도'],
 [('유지 · 1차 휴게환경','그늘 + 자리 + 오감 요소'),('추가 · 시민 참여','청년작가와 스툴 꾸미기'),'1차 시설 유지 + 공동 제작 프로그램 → 체류·참여 변화'],
 [('유지 · 1차 공간 구분','흡연존 + 휴게존'),('추가 · 유도사인','1분·30초·15초 안내'),'같은 공간 + 시간·방향 안내 → 인지·이동·행동 변화'],
 [('유지 · 1차 통합 안내','주요 시설 바닥 사이니지'),('추가 · 보관·정리공간','바닥 영역 + 벽면 안내'),'기존 안내 + 짐 정리공간 → 인지·실제 이용·편의 확인']
]

def arrow(p,x1,y1,x2,y2,clr=BLUE):
    p.line(x1,y1,x2,y2,clr,.9)
    a=math.atan2(y2-y1,x2-x1)
    for dt in [-.5,.5]:p.line(x2,y2,x2-3.7*math.cos(a+dt),y2-3.7*math.sin(a+dt),clr,.9)

def section(p,num,label,y):
    p.rect(M,y,21,16,NAVY)
    p.text(num,M+2,y+1,17,14,9,bold=True,clr=WHITE,align='center',leading=12)
    p.text(label,M+29,y-1,CW-29,19,11.6,bold=True,clr=NAVY,leading=16)

for idx,d in enumerate(DATA,1):
    p=Page()
    p.text('인천 창의디자인 사회실험',M,25,260,14,9,bold=True,clr=BLUE,leading=12)
    p.text(d['category'],M,44,350,14,9.2,clr=MUTED,leading=13)
    p.text(f'{idx:02d}',W-M-43,25,43,32,23,bold=True,clr=NAVY,align='right',leading=29)
    p.text(d['name'],M,68,CW,28,20,bold=True,clr=NAVY,leading=26)
    p.line(M,104,W-M,104,NAVY,1.1)
    p.text('실험배경',M,116,57,15,9.2,bold=True,clr=NAVY,leading=13)
    p.text(d['background'].replace(' → ','\n→ '),M+65,113,CW-65,32,9.7,leading=14)
    p.text(d['scope'],M+65,149,CW-65,14,8.4,clr=MUTED,leading=12)

    section(p,'01','실험의 구성과 비교 관계',178)
    gap=28;bw=(CW-gap)/2
    for j in [0,1]:
        xx=M+j*(bw+gap);label,body=MECHANISM[idx-1][j];fill=LIGHT if j==0 else PALE
        p.rect(xx,204,bw,42,fill)
        p.text(label,xx+8,210,bw-16,16,10.3,bold=True,clr=BLUE if j==0 else NAVY,leading=14,align='center')
        p.text(body,xx+8,229,bw-16,14,9.4,clr=INK,leading=13,align='center')
    # A small operator carries the relationship, while the lower bar states the comparison condition.
    op='+' if idx>=5 else ('→' if idx==2 else '↔')
    p.text(op,W/2-12,211,24,27,18,bold=True,clr=BLUE,align='center',leading=24)
    p.line(M+bw/2,246,M+bw/2,251,BLUE,.8)
    p.line(W-M-bw/2,246,W-M-bw/2,251,NAVY,.8)
    p.line(M+bw/2,251,W-M-bw/2,251,BLUE,.8)
    arrow(p,W/2,251,W/2,258,NAVY)
    p.text(MECHANISM[idx-1][2],M,261,CW,16,9.4,bold=True,clr=NAVY,align='center',leading=13)

    section(p,'02','사전 · 1차 · 2차 수집 항목 비교',291)
    labelw=54;sw=(CW-labelw)/3
    xs=[M+labelw+j*sw for j in range(3)]
    for j,st in enumerate(d['stages']):
        xx=xs[j];p.rect(xx,317,sw,22,['#ECEEF2',BLUE,NAVY][j])
        p.text(['사전 조사','1차 실험','2차 실험'][j],xx+6,321,sw-12,16,10,bold=True,clr=NAVY if j==0 else WHITE,align='center',leading=14)
    # Row labels and thin rules preserve alignment without enclosing every cell in a card.
    rows=[('실험·조사',339,39),('수집 항목',378,91),('수집 방법',469,39),('비교·활용',508,39)]
    for lab,y,h in rows:
        p.rect(M,y,labelw,h,GRAY)
        p.text(lab,M+3,y+11,labelw-6,23,8.7,bold=True,clr=NAVY,align='center',leading=12)
        p.line(M+labelw,y+h,W-M,y+h,LINE,.6)
    for j,st in enumerate(d['stages']):
        xx=xs[j]
        if j:p.line(xx,341,xx,547,LINE,.5)
        p.text(st['subtitle'],xx+8,350,sw-16,25,9.6,bold=True,clr=NAVY,align='center',leading=13)
        yy=389
        for item in st['items']:
            p.circle(xx+9,yy+5,1.3,BLUE if j<2 else NAVY)
            p.text(item,xx+16,yy-1,sw-24,26,9.2,leading=13)
            yy+=26
        p.text(st['method'].replace(' + ','\n'),xx+8,478,sw-16,28,9,clr=INK,leading=12.5,align='center')
        p.text(st['note'],xx+8,517,sw-16,28,8.6,clr=MUTED,leading=12,align='center')

    section(p,'03','수치 + 인터뷰 → 디자인 요소 추출',566)
    # Gangnam-style two-source convergence: what is compared, why it happens, then the common interpretation.
    aw=(CW-28)/2
    for j,(lab,title,body) in enumerate([('정량 · 집계와 비교',d['quant_title'],d['quant_body']),('정성 · 인터뷰와 경험',d['qual_title'],d['qual_body'])]):
        xx=M+j*(aw+28)
        p.rect(xx,594,aw,17,BLUE if j==0 else NAVY)
        p.text(lab,xx+6,596,aw-12,14,9,bold=True,clr=WHITE,leading=12)
        p.text(title,xx+6,620,aw-12,18,10,bold=True,clr=NAVY,leading=14)
        p.text(body,xx+6,644,aw-12,30,9.1,clr=INK,leading=13.2)
        p.line(xx,681,xx+aw,681,LINE,.6)
    p.circle(W/2,639,7,WHITE)
    p.text('+',W/2-8,628,16,22,16,bold=True,clr=BLUE,align='center',leading=21)
    p.line(M+aw/2,681,M+aw/2,690,BLUE,.8)
    p.line(W-M-aw/2,681,W-M-aw/2,690,NAVY,.8)
    p.line(M+aw/2,690,W-M-aw/2,690,BLUE,.8)
    arrow(p,W/2,690,W/2,698,NAVY)
    p.rect(M,701,CW,27,PALE)
    p.text(d['combine'],M+8,708,CW-16,17,9.8,bold=True,clr=NAVY,align='center',leading=14)

    # The three source-based keyword groups are the concrete handles for later design work.
    p.text('차후 디자인에 반영할 요소',M,742,CW,16,10.1,bold=True,clr=NAVY,leading=14)
    kw=(CW-16)/3
    for j,tag in enumerate(d['tags']):
        xx=M+j*(kw+8)
        p.line(xx,767,xx+kw,767,BLUE if j<2 else NAVY,1.7)
        p.text(tag,xx+3,775,kw-6,23,10,bold=True,clr=NAVY,align='center',leading=14)
    p.rect(M,806,CW,25,NAVY)
    p.text(d['result'],M+7,812,CW-14,17,11,bold=True,clr=WHITE,align='center',leading=15)
    c.showPage()

c.save();prs.save(pptx_path)
pdf=fitz.open(pdf_path)
assert len(pdf)==7 and len(prs.slides)==7
for i,pg in enumerate(pdf):
    text=pg.get_text()
    assert DATA[i]['name'] in text
    assert not pg.get_images()
    assert all(s in text for s in ['사전 조사','1차 실험','2차 실험','수집 항목','수집 방법','정량','정성','차후 디자인'])
    assert not any(s in text for s in ['출처','McNemar','Fisher','Wilcoxon','6문항','100~200명'])
    for b in pg.get_text('blocks'):
        assert b[0]>=0 and b[1]>=0 and b[2]<=W+.5 and b[3]<=H+.5,(i,b)
    pg.get_pixmap(matrix=fitz.Matrix(1.65,1.65)).save(PREVIEW/f'{i+1:02d}.png')
print(pdf_path);print(pptx_path);print('7 pages checked: compact mechanism, three-stage comparison, convergence and design keywords.')
