from pathlib import Path
import re, json, copy, zipfile, unicodedata, math, html, io
from lxml import etree as E
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_LEFT
import fitz
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parent
FONTS=Path('/Users/chokogamja/Library/Fonts')
pdfmetrics.registerFont(TTFont('Paper',str(FONTS/'Paperlogy-4Regular.ttf')))
pdfmetrics.registerFont(TTFont('PaperBold',str(FONTS/'Paperlogy-7Bold.ttf')))
pdfmetrics.registerFontFamily('Paper',normal='Paper',bold='PaperBold',italic='Paper',boldItalic='PaperBold')
FONT='페이퍼로지 4 Regular'; BOLD='페이퍼로지 7 Bold'
BLUE='#153C68'; TEAL='#009DAF'; GRAY='#536274'
TEMPLATE=next(p for p in WORK.glob('*.hwpx') if '약산' in unicodedata.normalize('NFC',p.name))

def plain(s):
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:m[1]+' ('+m[2]+')',s)
 return s.replace('**','').replace('`','')

def blocks(md):
 lines=md.splitlines();out=[];i=0
 while i<len(lines):
  s=lines[i].strip()
  if not s: i+=1;continue
  if s.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    row=[x.strip() for x in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch(r':?-+:?',x.replace(' ','')) for x in row):rows.append(row)
    i+=1
   out.append(('table',rows));continue
  m=re.match(r'^(#{1,3}) (.+)',s)
  if m:out.append(('h'+str(len(m[1])),m[2]));i+=1;continue
  par=[s];i+=1
  while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|')):
   par.append(lines[i].strip());i+=1
  out.append(('p','\n'.join(par)))
 return out

def pdf_html(s):
 parts=[];at=0
 for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)',s):
  parts.append(html.escape(s[at:m.start()]));parts.append('<link color="#007C91" href="'+html.escape(m[2],quote=True)+'">'+html.escape(m[1])+'</link>');at=m.end()
 parts.append(html.escape(s[at:]));return ''.join(parts).replace('\n','<br/>').replace('**','')

def write_pdf(md,path):
 styles={
 'p':ParagraphStyle('p',fontName='Paper',fontSize=10.2,leading=17,spaceAfter=9,wordWrap='CJK',textColor=colors.HexColor('#233144')),
 'h1':ParagraphStyle('h1',fontName='PaperBold',fontSize=21,leading=29,spaceAfter=16,textColor=colors.HexColor(BLUE),wordWrap='CJK',keepWithNext=True),
 'h2':ParagraphStyle('h2',fontName='PaperBold',fontSize=13,leading=20,spaceBefore=13,spaceAfter=7,textColor=colors.HexColor(BLUE),wordWrap='CJK',keepWithNext=True),
 'h3':ParagraphStyle('h3',fontName='PaperBold',fontSize=10.8,leading=17,spaceBefore=8,spaceAfter=5,textColor=colors.HexColor(TEAL),wordWrap='CJK',keepWithNext=True),
 'cell':ParagraphStyle('cell',fontName='Paper',fontSize=8.3,leading=12.5,wordWrap='CJK'),
 }
 story=[]
 for kind,value in blocks(md):
  if kind=='table':
   n=max(len(r) for r in value);rows=[[Paragraph(pdf_html(x),styles['cell']) for x in row]+['']*(n-len(row)) for row in value]
   table=Table(rows,colWidths=[483/n]*n,repeatRows=1,hAlign='LEFT')
   table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E4F1F5')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#CDD9E2')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
   story += [table,Spacer(1,10)]
  else:story.append(Paragraph(pdf_html(value),styles[kind]))
 title=next(v for k,v in blocks(md) if k=='h1')
 def page(c,d):
  c.setTitle(title);c.setAuthor('위즈플러스');c.setFont('Paper',7.2);c.setFillColor(colors.HexColor(GRAY));c.drawString(56,816,'ACT Incheon  |  2026.09.07 회의 반영 작성안');c.setStrokeColor(colors.HexColor('#DDE5ED'));c.line(56,808,539,808);c.drawString(56,30,'인천 창의디자인 사회실험');c.drawRightString(539,30,str(d.page))
 SimpleDocTemplate(str(path),pagesize=(595.28,841.89),leftMargin=56,rightMargin=56,topMargin=52,bottomMargin=52,title=title,author='위즈플러스').build(story,onFirstPage=page,onLaterPages=page)

def setrun(run,font=FONT,size=10.5,bold=False):
 run.font.name=font;run.font.size=Pt(size);run.font.bold=bold
 rp=run._element.get_or_add_rPr();f=rp.rFonts
 if f is None:f=OxmlElement('w:rFonts');rp.insert(0,f)
 for k in ['eastAsia','ascii','hAnsi','cs']:f.set(qn('w:'+k),font)

def add_docx_text(p,s):
 at=0
 for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)',s):
  if m.start()>at:setrun(p.add_run(s[at:m.start()]))
  rel=p.part.relate_to(m[2],'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
  a=OxmlElement('w:hyperlink');a.set(qn('r:id'),rel);r=OxmlElement('w:r');rp=OxmlElement('w:rPr');f=OxmlElement('w:rFonts');f.set(qn('w:eastAsia'),FONT);f.set(qn('w:ascii'),FONT);rp.append(f);co=OxmlElement('w:color');co.set(qn('w:val'),'007C91');rp.append(co);r.append(rp);t=OxmlElement('w:t');t.text=m[1];r.append(t);a.append(r);p._p.append(a);at=m.end()
 if at<len(s):setrun(p.add_run(s[at:]))

def write_docx(md,path):
 doc=Document();sec=doc.sections[0];sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=Cm(1.9);sec.bottom_margin=Cm(1.9);sec.left_margin=Cm(2);sec.right_margin=Cm(2)
 for name in ['Normal','Title','Heading 1','Heading 2']:
  st=doc.styles[name];st.font.name=FONT;st.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),FONT)
 normal=doc.styles['Normal'];normal.font.size=Pt(10.5);normal.paragraph_format.line_spacing=1.5;normal.paragraph_format.space_after=Pt(7)
 for kind,value in blocks(md):
  if kind=='table':
   table=doc.add_table(rows=0,cols=max(len(r) for r in value));table.style='Light Shading Accent 1'
   for ri,row in enumerate(value):
    cells=table.add_row().cells
    for i,t in enumerate(row):
     add_docx_text(cells[i].paragraphs[0],t)
     for r in cells[i].paragraphs[0].runs:setrun(r,size=9,bold=ri==0)
   doc.add_paragraph();continue
  p=doc.add_paragraph()
  if kind.startswith('h'):
   p.style={'h1':'Title','h2':'Heading 1','h3':'Heading 2'}[kind]
   r=p.add_run(value);setrun(r,BOLD,{'h1':22,'h2':14,'h3':11}[kind],True);r.font.color.rgb=RGBColor.from_string('153C68');p.paragraph_format.keep_with_next=True
  else:add_docx_text(p,value)
 head=sec.header.paragraphs[0];setrun(head.add_run('ACT Incheon  |  2026.09.07 회의 반영 작성안'),size=8)
 foot=sec.footer.paragraphs[0];setrun(foot.add_run('인천 창의디자인 사회실험  ·  '),size=8)
 field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');foot._p.append(field)
 doc.core_properties.title=next(v for k,v in blocks(md) if k=='h1');doc.core_properties.author='위즈플러스';doc.core_properties.subject='2026.09.07 회의 반영 작성안';doc.save(path)

def write_hwpx(md,path,pdfpath=None):
 with zipfile.ZipFile(TEMPLATE) as z:files={n:z.read(n) for n in z.namelist()}
 header=E.fromstring(files['Contents/header.xml']);ns=header.nsmap
 cp=header.find('.//hh:charProperties',ns);base=copy.deepcopy(cp[0]);cid={}
 for k,size,color in [('p',1050,'#233144'),('h1',2200,BLUE),('h2',1400,BLUE),('h3',1100,TEAL)]:
  el=copy.deepcopy(base);idx=max(int(x.get('id')) for x in cp)+1;el.set('id',str(idx));el.set('height',str(size));el.set('textColor',color)
  for a in el.find('hh:fontRef',ns).attrib:el.find('hh:fontRef',ns).set(a,'0' if k!='p' else '2')
  cp.append(el);cid[k]=str(idx)
 cp.set('itemCnt',str(len(cp)))
 for f in header.findall('.//hh:font',ns):f.set('face',BOLD if f.get('id')=='0' else FONT)
 pp=header.find('.//hh:paraProperties',ns);pbase=copy.deepcopy(pp[0]);pid={}
 for k in ['p','h1','h2','h3']:
  el=copy.deepcopy(pbase);idx=max(int(x.get('id')) for x in pp)+1;el.set('id',str(idx));el.find('hh:align',ns).set('horizontal','LEFT')
  bs=el.find('hh:breakSetting',ns);bs.set('breakNonLatinWord','BREAK_WORD');bs.set('widowOrphan','1');bs.set('keepWithNext','0' if k=='p' else '1')
  for x in el.findall('.//hh:lineSpacing',ns):x.set('value','165')
  for x in el.findall('.//hc:prev',ns):x.set('value','700' if k in ['h2','h3'] else '0')
  for x in el.findall('.//hc:next',ns):x.set('value','550' if k=='p' else '700')
  pp.append(el);pid[k]=str(idx)
 pp.set('itemCnt',str(len(pp)))
 oldsec=E.fromstring(files['Contents/section0.xml']);secpr=copy.deepcopy(oldsec.find('.//hp:secPr',ns));page=secpr.find('hp:pagePr',ns);page.set('width','59528');page.set('height','84189');page.set('landscape','WIDELY')
 margin=page.find('hp:margin',ns)
 for key,val in dict(left=5669,right=5669,top=5669,bottom=5669,header=1417,footer=1417,gutter=0).items():margin.set(key,str(val))
 newsec=E.Element(oldsec.tag,nsmap=oldsec.nsmap);pars=[]
 for kind,v in blocks(md):
  if kind=='table':
   heads=v[0]
   for row in v[1:]:pars.append(('p',' / '.join(h+': '+plain(t) for h,t in zip(heads,row))))
  else:pars.append((kind,plain(v)))
 for i,(kind,txt) in enumerate(pars):
  p=E.SubElement(newsec,'{'+ns['hp']+'}p',id=str(i),paraPrIDRef=pid[kind],styleIDRef='0',pageBreak='0',columnBreak='0',merged='0')
  r=E.SubElement(p,'{'+ns['hp']+'}run',charPrIDRef=cid[kind])
  if i==0:
   r.append(secpr);ctrl=E.SubElement(r,'{'+ns['hp']+'}ctrl');E.SubElement(ctrl,'{'+ns['hp']+'}colPr',id='',type='NEWSPAPER',layout='LEFT',colCount='1',sameSz='1',sameGap='0')
  t=E.SubElement(r,'{'+ns['hp']+'}t');t.text=txt
 title=next(v for k,v in blocks(md) if k=='h1')
 opf=E.fromstring(files['Contents/content.hpf']);opfn={'opf':'http://www.idpf.org/2007/opf/'}
 opf.find('.//opf:title',opfn).text=title
 for meta in opf.findall('.//opf:meta',opfn):
  if meta.get('name') in ['creator','lastsaveby']:meta.text='위즈플러스'
  elif meta.get('name') in ['CreatedDate','ModifiedDate']:meta.text='2026-09-07T00:00:00Z'
  elif meta.get('name')=='date':meta.text='2026년 9월 7일'
  else:meta.text=''
 settings=E.fromstring(files['settings.xml'])
 for pos in settings:
  if E.QName(pos).localname=='CaretPosition':pos.attrib.update({'listIDRef':'0','paraIDRef':'0','pos':'0'})
 for n,el in [('Contents/header.xml',header),('Contents/section0.xml',newsec),('Contents/content.hpf',opf),('settings.xml',settings)]:files[n]=E.tostring(el,encoding='UTF-8',xml_declaration=True,standalone=True)
 files['Preview/PrvText.txt']='\n'.join(t for k,t in pars).encode('utf-8')
 if pdfpath and pdfpath.exists():
  d=fitz.open(pdfpath);pix=d[0].get_pixmap(matrix=fitz.Matrix(0.25,0.25));files['Preview/PrvImage.png']=pix.tobytes('png');d.close()
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('mimetype',files.pop('mimetype'),compress_type=zipfile.ZIP_STORED)
  for n,b in files.items():z.writestr(n,b)

def output_for(p):
 if '_아이디어정교화' in p.name:return ROOT/'01_아이디어정교화'/p.stem
 if p.name.startswith('20_') or p.name.startswith('21_'):return ROOT/'03_분석과조사설계'/p.stem
 if p.name.startswith('10_'):return ROOT/'02_국장보고'/'00_발표설명포함_통합전체원고'
 if p.name.startswith('11_'):return ROOT/'02_국장보고'/'거점별'/p.stem[3:]
 raise ValueError(p)

if __name__=='__main__':
 manifest=[]
 for p in sorted((ROOT/'04_편집원고').glob('*.md')):
  if p.name.startswith('00_'):continue
  base=output_for(p);base.parent.mkdir(parents=True,exist_ok=True);md=p.read_text()
  write_pdf(md,base.with_suffix('.pdf'));write_docx(md,base.with_suffix('.docx'));write_hwpx(md,base.with_suffix('.hwpx'),base.with_suffix('.pdf'))
  d=fitz.open(base.with_suffix('.pdf'));manifest.append({'source':p.name,'chars':len(md),'pdf_pages':len(d),'output':str(base.relative_to(ROOT))});d.close()
 (ROOT/'05_제작기록'/'문서생성목록.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(json.dumps(manifest,ensure_ascii=False,indent=2))
