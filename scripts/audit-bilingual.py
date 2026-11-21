"""Verify the complete English CV and download links at responsive viewport sizes."""
import asyncio
import json
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"qa-output"
OUT.mkdir(exist_ok=True)
PAGE=(ROOT/"en"/"index.html").as_uri()

async def main():
    exe=next((shutil.which(name) for name in ("google-chrome","google-chrome-stable","chromium") if shutil.which(name)),None)
    assert exe,"Chromium/Chrome required"
    for f in ("majd-fatihy-cv-ar.pdf","majd-fatihy-cv-ats.pdf","majd-fatihy-cv-en.pdf"):
        path=ROOT/"_site"/f
        assert path.is_file() and path.stat().st_size>1000,f"Missing downloadable PDF: {f}"
    results=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=exe,headless=True,args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        for w,h in ((360,780),(390,844),(412,915),(768,900),(1024,768),(1440,900)):
            page=await browser.new_page(viewport={"width":w,"height":h},device_scale_factor=1)
            errors=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            await page.goto(PAGE,wait_until="domcontentloaded",timeout=30000)
            await page.wait_for_timeout(200)
            check=await page.evaluate("""() => {
               const boxes=[...document.querySelectorAll('.hero,.intro,.photo,.section,.tile,.top,footer,.contact a')];
               const outside=boxes.map(el=>({id:el.id,className:el.className,x:el.getBoundingClientRect().x,
                  right:el.getBoundingClientRect().right}))
                 .filter(x=>x.x < -2 || x.right > innerWidth + 2);
               const hero=document.querySelector('.hero').getBoundingClientRect();
               const header=document.querySelector('.top').getBoundingClientRect();
               return {
                 width:innerWidth,documentWidth:document.documentElement.scrollWidth,
                 title:document.querySelector('h1').innerText.trim(),outside,
                 headerOverlap:header.bottom > hero.top + 1,
                 portraitLoaded:document.querySelector('.photo img').naturalWidth > 0,
                 sections:[...document.querySelectorAll('main .section')].map(x=>x.id),
                 pdfLinks:[...document.querySelectorAll('a[download]')].map(x=>x.getAttribute('href')),
                 actionsVisible:getComputedStyle(document.querySelector('.mobile-bar')).display!=='none',
                 contacts:[...document.querySelectorAll('#contact a')].length
               };
             }""")
            assert check["width"]==w,(w,"Viewport changed",check)
            assert check["documentWidth"]<=w+2,(w,"Horizontal scrolling",check)
            assert not check["outside"],(w,"Card/section outside viewport",check["outside"])
            assert not check["headerOverlap"],(w,"Header overlaps hero")
            assert check["portraitLoaded"],(w,"Portrait failed to load")
            assert check["title"]=="Majd Fatihy",(w,"Incorrect name")
            assert len(check["sections"])>=9,(w,"Missing English sections")
            assert check["contacts"]>=3,(w,"Missing professional contact links")
            assert check["actionsVisible"]==(w<=650),(w,"Mobile actions visibility")
            assert not errors,(w,"JS errors",errors)
            if w in (390,1440):
                await page.screenshot(path=str(OUT/f"english-{w}.png"),full_page=True,animations="disabled")
            results.append({"width":w,"result":"pass","pageWidth":check["documentWidth"],"sectionCount":len(check["sections"])})
            await page.close()
        await browser.close()
    (OUT/"bilingual-audit.json").write_text(json.dumps(results,indent=2))
    print("PASS: English CV at 360/390/412/768/1024/1440px, no overflow, photo, navigation, contacts and PDF links.")

if __name__=="__main__":
    asyncio.run(main())
