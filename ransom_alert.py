
import json
import os
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

POSTS_PATH = "ransomwatch/data/posts.json"
CACHE_FILE = "prev_posts.json"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    print("텔레그램 응답:", response.text)

def guess_country(domain):
    if domain.endswith(".kr"):
        return "🇰🇷"
    elif domain.endswith(".jp"):
        return "🇯🇵"
    elif domain.endswith(".us"):
        return "🇺🇸"
    else:
        return "🌐"

def guess_industry(title):
    title = title.lower()
    if "bank" in title or "finance" in title:
        return "금융"
    elif "hospital" in title or "clinic" in title or "med" in title:
        return "의료"
    elif "school" in title or "edu" in title or "univ" in title:
        return "교육"
    elif "gov" in title or ".gov" in title:
        return "정부"
    else:
        return "일반"

def format_message(post):
    country = guess_country(post['title'])
    industry = guess_industry(post['title'])
    return (
        f"🔥 신규 피해자 감지 🔥\n"
        f"그룹: {post['group']}\n"
        f"피해 대상: {post['title']} {country} [{industry}]\n"
        f"📎 링크: {post['url']}"
    )

def load_prev_ids():
    if not os.path.exists(CACHE_FILE):
        return set()
    with open(CACHE_FILE, "r") as f:
        return set(json.load(f))

def save_ids(ids):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(ids), f)

def main():
    with open(POSTS_PATH, "r") as f:
        posts = json.load(f)

    prev_ids = load_prev_ids()
    new_posts = [p for p in posts if p['id'] not in prev_ids]

    for post in new_posts:
        msg = format_message(post)
        send_telegram(msg)

    current_ids = set(p['id'] for p in posts)
    save_ids(current_ids)
    print(f"알림 전송 완료: {len(new_posts)}건")

if __name__ == "__main__":
    main()
