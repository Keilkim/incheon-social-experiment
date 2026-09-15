# -*- coding: utf-8 -*-
"""사용자가 첨부한 월~목 시간표와 준비물을 PDF·DOCX·기존 일정 엑셀에 반영."""
from pathlib import Path
from html import escape
import 도구_공통 as C
import 조사지_제작 as M

ROOT=C.ROOT
PEOPLE={'월':'성훈, 은영, 지윤, 지유, 주호','화':'','수':'','목':'주호, 은영, 지윤, 성훈'}
SUPPLIES=[
    ('선인재단','4명','기록지 32장(4곳×8장), 클립보드 4개, 볼펜 4자루, 초 표시 시계'),
    ('굴포천','2명','삼각대 1개 + 카메라 1대(배터리·메모리카드), 기록지 8장, 폼보드 1판(600×900), 이젤, 스티커 최대 800개'),
    ('연안여객터미널','3명','2층 기록지 8장 + 1층 캐리어 시간표 1장, 좌석 배치도, 클립보드 3개, 볼펜'),
    ('로데오거리','5명','기록지 8장, 클립보드 5개, 볼펜, 초 표시 시계'),
    ('차이나타운','3명','폼보드 1판(900×600), 이젤, 그림 A·B, 그림 덮개, 스티커 최대 1,000개'),
    ('송도글로벌캠퍼스','3명','관찰 기록지 8장 + 인터뷰 기록표 2장(50명), 모집 폼 QR 안내, 클립보드, 볼펜'),
]
COMMON='공통: 여분 볼펜 · 클립보드 · 휴대폰(충전) · 집게 · 조사일/거점별 서류봉투'
NOTE='선인재단: 1번 출발 → 2~3번 중간 → 4번 도착. 기록표는 기본 200명/건, 송도 인터뷰는 50명.'


def schedule_rows():
    """(글, 열 병합, 행 병합) 목록. A 시간/B:C 월/D 화/E 수/F 목."""
    rows=[ [('구분',1,1),('월',2,1),('화',1,1),('수',1,1),('목',1,1)],
           [('인원',1,1),(PEOPLE['월'],2,1),('',1,1),('',1,1),(PEOPLE['목'],1,1)] ]
    for h in range(5,22):
        r=[(f'{h:02d}',1,1)]
        if h in (8,18):
            r.append(('선인재단 4명\n(1~4번 관찰)' if h==8 else '로데오거리 5명',2,2))
        elif h in (9,19):pass
        elif h==12:r.extend([('',1,1),('연안여객터미널\n3명',1,4)])
        elif h==13:r.append(('굴포천 2명',1,2))
        elif h==14:pass
        elif h==15:r.append(('',1,1))
        else:r.append(('',2,1))
        r.extend([('',1,1),('',1,1)])
        if h==13:r.append(('차이나타운 3명',1,2))
        elif h==18:r.append(('송도글로벌캠퍼스\n3명',1,2))
        elif h not in (14,19):r.append(('',1,1))
        rows.append(r)
    return rows


def html_schedule():
    rows=schedule_rows();out=''
    for idx,row in enumerate(rows):
        tag='th' if idx<2 else 'td'
        out+='<tr>'+''.join(f'<{tag} colspan="{cs}" rowspan="{rs}" class="{"event" if rs>1 else ""}">{escape(t).replace(chr(10),"<br>")}</{tag}>' for t,cs,rs in row)+'</tr>'
    return '<table class="schedule"><colgroup>'+''.join(f'<col style="width:{v}%">' for v in [7,18,18,15,15,27])+'</colgroup><tbody>'+out+'</tbody></table>'


CSS='''
.schedule th,.schedule td{border:1px solid #7F93A8;text-align:center;vertical-align:middle;padding:1px 3px;font-size:9pt}
.schedule tr{height:5.5mm}.schedule tr:first-child{height:6mm}.schedule tr:nth-child(2){height:8mm}
.schedule th{background:#EDF3F8;color:#153C68}.schedule td:first-child{color:#5A6B7D}
.schedule td.event{font-size:10pt;font-weight:700;color:#153C68;background:#F7FAFC}
.supplies th,.supplies td{border:1px solid #C3CFDB;font-size:8.6pt;padding:5px 6px;vertical-align:middle;line-height:1.45}
.supplies th{background:#EDF3F8;color:#153C68}.prep-title{font-size:12pt;color:#153C68;margin:9px 0 4px}
'''


def pdf():
    body=M.hd('일정','사전조사 시간표 · 준비물','월~목')+html_schedule()
    body+='<h2 class="prep-title">챙길 준비물</h2><div style="font-size:8.8pt;margin-bottom:5px">'+COMMON+'</div>'
    body+='<table class="supplies"><colgroup><col style="width:25%"><col style="width:8%"><col></colgroup><thead><tr><th>거점</th><th>인원</th><th>준비물</th></tr></thead><tbody>'
    body+=''.join('<tr>'+''.join(f'<td>{escape(t)}</td>' for t in row)+'</tr>' for row in SUPPLIES)+'</tbody></table>'
    body+='<div class="note" style="font-size:8pt">'+NOTE+'</div>'
    return C.render([body],ROOT/'00_시간표와_준비물.pdf',margin=(9,9,10,9),extra_css=M.CSS+CSS,footer='사전조사')


def docx():
    from docx import Document
    from docx.shared import Mm,Pt,RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT,WD_ROW_HEIGHT_RULE
    d=Document();sec=d.sections[0];sec.page_width=Mm(210);sec.page_height=Mm(297)
    sec.top_margin=Mm(9);sec.bottom_margin=Mm(9);sec.left_margin=Mm(9);sec.right_margin=Mm(9)
    normal=d.styles['Normal'];normal.font.name='맑은 고딕';normal.font.size=Pt(9)
    normal.element.rPr.rFonts.set(qn('w:eastAsia'),'맑은 고딕')
    normal.paragraph_format.space_after=Pt(0);normal.paragraph_format.line_spacing=1
    p=d.add_paragraph();r=p.add_run('사전조사 시간표 · 준비물');r.bold=True;r.font.size=Pt(17);r.font.color.rgb=RGBColor.from_string('153C68')
    p.paragraph_format.space_after=Pt(6)
    table=d.add_table(rows=19,cols=6);table.style='Table Grid';table.autofit=False;table.alignment=WD_TABLE_ALIGNMENT.CENTER
    widths=[13.4,34.6,34.6,28.8,28.8,51.8]
    for column,width in zip(table.columns,widths):column.width=Mm(width)
    for row in table.rows:
        row.height=Mm(5.5);row.height_rule=WD_ROW_HEIGHT_RULE.EXACTLY
        for i,cell in enumerate(row.cells):cell.width=Mm(widths[i]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    occupied=set()
    for ri,row in enumerate(schedule_rows()):
        ci=0
        for text,cs,rs in row:
            while (ri,ci) in occupied:ci+=1
            cell=table.cell(ri,ci)
            if cs>1 or rs>1:cell=cell.merge(table.cell(ri+rs-1,ci+cs-1))
            cell.text=text
            for para in cell.paragraphs:
                para.alignment=WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:run.font.size=Pt(9);run.bold=ri<2 or rs>1
            if ri<2 or rs>1:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EDF3F8' if ri<2 else 'F7FAFC');cell._tc.get_or_add_tcPr().append(sh)
            for rr in range(ri,ri+rs):
                for cc in range(ci,ci+cs):occupied.add((rr,cc))
            ci+=cs
    table.rows[0].height=Mm(6);table.rows[1].height=Mm(8)
    p=d.add_paragraph();p.paragraph_format.space_before=Pt(7);p.paragraph_format.space_after=Pt(4)
    r=p.add_run('챙길 준비물');r.bold=True;r.font.size=Pt(12)
    d.add_paragraph(COMMON)
    t=d.add_table(rows=1,cols=3);t.style='Table Grid';t.autofit=False
    for column,width in zip(t.columns,[46,14,132]):column.width=Mm(width)
    for c,txt in zip(t.rows[0].cells,['거점','인원','준비물']):c.text=txt
    for row in SUPPLIES:
        for c,txt in zip(t.add_row().cells,row):c.text=txt
    for row in t.rows:
        for i,c in enumerate(row.cells):
            c.width=Mm([46,14,132][i]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(3)
                for r in p.runs:r.font.size=Pt(8.5)
    p=d.add_paragraph(NOTE);p.paragraph_format.space_before=Pt(4)
    for r in p.runs:r.font.size=Pt(8)
    out=ROOT/'00_시간표와_준비물.docx';d.save(out);return out


def xlsx():
    from openpyxl import load_workbook,Workbook
    from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
    path=ROOT.parent/'사전조사 준비/02_사전조사 일정.xlsx'
    wb=load_workbook(path) if path.exists() else Workbook()
    name='사전조사 주간'
    if name in wb:wb.remove(wb[name])
    s=wb.create_sheet(name,0)
    s.merge_cells('A1:F1');s['A1']='사전조사 시간표 · 준비물'
    s.merge_cells('A2:F2');s['A2']='첨부 시간표 반영 · 목요일 성훈 추가 · 선인재단 4명 · 송도 인터뷰 50명'
    for c,width in zip('ABCDEF',[7,20,20,14,14,29]):s.column_dimensions[c].width=width
    occupied=set()
    for ri,row in enumerate(schedule_rows(),4):
        ci=1
        for text,cs,rs in row:
            while (ri,ci) in occupied:ci+=1
            if cs>1 or rs>1:s.merge_cells(start_row=ri,start_column=ci,end_row=ri+rs-1,end_column=ci+cs-1)
            c=s.cell(ri,ci,text);c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
            if ri<6 or rs>1:c.fill=PatternFill('solid',fgColor='EDF3F8' if ri<6 else 'F7FAFC');c.font=Font(name='맑은 고딕',bold=True,size=10,color='153C68')
            for rr in range(ri,ri+rs):
                for cc in range(ci,ci+cs):occupied.add((rr,cc))
            ci+=cs
        s.row_dimensions[ri].height=17
    s.row_dimensions[4].height=22;s.row_dimensions[5].height=29
    s.merge_cells('A24:F24');s['A24']='챙길 준비물'
    s.merge_cells('A25:F25');s['A25']=COMMON;s.row_dimensions[25].height=25
    for r,row in enumerate([('거점','인원','준비물'),*SUPPLIES],26):
        s.merge_cells(start_row=r,start_column=1,end_row=r,end_column=2)
        s.merge_cells(start_row=r,start_column=4,end_row=r,end_column=6)
        for c,txt in zip([1,3,4],row):s.cell(r,c,txt)
        s.row_dimensions[r].height=22 if r==26 else 38
    s.row_dimensions[28].height=51
    s.merge_cells('A34:F34');s['A34']=NOTE;s.row_dimensions[34].height=28
    border=Border(*[Side(style='thin',color='7F93A8')]*4)
    for row in s:
        for c in row:
            if not c.font.bold:c.font=Font(name='맑은 고딕',size=9)
            c.alignment=Alignment(horizontal='center' if c.row<23 else 'left',vertical='center',wrap_text=True)
            if 4<=c.row<=22 or 26<=c.row<=32:c.border=border
    s['A1'].font=Font(name='맑은 고딕',bold=True,size=16,color='153C68');s['A24'].font=Font(name='맑은 고딕',bold=True,size=12,color='153C68')
    s.freeze_panes='B6';s.print_area='A1:F34';s.sheet_properties.pageSetUpPr.fitToPage=True
    s.page_setup.orientation='portrait';s.page_setup.paperSize=s.PAPERSIZE_A4;s.page_setup.fitToWidth=1;s.page_setup.fitToHeight=1
    s.sheet_view.showGridLines=False
    if '날짜별 할 일' in wb:
        w=wb['날짜별 할 일']
        for r in range(5,w.max_row+1):
            site=w.cell(r,3).value
            if site=='선인재단':
                w.cell(r,4,'4');w.cell(r,5,'4개 위치에서 학생별 기록: 옷·가방 특징 · 시각 · 동선 · 행태 · 힘든 정도. 1 출발·2~3 중간·4 도착.');w.cell(r,6,'02_선인재단 (위치별 8장, 총 32장)')
            elif site=='굴포천':
                w.cell(r,5,'삼각대 + 카메라 1대(배터리·메모리카드)로 고정 녹화 · 머문 무리 기록지 · 사전 스티커판')
            elif site=='연안여객터미널':w.cell(r,6,'07_연안여객터미널 (9쪽) · 좌석 배치도')
            elif site=='송도글로벌캠퍼스':
                w.cell(r,5,'관찰 200건 · 인터뷰 50명(참여 의향 · 소통 기대 · 이유 · 필요한 것)');w.cell(r,6,'03_송도 (11쪽 / 인터뷰는 9~10쪽)')
    wb.save(path);return path


def build():
    for f in [pdf(),docx(),xlsx()]:print(f,flush=True)

if __name__=='__main__':build()
