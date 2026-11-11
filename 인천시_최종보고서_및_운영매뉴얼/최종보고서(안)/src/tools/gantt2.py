#!/usr/bin/env python3
"""Ⅰ장 p16 실험 캘린더(간트) 생성기 — STYLE_2 판.
원본: scratchpad/gen/gantt.py (v1). 구도·행·날짜는 그대로 두고 색·채움·선만 바꾼다.
- 사전조사 = 빗살(중간 블루) / 1차 = 솔리드 포인트 블루 / 재실험 = 빗살(포인트 블루, 점선 외곽선 대신)
- 2차(현재) = 솔리드 남색 / 미정(송도 2차) = 붉은 빗살(점선 외곽선 대신)
- 막대·범례 칩에 외곽선 없음, 모서리 0.3
사용: python3 gantt2.py <part2_1장.html>   (<!--GANTT-->…<!--/GANTT--> 사이를 교체)
"""
import sys, re, datetime as dt
path = sys.argv[1]
D0 = dt.date(2026, 9, 1); N = 91
X0, X1 = 38, 178; W = (X1 - X0) / N
def x(m, d): return X0 + ((dt.date(2026, m, d) - D0).days) * W

NAVY, BLUE, BLUE_D, BLUE_L, RED = "#1A2F4B", "#2E5A87", "#22476C", "#7D97B3", "#E5332A"
F_SAFE, F_INCL, F_ATTR, F_CONV = "#3A5F8E", "#3F7A6E", "#A67C45", "#675F8C"
rows = [
 ("01","약산초등학교",F_SAFE,[("pre",(9,17),(9,17))],[("1st",(10,20),(10,22)),("redo",(10,27),(10,29))],[("2nd",(11,3),(11,5))],"현장조사 7.29·8.11·8.27·9.15"),
 ("02","선인재단",F_SAFE,[("pre",(10,15),(10,15))],[("1st",(11,10),(11,12))],[("2nd",(11,17),(11,19))],"현장조사 9.14·9.23"),
 ("03","송도 캠퍼스타운역",F_INCL,[("pre",(10,23),(10,24))],[("1st",(11,20),(11,21))],[("dum",(11,27),(11,28))],"현장조사 9.23·10.7"),
 ("04","차이나타운",F_INCL,[("pre",(9,17),(9,17))],[("1st",(11,5),(11,5))],[("2nd",(11,6),(11,6))],"현장조사 7.29·8.24"),
 ("05","굴포천",F_ATTR,[("pre",(9,17),(9,17)),("pre",(10,17),(10,17))],[("1st",(11,21),(11,22))],[("2nd",(11,23),(11,23))],"현장조사 7.29·9.9·9.29"),
 ("06","로데오거리",F_CONV,[("pre",(9,14),(9,14))],[("1st",(11,15),(11,17))],[("2nd",(11,18),(11,21))],"현장조사 7.29·8.27·9.29"),
 ("07","연안여객터미널",F_CONV,[("pre",(9,14),(9,14))],[("1st",(11,11),(11,12))],[("2nd",(11,13),(11,14))],"현장조사 7.29·8.11·10.7"),
]
FILL = {"pre": "url(#g-hatch-pre)", "1st": BLUE, "redo": "url(#g-hatch-redo)", "2nd": NAVY, "dum": "url(#g-hatch-red)"}
LBL = {"pre": "#5C6F84", "1st": BLUE_D, "redo": BLUE_D, "2nd": NAVY}
RX = ".3"
H0 = 18; RH = 13.5; H = H0 + RH * len(rows) + 2

def hatch(pid, col, sw=".3", gap=1.3):
    return (f'<pattern id="{pid}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="{gap}" height="{gap}" fill="#fff"/><rect width="{sw}" height="{gap}" fill="{col}"/></pattern>')

o = [f'<svg viewBox="0 0 178 {H}" width="178mm" height="{H}mm" font-family="P">',
     '<defs>' + hatch("g-hatch-pre", BLUE_L) + hatch("g-hatch-redo", BLUE) + hatch("g-hatch-red", RED) + '</defs>']
# 주말 음영
for i in range(N):
    d = D0 + dt.timedelta(i)
    if d.weekday() >= 5:
        o.append(f'<rect x="{X0+i*W:.2f}" y="{H0-2}" width="{W:.2f}" height="{H-H0+2}" fill="#F3F6F8"/>')
# 월 경계선·라벨
for (m, lab) in [(9, "9월"), (10, "10월"), (11, "11월")]:
    xx = x(m, 1)
    o.append(f'<line x1="{xx:.2f}" x2="{xx:.2f}" y1="10" y2="{H}" stroke="{NAVY}" stroke-width=".3"/>')
    o.append(f'<text x="{xx+1.2:.2f}" y="14" font-size="3.6" font-weight="900" fill="{BLUE}">{lab}</text>')
o.append(f'<line x1="{X1}" x2="{X1}" y1="10" y2="{H}" stroke="{NAVY}" stroke-width=".3"/>')
# 범례 — 막대와 같은 채움
lx = 38
for k, lab in [("pre", "사전조사"), ("1st", "1차"), ("redo", "재실험"), ("2nd", "2차")]:
    o.append(f'<rect x="{lx}" y="1.6" width="4" height="2.4" rx="{RX}" fill="{FILL[k]}"/>')
    o.append(f'<text x="{lx+5}" y="3.7" font-size="2.6" font-weight="700" fill="{NAVY}">{lab}</text>')
    lx += 6 + len(lab) * 2.7 + 3
o.append(f'<text x="{X1}" y="3.7" font-size="2.3" font-weight="600" fill="#8C98A3" text-anchor="end">회색 열 = 주말(토·일)</text>')

def lbl(a, b):
    s = f"{a[0]}.{a[1]}"
    if b != a: s += f"~{b[1]}" if b[0] == a[0] else f"~{b[0]}.{b[1]}"
    return s

for r, (no, name, col, pre, first, second, field) in enumerate(rows):
    y = H0 + r * RH; cy = y + RH / 2
    o.append(f'<line x1="0" x2="{X1}" y1="{y:.2f}" y2="{y:.2f}" stroke="#D3DCE3" stroke-width=".25"/>')
    o.append(f'<circle cx="2.2" cy="{cy-1.6:.2f}" r="1.5" fill="{col}"/>')
    o.append(f'<text x="5" y="{cy-.6:.2f}" font-size="3.4" font-weight="800" fill="{NAVY}">{name}</text>')
    o.append(f'<text x="5" y="{cy+3.4:.2f}" font-size="2.3" font-weight="600" fill="#8C98A3">{field}</text>')
    for kind, a, b in pre + first + second:
        xa = x(*a); xb = x(*b) + W; w = max(xb - xa, 1.6)
        o.append(f'<rect x="{xa:.2f}" y="{cy-1.8:.2f}" width="{w:.2f}" height="3.6" rx="{RX}" fill="{FILL[kind]}"/>')
        if kind == "dum":
            o.append(f'<text x="{xa+w/2:.2f}" y="{cy+5.6:.2f}" font-size="2.4" font-weight="800" fill="{RED}" text-anchor="middle">11.[00]</text>'); continue
        if kind == "redo":
            o.append(f'<text x="{xa+w:.2f}" y="{cy+5.6:.2f}" font-size="2.3" font-weight="700" fill="{BLUE_D}" text-anchor="end">{lbl(a,b)}</text>'); continue
        above = kind in ("pre", "1st")
        ty = cy - 3 if above else cy + 5.6
        anchor = "end" if (kind == "1st" and second and second[0][1][0] == 11 and (x(*second[0][1]) - xb) < 9) else "middle"
        tx = xb if anchor == "end" else xa + w / 2
        if no == "01" and kind == "2nd": anchor = "start"; tx = xa
        o.append(f'<text x="{tx:.2f}" y="{ty:.2f}" font-size="2.4" font-weight="800" fill="{LBL[kind]}" text-anchor="{anchor}">{lbl(a,b)}</text>')
    if no == "01":
        xs = x(11, 6) + W / 2
        o.append(f'<path d="M{xs:.2f} {cy-1.6:.2f} l1.4 1.6 -1.4 1.6 -1.4 -1.6z" fill="{BLUE_L}"/>')
        o.append(f'<text x="{xs+2:.2f}" y="{cy-2.6:.2f}" font-size="2.2" font-weight="700" fill="{NAVY}">11.6 학교 설문</text>')
o.append(f'<line x1="0" x2="{X1}" y1="{H0+RH*len(rows):.2f}" y2="{H0+RH*len(rows):.2f}" stroke="{NAVY}" stroke-width=".35"/>')
o.append('</svg>')
svg = "\n".join(o)
s = open(path, encoding='utf-8').read()
s = re.sub(r'<!--GANTT-->.*?<!--/GANTT-->|<!--GANTT-->', lambda m: '<!--GANTT-->' + svg + '<!--/GANTT-->', s, count=1, flags=re.S)
open(path, 'w', encoding='utf-8').write(s)
print("ok", H)
