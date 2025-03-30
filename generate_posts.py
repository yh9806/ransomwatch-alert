import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

GROUPS_FILE = "ransomwatch-code/groups.json"
OUTPUT_FILE = "ransomwatch-data/posts.json"

# 자동 크롤링이 어려운 예외 그룹들
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
                print(f"[!] 접속 실패: {onion_url}")
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
        except Exception as e:
            print(f"[X] {group['name']} 에러: {e}")
    return posts

def main():
    groups = load_groups()
    all_posts = []
    for group in groups:
        posts = extract_posts_from_group(group)
        print(f"[+] {group['name']} → {len(posts)}건 감지")
        all_posts.extend(posts)

    os.makedirs("ransomwatch-data", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_posts, f, indent=2)

    print(f"[✔] 총 유출 감지: {len(all_posts)}건")

if __name__ == "__main__":
    main()