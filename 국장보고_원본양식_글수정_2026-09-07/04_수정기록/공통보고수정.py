# -*- coding: utf-8 -*-
import json, re, sys, io
from pathlib import Path
import fitz
from 원본양식수정 import Editor, ROOT, WORK, SOURCE, save_pdf, write_pptx, GRAY, NAVY, WHITE, color, ltext
SRC='인천창의디자인_국장님보고.pdf'
EXTRA='인천창의디자인_국장님보고_2_선인재단, 굴포천.pdf'
CYAN='28B0D5'; BLUE='31509E'

def block(e,idx,text,size=None,ink=None,align='left',rect=None):
 data=json.loads((Path('/tmp/incheon_original_layout')/(e.source+'.json')).read_text())[e.pn-1]
 b=data['blocks'][idx];sp=b['lines'][0]['spans'][0]
 r=fitz.Rect(rect or b['bbox']);r.y1+=1
 fs=size or sp['size'];c=ink or f'{sp["color"]:06X}'
 e.wipe(fitz.Rect(b['bbox'])+(-.4,-.25,.4,.25),absolute=True)
 e.put(r,text,size=fs,font='B' if 'Bold' in sp['font'] else 'R',ink=c,absolute=True,minsize=fs*.62,align=align)

def exact(e,old,new):
 for l in e.original_lines:
  if old in ltext(l):
   # Keep the replacement at the original line's position and baseline region.
   r=fitz.Rect(l['bbox']);fs=max(s['size'] for s in l['spans']);c=l['spans'][0]['color']
   e.wipe(r+(-.25,-.2,.25,.2),absolute=True)
   e.put(r+(0,0,2,1),ltext(l).replace(old,new),size=fs,font='M',ink=f'{c:06X}',absolute=True,minsize=fs*.7)

def common():
 out=[]
 for n in range(1,16):
  print('COMMON',n,flush=True);e=Editor(SRC,n,f'공통 보고 {n}')
  if n==1:block(e,2,'2026. 09. 07',size=15,ink=WHITE)
  if n==2:exact(e,'CONTENS','CONTENTS');block(e,16,'3. 실험별 세부계획',size=9.5,ink=WHITE)
  if n==4:
   block(e,10,'● 4개 분야\n  현재 7개 구체안',size=9)
   block(e,17,'과업범위',size=9,rect=(202.4,489.9,259,507.7))
   e.put((271.8,489.9,810,507.7),'계획: 4개 분야·8개소 내외 / 현재 제공된 구체안: 7개 거점·최종 실행 범위 협의',size=9,font='R',absolute=True,minsize=7)
  if n==5:
   block(e,2,'사회실험은 생활공간에 작은 변화를 적용하고, 시민이 실제 사용하는 과정에서 행동과 인식을 관찰하는 방법이다.\n사전·1차·2차의 조건과 측정 단위를 정해 비교하며, 예상과 다른 결과도 다음 설계를 위한 근거로 남긴다.',size=12.5,ink=GRAY)
   block(e,3,'정의: 본 사업의 실행·조사 기준으로 정리 · 2026.09.07 회의 반영',size=6.8)
   e.wipe((420,340,580,377),absolute=True)
   e.put((208,252,791,291),'작게 바꾸고, 실제로 사용하고, 결과로 다시 다듬습니다',size=20,font='B',ink=CYAN,absolute=True)
   e.put((209,323,792,453),'사전 | 기존 이용과 불편을 같은 구역·시간대에서 확인\n1차 | 시민 아이디어를 시제품으로 구현하고 반응 관찰\n2차 | 회의·1차 관찰을 반영해 조건을 조정하고 재측정\n결과 | 행동·체감·운영 부담을 함께 보고 후속 적용 판단',size=14,font='M',ink=GRAY,absolute=True)
   e.put((209,485,792,519),'조사 결과는 날짜·대상·응답 수·분모와 함께 제시하며, 가상 성과 수치를 넣지 않습니다.',size=11,font='R',absolute=True)
  if n==6:
   exact(e,'검증된 치수로','확인한 조건으로');exact(e,'정식 제작함','적용을 검토함')
   exact(e,'잘 맞은 것은 상설로 · 안 맞은 것은 다음 실험의 조건으로 진행함','효과·관리·비용을 함께 검토해 상설화 후보와 후속 실험 조건을 정함')
  if n==7:
   # Existing reference photos and all six circular graphics stay in place.
   e.wipe((25,279,208,332),absolute=True)
   e.put((108.7,317.4,171,338),'핵심 문제',size=12,font='B',absolute=True)
   e.wipe((108,437,173,460),absolute=True)
   e.put((108.7,438.1,173,460),'측정 관점',size=12,font='B',absolute=True)
   block(e,1,'환경정비와 이용 안내\n기존 무단투기 캠페인 참고 이미지',size=13,ink=NAVY)
   block(e,2,'행동을 유도하는 참여 장치\n기존 신호대기 디자인 참고 이미지',size=13,ink=NAVY)
   e.wipe((195,313,823,414),absolute=True)
   e.put((197.9,314.4,488,354),'생활공간의 불편을 공간·안내·관리 관점에서 파악\n행동이 발생한 장소와 운영 조건을 함께 확인',size=9.6,font='M',absolute=True)
   e.put((524.8,314.4,816,354),'시선을 끄는 장치가 실제 행동으로 이어지는지 확인\n이용자 반응과 보행 흐름을 함께 관찰',size=9.6,font='M',absolute=True)
   e.put((197.9,372,488,412),'정비·안내·교육·관리를 결합한 실험 구조 참고\n공식 확인 사례와 출처는 다음 쪽에 제시',size=9.5,font='R',absolute=True)
   e.put((524.8,372,816,412),'참여 방식과 비교 조건을 먼저 정한 뒤 측정\n사진의 캠페인 수치를 인천 성과로 전용하지 않음',size=9.5,font='R',absolute=True)
   e.wipe((195,436,820,500),absolute=True)
   for x,cap,val in [(204,'행동 지표','발생량'),(307,'이용 지표','참여'),(404,'관리 지표','유지'),(527,'인지 지표','식별'),(632,'경험 지표','체감'),(735,'운영 지표','부담')]:
    e.put((x,440,x+78,460),cap,size=9,font='M',absolute=True,align='center')
    e.put((x,468,x+78,495),val,size=17,font='B',ink=CYAN,absolute=True,align='center')
   e.wipe((195,532,822,556),absolute=True)
   e.put((197.9,534.2,489,555),'단기 반응과 지속적인 관리 가능성을 함께 판단',size=9.5,font='B',absolute=True)
   e.put((524.8,534.2,816,555),'눈에 띔·클릭·인지·행동의 차이를 구분',size=9.5,font='B',absolute=True)
  if n==8:
   block(e,5,'공식 자료로 확인한 실행·평가 방식',size=20,ink=CYAN,rect=(292.2,263.2,799,296))
   # The original blank case-study panel has no drawing or image to relocate.
   e.put((181,135,811,162),'해외 사례는 기대 성과율이 아닌 실험·평가·운영 절차를 참고합니다.',size=13,font='M',ink=CYAN,absolute=True)
   e.put((181,313,811,341),'뉴욕 교통국 | Green Light for Midtown 평가 보고서 (2010.01)',size=13,font='B',absolute=True)
   e.put((181,348,811,393),'임시 보행공간 적용 뒤 보행·이동·안전·이용 경험을 여러 지표로 평가했다.\n인천에서도 이용 변화와 운영 부담을 함께 비교한 뒤 고정시설 후보를 검토한다.',size=11.5,font='R',absolute=True)
   e.put((181,410,811,436),'캔터베리 뱅크스타운 시 | 무단투기 환경개선 사례 (2024.06.13)',size=13,font='B',absolute=True)
   e.put((181,445,811,488),'환경정비·안내·교육·관리 요소를 결합한 사례다. 디자인 하나의 효과로 단정하지 않는다.\n로데오거리도 시설·안내·청소 조건을 기록하고, 다른 개입과 함께 결과를 해석한다.',size=11.5,font='R',absolute=True)
   e.put((181,515,811,548),'출처: NYC DOT, Green Light for Midtown Evaluation Report / City of Canterbury Bankstown,\nBeautification project roots out dumpers. 원문 링크는 「수정 내용과 출처」에 수록.',size=9,font='R',absolute=True)
  if n==10:
   block(e,5,'공공디자인 정책과 진흥계획, 현장 문제를 연결해\n시민의 실제 이용을 확인하는 실증 자료를 만듭니다.',size=16,ink=CYAN)
   changes={
    9:'창의디자인 사회실험 추진 · 2026.04\n안전·포용·매력·편의 4개 분야와 8개소 내외의 사업 방향.\n시민·청년작가가 참여하고 우수 모델 확산을 검토한다.',
    10:'인천형 창의디자인 3S · 2026.02\nSustainable · Social · Scalable.\n지속성·사회적 가치·확산 가능성을 현장에서 살핀다.',
    11:'작게 구현하고 실제 이용을 확인\n가역적 설치와 관찰을 통해 설계 조건을 먼저 검토.\n확대 여부는 효과·관리·비용을 함께 판단한다.',
    13:'공공디자인 진흥계획 재정비 추진\n현장 이용 근거와 협업·운영 사례를 후속 검토에 제공.\n특정 연도 반영이나 제도 변경을 확정하지 않는다.',
    14:'사전·1차·2차 비교\n관찰 단위·응답 분모·비교 조건을 먼저 정한다.\n디자인 변경과 날씨·학사·운항 조건을 구분한다.',
    15:'지표별 설계·운영 원칙 정리\n인지·체류·행동과 체감 만족을 함께 기록.\n결과가 다른 경우도 수정 이유와 함께 남긴다.',
    17:'통학로·언덕길·교량 하부\n약산초의 위치 인지, 선인재단의 오름 경험,\n굴포천의 멈춤·휴식이라는 생활 문제를 검토한다.',
    18:'항만 관문·관광 동선·대학 생활권\n터미널의 휴식·짐 정돈, 차이나타운의 정보 전달,\n송도의 머무름·새로운 교류를 확인한다.',
    19:'상업가로의 흡연·보행 혼재\n로데오거리의 공간 이용·꽁초 처리·동선을 비교한다.'}
   for i,t in changes.items():block(e,i,t,size=7.3,ink=GRAY)
   block(e,12,'시민 아이디어를 작은 실험으로 구현하고\n실제 이용으로 판단할 근거가 필요함',size=8.5)
   block(e,16,'계획·설계·관리 검토에 활용할\n현장 실증 자료가 필요함',size=8.5)
   block(e,20,'거점의 생활 조건을 직접 관찰해',size=7.5)
   block(e,21,'지역에 맞는 적용 근거를 확보함',size=7.5)
   block(e,22,'인천의 생활 조건을 살피고, 시민과 실험하며, 후속 설계에 쓸 근거를 남깁니다.',size=10,ink=WHITE)
  if n==11:
   block(e,6,'3S 정책 방향 → 작은 구현·시민 참여·확산 가능성',size=6)
   block(e,8,'재정비·후속 설계에 활용할 현장 근거',size=6)
   block(e,10,'통학·하천·항만·상권의 실제 이용 조건',size=6)
   block(e,11,'인천의 생활 조건에서 실험하고, 결과를 다음 설계와 운영에 연결합니다.',size=10.5,ink=WHITE)
   block(e,24,'송도캠퍼스타운역',size=7)
   block(e,23,'항만 관문',size=5.8)
   block(e,33,'관광 동선',size=5.8)
   e.wipe((181,466,800,488),absolute=True)
   for r,t in [((186,467,285,488),'안내·공간 디자인\n이용 지표와 적용 조건'),((383,467,577,488),'운영 매뉴얼\n설치·청소·조사·유지관리'),((603,467,791,488),'후속 계획 검토\n협업 사례·고정시설 후보')]:e.put(r,t,size=7.3,font='M',absolute=True)
   block(e,38,'3S 정책 방향에 맞춰 실증 자료를 축적하며, 개별 제도 반영·인증·확산 여부는 후속 협의로 결정합니다.',size=7.2)
  if n==12:
   vals={8:'디자인·운영\n보완안',9:'현장 반응과 관리 조건을 정리',10:'설계·시제품 보완에 활용',12:'S T E P   0 3\n조건 검토',13:'고정시설\n후보 검토',14:'효과·관리·비용·기관 협의',15:'적용 가능한 후보를 선정',17:'S T E P   0 4\n연계 검토',18:'매뉴얼·후속\n사업 연계',19:'관계기관 검토에 자료 제공',20:'예산·절차·확산 범위 협의',
    21:'우수 모델의 확산에 쓸 수 있도록, 관찰 결과와 설계·운영 조건을 함께 정리합니다.',
    25:'송도캠퍼스타운역  연수',24:'연안여객터미널  항만',29:'차이나타운  관광',
    30:'휴식·시설 운영안\n좌석·휴식·청소·보행 동선',31:'공공 안내·시각매체\n표식·픽토그램·다국어·매체 선택',32:'공공공간 이용 원칙\n위치 인지·통학·참여디자인',33:'협업·관리 모델\n주체별 역할·운영 비용·유지관리',
    34:'확 산 단 계  ·  실험 결과와 실행 조건 검토 후',35:'군·구 공유\n거점별 적용 조건과 운영 매뉴얼',36:'협업 사례 문서화\n대학·상권·기업의 역할과 운영 조건',37:'성과 공유\n시민 참여 과정·결과·개선 과제 공개',38:'고정시설 구현\n최소 1개소 과업·최종 후보 협의',39:'실증 자료와 운영 원칙을 남기고, 우수 거점의 고정시설 구현은 효과·관리·비용·기관 협의로 결정합니다.'}
   for i,t in vals.items():
    ink=WHITE if i in [17,18,19,20] else None
    size=11 if i in [8,13,18] else (8 if i in [9,10,14,15,19,20,21] else 7)
    block(e,i,t,size=size,ink=ink)
  if n==13:
   block(e,9,'Transformative',size=6.3)
   # Its tiny caption's original font bounds overlap the large T's descender
   # bounds. Restore that fixed brand letter at its exact original baseline.
   e.restore('T',(698.0966796875,281.505615234375),60.13600158691406,'K',WHITE)
   block(e,16,'C - Connect',size=6.5)
   block(e,25,'행정은 현장 협의를 연결하고, 기업·기관은 협의된 자원을 제공함.\n수행기관과 현장 운영자가 실행·기록·관리를 함께 담당함.',size=8.5)
   e.wipe((165,486,379,518),absolute=True)
   e.put((166.7,487.5,378,517),'시민의 제안과 실제 이용을 바탕으로 디자인을 개선하고,\n협업 과정과 운영 조건을 다음 사업에 남김.',size=8.5,font='R',absolute=True)
  if n==14:
   block(e,26,'민간기업 — 협의 대상·역할 검토',size=6.5)
   block(e,9,'민 간 기 업\n세스코 등 협의\n연안여객터미널\n위생·향기 서비스 검토',size=8,ink=GRAY)
   block(e,14,'3M 등 협의\n그래픽 소재·부착 조건 검토',size=8,ink=GRAY)
   block(e,15,'참여 범위·비용 협의',size=7.5)
   block(e,10,'현 장\n학교·현장기관\n약산초·선인재단·송도 참여기관\n모집·운영 협의',size=8)
   block(e,33,'협의로 역할·제공 자원·일정·비용·관리 범위를 확정함.\n참여가 성립하지 않아도 가능한 기본 운영안을 함께 준비함.',size=10)
  if n==15:
   block(e,25,'기본 원칙 01\n날씨·시간·이용 조건을 기록함',size=7.5)
   block(e,26,'강우·온도·학사·운항과 이용 규모를 기록하고,\n계절·현장 조건이 다른 결과는 구분해 해석함.',size=6.7)
   block(e,28,'단기 시행·원상복구가 가능한 규모로 구현하고,\n확대 여부는 실제 이용과 관리 조건을 보고 판단함.',size=6.7)
   block(e,30,'같은 구역·노출·시간대를 맞추고 변경 요소를 기록함.\n불가피하게 조건이 다르면 별도 집계·해석함.',size=6.7)
   block(e,34,'후속 설계·운영 매뉴얼·고정시설 검토 중 활용처를\n정하고, 제도 반영 여부는 관계기관과 협의함.',size=6.7)
   block(e,40,'설치·통행·청소·민원·철거 또는 이관의 담당과\n운영 범위를 현장 관리 주체와 사전 협의함.',size=6.7)
   block(e,47,'2차 실험\n변수 조정과 비교',size=6.8)
  out.append(e.finish())
 return out

def framework():
 e=Editor(EXTRA,2,'대상지별 추진방향');pix=e.page.get_pixmap()
 def patch(rect,text,size=7.6,ink=GRAY,font='M'):
  r=fitz.Rect(rect);px=pix.pixel(int(r.x0+1),int(r.y0+1));fill=''.join(f'{v:02X}' for v in px[:3])
  e.cover(r,fill);e.put(r+(1,1,-1,-1),text,size=size,font=font,ink=ink,absolute=True,align='center',minsize=size*.75)
 # This original page embeds its table as an image. Mask only the text interiors;
 # every border, arrow, circle, color band and table position stays unchanged.
 xs=[114,213,315,414,519,624,723]; widths=[89.5]*7
 problem=['시설이 있어도 어린이가\n위치를 알아보고 설명하는\n데 어려움이 있을 수 있음','매일 올라야 하는 통학로\n부담과 재미·동행 경험을\n함께 살펴볼 필요','달리기·휴식 공간이\n새로운 만남과 교류로\n이어질 조건을 확인','관광 동선에서 필요한\n에티켓·화장실 위치의\n전달 방식 확인','교량 아래에 멈추고\n감상·휴식·활동할\n이유와 자리 확인','흡연 위치·꽁초 처리와\n보행 동선이 섞이는\n공간 이용 문제','출항 대기 중 2층 휴식과\n자가 관리 짐 정돈을\n돕는 안내 확인']
 p1=['시민안 색·상징 표식','발견형 깃대종 그래픽','짧은 코스·기본 휴식','현장 직접 안내','전시·좌석 연출','부스·방향·처리 안내','기둥 방향·짐 정돈']
 p2=['어린이안·장소 반영','나란히 오르는 안내','동일 코스+소통 요소','동일 정보 QR 안내','휴식·활동품 대여','유도 사인 추가','휴식·청결 관리 보완']
 effects=['인지·위치 설명\n표현·장소 다양성','오름 시간·관심 행동\n재미·힘듦·동행','머무름·새로운 교류\n실제 재참여','인지·내용 이해\n호감·정보 접근','체류·행태 다양성\n매력·만족·대여','꽁초 처리·공간 이용\n안쪽 방향·보행 방해','휴식 인원·체류시간\n짐 배치·위생 안심']
 for i,(x,w) in enumerate(zip(xs,widths)):
  patch((x+2,350.3,x+w-2,396),problem[i],7.5)
  patch((x+2,406.7,x+w-2,425.1),p1[i],7.7)
  patch((x+2,430.5,x+w-2,449.3),p2[i],7.7)
  patch((x+2,459.5,x+w-2,487.1),effects[i],7.7)
 # A few lines in the original raster table overflowed into the row gaps.
 # Restore those tiny text fringes from each row's own blank margin color,
 # including the existing horizontal border, without shifting any cell.
 high=e.page.get_pixmap(matrix=__import__('fitz').Matrix(4,4))
 for x,w in zip(xs,widths):
  for ya,yb in [(425.2,430.15),(449.3,454.0)]:
   y=ya
   while y<yb:
    end=min(y+.25,yb);rgb=high.pixel(120*4,int((y+end)/2*4));fill=''.join(f'{v:02X}' for v in rgb[:3])
    e.cover((x+4,y,x+w-4,end),fill);y=end
 patch((315,311,405,323),'캠퍼스타운역',9,font='B')
 patch((585,183,659,203.9),'2차 실험\n변수 조정과 비교',8,ink=WHITE)
 return e.finish()

def map_page():
 e=Editor(EXTRA,3,'거점 대상지 개념도')
 block(e,30,'',size=20)
 # The old oversized editing memo overlapped this fixed map label.
 e.wipe((255,323,296,341),absolute=True)
 e.restore('제물포구',(255.5239,337.230896),11.6573067,'K',f'{9474709:06X}')
 # Keep the original base map, site photos, route and callout shapes.
 labels={6:'5 굴포천',8:'1 약산초등학교',10:'2 선인재단',12:'4 차이나타운',14:'종전 후보지 참고',15:'종전 후보',16:'7 연안여객터미널',17:'4 차이나타운',18:'종전 후보지',19:'2 선인재단',20:'',21:'5 굴포천',23:'7 연안여객터미널',24:'6 구월동로데오거리',26:'3 송도캠퍼스타운',28:'6 구월동로데오거리',29:'3 송도캠퍼스타운'}
 for i,t in labels.items():block(e,i,t,size=9,ink='159ED0')
 cards={
 5:('흐르는 인천','전시·좌석과 대여가 만나는 교량 아래','체류·활동·매력을 함께 확인하다.'),
 7:('키우는 인천','어린이가 알아보고 말하는 우리 길','시민안에 어린이 표현과 장소를 더하다.'),
 9:('함께 오르는 인천','매일의 오름에 발견과 동행을 더하다','재미와 힘듦을 따로 살피다.'),
 11:('친절한 인천','같은 정보를 현장과 QR로 전달하다','인지·내용 이해·호감도를 비교하다.'),
 13:('사업 범위 확인','현재 구체안 7곳 · 최종 범위 협의','부두 사진은 종전 후보 검토 자료.'),
 22:('머무는 인천','안내와 휴식으로 출항 대기를 돕다','짐 정돈·2층 이용·만족을 확인하다.'),
 25:('함께 뛰는 인천','같은 코스에서 새로운 만남을 만들다','머무름·교류·실제 재참여를 살피다.'),
 27:('쾌적한 인천','자리와 처리 안내로 이용을 돕다','꽁초 처리·공간 이용·동선을 보다.')}
 data=json.loads((Path('/tmp/incheon_original_layout')/(EXTRA+'.json')).read_text())[2]
 for i,(head,desc,sub) in cards.items():
  b=fitz.Rect(data['blocks'][i]['bbox']);e.wipe(b+(-.3,-.3,.3,.3),absolute=True)
  e.put((b.x0,b.y0,b.x0+140,b.y0+27),head,size=17.5,font='B',ink=WHITE,absolute=True,minsize=11)
  e.put((b.x0,b.y0+29,b.x0+141,b.y0+42),desc,size=8.5,font='B',ink=WHITE,absolute=True,minsize=6.5)
  e.put((b.x0,b.y0+42,b.x0+141,b.y0+54),sub,size=7.5,font='R',ink='A7DCF0',absolute=True,minsize=6)
 e.put((278,274,577,312),'7개 거점 실험 방향\n기존 후보지 개념도 · 최종 설치 위치는 현장 협의',size=11.5,font='B',ink=BLUE,absolute=True,align='center')
 return e.finish()

def future():
 # These pages originally contain only title placeholders. Keep those title
 # positions, and fill the empty body using the same font/color hierarchy.
 rows=[
  (26,'일정계획','거점별 협의와 제작·조사를 연결하는 실행 일정',[
   ('9월 7~18일 | 실행 조건과 사전조사','설치 범위·관리 주체·학교와 대학 일정·조사 지표를 확정한다.\n관찰 구역과 응답 분모를 고정하고 조사자 예비 관찰을 진행한다.'),
   ('9월 21일~10월 2일 | 제작·점검과 1차 실험','부착·동선·웹 기록을 점검한 뒤 1차를 시행한다.\n약산초는 통학 노출→인지조사→어린이 워크숍의 순서를 지킨다.'),
   ('10월 5~16일 | 2차 실험과 자료 점검','같은 구역·시간대·노출 조건을 맞추고 변경한 요소를 기록한다.\n날씨·학사·운항이 달라지면 비교에서 구분하고 누락을 보완한다.'),
   ('10월 하순~12월 | 분석·공유·고정시설 검토','결과와 제한을 정리하고, 효과·관리·비용을 함께 검토한다.\n최소 1개소 고정시설 과업의 후보·실행 범위·이관 절차를 협의한다.')],
   '제안 일정입니다. 실제 학교·기관 운영일과 행사 일정, 제작·협의 진행에 맞춰 확정합니다.'),
  (27,'인천 디자인 위크','완성 이미지와 함께 시민 참여와 변화의 근거를 공유',[
   ('문제에서 출발한 7개 실험','왜 이 장소에서 실험했는지, 시민이 어떤 불편과 가능성을 발견했는지 보여준다.\n원안→1차 구현→관찰→2차 수정의 흐름을 거점별로 연결한다.'),
   ('결과를 과장하지 않는 전시','지표의 정의·응답 수·분모·기간을 함께 제시한다.\n잘 작동한 점과 예상과 달랐던 점, 관찰 누락과 운영 부담을 같이 설명한다.'),
   ('시민·작가·현장기관의 역할','어린이의 표현과 장소 선택, 작가 협업, 대학·상권·기관의 기여를 기록한다.\n사진·작품·발언은 실제 확보한 자료와 공개 가능한 범위로 구성한다.'),
   ('다음 적용을 위한 공유','거점별 설치·조사·운영 매뉴얼과 고정시설 검토 조건을 제공한다.\n행사 명칭·일정·장소·참여 방식은 주최 측 공지와 협의로 확정한다.')],
   '실측 전에는 기대 효과와 조사계획을, 실측 후에는 확인한 결과와 해석의 범위를 구분해 제시합니다.'),
  (28,'사회실험 최종목표','시민이 실제로 사용한 근거를 다음 설계와 운영에 연결',[
   ('7개 거점의 실행·측정 기록','문제·가설·디자인 버전·관찰 단위·설문·분모·조건 변화를 정리한다.\n인지·체류·행동 변화와 이용자의 체감, 관리 부담을 함께 판단한다.'),
   ('디자인·운영 매뉴얼','색·상징·언어·안내 매체·공간 배치의 적용 원칙을 남긴다.\n설치·청소·대여·반납·자료 기록·철거 또는 이관의 역할을 구체화한다.'),
   ('최소 1개소 고정시설 구현 검토','우수 거점은 효과·보행 영향·내구·관리·비용·기관 협의를 종합 검토한다.\n로데오거리 등 후보를 미리 확정하지 않고 실제 결과와 실행 조건으로 결정한다.'),
   ('후속 사업에서 다시 쓸 수 있는 근거','관계기관의 설계·계획·운영 검토에 현장 자료와 협업 사례를 제공한다.\n인증·제도 반영·예산·확산 일정은 해당 절차와 협의를 거쳐 결정한다.')],
   '원래 과업 범위인 8개소 내외와 현재 구체안 7곳의 차이는 최종 실행 범위로 별도 확정합니다.')]
 out=[]
 for pn,title,lead,parts,foot in rows:
  e=Editor(EXTRA,pn,title)
  b=e.original_lines[0]['bbox'];e.wipe(fitz.Rect(b)+(-1,-1,1,1),absolute=True)
  # Retain the title's x coordinate and use the surrounding blank title area.
  x=b[0];y=b[1]
  e.put((x,y,815,y+38),title,size=25,font='B',ink=CYAN,absolute=True)
  # Original title placeholders sit at mid-page; fill above and below without
  # shifting the original title to a newly invented header position.
  e.put((180,90,813,131),lead,size=16,font='B',ink=BLUE,absolute=True)
  tops=[145,220,375,460]
  for top,(h,t) in zip(tops,parts):
   e.put((180,top,813,top+23),h,size=12.5,font='B',ink=BLUE,absolute=True)
   e.put((180,top+27,813,top+74),t,size=10.5,font='R',absolute=True)
  e.put((180,552,813,580),foot,size=8.7,font='R',ink=GRAY,absolute=True)
  out.append(e.finish())
 return out

def main():
 c=common();f=framework();mp=map_page();chapter=Editor(EXTRA,1,'거점별 세부계획 표지').finish();future_chapter=Editor(EXTRA,25,'향후계획 표지');exact(future_chapter,'인천 디자인 워크','인천 디자인 위크');future_chapter.finish();last=future()
 additions=[chapter,f,mp,future_chapter]+last
 save_pdf(c,ROOT/'03_원본문서별/01_공통사업설명_15쪽_원본양식.pdf');write_pptx(c,ROOT/'03_원본문서별/01_공통사업설명_15쪽_원본양식.pptx')
 save_pdf(additions,ROOT/'03_원본문서별/02_대상지와향후계획_7쪽_원본양식.pdf');write_pptx(additions,ROOT/'03_원본문서별/02_대상지와향후계획_7쪽_원본양식.pptx')
 for i,e in enumerate(c+additions):e.page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(ROOT/'04_수정기록'/f'공통_{i+1:02}_검토.png')
 (ROOT/'04_수정기록/공통변경영역.json').write_text(json.dumps([{'source':e.source,'page':e.pn,'label':e.label,'clear':e.clear,'text':e.text,'covers':[(list(r),fill) for r,fill in e.covers]} for e in c+additions],ensure_ascii=False,indent=2))
 return c,additions
if __name__=='__main__':main()
