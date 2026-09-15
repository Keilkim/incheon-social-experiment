# -*- coding: utf-8 -*-
"""사전조사 입력용 기록부 · 현장 종이와 같은 칸 순서"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
BASE = ["날짜", "회차", "시간", "조사자"]
SHEETS = [
 ("약산초_설문", ["날짜", "회차", "번호", "학년", "반", "사진번호", "봤나(봄/못봄/모름/안다님)", "어디서(지도번호)", "어떻게 말할지(원문)", "워크숍 참여", "메모"]),
 ("선인재단_기록", ["날짜", "회차", "조사자", "위치", "번호", "인원수", "시각", "동선", "휴대폰 봄", "대화", "앞만 봄", "그냥 올라감", "뛰어놂", "관찰함", "힘들어 보이는 정도 1~5", "비고"]),
 ("선인재단_짝맞춤", ["날짜", "회차", "출발 번호", "도착 번호", "출발 시각", "도착 시각", "걸린 초", "확실함 O/△", "메모"]),
 ("송도_기록", ["날짜", "회차", "조사자", "구간", "번호", "인원수", "시각", "걷기", "달리기", "뛰다가 숨고르기", "구경하기", "휴대폰하고 놀기", "비고"]),
 ("송도_인터뷰", ["날짜", "회차", "조사자", "번호", "Q1 참여 의향 O/△/X", "Q2 소통 기대 O/△/X", "Q3 이유(원문)", "Q4 필요한 것(원문)", "비고"]),
 ("굴포천_기록", ["날짜", "회차", "조사자", "번호", "인원수", "들어온 시각", "나간 시각", "뛰기", "걷기", "놀기", "앉아서 쉬기(휴대폰X)", "앉아서 쉬기(휴대폰O)", "대화", "비고"]),
 ("굴포천_영상결과", ["날짜", "회차", "추적번호", "처음 보인 시각", "마지막 시각", "머문 초", "멈춘 초", "중앙 속도(m/s)", "들른 구역", "자전거·킥보드", "메모"]),
 ("굴포천_지나감_예비", ["날짜", "회차", "조사자", "그냥 지나간 사람(카메라 안 될 때)", "메모"]),
 ("로데오_사람", ["날짜", "회차", "조사자", "번호", "시각", "어디서(부스안/벤치/그밖)", "몸 방향(안쪽/바깥/?)", "꽁초(수거함/바닥/?)", "메모"]),
 ("터미널_2층", ["날짜", "회차", "조사자", "번호", "앉은 시각", "일어난 시각", "쉰 분", "자리 위치(의자 번호)", "만족도 1~5", "위생·안심도 1~5", "비고"]),
 ("터미널_1층캐리어", ["날짜", "회차", "조사자", "번호", "시각", "보관 공간 내 개수", "보관 공간 외 개수", "비고"]),
 ("스티커_폼보드", ["날짜", "회차", "거점", "문항", "1", "2", "3", "4", "5", "스티커 받은 사람", "메모"]),
]

wb = Workbook(); ws = wb.active; ws.title = "사용법"
for r in [["입력용 기록부 · 사전조사", "2026.09.12"],
          ["어떻게", "현장 종이의 칸 순서 그대로 옮겨 적습니다. 正은 숫자로 바꿔 적습니다(正 = 5)."],
          ["인원수", "종이에 비워 둔 인원수는 1로 입력합니다. 2명 이상이면 적힌 숫자를 씁니다. 한 줄 = 혼자 온 사람 또는 무리."],
          ["시각", "08:12:34처럼 시:분:초로 입력합니다."],
          ["행태 · 행위 칸", "✓ 표시는 1, 빈칸은 0으로 입력합니다(순서는 적지 않음)."],
          ["빈칸과 0", "못 봤거나 안 한 칸은 비워 두고, 봤는데 한 명도 없으면 0을 적습니다."],
          ["기호", "O 예 · X 아니오 · ? 모름 · – 안 물어봄"],
          ["선인재단", "기록 시트에 위치 번호(1 출발 · 2~4 중간 · 5 도착)와 함께 입력합니다. 출발 줄과 도착 줄을 같은 무리로 맞춰 짝맞춤 시트에 적으면 걸린 초가 자동 계산됩니다."],
          ["스티커", "문항마다 칸별 스티커 수를 적습니다. 보기가 1~5가 아닌 문항(봤나 · 그림)은 왼쪽 보기부터 1, 2, 3 …으로 적습니다."],
          ["영상결과", "굴포천 카메라 영상을 YOLO + ByteTrack으로 분석한 결과를 붙여 넣습니다. 한 줄 = 추적 번호 하나(사람 수보다 많을 수 있음)."],
          ["개인정보", "이름 · 연락처는 적지 않습니다."]]:
    ws.append(r)
ws.column_dimensions["A"].width = 14; ws.column_dimensions["B"].width = 90

for name, heads in SHEETS:
    w = wb.create_sheet(name); w.append(heads)
    if "회차" in heads:
        dv = DataValidation(type="list", formula1='"사전,1차,2차"', allow_blank=True)
        w.add_data_validation(dv)
        col = w.cell(1, heads.index("회차") + 1).column_letter
        dv.add(f"{col}2:{col}2000")
    for i, h in enumerate(heads, 1):
        w.column_dimensions[w.cell(1, i).column_letter].width = 26 if ("원문" in h or "메모" in h or "그렸나" in h) else max(10, len(h) * 1.6 + 4)
    w.freeze_panes = "A2"

# 선인재단: 시각 칸은 hh:mm:ss, 짝맞춤은 걸린 초 자동 계산
for w in wb:
    heads = [c.value for c in w[1]]
    for ci, h in enumerate(heads, 1):
        if h and "시각" in h:
            for r in range(2, 1001): w.cell(r, ci).number_format = "hh:mm:ss"
    if w.title == "선인재단_짝맞춤":
        for r in range(2, 501):
            w.cell(r, 7, f'=IF(AND(E{r}<>"",F{r}<>""),ROUND((F{r}-E{r})*86400,0),"")')

for w in wb:
    for c in w[1]:
        c.font = Font(name="맑은 고딕", bold=True, color="FFFFFF", size=10.5)
        c.fill = PatternFill("solid", fgColor="153C68")
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    w.row_dimensions[1].height = 34
for c in wb["사용법"]["A"]:
    c.font = Font(name="맑은 고딕", bold=True, color="153C68")
wb["사용법"]["A1"].font = Font(name="맑은 고딕", bold=True, color="FFFFFF", size=12)

out = ROOT / "08_입력용_기록부.xlsx"
wb.save(out); print(out.name, "·", len(wb.sheetnames), "시트")
