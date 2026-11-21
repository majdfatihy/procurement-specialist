"""Browser-language redirects: save explicit choice, preserve SEO-language URLs."""
import asyncio
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import shutil, tempfile, threading
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parent.parent

class QuietHTTP(SimpleHTTPRequestHandler):
    def log_message(self,*args):
        pass

async def main():
    browser_path=next((shutil.which(x) for x in ("google-chrome","google-chrome-stable","chromium") if shutil.which(x)),None)
    assert browser_path,"Chrome missing"
    with tempfile.TemporaryDirectory() as tmp:
        dst=Path(tmp)/"procurement-specialist"
        (dst/"en").mkdir(parents=True)
        (dst/"assets/js").mkdir(parents=True)
        shutil.copy2(ROOT/"index.html",dst/"index.html")
        shutil.copy2(ROOT/"en/index.html",dst/"en/index.html")
        shutil.copy2(ROOT/"assets/js/cv-language.js",dst/"assets/js/cv-language.js")
        server=ThreadingHTTPServer(("127.0.0.1",0),partial(QuietHTTP,directory=tmp))
        task=threading.Thread(target=server.serve_forever,daemon=True)
        task.start()
        origin=f"http://127.0.0.1:{server.server_port}/procurement-specialist/"
        try:
            async with async_playwright() as p:
                browser=await p.chromium.launch(executable_path=browser_path,headless=True,
                    args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu"])
                for locale,source,expected in [
                    ("ar-EG","", ""),("ar-EG","en/",""),
                    ("en-US","", "en/"),("en-US","en/","en/"),
                    ("fr-FR","", "en/")]:
                    ctx=await browser.new_context(locale=locale)
                    page=await ctx.new_page()
                    await page.goto(origin+source,wait_until="domcontentloaded")
                    await page.wait_for_url(origin+expected,timeout=5000)
                    assert page.url==origin+expected,(locale,source,page.url)
                    await ctx.close()
                # English browser visitor explicitly switches to Arabic.
                ctx=await browser.new_context(locale="en-US")
                page=await ctx.new_page()
                await page.goto(origin,wait_until="domcontentloaded")
                await page.wait_for_url(origin+"en/",timeout=5000)
                await page.goto(origin+"?lang=ar",wait_until="domcontentloaded")
                assert page.url==origin,page.url
                assert await page.evaluate("localStorage.getItem('majd-cv-preferred-language')")=="ar"
                await page.goto(origin+"en/",wait_until="domcontentloaded")
                await page.wait_for_url(origin,timeout=5000)
                await ctx.close()
                # Arabic browser visitor explicitly chooses English.
                ctx=await browser.new_context(locale="ar-EG")
                page=await ctx.new_page()
                await page.goto(origin+"en/?lang=en",wait_until="domcontentloaded")
                assert page.url==origin+"en/",page.url
                assert await page.evaluate("localStorage.getItem('majd-cv-preferred-language')")=="en"
                await page.goto(origin,wait_until="domcontentloaded")
                await page.wait_for_url(origin+"en/",timeout=5000)
                await ctx.close()
                # Googlebot user-agent must be able to access both indexable URLs.
                ctx=await browser.new_context(locale="en-US",user_agent="Googlebot/2.1 (+http://www.google.com/bot.html)")
                page=await ctx.new_page()
                await page.goto(origin,wait_until="domcontentloaded")
                assert page.url==origin,page.url
                await page.goto(origin+"en/",wait_until="domcontentloaded")
                assert page.url==origin+"en/",page.url
                await ctx.close()
                await browser.close()
        finally:
            server.shutdown();server.server_close()
    print("PASS: locale ar/en/other, manual choice persistence and Googlebot access.")

if __name__=="__main__":
    asyncio.run(main())
