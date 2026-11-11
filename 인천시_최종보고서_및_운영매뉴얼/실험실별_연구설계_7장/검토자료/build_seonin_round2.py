"""Build the anonymous, sticker-only second-round Seonin boards.

PDF: actual 1210 x 1610 mm, 5 mm bleed. Editable PPTX: 1:2 scale.
Selection-dependent colour/phrase samples are physical attachment fields.
"""
from pathlib import Path
from html import escape
import csv
import json
import math
import unicodedata

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4
from pptx import Presentation
from pptx.util import Mm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from PIL import Image, ImageOps
import fitz

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
reference = next(p for p in ROOT.rglob('*.pdf') if unicodedata.normalize('NFC', p.name).startswith('선인재단 설문 보드 3장'))
OUT = reference.parent
PREVIEW = BASE / '시각검토' / '선인재단_2차보드_20261110'
PREVIEW.mkdir(parents=True, exist_ok=True)
FONTDIR = Path('/Users/chokogamja/Library/Fonts')
pdfmetrics.registerFont(TTFont('BoardKo', str(FONTDIR / 'KoPubWorld Dotum Medium.ttf')))
pdfmetrics.registerFont(TTFont('BoardKoB', str(FONTDIR / 'KoPubWorld Dotum Bold.ttf')))
BLUE = '#3E5294'
INK = '#454D52'
MUTED = '#858B91'
LINE = '#CDD2D9'
PALE = '#EAF4FA'
VOTE = '#F5F6F8'
WHITE = '#FFFFFF'
W, H, S = 1210, 1610, .5
M = 60
CW = W - 2 * M
PDF = OUT / '선인재단 2차 경험 설문 보드 3장(출력용 · 1210×1610mm · 재단 여유 5mm 포함 · A·B·C).pdf'
PPTX = OUT / '선인재단 2차 경험 설문 보드_편집용_1대2.pptx'
prs = Presentation()
prs.slide_width, prs.slide_height = Mm(W*S), Mm(H*S)
prs.core_properties.title = '선인재단 마음, 마주봄 | 2차 경험 설문 보드'
prs.core_properties.author = ''
c = canvas.Canvas(str(PDF), pagesize=(W*mm, H*mm))
c.setTitle('선인재단 2차 경험 스티커 설문 | 1210×1610mm | 3장')
c.setAuthor('')
TEXT_BOXES = []

def rgb(value):
    return RGBColor.from_string(value.lstrip('#'))

class Board:
    def __init__(self, letter):
        self.letter = letter
        self.slide = prs.slides.add_slide(prs.slide_layouts[6])

    def rect(self, x, y, w, h, fill=WHITE, stroke=None, radius=0, width=.9):
        c.setFillColor(HexColor(fill or WHITE))
        if stroke:
            c.setStrokeColor(HexColor(stroke)); c.setLineWidth(width*mm)
        if radius:
            c.roundRect(x*mm, (H-y-h)*mm, w*mm, h*mm, radius*mm, fill=bool(fill), stroke=bool(stroke))
        else:
            c.rect(x*mm, (H-y-h)*mm, w*mm, h*mm, fill=bool(fill), stroke=bool(stroke))
        sh = self.slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, Mm(x*S), Mm(y*S), Mm(w*S), Mm(h*S))
        if fill: sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
        else: sh.fill.background()
        if stroke: sh.line.color.rgb = rgb(stroke); sh.line.width = Mm(width*S)
        else: sh.line.fill.background()
        if radius:
            sh.adjustments[0] = min(.45, radius/min(w,h))
        return sh

    def ellipse(self, x, y, w, h, fill=WHITE, stroke=None, width=1.5):
        c.setFillColor(HexColor(fill or WHITE))
        if stroke: c.setStrokeColor(HexColor(stroke)); c.setLineWidth(width*mm)
        c.ellipse(x*mm, (H-y-h)*mm, (x+w)*mm, (H-y)*mm, fill=bool(fill), stroke=bool(stroke))
        sh = self.slide.shapes.add_shape(MSO_SHAPE.OVAL, Mm(x*S), Mm(y*S), Mm(w*S), Mm(h*S))
        if fill: sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
        else: sh.fill.background()
        if stroke: sh.line.color.rgb = rgb(stroke); sh.line.width = Mm(width*S)
        else: sh.line.fill.background()
        return sh

    def line(self, x1, y1, x2, y2, color=LINE, width=1):
        c.setStrokeColor(HexColor(color)); c.setLineWidth(width*mm)
        c.line(x1*mm, (H-y1)*mm, x2*mm, (H-y2)*mm)
        sh = self.slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Mm(x1*S), Mm(y1*S), Mm(x2*S), Mm(y2*S))
        sh.line.color.rgb=rgb(color); sh.line.width=Mm(width*S)

    def poly(self, points, color=BLUE, width=2, fill=None, close=False):
        p=c.beginPath();p.moveTo(points[0][0]*mm,(H-points[0][1])*mm)
        for x,y in points[1:]:p.lineTo(x*mm,(H-y)*mm)
        if close:p.close()
        c.setStrokeColor(HexColor(color));c.setLineWidth(width*mm)
        if fill:c.setFillColor(HexColor(fill))
        c.drawPath(p,stroke=True,fill=bool(fill))
        b=self.slide.shapes.build_freeform(Mm(points[0][0]*S),Mm(points[0][1]*S))
        b.add_line_segments([(Mm(x*S),Mm(y*S)) for x,y in points[1:]],close=close)
        sh=b.convert_to_shape();sh.line.color.rgb=rgb(color);sh.line.width=Mm(width*S)
        if fill:sh.fill.solid();sh.fill.fore_color.rgb=rgb(fill)
        else:sh.fill.background()

    def text(self, text, x, y, w, h, size=24, bold=False, color=INK, align='left', leading=None):
        leading=leading or size*1.27
        style=ParagraphStyle('board',fontName='BoardKoB' if bold else 'BoardKo',fontSize=size*mm,leading=leading*mm,textColor=HexColor(color),wordWrap='CJK',alignment={'left':0,'center':1,'right':2}[align])
        p=Paragraph(escape(text).replace('\n','<br/>'),style)
        _,ph=p.wrap(w*mm,h*mm)
        if ph>h*mm+.1:raise ValueError(f'{self.letter} text overflow: {text}: {ph/mm:.1f}>{h}')
        p.drawOn(c,x*mm,(H-y)*mm-ph)
        TEXT_BOXES.append({'page':self.letter,'text':text,'box_mm':[x,y,w,h],'actual_height_mm':ph/mm})
        sh=self.slide.shapes.add_textbox(Mm(x*S),Mm(y*S),Mm(w*S),Mm(h*S))
        tf=sh.text_frame;tf.clear();tf.word_wrap=True
        tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
        for i,line in enumerate(text.split('\n')):
            pp=tf.paragraphs[0] if i==0 else tf.add_paragraph()
            pp.text=line;pp.font.name='KoPubWorldDotum Bold' if bold else 'KoPubWorldDotum Medium'
            pp.font.size=Pt(size*mm*S);pp.font.bold=bold;pp.font.color.rgb=rgb(color)
            pp.space_before=pp.space_after=Pt(0);pp.line_spacing=Pt(leading*mm*S)
            pp.alignment={'left':PP_ALIGN.LEFT,'center':PP_ALIGN.CENTER,'right':PP_ALIGN.RIGHT}[align]
            for run in pp.runs:
                ea=OxmlElement('a:ea');ea.set('typeface','KoPubWorld돋움체 Bold' if bold else 'KoPubWorld돋움체 Medium');run._r.get_or_add_rPr().append(ea)

    def header(self, qs):
        self.rect(0,0,W,180,BLUE)
        self.text('마음, 마주봄 · 2차 거울나무 경험 설문',M,42,CW-180,40,24,True,WHITE)
        self.text('거울나무를 본 뒤 답해 주세요 · 문항마다 스티커 1장',M,99,CW-180,31,17,color='#E6EBFB')
        self.text(self.letter,W-M-125,24,125,121,95,True,WHITE,'right',105)
        self.text(qs+' / 보드 3장',W-M-240,139,240,29,20,color='#E6EBFB',align='right')

    def heading(self, num, title, y, instruction):
        self.ellipse(M,y+1,57,57,BLUE)
        self.text(str(num),M,y+6,57,48,37,True,WHITE,'center',43)
        self.text(title,M+76,y,CW-76,66,39,True,leading=49)
        self.text(instruction,M+76,y+70,CW-76,32,17,color=MUTED)

    def vote(self, x, y, w, h):
        self.rect(x,y,w,h,VOTE,radius=7)
        self.text('여기에 스티커',x+3,y+7,w-6,20,11.5,color='#A1A6AF',align='center')
        for yy in range(int(y+43),int(y+h-10),23):
            for xx in range(int(x+16),int(x+w-10),23):
                self.ellipse(xx-.75,yy-.75,1.5,1.5,'#DDE1E8')

    def icon(self, kind, cx, cy, r=39):
        self.ellipse(cx-r-7,cy-r-7,2*r+14,2*r+14,PALE)
        if kind.startswith('face'):
            mood=kind.split(':')[-1]
            bg={'sad':'#A9C2D2','slight_sad':'#C3D6E0','neutral':'#E5E8DF','smile':'#F6D777','big_smile':'#F6CB4D','tired':'#B9C7CF'}.get(mood,'#F6D777')
            self.ellipse(cx-r*.77,cy-r*.77,r*1.54,r*1.54,bg,BLUE,1.8)
            for ex in [cx-r*.27,cx+r*.27]:self.ellipse(ex-2.6,cy-r*.19-2.6,5.2,5.2,BLUE)
            if mood in ['neutral','tired']:
                self.line(cx-r*.27,cy+r*.30,cx+r*.27,cy+r*.30,BLUE,2)
            else:
                curve=[]
                for i in range(13):
                    xx=-.38+.76*i/12
                    yy=(.17+.22*(1-(xx/.38)**2)) if mood in ['smile','big_smile'] else (.43-.22*(1-(xx/.38)**2))
                    curve.append((cx+r*xx,cy+r*yy))
                self.poly(curve,BLUE,2)
        elif kind=='palette':
            self.ellipse(cx-r*.78,cy-r*.52,r*1.56,r*1.2,WHITE,BLUE,2)
            for i,clr in enumerate(['#F5C945','#F29C8E','#8BBC74','#55A4C4','#A48BC1']):
                a=math.pi*(1.12+.78*i/4);xx=cx+math.cos(a)*r*.53;yy=cy+math.sin(a)*r*.46
                self.ellipse(xx-6,yy-6,12,12,clr)
        elif kind=='mirror':
            self.ellipse(cx-r*.71,cy-r*.71,r*1.42,r*1.42,'#C7D1D8',BLUE,2)
            self.ellipse(cx-r*.34,cy-r*.43,r*.24,r*.24,WHITE)
        elif kind=='tree':
            self.rect(cx-7,cy+9,14,28,'#BE9B6A')
            for dx,dy,rr in [(-15,0,22),(16,0,22),(0,-17,27)]:self.ellipse(cx+dx-rr,cy+dy-rr,rr*2,rr*2,'#8AB872')
        elif kind=='quote':
            self.rect(cx-r*.78,cy-r*.62,r*1.56,r*1.1,WHITE,BLUE,6,2)
            for yy in [-.3,0,.3]:self.line(cx-r*.47,cy+r*yy,cx+r*.47,cy+r*yy,BLUE,2)
        elif kind=='question':
            self.text('?',cx-r,cy-r*.78,2*r,2*r,58,True,BLUE,'center',66)
        elif kind=='check':
            self.poly([(cx-r*.5,cy),(cx-r*.1,cy+r*.38),(cx+r*.55,cy-r*.4)],BLUE,5)
        elif kind=='edit':
            self.poly([(cx-r*.55,cy+r*.5),(cx-r*.38,cy+r*.08),(cx+r*.35,cy-r*.6),(cx+r*.62,cy-r*.34),(cx-r*.1,cy+r*.36),(cx-r*.55,cy+r*.5)],BLUE,2,fill='#F5D777',close=True)
        elif kind=='unseen':
            self.ellipse(cx-r*.7,cy-r*.7,r*1.4,r*1.4,WHITE,BLUE,2)
            self.line(cx-r*.5,cy+r*.5,cx+r*.5,cy-r*.5,BLUE,3)
        else:
            self.ellipse(cx-r*.68,cy-r*.68,r*1.36,r*1.36,WHITE,BLUE,2)
            self.line(cx-r*.34,cy,cx+r*.34,cy,BLUE,3)

    def cards(self, options, y=330, height=475, label_size=25):
        gap=12;n=len(options);w=(CW-(n-1)*gap)/n
        for j,opt in enumerate(options):
            x=M+j*(w+gap)
            self.rect(x,y,w,height,WHITE,LINE,11,.95)
            kind=opt.get('kind','icon')
            if kind=='color_slot':
                self.ellipse(x+w/2-43,y+35,86,86,WHITE,LINE,1.6)
                self.text(opt['label'],x+9,y+139,w-18,78,label_size,True,BLUE,'center')
            elif kind=='phrase_slot':
                self.text(opt['label'],x+8,y+13,w-16,33,22,True,BLUE,'center')
                self.rect(x+10,y+58,w-20,151,'#FCFDFE',LINE,5,.8)
            else:
                self.icon(opt.get('icon','none'),x+w/2,y+83,r=35 if n>=7 else 39)
                self.text(opt['label'],x+8,y+142,w-16,91,label_size,True,INK,'center')
            vote_y=y+245
            self.vote(x+10,vote_y,w-20,height-262)

    def footer(self, main):
        self.rect(0,1520,W,90,'#F4F6F9')
        self.text(main,M,1535,CW-92,24,16,True,BLUE)
        self.text('익명 · 문항마다 1장 · 이번 2차 조사기간 중 1회 참여 · 궁금한 점은 안내 담당자에게',M,1570,CW-92,22,12,color=MUTED)
        self.ellipse(W-M-65,1540,58,58,BLUE)
        self.ellipse(W-M-48,1551,24,24,WHITE)
        self.rect(W-M-40,1570,8,20,WHITE)

    def finish(self):c.showPage()

QUESTIONS=[]
def remember(num,title,opts,board):
    QUESTIONS.append({'board':board,'question':num,'title':title,'options':[o['label'].replace('\n',' ') for o in opts]})

a=Board('A');a.header('Q1 · Q2')
q1=[{'label':'많이\n불편해졌어','icon':'face:sad'},{'label':'조금\n불편해졌어','icon':'face:slight_sad'},{'label':'달라지지\n않았어','icon':'face:neutral'},{'label':'조금\n편안해졌어','icon':'face:smile'},{'label':'많이\n편안해졌어','icon':'face:big_smile'},{'label':'보지\n못했어','icon':'unseen'}]
a.heading(1,'거울나무를 보고 마음이 달라졌나요?',222,'방금 느낀 마음에 가장 가까운 것 하나에 스티커')
a.cards(q1)
a.line(M,846,W-M,846,LINE,1)
q2=[{'label':'색','icon':'palette'},{'label':'문구','icon':'quote'},{'label':'거울','icon':'mirror'},{'label':'나무 모양','icon':'tree'},{'label':'도움된 것은\n없어','icon':'none'},{'label':'잘\n모르겠어','icon':'question'},{'label':'보지\n못했어','icon':'unseen'}]
a.heading(2,'마음을 편안하게 한 것은?',882,'실제로 경험한 것 중 가장 도움이 된 것 하나 · 없다면 “없어”를 선택해요')
a.cards(q2,990,475,24)
a.footer('편안함과 도움이 된 요소를 확인해 다음 설치에 반영합니다.')
a.finish();remember(1,'거울나무를 보고 마음이 달라졌나요?',q1,'A');remember(2,'마음을 편안하게 한 것은?',q2,'A')

b=Board('B');b.header('Q3 · Q4')
q3=[{'label':f'색 {x}','kind':'color_slot'} for x in ['①','②','③','④']]+[{'label':'편안해진\n색은 없어','icon':'none'},{'label':'색을\n못 봤어','icon':'unseen'},{'label':'잘\n모르겠어','icon':'question'}]
b.heading(3,'마음을 편안하게 한 색은?',222,'거울나무에서 실제로 본 색 중 하나 · 아래의 색 견본을 보고 골라 주세요')
b.cards(q3)
b.line(M,846,W-M,846,LINE,1)
q4=[{'label':'괜찮아 보여','icon':'face:smile'},{'label':'웃게 돼','icon':'face:big_smile'},{'label':'그냥 그래','icon':'face:neutral'},{'label':'피곤해 보여','icon':'face:tired'},{'label':'보기 싫어','icon':'face:sad'},{'label':'잘 모르겠어','icon':'question'},{'label':'거울을\n안 봤어','icon':'unseen'}]
b.heading(4,'거울을 보니 어떤 생각이 들었나요?',882,'지금 가장 가까운 것 하나 · 거울을 안 봤다면 마지막 칸에 스티커')
b.cards(q4,990,475,23)
b.footer('실제 색과 거울의 반응을 확인해 색·배치·보이는 방식을 다듬습니다.')
b.finish();remember(3,'마음을 편안하게 한 색은?',q3,'B');remember(4,'거울을 보니 어떤 생각이 들었나요?',q4,'B')

d=Board('C');d.header('Q5 · Q6')
q5=[{'label':f'문구 {x}','kind':'phrase_slot'} for x in ['①','②','③']]+[{'label':'와닿은 말은\n없어','icon':'none'},{'label':'문구를\n안 읽었어','icon':'unseen'},{'label':'잘\n모르겠어','icon':'question'}]
d.heading(5,'실제로 읽고 마음에 와닿은 말은?',222,'거울나무에서 직접 읽은 말 중 하나 · 와닿은 말이 없다면 “없어”를 선택해요')
d.cards(q5,330,400,24)
d.line(M,752,W-M,752,LINE,1)
q6=[{'label':'지금대로\n두면 좋겠어','icon':'check'},{'label':'바꿔서\n두면 좋겠어','icon':'edit'},{'label':'두지\n않았으면 해','icon':'none'},{'label':'잘\n모르겠어','icon':'question'},{'label':'보지\n못했어','icon':'unseen'}]
d.heading(6,'앞으로도 이 길에 있으면 좋겠나요?',778,'가장 가까운 것 하나에 스티커')
d.cards(q6,886,420,25)
d.rect(M,1334,CW,166,'#FFFBEA','#D7C36D',10,1)
d.text('좋았던 점이나 바꾸고 싶은 점을 적어 주세요',M+20,1346,CW-40,35,23,True,INK,'center')
d.text('이름은 쓰지 않아요 · 포스트잇과 펜은 안내 담당자에게',M+20,1385,CW-40,23,13,color=MUTED,align='center')
d.footer('문구와 유지·수정 의견을 모아 다음 디자인과 운영을 정합니다.')
d.finish();remember(5,'실제로 읽고 마음에 와닿은 말은?',q5,'C');remember(6,'앞으로도 이 길에 있으면 좋겠나요?',q6,'C')
c.save();prs.save(PPTX)

# Explicit trim and bleed boxes; text/icons stay well within the safe area.
r=PdfReader(PDF);writer=PdfWriter()
for page in r.pages:
    page.trimbox=RectangleObject([5*mm,5*mm,(W-5)*mm,(H-5)*mm])
    page.bleedbox=RectangleObject([0,0,W*mm,H*mm])
    writer.add_page(page)
writer.add_metadata({'/Title':'선인재단 2차 경험 설문 보드 A·B·C | 실물 1210×1610mm | 재단여유 5mm','/Author':''})
tmp=PDF.with_suffix('.tmp.pdf')
with tmp.open('wb') as f:writer.write(f)
tmp.replace(PDF)

doc=fitz.open(PDF)
images=[]
for idx,page in enumerate(doc,1):
    dest=PREVIEW/f'보드_{idx:02d}.png'
    page.get_pixmap(matrix=fitz.Matrix(.43,.43)).save(dest)
    im=Image.open(dest).convert('RGB');im.thumbnail((420,560));images.append(im)
sheet=Image.new('RGB',(3*440+20,600),'#EAF0F5')
for i,im in enumerate(images):sheet.paste(im,(20+i*440+(420-im.width)//2,20))
sheet.save(PREVIEW/'3장_미리보기.png')
asset=BASE/'시각검토'/'assets_print'/'02_second_board.jpg'
sheet.save(asset,quality=94)

# Use the actual first-round board artwork in the revised A4 comparison page.
source_doc=fitz.open(reference)
first_sheet=Image.new('RGB',(3*440+20,600),'#EAF0F5')
for idx,page in enumerate(source_doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(.2,.2),alpha=False)
    im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    im.thumbnail((420,560))
    first_sheet.paste(im,(20+idx*440+(420-im.width)//2,20))
first_sheet.save(BASE/'시각검토'/'assets_print'/'02_first_board.jpg',quality=94)

# Prewritten phrase labels can be cut from A4 and attached after selection.
labels=OUT/'선인재단 2차_선정문구 부착용 라벨_A4_5종.pdf'
lc=canvas.Canvas(str(labels),pagesize=A4)
phrases=['오늘도\n괜찮아','넌 충분히\n잘하고 있어','천천히\n가도 돼','오늘 하루도\n응원해','있는 그대로\n좋아']
for phrase in phrases:
    x,y,w,h=32.5*mm,90*mm,145*mm,125*mm
    lc.setStrokeColor(HexColor(LINE));lc.setDash(3,3);lc.rect(x,y,w,h,fill=0,stroke=1);lc.setDash()
    st=ParagraphStyle('label',fontName='BoardKoB',fontSize=23*mm,leading=30*mm,textColor=HexColor(BLUE),alignment=1,wordWrap='CJK')
    pp=Paragraph(escape(phrase).replace('\n','<br/>'),st);_,ph=pp.wrap(w-12*mm,h)
    assert ph<h
    pp.drawOn(lc,x+6*mm,y+(h-ph)/2)
    lc.setFont('BoardKo',10);lc.setFillColor(HexColor(MUTED))
    lc.drawString(10*mm,73*mm,'A4 100% 출력 · 점선을 잘라 선정된 문구 칸에 부착 · 번호는 설치 문구와 일치')
    lc.showPage()
lc.save()

guide=OUT/'선인재단 2차 경험 설문_출력·운영 안내_A4.pdf'
gc=canvas.Canvas(str(guide),pagesize=A4)
gw,gh=A4
gy=gh-38
def guide_text(text,size=10.3,bold=False,color=INK,gap=9):
    global gy
    st=ParagraphStyle('guide',fontName='BoardKoB' if bold else 'BoardKo',fontSize=size,leading=size*1.48,textColor=HexColor(color),wordWrap='CJK')
    pp=Paragraph(escape(text).replace('\n','<br/>'),st);_,ph=pp.wrap(gw-70,gh)
    if gy-ph<32:raise ValueError('Guide overflow')
    pp.drawOn(gc,35,gy-ph);gy-=ph+gap
guide_text('선인재단 2차 경험 설문 | 출력·운영 안내',17,True,BLUE,15)
guide_text('보드 3장·6문항 · 스티커 응답 · URL·개인 연결 코드 없음',10.4,True,gap=16)
guide_text('01  출력과 부착 준비',12,True,BLUE)
guide_text('출력 PDF는 1210×1610mm 실물 크기입니다. 재단 여유 5mm를 포함하며 재단 후 1200×1600mm입니다. 인쇄는 100%로 요청하세요. 편집용 PPTX는 1:2 축척이므로 실물로 사용할 때 200% 확대가 필요합니다.')
guide_text('B의 색 ①~④ 원 안에는 1차 선정 후 실제 설치된 색과 같은 견본을 지름 80~84mm 정도로 부착합니다. 설치 색이 3개라면 색 ④의 카드 전체를 가려 투표할 수 없게 합니다. 미선정 색을 임의로 채우지 않습니다.')
guide_text('C의 문구 ①~③에는 실제 설치 문구를 부착합니다. 함께 제공한 A4 라벨은 점선 재단 후 145×125mm이며, 1차 고정 보기 5종 중 선정된 것만 사용합니다. 자유문구가 선정되면 같은 크기로 출력하거나 편집용 문구 칸을 수정합니다. 미사용 문구 칸은 전체를 가립니다.',gap=15)
guide_text('02  응답 운영',12,True,BLUE)
guide_text('거울나무를 먼저 접한 뒤 보드에 답하게 합니다. 한 학생이 이번 2차 조사기간 중 문항마다 1장씩 답하도록 안내합니다. 안 본 요소·안 읽은 문구는 해당 칸에 표시하게 하고, 모름·도움 없음도 그대로 수집합니다. 긍정 답변을 유도하지 않습니다.')
guide_text('같은 선택 칸에 스티커가 겹치지 않게 붙이도록 안내합니다. 응답이 쌓이면 운영일·시간대별로 사진과 수량을 먼저 기록한 뒤 투표 영역을 정리합니다. 포스트잇도 수거 전 촬영합니다. 학교별 집계가 필요하면 학교별 스티커 색을 구분할 수 있으며 학생 번호는 사용하지 않습니다.',gap=15)
guide_text('03  집계와 해석',12,True,BLUE)
guide_text('기본 비율은 보기 응답 수 ÷ 해당 문항 전체 응답 수입니다. 경험 평가를 따로 제시할 때는 미노출·모름을 제외한 분모와 제외 수를 명시합니다. “도움 없음·와닿은 말 없음”은 유효한 부정 응답이며 제외하지 않습니다.')
guide_text('6문항 스티커 합계를 6으로 나눠 참여 인원을 추정하지 않습니다. 스티커 응답 수와 별도 현장 참여 계수를 구분합니다. Q1은 학생이 회고한 편안함 변화 반응이며, 실제 사전·사후 심리 점수의 변화량이 아닙니다.')
guide_text('1차 선호 → 실제 선정·반영 → 2차 경험 응답을 연결표로 정리합니다. 색·문구의 보기나 질문 맥락이 달라질 수 있으므로 차수별 비율을 빼서 효과량으로 쓰지 않습니다. Q4는 유형별 분포를 참고 대조하고 미노출은 별도 표시합니다. 개인 연결이 없어 대응검정·개인 변화·요소별 인과효과는 주장하지 않습니다.')
gc.save()

# Tally form keeps only marginal counts; it contains no fictional results.
csv_path=OUT/'선인재단 2차 경험 설문_문항별 집계표.csv'
with csv_path.open('w',encoding='utf-8-sig',newline='') as f:
    wr=csv.writer(f);wr.writerow(['운영일','학교또는시간대','보드','문항','보기','실제선정색또는문구','스티커응답수','문항전체응답수','운영메모'])
    for q in QUESTIONS:
        for opt in q['options']:wr.writerow(['','',q['board'],q['question'],opt,'','','',''])
(PREVIEW/'questions.json').write_text(json.dumps(QUESTIONS,ensure_ascii=False,indent=2))
(PREVIEW/'text_boxes.json').write_text(json.dumps(TEXT_BOXES,ensure_ascii=False,indent=2))
print('BOARD_PDF',PDF)
print('BOARD_PPTX_1_TO_2',PPTX)
print('PREVIEW',PREVIEW)
print('LABELS',labels)
print('TALLY',csv_path)
print('GUIDE',guide)
