
import requests
import json
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

DATA_URL = "https://raw.githubusercontent.com/joshhighet/ransomwatch/main/data/posts.json"
CACHE_FILE = "prev_posts.json"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def load_previous_ids():
    if not os.path.exists(CACHE_FILE):
        return set()
    with open(CACHE_FILE, "r") as f:
        return set(json.load(f))

def save_current_ids(post_ids):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(post_ids), f)

def fetch_current_posts():
    response = requests.get(DATA_URL)
    if response.status_code != 200:
        print("Failed to fetch posts.json")
        return []
    return response.json()

# 국가 추정
def guess_country(domain):
    domain = domain.lower()
    if domain.endswith(".kr"):
        return "🇰🇷"
    elif domain.endswith(".jp"):
        return "🇯🇵"
    elif domain.endswith(".ru"):
        return "🇷🇺"
    elif domain.endswith(".cn"):
        return "🇨🇳"
    elif domain.endswith(".us"):
        return "🇺🇸"
    else:
        return "🌐"

# 업종 추정
def guess_industry(title):
    title_lower = title.lower()
    if "bank" in title_lower or "finance" in title_lower:
        return "금융"
    elif "hospital" in title_lower or "clinic" in title_lower or "med" in title_lower:
        return "의료"
    elif "school" in title_lower or "edu" in title_lower or "univ" in title_lower:
        return "교육"
    elif "gov" in title_lower or ".gov" in title_lower:
        return "정부"
    else:
        return "일반"

# 메시지 포맷
def format_message(post):
    domain = post['title']
    country_flag = guess_country(domain)
    industry = guess_industry(domain)

    message = (
        f"🔥 신규 피해자 감지 🔥\n"
        f"그룹: {post['group']}\n"
        f"피해 대상: {domain} {country_flag} [{industry}]\n"
        f"📎 링크: {post['url']}"
    )
    return message

def main():
    prev_ids = load_previous_ids()
    posts = fetch_current_posts()

    new_posts = [p for p in posts if p["id"] not in prev_ids]

    if new_posts:
        for post in new_posts:
            msg = format_message(post)
            send_telegram(msg)
        print(f"알림 전송 완료: {len(new_posts)}건")

    current_ids = set(p["id"] for p in posts)
    save_current_ids(current_ids)

if __name__ == "__main__":
    main()
