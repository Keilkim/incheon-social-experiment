"""2026-11-11: source-based terminal revision and aligned vector page system.

Build into this review directory; publish only after visual and text checks.
"""
from pathlib import Path
from html import escape
import json
import math
import hashlib
import unicodedata

import fitz
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement

WORK = Path(__file__).resolve().parent
BASE = WORK.parent
OUT = BASE.parent
ROOT = OUT.parent
DATA = json.loads((BASE / '수정본_20261110/content.json').read_text())
PDF_NAME = '인천시_7개실험실_수집분석_다이어그램_A4_수정본.pdf'
PPTX_NAME = '인천시_7개실험실_수집분석_다이어그램_A4_수정본_편집용.pptx'
W, H = A4
M = 36
CW = W - 2 * M
CYAN = '#00B0D7'
BLUE = '#0079C2'
INK = '#343E49'
MUTED = '#687681'
LINE = '#D4DCE2'
WHITE = '#FFFFFF'
GRAY = '#F5F7F8'
ACCENTS = ['#3B5094', '#3B5094', '#299B91', '#299B91', '#55ADD0', '#55ADD0', '#3B5094']
TINTS = ['#EEF0F7', '#EEF0F7', '#EAF6F3', '#EAF6F3', '#E9F4FA', '#E9F4FA', '#EEF0F7']
FONTDIR = Path('/Users/chokogamja/Library/Fonts')
pdfmetrics.registerFont(TTFont('Paper', str(FONTDIR / 'Paperlogy-4Regular.ttf')))
pdfmetrics.registerFont(TTFont('PaperM', str(FONTDIR / 'Paperlogy-5Medium.ttf')))
pdfmetrics.registerFont(TTFont('PaperB', str(FONTDIR / 'Paperlogy-7Bold.ttf')))

# Match the actual simplified observation forms and the common four-question interview.
d = DATA[6]
d.update(
    lead='유도 방향과 짐 배치를 세고, 행동의 이유를 묻다',
    intro='1층 대합실에서 1차 통합 바닥 안내를 유지하고 2차 보관·정리공간을 더한다. '
          '같은 코스와 관찰 지점에서 입장·이동·짐 배치의 사람 수를 기록하고, 짧은 인터뷰로 방향 판단과 이용의 이유를 확인한다.',
    analysis='정량: 시간대별 A·B·C 인원과 C의 밖/안 분포를 1·2차 비교한다. '
             '정성: 방향 판단·망설임·짐 배치·이용 불편의 이유를 행동 기록과 연결한다.',
    extension='안내 위치·연결 방식과 보관공간의 경계·배치를 개선한다.',
    scope='실험 범위: 1층 대합실 · 관찰: 1·2차 같은 항목 · 인터뷰: 공통 4문항 중 해당 문항',
)
d['stages'][1].update(items=['A 유도 방향으로 간 사람 수', 'B 유도선을 따라간 사람 수', 'C 짐을 둔 사람 수 (밖 / 안)'],
                      method='정량: 30분 단위 관찰 계수\n정성: 공통 4문항 인터뷰')
d['stages'][2].update(items=d['stages'][1]['items'][:], method=d['stages'][1]['method'])
d.update(quant_title='시간대별 단계 인원·짐 배치 비교', quant_body='A·B·C 인원과 C 밖/안 분포를 같은 항목으로 1·2차 비교',
         qual_title='방향 판단·망설임·짐 배치 이유', qual_body='관찰한 행동과 공통 4문항 인터뷰를 연결',
         combine='단계 인원·짐 배치와 해당 행동의 이유를 함께 해석',
         result_body='안내의 위치·연결 방식과 보관공간 경계·배치의 개선으로 연결')
(WORK / 'content.json').write_text(json.dumps(DATA, ensure_ascii=False, indent=2) + '\n')

C = canvas.Canvas(str(WORK / PDF_NAME), pagesize=A4)
C.setTitle('인천 창의디자인 사회실험 | 7개 실험실 수집·분석 다이어그램 | 2026.11.11 수정')
C.setAuthor('')
PRS = Presentation()
PRS.slide_width = Pt(W)
PRS.slide_height = Pt(H)
PRS.core_properties.title = '인천 창의디자인 사회실험 | 7개 실험실 수집·분석 다이어그램'
PRS.core_properties.author = ''
BOXES = []
ALIGNMENTS = []


def rgb(s):
    return RGBColor.from_string(s.strip('#'))


class Page:
    def __init__(self, index):
        self.index = index
        self.accent = ACCENTS[index - 1]
        self.tint = TINTS[index - 1]
        self.slide = PRS.slides.add_slide(PRS.slide_layouts[6])

    def rect(self, x, y, w, h, fill=WHITE, stroke=None, radius=0):
        C.setFillColor(HexColor(fill))
        if stroke:
            C.setStrokeColor(HexColor(stroke))
            C.setLineWidth(.55)
        if radius:
            C.roundRect(x, H-y-h, w, h, radius, fill=1, stroke=bool(stroke))
        else:
            C.rect(x, H-y-h, w, h, fill=1, stroke=bool(stroke))
        shape = self.slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                             Pt(x), Pt(y), Pt(w), Pt(h))
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(fill)
        if stroke:
            shape.line.color.rgb = rgb(stroke)
            shape.line.width = Pt(.55)
        else:
            shape.line.fill.background()
        if radius:
            shape.adjustments[0] = radius / min(w, h)

    def line(self, x1, y1, x2, y2, color=LINE, width=.6):
        C.setStrokeColor(HexColor(color))
        C.setLineWidth(width)
        C.line(x1, H-y1, x2, H-y2)
        s = self.slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Pt(x1), Pt(y1), Pt(x2), Pt(y2))
        s.line.color.rgb = rgb(color)
        s.line.width = Pt(width)

    def circle(self, x, y, r, fill, stroke=None):
        C.setFillColor(HexColor(fill))
        if stroke:
            C.setStrokeColor(HexColor(stroke))
            C.setLineWidth(.7)
        C.circle(x, H-y, r, fill=1, stroke=bool(stroke))
        s = self.slide.shapes.add_shape(MSO_SHAPE.OVAL, Pt(x-r), Pt(y-r), Pt(2*r), Pt(2*r))
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
        if stroke:
            s.line.color.rgb = rgb(stroke)
            s.line.width = Pt(.7)
        else:
            s.line.fill.background()

    def text(self, text, x, y, w, h, size=10, bold=False, color=INK,
             align='left', valign='top', leading=None):
        leading = leading or size*1.4
        style = ParagraphStyle('t', fontName='PaperB' if bold else 'Paper', fontSize=size,
                               leading=leading, wordWrap='CJK', textColor=HexColor(color),
                               alignment={'left': 0, 'center': 1, 'right': 2}[align])
        paragraph = Paragraph(escape(text).replace('\n', '<br/>'), style)
        _, ph = paragraph.wrap(w, 1000)
        if ph > h + .05:
            raise ValueError(f'Page {self.index}: text {ph:.1f} > {h:.1f}: {text}')
        yy = y + (h-ph)/2 if valign == 'middle' else y
        paragraph.drawOn(C, x, H-yy-ph)
        BOXES.append(dict(page=self.index, text=text, x=x, y=yy, w=w, h=ph, size=size))
        shape = self.slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
        tf = shape.text_frame
        tf.clear()
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE if valign == 'middle' else MSO_ANCHOR.TOP
        for i, ln in enumerate(text.split('\n')):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = ln
            p.font.name = 'Paperlogy 7 Bold' if bold else 'Paperlogy 4 Regular'
            p.font.size = Pt(size)
            p.font.bold = bold
            p.font.color.rgb = rgb(color)
            p.space_before = p.space_after = Pt(0)
            p.line_spacing = Pt(leading)
            p.alignment = {'left': PP_ALIGN.LEFT, 'center': PP_ALIGN.CENTER, 'right': PP_ALIGN.RIGHT}[align]
            for run in p.runs:
                ea = OxmlElement('a:ea')
                ea.set('typeface', p.font.name)
                run._r.get_or_add_rPr().append(ea)
        return ph

    def centered(self, text, x, y, w, h, **kw):
        ALIGNMENTS.append(dict(page=self.index, text=text, center=[x+w/2, y+h/2]))
        self.text(text, x, y, w, h, align='center', valign='middle', **kw)

    def arrow(self, x1, y1, x2, y2, color=None):
        color = color or self.accent
        self.line(x1, y1, x2, y2, color, 1)
        ang = math.atan2(y2-y1, x2-x1)
        for dt in [-.55, .55]:
            self.line(x2, y2, x2-4*math.cos(ang+dt), y2-4*math.sin(ang+dt), color, 1)


def section(p, number, label, y):
    p.text(f'{number:02}', M, y, 23, 17, 11, bold=True, color=CYAN, leading=15)
    p.text(label, M+31, y, CW-31, 17, 11, bold=True, color=p.accent, leading=15)


def header(index):
    d = DATA[index-1]
    p = Page(index)
    p.text('ACT Incheon  |  인천 창의디자인 사회실험', M, 27, 320, 13, 8.5, color=BLUE, bold=True)
    p.text('수정본  2026.11.11', W-M-128, 27, 128, 13, 8.2, color=MUTED, align='right')
    p.line(M, 47, W-M, 47, LINE, .7)
    p.text(d['category'], M, 62, CW-60, 15, 9.1, color=p.accent, bold=True)
    p.text(d['name'], M, 84, CW-55, 29, 22, bold=True, color=p.accent, leading=28)
    p.text(f'{index:02}', W-M-48, 64, 48, 43, 32, color=p.accent, align='right', leading=39)
    p.text(d['lead'], M, 123, CW, 21, 12, bold=True, leading=17)
    p.text(d['intro'], M, 153, CW, 43, 10.05, leading=14.2)
    return p, d


def footer(p, d, terminal=False):
    p.line(M, 750, W-M, 750, p.accent, .9)
    p.text(d['result'], M, 761, CW, 18, 11.6, bold=True, color=p.accent, leading=16)
    p.text(d['scope'], M, 785, CW, 14, 8.0, color=MUTED, leading=11)
    if terminal:
        p.text('관찰기록지 1·2차 및 인터뷰설문지 보완본(2026.11.11) 반영', M, 804, CW, 12,
               8.0, color=MUTED, leading=11)
        p.text('관찰 후 참여 의사 확인 · Q1 모두 / Q2 해당 행동자 / Q3·4 보관공간에 들른 짐 소지자',
               M, 819, CW, 12, 7.6, color=MUTED, leading=10)
    else:
        p.text('설문 모집 공통 기준: 최소 100명 · 문항 수×20명(5문항 기준 100명)',
               M, 804, CW, 12, 8.0, color=MUTED, leading=11)
        p.text('송도 예외: 최대 20명 · 외국인 2~3명 가능 / 설치형 카메라는 굴포천에만 설치',
               M, 819, CW, 12, 7.6, color=MUTED, leading=10)


def stage_grid(p, d):
    section(p, 2, '사전·1차·2차 수집 항목', 390)
    gap = 12
    sw = (CW-2*gap)/3
    for j, st in enumerate(d['stages']):
        x = M+j*(sw+gap)
        p.rect(x, 416, sw, 166, GRAY if j == 0 else p.tint, radius=4)
        p.text(st['title'], x+11, 427, sw-22, 15, 10.2, bold=True,
               color=MUTED if j == 0 else p.accent, leading=14)
        p.line(x+11, 450, x+sw-11, 450, LINE, .5)
        p.text(st['subtitle'], x+11, 459, sw-22, 26, 9.1, bold=True, leading=12)
        y = 493
        for item in st['items']:
            p.text('·', x+11, y, 6, 14, 9.2, bold=True, color=p.accent, leading=12.5)
            ph = p.text(item, x+20, y, sw-30, 49, 8.9, leading=12.3)
            y += ph+3.0
        if y > 544:
            raise ValueError(f'Page {p.index} stage items exceed area: {j}: {y}')
        method = st['method'].replace(' / ', '\n')
        p.text(method, x+11, 551, sw-22, 27, 7.9, color=MUTED, leading=10.8)


def analysis(p, d):
    section(p, 3, '수치·경험의 해석과 디자인 연결', 603)
    left = 300
    x = M+326
    p.text('정량·정성 함께 읽기', M, 630, left, 15, 9.1, bold=True, color=p.accent, leading=12)
    p.text(d['analysis'], M, 652, left, 88, 9.35, leading=13.6)
    p.line(M+313, 630, M+313, 734, LINE, .6)
    p.text('차후 디자인에 반영', x, 630, CW-326, 15, 9.1, bold=True, color=p.accent, leading=12)
    p.text(d['extension'], x, 652, CW-326, 88, 9.15, leading=13.2)


def comparison(p):
    section(p, 1, '같은 사진·지도 질문으로 두 디자인을 비교', 212)
    gap = 18
    sw = (CW-gap)/2
    for j, (lab, terms, cap) in enumerate([
        ('1차  색연필 수비대', ['색', '형태', '문구'], '시민안 · 인지와 위치 설명 단서'),
        ('2차  꿈꾸는 안전디자이너', ['동물', '색', '완충재'], '어린이안 · 소재와 통행 여건까지'),
    ]):
        x = M+j*(sw+gap)
        p.rect(x, 239, sw, 130, p.tint if j == 1 else GRAY, radius=5)
        p.centered(lab, x+9, 249, sw-18, 19, size=10.1, bold=True, color=p.accent, leading=14)
        for k, term in enumerate(terms):
            cx = x+sw/2+(k-1)*66
            p.circle(cx, 305, 22, WHITE, LINE)
            p.centered(term, cx-21, 283, 42, 44, size=10.4, bold=True, color=p.accent)
        p.centered(cap, x+10, 341, sw-20, 17, size=8.6, color=MUTED, leading=12)


def seonin(p):
    section(p, 1, '요소별 선호에서 조형물 경험·설치 장소로', 212)
    centers = [M+77, W/2, W-M-77]
    for j, (cx, lab, title, desc) in enumerate(zip(centers,
          ['1차  마음, 바라봄', '2차  마음, 마주봄', '설치 장소 제안'],
          ['요소별 선호', '거울나무 경험', '장소와 개선점'],
          ['색·거울·긍정 문구', '기분 변화·응원받는 느낌', '스트레스 장소·설치 희망'])):
        p.centered(lab, cx-78, 239, 156, 18, size=9.4, bold=True, color=p.accent, leading=13)
        p.circle(cx, 302, 38, p.accent if j == 1 else p.tint)
        p.centered(title, cx-37, 264, 74, 76, size=10.1, bold=True,
                   color=WHITE if j == 1 else p.accent, leading=14)
        p.centered(desc, cx-81, 349, 162, 18, size=8.5, color=MUTED, leading=12)
        if j < 2:
            p.arrow(cx+46, 302, centers[j+1]-46, 302)


def songdo(p):
    section(p, 1, '안내 표현을 달리하고, 같은 교류 행동을 관찰', 212)
    sw = (CW-18)/2
    for j, (title, subtitle) in enumerate([('1차  교류 그림 안내', '주먹 인사·하이파이브 등'),
                                         ('2차  교류 문자 안내', '같은 행동을 영문·한국어로')]):
        x = M+j*(sw+18)
        p.rect(x, 239, sw, 68, p.tint if j == 0 else GRAY, radius=5)
        p.centered(title, x+10, 250, sw-20, 20, size=12, bold=True, color=p.accent, leading=17)
        p.centered(subtitle, x+10, 279, sw-20, 16, size=9.2, color=MUTED, leading=13)
    xs = [M+48+j*(CW-96)/3 for j in range(4)]
    for j, x in enumerate(xs):
        if j < 3:
            p.arrow(x+16, 337, xs[j+1]-16, 337)
        p.circle(x, 337, 12, WHITE, p.accent)
        p.centered(str(j+1), x-12, 325, 24, 24, size=9.8, bold=True, color=p.accent, leading=13)
        p.centered(['시작점', '중간 지점 1', '중간 지점 2', '끝점'][j], x-47, 358, 94, 14,
                   size=8.7, color=MUTED, leading=12)


def chinatown(p):
    section(p, 1, '변기·휴지·청결: 표현과 컷 수를 나누어 비교', 212)
    lx = M+110
    cell = 95
    p.centered('단일형  1컷', lx, 238, cell, 22, size=9.8, bold=True, color=p.accent)
    p.centered('연속형  3컷', lx+cell+8, 238, cell, 22, size=9.8, bold=True, color=p.accent)
    for j, title in enumerate(['1차  권유형', '2차  금지형']):
        yy = 270+j*49
        p.centered(title, M, yy, 100, 40, size=10.5, bold=True, color=p.accent)
        for k in range(2):
            xx = lx+k*(cell+8)
            p.rect(xx, yy, cell, 40, p.tint if j == 0 else GRAY, radius=3)
            # The tiny frame diagram represents composition rather than fabricated content.
            n = 1 if k == 0 else 3
            width = 19 if n == 3 else 31
            span = n*width+(n-1)*5
            start = xx+(cell-span)/2
            for f in range(n):
                p.rect(start+f*(width+5), yy+10, width, 20, WHITE, stroke=p.accent, radius=1)
    xx = M+346
    p.arrow(M+315, 313, xx-10, 313)
    p.rect(xx, 270, CW-346, 89, p.accent, radius=4)
    p.centered('선택 수·비율\n이해도·경각심\n5점 평가', xx+8, 278, CW-362, 73,
               size=10.1, bold=True, color=WHITE, leading=17)


def gulpo(p):
    section(p, 1, '하드웨어 유지 + 맞은편 프로그램 운영', 212)
    centers = [M+73, W/2, W-M-73]
    for j, (cx, title, desc) in enumerate(zip(centers,
          ['1차  하드웨어', '2차  소프트웨어', '이용·체류 비교'],
          ['그늘·자리·오감 요소', '맞은편 스툴 꾸미기', '프로그램 전·중·후'])):
        p.circle(cx, 289, 42, p.tint if j < 2 else p.accent)
        p.centered(title, cx-40, 247, 80, 84, size=10.1, bold=True,
                   color=p.accent if j < 2 else WHITE, leading=15)
        p.centered(desc, cx-82, 338, 164, 17, size=8.7, color=MUTED, leading=12)
    p.centered('+', centers[0]+49, 272, centers[1]-centers[0]-98, 34,
               size=20, color=p.accent, leading=25)
    p.arrow(centers[1]+50, 289, centers[2]-50, 289)
    p.centered('촬영: 담장 위 좌·우 각 1곳 / 하단부는 줌아웃 한계로 스마트폰 촬영',
               M, 363, CW, 15, size=8.5, color=MUTED, leading=12)


def rodeo(p):
    section(p, 1, '공간 조성에서 안내사인 추가로 이어지는 실험', 212)
    for j, (lab, title, sub, outcome) in enumerate([
        ('1차', '거리 바이오필릭 + 광장 흡연공간', '비흡연·휴식 공간과 흡연공간 조성', '거리 흡연자 수\n광장 안·밖 흡연 인원'),
        ('2차', '1차 환경 유지 + 안내사인 추가', '1분·30초·15초 거리·방향 안내', '사인 인지·공간 유도\n흡연 위치·인원 변화'),
    ]):
        y = 242+j*68
        p.circle(M+23, y+26, 21, p.accent if j == 1 else p.tint)
        p.centered(lab, M+2, y+5, 42, 42, size=10.5, bold=True,
                   color=WHITE if j == 1 else p.accent)
        p.text(title, M+57, y+5, 250, 20, 10.2, bold=True, color=p.accent, leading=15)
        p.text(sub, M+57, y+31, 250, 17, 8.7, color=MUTED, leading=12)
        p.arrow(M+304, y+26, M+327, y+26)
        p.rect(M+339, y, CW-339, 53, p.tint, radius=4)
        p.centered(outcome, M+348, y+5, CW-357, 43, size=9.3, bold=True,
                   color=p.accent, leading=14)


for idx, diagram in enumerate([comparison, seonin, songdo, chinatown, gulpo, rodeo], 1):
    p, d = header(idx)
    diagram(p)
    stage_grid(p, d)
    analysis(p, d)
    footer(p, d)
    C.showPage()


# Terminal page: intervention, observable behaviour, short interview, interpretation.
p, d = header(7)
section(p, 1, '1차 안내를 유지하고, 2차에 짐 정리 편의 추가', 212)
sw = (CW-18)/2
for j, (title, subtitle) in enumerate([('1차  발걸음은 가볍게', '주요 시설 통합 바닥 안내'),
                                      ('2차  두 손은 자유롭게', '기존 안내 + 보관·정리공간')]):
    xx = M+j*(sw+18)
    p.rect(xx, 238, sw, 53, p.tint if j == 1 else GRAY, radius=4)
    p.centered(title, xx+8, 245, sw-16, 18, size=10.6, bold=True, color=p.accent, leading=15)
    p.centered(subtitle, xx+8, 269, sw-16, 15, size=8.9, color=MUTED, leading=12)

section(p, 2, '정량: 1·2차 모두 같은 A·B·C 사람 수 기록', 310)
gap = 22
sw = (CW-2*gap)/3
for j, (letter, label, body) in enumerate([
    ('A', '입장 구간', '유도 방향으로\n간 사람 수'),
    ('B', '이동 구간', '유도선을 따라\n간 사람 수'),
    ('C', '보관공간', '짐을 둔 사람 수'),
]):
    xx = M+j*(sw+gap)
    p.rect(xx, 338, sw, 99, p.tint, radius=4)
    p.circle(xx+sw/2, 357, 12, p.accent)
    p.centered(letter, xx+sw/2-12, 345, 24, 24, size=11, bold=True, color=WHITE, leading=14)
    p.centered(label, xx+9, 378, sw-18, 18, size=10.4, bold=True, color=p.accent, leading=15)
    p.centered(body, xx+7, 402, sw-14, 29 if j < 2 else 14, size=9.3, leading=13)
    if j == 2:
        p.centered('밖  /  안', xx+10, 418, sw-20, 16, size=9.6, bold=True, color=p.accent, leading=13)
    if j < 2:
        p.arrow(xx+sw+4, 388, xx+sw+gap-4, 388)
p.text('07:30~15:00 · 30분 단위 · 같은 코스·관찰 지점·짐 안팎 경계', M, 448, CW, 15,
       9.2, bold=True, color=p.accent, leading=13)
p.text('각 단계에서 같은 사람은 한 번만 센다. C는 짐 개수가 아닌 사람 수이며 처음 둔 위치로 구분한다.\n'
       '관찰했으나 없으면 0, 보지 못한 칸은 공란. 중간 합류·관찰 누락·짐 이동은 짧게 메모한다.',
       M, 472, CW, 30, 8.9, leading=13)

section(p, 3, '정성: 공통 인터뷰 4문항으로 행동의 이유 확인', 519)
qgap = 14
qw = (CW-qgap)/2
questions = [
    ('1', '처음에 방향을 바로 알았나요?', '모두 · 방향을 정할 때 본 단서'),
    ('2', '망설이거나 되돌아간 이유는?', '보관공간 앞에서 돌아갔다면 원래 일의 완료도 확인'),
    ('3', '짐을 그 자리에 둔 이유는?', '보관공간의 짐 소지자 · 배치·미이용·이동 이유'),
    ('4', '불편하거나 망설였던 점은?', '안쪽 이용자 포함 · 밖·미이용자는 안쪽 인지 확인'),
]
for i, (num, title, sub) in enumerate(questions):
    xx = M+(i%2)*(qw+qgap)
    yy = 546+(i//2)*58
    p.rect(xx, yy, qw, 49, GRAY, radius=3)
    p.circle(xx+16, yy+17, 8, p.accent)
    p.centered(num, xx+8, yy+9, 16, 16, size=8.5, bold=True, color=WHITE, leading=11)
    p.text(title, xx+31, yy+10, qw-40, 16, 9.4, bold=True, leading=13)
    p.text(sub, xx+12, yy+31, qw-24, 13, 7.8, color=MUTED, leading=10.5)

p.line(M, 668, W-M, 668, LINE, .6)
p.text('분석 → 디자인 반영', M, 679, 116, 16, 9.6, bold=True, color=p.accent, leading=13)
p.text('시간대별 A·B·C 인원과 C 밖/안 분포를 1·2차 비교하고, 인터뷰 이유를 안내 위치·연결 및 보관공간 경계·배치의 개선으로 연결한다.',
       M+127, 679, CW-127, 29, 9.1, leading=13)
p.text('단계별 인원 차이는 중간 합류·관찰 누락을 함께 살피며 해석한다. 개별 이용자의 이탈로 단정하지 않는다.',
       M, 722, CW, 13, 8.2, color=MUTED, leading=11.5)
footer(p, d, terminal=True)
C.showPage()
C.save()
PRS.save(WORK / PPTX_NAME)

# Verify generated text, geometry, vector output and editable slide structure.
pdf = fitz.open(WORK / PDF_NAME)
assert len(pdf) == 7 and len(PRS.slides) == 7
required = {
    1: ['사진·지도', '동물', '완충재', '워크숍', '556명', '35명'],
    2: ['심리치료', '응원받는 느낌', '스트레스를 가장 많이 받는 장소', '설치 희망 장소'],
    3: ['교류 행동', '주먹 인사', '하이파이브', '치얼업', '보조 기능', '4개 관찰 지점', '한국인'],
    4: ['권유형', '금지형', '1컷', '3컷', '5점', '인터뷰'],
    5: ['맞은편', '줌아웃', '스마트폰 촬영', '좌·우 각 1곳', '하드웨어 이용', '전·중·후'],
    6: ['바이오필릭', '로데오광장', '안쪽·바깥쪽', '답답함', '호기심', '높이의 적정성', '추가 질문'],
    7: ['30분 단위', '07:30~15:00', '유도 방향으로', '유도선을 따라', '짐을 둔 사람 수', '밖 / 안',
        '공통 인터뷰 4문항', '처음 둔 위치', '짐 개수가 아닌 사람 수', '공란', '중간 합류', '참여 의사'],
}
for i, pg in enumerate(pdf, 1):
    txt = ''.join(pg.get_text().split())
    slide_txt = ''.join(''.join(sh.text.split()) for sh in PRS.slides[i-1].shapes if sh.has_text_frame)
    for term in required[i] + [DATA[i-1]['name'], '2026.11.11']:
        assert ''.join(term.split()) in txt, (i, term)
        assert ''.join(term.split()) in slide_txt, ('pptx', i, term)
    assert not pg.get_images()
    assert abs(pg.rect.width-W)<.1 and abs(pg.rect.height-H)<.1
    for b in pg.get_text('dict')['blocks']:
        for line in b.get('lines', []):
            for span in line['spans']:
                x0, y0, x1, y1 = span['bbox']
                assert M-.3 <= x0 < x1 <= W-M+.3 and 15 <= y0 < y1 <= H-10, (i, span)
    for font in pg.get_fonts():
        if 'Paperlogy' in font[3]:
            assert pdf.extract_font(font[0])[3]
terminal_text = ''.join(pdf[6].get_text().split())
for obsolete in ['길찾기정확도', '시설인지율', '탐색시간', '이동만족도', '편의만족도', '보관의향', '최소100명']:
    assert obsolete not in terminal_text, obsolete

overlaps = []
for i, a in enumerate(BOXES):
    for b in BOXES[i+1:]:
        if a['page'] != b['page']:
            continue
        dx = min(a['x']+a['w'], b['x']+b['w'])-max(a['x'], b['x'])
        dy = min(a['y']+a['h'], b['y']+b['h'])-max(a['y'], b['y'])
        if dx > .6 and dy > .6:
            overlaps.append({'page': a['page'], 'a': a['text'], 'b': b['text'], 'overlap': [dx, dy]})
assert not overlaps, overlaps

preview = WORK / '미리보기'
preview.mkdir(exist_ok=True)
sheet = Image.new('RGB', (4*440, 2*640), '#e1e5e8')
draw = ImageDraw.Draw(sheet)
for i, pg in enumerate(pdf):
    pix = pg.get_pixmap(matrix=fitz.Matrix(1.8, 1.8))
    pix.save(preview / f'{i+1:02}.png')
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    im.thumbnail((420, 598))
    x = (i%4)*440+10
    y = (i//4)*640+28
    sheet.paste(im, (x, y))
    draw.text((x, y-18), f'{i+1:02}', fill='#343e49')
sheet.save(WORK / '전체7쪽_검토.png')

sources = {}
for path in ROOT.rglob('*.pdf'):
    s = unicodedata.normalize('NFC', str(path))
    if '보완본_20261111' in s and '편집자료' not in s:
        sources[s] = hashlib.sha256(path.read_bytes()).hexdigest()
assert len(sources) == 3
verification = {
    'date': '2026-11-11', 'pages': 7, 'editable_slides': 7, 'format': 'A4 portrait',
    'font': 'Paperlogy (embedded in PDF)', 'reference': '정말 최종_인천시_심의도서보완.pdf, PDF pages 40 onwards',
    'source_pdfs': sources, 'text_box_overlaps': overlaps, 'centered_text_groups': len(ALIGNMENTS),
    'vector_only': True, 'pdf_sha256': hashlib.sha256((WORK / PDF_NAME).read_bytes()).hexdigest(),
    'pptx_sha256': hashlib.sha256((WORK / PPTX_NAME).read_bytes()).hexdigest(),
}
(WORK / 'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2)+'\n')
(WORK / 'alignment.json').write_text(json.dumps(ALIGNMENTS, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(verification, ensure_ascii=False, indent=2))
print('Staged for visual inspection:', WORK / PDF_NAME)
