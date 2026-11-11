"""Replace only Seonin page/slide 2 and verify all six other pages unchanged."""
from pathlib import Path
import csv
import hashlib
import json
import posixpath
import zipfile
from lxml import etree
from pypdf import PdfReader, PdfWriter
from pptx import Presentation
import fitz

BASE=Path(__file__).resolve().parent
OUT=BASE.parent
TEMP=Path('/tmp/seonin_visual_rebuild')
BACKUP=BASE/'수정전_20261110_선인재단'
PDFNAME='인천시_7개실험실_수집분석_시각화_A4.pdf'
PPTNAME='인천시_7개실험실_수집분석_시각화_A4_편집용.pptx'
dest_pdf=OUT/PDFNAME
dest_ppt=OUT/PPTNAME

# Preserve the six original PDF page objects instead of exporting them again.
old=PdfReader(dest_pdf)
new=PdfReader(TEMP/PDFNAME)
assert len(old.pages)==len(new.pages)==7
assert '6문항' in new.pages[1].extract_text()
writer=PdfWriter()
for i,page in enumerate(old.pages):writer.add_page(new.pages[1] if i==1 else page)
if old.metadata:writer.add_metadata({k:str(v) for k,v in old.metadata.items() if v is not None})
tmp=dest_pdf.with_suffix('.tmp.pdf')
with tmp.open('wb') as f:writer.write(f)
tmp.replace(dest_pdf)

# Preserve every original slide XML; replace only slide 2 and its image rels.
with zipfile.ZipFile(dest_ppt) as z:original={i.filename:(i,z.read(i.filename)) for i in z.infolist()}
with zipfile.ZipFile(TEMP/PPTNAME) as z:
    slide=z.read('ppt/slides/slide2.xml')
    rels=etree.fromstring(z.read('ppt/slides/_rels/slide2.xml.rels'))
    extras={}
    for rel in rels:
        if rel.get('Type','').endswith('/image'):
            source=posixpath.normpath(posixpath.join('ppt/slides',rel.get('Target')))
            suffix=Path(source).suffix
            target=f'ppt/media/seonin_round2_20261110_{rel.get("Id")}{suffix}'
            extras[target]=z.read(source)
            rel.set('Target','../media/'+Path(target).name)
    replacement={'ppt/slides/slide2.xml':slide,
                 'ppt/slides/_rels/slide2.xml.rels':etree.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)}
tmp=dest_ppt.with_suffix('.tmp.pptx')
with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for name,(info,data) in original.items():
        if name not in extras:z.writestr(info,replacement.get(name,data))
    for name,data in extras.items():z.writestr(name,data)
tmp.replace(dest_ppt)

# Verify page text, raster output, presentation structure and other-slide bytes.
before=fitz.open(BACKUP/PDFNAME);after=fitz.open(dest_pdf)
checks=[]
for i in range(7):
    if i==1:continue
    assert before[i].get_text()==after[i].get_text(),('other page text changed',i+1)
    a=before[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
    b=after[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
    assert (a.width,a.height)==(b.width,b.height) and a.samples==b.samples,('other page pixels changed',i+1)
    checks.append(i+1)
with zipfile.ZipFile(BACKUP/PPTNAME) as z0,zipfile.ZipFile(dest_ppt) as z1:
    for n in [1,3,4,5,6,7]:
        for name in [f'ppt/slides/slide{n}.xml',f'ppt/slides/_rels/slide{n}.xml.rels']:
            assert z0.read(name)==z1.read(name),('other slide XML changed',name)
    assert z1.testzip() is None
prs=Presentation(dest_ppt);assert len(prs.slides)==7
alltext='\n'.join(sh.text for sh in prs.slides[1].shapes if sh.has_text_frame)
assert '6문항 보드' in alltext and '개인 연결·대응검정 없이' in alltext
page=after[1].get_text()
for term in ['6문항','집단 선호','미노출','유지·수정','100~200명']:
    assert term in page,term
assert '자기수용감' not in page and '색·문구·높이에 반영' not in page
preview=BASE/'시각검토'/'시각화_완성본'/'02.png'
after[1].get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(preview)
record={'changed_pdf_page':2,'changed_pptx_slide':2,'unchanged_pdf_pages_text_and_pixels':checks,
        'unchanged_pptx_slides_xml':checks,'page_count':7,'slide_count':7,
        'pdf_sha256':hashlib.sha256(dest_pdf.read_bytes()).hexdigest(),
        'pptx_sha256':hashlib.sha256(dest_ppt.read_bytes()).hexdigest()}
(BASE/'시각검토'/'선인재단_2차보드_20261110'/'a4_update_verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print('Updated PDF page 2 and editable PPTX slide 2.')
print('Verified unchanged pages/slides:',checks)
print('Preview:',preview)
