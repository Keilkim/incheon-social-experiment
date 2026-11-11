from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

BASE=Path(__file__).resolve().parent
OUT=BASE.parent

CSS='''
@font-face{font-family:Ko;src:url('fonts/KoPub-Medium.ttf')}
@font-face{font-family:Ko;src:url('fonts/KoPub-Bold.ttf');font-weight:700}
*{box-sizing:border-box}html,body{margin:0;padding:0}body{font:10pt/1.4 Ko,'Apple SD Gothic Neo',sans-serif;color:#19394b;-webkit-print-color-adjust:exact;print-color-adjust:exact}
@page{size:A4 landscape;margin:0}.page{position:relative;width:297mm;height:210mm;padding:11mm 14mm 13mm;overflow:hidden}
.eyebrow{font-size:8.5pt;color:#637985;margin-bottom:2mm}.tag{float:right;color:#087d80;font-weight:700}h1{font-size:20pt;line-height:1.2;margin:0 0 3mm;letter-spacing:-.4pt}p{margin:0 0 2mm}.meta{line-height:1.8;padding:2mm 0;border-top:.3mm solid #b8cbd2;border-bottom:.3mm solid #b8cbd2;margin-bottom:3mm}.callout{background:#edf5f6;border-left:1mm solid #087d80;padding:2.5mm 3mm;margin-bottom:3mm;font-size:9.1pt;line-height:1.5}.small{font-size:8.8pt;line-height:1.45}.muted{color:#637985}
table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:9pt;line-height:1.3}th,td{border:.2mm solid #bfd0d7;padding:1mm 1.5mm;vertical-align:middle}th{background:#e8f1f4;font-weight:700;text-align:center;height:11mm}td{height:6mm;padding:.7mm 1.5mm;text-align:center}td:last-child{text-align:left}tbody tr:nth-child(even){background:#f7f9fa}.total td{background:#edf5f6;font-weight:700}
.footer{position:absolute;left:14mm;right:14mm;bottom:7mm;border-top:.2mm solid #c6d4da;padding-top:1.5mm;display:flex;justify-content:space-between;font-size:7.8pt;color:#637985}
.portrait .page{width:210mm;height:297mm;padding:13mm 15mm 15mm}.portrait{font-size:10.5pt}.portrait .footer{left:15mm;right:15mm;bottom:8mm}.question{margin-top:4mm}.q-title{font-weight:700;font-size:11.5pt;margin-bottom:2mm}.q-title span{color:#087d80;display:inline-block;min-width:8mm}.help{font-size:9pt;color:#637985;margin-bottom:2mm}.answer{border-bottom:.2mm solid #bfd0d7;height:6mm}.checks{line-height:1.8}.portrait .callout{font-size:9.7pt}.portrait h1{font-size:21pt}.endnote{margin-top:5mm;padding-top:3mm;border-top:.3mm solid #b8cbd2}
'''

def shell(title,tag,body,portrait=False):
    css=CSS+('\n@page{size:A4 portrait;margin:0}' if portrait else '')
    return f'''<!doctype html><html lang="ko"><meta charset="utf-8"><title>{title}</title><style>{css}</style><body class="{'portrait' if portrait else ''}"><section class="page"><header><div class="eyebrow">ACT Incheon　|　인천연안여객터미널 <span class="tag">{tag} · 간소화 보완본</span></div><h1>{title}</h1></header><main>{body}</main><footer class="footer"><span>2026.11.11 보완　|　현장 핵심 항목</span><span>1 / 1</span></footer></section></body></html>'''

def observation(phase):
    times=[]
    for m in range(450,900,30):
        times.append(f'{m//60:02d}:{m%60:02d}~{(m+30)//60:02d}:{(m+30)%60:02d}')
    rows=''.join('<tr><td>'+t+'</td><td></td><td></td><td>______ / ______</td><td></td></tr>' for t in times)
    body='''<div class="meta">날짜 __________　조사원 __________　담당 □ A □ B □ C·짐　코스·위치 __________　혼잡·운항 상황 __________</div>
    <div class="callout"><b>A 유도 방향으로 이동 → B 유도선을 따라 이동 → C 짐 배치(밖 / 안).</b> 각 단계에 해당하는 사람 수만 기록합니다.<br>1·2차는 같은 코스·관찰 지점·짐 안팎 경계를 사용합니다. 관찰했으나 없으면 0, 보지 못한 칸은 비워 둡니다.</div>
    <table><colgroup><col style="width:27mm"><col style="width:52mm"><col style="width:52mm"><col style="width:49mm"><col></colgroup><thead><tr><th>시간</th><th>A 입장 구간<br>유도 방향으로 간 사람 수</th><th>B 이동 구간<br>유도선을 따라간 사람 수</th><th>C 보관공간<br>짐을 둔 사람 수 (밖 / 안)</th><th>인터뷰 대상·특이사항<br><span style="font-weight:400">필요할 때만 짧게 메모</span></th></tr></thead><tbody>'''+rows+'''<tr class="total"><td>합계</td><td></td><td></td><td>______ / ______</td><td></td></tr></tbody></table>
    <div class="small" style="margin-top:2mm"><p><b>작성 예시:</b> <b>24 | 12 | 3/5</b> = A 유도 방향으로 간 사람 24명 / B 유도선을 따라간 사람 12명 / C 짐을 밖에 둔 사람 3명·안에 둔 사람 5명.</p><p><b>세는 기준:</b> 각 단계에서 같은 사람은 한 번만 셉니다. C는 짐 개수가 아닌 사람 수이며, <b>밖 / 안</b> 순서로 적습니다. 양쪽에 두거나 옮겼으면 처음 둔 위치로 세고 메모합니다.</p><p class="muted">단계별 차이는 집계 후 계산합니다. 중간 합류·관찰 누락은 메모합니다. 인터뷰에서는 망설임·되돌아감과 짐 배치의 이유를 확인합니다.</p></div>'''
    return shell(f'{phase}차 현장 행동관찰기록지',f'{phase}차 관찰',body)

def answer(n=1):
    return '<div class="answer"></div>'*n

def question(n,title,body,help=''):
    return f'<div class="question"><div class="q-title"><span>{n}</span>{title}</div>'+('<div class="help">'+help+'</div>' if help else '')+body+'</div>'

def interview():
    body='''<div class="meta">차수 □ 1차 □ 2차　날짜 __________　시각 ____:____　조사원 __________<br>인터뷰 위치 __________　원래 가려던 곳 ________________________</div>
    <div class="callout"><b>1·2차 모두 해당되는 질문만 짧게 묻고, 이유를 한 줄로 적습니다.</b><br>1번은 모두, 2번은 망설이거나 되돌아간 사람, 3~4번은 보관공간에 들른 짐 소지자에게 묻습니다. 행동을 관찰한 뒤 참여 의사를 확인하고 질문합니다.</div>'''
    body+=question('1','처음 들어왔을 때 어디로 가야 할지 바로 알 수 있었나요?',
        '<div class="checks">□ 바로 알았음　□ 살펴본 뒤 알았음　□ 알기 어려웠음<br>무엇을 보고 방향을 정하셨나요?</div>'+answer())
    body+=question('2','망설이거나 되돌아간 이유는 무엇인가요?',
        '<div class="checks">해당 지점 □ A 입장 구간 □ B 유도선 구간 □ C 보관공간<br>□ 망설임·되돌아감 없음 → 다음 질문</div>'+answer(2),
        '보관공간 앞까지 왔다가 돌아간 사람은 원래 하려던 일을 마쳤는지도 확인합니다.')
    body+=question('3','짐을 그 자리에 두신 이유는 무엇인가요?',
        '<div class="checks">□ 바깥쪽　□ 안쪽　□ 안·밖 모두　□ 내려놓지 않음</div>'+answer(2),
        '내려놓지 않았다면 그 이유, 자리를 옮겼다면 옮긴 이유를 묻습니다.')
    body+=question('4','짐을 두거나 정리하며 불편하거나 망설였던 점이 있었나요?',
        '<div class="checks">□ 있었음　□ 없었음　□ 이용하지 않음</div>'+answer(2),
        '안쪽에 둔 사람에게도 질문합니다. 바깥쪽·미이용자는 안쪽 공간을 알고 있었는지 확인합니다.')
    body+='''<div class="endnote small"><b>조사원 메모</b>　관찰한 행동과 응답이 다르거나 꼭 남길 내용만 기록'''+answer()+'''<p class="muted" style="margin-top:2mm">응답자가 말한 이유를 그대로 요약합니다. 추측한 원인은 적지 않습니다. 보관공간에 들르지 않았거나 짐이 없으면 3~4번은 건너뜁니다.</p></div>'''
    return shell('현장 인터뷰 — 핵심 4문항','1·2차 공통',body,True)

docs={
    '연안여객터미널_1차_행동관찰기록지_작성방법포함_보완본':observation(1),
    '연안여객터미널_2차_행동관찰기록지_작성방법포함_보완본':observation(2),
    '연안여객터미널_인터뷰설문지_보완본':interview(),
}

checks={}
with sync_playwright() as p:
    browser=p.chromium.launch()
    for name,html in docs.items():
        path=BASE/(name+'.html')
        path.write_text(html,encoding='utf-8')
        tab=browser.new_page()
        tab.goto(path.as_uri())
        tab.emulate_media(media='print')
        tab.evaluate('document.fonts.ready')
        gap=tab.evaluate("document.querySelector('footer').getBoundingClientRect().top-document.querySelector('main').getBoundingClientRect().bottom")
        target=OUT/(name+'.pdf')
        tab.pdf(path=str(target),prefer_css_page_size=True,print_background=True)
        pages=len(PdfReader(target).pages)
        checks[name]={'pages':pages,'footer_gap_px':gap,'bytes':target.stat().st_size}
        print(name,pages,'page / footer gap',round(gap,1))
        assert pages==1 and gap>=8,(name,pages,gap)
        tab.close()
    browser.close()
(BASE/'quick_check.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'사용안내_및_보완내용.txt').write_text('''연안여객터미널 간소화 보완본 (2026.11.11)

PDF 3개, 각각 1쪽입니다. 원본 PDF 3개는 그대로 보존했습니다.

1차·2차 관찰기록지 (A4 가로)
- A: 유도 방향으로 간 사람 수
- B: 유도선을 따라간 사람 수
- C: 짐을 둔 사람 수 (밖 / 안)
- 예: 24 | 12 | 3/5 = A 24명 / B 12명 / C 밖 3명·안 5명
- 각 단계에서 같은 사람은 한 번만 셉니다. 짐은 처음 둔 위치로 밖/안을 구분합니다.
- 같은 코스에서 각 단계의 사람 수를 30분 단위로 셉니다.
- 한 사람이 전 구간을 추적하거나 개인별 상세지를 쓰는 방식은 제외했습니다.
- 1·2차 모두 같은 항목과 공간 경계를 사용합니다.
- 이탈 인원은 별도 기록하지 않습니다. 같은 이용객 집단 기준으로 집계하면 A-B, B-(C밖+C안)으로 계산할 수 있습니다.
- 시간대 경계를 넘긴 이동, 중간 합류, 관찰 누락이 있으면 단계별 차이를 실제 이탈로 단정하지 않고 메모를 함께 확인합니다.

인터뷰 (A4 세로, 1·2차 공통, 핵심 4문항)
1. 입장 직후 방향을 알았는지, 무엇을 보고 정했는지
2. 망설이거나 되돌아간 이유
3. 짐을 그 자리에 둔 이유
4. 불편하거나 망설였던 점

해당되는 질문만 묻습니다. 관찰은 인터뷰 대상을 찾는 용도로 활용합니다.
되돌아간 사람뿐 아니라 안쪽·바깥쪽 짐 배치와 원활 이용 사례도 짧게 확인합니다.
관찰 전에 A·B·C 위치와 보관공간 안·밖 경계만 현장에서 함께 맞춥니다.

편집자료의 build_quick.py와 HTML 3개가 현재 간소화 보완본의 편집 원본입니다.
''',encoding='utf-8')
