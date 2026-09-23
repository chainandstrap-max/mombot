import os
import time
import random
import threading
from flask import Flask
from instagrapi import Client

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
SESSION_FILE = "session.json"

app = Flask(__name__)

@app.route('/')
def home():
    return "Mombot is Running!"

def bot_loop():
    while True:
        try:
            print("Starting Container - Initializing Instagram Client...", flush=True)
            cl = Client()
            
            # Updated modern device profile to bypass version deprecation
            cl.set_device({
                "app_version": "330.0.0.38.109",
                "android_version": 33,
                "android_release": "13.0",
                "dpi": "420dpi",
                "resolution": "1080x2400",
                "manufacturer": "samsung",
                "device": "SM-S911B",
                "model": "Galaxy S23",
                "cpu": "qcom",
                "version_code": "525381090"
            })
            cl.set_locale("en_US")
            cl.set_country_code(1)
            
            # Load existing session if available to avoid repeated full logins
            if os.path.exists(SESSION_FILE):
                print("Loading saved session...", flush=True)
                cl.load_settings(SESSION_FILE)
            
            # Attempt login (or verify session)
            cl.login(USERNAME, PASSWORD)
            
            # Save session for future container restarts
            cl.dump_settings(SESSION_FILE)
            print("New login OK - Bot Started", flush=True)

            while True:
                print("--- Bot is Alive and Logged In ---", flush=True)
                time.sleep(300)

        except Exception as e:
            print(f"Login fail: {e}", flush=True)
            # If session file is broken/expired due to the error, delete it for a fresh retry
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
