"""Overwrite only Seonin page/slide 2; retain six original pages/slides."""
from pathlib import Path
import hashlib
import json
import zipfile
from pypdf import PdfReader, PdfWriter
from pptx import Presentation
import fitz

BASE=Path(__file__).resolve().parent
OUT=BASE.parent
TEMP=Path('/tmp/seonin_diagram_revise/generated')
BACKUP=BASE/'수정전_20261110_선인재단_다이어그램'
PDFNAME='인천시_7개실험실_수집분석_다이어그램_A4.pdf'
PPTNAME='인천시_7개실험실_수집분석_다이어그램_A4_편집용.pptx'
dest_pdf=OUT/PDFNAME
dest_ppt=OUT/PPTNAME

old=PdfReader(dest_pdf)
new=PdfReader(TEMP/PDFNAME)
assert len(old.pages)==len(new.pages)==7
assert '형성평가' in new.pages[1].extract_text()
writer=PdfWriter()
for i,page in enumerate(old.pages):
    writer.add_page(new.pages[1] if i==1 else page)
if old.metadata:
    writer.add_metadata({k:str(v) for k,v in old.metadata.items() if v is not None})
pdf_temp=dest_pdf.with_suffix('.tmp.pdf')
with pdf_temp.open('wb') as f:
    writer.write(f)

# The generated slide has vector/text objects and three external DOI links.
with zipfile.ZipFile(dest_ppt) as z:
    original={i.filename:(i,z.read(i.filename)) for i in z.infolist()}
with zipfile.ZipFile(TEMP/PPTNAME) as z:
    replacement={name:z.read(name) for name in [
        'ppt/slides/slide2.xml','ppt/slides/_rels/slide2.xml.rels']}
assert b'/image' not in replacement['ppt/slides/_rels/slide2.xml.rels']
ppt_temp=dest_ppt.with_suffix('.tmp.pptx')
with zipfile.ZipFile(ppt_temp,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for name,(info,data) in original.items():
        z.writestr(info,replacement.get(name,data))

# Validate the replacements before the requested overwrite.
before=fitz.open(BACKUP/PDFNAME)
after=fitz.open(pdf_temp)
assert len(after)==7
unchanged=[]
for i in range(7):
    if i==1: continue
    assert before[i].get_text()==after[i].get_text(),('other page text changed',i+1)
    a=before[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
    b=after[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
    assert (a.width,a.height,a.samples)==(b.width,b.height,b.samples),('other page pixels changed',i+1)
    unchanged.append(i+1)
with zipfile.ZipFile(BACKUP/PPTNAME) as z0,zipfile.ZipFile(ppt_temp) as z1:
    assert z1.testzip() is None
    for name in z0.namelist():
        if name not in replacement:
            assert z0.read(name)==z1.read(name),('other PPTX part changed',name)
prs=Presentation(ppt_temp)
assert len(prs.slides)==7
page=after[1].get_text()
slide='\n'.join(s.text for s in prs.slides[1].shapes if s.has_text_frame)
for term in ['형성평가','5문항','6문항','접근·시선·멈춤·체류','통합표','Lundy','Moore','Fetters','무변화','회고 응답','인과효과 검정 제외']:
    assert term in page,term
    assert term in slide,term
for term in ['자기수용감','색·문구·높이에 반영','대조군: 1차']:
    assert term not in page,term
links=after[1].get_links()
assert len(links)==3
assert all(link['uri'].startswith('https://doi.org/') for link in links)
used_fonts={span['font'] for block in after[1].get_text('dict')['blocks']
            for line in block.get('lines',[]) for span in line['spans']}
for font in after[1].get_fonts():
    # ReportLab declares an unused Helvetica resource on every new canvas.
    if font[3].split('+')[-1] in used_fonts:
        assert after.extract_font(font[0])[3],('unembedded font',font)
for block in after[1].get_text('dict')['blocks']:
    for line in block.get('lines',[]):
        for span in line['spans']:
            x0,y0,x1,y1=span['bbox']
            assert 0<=x0<x1<=after[1].rect.width and 0<=y0<y1<=after[1].rect.height,span

preview_dir=BASE/'시각검토'/'선인재단_다이어그램_20261110'
preview_dir.mkdir(parents=True,exist_ok=True)
after[1].get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(preview_dir/'02.png')
after.close();before.close()
pdf_temp.replace(dest_pdf)
ppt_temp.replace(dest_ppt)
record={
    'changed_pdf_page':2,'changed_pptx_slide':2,
    'unchanged_pdf_pages_text_and_pixels':unchanged,
    'all_other_pptx_zip_parts_identical':True,
    'page_count':7,'slide_count':7,'source_hyperlinks':3,
    'pdf_sha256':hashlib.sha256(dest_pdf.read_bytes()).hexdigest(),
    'pptx_sha256':hashlib.sha256(dest_ppt.read_bytes()).hexdigest(),
}
(preview_dir/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('Overwritten:',dest_pdf)
print('Editable PPTX updated:',dest_ppt)
print('Unchanged PDF pages and PPTX slides:',unchanged)
print('Verified: source links, embedded fonts, text bounds, editable text and ZIP structure.')
