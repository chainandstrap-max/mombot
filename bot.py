import os, random, time
from datetime import datetime
from flask import Flask
import threading
from instagrapi import Client

app = Flask(__name__)
@app.route('/')
def home(): 
    return "Mom Bot is Running 24/7 - Followers < 700"

def run_flask(): 
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask).start()

# YAHAN AAP PAGES BADAL SAKTE HO
TARGET_PAGES = ["momcozy", "fridamom", "scarymommy", "solidstarts"]

cl = Client()

# Session Load
if os.path.exists("session.json"):
    cl.load_settings("session.json")
else:
    if os.environ.get("SESSION_DATA"):
        with open("session.json", "w") as f: 
            f.write(os.environ.get("SESSION_DATA"))
        cl.load_settings("session.json")

cl.login(os.environ.get("IG_USER"), os.environ.get("IG_PASS"))
print("Login Success!")

def is_target_mom(user_id):
    try:
        info = cl.user_info(user_id)
        if not info.is_private: 
            return False
        if info.follower_count > 700: 
            return False
        bio = (info.biography + " " + info.full_name).lower()
        if "mom" not in bio and "mama" not in bio and "mother" not in bio and "wife" not in bio and "kids" not in bio:
            return False
        if info.media_count < 2:
            return False
        return True
    except:
        return False

while True:
    now = datetime.now().hour
    # Raat 9 se subah 2 baje tak chalega
    if 21 <= now or now <= 2:
        for page in TARGET_PAGES:
            try:
                print(f"Checking Page: {page}")
                user_id = cl.user_id_from_username(page)
                medias = cl.user_medias(user_id, 2)
                for media in medias:
                    likers = cl.media_likers(media.id)
                    for user in likers:
                        if is_target_mom(user.pk):
                            cl.user_follow(user.pk)
                            print(f"FOLLOWED: {user.username} | Followers: {user.follower_count if hasattr(user, 'follower_count') else ''}")
                            sleep_time = random.randint(480, 900)
                            print(f"Sleeping {sleep_time//60} min...")
                            time.sleep(sleep_time)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(300)
    else:
        print("Abhi USA me din hai, 1 ghante baad check karunga...")
        time.sleep(3600)
