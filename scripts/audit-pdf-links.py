"""Verify exported PDFs retain clickable email, WhatsApp, Telegram and source links."""
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent.parent
pdfs={
 "majd-fatihy-cv-ar.pdf": ("https://dev.majdfatihy.com/procurement-specialist/",2),
 "majd-fatihy-cv-ats.pdf": ("https://dev.majdfatihy.com/procurement-specialist/",1),
 "majd-fatihy-cv-en.pdf": ("https://dev.majdfatihy.com/procurement-specialist/en/",2),
}
required={
 "mailto:info@majdfatihy.com",
 "https://api.whatsapp.com/send?phone=201066732514",
 "https://t.me/majdfatihy",
}
for filename,(source,pages) in pdfs.items():
    pdf=PdfReader(str(ROOT/"_site"/filename))
    assert len(pdf.pages)==pages,(filename,"Expected A4 page count",len(pdf.pages))
    for n,page in enumerate(pdf.pages,1):
        media=page.mediabox
        assert 590<=float(media.width)<=600 and 837<=float(media.height)<=846,(filename,n,"Not A4",media)
        found=set()
        for ref in page.get("/Annots",[]):
            a=ref.get_object()
            target=a.get("/A")
            if target is not None and target.get("/URI") is not None:
                found.add(str(target.get("/URI")))
        missing=(required|{source})-found
        assert not missing,(filename,n,"Missing clickable PDF links",sorted(missing),sorted(found))
    print(f"PASS: {filename}: {pages} A4 pages, professional contacts and source link on every page")
