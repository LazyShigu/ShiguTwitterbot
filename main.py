import os
import requests
import feedparser
import time
import threading
from fastapi import FastAPI
import uvicorn

# 1. CREATE A TINY WEB SERVER FOR RENDER
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Bot is running perfectly"}

# Configurations (Using environment variables for security)
RSS_FEED_URL = os.environ.get("TWITTER_RSS_URL")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

last_seen_link = None

def check_twitter_feed():
    global last_seen_link
    feed = feedparser.parse(RSS_FEED_URL)
    
    if not feed.entries:
        print("Feed is empty or could not be reached.")
        return

    latest_entry = feed.entries[0]
    latest_link = latest_entry.link

    if latest_link != last_seen_link:
        if last_seen_link is not None:  
            message = f"📢 **New Post on X:** {latest_link}"
            response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
            if response.status_code == 204:
                print(f"Successfully posted: {latest_link}")
            else:
                print(f"Failed to post to Discord: {response.status_code}")
        else:
            print(f"Bot initialized. Monitoring feed starting from: {latest_link}")
        
        last_seen_link = latest_link

# 2. RUN THE BOT LOOP SEPARATELY IN THE BACKGROUND
def bot_loop():
    while True:
        try:
            check_twitter_feed()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        time.sleep(180) # 3 minutes

# Start the background twitter loop thread
threading.Thread(target=bot_loop, daemon=True).start()

# 3. START THE WEB PORT BINDING FOR RENDER
if __name__ == "__main__":
    # Render automatically passes the correct port as an environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
