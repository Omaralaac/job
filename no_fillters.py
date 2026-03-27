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
    print("❌ TOKEN or CHAT_ID not found!")
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
# 📲 إرسال Telegram
# ==============================
def send_telegram(project):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        message = f"""🔥 *مشروع جديد*

📌 *العنوان:* {project['title']}
💰 *الميزانية:* {project['budget']}
⏳ *المدة:* {project['duration']}

📝 *الوصف:*
{project['description'][:300]}...
"""

        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps({
                "inline_keyboard": [
                    [
                        {
                            "text": "🔎 فتح المشروع",
                            "url": project['link']
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
# 🕷️ جلب المشاريع الأساسية
# ==============================
def get_projects():
    try:
        url = "https://mostaql.com/projects"
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        projects = []

        for c in soup.select("h2 a"):
            title = c.text.strip()

            href = c["href"]
            if href.startswith("http"):
                link = href
            else:
                link = "https://mostaql.com" + href
            link = link.strip()

            projects.append({
                "title": title,
                "link": link
            })

        return projects

    except Exception as e:
        print("Error:", e)
        return []

# ==============================
# 📄 جلب تفاصيل المشروع
# ==============================
def get_project_details(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(link, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        # الوصف
        desc = soup.select_one(".project-description")
        description = desc.text.strip() if desc else "غير متوفر"

        # الميزانية
        budget = soup.find(text=lambda t: "ميزانية المشروع" in t)
        if budget:
            budget = budget.find_next().text.strip()
        else:
            budget = "غير محدد"

        # المدة
        duration = soup.find(text=lambda t: "مدة التنفيذ" in t)
        if duration:
            duration = duration.find_next().text.strip()
        else:
            duration = "غير محدد"

        return {
            "description": description,
            "budget": budget,
            "duration": duration
        }

    except Exception as e:
        print("Details Error:", e)
        return {
            "description": "خطأ في جلب الوصف",
            "budget": "؟",
            "duration": "؟"
        }

# ==============================
# 🆕 تحقق من الجديد
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
print("🚀 Bot is running (FULL DATA)...")

while True:
    projects = get_projects()

    for p in projects:
        if is_new(p):
            details = get_project_details(p["link"])

            full_project = {
                "title": p["title"],
                "link": p["link"],
                "description": details["description"],
                "budget": details["budget"],
                "duration": details["duration"]
            }

            send_telegram(full_project)

            time.sleep(5)  # لتجنب الحظر على الموقع

    time.sleep(180)  # كل 3 دقائق
