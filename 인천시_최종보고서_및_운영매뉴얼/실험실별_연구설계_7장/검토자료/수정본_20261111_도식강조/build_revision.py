"""2026-11-11: large central diagrams, quiet light-gray supporting notes.

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
M = 40
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

# Audit the wording and the roles of conditions, observations and design feedback.
DATA[0].update(
    lead='시설물을 알아보고, 위치를 설명할 수 있을까',
    intro='학교 경계가 잘 보이지 않고 통학로가 좁은 여건에서 시설물을 알아보고 위치를 설명하는 단서를 살핀다. '
          '시민안의 색·형태·문구와 어린이안의 동물·색·완충재를 적용한 뒤, 같은 사진·지도 질문으로 반응을 비교한다.',
    analysis='1·2차에 같은 사진·지도 문항을 사용해 시설물 인지 응답 비율과 위치 정답률을 비교한다. '
             '인터뷰에서는 위치를 설명할 때 색·문구·동물을 어떻게 활용하는지 확인하고, 어린이 워크숍의 제안과 함께 해석한다.',
    extension='어린이의 제안을 반영한 동물 5종·배경색·EVA 스펀지를 검토한다. '
              '위치 설명에 도움이 된 단서와 통행 불편을 바탕으로 표현·소재·설치 위치를 다듬는다.',
)
DATA[0]['stages'][2]['items'] = ['시설물 인지·위치 정답률', '위치 설명에 쓴 동물·색', '동물 식별·소재·통행 불편']
DATA[1].update(
    lead='1차 선호를 거울나무에 반영하고, 2차 사용 경험을 묻다',
    intro='심리치료에서 활용되는 요소의 맥락을 참고해 색·거울·긍정 문구에 대한 학생의 선호를 묻는다. '
          '1차 응답을 반영한 거울나무를 2차에 설치하고, 기분 변화·응원받는 느낌과 설치 희망 장소를 확인한다.',
    analysis='1차는 요소별 선호 응답을, 2차는 기분 변화·응원받는 느낌·설치 희망 장소의 응답을 각각 집계한다. '
             '이용 인원·체류시간과 인터뷰에서 나온 선택·평가 이유를 함께 살핀다.',
    extension='선호한 요소가 거울나무 전체에서 어떻게 경험됐는지 확인한다. '
              '스트레스를 가장 많이 받는 장소와 설치 희망 장소에 관한 의견으로 색·문구·거울 높이·설치 위치를 검토한다.',
)
DATA[1]['stages'][0]['subtitle'] = '설치 여건·통행량 확인'
DATA[1]['stages'][2]['items'] = ['기분 변화·응원받는 느낌', '설치 희망 장소·그 이유']
DATA[2].update(
    analysis='그림 안내와 문자 안내 중 무엇이 기억에 남고, 부담이 적고, 교류에 도움이 됐는지 설문으로 비교한다. '
             '4개 관찰 지점에서 실제 교류 행동의 횟수·비율을 기록하고, 인터뷰로 응답 이유를 확인한다.',
    extension='한국인과 외국인의 반응을 함께 살펴 안내 표현을 다듬는다. '
              '시작점의 헬로를 주먹 인사 픽토그램으로 바꾸는 등, 기억·부담·실제 행동을 근거로 개선한다.',
)
for stage in DATA[2]['stages'][1:]:
    stage['items'][1] = '부담 정도·교류 도움'
DATA[3].update(
    intro='다국어 안내가 부족한 공중화장실에서 에티켓 그림의 표현과 구성을 살핀다. '
          '1차 권유형, 2차 금지형 각각에서 같은 3개 주제의 1컷·3컷을 비교하고, 선택 이유와 그림의 의미를 묻는다.',
    analysis='각 차수에서 1컷·3컷의 선택 수·비율과 이해도·경각심의 5점 응답을 비교한다. '
             '스티커 설문 뒤 심층 인터뷰로 선택 이유와 그림 해석을 수집해, 선호와 의미 이해의 관계를 살핀다.',
    extension='권유·금지 표현과 1컷·3컷 구성별로 이해를 돕거나 혼동을 준 부분을 정리한다. '
              '선택 이유와 개선 의견을 에티켓 픽토그램의 표현·구성에 반영한다.',
)
DATA[3]['stages'][0]['items'][1] = '다국어 안내 부족'
DATA[4].update(
    lead='맞은편 프로그램을 운영하면 휴게시설 이용이 달라질까',
    intro='1차는 그늘과 앉을 자리 등 휴게시설만 운영한다. 2차는 같은 시설을 유지하면서 맞은편에서 시민·청년작가의 스툴 꾸미기 프로그램을 운영한다. '
          '휴게시설 이용과 체류를 1·2차 비교하고, 2차 프로그램 운영 전·중·후의 변화도 살핀다.',
    analysis='1·2차의 휴게시설 이용 인원·비율, 멈춤률·체류시간을 같은 기준으로 비교한다. '
             '2차 기록은 프로그램 운영 전·중·후로 나눠, 맞은편 프로그램 운영 중 시설 이용과 체류가 어떻게 달라지는지 확인한다.',
    extension='시민·작가 인터뷰로 머무는 이유와 프로그램 참여·휴게시설 이용의 관계를 묻는다. '
              '관찰 기록과 응답 이유를 바탕으로 시설·프로그램의 배치와 운영 방식을 검토한다.',
    quant_title='휴게시설 이용과 체류의 1·2차 비교',
    quant_body='시설만 운영한 1차와 같은 시설·맞은편 프로그램을 운영한 2차를 비교',
    combine='같은 휴게시설의 이용·체류를 비교하고 2차 운영 전·중·후를 구분해 해석',
)
DATA[4]['stages'][1]['items'] = ['휴게시설 이용 인원·비율', '멈춤률·체류시간']
DATA[4]['stages'][2]['items'] = ['같은 휴게시설의 이용·체류', '프로그램 운영 전·중·후 기록']
DATA[5].update(
    lead='같은 공간에 안내사인을 더하면 흡연 위치가 달라질까',
    intro='1차는 로데오거리를 바이오필릭 휴식 공간으로 꾸미고, 로데오광장에 흡연공간을 조성한다. '
          '2차는 같은 공간에 안내사인을 추가한다. 사전·1차·2차의 흡연 위치·인원을 비교하고, 2차에는 사인 인지와 이동 반응도 확인한다.',
    analysis='사전·1차·2차의 거리 흡연자 수와 광장 흡연공간 안쪽·바깥쪽 흡연 인원을 같은 시간·구간에서 비교한다. '
             '설문으로 공간의 답답함, 높이의 적정성, 디자인에 대한 호기심·관심으로 들어왔는지를 묻는다.',
    extension='답답함·높이 평가의 이유, 디자인을 보고 들어온 계기, 흡연공간 이용·기피 이유를 추가 질문으로 확인한다. '
              '응답과 관찰 결과를 거리·광장 배치 및 시설물·사인 개선에 반영한다.',
)
DATA[5]['stages'][0]['items'][1] = '보행·휴식·흡연 동선'
DATA[5]['stages'][1]['items'] = ['거리 흡연자 수', '광장 흡연공간 안·밖 인원']
DATA[5]['stages'][2]['items'] = ['같은 구간의 흡연 위치·인원', '사인 인지·흡연공간으로 이동']

# Match the actual simplified observation forms and the common four-question interview.
d = DATA[6]
d.update(
    lead='안내를 따라간 사람과 짐을 둔 사람을 세고, 이유를 묻다',
    intro='1층 대합실에서 1차 통합 바닥 안내를 유지하고 2차 보관·정리공간을 더한다. '
          '같은 코스에서 관찰 위치별로 사람 수를 기록하고, 짧은 인터뷰로 방향 판단과 짐을 두거나 두지 않은 이유를 확인한다.',
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

    def ellipse(self, x, y, rx, ry, fill):
        C.setFillColor(HexColor(fill))
        C.ellipse(x-rx, H-y-ry, x+rx, H-y+ry, fill=1, stroke=0)
        s = self.slide.shapes.add_shape(MSO_SHAPE.OVAL, Pt(x-rx), Pt(y-ry), Pt(rx*2), Pt(ry*2))
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
        s.line.fill.background()

    def curve(self, pts, color, width=.8):
        # Cubic Bezier, with a sampled editable polyline in the PowerPoint.
        a, b, cc, d = pts
        C.setStrokeColor(HexColor(color)); C.setLineWidth(width)
        path = C.beginPath(); path.moveTo(a[0], H-a[1])
        path.curveTo(b[0], H-b[1], cc[0], H-cc[1], d[0], H-d[1])
        C.drawPath(path, stroke=1, fill=0)
        prev = a
        for i in range(1, 25):
            t = i/24
            x = (1-t)**3*a[0]+3*(1-t)**2*t*b[0]+3*(1-t)*t*t*cc[0]+t**3*d[0]
            y = (1-t)**3*a[1]+3*(1-t)**2*t*b[1]+3*(1-t)*t*t*cc[1]+t**3*d[1]
            s = self.slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Pt(prev[0]), Pt(prev[1]), Pt(x), Pt(y))
            s.line.color.rgb = rgb(color); s.line.width = Pt(width)
            prev = (x, y)

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
        self.line(x1, y1, x2, y2, color, 1.35)
        ang = math.atan2(y2-y1, x2-x1)
        for dt in [-.55, .55]:
            self.line(x2, y2, x2-5*math.cos(ang+dt), y2-5*math.sin(ang+dt), color, 1.35)


def section(p, number, label, y):
    p.text(label, M, y, CW, 17, 9.4, bold=True, color=MUTED, leading=13)


def header(index):
    d = DATA[index-1]
    p = Page(index)
    p.text('ACT Incheon  |  인천 창의디자인 사회실험', M, 24, 320, 13, 8.3, color=BLUE, bold=True)
    p.text('수정본  2026.11.11', W-M-128, 24, 128, 13, 7.9, color=MUTED, align='right')
    p.text(d['category'], M, 53, CW-60, 15, 8.7, color=p.accent, bold=True)
    p.text(d['name'], M, 75, CW-55, 29, 22, bold=True, color=INK, leading=28)
    p.text(f'{index:02}', W-M-48, 53, 48, 43, 30, color='#A9BAC6', align='right', leading=39)
    p.text(d['lead'], M, 113, CW, 21, 11.5, bold=True, leading=16)
    p.text(d['intro'], M, 141, CW, 40, 9.6, leading=13.2)
    return p, d


def footer(p, d, terminal=False):
    p.rect(M-9, 770, CW+18, 62, '#F3F4F5')
    p.text('도출 방향', M, 780, 43, 10, 6.9, color=MUTED, leading=9)
    p.text(d['result'], M+49, 777, CW-49, 14, 8.7, bold=True, color='#596771', leading=12)
    p.text(d['scope'], M, 797, CW, 10, 7.0, color=MUTED, leading=9.3)
    if terminal:
        p.text('관찰기록지 1·2차 및 인터뷰설문지 보완본(2026.11.11) 반영', M, 809, CW, 10,
               7.0, color=MUTED, leading=9.3)
        p.text('관찰 후 참여 의사 확인 · Q1 모두 / Q2 해당 행동자 / Q3·4 보관공간에 들른 짐 소지자',
               M, 821, CW, 10, 6.7, color=MUTED, leading=9)
    else:
        rule = ('공통 설문 모집 기준의 예외: 송도 총 참여자 최대 20명 · 외국인 2~3명 가능' if p.index == 3 else
                '설문 모집 공통 기준: 최소 100명 · 문항 수×20명(5문항 기준 100명)')
        p.text(rule,
               M, 809, CW, 10, 7.0, color=MUTED, leading=9.3)
        notes = {
            1: '설문 응답과 어린이 워크숍 참여는 별도로 집계',
            2: '1차 선호 응답과 2차 경험 응답은 문항별로 구분하여 해석',
            3: '시작점·끝점 포함 4개 지점 관찰 · 한국인과 외국인의 응답을 함께 수집',
            4: '1·2차에 같은 3개 주제·설문 문항·5점 척도 사용',
            5: '촬영: 담장 위 좌·우 각 1곳 / 하단부는 카메라 줌아웃 한계로 스마트폰 촬영',
            6: '사전·1차·2차 관찰은 같은 시간·구간을 기준으로 기록',
        }
        p.text(notes[p.index],
               M, 821, CW, 10, 6.7, color=MUTED, leading=9)


def stage_grid(p, d):
    gap = 24
    sw = (CW-2*gap)/3
    for j, st in enumerate(d['stages']):
        x = M+j*(sw+gap)
        p.text(st['title'], x, 515, sw, 14, 8.7, bold=True,
               color=MUTED if j == 0 else p.accent, leading=12)
        p.text(st['subtitle'], x, 536, sw, 25, 9.2, bold=True, leading=12)
        y = 570
        for item in st['items']:
            p.text('·', x, y, 6, 13, 8.5, bold=True, color=p.accent, leading=11.4)
            ph = p.text(item, x+9, y, sw-9, 43, 8.2, leading=11.4)
            y += ph+2.5
        if y > 615:
            raise ValueError(f'Page {p.index} stage items exceed area: {j}: {y}')
        method = st['method'].replace(' / ', '\n')
        p.text(method, x, 622, sw, 22, 7.3, color=MUTED, leading=9.8)


def analysis(p, d):
    left = 292
    x = M+318
    p.text('수치 비교와 응답 이유 해석', M, 662, left, 14, 8.8, bold=True, color=p.accent, leading=12)
    p.text(d['analysis'], M, 684, left, 77, 8.55, leading=11.8)
    p.text('디자인에 반영할 점', x, 662, CW-318, 14, 8.8, bold=True, color=p.accent, leading=12)
    p.text(d['extension'], x, 684, CW-318, 77, 8.35, leading=11.4)


from bold_diagrams import draw as draw_editorial_diagram

for idx in range(1, 7):
    p, d = header(idx)
    draw_editorial_diagram(p, idx, M=M, CW=CW, W=W, INK=INK, MUTED=MUTED, WHITE=WHITE)
    stage_grid(p, d)
    analysis(p, d)
    footer(p, d)
    C.showPage()


# Terminal page: intervention, observable behaviour, short interview, interpretation.
p, d = header(7)
section(p, 1, '1차 안내를 유지하고, 2차에 짐 정리 편의 추가', 192)
sw = (CW-18)/2
for j, (title, subtitle) in enumerate([('1차  발걸음은 가볍게', '주요 시설 통합 바닥 안내'),
                                      ('2차  두 손은 자유롭게', '기존 안내 + 보관·정리공간')]):
    xx = M+j*(sw+18)
    p.centered(title, xx+5, 227, sw-10, 22, size=12.0, bold=True, color=p.accent, leading=17)
    p.centered(subtitle, xx+5, 256, sw-10, 18, size=9.6, color=MUTED, leading=13)

section(p, 2, '정량: A·B·C 위치별 사람 수를 1·2차 같은 기준으로 집계', 292)
gap = 22
sw = (CW-2*gap)/3
for j, (letter, label, body) in enumerate([
    ('A', '입장 구간', '유도 방향으로\n간 사람 수'),
    ('B', '이동 구간', '유도선을 따라\n간 사람 수'),
    ('C', '보관공간', '짐을 둔 사람 수'),
]):
    xx = M+j*(sw+gap)
    p.centered(letter, xx+sw/2-33, 324, 66, 54, size=43, bold=False, color=p.accent, leading=52)
    p.centered(label, xx+5, 390, sw-10, 22, size=13.1, bold=True, color=p.accent, leading=18)
    p.centered(body, xx+5, 422, sw-10, 34 if j < 2 else 18, size=10.5, leading=15)
    if j == 2:
        p.centered('밖  /  안', xx+5, 446, sw-10, 18, size=11.4, bold=True, color=p.accent, leading=16)
p.text('07:30~15:00 · 30분 단위 · 같은 코스·관찰 지점·짐 안팎 경계', M, 478, CW, 14,
       8.8, bold=True, color=p.accent, leading=12)
p.text('각 단계에서 같은 사람은 한 번만 센다. C는 짐 개수가 아닌 사람 수이며 처음 둔 위치로 구분한다.\n'
       '관찰했으나 없으면 0, 보지 못한 칸은 공란. 중간 합류·관찰 누락·짐 이동은 짧게 메모한다.',
       M, 500, CW, 28, 8.0, leading=11.6)

section(p, 3, '정성: 공통 인터뷰 4문항으로 행동의 이유 확인', 548)
qgap = 14
qw = (CW-qgap)/2
questions = [
    ('1', '처음에 방향을 바로 알았나요?', '모두에게 질문 · 방향을 정할 때 본 단서 확인'),
    ('2', '망설이거나 되돌아간 이유는?', '보관공간 앞에서 돌아갔다면, 하려던 일을 마쳤는지도 확인'),
    ('3', '짐을 그 자리에 둔 이유는?', '보관공간에 들른 짐 소지자 · 짐을 두거나 두지 않은 이유, 옮긴 이유'),
    ('4', '불편하거나 망설였던 점은?', '안쪽 이용자도 질문. 밖·미이용자는 안쪽 공간을 알고 있었는지 확인'),
]
for i, (num, title, sub) in enumerate(questions):
    xx = M+(i%2)*(qw+qgap)
    yy = 571+(i//2)*56
    p.text(num, xx, yy+3, 21, 25, 18, color=p.accent, leading=23)
    p.text(title, xx+26, yy+5, qw-26, 16, 9.1, bold=True, leading=12.8)
    p.text(sub, xx+26, yy+25, qw-26, 23, 7.5, color=MUTED, leading=10.4)

p.text('비교와 디자인 개선', M, 702, 108, 14, 8.6, bold=True, color=p.accent, leading=12)
p.text('시간대별 A·B·C 인원과 C 밖/안 인원을 1·2차 비교한다. 관찰한 행동과 응답자가 말한 이유를 함께 살펴 안내 위치·연결 방식과 보관공간 경계·배치를 다듬는다.',
       M+118, 702, CW-118, 35, 8.1, leading=11.3)
p.text('A·B·C는 지점별 집계다. 단계별 인원 차이는 중간 합류·관찰 누락을 함께 살피며 해석한다.',
       M, 749, CW, 12, 7.6, color=MUTED, leading=10.5)
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
    5: ['맞은편', '줌아웃', '스마트폰 촬영', '좌·우 각 1곳', '휴게시설 이용', '전·중·후',
        '프로그램 없음', '같은 시설 유지', '휴게시설 구역', '맞은편 프로그램 구역'],
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
    'font': 'Paperlogy (embedded in PDF)',
    'references': {
        'palette_and_font': '정말 최종_인천시_심의도서보완.pdf, PDF pages 40 onwards',
        'hierarchy_and_scale': '240724_강남공공디자인진흥계획_위원회 심의자료(전체취합)_최종_편집.pdf',
    },
    'source_pdfs': sources, 'text_box_overlaps': overlaps, 'centered_text_groups': len(ALIGNMENTS),
    'vector_only': True, 'pdf_sha256': hashlib.sha256((WORK / PDF_NAME).read_bytes()).hexdigest(),
    'pptx_sha256': hashlib.sha256((WORK / PPTX_NAME).read_bytes()).hexdigest(),
}
(WORK / 'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2)+'\n')
(WORK / 'alignment.json').write_text(json.dumps(ALIGNMENTS, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(verification, ensure_ascii=False, indent=2))
print('Staged for visual inspection:', WORK / PDF_NAME)
