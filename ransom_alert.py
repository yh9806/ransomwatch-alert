
import requests
import json
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

DATA_URL = "https://raw.githubusercontent.com/joshhighet/ransomwatch/main/data/posts.json"
CACHE_FILE = "prev_posts.json"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
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

def main():
    prev_ids = load_previous_ids()
    posts = fetch_current_posts()

    new_posts = [p for p in posts if p["id"] not in prev_ids]

    if new_posts:
        for post in new_posts:
            msg = f"🚨 [{post['group']}] 새로운 피해자 발견: {post['title']}\nURL: {post['url']}"
            send_telegram(msg)
        print(f"알림 전송 완료: {len(new_posts)}건")

    current_ids = set(p["id"] for p in posts)
    save_current_ids(current_ids)

if __name__ == "__main__":
    main()
