import os
import random
import time
import json
import requests
import sys
import glob
import shutil
from icrawler.builtin import BingImageCrawler

# -------------------------------------------------------------
# 1. SECRETS & VARIABLES
# -------------------------------------------------------------
AUTOMATION_NAME = "Nature Crawler Poster"
SOCIAL_MEDIA_NAME = "Make.com (Instagram/Facebook)"
COOLDOWN_DAYS = 30
COOLDOWN_SECONDS = COOLDOWN_DAYS * 24 * 60 * 60

MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL")

SUCCESS_BOT_TOKEN = os.environ.get("TELEGRAM_SUCCESS_BOT_TOKEN")
SUCCESS_CHAT_ID = os.environ.get("TELEGRAM_SUCCESS_CHAT_ID")
ERROR_BOT_TOKEN = os.environ.get("TELEGRAM_ERROR_BOT_TOKEN")
ERROR_CHAT_ID = os.environ.get("TELEGRAM_ERROR_CHAT_ID")

HISTORY_FILE = "data/history.json"

# -------------------------------------------------------------
# 2. USER AGENTS (For Fallback Uploads)
# -------------------------------------------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

# -------------------------------------------------------------
# 3. TELEGRAM ALERTS
# -------------------------------------------------------------
def trigger_error_alert(error_detail):
    print(f"ERROR: {error_detail}")
    if not ERROR_BOT_TOKEN or not ERROR_CHAT_ID:
        sys.exit(1)
        
    error_msg = (
        f"🚨 <b>AUTOMATION FAILED!</b>\n\n"
        f"🤖 <b>Bot Name:</b> {AUTOMATION_NAME}\n"
        f"❌ <b>Error:</b> {error_detail}"
    )
    url = f"https://api.telegram.org/bot{ERROR_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": ERROR_CHAT_ID, "text": error_msg, "parse_mode": "HTML"})
    sys.exit(1)

# -------------------------------------------------------------
# 4. 30-DAY COOLDOWN LOGIC
# -------------------------------------------------------------
def load_history():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(HISTORY_FILE):
        return {"titles": {}, "hashtags": {}} # Removed prompts
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_history(history_data):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history_data, f, indent=4)

def get_available_item(category_name, file_path, history_data):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            all_items = [line.strip() for line in file.readlines() if line.strip()]
    except Exception as e:
        trigger_error_alert(f"Failed to read {file_path}: {e}")

    current_time = time.time()
    available_items = []

    for item in all_items:
        if item in history_data[category_name]:
            last_used_time = history_data[category_name][item]
            if (current_time - last_used_time) < COOLDOWN_SECONDS:
                continue
        available_items.append(item)

    if not available_items:
        trigger_error_alert(f"All items in {category_name} are on 30-day cooldown! Please add more.")

    return random.choice(available_items)

# -------------------------------------------------------------
# 5. ICRAWLER: BING IMAGE DOWNLOAD
# -------------------------------------------------------------
def download_image_from_bing():
    # Fix keyword as requested, no prompt used
    keyword = "Natural Nature image" 
    print(f"Searching and downloading image for topic: {keyword}")
    
    folder_name = f'image/{keyword.replace(" ",".")}'
    
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name, exist_ok=True)
    
    try:
        bing_crawler = BingImageCrawler(storage={'root_dir': folder_name})
        bing_crawler.crawl(keyword=keyword, filters=None, max_num=1, offset=0)
        
        downloaded_files = glob.glob(f"{folder_name}/*")
        
        if not downloaded_files:
            trigger_error_alert(f"No image downloaded by Bing Crawler for keyword: {keyword}")
            return None
            
        print(f"Image successfully downloaded: {downloaded_files[0]}")
        return downloaded_files[0]
        
    except Exception as e:
        trigger_error_alert(f"iCrawler Error: {e}")
        return None

# -------------------------------------------------------------
# 6. MULTI-HOST FALLBACK UPLOAD
# -------------------------------------------------------------
def upload_file_with_fallback(file_path):
    filename = os.path.basename(file_path)
    print(f"Uploading file: {filename}")
    
    upload_strategies = [
        ("Catbox", lambda: requests.post("https://catbox.moe/user/api.php", data={'reqtype': 'fileupload'}, files={'fileToUpload': open(file_path, 'rb')}, headers=get_headers(), timeout=30).text),
        ("Litterbox", lambda: requests.post("https://litterbox.catbox.moe/resources/internals/api.php", data={'reqtype': 'fileupload', 'time': '72h'}, files={'fileToUpload': open(file_path, 'rb')}, headers=get_headers(), timeout=30).text),
        ("0x0.st", lambda: requests.post("https://0x0.st", files={'file': open(file_path, 'rb')}, headers=get_headers(), timeout=30).text.strip()),
        ("Uguu.se", lambda: requests.post("https://uguu.se/upload.php", files={'files[]': open(file_path, 'rb')}, headers=get_headers(), timeout=30).json()['files'][0]['url'])
    ]

    random.shuffle(upload_strategies)

    for i, (provider_name, upload_func) in enumerate(upload_strategies):
        print(f"[{i+1}/{len(upload_strategies)}] Trying to upload via {provider_name}...")
        try:
            upload_url = upload_func()
            if upload_url and upload_url.startswith("http"):
                print(f"✅ Upload successful on {provider_name}")
                return upload_url
        except Exception as e:
            print(f"❌ Failed on {provider_name}")
            time.sleep(2) 
            
    trigger_error_alert("All Image Hosting Providers Failed. Unable to upload the downloaded image.")
    return None

# -------------------------------------------------------------
# 7. MAKE.COM WEBHOOK
# -------------------------------------------------------------
def send_to_make_webhook(title, hashtags, media_url): # Changed image_url to media_url
    print("Sending data to Make.com Webhook...")
    # Updated payload keys as requested
    payload = {"title": title, "hashtags": hashtags, "media_url": media_url}
    try:
        response = requests.post(MAKE_WEBHOOK_URL, json=payload, headers=get_headers())
        response.raise_for_status()
        return True
    except Exception as e:
        trigger_error_alert(f"Make.com Webhook Failed: {e}")

# -------------------------------------------------------------
# 8. MAIN EXECUTION
# -------------------------------------------------------------
def main():
    print("Starting Nature Crawler Workflow with 30-Day Cooldown...")
    
    # 1. Load History & Get Data
    history_data = load_history()
    
    # Initialize missing keys if needed
    if "titles" not in history_data:
        history_data["titles"] = {}
    if "hashtags" not in history_data:
        history_data["hashtags"] = {}
        
    title = get_available_item("titles", "data/titles.txt", history_data)
    hashtags = get_available_item("hashtags", "data/hashtags.txt", history_data)
    
    # 2. Bing Se Download Karo (Prompt nahi use hoga, fixed topic use hoga)
    image_path = download_image_from_bing()
    
    # 3. Downloaded Image Ko Catbox/0x0 Par Upload Karo
    final_media_url = upload_file_with_fallback(image_path)
    
    # 4. Webhook to Make.com
    send_to_make_webhook(title, hashtags, final_media_url)
    
    # 5. History Update Karo
    current_time = time.time()
    history_data["titles"][title] = current_time
    history_data["hashtags"][hashtags] = current_time
    save_history(history_data)
    
    # 6. Success Notification
    host_domain = final_media_url.split('/')[2] if '/' in final_media_url else "Unknown Host"
    success_msg = f"✅ <b>Post Successfully Uploaded!</b>\n\n🌐 <b>Topic:</b> Natural Nature image\n🖼️ <b>Host:</b> {host_domain}\n📝 <b>Title:</b> {title}"
    
    if SUCCESS_BOT_TOKEN and SUCCESS_CHAT_ID:
        url = f"https://api.telegram.org/bot{SUCCESS_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": SUCCESS_CHAT_ID, "text": success_msg, "parse_mode": "HTML"})
        
    print("Workflow completed successfully. History updated for next run.")

if __name__ == "__main__":
    main()
