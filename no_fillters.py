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

        # جلب الميزانية من sidebar (نطاق السعر الكامل)
        budget = "غير محدد"
        try:
            budget_elem = soup.select_one("td:contains('الميزانية') + td")
            if not budget_elem:
                # بديل لو الدعم لـ contains غير موجود في المكتبة
                all_td = soup.find_all("td")
                for i, td in enumerate(all_td):
                    if "الميزانية" in td.text:
                        budget_elem = all_td[i+1] if i+1 < len(all_td) else None
                        break
            if budget_elem:
                budget = budget_elem.text.strip()
        except:
            pass

        # جلب مدة التنفيذ من sidebar
        duration = "غير محدد"
        try:
            duration_elem = soup.select_one("td:contains('مدة التنفيذ') + td")
            if not duration_elem:
                all_td = soup.find_all("td")
                for i, td in enumerate(all_td):
                    if "مدة التنفيذ" in td.text:
                        duration_elem = all_td[i+1] if i+1 < len(all_td) else None
                        break
            if duration_elem:
                duration = duration_elem.text.strip()
        except:
            pass

        return {
            "budget": budget,
            "duration": duration
        }

    except Exception as e:
        print("Details Error:", e)
        return {
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
print("🚀 Bot is running (Without Description)...")

while True:
    projects = get_projects()

    for p in projects:
        if is_new(p):
            details = get_project_details(p["link"])

            full_project = {
                "title": p["title"],
                "link": p["link"],
                "budget": details["budget"],
                "duration": details["duration"]
            }

            send_telegram(full_project)

            time.sleep(5)  # لتجنب الحظر على الموقع

    time.sleep(180)  # كل 3 دقائق
