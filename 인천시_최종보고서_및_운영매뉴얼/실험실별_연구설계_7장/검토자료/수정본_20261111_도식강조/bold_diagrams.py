"""Large, open central diagrams with subordinate supporting information."""

def draw(p, index, *, M, CW, W, INK, MUTED, WHITE):
    def caption(t):
        p.text(t, M, 192, CW, 17, 9.7, bold=True, color=MUTED, leading=13)

    if index == 1:
        caption('시민안과 어린이안을 같은 사진·지도 질문으로 비교')
        sw = (CW-32)/2
        for j, (title, terms) in enumerate([
            ('1차  색연필 수비대', ['색', '형태', '문구']),
            ('2차  꿈꾸는 안전디자이너', ['동물', '색', '완충재']),
        ]):
            xx = M+j*(sw+32)
            p.centered(title, xx, 236, sw, 23, size=12.1, bold=True, color=p.accent, leading=17)
            for k, term in enumerate(terms):
                cx = xx+sw/2+(k-1)*78
                p.circle(cx, 315, 33, p.tint)
                p.centered(term, cx-33, 282, 66, 66, size=15.0, bold=True, color=p.accent)
        p.centered('같은 사진·지도 문항으로 묻는 것', M, 386, CW, 18,
                   size=10.3, color=MUTED, leading=14)
        p.centered('시설물 인지  ·  위치 선택  ·  설명 단서',
                   M, 419, CW, 30, size=17.0, bold=True, color=p.accent, leading=24)

    elif index == 2:
        caption('1차의 요소별 선호를 반영한 뒤, 2차에서 조형물 전체를 경험')
        lw = 158
        p.text('1차  마음, 바라봄', M, 235, lw, 23, 12.0, bold=True, color=p.accent, leading=17)
        p.text('요소별 선호', M, 288, lw, 30, 19.4, bold=True, color=p.accent, leading=27)
        p.text('색·거울·긍정 문구', M, 329, lw, 18, 10.5, leading=15)
        p.text('선택 이유와\n통학로에 바라는 점', M, 367, lw, 37, 10.8, leading=17)
        p.text('요소별 응답 집계', M, 429, lw, 16, 9.0, color=MUTED, leading=12)
        p.centered('디자인 반영', M+160, 313, 66, 16,
                   size=8.7, color=p.accent, bold=True, leading=12)
        p.arrow(M+164, 344, M+210, 344)
        rx = M+224
        rw = CW-224
        p.centered('2차  마음, 마주봄', rx, 235, rw, 23, size=12.0,
                   bold=True, color=p.accent, leading=17)
        p.ellipse(rx+rw/2, 354, rw/2, 83, p.tint)
        half = rw/2
        for j, (title, desc) in enumerate([
            ('거울나무 경험', '기분 변화\n응원받는 느낌'),
            ('설치 장소 의견', '설치 희망 장소\n선택한 이유'),
        ]):
            x = rx+j*half
            p.centered(title, x+3, 314, half-6, 26, size=12.0, bold=True,
                       color=p.accent, leading=17)
            p.centered(desc, x+6, 359, half-12, 40, size=10.9, leading=18)
        p.centered('선호한 요소를 조합한 거울나무 전체의 경험 확인',
                   M, 465, CW, 17, size=10.0, color=p.accent, leading=14)

    elif index == 3:
        caption('그림과 문자 안내의 기억·부담·교류 경험을 비교')
        sw = (CW-32)/2
        for j, (phase, title, sub) in enumerate([
            ('1차', '그림 안내', '주먹 인사·하이파이브 등'),
            ('2차', '문자 안내', '같은 행동을 영문·한국어로'),
        ]):
            xx = M+j*(sw+32)
            p.centered(phase, xx, 233, sw, 19, size=10.7, color=MUTED, leading=15)
            p.centered(title, xx, 270, sw, 45, size=30.0, bold=True, color=p.accent, leading=39)
            p.centered(sub, xx, 333, sw, 19, size=10.5, color=MUTED, leading=15)
        p.centered('공통 평가: 기억에 남는 안내 · 부담 정도 · 교류에 도움이 된 정도',
                   M, 383, CW, 19, size=10.2, color=p.accent, leading=14)
        xs = [M+40+i*(CW-80)/3 for i in range(4)]
        p.line(xs[0], 439, xs[-1], 439, p.accent, 1.25)
        for i, cx in enumerate(xs):
            p.circle(cx, 439, 5.0, p.accent)
            p.centered(['시작점', '중간 지점 1', '중간 지점 2', '끝점'][i], cx-45, 459, 90, 16,
                       size=9.4, color=MUTED, leading=13)

    elif index == 4:
        caption('권유형·금지형 각각에서 1컷과 3컷을 비교')
        x0 = M+109
        x1 = M+228
        p.centered('단일형  1컷', x0, 241, 95, 21, size=11.5, bold=True, color=p.accent, leading=16)
        p.centered('연속형  3컷', x1, 241, 95, 21, size=11.5, bold=True, color=p.accent, leading=16)
        for j, title in enumerate(['1차  권유형', '2차  금지형']):
            yy = 309+j*84
            p.text(title, M, yy-10, 107, 22, 12.5, bold=True, color=p.accent, leading=18)
            p.rect(x0+24, yy-19, 47, 38, WHITE, stroke=p.accent)
            for k in range(3):
                p.rect(x1+6+k*29, yy-19, 24, 38, WHITE, stroke=p.accent)
            p.arrow(M+333, yy, M+356, yy)
        ox = M+371
        p.text('선택 수·비율', ox, 298, CW-371, 26, 16.4, bold=True, color=p.accent, leading=23)
        p.text('이해도·경각심', ox, 345, CW-371, 25, 14.1, bold=True, color=p.accent, leading=20)
        p.text('각 형식의 5점 평가', ox, 391, CW-371, 19, 10.0, color=MUTED, leading=14)
        p.text('같은 3개 주제 · 같은 설문 문항과 척도', M+109, 463, CW-109, 17,
               9.5, color=MUTED, leading=13)

    elif index == 5:
        caption('휴게시설만 운영한 1차와 맞은편 프로그램을 더한 2차 비교')
        facility = M+112
        other = M+322
        p.text('휴게시설 구역', facility, 239, 151, 21, 11.3, bold=True, color=p.accent, leading=16)
        p.text('맞은편 프로그램 구역', other, 239, CW-322, 21, 11.3,
               bold=True, color=p.accent, leading=16)
        for j, (a, b) in enumerate([
            ('휴게시설 운영', '프로그램 없음'),
            ('같은 시설 유지', '스툴 꾸미기 운영'),
        ]):
            yy = 298+j*78
            p.text(['1차', '2차'][j], M, yy-7, 48, 32, 23.0,
                   color=p.accent, leading=29)
            cx = facility-35
            p.curve([(cx-17, yy+1), (cx-12, yy-21), (cx+12, yy-21), (cx+17, yy+1)], p.accent, 1.3)
            p.line(cx-17, yy+1, cx+17, yy+1, p.accent, 1.3)
            p.line(cx, yy+1, cx, yy+25, p.accent, 1.3)
            p.line(cx-8, yy+25, cx+8, yy+25, p.accent, 1.3)
            p.text(a, facility, yy, 163, 26, 14.0, bold=j == 1, leading=20)
            p.text(b, other, yy, CW-322, 26, 14.0, bold=j == 1,
                   color=INK if j == 1 else MUTED, leading=20)
        p.centered('휴게시설의 이용 인원·비율 · 멈춤률 · 체류시간 비교',
                   M, 440, CW, 24, size=12.5, bold=True, color=p.accent, leading=18)
        p.centered('2차는 프로그램 운영 전·중·후를 나누어 기록',
                   M, 476, CW, 16, size=9.4, color=MUTED, leading=13)

    elif index == 6:
        caption('공간 조성 뒤 같은 환경을 유지하고, 2차에 유도사인 추가')
        p.centered('1차  거리 휴식 공간과 광장 흡연공간 조성', M, 227, CW, 21,
                   size=11.4, bold=True, color=p.accent, leading=16)
        left = M+92
        right = W-M-92
        for cx, title, sub in [(left, '거리', '바이오필릭 휴식 공간'),
                               (right, '광장', '흡연공간')]:
            p.circle(cx, 334, 65, p.tint)
            p.centered(title, cx-61, 294, 122, 42, size=28.0, bold=True, color=p.accent, leading=37)
            p.centered(sub, cx-63, 356, 126, 22, size=10.5, color=MUTED, leading=15)
        p.centered('2차  안내사인 추가', left+74, 292, right-left-148, 23,
                   size=12.5, bold=True, color=p.accent, leading=18)
        p.arrow(left+78, 341, right-78, 341)
        p.centered('1분 → 30초 → 15초', left+73, 380, right-left-146, 20,
                   size=10.8, color=MUTED, leading=15)
        p.centered('사전·1차·2차 공통 관찰', M, 432, CW, 18,
                   size=10.0, color=MUTED, leading=14)
        p.centered('거리 흡연자 수  ·  광장 안·밖 흡연 인원',
                   M, 458, CW, 23, size=13.0, bold=True, color=p.accent, leading=18)
