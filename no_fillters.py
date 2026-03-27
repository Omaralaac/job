import requests
from bs4 import BeautifulSoup
import time
import json
import os

# ==============================
# 🔑 بيانات البوت
# ==============================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("❌ TOKEN or CHAT_ID not found in environment variables!")
    exit(1)

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
# 📲 إرسال رسالة Telegram (Buttons)
# ==============================
def send_telegram(title, link):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": f"🔥 *مشروع جديد:*\n{title}",
            "parse_mode": "Markdown",
            "reply_markup": json.dumps({
                "inline_keyboard": [
                    [
                        {
                            "text": "🔎 فتح المشروع",
                            "url": link
                        }
                    ],
                    [
                        {
                            "text": "💼 كل المشاريع",
                            "url": "https://mostaql.com/projects"
                        }
                    ]
                ]
            })
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
print("🚀 Bot is running with buttons...")

while True:
    projects = get_projects()

    for p in projects:
        if is_new(p):
            send_telegram(p['title'], p['link'])

    time.sleep(180)  # كل 3 دقايق
