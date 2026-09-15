# -*- coding: utf-8 -*-
"""사전조사 준비 · docx 공통 부품 (python-docx)"""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Mm
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import re

ROOT = Path(__file__).resolve().parents[1]
FONT = "페이퍼로지 4 Regular"
FONT_B = "페이퍼로지 7 Bold"
NAVY, TEAL, INK, MUTED = "153C68", "009DAF", "1B2735", "5A6B7D"
SOFT, WARN = "EDF3F8", "FFF4E5"


def _font(run, size=None, bold=None, color=None):
    name = FONT_B if bold else FONT
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for k in ("ascii", "hAnsi", "eastAsia", "cs"):
        rf.set(qn(f"w:{k}"), name)
    if size: run.font.size = Pt(size)
    if bold is not None: run.font.bold = bold
    if color: run.font.color.rgb = RGBColor.from_string(color)


def new(landscape=False, header=""):
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = (Mm(297), Mm(210)) if landscape else (Mm(210), Mm(297))
    if landscape: s.orientation = WD_ORIENT.LANDSCAPE
    s.left_margin = s.right_margin = Mm(18); s.top_margin = Mm(16); s.bottom_margin = Mm(15)
    st = d.styles["Normal"]; st.font.name = FONT; st.font.size = Pt(10)
    st.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), FONT)
    st.paragraph_format.space_after = Pt(4); st.paragraph_format.line_spacing = 1.35
    if header:
        hp = s.header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        _font(hp.add_run(header), 8, False, MUTED)
        fp = s.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run(); _font(r, 8, False, MUTED)
        for t, txt in (("begin", None), (None, "PAGE"), ("end", None)):
            if t:
                e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t); r._r.append(e)
            else:
                e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)
    return d


def rich(p, text, size=10, color=INK):
    """**굵게** 표기를 지원하는 문단 채우기"""
    for i, part in enumerate(re.split(r"(\*\*[^*]+\*\*)", text)):
        if not part: continue
        b = part.startswith("**")
        _font(p.add_run(part[2:-2] if b else part), size, b, color if not b else INK)
    return p


def title(d, t, sub=""):
    p = d.add_paragraph(); _font(p.add_run(t), 20, True, NAVY); p.paragraph_format.space_after = Pt(2)
    if sub:
        p = d.add_paragraph(); _font(p.add_run(sub), 9.5, False, MUTED)
    rule(d)


def rule(d, color=NAVY, sz=12):
    p = d.add_paragraph(); pPr = p._p.get_or_add_pPr()
    b = OxmlElement("w:pBdr"); bt = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", str(sz)), ("space", "1"), ("color", color)): bt.set(qn(f"w:{k}"), v)
    b.append(bt); pPr.append(b); p.paragraph_format.space_after = Pt(6)


def h1(d, t):
    p = d.add_paragraph(); _font(p.add_run(t), 14, True, NAVY)
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(4); p.paragraph_format.keep_with_next = True


def h2(d, t):
    p = d.add_paragraph(); _font(p.add_run(t), 11.5, True, TEAL)
    p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3); p.paragraph_format.keep_with_next = True


def para(d, t, size=10, color=INK):
    return rich(d.add_paragraph(), t, size, color)


def bullets(d, items, size=9.8):
    for it in items:
        p = d.add_paragraph(); p.paragraph_format.left_indent = Cm(0.5); p.paragraph_format.first_line_indent = Cm(-0.35)
        p.paragraph_format.space_after = Pt(2)
        _font(p.add_run("· "), size, True, TEAL); rich(p, it, size)


TCPR = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar",
        "textDirection", "tcFitText", "vAlign", "hideMark"]
TBLPR = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW",
         "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook"]


def _put(parent, child, order):
    """같은 태그는 바꾸고, 없으면 규격 순서 자리에 끼워 넣는다"""
    tag = child.tag.split("}")[1]
    old = parent.find(qn(f"w:{tag}"))
    if old is not None:
        parent.replace(old, child); return child
    after = order[order.index(tag) + 1:]
    for i, ex in enumerate(parent):
        if ex.tag.split("}")[1] in after:
            parent.insert(i, child); return child
    parent.append(child); return child


def shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr(); s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), hexc)
    _put(tcPr, s, TCPR)


def _borders(tbl, color="C3CFDB"):
    tblPr = tbl._tbl.tblPr; b = OxmlElement("w:tblBorders")
    for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
        x = OxmlElement(f"w:{e}")
        for k, v in (("val", "single"), ("sz", "4"), ("space", "0"), ("color", color)): x.set(qn(f"w:{k}"), v)
        b.append(x)
    _put(tblPr, b, TBLPR)


def fix_widths(t, widths_cm):
    """표 너비 고정: Word · 한글 · 미리보기 어디서 열어도 같은 칸 너비"""
    t.autofit = False  # python-docx가 tblLayout=fixed를 규격 위치에 넣음
    tblPr = t._tbl.tblPr
    tw = OxmlElement("w:tblW"); tw.set(qn("w:w"), str(int(sum(widths_cm) * 567))); tw.set(qn("w:type"), "dxa")
    _put(tblPr, tw, TBLPR)
    for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), widths_cm):
        gc.set(qn("w:w"), str(int(w * 567)))
    for row in t.rows:
        for c, w in zip(row.cells, widths_cm):
            c.width = Cm(w)


def usable_cm(d):
    s = d.sections[-1]
    return (s.page_width - s.left_margin - s.right_margin) / 360000


def table(d, rows, widths_cm=None, header=True, size=9, first_col_bold=False, fills=None, center_cols=()):
    """rows: 2차원 리스트. fills: {(r,c): 색}"""
    t = d.add_table(rows=len(rows), cols=len(rows[0])); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    _borders(t)
    for ri, row in enumerate(rows):
        for ci, v in enumerate(row):
            c = t.cell(ri, ci); c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.2
            if header and ri == 0:
                shade(c, NAVY); _font(p.add_run(str(v)), size, True, "FFFFFF"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                rich(p, str(v), size)
                if first_col_bold and ci == 0:
                    for r in p.runs: r.font.bold = True; r.font.color.rgb = RGBColor.from_string(NAVY)
                if ci in center_cols: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if fills and (ri, ci) in fills: shade(c, fills[(ri, ci)])
    if widths_cm:
        fix_widths(t, widths_cm)
    d.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def box(d, text, fill=WARN, size=9.5, label=""):
    t = d.add_table(rows=1, cols=1); _borders(t, "E6D3B3" if fill == WARN else "B8DDE3")
    fix_widths(t, [usable_cm(d)])
    c = t.cell(0, 0); shade(c, fill); p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
    if label: _font(p.add_run(label + "  "), size, True, NAVY)
    rich(p, text, size)
    d.add_paragraph().paragraph_format.space_after = Pt(2)


def image(d, path, width_cm=16, caption=""):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Cm(width_cm)); p.paragraph_format.keep_with_next = True
    if caption:
        c = d.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER; _font(c.add_run(caption), 8.8, False, MUTED)


def page_break(d):
    d.add_page_break()
