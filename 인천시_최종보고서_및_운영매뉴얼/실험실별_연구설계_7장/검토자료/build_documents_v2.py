from pathlib import Path
import json
from html import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE = Path(__file__).resolve().parent
OUT = BASE.parent
DATA = json.loads((BASE / 'content.json').read_text())
FONT_DIR = Path('/Users/chokogamja/Library/Fonts')
pdfmetrics.registerFont(TTFont('Ko', str(FONT_DIR / 'KoPubWorld Dotum Medium.ttf')))
pdfmetrics.registerFont(TTFont('KoB', str(FONT_DIR / 'KoPubWorld Dotum Bold.ttf')))
pdfmetrics.registerFontFamily('Ko', normal='Ko', bold='KoB')
NAVY = '#19394B'
TEAL = '#087D80'
MUTED = '#54636B'
PALE = '#F0F6F6'
GREY = '#D5DFE2'
W, H = A4
M = 45.4
CW = W - 2*M

def style(size=10.1, leading=15.6, **kwargs):
    return ParagraphStyle('p', fontName='Ko', fontSize=size, leading=leading,
                          textColor=colors.HexColor(NAVY), wordWrap='CJK', **kwargs)

def para(c, text, y, sty=None, x=M, width=CW):
    p = Paragraph(text, sty or style())
    _, height = p.wrap(width, H)
    p.drawOn(c, x, y-height)
    return y-height

def section(c, number, title, y):
    y -= 9
    y = para(c, f'<font color="{TEAL}">{number}</font>  <b>{title}</b>', y,
             style(10.5, 15.5))
    return y-4

pdf_path = OUT / '인천시_7개_실험실_사전1차2차비교_A4_수정본.pdf'
c = canvas.Canvas(str(pdf_path), pagesize=A4)
c.setTitle('인천 창의디자인 사회실험 | 7개 실험실 연구설계 보완안')
c.setAuthor('인천 창의디자인 사회실험 연구설계')
heights=[]
for i,d in enumerate(DATA,1):
    c.setFillColor(colors.HexColor(TEAL))
    c.rect(M,H-33,26,3,fill=1,stroke=0)
    para(c, '인천 창의디자인 사회실험  /  실험실별 연구설계 보완안', H-41, style(8.2,11))
    c.setFillColor(colors.HexColor(TEAL))
    c.setFont('KoB',30)
    c.drawRightString(W-M,H-72,f'{i:02d}')
    y=para(c,escape(d['name']),H-66,
           ParagraphStyle('title',fontName='KoB',fontSize=21,leading=28,textColor=colors.HexColor(NAVY),wordWrap='CJK'),width=CW-48)
    y=para(c,escape(d['theme']),y-4,
           ParagraphStyle('sub',fontName='Ko',fontSize=10.4,leading=15,textColor=colors.HexColor(MUTED),wordWrap='CJK'))
    y-=12
    q=Paragraph('<b>'+escape(d['question'])+'</b>',style(11,16))
    _,qh=q.wrap(CW-20,H)
    c.setFillColor(colors.HexColor(PALE))
    c.roundRect(M,y-qh-17,CW,qh+17,4,fill=1,stroke=0)
    q.drawOn(c,M+10,y-qh-8)
    y-=qh+22
    y=section(c,'01','실험배경',y)
    y=para(c,escape(d['background']),y)
    y=section(c,'02','어떤 실험을 하는가',y)
    y=para(c,escape(d['experiment']),y)
    y=section(c,'03','사전 | 1차 | 2차 수집 항목과 비교 범위',y)
    y=para(c,'<b>사전자료 상태</b>  '+escape(d['baseline']),y,style(9.3,13.5))
    y-=5
    rows=[[Paragraph('<b>'+s+'</b>',style(9.4,13)) for s in ['수집 항목','사전','1차','2차']]]
    rows += [[Paragraph(('<b>' if j==0 else '')+escape(s).replace('\n','<br/>')+('</b>' if j==0 else ''),style(9.2,13.2)) for j,s in enumerate(row)] for row in d['matrix']]
    t=Table(rows,colWidths=[69,(CW-69)/3,(CW-69)/3,(CW-69)/3])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor(PALE)),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LINEBELOW',(0,0),(-1,0),.65,colors.HexColor(TEAL)),
        ('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor(GREY)),
    ]))
    _,th=t.wrap(CW,H)
    t.drawOn(c,M,y-th);y-=th
    y=para(c,'<b>비교 범위</b>  '+escape(d['comparison']),y-6,style(9.3,13.5))
    y=section(c,'04','통계분석과 인터뷰를 어떻게 연결하는가',y)
    y=para(c,'<b>통계분석</b>  '+escape(d['stats']),y)
    y=para(c,'<b>인터뷰·통합 해석</b>  '+escape(d['interview']),y-5)
    y=section(c,'05','향후 디자인에 확장할 요소',y)
    y=para(c,escape(d['design']),y)
    y=para(c,'<b>해석·후속 실험</b>  '+escape(d['limit']),y-7,style(9.3,13.6))
    heights.append((d['name'],round(y,1)))
    if y<78:
        raise RuntimeError(f'Page overflow: {d["name"]}, bottom={y}')
    c.setStrokeColor(colors.HexColor(GREY));c.setLineWidth(.5)
    c.line(M,66,W-M,66)
    para(c,'근거: 「정말 최종_인천시_심의도서보완.pdf」 '+escape(d['source']),59,style(7.1,10))
    para(c,'표는 원문 계획 기준. 일정 기재는 완료·원자료 확보를 뜻하지 않음. [보완]은 추가 제안이며, 미확인·미수집·비해당을 구분해 확정.',47,style(7.1,10))
    c.setFont('KoB',8);c.setFillColor(colors.HexColor(TEAL));c.drawRightString(W-M,27,f'{i} / 7')
    c.showPage()
c.save()

doc=Document()
sec=doc.sections[0]
sec.page_width=Mm(210);sec.page_height=Mm(297)
sec.top_margin=Mm(14);sec.bottom_margin=Mm(14)
sec.left_margin=Mm(16);sec.right_margin=Mm(16)
sec.header_distance=Mm(6);sec.footer_distance=Mm(7)
normal=doc.styles['Normal']
normal.font.name='KoPubWorld돋움체 Medium';normal.font.size=Pt(10)
normal.font.color.rgb=RGBColor.from_string('19394B')
normal.element.rPr.rFonts.set(qn('w:eastAsia'),'KoPubWorld돋움체 Medium')
normal.paragraph_format.space_after=Pt(4)
normal.paragraph_format.line_spacing=1.15
for name,size in [('Title',20),('Subtitle',10.5),('Heading 1',10.6)]:
    s=doc.styles[name];s.font.name='KoPubWorld돋움체 Bold';s.font.size=Pt(size)
    s.font.color.rgb=RGBColor.from_string('087D80' if name=='Heading 1' else '19394B')
    s.element.rPr.rFonts.set(qn('w:eastAsia'),'KoPubWorld돋움체 Bold')
    s.paragraph_format.space_before=Pt(7 if name=='Heading 1' else 0)
    s.paragraph_format.space_after=Pt(4)
    s.paragraph_format.keep_with_next=True

def addp(text,bold_prefix=None):
    p=doc.add_paragraph()
    if bold_prefix:
        p.add_run(bold_prefix+'  ').bold=True
    p.add_run(text)
    return p

for i,d in enumerate(DATA,1):
    if i>1:doc.add_page_break()
    p=addp(f'인천 창의디자인 사회실험  /  연구설계 보완안                                      {i:02d} / 07')
    for r in p.runs:r.font.size=Pt(8)
    doc.add_paragraph(d['name'],'Title')
    doc.add_paragraph(d['theme'],'Subtitle')
    p=addp(d['question']);p.runs[0].bold=True
    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'F0F6F6');p._p.get_or_add_pPr().append(shade)
    for h,key in [('01  실험배경','background'),('02  어떤 실험을 하는가','experiment')]:
        doc.add_paragraph(h,'Heading 1');addp(d[key])
    doc.add_paragraph('03  사전 | 1차 | 2차 수집 항목과 비교 범위','Heading 1')
    p=addp(d['baseline'],'사전자료 상태')
    for run in p.runs:run.font.size=Pt(9.3)
    table=doc.add_table(rows=1, cols=4)
    table.autofit=False
    table.columns[0].width=Mm(24)
    for j in range(1,4):table.columns[j].width=Mm(51.3)
    for cell,s in zip(table.rows[0].cells,['수집 항목','사전','1차','2차']):cell.text=s
    for row in d['matrix']:
        for cell,s in zip(table.add_row().cells,row):cell.text=s
    for ri,row in enumerate(table.rows):
        trPr=row._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trPr.append(cant)
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_before=Pt(2);p.paragraph_format.space_after=Pt(3)
                for run in p.runs:run.font.size=Pt(9);run.bold=ri==0
            if ri==0:
                s=OxmlElement('w:shd');s.set(qn('w:fill'),'F0F6F6');cell._tc.get_or_add_tcPr().append(s)
    p=addp(d['comparison'],'비교 범위')
    for run in p.runs:run.font.size=Pt(9.3)
    doc.add_paragraph('04  통계분석과 인터뷰를 어떻게 연결하는가','Heading 1')
    addp(d['stats'],'통계분석');addp(d['interview'],'인터뷰·통합 해석')
    doc.add_paragraph('05  향후 디자인에 확장할 요소','Heading 1')
    addp(d['design'])
    p=addp(d['limit'],'해석·후속 실험')
    for r in p.runs:r.font.size=Pt(9)
    p=addp('근거: 「정말 최종_인천시_심의도서보완.pdf」 '+d['source'])
    p.paragraph_format.space_before=Pt(5)
    for r in p.runs:r.font.size=Pt(7)
footer=sec.footer.paragraphs[0]
footer.text='원문 계획 기준 · 일정 기재는 완료·원자료 확보를 뜻하지 않음 · [보완]은 추가 제안 · 미확인·미수집·비해당 구분'
for r in footer.runs:r.font.size=Pt(7)
doc_path=OUT/'인천시_7개_실험실_사전1차2차비교_A4_수정본.docx'
doc.save(doc_path)
print('PDF:',pdf_path)
print('DOCX:',doc_path)
print('Content bottom positions:',heights)

# Reopen the final PDF to check dimensions, content and page count.
import fitz
pdf=fitz.open(pdf_path)
assert len(pdf)==7
for pg,d in zip(pdf,DATA):
    assert abs(pg.rect.width-W)<.1 and abs(pg.rect.height-H)<.1
    assert d['name'] in pg.get_text()
    assert '향후 디자인에 확장할 요소' in pg.get_text()
    assert '사전자료 상태' in pg.get_text()
    assert '비교 범위' in pg.get_text()
    pg.get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(str(BASE/f'완성본_{pg.number+1}쪽.png'))
print('Verified: 7 A4 portrait pages, all seven laboratory names and final sections present.')
