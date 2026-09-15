# -*- coding: utf-8 -*-
"""사전조사 일정 · 「조사 방법 및 내용 등.hwpx」(2026.09.12 09:05 수정본) 조사 시기 표 기준"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = Path(__file__).resolve().parents[1] / "02_사전조사 일정.xlsx"
NAVY, TEAL, SOFT, WARN = "153C68", "009DAF", "EDF3F8", "FFF4E5"
F = "맑은 고딕"
thin = Side(style="thin", color="C3CFDB")
BD = Border(left=thin, right=thin, top=thin, bottom=thin)
SITE_COL = {"선인재단": "DCEBFA", "굴포천": "DDF3EA", "연안여객터미널": "E8E4F7",
            "로데오거리": "FCE3D6", "차이나타운": "FBEBC8", "송도글로벌캠퍼스": "F9DDE8"}


def hdr(ws, row, vals, widths=None):
    for i, v in enumerate(vals, 1):
        c = ws.cell(row, i, v)
        c.font = Font(name=F, bold=True, color="FFFFFF", size=10.5)
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BD
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def cell(ws, r, c, v, bold=False, fill=None, color="1B2735", center=False, size=10):
    x = ws.cell(r, c, v)
    x.font = Font(name=F, bold=bold, color=color, size=size)
    x.alignment = Alignment(horizontal="center" if center else "left", vertical="center", wrap_text=True)
    x.border = BD
    if fill: x.fill = PatternFill("solid", fgColor=fill)
    return x


def title(ws, t, sub):
    ws["A1"] = t; ws["A1"].font = Font(name=F, bold=True, size=15, color=NAVY)
    ws["A2"] = sub; ws["A2"].font = Font(name=F, size=9.5, color="5A6B7D")


wb = Workbook()

# ── 1. 사전조사 주간 (원 조사표 그대로 + 날짜 제안)
ws = wb.active; ws.title = "사전조사 주간"
title(ws, "사전조사 시간표", "원본: 「조사 방법 및 내용 등.hwpx」 조사 시기 표 (2026.09.12 09:05 수정본) · 날짜는 제안이며 확인 필요")
days = ["구분", "월\n9/14 (제안)", "화\n9/15", "수\n9/16", "목\n9/17 (제안)", "금\n9/18 예비"]
hdr(ws, 4, days, [9, 34, 16, 16, 30, 18])
people = ["인원", "성훈, 은영, 지윤, 지유", "은영, 지윤", "성훈, 은영, 지윤", "주호, 은영, 지윤", "—"]
for i, v in enumerate(people, 1):
    cell(ws, 5, i, v, bold=(i == 1), fill=SOFT, center=True)
plan = {  # (요일열, 시) : 내용  — 원 조사표 칸 그대로
    (2, 8): "선인재단 (5명)", (2, 9): "선인재단 (5명)",
    (2, 13): "굴포천 (2명)  ·  연안여객터미널 (3명)", (2, 14): "굴포천 (2명)  ·  연안여객터미널 (3명)",
    (2, 18): "로데오거리 (5명)", (2, 19): "로데오거리 (5명)",
    (5, 13): "차이나타운 (3명)", (5, 14): "차이나타운 (3명)",
    (5, 18): "송도글로벌캠퍼스 (3명)", (5, 19): "송도글로벌캠퍼스 (3명)",
}
r = 6
for h in range(5, 22):
    cell(ws, r, 1, f"{h:02d}", bold=True, fill=SOFT, center=True)
    for c in range(2, 7):
        v = plan.get((c, h), "")
        site = next((s for s in SITE_COL if s in v), None)
        cell(ws, r, c, v, fill=SITE_COL[site] if site else None, center=True, bold=bool(v))
    ws.row_dimensions[r].height = 22
    r += 1
r += 1
notes = [
    ("확인 필요", "연안여객터미널은 12~16시(4시간)로 진행하기로 했습니다. 조사표에는 월 13~14시로 되어 있어 표도 고칠지 확인합니다."),
    ("확인 필요", "월요일은 선인재단·로데오거리가 각 5명, 13~14시는 굴포천 2명 + 터미널 3명 = 5명인데, 인원 칸 명단은 4명입니다. 1명을 더 정하거나 역할을 줄여야 합니다."),
    ("확인 필요", "날짜는 이전 작성본의 사전조사 주간(9/14~18) 기준 제안입니다. 조사표에는 요일만 있습니다."),
    ("확인 필요", "선인재단 08·09시 칸은 학교 등교 시각과 맞는지 확인합니다. 등교가 끝나면 올라가는 학생이 거의 없습니다."),
    ("비어 있음", "화·수요일은 명단만 있고 배정된 조사가 없습니다. 비·결항 대체일이나 약산초 학교 협의(조사표에 시간 없음)에 쓸 수 있습니다."),
    ("동시 진행", "월 13~14시는 굴포천과 터미널이 같은 시간입니다. 두 곳 이동이 없도록 조를 나눠 출발합니다."),
]
for k, v in notes:
    cell(ws, r, 1, k, bold=True, fill=WARN, center=True, size=9)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    cell(ws, r, 2, v, size=9.5); ws.row_dimensions[r].height = 30
    r += 1
ws.freeze_panes = "B6"

# ── 2. 날짜별 할 일
ws = wb.create_sheet("날짜별 할 일")
title(ws, "날짜별 할 일", "현장에 가져갈 종이는 「사전조사 준비물」의 거점 파일 · 담당자 칸은 비워 두었습니다(명단 확정 후 기입)")
hdr(ws, 4, ["날짜", "시간", "거점", "인원", "현장에서 할 일", "뽑아갈 종이", "담당자", "완료"],
    [13, 11, 16, 7, 50, 30, 16, 7])
todo = [
    ("9/12 (토)", "—", "사무실", "", "인쇄 파일 확정 · 폼보드 2판(굴포천 사전판 · 차이나타운판) 출력 주문 — 굴포천은 월 13시 전, 차이나타운은 목 13시 전", "보드_출력파일 폴더", "", ""),
    ("9/12 (토)", "—", "사무실", "", "터미널·굴포천·선인재단 관리 쪽에 방문 시간 알리기 · 로데오 상인회 연락", "", "", ""),
    ("9/13 (일)", "—", "사무실", "", "종이 인쇄 · 스티커 문항별 색으로 나눠 담기 · 클립보드 챙기기", "03_거점별 준비물", "", ""),
    ("9/14 (월)", "08~09시대", "선인재단", "5", "기록지(5명 공통): 인원수 · 시각 · 동선(왼/오) · 행태 · 힘들어 보이는 정도", "02_선인재단 (위치 1~5, 5장)", "", ""),
    ("9/14 (월)", "13~14시대", "굴포천", "2", "고정 카메라 녹화(기준점 촬영 · 시각 맞추기) · 머문 무리 기록지 · 사전 스티커판", "05_굴포천 · 폼보드 사전판", "", ""),
    ("9/14 (월)", "12~16시", "연안여객터미널", "3", "2층: 앉은·일어난 시각 · 의자 번호 · 만족도 · 위생·안심도(물어서) / 1층: 15분마다 캐리어 안·밖", "07_연안여객터미널 (2쪽) · 좌석 배치도", "", ""),
    ("9/14 (월)", "18~19시대", "로데오거리", "5", "피우는 사람 한 줄씩: 어디서 · 몸 방향 · 꽁초 동그라미", "06_로데오거리", "", ""),
    ("9/15 (화)", "—", "예비", "", "비 온 날 대체 · 월요일 종이 입력(08_입력용_기록부)", "", "", ""),
    ("9/16 (수)", "—", "예비", "", "약산초 학교 협의 · 설문지 배포 일정 잡기", "01_약산초등학교", "", ""),
    ("9/17 (목)", "13~14시대", "차이나타운", "3", "스티커 보드(Q1~Q4, 기존 안내 기준)", "04_차이나타운_폼보드", "", ""),
    ("9/17 (목)", "18~19시대", "송도글로벌캠퍼스", "3", "구간마다 들어온 무리 기록(인원수 · 시각 · 행위) · 중간에 인터뷰(참여 의향 · 소통 기대 · 이유 · 필요한 것)", "03_송도 (2쪽)", "", ""),
    ("9/18 (금)", "—", "사무실", "", "전체 입력 · 사진 정리(거점_회차_날짜) · 1차 준비 회의", "", "", ""),
]
for i, row in enumerate(todo, 5):
    site = next((s for s in SITE_COL if s == row[2]), None)
    for j, v in enumerate(row, 1):
        cell(ws, i, j, v, fill=(SITE_COL[site] if site and j == 3 else None), center=(j in (1, 2, 4, 8)), bold=(j == 3))
    ws.row_dimensions[i].height = 32
ws.freeze_panes = "A5"

# ── 3. 전체 흐름 (제안)
ws = wb.create_sheet("전체 흐름")
title(ws, "전체 흐름 (제안)", "이전 작성본(21_조사설계와현장운영)의 제안 일정 · 확정 아님 · 휴일·학교·기관 일정 확인 후 조정")
weeks = ["9/14", "9/21", "9/28", "10/5", "10/12", "10/19", "10/26"]
hdr(ws, 4, ["단계", "기간", *[f"{w} 주" for w in weeks], "비고"], [20, 16, *[9] * len(weeks), 40])
flow = [
    ("사전조사 · 현장 실측", "9/14~9/18", [0], "이번 주"),
    ("제작 · 부착 시험", "9/21~9/23", [1], "원상복구 가능 여부 확인"),
    ("1차 실험", "9/28~10/2", [2], "추석 연휴 확인 필요"),
    ("2차 실험 · 누락 보완", "10/5~10/16", [3, 4], "약산초는 학교 일정 따로"),
    ("분석 · 성과 공유", "10월 하순~", [5, 6], ""),
]
for i, (a, b, ws_, note) in enumerate(flow, 5):
    cell(ws, i, 1, a, bold=True); cell(ws, i, 2, b, center=True)
    for j in range(len(weeks)):
        cell(ws, i, 3 + j, "", fill=(TEAL if j in ws_ else None))
    cell(ws, i, 3 + len(weeks), note, size=9.5)
    ws.row_dimensions[i].height = 24

wb.save(OUT); print(OUT.name, wb.sheetnames)
