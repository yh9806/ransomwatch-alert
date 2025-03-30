import json
import os
import requests
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

POSTS_PATH = "ransomwatch/data/posts.json"
GROUPS_PATH = "ransomwatch/data/groups.json"
CACHE_FILE = "prev_posts.json"
GROUP_CACHE_FILE = "prev_groups.json"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    print("텔레그램 응답:", response.text)

def guess_country(domain):
    domain = domain.lower()
    if domain.endswith(".kr"):
        return "🇰🇷"
    elif domain.endswith(".jp"):
        return "🇯🇵"
    elif domain.endswith(".cn"):
        return "🇨🇳"
    elif domain.endswith(".us"):
        return "🇺🇸"
    elif domain.endswith(".fr"):
        return "🇫🇷"
    elif domain.endswith(".de"):
        return "🇩🇪"
    elif domain.endswith(".in"):
        return "🇮🇳"
    elif domain.endswith(".ca"):
        return "🇨🇦"
    elif domain.endswith(".uk"):
        return "🇬🇧"
    else:
        return "🌐"

def guess_industry(title):
    title = title.lower()
    if any(keyword in title for keyword in ["bank", "finance", "card", "capital"]):
        return "금융"
    elif any(keyword in title for keyword in ["hospital", "clinic", "med", "pharma", "health"]):
        return "의료"
    elif any(keyword in title for keyword in ["school", "edu", "univ", "college", "academy"]):
        return "교육"
    elif any(keyword in title for keyword in ["gov", ".gov", "municipal", "state", "city"]):
        return "공공기관"
    elif any(keyword in title for keyword in ["law", "legal", "attorney", "court"]):
        return "법률"
    elif any(keyword in title for keyword in ["telecom", "mobile", "network", "broadband"]):
        return "통신"
    elif any(keyword in title for keyword in ["energy", "oil", "gas", "power", "nuclear"]):
        return "에너지"
    elif any(keyword in title for keyword in ["factory", "plant", "mfg", "manufacture", "industrial"]):
        return "제조업"
    else:
        return "기타"

def format_message(post):
    country = guess_country(post['title'])
    industry = guess_industry(post['title'])
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    message = (
        f"🚨 [랜섬웨어 피해 감지 알림]\n\n"
        f"🦠 그룹명     : {post['group']}\n"
        f"🏢 피해 대상 : {post['title']} {country} [{industry}]\n"
        f"🔗 유출 링크 : {post['url']}\n"
        f"🕒 감지 시간 : {now_str}"
    )
    return message

def load_json_set(filepath):
    if not os.path.exists(filepath):
        return set()
    with open(filepath, "r") as f:
        return set(json.load(f))

def save_json_set(filepath, items):
    with open(filepath, "w") as f:
        json.dump(list(items), f)

def check_new_groups():
    try:
        with open(GROUPS_PATH, "r") as f:
            groups_data = json.load(f)
        current_groups = set(g['name'] for g in groups_data)
        previous_groups = load_json_set(GROUP_CACHE_FILE)

        new_groups = current_groups - previous_groups
        if new_groups:
            for group in new_groups:
                send_telegram(f"🆕 신규 랜섬웨어 그룹 등장: {group}")
            print(f"신규 그룹 감지: {len(new_groups)}건")

        save_json_set(GROUP_CACHE_FILE, current_groups)
    except Exception as e:
        print("신규 그룹 체크 중 오류:", e)

def main():
    with open(POSTS_PATH, "r") as f:
        posts = json.load(f)

    prev_ids = load_json_set(CACHE_FILE)
    new_posts = [p for p in posts if p['id'] not in prev_ids]

    for post in new_posts:
        msg = format_message(post)
        send_telegram(msg)

    current_ids = set(p['id'] for p in posts)
    save_json_set(CACHE_FILE, current_ids)

    check_new_groups()

    print(f"알림 전송 완료: {len(new_posts)}건")

if __name__ == "__main__":
    main()