import os
import requests
import feedparser
import time

# Configurations (Using environment variables for security)
RSS_FEED_URL = os.environ.get("TWITTER_RSS_URL")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Keep track of the last processed tweet link to avoid duplicates
last_seen_link = None

def check_twitter_feed():
    global last_seen_link
    
    # Parse the RSS feed
    feed = feedparser.parse(RSS_FEED_URL)
    
    if not feed.entries:
        print("Feed is empty or could not be reached.")
        return

    # Get the absolute newest tweet from the feed
    latest_entry = feed.entries[0]
    latest_link = latest_entry.link

    # If it's a brand new tweet, send it to Discord
    if latest_link != last_seen_link:
        # Prevents spamming an old tweet immediately when the script first starts up
        if last_seen_link is not None:  
            message = f"📢 **New Post on X:** {latest_link}"
            
            # Send payload to Discord Webhook
            response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
            if response.status_with == 204:
                print(f"Successfully posted: {latest_link}")
            else:
                print(f"Failed to post to Discord: {response.status_code}")
        else:
            print(f"Bot initialized. Monitoring feed starting from: {latest_link}")
        
        last_seen_link = latest_link

# Infinite loop checking every 3 minutes (180 seconds)
while True:
    try:
        check_twitter_feed()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    # Sleep for 180 seconds (3 minutes)
    time.sleep(180) 
