"""Browser-level visual audit for the standalone procurement CV (no production changes)."""
import asyncio
import json
import shutil
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "qa-output"
OUTPUT.mkdir(exist_ok=True)
URL = (ROOT / "index.html").as_uri()

LAYOUT_JS = """() => {
  const rect = (el) => {
    const r = el.getBoundingClientRect();
    return {left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height};
  };
  const selectors = ['main section', '.hero', '.hero-main','.hero-side',
    '.section', '.grid-two', '.advantage-grid', '.timeline-job-card',
    '.contact-row', '.footer', '.topbar'];
  const nodes = [...new Set(selectors.flatMap(s => [...document.querySelectorAll(s)]))];
  const offscreen = nodes.map(n => ({tag:n.tagName,id:n.id,class:n.className,...rect(n)}))
    .filter(r => r.left < -2 || r.right > innerWidth + 2);
  const header = document.querySelector('.topbar');
  const hero = document.querySelector('.hero');
  const title = document.getElementById('main-title');
  const english = document.querySelector('.hero .en-name');
  const t=rect(title), e=rect(english);
  return {
    viewport:innerWidth,
    documentWidth:document.documentElement.scrollWidth,
    bodyWidth:document.body.scrollWidth,
    offscreen,
    headerHeroOverlap:rect(header).bottom > rect(hero).top + 1,
    titleEnglishOverlap:t.bottom > e.top + 1,
    sections:[...document.querySelectorAll('main > .section')].map(s => s.id),
    motionButton:document.getElementById('motionToggle')!==null
  };
}"""

MENU_JS = """() => {
  const menu=document.querySelector('.mobile-menu');
  const nav=document.querySelector('.mobile-nav');
  const links=[...nav.querySelectorAll('a')];
  const intercepts=links.map(link => {
    const r=link.getBoundingClientRect();
    const centerX=(r.left+r.right)/2, centerY=(r.top+r.bottom)/2;
    const el=document.elementFromPoint(centerX,centerY);
    return {text:link.textContent.trim(),visible:r.width>0&&r.height>0,
      front:el===link || link.contains(el),
      covering:el ? (el.className || el.tagName) : 'none'};
  });
  const style=getComputedStyle(nav);
  return {opened:menu.open,intercepts,
    background:style.backgroundColor,opacity:style.opacity,
    headerZ:getComputedStyle(document.querySelector('.topbar')).zIndex};
}"""

async def audit():
    binary=next((shutil.which(b) for b in
        ("google-chrome","google-chrome-stable","chromium")
        if shutil.which(b)),None)
    if not binary:
        raise RuntimeError("Chrome/Chromium was not found")
    diagnostics=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=binary, headless=True,
             args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
        for width,height in ((360,780),(390,844),(412,915),(768,900),(1024,768),(1440,900)):
            page=await browser.new_page(viewport={"width":width,"height":height},
                                          device_scale_factor=1)
            errors=[]
            page.on("pageerror",lambda err: errors.append(str(err)))
            await page.goto(URL,wait_until="domcontentloaded",timeout=30000)
            await page.wait_for_timeout(150)
            result=await page.evaluate(LAYOUT_JS)
            assert result["viewport"]==width,(width,"Unexpected viewport",result["viewport"])
            assert not result["motionButton"],(width,"Motion button still visible")
            assert not result["headerHeroOverlap"],(width,"Hero overlaps header")
            assert not result["titleEnglishOverlap"],(width,"English name overlaps Arabic title")
            assert not result["offscreen"],(width,"Out-of-bounds CV sections",result["offscreen"])
            assert result["documentWidth"]<=width+2,(width,"Horizontal overflow",result)
            assert len(result["sections"])>=7,(width,"Missing sections",result["sections"])
            assert not errors,(width,"JavaScript errors",errors)
            menuData=None
            if width<=1100:
                toggle=page.locator(".mobile-menu summary")
                assert await toggle.is_visible(),(width,"Mobile menu button hidden")
                await toggle.click()
                menuData=await page.evaluate(MENU_JS)
                assert menuData["opened"],(width,"Menu not opened")
                assert menuData["opacity"]=="1",(width,"Menu is translucent")
                assert all(x["visible"] and x["front"] for x in menuData["intercepts"]),(
                    width,"Dropdown behind CV section",menuData)
                await page.screenshot(path=str(OUTPUT/f"menu-open-{width}.png"),
                                      full_page=False,animations="disabled")
                await page.locator('.mobile-nav a[href="#experience"]').click()
                assert not await page.locator(".mobile-menu").evaluate("(el)=>el.open"),(
                    width,"Menu did not close after navigation")
                assert await page.evaluate("location.hash")=="#experience",(
                    width,"Section navigation failed")
                if width<=600:
                    await page.evaluate("document.querySelector('.hero-actions').scrollIntoView({behavior:'instant',block:'center'})")
                    await page.wait_for_timeout(280)
                    assert not await page.locator('.mobile-quick-actions').is_visible(),(
                        width,"Sticky actions overlap main hero buttons")
                    await page.evaluate("window.scrollTo({top:document.body.scrollHeight,behavior:'instant'})")
                    await page.wait_for_timeout(280)
                    assert await page.locator('.mobile-quick-actions').is_visible(),(
                        width,"Sticky actions unavailable after scrolling")
            else:
                assert await page.locator(".desktop-nav").is_visible(),(
                    width,"Desktop navigation hidden")
            await page.screenshot(path=str(OUTPUT/f"full-page-{width}.png"),
                                  full_page=True,animations="disabled")
            diagnostics.append({"width":width,"layout":result,"menu":menuData})
            await page.close()
        await browser.close()
    (OUTPUT/"layout-audit.json").write_text(json.dumps(diagnostics,ensure_ascii=False,indent=2))
    print("PASS: six responsive viewports, all visible sections, no clipping/overlap.")
    print("PASS: dropdown above content at 360,390,412,768,1024; links close menu.")

if __name__=="__main__":
    asyncio.run(audit())
