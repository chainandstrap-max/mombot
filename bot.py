import os, random, time, re, requests, csv, io
from datetime import datetime
from flask import Flask
import threading
from instagrapi import Client

app = Flask(__name__)
@app.route('/')
def home():
    return "Mom Bot - Google Sheet Live Mode"

def run_flask():
    app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask).start()

# --- GOOGLE SHEET SE LIVE PAGES ---
SHEET_URL = os.environ.get("SHEET_URL") # Render me ye variable dalna hai

def get_username_from_url(url):
    url = str(url).strip()
    if not url or url.lower() == 'page': return None
    if "instagram.com" in url:
        m = re.search(r"instagram\.com/([^/?\s]+)", url)
        if m: return m.group(1)
    return url.replace("@","").strip()

def load_pages_from_google_sheet():
    try:
        print("Google Sheet se pages load ho rahe hain...")
        r = requests.get(SHEET_URL, timeout=10)
        r.raise_for_status()

        pages = []
        f = io.StringIO(r.text)
        reader = csv.reader(f)
        for row in reader:
            if row and row[0]:
                u = get_username_from_url(row[0])
                if u and u.lower()!= 'page':
                    pages.append(u)

        pages = list(dict.fromkeys(pages)) # duplicate remove
        print(f"Sheet se {len(pages)} pages mile: {pages[:3]}...")
        return pages
    except Exception as e:
        print(f"Sheet Error: {e}")
        return ["momcozy", "fridamom", "scarymommy"]

# --- LOGIN ---
cl = Client()
cl.delay_range = [2, 5]
if os.path.exists("session.json"):
    cl.load_settings("session.json")
elif os.environ.get("SESSION_DATA"):
    with open("session.json", "w") as f:
        f.write(os.environ.get("SESSION_DATA"))
    cl.load_settings("session.json")

cl.login(os.environ.get("IG_USER"), os.environ.get("IG_PASS"))
print("Login Success!")

def is_target_mom(user_id):
    try:
        info = cl.user_info(user_id)
        if not info.is_private: return False
        if info.follower_count > 700: return False
        bio = (info.biography + " " + info.full_name).lower()
        if not any(k in bio for k in ["mom", "mama", "mother", "wife", "kids", "baby"]):
            return False
        if info.media_count < 2: return False
        return True
    except: return False

# --- LOOP ---
while True:
    ALL_PAGES = load_pages_from_google_sheet()
    today_day = datetime.now().timetuple().tm_yday
    todays_page = ALL_PAGES[today_day % len(ALL_PAGES)]

    now = datetime.now().hour
    if 21 <= now or now <= 2:
        print(f"==== AAJ KA PAGE (Sheet se): {todays_page} | Total: {len(ALL_PAGES)} ====")
        try:
            user_id = cl.user_id_from_username(todays_page)
            medias = cl.user_medias(user_id, 3)
            for media in medias:
                likers = cl.media_likers(media.id)
                random.shuffle(likers)
                for user in likers:
                    if is_target_mom(user.pk):
                        try:
                            cl.user_follow(user.pk)
                            print(f"FOLLOWED: {user.username}")
                            time.sleep(random.randint(480, 900))
                        except:
                            time.sleep(300)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(600)
    else:
        print("Din hai USA me, 1 ghante baad Sheet se naya check karunga...")
        time.sleep(3600)
