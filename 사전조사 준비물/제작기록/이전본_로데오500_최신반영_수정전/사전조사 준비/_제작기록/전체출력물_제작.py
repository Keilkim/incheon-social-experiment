"""A4 기록지·설문·안내와 A3 보드를 함께 준비하는 출력 목록."""
from pathlib import Path
from html import escape
import sys, shutil, json
from pypdf import PdfReader, PdfWriter
sys.path.insert(0,str(Path(__file__).parent))
import docx_공통 as W
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'사전조사 준비물/제작기록'))
import 도구_공통 as C
import 조사지_제작 as M
FINAL=BASE/'최종_현장조사'
SOURCE=FINAL if FINAL.exists() else BASE
OUT=BASE/'사전조사 준비'
PHASES=['사전조사 준비물','1차 실험','2차 실험']
MANIFEST=[]


def extract(src,dest,indices=None):
    reader=PdfReader(src);indices=list(range(len(reader.pages))) if indices is None else list(indices)
    writer=PdfWriter()
    for i in indices:
        p=reader.pages[i]
        dims=sorted([float(p.mediabox.width)*25.4/72,float(p.mediabox.height)*25.4/72])
        assert abs(dims[0]-210)<0.5 and abs(dims[1]-297)<0.5,(src,i,dims)
        writer.add_page(p)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('wb') as f:writer.write(f)
    return len(indices)


def make_phase(phase):
    folder=PHASES[phase];src=SOURCE/folder;dest=OUT/'A4_출력파일'/folder
    records=[];items=[]
    def add(name,source,pages=None,copies=1,duplex=False,note='',record=False):
        file=dest/(name+'.pdf');n=extract(source,file,pages)
        item={'파일':file.name,'쪽수':n,'부수':copies,'방식':'양면' if duplex else '단면','장수':((n+1)//2 if duplex else n)*copies,'내용':note,'경로':str(file.relative_to(OUT))}
        items.append(item)
        if record:records.append(file)
    if phase==0:add('01_시간표와_준비물',src/'00_시간표와_준비물.pdf',note='조사팀 공유용')
    add('02_조사한눈에',src/('00_조사한눈에.pdf' if phase==0 else '00_한눈에.pdf'),note='A4 가로 · 전체 내용 확인')
    add('03_조사원수칙',SOURCE/'사전조사 준비물/00_조사원수칙.pdf',copies=5,note='조사자용 · 최대 5명 기준')
    add('04_표정과_인쇄안내',SOURCE/'사전조사 준비물/00_표정과_200건_인쇄안내.pdf',note='표정·수량 확인용')
    add('05_선인재단_매칭안내',src/'02_선인재단_매칭안내.pdf',copies=4,note='위치 담당자 4명에게 1부씩')
    add('06_약산초_지도와설문',src/'01_약산초등학교.pdf',range(2),copies=200,duplex=True,note='지도+설문 2쪽을 200부 · 긴 쪽 넘김')
    if phase==1:add('07_약산초_워크숍기록',src/'01_약산초등학교.pdf',range(2,10),note='001~200 · 25줄×8장',record=True)
    add('08_선인재단_기록지',src/'02_선인재단.pdf',note='위치별 8장×4곳 · 200명',record=True)
    add('09_송도_관찰기록지',src/'03_송도.pdf',range(8),note='001~200 · 관찰 200건',record=True)
    add('10_송도_인터뷰기록표',src/'03_송도.pdf',range(8,10),note='001~050 · 인터뷰 50명',record=True)
    if len(PdfReader(src/'03_송도.pdf').pages)>10:add('11_송도_모집폼문항',src/'03_송도.pdf',[10],note='폼 작성·안내용')
    add('12_굴포천_기록지',src/'05_굴포천.pdf',note='001~200 · 관찰 200건',record=True)
    add('13_로데오거리_기록지',src/'06_로데오거리.pdf',note='001~200 · 200명',record=True)
    add('14_터미널_2층기록지',src/'07_연안여객터미널.pdf',range(8),note='001~200 · 200명',record=True)
    add('15_터미널_캐리어시간표',src/'07_연안여객터미널.pdf',[8],note='12:00~16:00 · 15분 간격',record=True)
    if phase==2:add('16_차이나타운_웹집계',src/'04_차이나타운_웹기록.pdf',note='14일 집계표',record=True)
    writer=PdfWriter()
    for path in records:
        for page in PdfReader(path).pages:writer.add_page(page)
    n=len(writer.pages);bundle=dest/f'00_현장기록지_일괄_{n}장_단면1부.pdf'
    with bundle.open('wb') as f:writer.write(f)
    lines=[f'# {folder} · A4 출력', '', f'현장 기록지는 **{bundle.name} 전체를 단면 1부** 출력하면 됩니다. 일괄 파일은 아래 개별 기록지를 모은 파일입니다. 두 방식을 중복 출력하지 않습니다.', '', '**약산초 지도+설문은 별도로 양면 200부**입니다. 안내문·수칙·모집폼은 아래 부수를 따릅니다.', '', '| 파일 | 쪽 | 부수 | 방식 | 실제 종이 | 내용 |','| --- | ---: | ---: | --- | ---: | --- |']
    for x in items:lines.append(f'| [{x["파일"]}]({x["파일"]}) | {x["쪽수"]} | {x["부수"]} | {x["방식"]} | {x["장수"]}장 | {x["내용"]} |')
    lines.extend(['','A4 실제 크기(100%), 자동 방향으로 출력합니다. 약산초 지도·사진의 빈 프레임은 현장 원본을 넣어 사용합니다.'])
    (dest/'00_출력방법.md').write_text('\n'.join(lines)+'\n')
    info={'회차':folder,'일괄파일':bundle.name,'일괄장수':n,'항목':items};MANIFEST.append(info)
    return info


def make_boards():
    output=OUT/'보드_출력파일';output.mkdir(exist_ok=True)
    for source,name in [('05_굴포천_폼보드.pdf','B1_굴포천_스티커판_사전_A3.pdf'),('04_차이나타운_폼보드.pdf','B4_차이나타운_스티커보드_A3.pdf')]:
        shutil.copy2(SOURCE/'사전조사 준비물'/source,output/name)
    items=[]
    for folder in PHASES:
        for f in sorted((SOURCE/folder).glob('*_폼보드.pdf')):
            p=PdfReader(f).pages[0];landscape=float(p.mediabox.width)>float(p.mediabox.height)
            items.append((folder,f.name,'A3 가로' if landscape else 'A3 세로','1쪽 × 1부','폼보드 1판 · 교체용 출력지는 필요 시 추가'))
    return items


def build():
    infos=[make_phase(p) for p in range(3)];boards=make_boards()
    d=W.new(header='A4·A3 전체 출력물 목록 · 2026.09.13');html=[]
    for i,info in enumerate(infos):
        if i:W.page_break(d)
        title=info['회차']+' · A4 출력물'
        note=f'현장 기록지 일괄 {info["일괄장수"]}장: 단면 1부. 약산초 지도+설문: 별도 양면 200부.'
        W.title(d,title,note)
        W.para(d,'일괄 PDF는 개별 기록지를 모은 파일입니다. 일괄 또는 개별 중 한 방식으로 출력합니다. 안내문은 아래 수량을 따릅니다.',9,W.MUTED)
        rows=[['파일','출력 설정','실제 종이','내용']]+[[x['파일'],f'{x["쪽수"]}쪽 × {x["부수"]}부\n{x["방식"]}',f'{x["장수"]}장',x['내용']] for x in info['항목']]
        W.table(d,rows,[6.5,3,1.6,6.3],size=8.3,center_cols=(1,2))
        W.para(d,'파일 위치: A4_출력파일 / '+info['회차'],9,W.MUTED)
        body=M.hd('출력목록',title,'A4 실제 크기 · 자동 방향')+f'<div class="how">{escape(note)}</div><p class="tip">일괄 또는 개별 중 한 방식으로 출력합니다. 안내문은 아래 수량을 따릅니다.</p>'
        body+='<table><colgroup><col style="width:36%"><col style="width:18%"><col style="width:10%"><col></colgroup><thead><tr>'+''.join(f'<th>{x}</th>' for x in rows[0])+'</tr></thead><tbody>'
        body+=''.join('<tr>'+''.join(f'<td>{escape(c).replace(chr(10),"<br>")}</td>' for c in row)+'</tr>' for row in rows[1:])+'</tbody></table>'
        body+=f'<div class="note">파일 위치: A4_출력파일 / {info["회차"]}<br>일괄 파일: {info["일괄파일"]}</div>'
        html.append(body)
    W.page_break(d);W.title(d,'A3 폼보드 · 출력물','사람이 들고 이동 · 굴포천·터미널 세로 / 차이나타운 가로')
    b_rows=[['회차','파일','규격','출력']]+[[a,b,c,e] for a,b,c,e,n in boards]
    W.table(d,b_rows,[3.1,7.6,3.1,3.6],size=8.8)
    notes=['A3 실제 크기(100%)로 출력해 같은 크기의 폼보드에 붙입니다.',
           '응답칸이 차면 사진·집계 후 같은 A3 출력지를 덧붙여 계속 사용합니다.',
           '굴포천: 스티커 800개. 차이나타운: 800개+여분 200개. 터미널 1·2차: 400개.',
           '차이나타운 그림 A·B, 약산초 지도·사진은 실제 현장 자료를 넣습니다.',
           '핸드폰으로 시간을 확인합니다. 송도는 구매한 A4 받침대를 사용합니다. 굴포천은 카메라 1대·삼각대 1개를 준비합니다.']
    W.bullets(d,notes,9.5)
    body=M.hd('출력목록','A3 폼보드','실제 크기 100%')+'<div class="how">폼보드는 사람이 들고 이동합니다.</div>'
    body+='<table><thead><tr>'+''.join(f'<th>{x}</th>' for x in b_rows[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{escape(c)}</td>' for c in row)+'</tr>' for row in b_rows[1:])+'</tbody></table>'
    body+='<div class="legend">'+'<br>'.join(escape(n) for n in notes)+'</div>';html.append(body)
    name='04_전체 출력물 목록'
    d.save(OUT/(name+'.docx'))
    C.render(html,OUT/(name+'.pdf'),extra_css=M.CSS+'td{padding:6px 5px;font-size:8.4pt;vertical-align:middle}th{font-size:8.5pt}.tip{margin-bottom:7px}',footer='A4·A3 전체 출력물 목록')
    (OUT/'A4_출력파일/출력목록.json').write_text(json.dumps(MANIFEST,ensure_ascii=False,indent=2))
    if FINAL.exists():
        prep=FINAL/'사전조사 준비'
        shutil.copytree(OUT/'A4_출력파일',prep/'A4_출력파일',dirs_exist_ok=True)
        for suffix in ['.pdf','.docx']:shutil.copy2(OUT/(name+suffix),prep/(name+suffix))
    print('A4 출력물 3개 회차, 현장기록 일괄 67·75·68장, A4·A3 전체 목록 생성 완료')

if __name__=='__main__':build()
