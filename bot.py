import os, csv, json, time, random
from datetime import datetime
from threading import Thread
from flask import Flask
import requests
from instagrapi import Client
from instagrapi.types import DeviceOrUserAgent

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQp86SZx0TWZLNKeRNlvAla9YKKoeT6Tu8J5A6C6zSV3zNaBTVn1UrZsU0sRDrKOWJKBWiU-zJeyhdH/pub?output=csv"

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
DAILY_TARGET = 90

app = Flask(__name__)
cl = Client()
cl.set_device(DeviceOrUserAgent(
    app_version="275.0.0.27.98",
    android_version=26,
    android_release="8.0.0",
    dpi="480dpi",
    resolution="1080x1920",
    manufacturer="OnePlus",
    device="ONEPLUS A3003",
    model="OnePlus3",
    cpu="qcom",
    version_code="200000",
))
cl.delay_range = [1, 3]
SESSION_FILE = "session.json"
MOMS_FILE = "moms.csv"
COUNT_FILE = "count.json"

def load_pages():
    try:
        r = requests.get(SHEET_URL, timeout=20)
        pages = [row[0].strip().replace("@","") for row in csv.reader(r.text.splitlines()) if row and row[0].strip()]
        if len(pages) >= 3:
            return pages
    except:
        pass
    return ["cindysstyle", "imagessalonoc", "3sistersarchive"]

def get_today_count():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(COUNT_FILE):
        try:
            data = json.load(open(COUNT_FILE))
            if data.get("date") == today:
                return data.get("count", 0)
        except:
            pass
    json.dump({"date": today, "count": 0}, open(COUNT_FILE,"w"))
    return 0

def add_count():
    today = datetime.now().strftime("%Y-%m-%d")
    c = get_today_count() + 1
    json.dump({"date": today, "count": c}, open(COUNT_FILE,"w"))
    return c

def login():
    # NEW: SESSION_JSON variable se load
    sess_data = os.getenv("SESSION_JSON")
    if sess_data:
        try:
            open(SESSION_FILE, "w", encoding="utf-8").write(sess_data)
            print("SESSION_JSON variable loaded")
        except Exception as e:
            print(f"SESSION_JSON write error: {e}")

    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(USERNAME, PASSWORD)
            print("Login with session OK")
            return True
        except Exception as e:
            print(f"Session login fail: {e}")

    try:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print("New login OK")
        return True
    except Exception as e:
        print(f"Login fail: {e}")
        return False

def is_mom(bio):
    if not bio: return False
    bio = bio.lower()
    keywords = ["mom", "mama", "mum", "mummy", "mother", "mommy", "momma", "mom of", "mama of", "mom to", "mama to", "boy mom", "girl mom", "dog mom", "toddler mom", "mother of", "mom life"]
    return any(k in bio for k in keywords)

def bot_loop():
    if not login():
        return
    if not os.path.exists(MOMS_FILE):
        open(MOMS_FILE, "w").write("username,full_name,bio,date,source_page\n")
    already_followed = set()
    if os.path.exists(MOMS_FILE):
        try:
            already_followed = set(row[0] for row in csv.reader(open(MOMS_FILE)) if row)
        except:
            pass
    while True:
        today_count = get_today_count()
        if today_count >= DAILY_TARGET:
            print(f"Target {DAILY_TARGET} done today. Sleeping 1 hour...")
            time.sleep(3600)
            continue
        PAGES = load_pages()
        day_num = datetime.now().timetuple().tm_yday
        todays_pages = [PAGES[(day_num*3) % len(PAGES)], PAGES[(day_num*3+1) % len(PAGES)], PAGES[(day_num*3+2) % len(PAGES)]]
        print(f"--- TODAY 3 PAGES: {todays_pages} | Done: {today_count}/{DAILY_TARGET} ---")
        for page in todays_pages:
            if get_today_count() >= DAILY_TARGET:
                break
            try:
                print(f"Checking page: {page}")
                uid = cl.user_id_from_username(page)
                medias = cl.user_medias(uid, 5)
                for media in medias:
                    if get_today_count() >= DAILY_TARGET:
                        break
                    likers = cl.media_likers(media.id)
                    random.shuffle(likers)
                    for user in likers:
                        if get_today_count() >= DAILY_TARGET:
                            break
                        if user.username in already_followed:
                            continue
                        try:
                            info = cl.user_info(user.pk)
                            if is_mom(info.biography):
                                cl.user_follow(user.pk)
                                open(MOMS_FILE, "a", encoding="utf-8").write(f'"{info.username}","{info.full_name}","{info.biography[:50]}","{datetime.now()}","{page}"\n')
                                already_followed.add(info.username)
                                c = add_count()
                                gap = random.randint(8*60, 15*60)
                                print(f"Followed {info.username} ({c}/{DAILY_TARGET}) - Next in {gap//60} min")
                                time.sleep(gap)
                        except Exception as e:
                            print(f"Error: {e}")
                            time.sleep(60)
            except Exception as e:
                print(f"Page {page} error: {e}")
                time.sleep(60)
        time.sleep(300)

@app.route('/')
def home():
    return f"Bot Running! Today: {get_today_count()}/{DAILY_TARGET}"

if __name__ == "__main__":
    Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
