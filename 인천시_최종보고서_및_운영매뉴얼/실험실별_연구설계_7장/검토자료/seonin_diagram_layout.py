"""Editable A4 layout: preference-informed installation and formative evaluation.

Used by build_review.py for Seonin only. All objects are PDF/PPTX vectors/text.
Literature supports the stated methodological principles, not intervention efficacy.
"""

def render_seonin(p, d, W, H, canvas):
    purple = '#5500FF'
    ink = '#474443'
    dark = '#332C2B'
    muted = '#666666'
    light = '#F1EFF9'
    line = '#D3CFDE'
    white = '#FFFFFF'
    yellow = '#FFFDA5'
    M = 35
    cw = W - 2*M
    gap = 24
    bw = (cw-gap)/2

    def text(t, x, y, w, h=15, size=9.3, **kw):
        p.text(t, x, y, w, h, size, leading=kw.pop('leading', size*1.4), **kw)

    def heading(t, y):
        text(t, M, y, cw, 19, 11.5, bold=True, clr=purple, leading=16)

    p.rect(M,29,133,15,purple)
    text('인천 창의디자인 사회실험',M+4,30,125,14,8.4,clr=white,leading=12)
    text('거점별 실험·분석 계획',M,51,cw,20,13.8,bold=True,clr=purple,leading=18)
    text(d['category'],M,78,cw,15,9.6,clr=muted)
    text('02. '+d['name'],M,101,cw,27,19,bold=True,clr=dark,leading=25)
    p.line(M,139,W-M,139,line,.6)

    text('실험배경',M,153,62,16,10,bold=True,clr=purple)
    text(d['background'],M+70,151,cw-70,32,10.1,leading=14)
    text(d['scope'],M+70,186,cw-70,14,8.4,clr=muted,leading=12)

    p.rect(M,204,64,16,purple)
    text('사전 조사',M+4,205,56,14,9.2,bold=True,clr=white,leading=13)
    text('현장 관찰 + 설치 전 통행 계수 · 설치·보행 조건 확인',M+73,205,cw-73,15,9.1,clr=muted)
    p.rect(M,227,cw,27,light)
    for j, t in enumerate(d['stages'][0]['items']):
        x = M+j*cw/3
        if j: p.line(x,232,x,249,line,.5)
        text(t,x+6,234,cw/3-12,15,8.5,bold=True,clr=dark,align='center',leading=12)

    heading('01  실험 구성 및 수집 항목',268)
    for j in range(2):
        x = M+j*(bw+gap)
        s = d['stages'][j+1]
        p.rect(x,292,bw,19,purple)
        text(s['title'],x+6,294,bw-12,16,10,bold=True,clr=white,leading=14)
        text(s['subtitle'],x,320,bw,20,11.6,bold=True,clr=dark,leading=16)
        text(s['method'],x,346,bw,15,8.8,bold=True,clr=purple,leading=12)
        p.line(x,367,x+bw,367,line,.55)
        for k,t in enumerate(s['items']):
            text('· '+t,x,375+17*k,bw,17,9.1,leading=13)
        text(s['note'],x,427,bw,13,8,clr=muted,leading=11)
    text('→',W/2-10,338,20,25,18,bold=True,clr=purple,align='center',leading=23)

    p.rect(M,448,cw,31,yellow)
    text('1차 선호 → 색·문구 선정·반영 기록 → 2차 실제 경험',M+8,452,cw-16,15,10,bold=True,clr=purple,align='center',leading=14)
    text('의견을 반영한 설치물의 수용과 수정점을 찾는 형성평가',M+8,467,cw-16,11,8.3,clr=dark,align='center',leading=11)

    heading('02  정량·정성 결합 분석',490)
    p.rect(M,515,cw,81,light)
    for j,(title,body) in enumerate([(d['quant_title'],d['quant_body']),(d['qual_title'],d['qual_body'])]):
        x=M+j*(bw+gap)
        text(title,x+9,523,bw-18,17,9.5,bold=True,clr=purple,leading=13)
        text(body,x+9,546,bw-18,45,8.7,leading=13)
    p.circle(W/2,556,6.5,purple)
    text('+',W/2-6,547,12,17,12.7,bold=True,clr=white,align='center',leading=17)

    text('통합표  1차 선호 | 실제 반영 | 2차 반응 | 관찰·이유 | 다음 조치',M,607,cw,15,9.2,bold=True,clr=dark,leading=13)
    text('회차·학교·날짜별 보드 사진·집계 · 문항마다 1인 1표 안내(중복·동조 가능)',M,626,cw,12,8,clr=muted,leading=11)
    text('개인 전후·문항 간 연관·인과효과 검정 제외 · 다른 문항·보기의 비율을 단순 차감하지 않음',M,639,cw,12,8,clr=muted,leading=11)

    heading('03  디자인 반영 및 결과물',660)
    for j, (title, body) in enumerate(d['outputs']):
        x=M+j*cw/3
        if j: p.line(x,687,x,728,line,.5)
        text(title,x+7,685,cw/3-14,16,9.4,bold=True,clr=purple,align='center',leading=13)
        text(body,x+7,704,cw/3-14,25,8.8,clr=dark,align='center',leading=12)

    text('방법 근거와 본 실험에 적용하는 범위',M,741,cw,14,9,bold=True,clr=purple,leading=12)
    for i, ref in enumerate(d['method_basis']):
        y=761+15*i
        text(ref['label'],M,y,cw,13,7.9,clr=ink,leading=11)
        canvas.linkURL(ref['url'],(M,H-y-13,W-M,H-y),relative=0,thickness=0)
        # Page.text creates exactly one editable text box per call.
        shape=p.slide.shapes[-1]
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.hyperlink.address=ref['url']
    text('※ 문헌은 방법 선택의 근거이며, 이 설치물의 청소년 정서안정 효과를 직접 입증한 연구는 아님.',M,808,cw,12,7.8,clr=muted,leading=11)
    p.line(M,828,W-M-27,828,line,.5)
    text('02',W-M-20,821,20,15,10,bold=True,clr=dark,align='right',leading=14)
