import asyncio
from datetime import datetime
from urllib.parse import urljoin
from playwright.async_api import async_playwright

async def extract_posts_with_playwright(group):
    posts = []
    async with async_playwright() as p:
        browser = await p.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"}, headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for onion_url in group.get("locations", []):
            try:
                print(f"[INFO] 접속 시도 중: {onion_url}")
                await page.goto(onion_url, timeout=30000)
                elements = await page.query_selector_all("h2, h3, a")
                for el in elements:
                    title = (await el.inner_text()).strip()
                    href = await el.get_attribute("href") or ""
                    if not title or len(title) < 4:
                        continue
                    full_url = urljoin(onion_url, href)
                    posts.append({
                        "id": f"{group['name']}::{title}",
                        "group": group["name"],
                        "title": title,
                        "url": full_url,
                        "timestamp": datetime.utcnow().isoformat()
                    })
            except Exception as e:
                print(f"[ERROR] {onion_url} 접속 실패: {e}")
        await browser.close()
    return posts