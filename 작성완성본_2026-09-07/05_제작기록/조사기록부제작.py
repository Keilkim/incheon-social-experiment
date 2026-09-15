# -*- coding: utf-8 -*-
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
ROOT=Path(__file__).resolve().parents[1]
wb=Workbook();ws=wb.active;ws.title='사용안내'
rows=[['통합 조사기록부','2026.09.07 작성안'],['자료 상태','실측 데이터가 없는 빈 입력 양식입니다. 예시 결과를 넣지 않았습니다.'],['함께 볼 문서','21_조사설계와현장운영: 질문·관찰단위·분모·제외 기준을 확인하세요.'],['회차','사전, 1차, 2차'],['빈값과 0','미조사는 빈값/NA, 관찰했지만 발생하지 않은 경우는 0을 입력합니다.'],['익명번호','분석용 번호만 사용합니다. 이름·연락처는 이 파일에 입력하지 않습니다.'],['시간','날짜와 시작·종료시각을 각각 입력하고 자정을 넘으면 날짜도 구분합니다.'],['상행·세션·물품','통행 건수·웹 세션·물품 수를 고유 인원과 혼용하지 않습니다.'],['표본과 분모','누락·경계 표본·노출 없음·무응답을 별도 표시합니다. 분모가 0이면 비율 산출 불가입니다.'],['확정 사항','후보 위치·문항·관찰창은 현장 협의 후 고정하고 버전을 기록합니다.']]
for r in rows:ws.append(r)
common=['일자','회차','관찰창','구역번호','조사자']
specs=[
('공통현장일지',['대상지',*common,'시작시각','종료시각','유효관찰분','날씨','기온','설치버전','청소·행사·운항 등 변화','개입시각','변경·중단 이유','자료파일명']),
('약산초_인지설문',[*common,'익명번호','학년','통학경로','구간노출여부','노출통학일수','워크숍참여','이미지시설번호','A1 봄·못봄·모름·비경로','A2 선택위치','A2 정오·모름','A3 위치설명 원문','설명점수 0~2','정답안내개입','비고']),
('약산초_아이디어',[*common,'익명번호','시민·어린이','제안번호','이름','형태·색·상징','행동단서','제안장소번호','장소유형','선택이유','선정여부','수정이유','비고']),
('선인재단_관찰',[*common,'관찰사건번호','상행여부','혼자·동행','진입시각','중간시각','도착시각','연결완전여부','주시','가리키기','알리기','나란히','기다림','멈춤','웃음·미소','휴대전화','추월·뜀','안전특이사항']),
('선인재단_설문',[*common,'응답번호','재미 1~5','힘듦 1~5','재이용의향 1~5','기억표시 원문','비고']),
('송도_참여',[*common,'익명참여번호','신청회차','혼자·지인동반','참여목적','교류기회','선택언어','선택학교','선택국적범주','출석','활동시작','활동종료','재참여의향 1~5','1차참여여부','2차실제참여','비고']),
('송도_관찰설문',[*common,'익명참여번호 또는 사건번호','입장시각','퇴장시각','경계표본','걷기','달리기','휴식','대화','요소번호','요소사용','운영자와교류','새참여자교류 확인응답','사전지인여부','기본공간도움 1~5','추가요소도움','상권실제·계획·없음','쿠폰익명번호','비고']),
('차이나타운_설문',[*common,'응답번호','선택언어','C1 안내인지','QR실제열림 응답','C2 이미지선택','C2 정오·모름','C3 내용문항버전','C3 응답','C3 정오·모름','찾기쉬움 1~5','표현부담없음 1~5','표현선호','개선의견','비고']),
('차이나타운_웹사건',['일자','회차','지점번호','익명세션','사건시각','사건명','시험접속','중복여부','비활성·오류','유효기록여부','비고']),
('굴포천_관찰',[*common,'방문사건번호','입장시각','퇴장시각','연결완전여부','경계표본','멈춤3초이상','착석','감상','만짐','대화','촬영','휴식','운동·놀이','활동방해','가용좌석수','가용물품수','비고']),
('굴포천_대여',[*common,'물품번호','품목','대여시각','반납시각','실제사용확인','반납상태','손상','청소소요분','비고']),
('굴포천_설문',[*common,'응답번호','현재매력 1~5','현재만족 1~5','재이용의향 1~5','사전전시기대 1~5','작품공간어울림 1~5','활동방해 1~5','타공간이용의향','비고']),
('로데오_행동',[*common,'흡연사건번호','시작시각','종료시각','흡연위치','방향확인시각','내부·외부·혼합','꽁초처리위치','처리끝확인여부','사인주시','방향전환','부스유입','보행방해','사인유입 응답','불편의견','비고']),
('로데오_환경',[*common,'관찰시작시각','시작전꽁초','시작청소','종료시각','신규바닥꽁초','수거부회수','중간청소시각','중간회수량','기타쓰레기','풍향','단속·행사','비고']),
('터미널_시점',[*common,'관찰시각','1층일반대기인원','2층일반휴식인원','가용좌석수','짐구역내','짐경계','짐구역밖','통로방해','항로·편','지연·결항','단체승객 등 특이사항']),
('터미널_이용설문',[*common,'이용사건번호','휴식시작','휴식종료','연결완전여부','경계표본','자리유형','휴식목적확인','출항까지시간구간','안내이해 1~5','공간만족 1~5','청결인식 1~5','위생안심 1~5','1층잔류이유','향기평가','비고']),
('협의제작관리',['대상지','항목','담당기관·주체','요청일','협의상태','확정내용','임시·고정구분','수량','견적금액','제작·설치일','관리·철수조건','증빙파일','비고'])]
for name,heads in specs:
 w=wb.create_sheet(name);w.append(heads)
 for row in range(2,32):
  for col in range(1,len(heads)+1):w.cell(row,col,'')
 if '회차' in heads:
  dv=DataValidation(type='list',formula1='"사전,1차,2차"',allow_blank=True);w.add_data_validation(dv);ci=heads.index('회차')+1;letter=w.cell(1,ci).column_letter;dv.add(f'{letter}2:{letter}10000')
 w.freeze_panes='F2' if len(heads)>8 else 'A2';w.auto_filter.ref=w.dimensions
 w.sheet_view.zoomScale=85
 for col,h in enumerate(heads,1):w.column_dimensions[w.cell(1,col).column_letter].width=25 if any(x in h for x in ['원문','의견','특이','이유','내용']) else 18
for w in wb:
 for cell in w[1]:cell.font=Font(name='맑은 고딕',size=11,bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='153C68');cell.alignment=Alignment(wrap_text=True,vertical='center')
 w.row_dimensions[1].height=38
 for row in w.iter_rows(min_row=2):
  for c in row:
   c.font=Font(name='맑은 고딕',size=10);c.alignment=Alignment(vertical='top',wrap_text=True);c.border=Border(bottom=Side(style='hair',color='DFE7EF'))
   if c.row%2==0:c.fill=PatternFill('solid',fgColor='F3F7FB')
 w.print_options.horizontalCentered=True;w.sheet_properties.pageSetUpPr.fitToPage=True;w.page_setup.orientation='landscape';w.page_setup.paperSize=w.PAPERSIZE_A3;w.page_setup.fitToWidth=1;w.page_setup.fitToHeight=0;w.print_title_rows='1:1'
ws.column_dimensions['A'].width=23;ws.column_dimensions['B'].width=106
wb.save(ROOT/'03_분석과조사설계'/'22_현장조사_빈기록부.xlsx')
print('Workbook sheets:',len(wb.sheetnames))
