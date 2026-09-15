"""기존 기록부 양식을 읽어 200명 기준 사전/1차/2차 입력 서식을 만든다."""
from pathlib import Path
from datetime import time
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.pagebreak import Break
from openpyxl.utils import get_column_letter as column
from openpyxl.formatting.rule import FormulaRule

ROOT=Path(__file__).resolve().parents[1]
COLORS=['E85B61','F39A46','F2CD4C','61B77B','579BDE']

def build(phase):
    name=['사전조사','1차 실험','2차 실험'][phase]
    label=['사전','1차','2차'][phase]
    dest=ROOT if phase==0 else ROOT.parent/name
    wb=Workbook(); info=wb.active; info.title='사용법'
    for row in [
        ['입력용 기록부 · '+name,'200명/응답 기준 · 2026.09.13'],
        ['준비한 행','001~200은 입력칸. 실제 관찰/응답만 입력합니다. 빈칸은 미관찰·무응답, 관찰 결과 없음은 0.'],
        ['반복 측정','선인재단 5개 위치×200행. 약산초 200명×사진6개. 반복행 수를 사람 수로 세지 않습니다.'],
        ['기록 단위','선인재단·터미널·로데오·인터뷰는 개인. 송도·굴포천 관찰은 사람 또는 무리 200건(실제 인원은 합산).'],
        ['선인재단 코드','각 위치 기록번호는 현장 순서. 출발 001의 코드는 S001. 뒤 위치에서는 확인된 코드만 씁니다.'],
        ['특징','종이에 적은 옷·가방 특징 한 줄을 옮깁니다. 같은 교복·가방이면 특징만으로 확정하지 않습니다.'],
        ['짝맞춤','출발코드별 위치 기록번호·시각을 입력. 확인 O만 계산. △/X/시각누락/도착이 더 이른 행은 계산하지 않습니다.'],
        ['시각','08:12:34처럼 시:분:초 입력. 같은 날의 시각으로 계산합니다.'],
        ['표정 점수','5색 응답: 빨강1·주황2·노랑3·초록4·파랑5. 점수는 분석 입력값입니다.'],
        ['선인재단 척도','사전 힘든 정도 1 안 힘듦~5 매우 힘듦. 1·2차는 웃음/보통/힘듦 3범주. 5점 척도로 바꾸지 않습니다.'],
        ['원래 보기','차이나타운 Q3 동기 정도, Q4 강하게~부드럽게, 봤나 O/X/?, 송도 O/△/X는 원래 보기 유지.'],
        ['행태','관찰한 행동 ✓=1, 관찰했으나 해당 없음=0. 못 본 항목은 빈칸.'],
        ['인원수','송도·굴포천에서 혼자면 1, 무리는 인원수 입력. 선인재단은 학생별 한 행.'],
        ['스티커','각 칸 스티커를 세어 입력. 준비 기준 200을 실제 응답수로 채우지 않습니다.'],
        ['개인정보','이름·연락처는 쓰지 않습니다. 송도 모집 연락처는 운영용으로 별도 관리.'],
    ]:info.append(row)
    info.column_dimensions['A'].width=20;info.column_dimensions['B'].width=100
    for r in range(2,info.max_row+1):info.row_dimensions[r].height=32
    def sheet(title,heads,n=200):
        w=wb.create_sheet(title);w.append(heads)
        for num in range(1,n+1):w.append([label if h=='회차' else num if h=='번호' else None for h in heads])
        for c,h in enumerate(heads,1):
            w.column_dimensions[column(c)].width=28 if any(x in h for x in ('원문','비고','특징','메모')) else min(24,max(11,len(h)*1.5))
            for r in range(2,n+2):
                if '시각' in h:w.cell(r,c).number_format='hh:mm:ss'
                elif '번호'==h or '기록번호' in h:w.cell(r,c).number_format='000'
            if '1~5' in h:
                v=DataValidation(type='whole',operator='between',formula1=1,formula2=5,allow_blank=True);v.showErrorMessage=True;v.error='1~5만 입력하세요.'
                w.add_data_validation(v);v.add(f'{column(c)}2:{column(c)}{n+1}')
        w.freeze_panes='A2';w.auto_filter.ref=w.dimensions;w.print_title_rows='1:1'
        w.print_area=f'A1:{column(len(heads))}{n+1}';w.sheet_properties.pageSetUpPr.fitToPage=True
        w.page_setup.orientation='landscape';w.page_setup.paperSize=w.PAPERSIZE_A4;w.page_setup.fitToWidth=1;w.page_setup.fitToHeight=0
        for row in range(26,n+1,25):w.row_breaks.append(Break(id=row))
        return w
    y=sheet('약산초_설문',['회차','번호','학년','반','사진번호','봤나(봄/못봄/모름/안다님)','어디서(지도번호)','어떻게 말할지(원문)','비고'],1200)
    for i in range(1200):y.cell(i+2,2,i//6+1);y.cell(i+2,5,i%6+1)
    s=sheet('선인재단_기록',['회차','위치','번호','옷·가방 특징','출발코드','시각','동선','휴대폰 봄','대화','앞만 봄','그냥 올라감','뛰어놂','관찰함']+(['그림 봄','표정(웃음/보통/힘듦)'] if phase else ['힘든 정도 1~5'])+['비고'],1000)
    for i in range(1000):
        r=i+2;pos=i//200+1;num=i%200+1;s.cell(r,2,pos);s.cell(r,3,num)
        if pos==1:s.cell(r,5,f'S{num:03d}')
    m=sheet('선인재단_짝맞춤',['출발코드','옷·가방 특징','위치1 기록번호','위치1 시각','위치2 기록번호','위치2 시각','위치3 기록번호','위치3 시각','위치4 기록번호','위치4 시각','위치5 기록번호','위치5 시각','확인 O/△/X','1→2 초','2→3 초','3→4 초','4→5 초','1→5 초','비고'])
    v=DataValidation(type='list',formula1='"O,△,X"',allow_blank=True);m.add_data_validation(v);v.add('M2:M201')
    for r in range(2,202):
        m.cell(r,1,f'S{r-1:03d}');m.cell(r,3,r-1)
        for out,a,b in [(14,'D','F'),(15,'F','H'),(16,'H','J'),(17,'J','L'),(18,'D','L')]:
            m.cell(r,out,f'=IF(AND($M{r}="O",ISNUMBER({a}{r}),ISNUMBER({b}{r}),{b}{r}>={a}{r}),ROUND(({b}{r}-{a}{r})*86400,0),"")')
    codes=DataValidation(type='list',formula1='INDIRECT("\'선인재단_짝맞춤\'!$A$2:$A$201")',allow_blank=True)
    codes.showErrorMessage=True;codes.error='S001~S200 중 확인한 출발코드를 입력하세요.'
    s.add_data_validation(codes);codes.add('E2:E1001')
    s.conditional_formatting.add('E2:E1001',FormulaRule(formula=['AND(E2<>"",COUNTIFS($B$2:$B$1001,$B2,$E$2:$E$1001,$E2)>1)'],fill=PatternFill('solid',fgColor='FFCCCC')))
    info.append(['관찰된 출발 학생 수','=COUNTIFS(선인재단_기록!B2:B1001,1,선인재단_기록!F2:F1001,"<>")'])
    info.append(['통과시간 계산 가능 수','=COUNT(선인재단_짝맞춤!R2:R201)'])
    info.append(['코드 확인','같은 위치에 같은 출발코드가 2번 들어가면 빨간 배경으로 표시됩니다. 확인 후 수정하세요.'])
    sheet('송도_기록',['회차','구간','번호','인원수','시각','걷기','달리기','뛰다가 숨고르기','구경하기','휴대폰하고 놀기']+(['매개 요소 이용'] if phase==2 else [])+['비고'])
    sheet('송도_인터뷰',['회차','번호']+(['Q1 참여 O/△/X','Q2 소통 기대 O/△/X','Q3 이유(원문)','Q4 필요한 것(원문)'] if phase==0 else ['Q1 소통 O/△/X','Q2 이유(원문)','Q3 '+('더 필요한 것(원문)' if phase==1 else '도움된 요소(원문)')])+['비고'])
    sheet('굴포천_기록',['회차','번호','인원수','들어온 시각','나간 시각','뛰기','걷기','놀기','앉아서 쉬기(휴대폰X)','앉아서 쉬기(휴대폰O)','대화','비고'])
    sheet('굴포천_영상결과',['회차','번호','추적번호','처음 보인 시각','마지막 시각','머문 초','멈춘 초','중앙 속도(m/s)','들른 구역','비고'])
    sheet('굴포천_지나감_예비',['회차','그냥 지나간 사람(카메라 안 될 때)','비고'],1)
    sheet('로데오_사람',['회차','번호','시각','어디서(부스안/벤치/그밖)','몸 방향(안쪽/바깥/?)','꽁초(수거함/바닥/?)']+(['사인 보고 왔나(예/아니오/?)'] if phase==2 else [])+['비고'])
    sheet('터미널_2층',['회차','번호','앉은 시각','일어난 시각','자리 위치(의자 번호)']+(['만족도 1~5','위생·안심도 1~5'] if phase==0 else [])+['비고'])
    t=sheet('터미널_1층캐리어',['회차','번호','시각','보관 공간 내 개수','보관 공간 외 개수','비고'],17)
    for i in range(17):t.cell(i+2,3,time(12+i//4,i%4*15))
    keys=([('차이나타운','사용언어')]+[('차이나타운',f'Q{i}') for i in range(1,5)] if phase<2 else [])+[('굴포천',f'Q{i}') for i in range(1,5)]+([('터미널',f'Q{i}') for i in range(1,3)] if phase else [])
    b=sheet('스티커_폼보드',['회차','거점','문항','1','2','3','4','5','응답수 합계','비고'],len(keys))
    for r,(place,q) in enumerate(keys,2):
        b.cell(r,2,place);b.cell(r,3,q);b.cell(r,9,f'=IF(COUNT(D{r}:H{r})=0,"",SUM(D{r}:H{r}))');b.cell(r,10,'5색 응답' if place in ('굴포천','터미널') else '원 보기 순서대로 입력')
    if phase==1:sheet('약산초_워크숍',['회차','번호','학급','붙인 이름','무엇을 그렸나','어디에 두고 싶나(지도번호)','왜 거기(원문)','뽑힘','비고'])
    if phase==2:sheet('차이나타운_웹기록',['날짜','QR 접속','에티켓 확인','확인시간 중앙값(초)','좋아요','나빠요','무응답','비고'],14)
    l=wb.create_sheet('표정_코드표');l.append(['점수','색상','의미'])
    for i,(color,text) in enumerate(zip(COLORS,['매우 안 좋음','안 좋음','보통','좋음','매우 좋음']),1):
        l.append([i,['빨강','주황','노랑','초록','파랑'][i-1],text]);l.cell(i+1,2).fill=PatternFill('solid',fgColor=color)
    l.column_dimensions['B'].width=15;l.column_dimensions['C'].width=24
    for w in wb:
        for row in w:
            for c in row:c.font=Font(name='맑은 고딕',size=10);c.alignment=Alignment(wrap_text=True,vertical='center')
        for c in w[1]:c.font=Font(name='맑은 고딕',bold=True,size=10,color='FFFFFF');c.fill=PatternFill('solid',fgColor='153C68')
        w.row_dimensions[1].height=36
    out=dest/'08_입력용_기록부.xlsx';wb.save(out);print(out)

if __name__=='__main__':
    for phase in (0,1,2):build(phase)
