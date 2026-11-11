"""Open diagrams: shapes describe relationships rather than contain paragraphs."""

def draw(p, index, *, M, CW, W, INK, MUTED, WHITE):
    def caption(t):
        p.text(t, M, 214, CW, 17, 9.4, bold=True, color=MUTED, leading=13)

    if index == 1:
        caption('시민안과 어린이안을 같은 사진·지도 질문으로 비교')
        sw = (CW-32)/2
        for j, (title, terms) in enumerate([
            ('1차  색연필 수비대', ['색', '형태', '문구']),
            ('2차  꿈꾸는 안전디자이너', ['동물', '색', '완충재']),
        ]):
            xx = M+j*(sw+32)
            p.centered(title, xx, 246, sw, 19, size=10.3, bold=True, color=p.accent, leading=14)
            for k, term in enumerate(terms):
                cx = xx+sw/2+(k-1)*64
                p.circle(cx, 302, 23, p.tint)
                p.centered(term, cx-23, 279, 46, 46, size=10.7, bold=True, color=p.accent)
        p.centered('같은 문항으로 묻는 것', M, 345, CW, 15, size=8.6, color=MUTED, leading=12)
        p.centered('시설물 인지  ·  지도 위치 선택  ·  위치 설명 단서',
                   M, 367, CW, 19, size=10.2, bold=True, color=p.accent, leading=14)

    elif index == 2:
        caption('1차의 요소별 선호를 반영한 뒤, 2차에서 조형물 전체를 경험')
        lw = 167
        p.text('1차  마음, 바라봄', M, 249, lw, 19, 10.4, bold=True, color=p.accent, leading=14)
        for j, term in enumerate(['색·거울·긍정 문구의 선호', '선택 이유', '통학로에 바라는 점']):
            yy = 285+j*25
            p.circle(M+3, yy+6, 2.2, p.accent)
            p.text(term, M+14, yy, lw-14, 17, 9.5, leading=13)
        p.text('요소별 응답 집계', M+14, 368, lw-14, 15, 8.6, color=MUTED, leading=12)
        p.centered('색·문구 등\n디자인 반영', M+173, 264, 76, 31,
                   size=8.7, color=p.accent, bold=True, leading=13)
        p.arrow(M+178, 316, M+249, 316)
        rx = M+260
        rw = CW-260
        p.centered('2차  마음, 마주봄', rx, 249, rw, 19, size=10.4, bold=True,
                   color=p.accent, leading=14)
        p.ellipse(rx+rw/2, 326, rw/2, 56, p.tint)
        half = rw/2
        for j, (title, desc) in enumerate([
            ('거울나무 경험', '기분 변화\n응원받는 느낌'),
            ('설치 장소 의견', '설치 희망 장소\n선택한 이유'),
        ]):
            x = rx+j*half
            p.centered(title, x+3, 294, half-6, 20, size=9.8, bold=True,
                       color=p.accent, leading=14)
            p.centered(desc, x+4, 325, half-8, 33, size=9.2, leading=15)

    elif index == 3:
        caption('그림과 문자 안내의 기억·부담·교류 경험을 비교')
        sw = (CW-32)/2
        for j, (phase, title, sub) in enumerate([
            ('1차', '그림 안내', '주먹 인사·하이파이브 등'),
            ('2차', '문자 안내', '같은 행동을 영문·한국어로'),
        ]):
            xx = M+j*(sw+32)
            p.centered(phase, xx, 241, sw, 16, size=9.0, color=MUTED, leading=12)
            p.centered(title, xx, 263, sw, 33, size=22, bold=True, color=p.accent, leading=28)
            p.centered(sub, xx, 304, sw, 16, size=9.0, color=MUTED, leading=13)
        p.centered('공통 평가: 기억에 남는 안내 · 부담 정도 · 교류에 도움이 된 정도',
                   M, 331, CW, 16, size=8.8, color=p.accent, leading=12)
        xs = [M+40+i*(CW-80)/3 for i in range(4)]
        p.line(xs[0], 366, xs[-1], 366, p.accent, .7)
        for i, cx in enumerate(xs):
            p.circle(cx, 366, 3.4, p.accent)
            p.centered(['시작점', '중간 지점 1', '중간 지점 2', '끝점'][i], cx-43, 377, 86, 14,
                       size=8.3, color=MUTED, leading=11)

    elif index == 4:
        caption('권유형·금지형 각각에서 1컷과 3컷을 비교')
        x0 = M+112
        x1 = M+219
        p.centered('단일형  1컷', x0, 245, 87, 18, size=9.6, bold=True, color=p.accent, leading=13)
        p.centered('연속형  3컷', x1, 245, 87, 18, size=9.6, bold=True, color=p.accent, leading=13)
        for j, title in enumerate(['1차  권유형', '2차  금지형']):
            yy = 286+j*52
            p.text(title, M, yy-8, 105, 18, 10.4, bold=True, color=p.accent, leading=14)
            # These are actual comic frames; the surrounding grid is intentionally open.
            p.rect(x0+26, yy-12, 35, 24, WHITE, stroke=p.accent)
            for k in range(3):
                p.rect(x1+7+k*25, yy-12, 19, 24, WHITE, stroke=p.accent)
            p.arrow(M+316, yy, M+344, yy)
        ox = M+359
        p.text('선택 수·비율', ox, 274, CW-359, 24, 13.0, bold=True, color=p.accent, leading=19)
        p.text('이해도·경각심', ox, 308, CW-359, 22, 11.2, bold=True, color=p.accent, leading=16)
        p.text('각 형식의 5점 평가', ox, 341, CW-359, 17, 9.1, color=MUTED, leading=13)
        p.text('같은 3개 주제 · 같은 설문 문항과 척도', M+112, 376, CW-112, 15,
               8.7, color=MUTED, leading=12)

    elif index == 5:
        caption('휴게시설만 운영한 1차와 맞은편 프로그램을 더한 2차 비교')
        facility = M+102
        other = M+322
        p.text('휴게시설 구역', facility, 244, 149, 17, 9.4, bold=True, color=p.accent, leading=13)
        p.text('맞은편 프로그램 구역', other, 244, CW-322, 17, 9.4,
               bold=True, color=p.accent, leading=13)
        for j, (a, b) in enumerate([
            ('휴게시설 운영', '프로그램 없음'),
            ('같은 시설 유지', '스툴 꾸미기 운영'),
        ]):
            yy = 280+j*57
            p.text(['1차', '2차'][j], M, yy-3, 40, 23, 15.5,
                   bold=False, color=p.accent, leading=20)
            # A minimal parasol describes the fixed facility rather than a decorative frame.
            cx = facility-28
            p.curve([(cx-12, yy+2), (cx-8, yy-13), (cx+8, yy-13), (cx+12, yy+2)], p.accent, .9)
            p.line(cx-12, yy+2, cx+12, yy+2, p.accent, .9)
            p.line(cx, yy+2, cx, yy+18, p.accent, .9)
            p.line(cx-6, yy+18, cx+6, yy+18, p.accent, .9)
            p.text(a, facility, yy, 153, 20, 11.0, bold=j == 1, leading=15)
            p.text(b, other, yy, CW-322, 20, 11.0, bold=j == 1,
                   color=INK if j == 1 else MUTED, leading=15)
        p.centered('휴게시설의 이용 인원·비율 · 멈춤률 · 체류시간 비교',
                   M, 371, CW, 18, size=10.3, bold=True, color=p.accent, leading=14)
        p.centered('2차는 프로그램 운영 전·중·후를 나누어 기록',
                   M, 393, CW, 12, size=8.4, color=MUTED, leading=11)

    elif index == 6:
        caption('공간 조성 뒤 같은 환경을 유지하고, 2차에 유도사인 추가')
        p.centered('1차  거리 휴식 공간과 광장 흡연공간 조성', M, 241, CW, 18,
                   size=9.6, bold=True, color=p.accent, leading=13)
        left = M+103
        right = W-M-103
        for cx, title, sub in [(left, '거리', '바이오필릭 휴식 공간'),
                               (right, '광장', '흡연공간')]:
            p.circle(cx, 310, 43, p.tint)
            p.centered(title, cx-40, 284, 80, 25, size=16.0, bold=True, color=p.accent, leading=22)
            p.centered(sub, cx-72, 324, 144, 16, size=8.8, color=MUTED, leading=12)
        p.centered('2차  안내사인 추가', left+49, 280, right-left-98, 18,
                   size=9.3, bold=True, color=p.accent, leading=13)
        p.arrow(left+54, 313, right-54, 313)
        p.centered('1분 → 30초 → 15초', left+47, 349, right-left-94, 16,
                   size=8.7, color=MUTED, leading=12)
        p.centered('사전·1차·2차 공통 관찰: 거리 흡연자 수 · 광장 안·밖 흡연 인원',
                   M, 371, CW, 17, size=9.5, bold=True, color=p.accent, leading=13)
        p.centered('2차에는 사인 인지 · 흡연공간으로의 이동도 확인',
                   M, 393, CW, 12, size=8.4, color=MUTED, leading=11)
