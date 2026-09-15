# -*- coding: utf-8 -*-
"""사전조사 준비물 · 조사지
- 관찰: 사람마다 한 줄 대신 시간대별 바를 정(正) 세기
- 질문: 코팅 카드를 읽고 기록표에 한 사람 = 한 줄
- 파일: 거점별로 묶어 그날 가는 곳만 인쇄"""
import 도구_공통 as C

B, T, M = C.BLUE, C.TEAL, C.MUTED
ROOT = C.ROOT

CSS = f"""
.hd{{display:flex;align-items:flex-end;gap:8px;border-bottom:1.8px solid {B};padding-bottom:4px;margin-bottom:6px}}
.hd h1{{font-size:17pt;font-weight:700;color:{B};line-height:1.15}}
.hd .no{{font-size:9pt;font-weight:700;color:#fff;background:{B};padding:2px 8px;border-radius:3px}}
.hd .r{{margin-left:auto;font-size:8pt;color:{M};text-align:right}}
.how{{font-size:9.6pt;line-height:1.5;margin:0 0 6px;padding:5px 9px;background:#F0FAFB;border-left:3px solid {T}}}
.how b{{color:{B}}}
.st{{display:flex;flex-wrap:wrap;border:1px solid {C.LINE2};margin-bottom:7px}}
.st div{{flex:1 1 auto;border-right:1px solid {C.LINE};padding:5px 8px;font-size:9pt;white-space:nowrap}}
.st div:last-child{{border-right:0}}
.st b{{color:{B};margin-right:5px}}
table.tl th{{font-size:9.2pt;padding:4px 3px;line-height:1.25}}
table.tl th small{{display:block;font-weight:400;font-size:7.4pt;color:{M}}}
table.tl td{{font-size:9pt}}
table.tl tr.r td{{height:11.5mm}}
table.tl td.tm{{background:#F7FAFC;font-size:8pt;color:{M};text-align:center;vertical-align:middle}}
table.tl tr.sum td{{height:9mm;background:#E8F1F6;font-weight:700;color:{B};font-size:8.6pt;vertical-align:middle}}
table.tl .gs{{border-left:2px solid {B}}}
table.tl thead tr.g th{{background:{B};color:#fff;font-size:8.6pt;padding:3px}}
table.qr tr.r td{{height:8.6mm}}
.card{{border:1.4px solid {B};border-radius:4px;padding:7px 11px;margin-bottom:8px}}
.card .cap{{font-size:8.4pt;font-weight:700;color:{T};margin-bottom:3px}}
.card ol{{margin:0;padding-left:0;list-style:none}}
.card li{{font-size:10.6pt;font-weight:700;line-height:1.45;padding:3px 0;border-bottom:1px dotted {C.LINE}}}
.card li:last-child{{border-bottom:0}}
.card li .a{{font-weight:400;font-size:8.6pt;color:{M};margin-left:6px}}
.card li .e{{display:block;font-weight:400;font-size:8.4pt;color:{M}}}
.card li .qn{{display:inline-block;min-width:24px;margin-right:6px;color:{T}}}
.tip{{font-size:8.4pt;color:{M};line-height:1.5;margin-top:5px}}
.tip b{{color:{C.INK}}}
.two{{display:flex;gap:8px}}
"""

CSS += "table.pc td.ck{background:#F4F8FB} table.pc th{font-size:8.4pt} table.qr tr.r td{height:7mm}"


def hd(no, title, right=""):
    return (f"<div class='brand'>{C.BRAND}</div><div class='hd'><span class='no'>{no}</span>"
            f"<h1>{title}</h1><div class='r'>{right}<br>{C.VER}</div></div>")


def st(extra=()):
    """조사 내용에 필요한 칸만 (날짜 · 회차 · 시간 · 조사자 · 날씨는 두지 않음 — 모두 사전조사)"""
    if not extra:
        return ""
    return "<div class='st'>" + "".join(f"<div><b>{a}</b>{b}</div>" for a, b in extra) + "</div>"

def tally(first, cols, rows=9, w_first=64, w_memo=150, groups=None, total=True, times=None):
    """시간대별 세기 표. cols: [(제목, 작은설명, 그룹시작여부)]"""
    cg = f"<col style='width:{w_first}px'>" + "".join("<col>" for _ in cols) + f"<col style='width:{w_memo}px'>"
    g = ""
    if groups:
        g = "<tr class='g'><th></th>" + "".join(
            f"<th colspan='{n}' class='{'gs' if i else ''}'>{lab}</th>" for i, (lab, n) in enumerate(groups)
        ) + "<th></th></tr>"
    th = (f"<tr><th>{first}</th>"
          + "".join(f"<th class='{'gs' if gs else ''}'>{a}<small>{b}</small></th>" for a, b, gs in cols)
          + "<th>메모</th></tr>")
    body = ""
    for i in range(rows):
        t = times[i] if times and i < len(times) else ""
        body += (f"<tr class='r'><td class='tm'>{t}</td>"
                 + "".join(f"<td class='{'gs' if gs else ''}'></td>" for _, _, gs in cols) + "<td></td></tr>")
    if total:
        body += ("<tr class='sum'><td style='text-align:center'>합계</td>"
                 + "".join(f"<td class='{'gs' if gs else ''}'></td>" for _, _, gs in cols) + "<td></td></tr>")
    return f"<table class='tl'><colgroup>{cg}</colgroup><thead>{g}{th}</thead><tbody>{body}</tbody></table>"


def qrec(cols, rows=24, w_no=34, w_memo=120, first="번호", sample_size=C.SAMPLE_SIZE):
    """응답 기록표: 한 사람 = 한 줄"""
    rows = C.ROWS_PER_PAGE
    w_no = max(w_no, 34)
    cg = f"<col style='width:{w_no}px'>" + "".join(
        f"<col style='width:{w}px'>" if w else "<col>" for _, _, w in cols) + f"<col style='width:{w_memo}px'>"
    th = (f"<tr><th>{first}</th>" + "".join(f"<th>{a}<small>{b}</small></th>" for a, b, _ in cols)
          + "<th>메모</th></tr>")
    body = "".join(f"<tr class='r'><td class='n'>{i}</td>" + "<td></td>" * len(cols) + "<td></td></tr>"
                   for i in range(1, rows + 1))
    return f"<table class='tl qr numbered' data-sample-size='{sample_size}'><colgroup>{cg}</colgroup><thead>{th}</thead><tbody>{body}</tbody></table>"


def card(cap, qs):
    li = "".join(
        f"<li><span class='qn'>{n}</span>{q}<span class='a'>{a}</span>" + (f"<span class='e'>{e}</span>" if e else "") + "</li>"
        for n, q, a, e in qs)
    return f"<div class='card'><div class='cap'>{cap}</div><ol>{li}</ol></div>"


def small_tbl(title, cols, rows, widths=None):
    cg = "".join(f"<col style='width:{w}px'>" for w in widths) if widths else ""
    th = "".join(f"<th>{c}</th>" for c in cols)
    body = "".join("<tr class='r' style='height:8.2mm'>" + f"<td class='n'>{i}</td>" + "<td></td>" * (len(cols) - 1) + "</tr>"
                   for i in range(1, rows + 1))
    return (f"<div style='font-size:9.6pt;font-weight:700;color:{B};margin:0 0 3px'>{title}</div>"
            f"<table class='tl'><colgroup>{cg}</colgroup><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>")


def count_line(*items):
    return ("<div class='tip' style='display:flex;gap:22px;font-size:9pt;color:#1B2735;margin-top:6px'>"
            + "".join(f"<span>{x} <span style='display:inline-block;width:46px;border-bottom:1px solid #7F93A8'></span></span>" for x in items)
            + "</div>")


L5 = "1 전혀 아니다 · 2 · 3 보통 · 4 · 5 매우 그렇다"


# ───────────────────────────── 공통 2장
def overview():
    rows = [
        ("약산초등학교", "어린이가 표시를 알아보고, 어디인지 말할 수 있나",
         "—", "사진 보고 ① 봤는지 ② 어디서 ③ 어떻게 말할지<br><span style='color:#5A6B7D'>학교에서 나눠주고 걷음</span>",
         "사전 · 1차 · 2차", "학교와 협의<br>담당 1", "동네 지도 · 어린이 설문지"),
        ("선인재단", "그림이 있으면 오르막이 즐거워지나",
         "학생 한 명씩: 특징 · 시각 · 동선 · 행태 ✓<br>힘들어 보이는 정도 1~5 · 통과시간은 동일 학생 확인 후 시각 짝 맞춤", "— <span style='color:#5A6B7D'>(힘들어 보이는 정도는 관찰)</span>",
         "사전 · 1차 · 2차", "월 08~09시<br>4명 · 관찰 4곳", "위치별 8장 × 4곳 = 32장"),
        ("송도", "러닝존에서 처음 만난 사람과 어울리나",
         "들어온 사람·무리 한 줄씩: 인원수 · 시각<br>걷기 · 달리기 · 숨고르기 · 구경 · 휴대폰 ✓", "인터뷰 50명: 참여 의향 · 소통 기대(O/△/X) · 이유 · 필요한 것",
         "사전 · 1차 · 2차", "목 18~19시<br>3명", "기록지 · 인터뷰 기록표 · 모집 구글폼"),
        ("차이나타운", "바로 보는 안내와 QR 안내, 어느 쪽이 잘 전달되나",
         "— <span style='color:#5A6B7D'>(QR 접속은 웹에 자동 기록)</span>", "<b>스티커 보드</b>: 봤는지 · 어떤 그림 · 경각심 · 문구 표현",
         "사전(Q1·Q4) · 1차 · 2차", "목 13~14시<br>3명", "폼보드"),
        ("굴포천", "작품과 빌려 쓰는 물건이 사람을 머물게 하나",
         "<b>머문 사람·무리 한 줄씩</b>: 인원수 · 들어온·나간 시각 · 주요 행태 ✓<br>지나간 사람 · 속도는 카메라(YOLO + ByteTrack)", "스티커 폼보드 4문항",
         "사전 · 1차 · 2차", "월 13~14시<br>2명", "기록지 · 폼보드 · 고정 카메라"),
        ("로데오거리", "부스가 생기면 피우는 곳과 꽁초 버리는 곳이 바뀌나",
         "<b>피우는 사람 한 명씩</b> 어디서 · 몸 방향 · 꽁초 ○", "—",
         "사전 · 1차 · 2차", "월 18~19시<br>5명", "기록지"),
        ("연안여객터미널", "안내와 라운지가 있으면 2층에서 쉬나",
         "<b>2층 쉬는 사람 한 명씩</b> 앉은·일어난 시각 · 의자 번호<br>1층 캐리어 15분마다 (보관 공간 안 · 밖)", "만족도 · 위생·안심도 (5색 표정을 보여 주고 물음)",
         "사전 · 1차 · 2차", "월 12~16시<br>3명", "2층 기록지 · 1층 캐리어 세기"),
    ]
    tr = "".join(
        f"<tr><td style='font-weight:700;color:{B};font-size:10pt;vertical-align:middle'>{a}</td>"
        + "".join(f"<td style='font-size:9pt;line-height:1.45;vertical-align:middle'>{x}</td>" for i, x in enumerate(r) if i != 3)
        + "</tr>" for a, *r in rows)
    ck = ["클립보드 · 볼펜 (여분)", "휴대폰 시계 — 조사자끼리 시간 맞추기", "뽑은 종이 (그날 거점 파일)",
          "원형 스티커 · 폼보드 · 이젤 (굴포천 · 차이나타운)", "고정 카메라 · 삼각대 · 줄자 · 콘 4개 (굴포천)", "그림 A · B를 넣은 보드 (차이나타운)",
          "사진 찍을 휴대폰", "비닐 · 집게 (비 올 때)"]
    return (hd("한눈에", "7개 거점 조사 한눈에", "사업 전체 · 계획용")
            + "<table><colgroup><col style='width:92px'><col style='width:170px'><col><col style='width:190px'>"
              "<col style='width:120px'><col style='width:130px'></colgroup>"
              "<thead><tr><th>거점</th><th>알고 싶은 것</th><th>보는 것 (관찰)</th><th>묻는 것</th>"
              "<th>시간 · 인원</th><th>뽑을 종이</th></tr></thead>"
            + f"<tbody>{tr}</tbody></table>"
            + "<div class='two' style='margin-top:8px'>"
              "<div class='legend' style='flex:1;margin:0;font-size:8.8pt'><b>챙길 것</b><br>"
            + " &nbsp; ".join(f"□ {x}" for x in ck) + "</div>"
              "<div class='legend' style='flex:0 0 330px;margin:0;font-size:8.8pt'><b>이것만은 지키기</b><br>"
              "정해 둔 <b>시간 · 자리</b>를 그대로 지킵니다. 나중에 같은 조건으로 다시 봐야 비교가 됩니다. "
              "시간 · 인원은 「조사 방법 및 내용 등」 조사 시기 표(9/12 수정본) 기준입니다. "
              "월 13~14시는 굴포천(2명)과 터미널(3명)이 동시에 진행됩니다.</div></div>")


def rules():
    def rule(n, t, d):
        return (f"<div style='display:flex;gap:10px;padding:7px 0;border-bottom:1px solid {C.LINE}'>"
                f"<div style='flex:0 0 30px;height:30px;border-radius:50%;background:{B};color:#fff;"
                f"font-weight:700;font-size:13pt;display:flex;align-items:center;justify-content:center'>{n}</div>"
                f"<div><div style='font-size:12pt;font-weight:700;color:{B}'>{t}</div>"
                f"<div style='font-size:9.6pt;line-height:1.5'>{d}</div></div></div>")
    sym = [("正", "5명(5번)마다 한 글자"), ("✓", "그 사람이 한 행동"), ("O", "예"), ("X", "아니오"), ("?", "모름"),
           ("–", "안 물어봄 · 못 봄"), ("0", "봤는데 한 명도 없음")]
    return (hd("수칙", "조사원 수칙", "모든 거점 공통 · 한 장")
            + rule(1, "먼저 알려주지 않아요", "질문하기 전에 안내판 · 그림 · 부스를 가리키거나 설명하지 않습니다.")
            + rule(2, "정답을 알려주지 않아요", "궁금해하면 “끝나고 알려드릴게요”라고 하고 조사를 먼저 끝냅니다.")
            + rule(3, "대신 골라주지 않아요", "고민하면 질문을 한 번 더 읽어 줍니다. 그래도 모르면 <b>?</b>로 적습니다.")
            + rule(4, "이름 · 전화번호는 받지 않아요", "송도 신청 연락처만 운영용으로 따로 둡니다.")
            + rule(5, "평소와 다른 일은 메모해요", "청소 · 행사 · 비 · 단속 · 배 지연 · 운영자 설명 — <b>시각과 함께</b> 메모 칸에 적습니다.")
            + f"<div style='font-size:11pt;font-weight:700;color:{B};margin:12px 0 5px'>적는 기호</div>"
            + "<div style='display:flex;gap:6px'>"
            + "".join(f"<div style='flex:1;border:1px solid {C.LINE2};border-radius:3px;text-align:center;padding:6px 3px'>"
                      f"<div style='font-size:18pt;font-weight:700;color:{B};line-height:1.1'>{a}</div>"
                      f"<div style='font-size:8.4pt;color:{M}'>{b}</div></div>" for a, b in sym)
            + "</div>"
            + f"<div style='font-size:11pt;font-weight:700;color:{B};margin:12px 0 5px'>말 거는 법</div>"
            + "<table><colgroup><col style='width:64px'><col></colgroup><tbody>"
            + "".join(f"<tr><td style='font-weight:700;color:{B};vertical-align:middle'>{a}</td>"
                      f"<td style='font-size:9.8pt;line-height:1.55'>{b}</td></tr>" for a, b in [
                ("한국어", "“안녕하세요, 인천시 디자인 조사예요. <b>30초만</b> 여쭤봐도 될까요? 이름은 안 받아요.”"),
                ("English", "“Hi, this is a short design survey by Incheon City. May I ask you a few quick questions? It’s anonymous.”"),
                ("中文", "“您好，这是仁川市的设计调查，可以占用您30秒吗？不需要留姓名。”"),
                ("거절하면", "“네, 감사합니다.” 하고 끝냅니다. 설득하지 않고, 기록표 아래 <b>거절</b> 칸에 正 하나."),
                ("끝나면", "“감사합니다. 공간을 고치는 데 참고할게요.”"),
            ]) + "</tbody></table>"
            + f"<div style='font-size:11pt;font-weight:700;color:{B};margin:12px 0 5px'>끝나고 바로 할 일</div>"
            + "<div style='font-size:9.8pt;line-height:1.8'>"
              "□ 종이 장수 세기 &nbsp;&nbsp; □ 빈칸이 <b>–</b>(못 봄)인지 <b>0</b>(없었음)인지 표시 &nbsp;&nbsp; "
              "□ 폼보드 · 현장 사진 찍기<br>□ 사진 이름은 <b>거점_날짜</b> (예: 굴포천_0914) &nbsp;&nbsp; "
              "□ 종이는 그날 담당자에게 넘기기</div>")


# ───────────────────────────── 거점별
def _yaksan_photo(i):
    """약산초_사진 폴더에 1.jpg · 2.png 같은 파일이 있으면 프레임에 넣는다(base64로 PDF에 포함)"""
    import base64
    d = ROOT / "약산초_사진"
    for ext in ("jpg", "jpeg", "png", "JPG", "JPEG", "PNG"):
        f = d / f"{i}.{ext}"
        if f.exists():
            mime = "image/png" if ext.lower() == "png" else "image/jpeg"
            return f"data:{mime};base64," + base64.b64encode(f.read_bytes()).decode()
    return None


def _photo_card(i):
    src = _yaksan_photo(i)
    if src:
        inner = f"<img src='{src}' style='width:100%;height:100%;object-fit:cover;display:block'>"
        border = "1.2px solid #7F93A8"
    else:
        inner = ("<div style='height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center'>"
                 f"<div style='font-size:15pt;font-weight:700;color:#9FB3C6'>사진 {i}</div>"
                 "<div style='font-size:7.4pt;color:#9AA8B6;margin-top:2px'>여기에 사진 · 세로</div></div>")
        border = "1.4px dashed #9FB3C6"
    return ("<div style='display:flex;gap:8px;align-items:center;border:1px solid #C3CFDB;border-radius:4px;padding:6px'>"
            f"<div style='flex:0 0 44mm;height:52mm;border:{border};border-radius:3px;background:#FFFFFF;overflow:hidden;position:relative'>"
            f"<div style='position:absolute;left:4px;top:4px;background:#153C68;color:#fff;font-size:9.5pt;font-weight:700;"
            f"padding:0 7px;border-radius:2px;z-index:2'>{i}</div>{inner}</div>"
            "<div style='flex:1;font-size:10pt;line-height:1.8'>○ 봤어요<br>○ 못 봤어요<br>○ 잘 모르겠어요<br>○ 이 길로 안 다녀요"
            "<div style='margin-top:2px;font-size:9pt'>어디서? 지도 번호 <span style='display:inline-block;width:30px;border-bottom:1px solid #7F93A8'></span></div>"
            "</div></div>")


MAP_DIRS = [ROOT / "약산초_지도"]  # 1·2차는 자기 폴더를 앞에 끼워 넣음 (비어 있으면 사전조사 지도를 씀)
IMG_EXT = ("jpg", "jpeg", "png", "JPG", "JPEG", "PNG")


def _map_dir():
    for d in MAP_DIRS:
        if (d / "번호.txt").exists() or any((d / f"지도.{e}").exists() for e in IMG_EXT):
            return d
    return MAP_DIRS[-1]


def yaksan_map(n=10):
    """설문지 앞장 · 「약산초_지도」에 지도.jpg(Google 지도 캡처 + 번호 표시)와 번호.txt(한 줄에 '1 정문 앞')를 넣으면 들어간다"""
    import base64
    d = _map_dir()
    img = next((d / f"지도.{e}" for e in IMG_EXT if (d / f"지도.{e}").exists()), None)
    names = []
    if (d / "번호.txt").exists():
        for ln in (d / "번호.txt").read_text(encoding="utf-8").splitlines():
            if ln.strip():
                head, _, rest = ln.strip().partition(" ")
                names.append(rest.strip() if head.rstrip(".)").isdigit() else ln.strip())
    k = max(n, len(names) + len(names) % 2)
    if img:
        mime = "image/png" if img.suffix.lower() == ".png" else "image/jpeg"
        frame = (f"<div style='height:190mm;border:1.2px solid #7F93A8;border-radius:3px;overflow:hidden;background:#fff'>"
                 f"<img src='data:{mime};base64,{base64.b64encode(img.read_bytes()).decode()}' "
                 "style='width:100%;height:100%;object-fit:contain;display:block'></div>")
    else:
        frame = ("<div style='height:190mm;border:1.4px dashed #9FB3C6;border-radius:3px;background:#fff;display:flex;"
                 "flex-direction:column;align-items:center;justify-content:center'>"
                 "<div style='font-size:20pt;font-weight:700;color:#9FB3C6'>Google 지도 캡처</div>"
                 "<div style='font-size:9pt;color:#9AA8B6;margin-top:4px'>학교 주변 · 후보 위치에 번호 1, 2, 3 … 을 표시해 "
                 "「약산초_지도」 폴더에 지도.jpg로 넣으세요</div></div>")
    cell = lambda i: ("<div style='display:flex;align-items:center;gap:8px;height:9.5mm;border-bottom:1px solid #C3CFDB'>"
                      f"<span style='flex:0 0 7mm;height:7mm;border-radius:50%;background:{B};color:#fff;font-weight:700;font-size:11pt;"
                      f"display:flex;align-items:center;justify-content:center'>{i}</span>"
                      f"<span style='font-size:11pt'>{names[i - 1] if i <= len(names) else ''}</span></div>")
    return ("A4", hd("약산초", "우리 동네 지도", "설문지 앞장 · 함께 나눠 줌")
            + "<div class='how' style='font-size:11pt'><b>사진 속 표시를 어디서 봤는지</b> 지도에서 찾아보세요. "
              "찾은 곳의 <b>번호</b>를 설문지 ‘어디서? 지도 번호’ 칸에 적어요.</div>"
            + frame
            + f"<div style='font-size:12pt;font-weight:700;color:{B};margin:8px 0 2px'>지도 번호</div>"
            + f"<div style='display:grid;grid-auto-flow:column;grid-template-columns:1fr 1fr;grid-template-rows:repeat({k // 2},auto);column-gap:16px'>"
            + "".join(cell(i) for i in range(1, k + 1)) + "</div>")


def yaksan():
    p1 = (hd("약산초 ①", "등하굣길 표시 찾기", "어린이가 직접 쓰는 종이")
          + "<div class='how' style='font-size:11pt'><b>우리 길에 있는 표시를 찾아보는 조사예요.</b> 맞고 틀린 답은 없어요. "
            "등하굣길에서 <b>진짜로 본 것</b>만 골라 주세요. 이름은 쓰지 않아요.</div>"
          + "<div class='st'><div><b>학년</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;학년</div><div><b>반</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;반</div>"
            "</div>"
          + f"<div style='font-size:12pt;font-weight:700;color:{B};margin:8px 0 5px'>1. 사진을 보고 골라 주세요 "
            "<span style='font-weight:400;font-size:10pt;color:#1B2735'>— 이번 등하굣길에서 봤나요? 봤다면 어디서 봤어요?</span></div>"
          + "<div style='display:grid;grid-template-columns:1fr 1fr;gap:6px'>" + "".join(_photo_card(i) for i in range(1, 7)) + "</div>"
          + f"<div style='font-size:12pt;font-weight:700;color:{B};margin:12px 0 4px'>2. 가족이나 어른에게 이곳을 알려준다면, 어떻게 말할 거예요?</div>"
          + "".join("<div style='border-bottom:1px dotted #7F93A8;height:10mm'></div>" for _ in range(3)))
    p2 = (hd("약산초", "워크숍 결과 기록", "1차 실험 · 200건 기록용 · 학급은 메모에")
          + "<div class='st'><div><b>학급</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div><div><b>날짜</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div>"
            "<div><b>참여 인원</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;명</div><div><b>기록한 사람</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div></div>"
          + qrec([("붙인 이름", "", 110), ("무엇을 그렸나", "색 · 모양 · 그림", None),
                  ("어디에 두고 싶나", "지도 번호", 90), ("왜 거기?", "어린이 말 그대로", None),
                  ("뽑힘", "○", 44)], rows=26, w_memo=110)
          + "<div class='tip'>안 뽑힌 아이디어도 지우지 않고 다 적습니다. 한 어린이가 여러 개 내면 줄을 나눠 적고 메모에 ‘같은 사람’이라고 씁니다.</div>")
    return [("A4", p1), ("A4", p2)]  # p1 사전조사 · p2 워크숍 기록표(세로)는 「1차 실험」 폴더로


def pcheck(cols, rows=18, start=1, w_no=26, w_memo=110, row_h=7.4, memo="메모"):
    """사람 체크표: 한 줄 = 한 사람. cols: [(제목, 작은설명, 너비px 또는 None, 미리 인쇄할 보기)]"""
    rows, row_h, w_no = C.ROWS_PER_PAGE, 7.4, max(w_no, 34)
    cg = f"<col style='width:{w_no}px'>" + "".join(
        f"<col style='width:{w}px'>" if w else "<col>" for _, _, w, _ in cols) + f"<col style='width:{w_memo}px'>"
    th = "<tr><th>번호</th>" + "".join(f"<th>{a}<small>{b}</small></th>" for a, b, _, _ in cols) + f"<th>{memo}</th></tr>"
    body = ""
    for i in range(start, start + rows):
        tds = "".join(
            f"<td style='text-align:center;vertical-align:middle;color:#9AA8B6;font-size:7.8pt'>{pre}</td>" if pre
            else "<td class='ck'></td>" for _, _, _, pre in cols)
        body += f"<tr style='height:{row_h}mm'><td class='n'>{i}</td>{tds}<td></td></tr>"
    return f"<table class='tl pc numbered'><colgroup>{cg}</colgroup><thead>{th}</thead><tbody>{body}</tbody></table>"


def route(active):
    """선인재단 경로 위 내 자리 표시"""
    steps = [("출발", "1번"), ("중간", "2~3번"), ("도착", "4번")]
    out = []
    for i, (k, d) in enumerate(steps):
        on = k in (active if isinstance(active, tuple) else (active,))
        bg, fg = (B, "#fff") if on else ("#fff", B)
        out.append(f"<div style='flex:1;border:1.4px solid {B};border-radius:4px;padding:4px 9px;background:{bg};color:{fg};font-size:9.2pt'>"
                   f"<b>{k}</b> <span style='font-size:8pt'>{d}{' · 이 종이' if on else ''}</span></div>")
        if i < 2:
            out.append(f"<div style='flex:0 0 22px;text-align:center;color:{B};font-weight:700;font-size:12pt'>→</div>")
    return "<div style='display:flex;align-items:center;margin-bottom:6px'>" + "".join(out) + "</div>"


def gcheck(lead, glabel, gcols, rows=17, start=1, w_no=30, w_memo=150, row_h=7.4, tail=(), memo_label="비고<small>기타 행위</small>"):
    """한 줄 = 한 사람 또는 무리. lead: [(제목, 작은설명, 너비, 미리 인쇄할 보기)] · gcols: 체크 칸 ·
    tail의 보기가 리스트면 칸을 나눠 숫자를 미리 인쇄한다(동그라미 치기 · 스캔용)"""
    rows, row_h, w_no = C.ROWS_PER_PAGE, 7.4, max(w_no, 34)
    scale = lambda pre: isinstance(pre, (list, tuple))
    cg = f"<col style='width:{w_no}px'>" + "".join(f"<col style='width:{w}px'>" for _, _, w, _ in lead) + "".join("<col>" for _ in gcols)
    for _, _, w, pre in tail:
        cg += "".join(f"<col style='width:{w}px'>" for _ in pre) if scale(pre) else f"<col style='width:{w}px'>"
    cg += f"<col style='width:{w_memo}px'>"
    r1 = "<th rowspan='2'>번호</th>" + "".join(f"<th rowspan='2'>{a}<small>{b}</small></th>" for a, b, _, _ in lead)
    r2 = ""
    if gcols:
        r1 += (f"<th colspan='{len(gcols)}' class='gs' style='background:{B};color:#fff'>{glabel} "
               "<span style='font-weight:400;font-size:7.6pt'>해당하면 모두 ✓</span></th>")
        r2 += "".join(f"<th class='{'gs' if i == 0 else ''}'>{g}</th>" for i, g in enumerate(gcols))
    for a, b, _, pre in tail:
        if scale(pre):
            r1 += (f"<th colspan='{len(pre)}' class='gs' style='background:{B};color:#fff'>{a}"
                   f"<span style='display:block;font-weight:400;font-size:7pt'>{b}</span></th>")
            import re
            def heading(o):
                label = re.search(r'alt="([^"]+)"', o)
                return o + (f'<small>{label.group(1)}</small>' if label else '')
            r2 += "".join(f"<th class='{'gs' if k == 0 else ''}'>{heading(o)}</th>" for k, o in enumerate(pre))
        else:
            r1 += f"<th rowspan='2' class='gs'>{a}<small>{b}</small></th>"
    r1 += f"<th rowspan='2'>{memo_label}</th>"
    body = ""
    for i in range(start, start + rows):
        tds = "".join(f"<td style='text-align:center;vertical-align:middle;color:#9AA8B6;font-size:8.6pt'>{pre}</td>" if pre
                      else "<td></td>" for *_, pre in lead)
        tds += "".join(f"<td class='ck{' gs' if j == 0 else ''}'></td>" for j in range(len(gcols)))
        for *_, pre in tail:
            if scale(pre):
                tds += "".join(f"<td class='{'gs' if k == 0 else ''}' style='text-align:center;vertical-align:middle;color:#AEBBC8;font-size:9.5pt'>{o}</td>"
                               for k, o in enumerate(pre))
            else:
                tds += f"<td class='gs' style='text-align:center;vertical-align:middle;color:#9AA8B6;font-size:8.2pt'>{pre}</td>"
        body += f"<tr style='height:{row_h}mm'><td class='n'>{i}</td>{tds}<td></td></tr>"
    return f"<table class='tl pc numbered'><colgroup>{cg}</colgroup><thead><tr>{r1}</tr><tr>{r2}</tr></thead><tbody>{body}</tbody></table>"


GROUP_RULE = "<b>인원수</b>는 혼자면 비워 두고(=1명), 2명 이상이면 숫자. 시각은 <b>00:00:00</b>(시:분:초)"


def seonin(phase=0):
    where = {1: "출발", 2: "중간", 3: "중간", 4: "도착"}
    pages = []
    for n in range(1, 5):
        badge = (f"<span style='display:inline-block;text-align:center;border:2px solid {B};border-radius:6px;padding:1px 12px 3px;"
                 f"color:{B};line-height:1.05;vertical-align:bottom'><span style='font-size:8pt;display:block'>{where[n]}</span>"
                 f"<span style='font-size:26pt;font-weight:700'>{n}</span></span>")
        acts = ["휴대폰 봄", "대화", "앞만 봄", "그냥 올라감", "뛰어놂", "관찰함"] + (["그림 봄"] if phase else [])
        feeling = ([("표정", "하나에 ○", 24, [C.face(5, "4.5mm", "웃음"), C.face(3, "4.5mm", "보통"), C.face(1, "4.5mm", "힘듦")])]
                   if phase else [("힘든 정도", "1 안 힘듦 → 5 매우", 18, ["1", "2", "3", "4", "5"])])
        explanation = ("표정: 파랑 웃음 · 노랑 보통 · 빨강 힘듦. " if phase else "힘든 정도: 1 전혀 안 힘들어 보임 → 5 매우 힘들어 보임. ")
        pages.append(("A4",
            hd("선인재단", "기록지", badge)
            + "<div class='how' style='font-size:8.3pt'>1 출발 · 2~3 중간 · 4 도착. <b>한 학생 = 한 줄</b>, 시계는 초까지 맞춥니다. "
              "번호는 <b>각 위치의 기록순서</b>입니다. 옷·가방 특징을 한 줄(예: 검정상의/빨강가방)로 적고 시각은 <b>00:00:00</b>. "
            + "위치별 기록은 동일 학생임을 확인한 경우만 연결하고, 도착순서로 맞추지 않습니다. "
            + explanation + "행태는 모두 ✓, 못 봤으면 비고에 ‘못 봄’.</div>"
            + gcheck([("옷·가방 특징", "한 줄만", 120, ""), ("시각", "00:00:00", 90, ""), ("동선", "○", 45, "왼·오")],
                     "행태", acts, tail=feeling, w_no=34, w_memo=48, row_h=7.4)))
    return pages


def songdo():
    p1 = (hd("송도 ①", "러닝존 기록지", "")
          + st([("내 구간", "□ 출발 &nbsp;□ 코스 &nbsp;□ 쉼터 &nbsp;□ 횡단보도")])
          + "<div class='how'>내 구간에 들어온 사람을 한 줄씩 적습니다. " + GROUP_RULE
          + ". 행위는 해당하면 모두 ✓, 그 밖의 행동은 비고에.</div>"
          + gcheck([("인원수", "비우면 1", 54, ""), ("시각", "00:00:00", 86, "")],
                   "행위", ["걷기", "달리기", "뛰다가 숨고르기", "구경하기", "휴대폰하고 놀기"], rows=25, w_no=28, w_memo=110, row_h=7.9))
    p2 = (hd("송도 ②", "인터뷰 기록표", "사전조사 · 조사 중간에 누구에게나 · 1분")
          + card("읽어 줄 질문 · O 그렇다 · △ 잘 모르겠다 · X 아니다", [
              ("Q1", "이곳에 러닝 코스가 생기면 참여할 것 같나요?", "O / △ / X", "If a running course opens here, would you join?"),
              ("Q2", "러닝 코스가 생기면 사람들 사이의 소통이 늘어날 것 같나요?", "O / △ / X", "Do you think it would help people interact more?"),
              ("Q3", "왜 그렇게 생각하세요?", "Q1 · Q2에 O나 X로 답했을 때 · 말 그대로", "Why do you think so?"),
              ("Q4", "러닝 코스가 잘 쓰이고 소통이 생기려면 무엇이 필요할까요?", "말 그대로", "What would it take for the course to be used and help people connect?")])
          + st()
          + "<style>.iv table.qr tr.r td{height:6.4mm}.iv .card li{font-size:9pt}</style><div class='iv'>"
          + qrec([("Q1 참여", "O / △ / X", 62), ("Q2 소통", "O / △ / X", 62), ("Q3 이유", "말 그대로", None),
                  ("Q4 필요한 것", "말 그대로", None)], rows=25, w_memo=60, sample_size=50) + "</div>"
          + count_line("말 건 사람", "거절", "말이 안 통함"))
    return [("A4", p1), ("A4", p2), ("A4", songdo_form())]


def songdo_form():
    """참가자 모집 구글폼 문항표 · 1차 러닝 활동 전에 열어 둔다"""
    return (hd("송도 ③", "참가자 모집 구글폼 문항표", "폼에 그대로 옮겨 씀")
            + "<div class='how'>1차 러닝 활동 전에 참가자를 모읍니다. 아래 문항을 구글폼에 그대로 옮기고(한국어 · 영어 함께), "
              "인터뷰 Q1에 O나 △로 답한 분께 폼 QR을 보여 드립니다.</div>"
            + card("구글폼 문항 · 필수는 ① ② ③ ⑥", [
                ("①", "참가하고 싶은 날짜를 골라 주세요.", "1차 활동 날짜 · 여러 개", "Which date(s) can you join?"),
                ("②", "이름 또는 닉네임", "운영용 · 분석에 쓰지 않음", "Name or nickname"),
                ("③", "연락처", "활동 안내 문자용 · 분석에 쓰지 않음", "Phone number"),
                ("④", "혼자 오시나요, 아는 사람과 함께 오시나요?", "혼자 / 함께(몇 명)", "Coming alone or with people you know?"),
                ("⑤", "참여하려는 이유는 무엇인가요?", "운동 · 휴식 · 새로운 사람 · 기타 (여러 개)", "Why would you like to join?"),
                ("⑥", "개인정보 수집 · 이용에 동의하시나요?", "목적: 활동 안내 · 항목: 이름 · 연락처 · 실험이 끝나면 파기",
                 "Do you agree to the collection and use of your personal information?")])
            + "<div class='tip'>참가번호는 신청 순서대로 줍니다(S001~S200). 1차 · 2차 출석과 재참여를 같은 번호로 확인합니다.</div>")


def _img_src(folder, name):
    """폴더에 name.jpg/png가 있으면 base64로 넣는다"""
    import base64
    d = ROOT / folder
    for ext in ("jpg", "jpeg", "png", "JPG", "JPEG", "PNG"):
        f = d / f"{name}.{ext}"
        if f.exists():
            return f"data:{'image/png' if ext.lower() == 'png' else 'image/jpeg'};base64," + base64.b64encode(f.read_bytes()).decode()
    return None


def _frame(folder, name, label, h, big=15, bw='1.4px dashed'):
    src = _img_src(folder, name)
    if src:
        return (f"<div style='height:{h};border:1.2px solid #7F93A8;border-radius:3px;overflow:hidden;background:#fff'>"
                f"<img src='{src}' style='width:100%;height:100%;object-fit:contain;display:block'></div>")
    return (f"<div style='height:{h};border:{bw} #9FB3C6;border-radius:3px;background:#FFFFFF;display:flex;"
            f"flex-direction:column;align-items:center;justify-content:center'><div style='font-size:{big}pt;font-weight:700;color:#9FB3C6'>{label}</div>"
            f"<div style='font-size:{big * 0.5:.1f}pt;color:#9AA8B6'>여기에 그림</div></div>")


CH_Q = [  # (번호, 한국어, English, 中文, 보기[(기호, 한, 영, 중)])
    ("Q1", "방금 이 근처에서 화장실 안내를 보셨어요?", "Did you see the restroom sign around here just now?", "您刚才在附近看到卫生间的指示了吗？",
     [("O", "봤어요", "Yes", "是"), ("X", "못 봤어요", "No", "否"), ("?", "잘 모르겠어요", "Not sure", "不确定")]),
    ("Q2", "어떤 안내였나요?", "Which sign was it?", "是哪一个指示？",
     [("A", "그림 A", "A", "A"), ("B", "그림 B", "B", "B"), ("?", "정확히 기억이 안 나요", "Don’t remember exactly", "记不清了")]),
    ("Q3", "안내를 보고 올바르게 써야겠다는 생각이 얼마나 들었나요?", "How much did it make you want to use the restroom properly?",
     "它让您觉得应该正确使用卫生间吗？",
     [("1", "전혀 아니다", "Not at all", "完全没有"), ("2", "아니다", "Not really", "不太"), ("3", "보통", "Neutral", "一般"),
      ("4", "그렇다", "Yes", "是"), ("5", "매우 그렇다", "Very much", "非常")]),
    ("Q4", "안내 문구의 표현은 어떤가요?", "How should the wording be?", "您觉得指示语的表达应该怎样？",
     [("1", "훨씬 더 강해야 한다", "Much stronger", "强烈得多"), ("2", "좀 더 강해야 한다", "A bit stronger", "稍强一些"),
      ("3", "지금이 괜찮다", "Fine as is", "现在正好"), ("4", "좀 더 부드럽게 표현되어야 한다", "A bit softer", "稍柔和一些"),
      ("5", "훨씬 부드럽게 표현되었으면 한다", "Much softer", "柔和得多")]),
]
CH_LANG = [("한", "한국어", "Korean", "韩语"), ("EN", "English", "English", "英语"), ("中", "中文", "Chinese", "中文"), ("…", "기타", "Other", "其他")]


def china():
    qs = "".join(f"<li><span class='qn'>{n}</span>{k}<span class='a'>{' / '.join(o[1] for o in opts)}</span></li>" for n, k, e, z, opts in CH_Q)
    en = "".join(f"<li><span class='qn'>{n}</span>{e}<span class='a'>{' / '.join(o[2] for o in opts)}</span></li>" for n, k, e, z, opts in CH_Q)
    zh = "".join(f"<li><span class='qn'>{n}</span>{z}<span class='a'>{' / '.join(o[3] for o in opts)}</span></li>" for n, k, e, z, opts in CH_Q)
    big = (".big .card{padding:8px 12px;margin-bottom:8px}.big .card li{font-size:11.4pt;padding:4px 0}"
           ".big .card li .a{font-size:8.4pt;display:block;margin-left:24px}")
    p1 = (f"<style>{big}</style><div class='big'>" + hd("차이나타운 ①", "질문 카드", "코팅해서 들고 다니기 · 읽기만 함")
          + "<div class='how'>보드(스티커)가 기본입니다. 말로 물을 때만 이 카드를 읽고 기록표(②)에 적습니다. Q1이 ‘못 봤어요’면 Q2~Q4는 건너뜁니다. "
            "사전에는 <b>기존 화장실 안내</b>를 기준으로 묻고, 그림 A · B에 기존 안내 사진과 대조 그림을 넣습니다.</div>"
          + "<div style='display:flex;gap:10px;margin-bottom:8px'>"
          + "".join(f"<div style='flex:1'><div style='font-size:10pt;font-weight:700;color:{B};margin-bottom:3px'>그림 {x}</div>"
                    + _frame("차이나타운_그림", x, f"그림 {x}", "58mm") + "</div>" for x in "AB") + "</div>"
          + f"<div class='card'><div class='cap'>한국어 · 먼저 사용 언어를 묻습니다 (한국어 / English / 中文 / 기타)</div><ol>{qs}</ol></div>"
          + f"<div class='card'><div class='cap'>English</div><ol>{en}</ol></div>"
          + f"<div class='card'><div class='cap'>中文</div><ol>{zh}</ol></div></div>")
    p2 = (hd("차이나타운 ②", "응답 기록표", "한 사람 = 한 줄")
          + st()
          + qrec([("사용 언어", "한 / 영 / 중 / 기타", 80), ("Q1 봤나", "O / X / ?", 72), ("Q2 어느 그림", "A / B / ?", 80),
                  ("Q3 경각심", "1~5", 72), ("Q4 문구 표현", "1 훨씬 강하게 ~ 5 훨씬 부드럽게", 120)], rows=24)
          + count_line("말 건 사람", "거절", "말이 안 통함")
          + "<div class='tip'>QR 접속 수 · 에티켓 확인 · 좋아요/나빠요는 웹에 자동으로 남습니다. 조사자가 시험으로 QR을 찍었다면 메모에 시각을 적습니다.</div>")
    return [("A4", p1), ("A4", p2)]


def boards_china():
    """차이나타운 스티커 보드 · 가로 900×600 · 왼쪽: 사용 언어 · Q1 · Q2 / 오른쪽: Q3 · Q4"""
    def cells(opts):
        return "".join(
            f"<div class='cell'><div class='slot'></div><div class='lb'><b>{sym}</b><span>{k}</span>"
            "</div></div>"
            for sym, k, e, z in opts)

    def row(n, k, e, z, body, fx):
        return (f"<div class='row' style='flex:{fx} 1 0'><div class='bq'><span>{n}</span>{k}"
                f"<div style='font-size:19pt;font-weight:400;color:{M};margin-top:1.5mm;line-height:1.3'>{e}<br>{z}</div></div>"
                f"<div class='scale'>{body}</div></div>")
    q = {x[0]: x for x in CH_Q}
    native = {"한": "한국어", "EN": "English", "中": "中文", "…": "기타 · Other · 其他"}
    langs = "".join(f"<div class='cell'><div class='slot'></div><div class='lb'><b>{sym}</b><span>{native[sym]}</span></div></div>"
                    for sym, *_ in CH_LANG)
    pic = "".join(f"<div class='cell' style='flex:2'>{_frame('차이나타운_그림', x, '그림 ' + x, '92mm', 30, '0.8mm solid')}"
                  f"<div class='slot' style='margin-top:3mm;border-style:dashed'></div>"
                  f"<div class='lb'><b>{x}</b><span>그림 {x}</span></div></div>" for x in "AB")
    pic += cells([q["Q2"][4][2]])
    left = row(*q["Q1"][:4], cells(q["Q1"][4]), 1) + row(*q["Q2"][:4], pic, 2.2)
    def anchored(key, en, zh):
        n, k, e, z, _ = q[key]
        return n, k, f"{e} ({en})", f"{z}（{zh}）"
    right = (row(*anchored("Q3", "1 not at all – 5 very much", "1 完全没有 – 5 非常"), cells(q["Q3"][4]), 1)
             + row(*anchored("Q4", "1 much stronger – 5 much softer", "1 强烈得多 – 5 柔和得多"), cells(q["Q4"][4]), 1))
    css = ("<style>.fitbox{height:550mm !important}.bt{font-size:50pt !important}.row .slot{min-height:22mm}"
           ".row .bq{font-size:27pt}.lb b{font-size:34pt}.lb span{font-size:15pt}</style>")
    lab = "style='color:#153C68;display:inline-block;width:46mm'"
    head = (f"<div class='bh' style='display:flex;align-items:flex-end;gap:10mm;margin-bottom:7mm'><div style='flex:1'>"
            "<div class='bb'>ACT Incheon · 인천 창의디자인 사회실험 · 차이나타운</div>"
            "<div class='bt'>화장실 안내, 어떠셨어요?</div>"
            f"<div class='bs'>질문마다 스티커 한 장씩 붙여 주세요. <span style='color:{M}'>One sticker per question · 每题请贴一张贴纸</span></div></div>"
            "</div>")
    body = ("<div style='flex:1 1 0;min-height:0;display:flex;gap:12mm'>"
            f"<div style='flex:1.15;display:flex;flex-direction:column;min-width:0'>{left}</div>"
            f"<div style='flex:1;display:flex;flex-direction:column;min-width:0'>{right}</div></div>")
    return [css + head + body]


def gulpo():
    p1 = (hd("굴포천 ①", "머무는 사람 기록지", "사전조사")
          + st()
          + "<div class='how'>다리 밑에서 <b>멈추거나 머문 사람</b>을 한 줄씩 적습니다. " + GROUP_RULE
          + ". 주요 행태는 해당하면 모두 ✓, 그 밖의 행동은 비고에. 그냥 지나간 사람 수 · 이동 속도는 고정 카메라 녹화 영상을 사무실에서 분석합니다.</div>"
          + "<div style='border:1.2px dashed #7F93A8;border-radius:4px;padding:6px 10px;margin-bottom:7px;font-size:9.4pt;height:11mm'>"
            "<b style='color:#153C68'>카메라가 안 될 때만</b> · 그냥 지나간 사람 <span style='color:#5A6B7D;font-size:8.4pt'>正</span></div>"
          + gcheck([("인원수", "비우면 1", 42, ""), ("들어온 시각", "00:00:00", 74, ""), ("나간 시각", "00:00:00", 74, "")],
                   "주요 행태", ["뛰기", "걷기", "놀기", "앉아서 쉬기<br><small>휴대폰 X</small>", "앉아서 쉬기<br><small>휴대폰 O</small>", "대화"], rows=24, w_no=28, w_memo=70, row_h=7.9))

    return [("A4", p1)]


def rodeo():
    p1 = (hd("로데오거리", "담배 피우는 사람 기록지", "")
          + st()
          + "<div class='how'>담배 피우는 사람 <b>한 명 = 한 줄</b>, 해당하는 것에 <b>동그라미</b>. 몸 방향은 피우는 중간에 한 번 봅니다. 꽁초를 끝까지 못 봤으면 ?. "
            "사전에는 부스가 없으니 벤치 기준입니다. 사람을 따라다니거나 사진 찍지 않습니다.</div>"
          + pcheck([("시각", "시:분", 60, ""), ("어디서", "", 150, "부스 안 · 벤치 · 그 밖"), ("몸 방향", "", 110, "안쪽 · 바깥 · ?"),
                    ("꽁초", "", 130, "수거함 · 바닥 · ?")], rows=26, w_no=28, w_memo=120, row_h=8.2, memo="비고"))
    return [("A4", p1)]


def terminal():
    p1 = (hd("연안여객터미널 ①", "2층에서 쉬는 사람 기록지", "2층 담당 · 사전조사 · 관찰하고 물어서 적기")
          + st()
          + "<div class='how'>2층 일반 휴식 구역에 <b>앉는 사람마다 한 줄</b>. 시각은 <b>00:00:00</b>, 자리 위치는 좌석 배치도의 <b>의자 번호</b>. "
            "일어설 때(또는 쉬는 데 방해되지 않을 때) 아래 두 가지를 묻고 해당 표정에 동그라미 칩니다. 직원 · 전용공간 이용자는 적지 않습니다.</div>"
          + card("읽어 줄 질문 · 빨강 전혀 아니다 → 파랑 매우 그렇다",
                 [("만족도", "지금 이 공간에 얼마나 만족하세요?", "표정 하나", ""),
                  ("위생·안심도", "위생적이고 안심하고 쉴 수 있다고 느끼세요?", "표정 하나", "")])
          + C.face_legend(("전혀 아니다", "아니다", "보통", "그렇다", "매우 그렇다"))
          + gcheck([("앉은 시각", "00:00:00", 76, ""), ("일어난 시각", "00:00:00", 80, ""), ("자리 위치", "의자 번호", 62, "")], "", [],
                   rows=25, tail=[("만족도", "빨강 → 파랑", 23, [C.face(i, "4.5mm") for i in range(1, 6)]), ("위생·안심도", "빨강 → 파랑", 23, [C.face(i, "4.5mm") for i in range(1, 6)])],
                   w_no=30, w_memo=70, row_h=8.4, memo_label="비고"))
    times = [f"{h:02d}:{m:02d}" for h in range(12, 17) for m in (0, 15, 30, 45) if h < 16 or m == 0]
    rows = "".join(f"<tr style='height:11.5mm'><td class='n' style='vertical-align:middle'>{i}</td><td style='text-align:center;vertical-align:middle;font-weight:700;"
                   f"font-size:11pt;color:{B};background:#F7FAFC'>{t}</td><td></td><td></td><td></td></tr>" for i, t in enumerate(times, 1))
    p2 = (hd("연안여객터미널 ②", "1층 짐 보관 공간 캐리어 세기", "1층 담당 · 사전조사 · 15분마다")
          + st()
          + "<div class='how'>15분마다 1층 짐 보관 공간 <b>안</b>에 놓인 캐리어와 그 <b>주변(공간 밖)</b>에 놓인 캐리어를 셉니다(원 조사표: 짐 보관 공간에 넣는 수). "
            "잠시 둔 짐을 버린 짐으로 보지 않고 ‘밖’으로만 셉니다. 못 센 시각은 비워 두고 비고에 이유를 적습니다.</div>"
          + "<table class='tl'><colgroup><col style='width:40px'><col style='width:110px'><col><col><col style='width:200px'></colgroup>"
            "<thead><tr><th>번호</th><th>시각</th><th>보관 공간 내 개수</th><th>보관 공간 외 개수</th><th>비고</th></tr></thead>"
          + f"<tbody>{rows}</tbody></table>")
    return [("A4", p1), ("A4", p2)]


# ───────────────────────────── 폼보드 (600×900)
BOARD_CSS = f"""
.page{{display:block}}
.fitbox{{display:flex;flex-direction:column;height:850mm}}
.bb{{font-size:12pt;color:{M};letter-spacing:.05em;margin-bottom:3mm}}
.bt{{font-size:60pt;font-weight:700;color:{B};line-height:1.1;letter-spacing:-.02em}}
.bs{{font-size:20pt;margin-top:5mm;line-height:1.4}}
.bh{{flex:0 0 auto;border-bottom:3mm solid {B};padding-bottom:7mm;margin-bottom:10mm}}
.row{{flex:1 1 0;min-height:0;display:flex;flex-direction:column;margin-bottom:9mm}}
.row .bq{{flex:0 0 auto;font-size:30pt;font-weight:700;line-height:1.3;margin-bottom:5mm;
  border-left:3mm solid {T};padding-left:6mm}}
.row .bq span{{color:{T};margin-right:4mm}}
.scale{{flex:1 1 0;min-height:0;display:flex;gap:4mm}}
.cell{{flex:1;display:flex;flex-direction:column}}
.slot{{flex:1 1 auto;min-height:40mm;border:.8mm solid #9FB3C6;border-radius:2.5mm;
  background:#FFFFFF}}
.lb{{text-align:center;padding-top:3mm}}
.lb b{{display:block;font-size:40pt;font-weight:700;color:{B};line-height:1}}
.lb span{{display:block;font-size:16pt;margin-top:2mm}}
.bf{{flex:0 0 auto;border-top:1mm solid {B};padding-top:6mm;display:flex;gap:8mm;align-items:center}}
.bf .h{{flex:1;font-size:15pt;line-height:1.5}}
.bf .h b{{color:{B}}}
.bf .w{{flex:0 0 190mm;border:.7mm solid {M};padding:4mm 6mm;font-size:13pt;line-height:2}}
.bf .w b{{color:{B};display:inline-block;width:52mm}}
"""


def board(code, title, sub, qs, labels, place):
    rows = ""
    for n, q in qs:
        cells = "".join(f"<div class='cell'><div class='slot'></div><div class='lb'>{C.face(i, '17mm', t)}<span>{t}</span></div></div>"
                        for i, t in enumerate(labels, 1))
        rows += f"<div class='row'><div class='bq'><span>{n}</span>{q}</div><div class='scale'>{cells}</div></div>"
    return (f"<div class='bh'><div class='bb'>ACT Incheon · 인천 창의디자인 사회실험 · {code}</div>"
            f"<div class='bt'>{title}</div><div class='bs'>{sub}</div></div>"
            + rows)


YES5 = ["전혀 아니다", "아니다", "보통", "그렇다", "매우 그렇다"]


def boards_gulpo():
    ga = board("사전", "이 자리, 어떠세요?", "굴포천 다리 밑 공간을 지금 모습 그대로 평가해 주세요. 질문마다 스티커 한 장씩 붙여 주세요.",
               [("1", "머물고 싶을 만큼 매력적인가요?"), ("2", "지금 이 공간에 만족하시나요?"),
                ("3", "다음에도 다시 오고 싶나요?"), ("4", "여기에 작가 전시가 생기면 기대되나요?")],
               YES5, "굴포천")
    gb = board("1차 · 2차", "그림이 있는 이 자리,<br>어떠세요?", "오늘 이용해 보신 그대로 붙여 주세요.",
               [("1", "머물고 싶을 만큼 매력적인가요?"), ("2", "지금 이 공간에 만족하시나요?"),
                ("3", "다음에도 다시 오고 싶나요?"), ("4", "다른 다리 밑 공간도 이렇게 바뀌면 이용하고 싶나요?")],
               YES5, "굴포천")
    return [ga]  # 지금은 사전조사만 · 1·2차판(gb)은 1·2차 준비 때 [ga, gb]로 되돌린다


def boards_terminal():
    return [board("사전 · 1차 · 2차", "기다리는 이 자리,<br>어떠세요?", "2층 휴식공간을 이용해 보신 그대로 붙여 주세요.",
                  [("1", "지금 이 공간에 만족하시나요?"), ("2", "위생적이고 안심하고 쉴 수 있나요?")],
                  YES5, "연안여객터미널 2층")]


def build():
    out = []

    def mk(pages, name, size="A4"):
        f = C.render(pages, ROOT / name, size=size, margin=(9, 9, 11, 9), extra_css=CSS, footer="사전조사")
        out.append(f)

    def mixed(items, name, footer="사전조사"):
        """세로·가로가 섞인 거점 파일: 판형별로 뽑은 뒤 순서대로 합친다."""
        C.render_mixed(items, ROOT / name, extra_css=CSS, footer=footer)
        out.append(ROOT / name)

    (ROOT / "약산초_지도").mkdir(exist_ok=True)
    (ROOT / "약산초_지도" / "여기에 넣으세요.txt").write_text(
        "지도.jpg — Google 지도에서 학교 주변을 캡처하고 후보 위치에 번호(1, 2, 3 …)를 표시한 그림\n"
        "번호.txt — 한 줄에 하나씩 '1 정문 앞 횡단보도'처럼 쓰면 지도 아래 번호표에 들어갑니다\n"
        "「1차 실험」 · 「2차 실험」 폴더의 약산초_지도가 비어 있으면 이 지도를 그대로 씁니다\n")
    mk([overview()], "00_조사한눈에.pdf", "A4L")
    mk([rules()], "00_조사원수칙.pdf", "A4")
    mixed([yaksan_map()] + yaksan()[:1], "01_약산초등학교.pdf")
    mixed(seonin(), "02_선인재단.pdf")
    mixed(songdo(), "03_송도.pdf")
    mixed(gulpo(), "05_굴포천.pdf")
    mixed(rodeo(), "06_로데오거리.pdf")
    mixed(terminal(), "07_연안여객터미널.pdf")
    for pages, name in [(boards_gulpo(), "05_굴포천_폼보드.pdf"), (boards_china(), "04_차이나타운_폼보드.pdf")]:
        out.append(C.render(pages, ROOT / name, size="BOARDL" if "차이나타운" in name else "BOARD", margin=(25, 25, 25, 25), extra_css=BOARD_CSS))
    return out


from pathlib import Path

if __name__ == "__main__":
    for f in build():
        print(Path(f).name)
