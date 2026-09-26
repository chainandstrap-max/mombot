import os
import time
import threading
from flask import Flask
from instagrapi import Client

# Load environment variables for security
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
SESSION_FILE = "session.json"

app = Flask(__name__)

@app.route('/')
def home():
    return "Mombot is Running and Active!"

def bot_loop():
    while True:
        try:
            print("Initializing Instagram Client...", flush=True)
            cl = Client()
            
            # Use instagrapi's default modern client configuration 
            # (Avoids hardcoding old app versions that trigger the 'out of date' error)
            cl.set_locale("en_US")
            cl.set_country_code(1)
            
            # Load session if it exists to bypass direct password logins
            if os.path.exists(SESSION_FILE):
                print("Loading existing session from session.json...", flush=True)
                cl.load_settings(SESSION_FILE)
            
            # Log in using credentials or validate the loaded session
            print("Logging in / validating session...", flush=True)
            cl.login(USERNAME, PASSWORD)
            
            # Save/update session data
            cl.dump_settings(SESSION_FILE)
            print("Successfully logged in - Bot loop started!", flush=True)

            # Main automation loop (put your bot tasks here)
            while True:
                print("--- Mombot is active and running tasks ---", flush=True)
                
                # TODO: Add your custom automation logic here (e.g., check DMs, fetch posts)
                
                time.sleep(300) # Wait 5 minutes between loops

        except Exception as e:
            print(f"Bot error encountered: {e}", flush=True)
            # If the session expired or threw an error, clean it up for the next retry
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            print("Retrying connection in 60 seconds...", flush=True)
            time.sleep(60)

# Run the bot logic in a background thread so the Flask server can bind to the port immediately
threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    # Railway/Cloud services require binding to 0.0.0.0 and port 8080 (or PORT env variable)
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
