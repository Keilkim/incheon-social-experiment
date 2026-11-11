from pathlib import Path
from html import escape
import json
import shutil
import unicodedata
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

BASE = Path(__file__).resolve().parent
OUT = BASE.parent
FONT = Path.home() / 'Library/Fonts'
for src, name in [('KoPubWorld Dotum Medium.ttf', 'KoPub-Medium.ttf'), ('KoPubWorld Dotum Bold.ttf', 'KoPub-Bold.ttf')]:
    (BASE / 'fonts').mkdir(exist_ok=True)
    shutil.copyfile(FONT / src, BASE / 'fonts' / name)

CSS = '''
@font-face{font-family:Ko;src:url('fonts/KoPub-Medium.ttf')} 
@font-face{font-family:Ko;src:url('fonts/KoPub-Bold.ttf');font-weight:700}
*{box-sizing:border-box} html,body{margin:0;padding:0} body{font-family:Ko,'Apple SD Gothic Neo',sans-serif;color:#19394b;font-size:10pt;line-height:1.38;-webkit-print-color-adjust:exact;print-color-adjust:exact}
@page{size:A4 landscape;margin:0}
.page{width:297mm;height:210mm;position:relative;padding:11mm 14mm 14mm;break-after:page;background:#fff;overflow:hidden}
.page:last-child{break-after:auto}.body-content{display:flow-root}
.portrait .page{width:210mm;height:297mm;padding:13mm 15mm 15mm}.portrait{font-size:10.3pt}
.eyebrow{font-size:8pt;color:#637985;letter-spacing:.2pt;margin-bottom:2mm}.tag{float:right;color:#087d80;font-weight:700}
h1{font-size:20pt;line-height:1.2;margin:0 0 2mm;font-weight:700;letter-spacing:-.45pt} .portrait h1{font-size:19pt}
.subtitle{font-size:9.1pt;color:#546773;margin-bottom:3mm}h2{font-size:11.2pt;margin:0 0 2mm;font-weight:700}h3{font-size:10.3pt;margin:0 0 1.5mm}
p{margin:0 0 2mm}b{font-weight:700}.small{font-size:8.7pt;line-height:1.4}.tiny{font-size:8pt;line-height:1.35}.muted{color:#637985}.teal{color:#087d80}.nowrap{white-space:nowrap}
.callout{padding:2.6mm 3mm;background:#edf5f6;border-left:1mm solid #087d80;margin:2.5mm 0 3mm}.callout p:last-child{margin-bottom:0}
.meta{font-size:9.2pt;padding:2.2mm 0;border-top:.3mm solid #b8cbd2;border-bottom:.3mm solid #b8cbd2;margin-bottom:3mm;line-height:1.7}.meta.slim{margin-bottom:2mm;padding:1.7mm 0}
.row{display:flex;gap:3.5mm}.col{flex:1;min-width:0}.panel{border:.25mm solid #bfd0d7;padding:3mm;break-inside:avoid}.panel.pale{background:#f5f8f9}.panel h2{color:#087d80}.stack>*+*{margin-top:3mm}.section{margin-top:3mm}.section h2{padding-bottom:1.4mm;border-bottom:.4mm solid #19394b}
.route{display:flex;align-items:stretch;gap:3mm;margin:3mm 0}.route .step{flex:1;background:#edf5f6;border-top:1mm solid #087d80;padding:2.8mm 3mm}.route .arrow{display:flex;align-items:center;font-size:18pt;color:#087d80}.route b{display:block;font-size:12pt;margin-bottom:1mm}.route .small{font-size:9pt}
.checks{line-height:1.8;margin-bottom:1.2mm}.checks.tight{line-height:1.6}.rule{border-bottom:.2mm solid #c1cfd5;height:7mm}.rules{margin-top:1mm}.rules.compact .rule{height:6mm}
.note-label{font-size:8.5pt;color:#637985;margin-top:2mm}.form-card{border:.25mm solid #b8cbd2;padding:3mm;height:93mm}.form-card h2{font-size:13pt;color:#087d80;border-bottom:.4mm solid #087d80;padding-bottom:2mm;margin-bottom:2.3mm}
table{width:100%;border-collapse:collapse;table-layout:fixed}th,td{border:.2mm solid #bed0d8;padding:1.5mm 1.8mm;vertical-align:top}th{background:#e8f1f4;text-align:left;font-weight:700}table.codes td{padding:1.6mm 2mm}table.codes th{padding:1.8mm 2mm}
.tally{font-size:8.1pt;line-height:1.2}.tally th{text-align:center;vertical-align:middle;padding:1.6mm .8mm;height:13mm}.tally td{height:6.2mm;padding:.8mm 1.1mm;vertical-align:middle;text-align:center}.tally td:last-child{text-align:left}.tally tbody tr:nth-child(even){background:#f7f9fa}.tally .total td{background:#edf5f6;font-weight:700;height:6.4mm}
.footer{position:absolute;bottom:7mm;left:14mm;right:14mm;border-top:.2mm solid #c6d4da;padding-top:1.5mm;display:flex;justify-content:space-between;font-size:7.5pt;color:#637985}.portrait .footer{left:15mm;right:15mm;bottom:8mm}
.question{margin-top:3.3mm;break-inside:avoid}.question .q-title{font-weight:700;margin-bottom:1.7mm}.question .q-title .n{color:#087d80;display:inline-block;min-width:8mm}.question p{margin-bottom:1.4mm}.question .help{font-size:8.5pt;color:#637985;margin-bottom:1.2mm}.choice-row{display:flex;border:.2mm solid #bfd0d7}.choice-row>div{flex:1;padding:2mm 1mm;text-align:center;border-right:.2mm solid #bfd0d7;font-size:9.5pt}.choice-row>div:last-child{border-right:none}.choice-row.scale>div{padding:1.5mm .7mm;font-size:8.8pt}.choice-row.scale b{display:block;font-size:9.5pt;margin-bottom:.6mm}.skip{font-size:8.3pt;color:#637985;margin-top:1mm}.number{color:#087d80;font-weight:700}.interview-top{font-size:9.3pt;line-height:1.7;border-top:.3mm solid #bfd0d7;border-bottom:.3mm solid #bfd0d7;padding:2mm 0;margin:3mm 0}
.guide-list p{margin-bottom:2.2mm}.guide-list b{color:#087d80}.portrait .panel{padding:3mm}.portrait .section{margin-top:3mm}.portrait .rule{height:8mm}.portrait .rules.compact .rule{height:6.5mm}.spacer{height:2mm}.blankbox{height:12mm;border:.2mm dashed #b5c7cf;margin-top:1.5mm}
'''

def rules(n=2, compact=False):
    return '<div class="rules'+(' compact' if compact else '')+'">'+'<div class="rule"></div>'*n+'</div>'

def panel(title, body, cls=''):
    return f'<div class="panel {cls}"><h2>{title}</h2>{body}</div>'

def page(title, subtitle, body, number, total, label, portrait=False):
    return f'''<section class="page"><header><div class="eyebrow">ACT Incheon　|　인천연안여객터미널 <span class="tag">{label} · 보완본</span></div><h1>{title}</h1><div class="subtitle">{subtitle}</div></header><main class="body-content">{body}</main><footer class="footer"><span>2026.11.11 보완　|　A·B·C는 공간 구간 / 행동 이유는 인터뷰로 확인</span><span>{number} / {total}</span></footer></section>'''

def wrap(pages, portrait=False):
    css = CSS + ('\n@page{size:A4 portrait;margin:0}' if portrait else '')
    return '<!doctype html><html lang="ko"><meta charset="utf-8"><title>연안여객터미널 조사도구 보완본</title><style>'+css+'</style><body class="'+('portrait' if portrait else '')+'">'+''.join(pages)+'</body></html>'

def observation(phase):
    label = f'{phase}차 행동관찰'
    condition = '통합 바닥 안내사인 설치 상태' if phase == 1 else '1차 바닥 안내 유지 + 보관·짐 정리 공간 추가 상태'
    pages = []
    guide = f"""
    <div class="callout"><b>관찰로 행동 유형을 찾고, 인터뷰로 그 이유를 확인합니다.</b><br>단순 통과 건수보다 ‘A에서 유도 방향으로 갔는가 → B에서 되돌아갔는가 → C에 도착하고도 되돌아갔는가’를 봅니다. 이유를 관찰만으로 단정하지 않습니다.</div>
    <div class="route">
      <div class="step"><b>A 입장·최초 방향 선택</b><div class="small">입장 후 첫 선택 지점에서 지정한 유도 방향으로 이동하는지 기록. 합류 / 다른 방향 / 미확인.</div></div><div class="arrow">→</div>
      <div class="step"><b>B 이동 중간 구간</b><div class="small">A와 C 사이에서 A 쪽으로 실제 되돌아 이동하는지 기록. 단순 시선 전환·정지는 별도 메모.</div></div><div class="arrow">→</div>
      <div class="step"><b>C 코스 끝·도착 구간</b><div class="small">정한 도착선에 온 뒤 이전 구간 쪽으로 되돌아가는지 기록. 도착 완료 후 정상 복귀인지도 인터뷰로 확인.</div></div>
    </div>
    <div class="row">
      <div class="col stack">
        {panel('01　현장에서 먼저 고정할 것', '''<p class="small">A 선택선·유도 방향, B 진입·되돌림 판정선, C 도착·퇴장선과 관찰 종료 지점을 도면·사진에 표시합니다. 선택한 코스는 A→B→C가 이어져야 합니다.</p><p class="small">C 앞 짐 보관공간의 <b>안쪽 기준 영역</b>과 비교할 <b>바깥쪽 관찰 범위</b>도 함께 표시합니다. 1차에도 2차 설치 예정 영역과 같은 물리적 범위를 사용합니다.</p><p class="small"><b>1·2차 공통:</b> 경계·코스·관찰 시간·선정 방식·단위를 유지합니다. 바뀌면 변경 내역과 비교 한계를 적습니다.</p><div class="tiny muted">현재 차수 설치 조건: '''+condition+'''</div>''')}
        {panel('02　선정·추적·기록', '''<p class="small">A 진입 시 관찰번호를 부여하고 종료까지 같은 번호를 씁니다. 보관공간에서 새로 관찰한 사례도 번호를 부여하되 동선 관찰 여부를 구분합니다.</p><p class="small">전수 관찰이 어려우면 사전에 ‘매 n번째’처럼 고정 기준을 정합니다. 특이 행동 사례는 상세기록·인터뷰에 추가할 수 있으나 보조 집계에는 중복·임의 추가하지 않습니다.</p><p class="small">관찰 단위는 이용객 1명. 함께 행동해 개별 구분이 어려우면 일행 1사례로 표시하고 인원수를 씁니다. 1명 기록과 일행 기록의 합계는 분리합니다.</p>''')}
      </div>
      <div class="col stack">
        {panel('03　짐 위치와 머문 시간도 두 차수 공통', '''<p class="small"><b>I 안쪽만 / O 바깥쪽만 / M 안·밖 모두 / N 내려놓지 않음 / U 판단 불가.</b> 이동 중 바닥에 닿은 바퀴는 ‘짐을 두었다’에 포함하지 않습니다.</p><p class="small">체류 시작 = 이용객의 전면 관찰 범위 진입, 종료 = 이용객의 범위 이탈. 초까지 재서 분·초로 적습니다. 사람이 떠나고 짐만 남으면 별도 메모하며 총 짐 보관시간으로 해석하지 않습니다.</p><p class="small">시작·끝을 놓치면 ‘일부 관찰’로 표시합니다. 완결 체류시간에 섞지 않습니다. 체감 시간은 인터뷰 L3에서 실제 측정값을 알려주기 전에 묻습니다.</p>''')}
        {panel('04　인터뷰로 연결하는 방법', '''<p class="small">① A에서 다른 방향　② B 되돌아감　③ C 도착 후 되돌아감　④ 안쪽에 짐 둠　⑤ 바깥쪽에 짐 둠　⑥ 망설임 없이 이동·이용한 비교 사례를 고르게 접촉합니다.</p><p class="small">행동이 끝난 뒤 같은 관찰번호로 질문합니다. 한 사람이 여러 유형이면 모두 표시합니다. 거절·시간 부족·접촉 불가도 기록합니다. 관찰되지 않은 이유는 ‘미확인’으로 남깁니다.</p><div class="tiny muted">예: B에서 되돌아가고 C에 미도달 → B ‘있음’, C ‘미도달’. ‘길을 몰라 포기’라고 쓰지 않고 인터뷰 R4로 이유를 확인.</div>''')}
      </div>
    </div>
    <p class="tiny muted" style="margin-top:2mm">사용 순서: 2쪽 동선 상세 → 3쪽 짐 상세(해당 사례) → 4·5쪽 보조 집계 → 별도 인터뷰 설문지. 상세지는 필요한 만큼 복사합니다. 0=관찰했으나 없음, 공란=미관찰 시간대, 미확인=사례는 있으나 판정 불가.</p>
    """
    pages.append(page(f'{phase}차 행동관찰 작성방법', '1·2차 공통 관찰 틀　|　동선의 차이와 짐 배치 행동을 인터뷰 대상 선정에 연결', guide, 1, 5, label))

    route = '''
    <div class="meta">관찰번호 __________　날짜 __________　관찰 시작 ____:____:____　종료 ____:____:____　조사원 __________<br>코스·도면번호 __________　관찰 단위 □ 1명 □ 일행 1사례(____명)　짐 소지 □ 있음 □ 없음 □ 미확인　동행 □ 있음 □ 없음 □ 미확인</div>
    <div class="row">
      <div class="col form-card"><h2>A　입장·최초 방향 선택</h2><p class="small">입장 후 <b>처음 선택한 이동 방향</b>을 기록합니다.</p><div class="checks">□ 지정 유도 방향으로 합류<br>□ 다른 방향으로 이동<br>□ 방향을 판단하지 못함</div><p class="small">관찰된 이동 방향·목적지 표지</p>'''+rules(2,True)+'''<p class="small" style="margin-top:2mm">사인 쪽 시선·고개 전환<br>□ 있음 □ 없음 □ 미확인</p><p class="tiny muted">시선 전환은 보조 정보입니다. 안내를 이해했는지는 인터뷰 R2로 확인합니다.</p></div>
      <div class="col form-card"><h2>B　이동 중간 구간</h2><div class="checks">□ 진입 후 행동 확인<br>□ 미진입　□ 진입·행동 미확인</div><p class="small"><b>진입 후 행동 확인 사례만</b></p><div class="checks">되돌아감 □ 있음 □ 없음</div><p class="small">되돌림 시각 ____:____:____<br>되돌린 위치·방향·이후 행동</p>'''+rules(2,True)+'''<p class="tiny muted" style="margin-top:2mm">A 쪽 판정선을 넘어 실제 되돌아 이동하면 ‘있음’. 여러 번 돌아도 사례별 1회 집계하고 반복 횟수는 메모합니다.</p></div>
      <div class="col form-card"><h2>C　코스 끝·도착 구간</h2><div class="checks">□ 도달 후 행동 확인<br>□ 미도달　□ 도달·행동 미확인</div><p class="small"><b>도달 후 행동 확인 사례만</b></p><div class="checks">되돌아감 □ 있음 □ 없음</div><p class="small">도착 ____:____:____<br>되돌림 시각 ____:____:____<br>도착 후 실제 행동·되돌린 방향</p>'''+rules(2,True)+'''<p class="tiny muted" style="margin-top:2mm">도착 후 복귀도 관찰 사실로 기록합니다. 목적을 마친 복귀인지, 이용을 포기했는지는 인터뷰 R5로 확인합니다.</p></div>
    </div>
    <div class="row section">
      <div class="col"><h2>정지·망설임의 단서 / 주변 상황</h2><p class="small">2초 이상 정지 □ 있음 □ 없음 □ 미확인　구간 □ A □ B □ C<br>위치·대략 초수, 두리번거림·사인 재확인, 대기열·동행·혼잡 등 <b>보인 행동</b>을 기록</p>'''+rules(2,True)+'''</div>
      <div class="col"><h2>종료·인터뷰 연결</h2><p class="small">종료 □ 정한 지점까지 확인 □ 시야 이탈 □ 조사 종료 □ 기타 ______<br>인터뷰 후보 유형 □ A 다른 방향 □ B 복귀 □ C 복귀 □ 원활 이동 □ 기타 ____<br>접촉 □ 완료 □ 거절 □ 시간 부족 □ 접촉 불가 □ 미접촉<br>인터뷰번호 __________　짐 상세기록 □ 연결(같은 번호) □ 없음</p></div>
    </div>
    <p class="tiny muted" style="margin-top:2mm">‘다른 방향’은 지정 유도 방향과의 차이이며 길찾기 오류를 뜻하지 않습니다. 원래 목적지·첫 동선 인지·망설임·복귀 이유를 인터뷰에서 확인합니다.</p>
    '''
    pages.append(page(f'{phase}차 개별 동선 관찰기록지', '사례별 1장　|　A→B→C를 같은 번호로 추적하고 관찰 사실만 적습니다', route, 2, 5, label))

    luggage = '''
    <div class="meta">관찰번호 __________　날짜 __________　조사원 __________　동선 상세지 □ 연결 □ 보관공간에서 별도 선정<br>단위 □ 1명 □ 일행 1사례(____명)　짐 종류·개수 __________________　코스·경계 도면번호 __________　혼잡·출항 상황 __________________</div>
    <div class="row">
      <div class="col stack">
        '''+panel('01　짐을 어디에 두었는가', '''<p class="small">정해진 안쪽 영역과 바깥쪽 비교 범위를 기준으로 <b>아래 하나</b>를 선택합니다. 관찰 중 양쪽에 두거나 옮겼으면 M입니다.</p><div class="checks">□ I 안쪽에만 둠　□ O 바깥쪽에만 둠<br>□ M 안·밖 모두 둠　□ N 내려놓지 않음<br>□ U 위치·배치 행동 판단 불가</div><p class="small">구체적 자리 □ 바닥 □ 선반 □ 테이블 □ 보관함 □ 기타 ____<br>위치 이동 □ 없음 □ 밖→안 □ 안→밖 □ 반복 □ 미확인</p><div class="note-label">놓은 시각·위치 → 옮긴 시각·위치 → 떠날 때의 상태</div>'''+rules(3,True))+'''
        '''+panel('02　관찰된 이용 행동', '''<div class="checks tight small">□ 짐 정리 □ 보관함 사용 □ 잠시 내려놓고 대기<br>□ 짐 둔 뒤 다른 곳으로 이동 □ 동행이 짐을 지킴<br>□ 공간을 봤으나 이용 안 함 □ 기타 ______ □ 미확인</div><p class="small">범위 이탈 시 짐 □ 함께 이동 □ 남아 있음 □ 미확인</p><p class="tiny muted">행동은 복수 체크. 바닥에 바퀴가 닿은 채 끌고 이동하는 장면만으로는 짐을 둔 것으로 세지 않습니다.</p>''')+'''
      </div>
      <div class="col stack">
        '''+panel('03　실제 체류시간', '''<p class="small">이용객이 전면 관찰 범위에 들어온 때부터 벗어난 때까지 측정합니다.</p><p>진입　____시 ____분 ____초<br>이탈　____시 ____분 ____초<br><b>체류　____분 ____초 (= ______초)</b></p><div class="checks small">□ 시작·끝 모두 확인(완결)<br>□ 시작 놓침 □ 종료 놓침 □ 계속 체류 중<br>일부 관찰 구간 ____:____:____ ~ ____:____:____</div><p class="tiny muted">일부 관찰은 관찰된 시간만 적고 완결값에 포함하지 않습니다. 예: 09:12:10→09:16:40 = 4분 30초. 이 값은 짐의 총 보관시간이 아닙니다.</p>''')+'''
        '''+panel('04　불편·망설임의 단서와 인터뷰', '''<p class="small">멈춤·다시 들기·자리를 바꿈·통로 막힘·물건 찾기 등 실제 보인 장면</p>'''+rules(2,True)+'''<p class="small" style="margin-top:2mm">인터뷰 후보 □ I □ O □ M □ N □ 망설임 □ 원활 이용<br>접촉 □ 완료 □ 거절 □ 시간 부족 □ 접촉 불가 □ 미접촉<br>인터뷰번호 __________</p><p class="tiny muted">인터뷰 L1~L4: 안·밖 선택 이유, 안쪽 이용의 불편, 머문 시간에 대한 체감, 처음 기대와 실제 경험을 확인합니다.</p>''')+'''
      </div>
    </div>
    <div class="callout small"><b>사실과 응답을 분리:</b> 관찰에는 ‘밖에 짐을 놓고 3분 대기’처럼 씁니다. ‘안쪽이 불편해서’와 같은 이유는 인터뷰에서 확인한 경우에만 응답으로 기록합니다. 체감 시간을 묻기 전 실제 측정값을 알려주지 않습니다.</div>
    '''
    pages.append(page(f'{phase}차 짐 배치·체류 관찰기록지', '1·2차 모두 사용　|　C 구간 앞 보관공간의 안·밖 배치와 실제 머문 시간', luggage, 3, 5, label))

    times=[]
    for minute in range(7*60+30,15*60,30):
        times.append(f'{minute//60:02d}:{minute%60:02d}~{(minute+30)//60:02d}:{(minute+30)%60:02d}')
    tally_rows = ''.join('<tr><td>'+t+'</td>'+'<td></td>'*10+'</tr>' for t in times)
    cols='<col style="width:25mm">'+''.join(f'<col style="width:{w}mm">' for w in [16,18,18,18,21,19,21,19,17])+'<col>'
    tally = '''
    <div class="meta slim">날짜 __________　조사 시간 07:30~15:00　코스·도면번호 __________　조사원 __________　관찰 단위 □ 1명 □ 일행<br>선정 □ 전수 □ 매 ____번째 □ 기타 __________　중단·누락 시간 __________________　설치 조건·날씨·혼잡 __________________</div>
    <div class="callout small"><b>보조 집계:</b> 사전에 정한 기준으로 선정한 사례만 셉니다. A 진입 시간대에 배정하고 B·C 결과를 추적 종료 후 같은 행에 반영합니다. 특이 사례만 골라 본 기록은 별도 상세지에 남깁니다.</div>
    <table class="tally"><colgroup>'''+cols+'''</colgroup><thead><tr><th>시간대</th><th>A 진입<br>선정 수</th><th>A 유도<br>방향 합류</th><th>A 다른<br>방향</th><th>A 방향<br>미확인</th><th>B 진입 후<br>행동 확인</th><th>그중 B<br>되돌아감</th><th>C 도달 후<br>행동 확인</th><th>그중 C<br>되돌아감</th><th>추적<br>불완전*</th><th>특이사항·연결 관찰번호</th></tr></thead><tbody>'''+tally_rows+'''<tr class="total"><td>합계</td>'''+('<td></td>'*10)+'''</tr></tbody></table>
    <div class="row" style="margin-top:2mm"><div class="col tiny"><b>확인:</b> A 선정 수 = 합류 + 다른 방향 + 방향 미확인. B·C 되돌아감 수는 각 ‘행동 확인’ 수 이하입니다. 미진입·미도달과 행동 미확인을 구분해 상세지에 적습니다.</div><div class="col tiny"><b>*추적 불완전:</b> B·C 중 진입·도달 또는 후속 행동을 확인하지 못한 사례 수(사례당 1회). A·B·C·불완전 수는 중복될 수 있으므로 서로 더하지 않습니다. 0·공란·미확인을 구분합니다.</div></div>
    <p class="tiny muted" style="margin-top:1.5mm">비율이 필요할 때: A 합류÷(합류+다른 방향), B 복귀÷B 행동 확인, C 복귀÷C 행동 확인. 분모 0은 계산하지 않습니다. 선정 사례의 참고값이며 전체 이용객 비율·오류율로 일반화하지 않습니다.</p>
    '''
    pages.append(page(f'{phase}차 구간별 30분 보조 집계표', 'A 입장 방향 · B 중간 복귀 · C 도착 후 복귀　|　상세기록과 인터뷰 선정을 보조하는 집계', tally, 4, 5, label))

    storage_rows=''.join('<tr><td>'+t+'</td>'+'<td></td>'*9+'</tr>' for t in times)
    storage = '''
    <div class="meta slim">날짜 __________　보관공간·경계 도면번호 __________　조사원 __________　관찰 단위 □ 1명 □ 일행<br>짐 소지 사례 선정 □ 전수 □ 매 ____번째 □ 기타 __________　중단·누락 시간 __________　1차와 경계 □ 동일 □ 변경(메모)</div>
    <div class="callout small">보관공간 전면 관찰 범위에 들어온 <b>짐 소지 사례</b>를 진입 시간대에 배정합니다. I·O·M·N·U는 최종적으로 하나만 선택합니다. 체류시간은 3쪽 개별 기록지에 분·초로 기록합니다.</div>
    <table class="tally"><colgroup><col style="width:25mm"><col style="width:19mm"><col style="width:20mm"><col style="width:20mm"><col style="width:20mm"><col style="width:20mm"><col style="width:20mm"><col style="width:23mm"><col style="width:23mm"><col></colgroup><thead><tr><th>시간대</th><th>짐 소지<br>선정 수</th><th>I<br>안쪽만</th><th>O<br>바깥쪽만</th><th>M<br>안·밖 모두</th><th>N<br>안 내려놓음</th><th>U<br>판단 불가</th><th>체류 완결<br>측정 수*</th><th>체류 일부<br>관찰 수*</th><th>연결 번호·경계 변경·특이사항</th></tr></thead><tbody>'''+storage_rows+'''<tr class="total"><td>합계</td>'''+('<td></td>'*9)+'''</tr></tbody></table>
    <div class="row" style="margin-top:2mm"><div class="col tiny"><b>확인:</b> 선정 수 = I+O+M+N+U. 실제 짐을 둔 사례는 I+O+M. 안쪽만·바깥쪽만 비중을 비교할 때는 I+O+M을 분모로 하며 M을 별도 제시합니다.</div><div class="col tiny"><b>*체류 측정:</b> 집계 대상으로 선정한 사례 중 3쪽 상세지를 쓴 사례 수. 완결·일부는 서로 중복하지 않습니다. 시간 요약 시 완결 사례 수와 범위를 함께 쓰고, 일부 관찰은 분리합니다.</div></div>
    <p class="tiny muted" style="margin-top:1.5mm">동선 관찰과 보관공간 관찰의 대상은 다를 수 있습니다. 두 표의 선정 수를 같게 맞추지 않습니다. 1·2차 비교는 같은 경계·선정 기준·시간대를 전제로 하며 혼잡·운항 여건을 함께 확인합니다.</p>
    '''
    pages.append(page(f'{phase}차 짐 배치·체류 30분 보조 집계표', '안쪽 / 바깥쪽 / 양쪽 / 미배치 구분　|　1·2차 같은 공간 기준으로 비교', storage, 5, 5, label))
    return wrap(pages)

def choices(items, scale=False):
    return '<div class="choice-row'+(' scale' if scale else '')+'">'+''.join('<div>'+s+'</div>' for s in items)+'</div>'

def q(n,title,body,help=''):
    return '<div class="question"><div class="q-title"><span class="n">'+n+'</span>'+title+'</div>'+('<div class="help">'+help+'</div>' if help else '')+body+'</div>'

def likert(labels,na):
    return choices([f'<b>□ {i}점</b>{s}' for i,s in enumerate(labels,1)],True)+'<div class="skip">□ 해당없음: '+na+'　　□ 응답 거부</div>'

def ident():
    return '<div class="interview-top">차수 □ 1차 □ 2차　관찰번호 __________　인터뷰번호 __________<br>날짜 __________　시각 ____:____　위치 __________　조사원 __________</div>'

def interview():
    pages=[]
    guide='''
    <div class="callout"><b>인터뷰의 중심은 ‘왜 그렇게 행동했는가’입니다.</b><br>관찰은 인터뷰 대상자를 찾는 출발점입니다. 관찰된 행동을 설명하는 응답과, 원활하게 이용한 비교 사례를 함께 모읍니다.</div>
    <div class="section"><h2>01　행동을 보고 대상자를 선정합니다</h2>
    <table class="codes small"><colgroup><col style="width:39mm"><col><col style="width:28mm"></colgroup><thead><tr><th>관찰 유형</th><th>확인할 핵심 이유</th><th>연결 문항</th></tr></thead><tbody>
    <tr><td>A 다른 방향</td><td>원래 목적지, 입장 직후 동선 인지, 선택 단서</td><td>R1·R2</td></tr>
    <tr><td>B 중간 되돌아감</td><td>되돌린 계기·위치·계획 변경·불편</td><td>R3·R4</td></tr>
    <tr><td>C 도착 후 되돌아감</td><td>도착 인지, 목적 달성 후 복귀인지, 이용하지 않은 이유</td><td>R3·R5</td></tr>
    <tr><td>I 안쪽 / O 바깥쪽 / M 양쪽</td><td>그 자리에 둔 이유, 안쪽 이용 시 불편, 이동 이유</td><td>L1·L2</td></tr>
    <tr><td>N 미배치 / 원활 이동·이용</td><td>두지 않은 이유, 도움이 된 안내·공간, 불편 유무</td><td>R6·L1~L4</td></tr>
    </tbody></table>
    <p class="small muted" style="margin-top:2mm">한 사람이 여러 유형에 해당하면 모두 표시합니다. 특이 행동만으로 대상자를 채우지 않고 원활 이동·안쪽 이용 사례도 포함합니다. 목표 수와 시간대별 배분은 현장 운영 전에 정합니다.</p></div>
    <div class="section"><h2>02　질문 순서와 건너뛰기</h2><div class="guide-list small">
    <p><b>① 관찰 종료 후 접촉.</b> “터미널에서 이동하고 짐을 둔 경험을 짧게 여쭤봐도 될까요?” 참여 여부를 확인하고 관찰번호를 연결합니다. 이동·이용이 끝나기 전에 질문하면 이후 관찰은 별도 표시합니다.</p>
    <p><b>② 공통 기본 문항 Q1~Q7.</b> 두 차수에 같은 문구로 묻습니다. 같은 코스의 같은 접촉 지점을 우선하며, 다른 위치에서 질문했다면 반드시 표시합니다. 답을 암시하거나 사인을 먼저 설명하지 않습니다.</p>
    <p><b>③ 공통 이유 문항 R·L.</b> 이유를 먼저 자유롭게 듣고 필요할 때만 보충합니다. 짐을 소지하지 않았으면 L은 건너뜁니다. B·C 복귀가 없으면 해당 문항은 ‘해당없음’으로 표시합니다.</p>
    <p><b>④ 2차만 S1~S4 추가, 마지막에 공통 T1.</b> 공간을 보지 못한 사람에게 편의 점수를 억지로 받지 않습니다. 체감 체류시간 L3은 실제 측정값을 알려주기 전에 질문합니다.</p>
    </div></div>
    <div class="section"><h2>03　기록과 해석</h2><div class="guide-list small">
    <p>관찰 사실과 응답을 분리합니다. “길을 몰라 되돌아갔다”처럼 조사원이 원인을 넣지 않고 응답자의 표현을 짧게 인용합니다. 모름·기억 안 남·거부·해당없음은 구분합니다.</p>
    <p>이름·전화번호 없이 관찰번호와 인터뷰번호로 연결합니다. 접촉 결과와 유형별 완료 수를 남깁니다. 행동 유형에 따라 선정한 응답을 전체 이용객 비율로 해석하지 않습니다.</p>
    <p>Q1은 <b>인터뷰 시점의 방향 인지</b>입니다. C에 도착한 뒤의 정답을 입장 당시 인지로 해석하지 않습니다. 첫 입장 인지는 R2의 경험 응답으로 확인합니다.</p>
    </div></div>
    <div class="callout small">출력: 1쪽은 조사원 공용 안내. 응답자별로 2~5쪽을 한 묶음으로 사용합니다. 1차도 5쪽의 공통 마무리 T1을 사용하며 S1~S4만 건너뜁니다. 서술 답변은 추가 용지에 같은 번호로 이어 적을 수 있습니다.</div>
    '''
    pages.append(page('현장 인터뷰 운영 안내', '1·2차 공통 질문 + 관찰 행동별 이유 질문 + 2차 공간 경험 추가',guide,1,5,'인터뷰',True))

    core=ident()+'''<p class="small">기본 확인　첫 방문 □ 예 □ 아니요 □ 모름　큰 짐 소지 □ 예 □ 아니요<br>동행 □ 있음 □ 없음　관찰 연결 □ 있음 □ 없음　참여 동의 □ 예 □ 아니요(종료)</p>
    <div class="callout small">각 문항 하나만 선택. 1~5점은 부정→긍정. 해당없음·응답 거부는 점수에 포함하지 않습니다. 위치에 따른 해석 차이를 확인합니다.</div>'''
    core+=q('Q1','지금 이곳에서 수화물 보관소는 어느 방향일까요?',choices(['□ 정확한 방향','□ 다른 방향','□ 모르겠다고 함']), '손으로 가리키게 한 뒤 조사원 판단 / 방향을 알려주거나 유도 금지')
    core+=q('Q2','수화물 보관소가 있다는 사실을 언제 알게 되셨나요?',choices(['□ 방문 전부터 알았음','□ 오늘 안내를 보고 알았음','□ 오늘 처음 들음']))
    core+=q('Q3','바닥에 표시된 색깔 안내 사인을 보셨나요?',choices(['□ 봤음','□ 못 봄','□ 기억 안 남']))
    core+=q('Q4','오늘 원하는 장소를 찾기는 얼마나 쉬우셨나요?',likert(['매우 어려움','어려움','보통','쉬움','매우 쉬움'],'아직 목적지를 찾아 이동하지 않음'))
    core+=q('Q5','바닥 안내 사인은 얼마나 눈에 잘 띄었나요?',likert(['전혀 안 띔','잘 안 띔','보통','잘 띔','매우 잘 띔'],'바닥 사인을 보지 못함'))
    core+=q('Q6','바닥 안내 사인은 이동 방향을 이해하는 데 얼마나 도움이 되었나요?',likert(['전혀 도움 안 됨','도움 안 됨','보통','도움 됨','매우 도움 됨'],'바닥 사인을 보지 못함'))
    core+=q('Q7','터미널의 길찾기 안내에 전반적으로 얼마나 만족하셨나요?',likert(['매우 불만족','불만족','보통','만족','매우 만족'],'길찾기 안내를 이용해 보지 않음'))
    core+='''<div class="section small"><b>모집·연결 메모</b><br>대상 유형(복수) □ A 다른 방향 □ B 복귀 □ C 복귀 □ I 안쪽 □ O 바깥쪽<br>□ M 양쪽 □ N 미배치 □ 원활 이동·이용 □ 기타 ______<br>관찰 종료 후 질문 □ 예 □ 아니요　기준 접촉 지점 □ 동일 □ 다름(________)</div>'''
    pages.append(page('공통 기본 인터뷰', '1·2차 동일 문구　|　기존 Q1~Q7 유지',core,2,5,'인터뷰',True))

    route=ident()
    route+=q('R1','들어오실 때 원래 어디로 가려고 하셨나요?',rules(1), '목적지·방문 목적을 먼저 묻습니다. 지정 유도 방향과 달라도 오류로 단정하지 않습니다.')
    route+=q('R2','처음 들어왔을 때 어디로 가야 할지 바로 알 수 있었나요?', '''<div class="checks small">□ 바로 알았음 □ 잠시 살핀 뒤 알았음 □ 알기 어려웠음 □ 기억 안 남</div><p class="small">무엇을 보고 어느 방향으로 가기로 하셨나요?</p>'''+rules(2,True), '먼저 자유 응답. 필요 시 바닥 선·화살표·글자·기존 안내·사람에게 질문·익숙한 길 등을 보충 확인.')
    route+=q('R3','이동하면서 망설이거나 멈췄던 순간이 있었나요?', '''<div class="checks small">□ 있었음 □ 없었음 □ 기억 안 남</div><p class="small">있었다면 어느 지점에서, 무엇 때문에 그랬나요?</p>'''+rules(2,True), '관찰상 정지가 있었다면 “이 지점에서 잠시 멈추셨는데 그때 어떤 상황이었나요?”처럼 중립적으로 확인.')
    route+=q('R4','중간에서 되돌아가신 것은 어떤 이유였나요?', '''<div class="checks small">□ 질문함 □ 해당없음(B 복귀 없음) □ 관찰 미확인</div><p class="small">그때 원래 하려던 일, 되돌리게 된 계기, 이후 한 일은 무엇이었나요?</p>'''+rules(2,True), 'B 복귀 관찰 사례에 질문. 길찾기 문제·일정 변경·동행 등 이유를 미리 읽어 주지 않습니다.')
    route+=q('R5','코스 끝까지 오신 뒤 다시 돌아가신 것은 어떤 이유였나요?', '''<div class="checks small">□ 질문함 □ 해당없음(C 복귀 없음) □ 관찰 미확인</div><p class="small">도착한 줄 알고 계셨나요? 원래 하려던 일은 하셨나요?<br>이용하지 않았다면 무엇 때문에 이용하지 않으셨나요?</p>'''+rules(2,True), 'C 도착 후 복귀 사례에 질문. 목적을 마친 정상 복귀와 이용하지 않고 떠남을 응답으로 구분합니다.')
    route+=q('R6','길을 찾는 데 도움이 된 점이나 불편했던 점은 무엇인가요?',rules(2,True), '되돌아감이 없었던 사람에게도 질문. 원활하게 이동한 이유와 개선할 점을 함께 듣습니다.')
    pages.append(page('공통 동선·되돌아감 이유', 'A 입장 인지 → B 중간 복귀 → C 도착 후 복귀　|　해당 행동만 추가 확인',route,3,5,'인터뷰',True))

    luggage=ident()+'''<div class="callout small">짐 소지 □ 예 □ 아니요 → 아니요면 L1~L4 건너뛰기.<br>관찰 위치 유형 □ I 안쪽 □ O 바깥쪽 □ M 양쪽 □ N 미배치 □ U 미확인<br>아래 이유는 자유 응답을 먼저 받습니다. 관찰된 위치와 답이 다르면 모두 적습니다.</div>'''
    luggage+=q('L1','짐을 어디에 두셨나요? 그 자리를 선택한 이유는 무엇인가요?', '''<p class="small">안쪽·바깥쪽·양쪽에 둔 이유를 응답자의 말로 기록합니다.<br>내려놓지 않았다면: “짐을 따로 두지 않으신 이유는 무엇인가요?”</p>'''+rules(3,True), '양쪽에 두거나 옮긴 경우에는 처음 자리와 옮긴 계기를 함께 묻습니다.')
    luggage+=q('L2','그곳에 짐을 두거나 정리하면서 어떤 점이 편하거나 불편했나요?', '''<p class="small"><b>안쪽 이용:</b> 실제로 써 보니 불편하거나 망설였던 점이 있었나요?<br><b>바깥쪽·미배치:</b> 안쪽 공간이 있는 줄 아셨나요? 이용을 고려하셨나요?<br><b>양쪽 이용:</b> 각 자리에서 달랐던 점은 무엇이었나요?</p>'''+rules(3,True), '해당 유형의 보충 질문만 사용. “불편하지 않았나요?”처럼 답을 유도하지 않습니다.')
    luggage+=q('L3','그곳에 얼마나 머무셨다고 느끼시나요?', '''<p class="small">응답자가 느낀 시간　약 ____분 ____초　□ 잘 모르겠음<br>체감 □ 짧았음 □ 적당했음 □ 길었음 □ 판단 어려움<br>그렇게 느낀 이유 / 머무는 동안 한 일</p>'''+rules(2,True)+'''<p class="small" style="margin-top:2mm">[응답 후 조사원 기입] 실제 체류 ____분 ____초<br>□ 완결 측정 □ 일부 관찰 □ 측정 안 됨</p>''', '먼저 실제 측정값을 말하지 않습니다. ‘얼마나 오래’와 ‘그 시간이 어땠는지’를 구분합니다.')
    luggage+=q('L4','짐을 두거나 정리하기에 이 공간은 실제로 얼마나 편리했나요?',likert(['매우 불편','불편','보통','편리','매우 편리'],'이용하지 않아 실제 경험을 평가할 수 없음')+'''<p class="small" style="margin-top:2mm">그렇게 답한 가장 큰 이유는 무엇인가요?</p>'''+rules(2,True), '실제로 짐을 두거나 정리한 사람에게만 1~5점. 1·2차 동일 질문입니다.')
    pages.append(page('공통 짐 배치·체류 경험', '안쪽·바깥쪽 선택 이유와 실제 이용 불편　|　1·2차 모두 질문',luggage,4,5,'인터뷰',True))

    extra=ident()+'''<div class="callout small"><b>S1~S4는 2차만 질문합니다.</b> 1차는 바로 아래 공통 마무리 T1로 이동합니다.<br>추가 공간은 현장에서 정한 동일한 대상을 가리킵니다. 평가 전에 기능을 설명해 답을 유도하지 않습니다.</div>'''
    extra+=q('S1','수화물 보관소 앞의 새 안내 또는 짐 정리 공간을 보셨나요?',choices(['□ 봤음','□ 못 봄','□ 기억 안 남']))
    extra+=q('S2','새로 마련된 공간을 실제로 이용해 보셨나요?',choices(['□ 이용했음','□ 이용하지 않음','□ 어떤 공간인지 모름']))
    extra+=q('S3','앞으로 짐을 정리하거나 보관하기 위해 이 공간을 이용할 의향은 어느 정도인가요?',likert(['전혀 없음','없음','보통','있음','매우 있음'],'어떤 공간인지 보거나 설명을 듣지 못함'))
    extra+=q('S4','이 공간은 짐을 정리하거나 보관하기에 얼마나 편리해 보이나요?',likert(['매우 불편','불편','보통','편리','매우 편리'],'공간을 보지 못해 평가할 수 없음'), '보기에 대한 평가입니다. 실제 이용 편의 L4와 구분합니다. 기존 2차 Q8~Q11의 내용을 유지했습니다.')
    extra+='''<div class="section"><h2>1·2차 공통 마무리</h2></div>'''
    extra+=q('T1','터미널 길찾기 또는 짐 보관·정리 공간에서 가장 개선되었으면 하는 점은 무엇인가요?',rules(3,True)+'''<div class="checks small">□ 특별한 의견 없음 □ 응답 거부</div>''', '기존 개선 의견 문항을 통합. 공간을 이용하지 않은 응답자는 길찾기 경험 중심으로 답할 수 있습니다.')
    extra+='''<div class="section"><h2>조사원 정리 — 질문을 마친 뒤 작성</h2><p class="small">접촉 결과 □ 완료 □ 일부 완료 □ 거절 □ 시간 부족 □ 접촉 불가<br>관찰 사실과 응답이 □ 부합 □ 다름 □ 비교 불가<br>핵심 이유(응답의 표현) / 불일치 메모</p>'''+rules(2,True)+'''<p class="tiny muted" style="margin-top:2mm">정리: 관찰 유형 → 응답자가 밝힌 이유 → 도움이 된 점·불편 → 개선 단서. 원인 코드는 응답 후 부여하며 추정한 이유는 섞지 않습니다. 해당없음·모름·거부는 임의로 점수화하지 않습니다.</p></div>'''
    pages.append(page('2차 공간 추가 질문·공통 마무리', '2차 추가 인지·이용·의향·예상 편의　|　T1은 1·2차 모두 사용',extra,5,5,'인터뷰',True))
    return wrap(pages,True)

DOCS = {
    '연안여객터미널_1차_행동관찰기록지_작성방법포함_보완본': observation(1),
    '연안여객터미널_2차_행동관찰기록지_작성방법포함_보완본': observation(2),
    '연안여객터미널_인터뷰설문지_보완본': interview(),
}

checks={}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    for name,html in DOCS.items():
        html_path=BASE/(name+'.html')
        html_path.write_text(html,encoding='utf-8')
        tab=browser.new_page()
        tab.goto(html_path.as_uri())
        tab.emulate_media(media='print')
        tab.evaluate('document.fonts.ready')
        metrics=tab.evaluate('''() => [...document.querySelectorAll('.page')].map((s,i)=>{
          const main=s.querySelector('main').getBoundingClientRect();
          const f=s.querySelector('footer').getBoundingClientRect();
          return {page:i+1,mainBottom:main.bottom-s.getBoundingClientRect().top,footerTop:f.top-s.getBoundingClientRect().top,gap:f.top-main.bottom};
        })''')
        pdf_path=OUT/(name+'.pdf')
        tab.pdf(path=str(pdf_path),prefer_css_page_size=True,print_background=True)
        reader=PdfReader(pdf_path)
        checks[name]={'pages':len(reader.pages),'layout':metrics,'bytes':pdf_path.stat().st_size}
        for metric in metrics:
            if metric['gap']<5:
                print('LAYOUT WARNING',name,metric)
        print(name,len(reader.pages),'pages',pdf_path.stat().st_size,'bytes')
        tab.close()
    browser.close()
(BASE/'layout_check.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')

README='''연안여객터미널 조사도구 보완본 (2026.11.11)

원본 PDF 3개는 그대로 보존했습니다. 이 폴더의 PDF 3개가 보완본입니다.

1. 1차 행동관찰기록지 / 2차 행동관찰기록지: 각 5쪽, A4 가로
   1쪽: 작성방법과 대상자 선정 원칙
   2쪽: 개별 동선 관찰(필요 수량 복사)
   3쪽: 개별 짐 배치·체류 관찰(해당 사례만 복사)
   4쪽: A·B·C 구간별 30분 보조 집계
   5쪽: 짐 배치·체류 30분 보조 집계

2. 인터뷰 설문지: 5쪽, A4 세로
   1쪽: 조사원 운영 안내(공용)
   2쪽: 기존 공통 Q1~Q7
   3쪽: A 입장 인지, B 중간 복귀, C 도착 후 복귀, 망설임과 이유
   4쪽: 안·밖 짐 배치 이유, 이용 불편, 실제·체감 체류시간
   5쪽: 2차 추가 S1~S4, 1·2차 공통 마무리 T1
   응답자별로 2~5쪽을 묶고, 1차는 S1~S4만 건너뜁니다.

주요 보완
- 기존 행동 코드 A·B·C를 공간 구간 A·B·C로 바꾸었습니다.
- 1·2차 관찰 항목과 기록 기준을 통일했습니다.
- C 구간 앞 짐 보관공간의 안쪽·바깥쪽·양쪽·미배치를 두 차수 모두 기록합니다.
- 1차에는 2차 설치 예정 영역과 동일한 물리적 기준 범위를 사용합니다.
- 실제 체류시간은 초 단위로 측정하고, 본인이 느낀 시간은 인터뷰에서 따로 묻습니다.
- 관찰번호로 행동 유형과 인터뷰 응답을 연결합니다.
- 관찰된 복귀를 실패나 불편으로 단정하지 않고 원래 목적지·복귀 계기·이용 완료 여부를 확인합니다.
- 원활 이동·안쪽 이용 사례도 인터뷰에 포함합니다.
- 기존 Q1~Q7과 2차 공간 인지·이용·의향·예상 편의 항목을 유지했습니다.

현장 적용 전
실제 코스, A·B·C 경계와 관찰 종료 지점, 안쪽 영역·바깥쪽 범위를 도면에 표시해야 합니다.
현재 제공된 원본에는 구체적인 구간 도면이 없어 위치를 임의로 확정하지 않았습니다.
1·2차 모두 같은 경계·시간대·선정 기준·관찰 단위를 사용합니다.
1명 단위와 일행 단위는 합계를 분리합니다. 관찰 누락과 미확인을 0으로 바꾸지 않습니다.
체류시간은 이용객의 전면 범위 진입~이탈이며, 맡긴 짐의 총 보관시간과 다릅니다.
선정한 사례의 수치와 인터뷰 응답은 전체 이용객 비율로 일반화하지 않습니다.

편집자료
HTML 3개와 생성 스크립트, 사용 폰트를 함께 보관했습니다.
HTML은 브라우저에서 열어 인쇄할 수 있습니다(배경 그래픽 켜기, 여백 없음, 배율 100%).
PDF를 다시 생성하려면 Python 환경에 playwright와 pypdf가 필요합니다.
build_revised.py의 FONT 경로는 이 컴퓨터의 원본 폰트 위치입니다.
'''
(OUT/'사용안내_및_보완내용.txt').write_text(README,encoding='utf-8')
