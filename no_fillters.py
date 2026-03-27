import requests
from bs4 import BeautifulSoup
import time
import json
import os

# ==============================
# 🔑 بيانات البوت
# ==============================

import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
#TOKEN = "8601457115:AAFD7Mb5WPVoGhmNWimiQpzAIhJTzLvb5mc"
#CHAT_ID = "1130472857"

# ==============================
# 📁 ملف حفظ المشاريع
# ==============================
SEEN_FILE = "seen.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

seen = load_seen()

# ==============================
# 📲 إرسال رسالة Telegram
# ==============================
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message
        }
        res = requests.post(url, data=data)
        print("Sent:", res.json())
    except Exception as e:
        print("Telegram Error:", e)

# ==============================
# 🕷️ جلب المشاريع
# ==============================
def get_projects():
    try:
        url = "https://mostaql.com/projects"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        projects = []

        for c in soup.select("h2 a"):
            title = c.text.strip()
            link = "https://mostaql.com" + c["href"]

            projects.append({
                "title": title,
                "link": link
            })

        return projects

    except Exception as e:
        print("Scraping Error:", e)
        return []

# ==============================
# 🆕 التحقق من المشاريع الجديدة
# ==============================
def is_new(project):
    if project["link"] in seen:
        return False

    seen.add(project["link"])
    save_seen(seen)
    return True

# ==============================
# 🔁 تشغيل البوت
# ==============================
print("🚀 Bot is running (No Filter)...")

while True:
    projects = get_projects()

    for p in projects:
        if is_new(p):
            message = f"🔥 مشروع جديد:\n{p['title']}\n{p['link']}"
            send_telegram(message)

    time.sleep(180)  # كل 3 دقايق
