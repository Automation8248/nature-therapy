import requests
import random
import os
import json
from datetime import datetime

# ================= CONFIGURATION =================
# Webhook URL
MAKE_WEBHOOK_URL = "YOUR_MAKE_WEBHOOK_URL"

# Telegram Setup (Alag Tokens, Alag Chat IDs)
TELEGRAM_SUCCESS_BOT_TOKEN = "YOUR_SUCCESS_BOT_TOKEN"
TELEGRAM_SUCCESS_CHAT_ID = "YOUR_SUCCESS_CHAT_ID"

TELEGRAM_ERROR_BOT_TOKEN = "YOUR_ERROR_BOT_TOKEN"
TELEGRAM_ERROR_CHAT_ID = "YOUR_ERROR_CHAT_ID"

# Automation Info (Jo Telegram par jayega)
AUTOMATION_NAME = "My AutoPoster Pro"
SOCIAL_MEDIA_NAME = "Facebook & Instagram (USA Target)"

# Cooldown Time
COOLDOWN_DAYS = 30

# File Paths
HISTORY_FILE = "history.json"
TITLES_FILE = "titles.txt"
HASHTAGS_FILE = "hashtags.txt"
IMAGE_FOLDER = "images"
# =================================================

def load_history():
    """History file load karta hai taaki cooldown track ho sake."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"titles": {}, "hashtags": {}}

def save_history(history):
    """Update ki hui history save karta hai."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def get_available_item(file_path, item_type, history):
    """30 days ke cooldown ko check karke random title/hashtag pick karta hai."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            items = [line.strip() for line in f.readlines() if line.strip()]
            
        available_items = []
        now = datetime.now()
        
        for item in items:
            if item in history[item_type]:
                last_used_date = datetime.strptime(history[item_type][item], "%Y-%m-%d")
                days_passed = (now - last_used_date).days
                if days_passed >= COOLDOWN_DAYS:
                    available_items.append(item)
            else:
                available_items.append(item)
                
        if not available_items:
            raise Exception(f"Sabhi {item_type} cooldown mein hain! Kripya naye data add karein.")
            
        return random.choice(available_items)
    except FileNotFoundError:
        raise Exception(f"File {file_path} nahi mili!")

def send_telegram_log(status, error_message=""):
    """Telegram par Success ya Error ka log bhejta hai naye variables ke sath."""
    if status == "success":
        bot_token = TELEGRAM_SUCCESS_BOT_TOKEN
        chat_id = TELEGRAM_SUCCESS_CHAT_ID
        text_message = f"✅ **SUCCESS**\n\n🤖 **Automation:** {AUTOMATION_NAME}\n🌐 **Social Media:** {SOCIAL_MEDIA_NAME}\n\nStatus: Aaj ka task successfully complete ho gaya hai! Image delete kar di gayi hai."
    else:
        bot_token = TELEGRAM_ERROR_BOT_TOKEN
        chat_id = TELEGRAM_ERROR_CHAT_ID
        text_message = f"❌ **ERROR ALERT**\n\n🤖 **Automation:** {AUTOMATION_NAME}\n🌐 **Social Media:** {SOCIAL_MEDIA_NAME}\n\n⚠️ **Error Detail:**\n{error_message}"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text_message, "parse_mode": "Markdown"}
    
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram notification failed: {e}")

def send_to_webhook_direct(image_path, title, hashtag):
    """Webhook par actual image file aur data direct bhejta hai."""
    with open(image_path, "rb") as img_file:
        files = {
            "image": img_file  # Webhook par image is key par aayegi
        }
        data = {
            "title": title,
            "hashtags": hashtag
        }
        response = requests.post(MAKE_WEBHOOK_URL, data=data, files=files)
        
        if response.status_code not in [200, 204, 201]:
            raise Exception(f"Webhook error: {response.text}")

def daily_job():
    """Ye main function hai jo daily run hoga."""
    print(f"\n--- Starting Job: {datetime.now()} ---")
    try:
        # 1. Cooldown history load karein
        history = load_history()
        
        # 2. Pick Title & Hashtag
        title = get_available_item(TITLES_FILE, "titles", history)
        hashtag = get_available_item(HASHTAGS_FILE, "hashtags", history)
        
        # 3. Pick random Image from 'images' folder (SIRF IMAGES PICK KAREGA, TXT IGNORE KAREGA)
        if not os.path.exists(IMAGE_FOLDER):
            os.makedirs(IMAGE_FOLDER)
            raise Exception("Images folder empty ya create kiya gaya hai. Images add karein!")
            
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(valid_extensions)]
        
        if not images:
            raise Exception("Images folder mein koi VALID image file nahi bachi hai!")
            
        selected_image = random.choice(images)
        image_path = os.path.join(IMAGE_FOLDER, selected_image)
        
        # 4. Send File & Data to Webhook Directly
        print(f"Sending {selected_image} and data to Webhook...")
        send_to_webhook_direct(image_path, title, hashtag)
        
        # 5. Update History with today's date
        today_str = datetime.now().strftime("%Y-%m-%d")
        history["titles"][title] = today_str
        history["hashtags"][hashtag] = today_str
        save_history(history)
        
        # 6. Automatic Image Deletion
        os.remove(image_path)
        print(f"Image {selected_image} successfully deleted from folder.")
        
        # 7. Send Success to Telegram Bot
        print("Job successful! Sending Telegram Success log.")
        send_telegram_log(status="success")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        # Send Error to Telegram Bot
        send_telegram_log(status="error", error_message=str(e))

if __name__ == "__main__":
    # GitHub Actions isko daily cron job ke through trigger karega
    daily_job()
