import requests
import random
import os
import json
from datetime import datetime

# ================= CONFIGURATION (Fetching from GitHub Secrets) =================
# Ab yahan apne aap GitHub Secrets se data fetch hoga
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

TELEGRAM_SUCCESS_BOT_TOKEN = os.getenv("TELEGRAM_SUCCESS_BOT_TOKEN")
TELEGRAM_SUCCESS_CHAT_ID = os.getenv("TELEGRAM_SUCCESS_CHAT_ID")

TELEGRAM_ERROR_BOT_TOKEN = os.getenv("TELEGRAM_ERROR_BOT_TOKEN")
TELEGRAM_ERROR_CHAT_ID = os.getenv("TELEGRAM_ERROR_CHAT_ID")

# Automation Info
AUTOMATION_NAME = "Nature Therapy img post"
SOCIAL_MEDIA_NAME = "Facebook (USA Target)"
COOLDOWN_DAYS = 30

# File Paths
HISTORY_FILE = "history.json"
TITLES_FILE = "titles.txt"
HASHTAGS_FILE = "hashtags.txt"
IMAGE_FOLDER = "images"
# =================================================================================

# 30+ Free File Hosting APIs (Fallback List)
UPLOAD_HOSTS = [
    {"name": "Catbox", "url": "https://catbox.moe/user/api.php", "type": "catbox"},
    {"name": "Uguu.se", "url": "https://uguu.se/upload.php", "type": "pomf"},
    {"name": "Pixeldrain", "url": "https://pixeldrain.com/api/file", "type": "pixeldrain"},
    {"name": "0x0.st", "url": "https://0x0.st", "type": "text"},
    {"name": "Envs.sh", "url": "https://envs.sh", "type": "text"},
    {"name": "Ttm.sh", "url": "https://ttm.sh", "type": "text"},
    {"name": "Pomf.lain.la", "url": "https://pomf.lain.la/upload.php", "type": "pomf"},
    {"name": "File.io", "url": "https://file.io", "type": "fileio"},
    {"name": "x0.at", "url": "https://x0.at", "type": "text"},
    {"name": "Qu.ax", "url": "https://qu.ax/upload.php", "type": "pomf"},
    {"name": "Litterbox", "url": "https://litterbox.catbox.moe/user/api.php", "type": "catbox_litter"},
    {"name": "Tmpfiles", "url": "https://tmpfiles.org/api/v1/upload", "type": "tmpfiles"},
    {"name": "Oshi.at", "url": "https://oshi.at", "type": "text"},
    {"name": "Bashupload", "url": "https://bashupload.com", "type": "text"},
    {"name": "Upx.nz", "url": "https://upx.nz", "type": "text"},
    {"name": "S.Zillyhuhn", "url": "https://s.zillyhuhn.com/upload.php", "type": "pomf"},
    {"name": "Filecoffee", "url": "https://filecoffee.com/api/v1/upload", "type": "filecoffee"},
    {"name": "Hostux", "url": "https://hostux.network/upload.php", "type": "pomf"},
    {"name": "Ptp.moe", "url": "https://ptp.moe/upload.php", "type": "pomf"},
    {"name": "Imadns", "url": "https://up.imadns.com/upload.php", "type": "pomf"},
    {"name": "Miyou", "url": "https://miyou.tv/upload.php", "type": "pomf"},
    {"name": "0x0.la", "url": "https://0x0.la", "type": "text"},
    {"name": "Transfer.sh", "url": "https://transfer.sh", "type": "text"},
    {"name": "Ashi.at", "url": "https://ashi.at", "type": "text"},
    {"name": "Cata.st", "url": "https://cata.st", "type": "text"},
    {"name": "P.ip.fi", "url": "https://p.ip.fi", "type": "text"},
    {"name": "Paste.c-net", "url": "https://paste.c-net.org", "type": "text"},
    {"name": "F.losno", "url": "https://f.losno.co", "type": "text"},
    {"name": "Nullbyte", "url": "https://0x0.st", "type": "text"}, 
    {"name": "SafeMoe", "url": "https://uguu.se/upload.php", "type": "pomf"}
]

def check_secrets():
    """Check karega ki GitHub Secrets sahi se load hue hain ya nahi"""
    if not MAKE_WEBHOOK_URL:
        raise Exception("MAKE_WEBHOOK_URL secret mein nahi mila!")
    if not TELEGRAM_SUCCESS_BOT_TOKEN or not TELEGRAM_ERROR_BOT_TOKEN:
        print("Warning: Telegram tokens missing hain. Telegram logs send nahi honge.")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"titles": {}, "hashtags": {}}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def get_available_item(file_path, item_type, history):
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

def upload_with_fallback(image_path):
    for host in UPLOAD_HOSTS:
        print(f"Trying to upload image via: {host['name']}...")
        try:
            with open(image_path, "rb") as f:
                host_type = host["type"]
                url = host["url"]
                
                if host_type == "catbox":
                    response = requests.post(url, data={"reqtype": "fileupload"}, files={"fileToUpload": f}, timeout=15)
                    if response.status_code == 200 and "catbox.moe" in response.text:
                        return response.text.strip()
                elif host_type == "catbox_litter":
                    response = requests.post(url, data={"reqtype": "fileupload", "time": "24h"}, files={"fileToUpload": f}, timeout=15)
                    if response.status_code == 200:
                        return response.text.strip()
                elif host_type == "pomf":
                    response = requests.post(url, files={"files[]": f}, timeout=15)
                    if response.status_code == 200:
                        return response.json()["files"][0]["url"]
                elif host_type == "pixeldrain":
                    response = requests.post(url, files={"file": f}, timeout=15)
                    if response.status_code in [200, 201]:
                        return f"https://pixeldrain.com/api/file/{response.json()['id']}"
                elif host_type == "fileio":
                    response = requests.post(url, files={"file": f}, timeout=15)
                    if response.status_code == 200:
                        return response.json()["link"]
                elif host_type == "tmpfiles":
                    response = requests.post(url, files={"file": f}, timeout=15)
                    if response.status_code == 200:
                        raw_url = response.json()["data"]["url"]
                        return raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                elif host_type == "text":
                    response = requests.post(url, files={"file": f}, timeout=15)
                    if response.status_code == 200 and "http" in response.text:
                        return response.text.strip()
        except Exception as e:
            print(f"❌ Failed on {host['name']}: {e}")
            continue
            
    raise Exception("All 30+ File Hosting Websites Failed to Upload!")

def send_telegram_log(status, error_message="", host_used=""):
    if status == "success" and TELEGRAM_SUCCESS_BOT_TOKEN:
        bot_token = TELEGRAM_SUCCESS_BOT_TOKEN
        chat_id = TELEGRAM_SUCCESS_CHAT_ID
        text_message = f"✅ **SUCCESS**\n\n🤖 **Automation:** {AUTOMATION_NAME}\n🌐 **Social Media:** {SOCIAL_MEDIA_NAME}\n🔗 **Hosted On:** {host_used}\n\nStatus: Aaj ka task successfully complete ho gaya hai! Image webhook par send hoke delete ho gayi hai."
    elif status == "error" and TELEGRAM_ERROR_BOT_TOKEN:
        bot_token = TELEGRAM_ERROR_BOT_TOKEN
        chat_id = TELEGRAM_ERROR_CHAT_ID
        text_message = f"❌ **ERROR ALERT**\n\n🤖 **Automation:** {AUTOMATION_NAME}\n🌐 **Social Media:** {SOCIAL_MEDIA_NAME}\n\n⚠️ **Error Detail:**\n{error_message}"
    else:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text_message, "parse_mode": "Markdown"}
    
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram notification failed: {e}")

def send_to_webhook(image_url, title, hashtag):
    payload = {
        "title": title,
        "hashtags": hashtag,
        "image_url": image_url
    }
    response = requests.post(MAKE_WEBHOOK_URL, json=payload)
    
    if response.status_code not in [200, 204, 201]:
        raise Exception(f"Webhook error: {response.text}")

def daily_job():
    print(f"\n--- Starting Job: {datetime.now()} ---")
    try:
        check_secrets() # Check if secrets are loaded
        history = load_history()
        title = get_available_item(TITLES_FILE, "titles", history)
        hashtag = get_available_item(HASHTAGS_FILE, "hashtags", history)
        
        if not os.path.exists(IMAGE_FOLDER):
            os.makedirs(IMAGE_FOLDER)
            raise Exception("Images folder empty ya create kiya gaya hai. Images add karein!")
            
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(valid_extensions)]
        
        if not images:
            raise Exception("Images folder mein koi VALID image file nahi bachi hai!")
            
        selected_image = random.choice(images)
        image_path = os.path.join(IMAGE_FOLDER, selected_image)
        
        print(f"File selected: {selected_image}. Starting upload process...")
        final_image_url = upload_with_fallback(image_path)
        print(f"✅ Upload Successful! Image URL: {final_image_url}")
        
        print("Sending Data to Make Webhook...")
        send_to_webhook(final_image_url, title, hashtag)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        history["titles"][title] = today_str
        history["hashtags"][hashtag] = today_str
        save_history(history)
        
        os.remove(image_path)
        print(f"Image {selected_image} successfully deleted from local folder.")
        
        host_name = final_image_url.split('/')[2] if '/' in final_image_url else "Unknown"
        send_telegram_log(status="success", host_used=host_name)
        
    except Exception as e:
        print(f"Error occurred: {e}")
        send_telegram_log(status="error", error_message=str(e))

if __name__ == "__main__":
    daily_job()
