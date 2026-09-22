import os, time, random, threading
from flask import Flask
from instagrapi import Client

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")

app = Flask(__name__)

@app.route('/')
def home():
    return "Mombot is Running!"

def bot_loop():
    while True:
        try:
            print("Starting Container - Trying Login...", flush=True)
            cl = Client()
            # --- NAYA FIX ---
            cl.set_device({
                "app_version": "314.0.0.49.146",
                "android_version": 33,
                "android_release": "13.0",
                "dpi": "420dpi",
                "resolution": "1080x2400",
                "manufacturer": "samsung",
                "device": "SM-G998B",
                "model": "Galaxy S21 Ultra",
                "cpu": "exynos2100",
                "version_code": "314002146"
            })
            cl.set_locale("en_US")
            cl.set_country_code(1)
            
            cl.login(USERNAME, PASSWORD)
            print("New login OK - Bot Started", flush=True)

            while True:
                print("--- Bot is Alive and Logged In ---", flush=True)
                time.sleep(300)

        except Exception as e:
            print(f"Login fail: {e}", flush=True)
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    
