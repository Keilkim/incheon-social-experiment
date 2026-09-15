# -*- coding: utf-8 -*-
from pathlib import Path
import json,io,copy
import fitz
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN
from 원본양식수정 import ROOT,FONTS,FF,color

BASES={
 'common':ROOT/'03_원본문서별/01_공통사업설명_15쪽_원본양식',
 'extra':ROOT/'03_원본문서별/02_대상지와향후계획_7쪽_원본양식',
 'sites':ROOT/'02_통합/01_7개거점_21쪽_원본양식'}
PDF={k:fitz.open(p.with_suffix('.pdf')) for k,p in BASES.items()}
PPT={k:Presentation(p.with_suffix('.pptx')) for k,p in BASES.items()}
R=json.loads((ROOT/'04_수정기록/변경영역.json').read_text());C=json.loads((ROOT/'04_수정기록/공통변경영역.json').read_text())
REC={'common':C[:15],'extra':C[15:],'sites':R}

def part(key,nums):return [(key,i) for i in nums]
def merge(order,path,toc=None):
 print('MERGE',path.name,flush=True)
 doc=fitz.open();prs=Presentation();prs.slide_width=Pt(853.228);prs.slide_height=Pt(606.614);records=[]
 for ix,(key,pn) in enumerate(order,1):
  doc.insert_pdf(PDF[key],from_page=pn,to_page=pn);page=doc[-1];rec=copy.deepcopy(REC[key][pn]);rec['final_page']=ix
  hasnum=any(t.get('role')=='page_number' for t in rec['text'])
  if hasnum:
   off=(page.rect.width-841.8900146484375)/2
   page.add_redact_annot(fitz.Rect(805+off,557+off,829+off,578+off),fill=False,cross_out=False);page.apply_redactions(images=0,graphics=0,text=0)
   page.insert_font(fontname='FinalPageNo',fontfile=str(FONTS['M']))
   font=FF['M'];fs=8.4;w=font.text_length(str(ix),fontsize=fs);x=806.6+off+(12.4-w)/2;y=560.5+off+font.ascender*fs
   page.insert_text((x,y),str(ix),fontname='FinalPageNo',fontsize=fs,color=color('818587'))
   for t in rec['text']:
    if t.get('role')=='page_number':
     t['text']=str(ix);t['placed']=[{'text':str(ix),'x':x,'baseline':y,'width':w}]
  records.append(rec)
  original=PPT[key].slides[pn];slide=prs.slides.add_slide(prs.slide_layouts[6])
  for sh in original.shapes:
   if sh.shape_type==13:
    new=slide.shapes.add_picture(io.BytesIO(sh.image.blob),sh.left,sh.top,width=sh.width,height=sh.height)
   else:
    el=copy.deepcopy(sh.element);slide.shapes._spTree.insert_element_before(el,'p:extLst')
  for sh in slide.shapes:
   if sh.name=='page_number':
    p=sh.text_frame.paragraphs[0];p.runs[0].text=str(ix);p.alignment=PP_ALIGN.CENTER
    sh.left=Pt(812.269);sh.width=Pt(12.4)
  slide.notes_slide.notes_text_frame.text=original.notes_slide.notes_text_frame.text
 doc.set_metadata({'title':path.stem,'author':'위즈플러스','subject':'원본 PDF의 양식·이미지·위치를 유지한 글 수정본 · 2026.09.07'})
 if toc:doc.set_toc(toc)
 doc.subset_fonts();doc.save(path.with_suffix('.pdf'),garbage=4,deflate=True);doc.close();prs.save(path.with_suffix('.pptx'))
 return records

def main():
 sites=part('sites',range(21));front=part('extra',[0,1,2]);back=part('extra',[3,4,5,6])
 records=merge(part('common',range(15))+front+sites+back,ROOT/'02_통합/00_국장보고_전체43쪽_원본양식',[
 [1,'Ⅰ 개요·사회실험',1],[1,'Ⅱ 사업 방향',9],[1,'Ⅲ 거점별 세부계획',16],
 [2,'약산초등학교',19],[2,'선인재단',22],[2,'송도캠퍼스타운역',25],[2,'차이나타운',28],[2,'굴포천',31],[2,'구월동로데오거리',34],[2,'연안여객터미널',37],[1,'Ⅳ 향후계획',40]])
 (ROOT/'04_수정기록/통합43쪽_변경영역.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 merge(front+sites+back,ROOT/'03_원본문서별/03_거점별세부계획과향후계획_원본구성28쪽')
 merge(front+part('sites',range(0,3))+part('sites',range(9,12))+part('sites',range(12,15)),ROOT/'03_원본문서별/04_약산초_차이나타운_굴포천_원본구성12쪽')
 merge(part('sites',range(18,21))+part('sites',range(6,9)),ROOT/'03_원본문서별/05_연안여객터미널_송도_원본구성6쪽')
 return records
if __name__=='__main__':main()
