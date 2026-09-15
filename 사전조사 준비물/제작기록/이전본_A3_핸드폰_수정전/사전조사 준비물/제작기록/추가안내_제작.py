"""200건 인쇄·표정 적용 안내, 선인재단 매칭 운영표."""
from pathlib import Path
import 도구_공통 as C
import 조사지_제작 as M
from playwright.sync_api import sync_playwright

MATCH = """# 선인재단 위치별 기록 맞추기 · 현장 운영

관찰 기록은 200명 기준으로 준비합니다. 위치 1~4마다 25줄×8장, 총 32장입니다. 4번이 마지막 도착 지점입니다. 통과시간 결과에는 동일 학생으로 확인된 수를 따로 적습니다.

1. **시작 전**: 위치 1 출발 · 2~3 중간 · 4 도착을 정하고 초까지 시계를 맞춥니다.
2. **기록 단위**: 학생 한 명당 한 줄. 각 위치의 번호 001~200은 그 위치에서 기록한 순서입니다. 함께 오는 학생도 개인별로 씁니다.
3. **특징 한 줄**: 상의색/가방색/눈에 띄는 소지품만 짧게 적습니다. 예: 검정상의/빨강가방, 흰상의/파랑가방/우산. 이름·얼굴 특징·사진은 받지 않습니다.
4. **중간·도착**: 내 위치의 다음 줄에 특징·시각을 적습니다. 기록번호가 같거나 먼저 도착했다는 이유로 같은 학생으로 보지 않습니다. 특징·시각은 보조 단서이며 그것만으로 확정하지 않습니다.
5. **몰릴 때**: 동일 학생인지 놓쳤으면 비고에 ‘미확인’으로 남깁니다. 순서만으로 억지로 연결하지 않습니다. 놓친 학생은 비고에 누락으로 표시합니다.
6. **끝난 뒤**: 같은 학생임이 확인된 위치별 기록번호·시각을 엑셀 짝맞춤 시트에 옮깁니다. 확실함 O만 시간 분석, △ 불확실/X 연결 안 됨은 제외. 같은 위치 기록번호를 중복 연결하면 먼저 확인합니다.

**추월 예시**: 위치1의 002 학생이 먼저 도착하면 위치4에서는 001로 적힐 수 있습니다. 동일 학생임이 확인되면 짝맞춤 시트의 위치1 기록번호=002, 위치4 기록번호=001로 연결합니다.

옷·가방 특징만으로 200명 모두의 연결을 보장할 수는 없습니다. 실제 관찰수와 시간 분석에 쓴 확실한 연결 수를 구분합니다.

종이 묶음은 조사일·거점·회차별로 따로 보관합니다. 날짜가 다른 기록의 같은 번호를 같은 학생으로 간주하지 않습니다.
"""

def build():
    root=C.ROOT
    (root/'02_선인재단_매칭안내.md').write_text(MATCH)
    sections = [
        ('시작 전','<b>1 출발 · 2~3 중간 · 4 도착</b>. 4번이 마지막 지점입니다. 모든 담당자가 초까지 시계를 맞춥니다.'),
        ('학생 한 명씩','각 위치 번호 001~200은 그 자리에서 적은 순서입니다. 함께 오는 학생도 한 명씩 적습니다.'),
        ('번호 뒤 특징 한 줄','상의색/가방색/소지품만. 예: <b>검정상의/빨강가방</b>, <b>흰상의/파랑가방/우산</b>. 이름·얼굴 특징·사진은 받지 않습니다.'),
        ('중간·도착에서는','내 위치의 다음 줄에 특징·시각을 적습니다. <b>같은 번호나 도착순서만으로 같은 학생이라고 보지 않습니다.</b> 특징·시각은 보조 단서입니다.'),
        ('한꺼번에 몰리면','동일 학생인지 놓쳤으면 비고에 미확인, 관찰 자체를 놓쳤으면 누락을 남깁니다. 순서만으로 억지로 연결하지 않습니다.'),
        ('조사 후','동일 학생임이 확인된 위치별 기록번호·시각을 엑셀에 옮깁니다. <b>확실함 O만 시간 계산</b>, △ 불확실/X 미연결은 제외. 같은 위치 기록번호를 중복 연결하면 확인합니다.'),
    ]
    body = M.hd('선인재단','위치별 기록 맞추기','위치별 8장 × 4곳 = 32장')
    body += '<div class="how"><b>200명은 기록 용량입니다.</b> 통과시간 분석에는 실제로 연결된 학생 수를 따로 적습니다.</div>'
    for i,(title,desc) in enumerate(sections,1):
        body += f'<div style="padding:8px 0;border-bottom:1px solid #C3CFDB"><b style="font-size:11pt;color:#153C68">{i}. {title}</b><div style="font-size:10pt;margin-top:3px">{desc}</div></div>'
    body += '<div class="legend" style="font-size:10pt"><b>추월 예시</b><br>위치1의 002 학생이 먼저 도착 → 위치4에서는 001로 기록될 수 있음<br>동일 학생 확인 후: 위치1 기록번호 002 ↔ 위치4 기록번호 001</div>'
    body += '<div class="warn" style="font-size:9.3pt">옷·가방 특징만으로 200명 모두의 연결을 보장할 수는 없습니다. 실제 관찰수와 시간 분석에 쓴 확실한 연결 수를 구분합니다.</div>'
    body += '<div class="note">종이는 조사일·거점·회차별로 따로 보관. 날짜가 다른 기록의 같은 번호를 같은 학생으로 간주하지 않습니다.</div>'
    for folder,phase in [(root,'사전조사'),(root.parent/'1차 실험','1차 실험'),(root.parent/'2차 실험','2차 실험')]:
        C.render([body],folder/'02_선인재단_매칭안내.pdf',extra_css=M.CSS,footer=phase)
    labels=['매우 안 좋음','안 좋음','보통','좋음','매우 좋음']
    faces='<div style="display:flex;gap:20px;margin:35px 0">'+''.join(f'<div style="flex:1;text-align:center">{C.face(i,"26mm")}<div style="font-size:12pt;margin-top:8px">{t}</div></div>' for i,t in enumerate(labels,1))+'</div>'
    content=M.hd('수정 안내','표정 5종 · 200건 인쇄','2026.09.13 적용')+faces
    content+='<div class="how"><b>빨강 → 주황 → 노랑(보통) → 초록 → 파랑</b><br>개별 PNG는 배경 투명, SVG는 확대 인쇄용입니다.</div>'
    rows=[('표정 적용','굴포천 사전·1·2차의 매력도·만족도·재방문·기대·이용의향, 터미널 사전 기록표와 1·2차 폼보드의 만족도·위생 안심도'),('3단계 유지','선인재단 1·2차: 웃음(파랑)·보통(노랑)·힘듦(빨강). 기존 3범주 유지'),('숫자·원래 보기 유지','선인재단 사전 힘든 정도, 차이나타운 Q3 동기 정도·Q4 문구 강도, 예/아니오·모름, O/△/X, 사진·지도·위치 번호'),('번호 있는 기록표','송도 인터뷰 001~050 · 25줄×2장. 나머지 기록표 001~200 · 25줄×8장. 선인재단은 4곳×8장=32장'),('개별 어린이 설문','지도+설문지 2쪽을 200부 인쇄(총 400면, 양면 200장). 1차 파일의 3~10쪽 워크숍 기록은 별도 1세트'),('시간표·보드','캐리어 15분 시간표 17회와 일별 웹 집계표는 그대로. 보드는 각 1판, 문항별 200명 응답분 스티커 준비'),('스티커 수량','굴포천 4문항 최대 800개, 터미널 2문항 최대 400개, 차이나타운 언어+4문항 최대 1,000개. 무응답·건너뜀은 별도'),('번호와 실제 표본수','송도·굴포천 관찰은 200건(개인 또는 무리); 인원수 합계는 따로 계산. 준비한 행 수를 실제 표본수로 쓰지 않음')]
    content+='<table><colgroup><col style="width:125px"><col></colgroup><tbody>'+''.join(f'<tr><th style="font-size:10pt">{a}</th><td style="font-size:10pt;padding:9px">{b}</td></tr>' for a,b in rows)+'</tbody></table>'
    C.render([content],root/'00_표정과_200건_인쇄안내.pdf',extra_css=M.CSS)
    preview='<html><meta charset="utf-8"><style>body{font-family:Paperlogy,sans-serif;margin:0;background:#fff;color:#25364A}.preview{padding:36px}h1{font-size:28px;margin:0}p{font-size:16px;color:#5A6B7D}img{width:180px!important;height:180px!important}</style><div class="preview"><h1>다섯 가지 표정</h1><p>빨강 → 주황 → 노랑(보통) → 초록 → 파랑 · 개별 아이콘은 배경 투명</p>'+faces+'</div></html>'
    (root/'표정아이콘/미리보기.html').write_text(preview)
    with sync_playwright() as p:
        b=p.chromium.launch();pg=b.new_page(viewport={'width':1200,'height':400});pg.set_content(preview);pg.screenshot(path=str(root/'표정아이콘/표정5종_미리보기.png'));b.close()
    print('매칭 안내 3종, 인쇄안내, 아이콘 미리보기 완료')

if __name__=='__main__':build()
