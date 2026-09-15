# -*- coding: utf-8 -*-
"""인천 창의디자인 사회실험 · 현장조사도구 공통 렌더러
HTML을 Chromium(playwright)으로 인쇄용 PDF로 만든다. 서체는 기존 보고문서와 같은 페이퍼로지."""
from pathlib import Path
import html as H
import base64
import re
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]
VER = "2026.09.13"
SAMPLE_SIZE = 200
ROWS_PER_PAGE = 25
ICON_DIR = ROOT / "표정아이콘"
ICON_NAMES = ("01_red_very_bad", "02_orange_bad", "03_yellow_neutral", "04_green_good", "05_blue_very_good")
BRAND = "ACT Incheon · 인천 창의디자인 사회실험"

# 기존 보고문서와 같은 색 체계
BLUE, TEAL, INK, MUTED = "#153C68", "#009DAF", "#1B2735", "#5A6B7D"
LINE, LINE2, SOFT, FILL = "#C3CFDB", "#7F93A8", "#EDF3F8", "#F7FAFC"

SIZES = {  # (너비mm, 높이mm)
    "A4": (210, 297), "A4L": (297, 210),
    "A3": (297, 420), "A3L": (420, 297),
    "BOARD": (297, 420),      # 손에 들고 쓰는 A3 폼보드 세로
    "BOARDL": (420, 297),     # 손에 들고 쓰는 A3 폼보드 가로
    "CARD": (105, 148),       # A6 제시·질문 카드
}

CSS = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{font-family:'Paperlogy','Apple SD Gothic Neo',sans-serif;color:{INK};
  -webkit-print-color-adjust:exact;print-color-adjust:exact;
  font-variant-numeric:tabular-nums;line-height:1.45}}
.page{{position:relative;page-break-after:always;break-after:page;overflow:hidden}}
.page:last-child{{page-break-after:auto;break-after:auto}}

/* ── 시트 머리 ── */
.brand{{font-size:7pt;color:{MUTED};letter-spacing:.02em}}
.headrow{{display:flex;align-items:flex-end;gap:7px;border-bottom:1.6px solid {BLUE};padding-bottom:4px;margin-bottom:6px}}
.code{{font-size:8.4pt;font-weight:700;color:#fff;background:{BLUE};padding:2px 7px;border-radius:3px;letter-spacing:.03em}}
h1.t{{font-size:15pt;font-weight:700;color:{BLUE};letter-spacing:-.01em;line-height:1.15}}
.sub{{font-size:8.2pt;color:{MUTED};margin-left:auto;text-align:right;line-height:1.35}}
.lead{{font-size:8.6pt;color:{MUTED};margin:5px 0 7px;line-height:1.5}}

/* ── 기입란 ── */
.meta{{display:flex;flex-wrap:wrap;gap:0;border:1px solid {LINE2};margin-bottom:7px}}
.meta > div{{flex:1 1 auto;border-right:1px solid {LINE};padding:4px 7px;min-height:26px;display:flex;align-items:center;gap:5px}}
.meta > div:last-child{{border-right:0}}
.meta b{{font-size:7.6pt;font-weight:700;color:{BLUE};white-space:nowrap}}
.meta .w{{flex:0 0 auto;border-bottom:1px dotted {LINE2};min-width:38px;height:12px}}
.chk{{font-size:8.4pt;white-space:nowrap}}

/* ── 표 ── */
table{{width:100%;border-collapse:collapse;table-layout:fixed}}
th,td{{border:.5px solid {LINE};padding:3.4px 5px;font-size:8pt;vertical-align:top;word-break:keep-all}}
thead th{{background:{SOFT};color:{BLUE};font-weight:700;font-size:7.6pt;text-align:center;
  border-color:{LINE2};line-height:1.3}}
thead th.sub2{{background:#F6FAFC;font-weight:400;color:{MUTED};font-size:7pt}}
td.c,th.c{{text-align:center}}
td.n{{text-align:center;color:{MUTED};font-size:7.6pt;background:{FILL}}}
tbody tr.blank td{{height:23px}}
tbody tr.blank td.tick{{background:#EEF4F9}}
.grp td{{background:{SOFT};font-weight:700;color:{BLUE};font-size:8.2pt;border-color:{LINE2}}}
.tot td{{background:#E8F1F6;font-weight:700;font-size:8pt;border-color:{LINE2}}}

/* ── 범례·주석 ── */
.legend{{border:1px solid {LINE2};background:{FILL};padding:6px 9px;font-size:7.6pt;
  color:{INK};line-height:1.55;margin-top:7px}}
.legend b{{color:{BLUE}}}
.legend .k{{display:inline-block;min-width:15px;font-weight:700;color:{TEAL}}}
.note{{font-size:7.4pt;color:{MUTED};line-height:1.5;margin-top:5px}}
.warn{{border-left:3px solid {TEAL};background:#F0FAFB;padding:5px 9px;font-size:7.6pt;line-height:1.55;margin-top:6px}}

/* ── 설문 문항 ── */
.q{{border:1px solid {LINE2};margin-bottom:6px}}
.q > .qh{{background:{SOFT};padding:5px 9px;border-bottom:1px solid {LINE};display:flex;gap:7px;align-items:baseline}}
.q .qno{{font-weight:700;color:{BLUE};font-size:8.6pt;white-space:nowrap}}
.q .qtx{{font-size:9.4pt;font-weight:700;line-height:1.4}}
.q .qen{{font-size:7.6pt;color:{MUTED};font-weight:400;display:block;margin-top:2px;line-height:1.35}}
.q > .qb{{padding:6px 9px}}
.opt{{display:flex;flex-wrap:wrap;gap:5px 12px;font-size:8.6pt;align-items:center}}
.opt span{{white-space:nowrap}}
.box{{display:inline-block;width:10px;height:10px;border:1px solid {MUTED};vertical-align:-1px;margin-right:3px}}
.wline{{display:block;border-bottom:1px dotted {LINE2};height:17px;margin-top:3px}}
.lik{{display:flex;gap:0;margin-top:2px}}
.lik div{{flex:1;border:1px solid {LINE};text-align:center;font-size:7.6pt;padding:3px 2px;line-height:1.3;color:{MUTED}}}
.lik div b{{display:block;font-size:11pt;color:{BLUE};margin-bottom:1px}}
.lik div.na{{flex:.8;background:{FILL}}}
"""

CSS += """
.rating-icon{width:5.5mm;height:5.5mm;object-fit:contain;vertical-align:middle}
.rating-legend{display:flex;gap:6px;align-items:center;justify-content:space-between;margin:4px 0;font-size:7.5pt}
.rating-legend span{display:flex;align-items:center;gap:3px}
.batch-label{font-size:8pt;font-weight:700;color:#153C68;border-bottom:1px solid #C3CFDB;padding-bottom:3px;margin-bottom:5px;text-align:right}
table.numbered tr{break-inside:avoid}
"""


@lru_cache(maxsize=5)
def icon_src(score):
    f = ICON_DIR / (ICON_NAMES[score - 1] + ".svg")
    return "data:image/svg+xml;base64," + base64.b64encode(f.read_bytes()).decode()


def face(score, size="5.5mm", label=""):
    return f'<img class="rating-icon" src="{icon_src(score)}" alt="{H.escape(label)}" style="width:{size};height:{size}">'


def face_legend(labels=("매우 안 좋음", "안 좋음", "보통", "좋음", "매우 좋음")):
    return '<div class="rating-legend">' + ''.join(f'<span>{face(i)}{label}</span>' for i, label in enumerate(labels, 1)) + '</div>'


def expand_numbered(items):
    """표별 준비 수량에 따라 25줄씩 확장. 기본 200건, 송도 인터뷰 50명."""
    out = []
    for size, markup in items:
        match = re.search(r"<table class='[^']*\bnumbered\b[^']*'.*?</table>", markup, re.S)
        if not match:
            out.append((size, markup))
            continue
        table = match.group()
        sample_attr = re.search(r"data-sample-size='(\d+)'", table)
        sample_size = int(sample_attr.group(1)) if sample_attr else SAMPLE_SIZE
        assert sample_size > 0 and sample_size % ROWS_PER_PAGE == 0
        page_count = sample_size // ROWS_PER_PAGE
        assert len(re.findall(r"<td class='n'>\d+</td>", table)) == ROWS_PER_PAGE
        for start in range(1, sample_size + 1, ROWS_PER_PAGE):
            nums = iter(range(start, start + ROWS_PER_PAGE))
            updated = re.sub(r"<td class='n'>\d+</td>", lambda _: f"<td class='n'>{next(nums):03d}</td>", table)
            label = (f"<div class='batch-label'>기록 {start:03d}–{start + ROWS_PER_PAGE - 1:03d} · "
                     f"{(start - 1) // ROWS_PER_PAGE + 1}/{page_count}장 · {sample_size}건 1세트</div>")
            out.append((size, label + markup[:match.start()] + updated + markup[match.end():]))
    return out


def render_mixed(items, path, extra_css="", footer=""):
    """연속된 같은 판형은 한 번에 렌더링한다."""
    from itertools import groupby
    from tempfile import TemporaryDirectory
    from pypdf import PdfReader, PdfWriter
    writer = PdfWriter()
    with TemporaryDirectory(prefix="incheon_print_") as temp:
        for idx, (size, group) in enumerate(groupby(expand_numbered(items), key=lambda item: item[0])):
            part = Path(temp) / f"{idx}.pdf"
            render([markup for _, markup in group], part, size=size, margin=(9,9,11,9), extra_css=extra_css, footer=footer)
            reader = PdfReader(part)
            for page in reader.pages:
                writer.add_page(page)
        with open(path, "wb") as target:
            writer.write(target)
    return path


def sheet_head(code, title, right="", lead=""):
    r = f'<div class="sub">{right}</div>' if right else ""
    l = f'<div class="lead">{lead}</div>' if lead else ""
    return (f'<div class="brand">{BRAND}</div>'
            f'<div class="headrow"><span class="code">{code}</span>'
            f'<h1 class="t">{title}</h1>{r}</div>{l}')


def meta_bar(fields):
    """fields: [(라벨, 폭px 또는 'chk:...')]"""
    out = []
    for lab, kind in fields:
        if kind.startswith("chk:"):
            items = "".join(f'<span class="chk"><span class="box"></span>{x}</span>'
                            for x in kind[4:].split(","))
            out.append(f'<div style="flex:0 0 auto"><b>{lab}</b>{items}</div>')
        else:
            out.append(f'<div style="flex:{kind}"><b>{lab}</b><span class="w" style="flex:1"></span></div>')
    return '<div class="meta">' + "".join(out) + "</div>"


def blank_rows(n, cols, tickcols=()):
    """빈 기록행. cols: 열 수. tickcols: 음영 처리할 열 인덱스."""
    rows = []
    for i in range(1, n + 1):
        tds = [f'<td class="n">{i}</td>']
        for c in range(1, cols):
            cls = "tick" if c in tickcols else ""
            tds.append(f'<td class="{cls}"></td>')
        rows.append(f'<tr class="blank">{"".join(tds)}</tr>')
    return "".join(rows)


def likert(labels=("전혀 그렇지 않다", "그렇지 않다", "보통이다", "그렇다", "매우 그렇다"),
           na="경험하지<br>않음"):
    cells = "".join(f'<div><b>{i}</b>{t}</div>' for i, t in enumerate(labels, 1))
    if na:
        cells += f'<div class="na"><b>8</b>{na}</div>'
    return f'<div class="lik">{cells}</div>'


FIT_JS = """(avail)=>{
  const out=[];
  document.querySelectorAll('.page').forEach((el,i)=>{
    // 내용을 감싸는 상자를 만들어 그 상자만 축소하고, 바깥 상자의 높이를 고정한다.
    let inner=el.firstElementChild;
    if(!inner || !inner.classList.contains('fitbox')){
      inner=document.createElement('div'); inner.className='fitbox';
      while(el.firstChild) inner.appendChild(el.firstChild);
      el.appendChild(inner);
    }
    inner.style.transform='none'; inner.style.width='100%';
    el.style.height='auto';
    const h=inner.scrollHeight;
    if(h>avail+2){
      const k=Math.max(0.60,(avail-2)/h);
      inner.style.transformOrigin='top left';
      inner.style.transform='scale('+k+')';
      inner.style.width=(100/k)+'%';
      el.style.height=Math.floor(h*k)+'px';
      el.style.overflow='hidden';
      out.push([i+1, Math.round(k*1000)/1000]);
    }
  });
  return out;}"""


def render(pages, path, size="A4", margin=(11, 10, 10, 10), extra_css="", fit=True, footer=""):
    """pages: HTML 문자열 리스트(각각 한 쪽). fit=True면 넘치는 쪽을 한 장에 맞춰 축소한다."""
    from playwright.sync_api import sync_playwright
    w, h = SIZES[size]
    mt, mr, mb, ml = margin
    body = "".join(f'<div class="page">{p}</div>' for p in pages)
    doc = (f"<!doctype html><meta charset=utf-8><style>{CSS}{extra_css}"
           f"@page{{size:{w}mm {h}mm;margin:{mt}mm {mr}mm {mb}mm {ml}mm}}</style>"
           f"<body>{body}</body>")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.set_content(doc, wait_until="load")
        pg.emulate_media(media="print")
        if fit:
            avail = (h - mt - mb) / 25.4 * 96
            shrunk = pg.evaluate(FIT_JS, avail)
            for i, k in shrunk:
                print(f"    · {Path(path).name} {i}쪽 → {k:.0%}로 축소해 한 장에 맞춤")
        pg.pdf(path=str(path), width=f"{w}mm", height=f"{h}mm", print_background=True,
               margin={"top": f"{mt}mm", "right": f"{mr}mm",
                       "bottom": f"{mb}mm", "left": f"{ml}mm"},
               display_header_footer=bool(footer), header_template="<div></div>",
               footer_template=("<div style=\"width:100%;text-align:center;font-family:'Paperlogy',sans-serif;font-size:10px;"
                                "font-weight:700;color:#153C68;letter-spacing:.1em\">" + footer + "</div>") if footer else "<div></div>")
        b.close()
    return path


def esc(s):
    return H.escape(str(s))
