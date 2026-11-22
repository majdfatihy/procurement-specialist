"""Ensure each CV language URL is indexable and visitors may opt into another language."""
import asyncio
import shutil
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent

class QuietHTTP(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

async def main():
    browser_path = next((shutil.which(x) for x in ("google-chrome", "google-chrome-stable", "chromium")
                         if shutil.which(x)), None)
    assert browser_path, "Chrome missing"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "procurement-specialist"
        (root / "en").mkdir(parents=True)
        (root / "assets/js").mkdir(parents=True)
        shutil.copy2(ROOT / "index.html", root / "index.html")
        shutil.copy2(ROOT / "en/index.html", root / "en/index.html")
        shutil.copy2(ROOT / "assets/js/cv-language.js", root / "assets/js/cv-language.js")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHTTP, directory=tmp))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}/procurement-specialist/"
        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    executable_path=browser_path, headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"])
                for locale in ("ar-EG", "en-US", "fr-FR"):
                    for slug, language, suggestion in (
                        ("", "ar", locale != "ar-EG"),
                        ("en/", "en", locale == "ar-EG")
                    ):
                        ctx = await browser.new_context(locale=locale)
                        page = await ctx.new_page()
                        await page.goto(url + slug, wait_until="domcontentloaded")
                        assert page.url == url + slug, (locale, slug, "Locale changed canonical URL", page.url)
                        assert await page.locator("html").get_attribute("lang") == language
                        notice = page.locator("#cv-language-notice")
                        assert await notice.is_visible() == suggestion, (
                            locale, slug, "Unexpected language suggestion")
                        assert await page.locator("link[rel=canonical]").get_attribute("href") == (
                            "https://dev.majdfatihy.com/procurement-specialist/" + slug)
                        await ctx.close()

                # A visitor selects English explicitly and the preference is stored.
                ctx = await browser.new_context(locale="ar-EG")
                page = await ctx.new_page()
                await page.goto(url, wait_until="domcontentloaded")
                assert not await page.locator("#cv-language-notice").is_visible()
                await page.goto(url + "en/?lang=en", wait_until="domcontentloaded")
                assert page.url == url + "en/", page.url
                assert await page.evaluate("localStorage.getItem('majd-cv-preferred-language')") == "en"
                await page.goto(url, wait_until="domcontentloaded")
                assert page.url == url
                assert await page.locator("#cv-language-notice").is_visible()
                assert await page.locator("[data-cv-language-link]").evaluate("(el) => el.href") == (
                    url + "en/?lang=en")
                await page.locator("[data-cv-language-dismiss]").click()
                assert not await page.locator("#cv-language-notice").is_visible()
                await page.reload(wait_until="domcontentloaded")
                assert not await page.locator("#cv-language-notice").is_visible()
                await ctx.close()

                # Switching languages must not erase unrelated URL parameters.
                ctx = await browser.new_context(locale="en-US")
                page = await ctx.new_page()
                await page.goto(url + "?lang=ar&utm_source=resume", wait_until="domcontentloaded")
                assert page.url == url + "?utm_source=resume", page.url
                assert await page.evaluate("localStorage.getItem('majd-cv-preferred-language')") == "ar"
                await page.goto(url + "en/", wait_until="domcontentloaded")
                assert page.url == url + "en/"
                assert await page.locator("#cv-language-notice").is_visible()
                await ctx.close()

                # The same canonical URLs work without JS and with Googlebot user agent.
                for bot in (False, True):
                    ctx = await browser.new_context(
                        locale="en-US", java_script_enabled=not bot,
                        user_agent="Googlebot/2.1 (+http://www.google.com/bot.html)" if bot else None)
                    page = await ctx.new_page()
                    for slug in ("", "en/"):
                        await page.goto(url + slug, wait_until="domcontentloaded")
                        assert page.url == url + slug
                        assert await page.locator("h1").count() == 1
                    await ctx.close()
                await browser.close()
        finally:
            server.shutdown()
            server.server_close()
    print("PASS: canonical AR/EN URLs are accessible in every locale, optional suggestions, saved choices, dismiss, no-JS, and crawler access.")

if __name__ == "__main__":
    asyncio.run(main())
