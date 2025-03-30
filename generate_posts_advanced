import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

GROUPS_FILE = "ransomwatch-code/groups.json"
OUTPUT_FILE = "ransomwatch-data/posts.json"
POST_CACHE = "prev_posts.json"
GROUP_CACHE = "prev_groups.json"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

EXCLUDE_GROUPS = [g.lower() for g in [
    "akira", "alphv", "blackcat", "ransomhouse", "play",
    "trigona", "cactus", "darkrace", "blackbasta"
]]

def load_groups():
    with open(GROUPS_FILE, "r") as f:
        groups = json.load(f)
    return [g for g in groups if g.get("active") and g["name"].lower() not in EXCLUDE_GROUPS]

def extract_posts_from_group(group):
    posts = []
    for onion_url in group.get("locations", []):
        try:
            resp = requests.get(onion_url, timeout=15)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            titles = soup.find_all("h3") + soup.find_all("h2") + soup.find_all("a")
            for tag in titles:
                title = tag.get_text(strip=True)
                if not title or len(title) < 4:
                    continue
                post_url = urljoin(onion_url, tag.get("href", ""))
                posts.append({
                    "id": f"{group['name']}::{title}",
                    "group": group["name"],
                    "title": title,
                    "url": post_url,
                    "timestamp": datetime.utcnow().isoformat()
                })
        except:
            continue
    return posts

def load_json_set(path):
    if not os.path.exists(path):
        return set()
    with open(path, "r") as f:
        return set(json.load(f))

def save_json_set(path, data):
    with open(path, "w") as f:
        json.dump(list(data), f)

def send_telegram_html(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("[!] 텔레그램 환경변수 없음")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    res = requests.post(url, data=payload)
    print("[텔레그램]", res.status_code, res.text)

def format_html(post):
    return (
        f"🚨 <b>[랜섬웨어 감지]</b>\n\n"
        f"🦠 <b>그룹:</b> <code>{post['group']}</code>\n"
        f"🏢 <b>피해 대상:</b> <u>{post['title']}</u>\n"
        f"🔗 <b>링크:</b> <a href='{post['url']}'>열기</a>\n"
        f"🕒 <b>감지 시간:</b> {post['timestamp']}"
    )

def detect_new_groups(groups):
    current = set(g["name"] for g in groups)
    previous = load_json_set(GROUP_CACHE)
    new_groups = current - previous
    for name in new_groups:
        msg = f"🆕 <b>신규 랜섬웨어 그룹 등장</b>: <code>{name}</code>"
        send_telegram_html(msg)
    save_json_set(GROUP_CACHE, current)

def main():
    groups = load_groups()
    detect_new_groups(groups)

    all_posts = []
    for g in groups:
        all_posts.extend(extract_posts_from_group(g))

    # 테스트용 유출 알림 추가
    all_posts.append({
        "id": "TEST::example.co.kr",
        "group": "TEST",
        "title": "example.co.kr",
        "url": "http://fake-leak-site.onion/test",
        "timestamp": datetime.utcnow().isoformat()
    })

    os.makedirs("ransomwatch-data", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_posts, f, indent=2)

    old_ids = load_json_set(POST_CACHE)
    new_posts = [p for p in all_posts if p["id"] not in old_ids]

    for post in new_posts:
        send_telegram_html(format_html(post))

    save_json_set(POST_CACHE, set(p["id"] for p in all_posts))
    print(f"[✔] 유출 감지 완료: 총 {len(new_posts)}건")

if __name__ == "__main__":
    main()
