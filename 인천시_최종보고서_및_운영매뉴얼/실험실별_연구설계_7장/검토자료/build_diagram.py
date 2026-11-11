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
OUT=BASE.parent
PREVIEW=BASE/'시각검토/다이어그램_완성본'
PREVIEW.mkdir(exist_ok=True)
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

RECIPES=[
    dict(op='↔',left='색 + 형태 + 문구',right='동물 + 색 + 완충재',right_label='2차 실험',relation='시민안과 어린이안을 같은 사진·지도 문항과 위치 설명으로 비교'),
    dict(op='→',left='학생 선호 + 바라는 것',right='거울 + 색 + 긍정 문구',right_label='2차 실험',relation='1차 응답을 색·문구·높이에 반영 → 거울나무 설치 후 반응 확인'),
    dict(op='↔',left='픽토그램 안내',right='영문 + 한국어 병기',right_label='2차 실험',relation='같은 경로에서 안내 방식별 이해도·참여 의사 비교'),
    dict(op='↔',left='권유형 : 1컷 ↔ 3컷',right='금지형 : 1컷 ↔ 3컷',right_label='2차 실험',relation='같은 3개 주제·장소·배치·문항·척도로 표현 방식 비교'),
    dict(op='+',left='그늘 + 자리 + 오감 요소',right='시민 스툴 꾸미기',right_label='2차에 추가',relation='1차 시설물 그대로 유지 + 청년작가·시민 참여 프로그램'),
    dict(op='+',left='흡연존 + 휴게존',right='시간 + 방향 안내',right_label='2차에 추가',relation='1차 공간 구분 유지 + 흡연존까지 1분·30초·15초 유도사인'),
    dict(op='+',left='통합 바닥 안내',right='짐 보관·정리공간',right_label='2차에 추가',relation='1차 사이니지 유지 + 바닥 영역·벽면 안내·짐 정리공간')
]

for idx,(d,r) in enumerate(zip(DATA,RECIPES),1):
    p=Page()
    p.rect(M,25,23,3,TEAL)
    p.text('인천 창의디자인 사회실험',M,37,CW-60,14,8.8,bold=True,clr=MUTED)
    p.text(f'{idx:02d}',W-M-48,33,48,32,27,bold=True,clr=TEAL,align='right',leading=32)
    p.text(d['category'],M,58,CW-60,15,9.4,clr=TEAL)
    p.text(d['name'],M,83,CW,28,21,bold=True,leading=27)
    p.text(d['headline'].replace('\n',' '),M,119,CW,25,14.3,bold=True,leading=20)

    # Prior observation is one shared starting point, rather than another experiment.
    pre=d['stages'][0]
    p.rect(M,164,CW,87,LIGHT,r=5)
    p.text('사전 조사',M+12,174,73,17,11.2,bold=True,clr=NAVY)
    p.text(pre['method'],M+87,176,CW-102,15,9.4,clr=MUTED)
    chipw=(CW-38)/3
    for j,item in enumerate(pre['items']):
        x=M+12+j*(chipw+7)
        p.rect(x,201,chipw,33,WHITE,r=3)
        p.text(item,x+4,209,chipw-8,20,9.8,bold=True,leading=14,align='center')
    # Keep qualifiers that identify early fieldwork, without photograph captions.
    note=pre['note'].replace('사진: ','')
    p.text(note,M+12,236,CW-24,12,8.2,clr=MUTED)
    p.down(W/2,255,clr=MUTED)

    p.text('01   무엇을 바꾸고, 무엇을 수집하나',M,274,CW,20,12.7,bold=True,clr=NAVY)
    bw=(CW-39)/2
    tops=307
    for x,j,label,formula,accent in [(M,1,'1차 실험',r['left'],BLUE),(M+bw+39,2,r['right_label'],r['right'],TEAL)]:
        s=d['stages'][j]
        p.rect(x,tops,bw,181,WHITE,r=5,stroke=LINE)
        p.rect(x,tops,bw,3,accent)
        p.text(label,x+12,tops+12,bw-24,18,11,bold=True,clr=accent)
        p.text(formula,x+12,tops+40,bw-24,29,13.2,bold=True,leading=18)
        p.line(x+12,tops+74,x+bw-12,tops+74,LINE,.7)
        p.text('수집 항목',x+12,tops+84,bw-24,14,9,bold=True,clr=MUTED)
        for k,item in enumerate(s['items']):
            p.rect(x+12,tops+110+k*17,2.4,2.4,accent)
            p.text(item,x+20,tops+104+k*17,bw-31,17,10.5,leading=15)
        p.text(s['method'],x+12,tops+160,bw-24,16,9.1,bold=True,clr=accent,leading=12.8)
    # + means an additional intervention; ↔ means an alternative design comparison.
    p.rect(W/2-15,tops+34,30,37,WHITE,r=5)
    p.text(r['op'],W/2-14,tops+35,28,34,27,bold=True,clr=TEAL,leading=33,align='center')
    p.text(r['relation'],M+4,498,CW-8,29,10.2,bold=True,clr=MUTED,align='center',leading=14)
    p.down(W/2,528,clr=MUTED)

    p.text('02   수치 비교 + 인터뷰 해석',M,542,CW,20,12.7,bold=True,clr=NAVY)
    ay=575;ah=86;aw=(CW-28)/2
    for x,label,title,body,accent in [
        (M,'정량',d['quant_title'],d['quant_body'],BLUE),
        (M+aw+28,'정성',d['qual_title'],d['qual_body'],TEAL)
    ]:
        p.rect(x,ay,aw,ah,LIGHT,r=4)
        p.text(label,x+11,ay+9,aw-22,14,8.8,bold=True,clr=accent)
        p.text(title,x+11,ay+29,aw-22,19,10.8,bold=True,clr=accent,leading=15)
        p.text(body,x+11,ay+51,aw-22,31,9.5,leading=13.2)
    p.text('+',W/2-10,ay+26,20,31,24,bold=True,clr=TEAL,align='center',leading=30)
    p.down(W/2,667)
    p.text(d['combine'],M+4,688,CW-8,24,10.4,bold=True,clr=TEAL,leading=15,align='center')
    p.down(W/2,714)

    p.rect(M,727,CW,86,NAVY,r=5)
    p.text('03   얻고자 하는 디자인',M+13,737,CW-26,14,9,bold=True,clr='#A9D7D7')
    p.text(d['result'],M+13,757,CW-26,22,14.2,bold=True,clr=WHITE,leading=19)
    tw=(CW-38)/3
    for j,tag in enumerate(d['tags']):
        x=M+13+j*(tw+6)
        p.rect(x,787,tw,17,'#245064',r=3)
        p.text(tag,x+2,788,tw-4,15,9.3,bold=True,clr=WHITE,align='center',leading=13)
    p.text(d['scope'],M,824,CW-38,12,8.2,clr=MUTED)
    p.text(f'{idx} / 7',W-M-35,823,35,13,8.7,bold=True,clr=TEAL,align='right')
    c.showPage()

c.save();prs.save(pptx_path)
pdf=fitz.open(pdf_path)
assert len(pdf)==7
for page,d in zip(pdf,DATA):
    txt=page.get_text()
    assert d['name'] in txt
    assert len(page.get_images())==0
    assert all(s in txt for s in ['사전 조사','1차 실험','수집 항목','정량','정성','얻고자 하는 디자인'])
    assert all(s not in txt for s in ['출처','근거:','PDF','원문','미기재','McNemar','Fisher','Wilcoxon','신뢰구간'])
    page.get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(PREVIEW/f'{page.number+1:02d}.png')
assert len(prs.slides)==7
assert all(all(s.shape_type!=13 for s in slide.shapes) for slide in prs.slides)
print('PDF:',pdf_path)
print('PPTX:',pptx_path)
print('Verified: 7 portrait A4 pages and 7 editable slides; zero embedded images.')

