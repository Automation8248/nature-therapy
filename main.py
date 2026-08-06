import os
import random
import time
import json
import requests
import sys

# -------------------------------------------------------------
# 1. SECRETS & VARIABLES
# -------------------------------------------------------------
AUTOMATION_NAME = "TensorArt Image Poster"
SOCIAL_MEDIA_NAME = "Make.com (Instagram/Facebook)"
COOLDOWN_DAYS = 30
COOLDOWN_SECONDS = COOLDOWN_DAYS * 24 * 60 * 60

TENSORART_API_KEY = os.environ.get("TENSORART_API_KEY")
MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL")

SUCCESS_BOT_TOKEN = os.environ.get("TELEGRAM_SUCCESS_BOT_TOKEN")
SUCCESS_CHAT_ID = os.environ.get("TELEGRAM_SUCCESS_CHAT_ID")
ERROR_BOT_TOKEN = os.environ.get("TELEGRAM_ERROR_BOT_TOKEN")
ERROR_CHAT_ID = os.environ.get("TELEGRAM_ERROR_CHAT_ID")

HISTORY_FILE = "data/history.json"

# -------------------------------------------------------------
# 2. 50+ USER AGENTS LIST
# -------------------------------------------------------------
USER_AGENTS = [
    # Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Mac OS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/105.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/105.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Vivaldi/6.5.3206.50",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Android (Mobile)
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; M2101K6G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 13; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
    "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 EdgA/120.0.0.0",
    "Mozilla/5.0 (Linux; Android 12; V2111) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; 22101316G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; vivo 1920) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    # iOS (iPhone/iPad)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_7_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/121.0 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/120.0.2210.150 Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1"
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
        f"🌐 <b>Platform:</b> {SOCIAL_MEDIA_NAME}\n"
        f"❌ <b>Error:</b> {error_detail}"
    )
    url = f"https://api.telegram.org/bot{ERROR_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": ERROR_CHAT_ID, "text": error_msg, "parse_mode": "HTML"}
    requests.post(url, json=payload)
    sys.exit(1)

# -------------------------------------------------------------
# 4. 30-DAY COOLDOWN LOGIC (NEW)
# -------------------------------------------------------------
def load_history():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(HISTORY_FILE):
        return {"prompts": {}, "titles": {}, "hashtags": {}}
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_history(history_data):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history_data, f, indent=4)

def get_available_item(category_name, file_path, history_data):
    """File padhega, history check karega, aur sirf fresh items dega"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            all_items = [line.strip() for line in file.readlines() if line.strip()]
    except Exception as e:
        trigger_error_alert(f"Failed to read {file_path}: {e}")

    current_time = time.time()
    available_items = []

    for item in all_items:
        # Check if item is in history
        if item in history_data[category_name]:
            last_used_time = history_data[category_name][item]
            # Agar 30 din (COOLDOWN_SECONDS) nahi hue hain, toh skip kardo
            if (current_time - last_used_time) < COOLDOWN_SECONDS:
                continue
        # Agar item history me nahi hai ya 30 din poore ho gaye, toh list me daal do
        available_items.append(item)

    if not available_items:
        trigger_error_alert(f"All items in {category_name} are on 30-day cooldown! Please add more items to {file_path}.")

    # Ek fresh item randomly choose karo
    selected_item = random.choice(available_items)
    return selected_item

# -------------------------------------------------------------
# 5. TENSORART IMAGE GENERATION (UPDATED WORKFLOW API)
# -------------------------------------------------------------
def generate_image_tensorart(prompt):
    print(f"Generating image for prompt: {prompt}")
    
    # Naya API Endpoint
    url = "https://ap-east-1.tensorart.cloud/v1/jobs/workflow/template"
    
    headers = {
        "Authorization": f"Bearer {TENSORART_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Updated Payload Structure
    payload = {
        "templateId": "799541882207328343",
        "fields": {
            "fieldAttrs": [
                {
                    "nodeId": "30",
                    "fieldName": "ckpt_name",
                    "fieldValue": "757279507095956705"
                },
                # ⚠️ IMPORTANT: Yahan par apne prompt block ka nodeId aur fieldName update karein
                {
                    "nodeId": "string", # Example: "6" 
                    "fieldName": "string", # Example: "text" ya "positive_prompt"
                    "fieldValue": "any"
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
             trigger_error_alert(f"TensorArt Error: {response.status_code} - {response.text}")
             return None
             
        job_id = response.json().get('job_id')
        
        if not job_id: 
            trigger_error_alert("Failed to get Job ID from TensorArt API")
            return None
             
        print(f"Job created: {job_id}. Waiting for completion...")
        
        # Naya Polling URL
        status_url = f"https://ap-east-1.tensorart.cloud/v1/jobs/{job_id}"
        
        for i in range(30):
            time.sleep(10) 
            status_response = requests.get(status_url, headers=headers)
            status_data = status_response.json()
            
            if status_data.get('status') == 'SUCCESS':
                image_url = status_data['successInfo']['images'][0]['url']
                local_filename = "generated_img.jpg"
                img_data = requests.get(image_url).content
                with open(local_filename, 'wb') as handler:
                    handler.write(img_data)
                return local_filename
                
            elif status_data.get('status') == 'FAILED':
                trigger_error_alert("TensorArt Job Failed internally")
                return None
            
        trigger_error_alert("Timeout: Image took too long to generate (more than 5 mins)")
        return None
        
    except Exception as e:
        trigger_error_alert(f"TensorArt API Connection Failed: {e}")
        return None

# -------------------------------------------------------------
# 6. MULTI-HOST FALLBACK UPLOAD
# -------------------------------------------------------------
def upload_file_with_fallback(file_path):
    filename = os.path.basename(file_path)
    upload_strategies = [
        ("Catbox", lambda: requests.post("https://catbox.moe/user/api.php", data={'reqtype': 'fileupload'}, files={'fileToUpload': open(file_path, 'rb')}, headers=get_headers(), timeout=30).text),
        ("Litterbox", lambda: requests.post("https://litterbox.catbox.moe/resources/internals/api.php", data={'reqtype': 'fileupload', 'time': '72h'}, files={'fileToUpload': open(file_path, 'rb')}, headers=get_headers(), timeout=30).text),
        ("0x0.st", lambda: requests.post("https://0x0.st", files={'file': open(file_path, 'rb')}, headers=get_headers(), timeout=30).text.strip()),
        ("Transfer.sh", lambda: requests.put(f"https://transfer.sh/{filename}", data=open(file_path, 'rb'), headers=get_headers(), timeout=30).text.strip()),
        ("Uguu.se", lambda: requests.post("https://uguu.se/upload.php", files={'files[]': open(file_path, 'rb')}, headers=get_headers(), timeout=30).json()['files'][0]['url']),
        ("Tmpfiles.org", lambda: requests.post("https://tmpfiles.org/api/v1/upload", files={'file': open(file_path, 'rb')}, headers=get_headers(), timeout=30).json()['data']['url'].replace('tmpfiles.org/', 'tmpfiles.org/dl/')),
        ("Pomf.lain.la", lambda: requests.post("https://pomf.lain.la/upload.php", files={'files[]': open(file_path, 'rb')}, headers=get_headers(), timeout=30).json()['files'][0]['url']),
        ("Temp.sh", lambda: requests.put(f"https://temp.sh/{filename}", data=open(file_path, 'rb'), headers=get_headers(), timeout=30).text.strip()),
        ("Bashupload", lambda: requests.put(f"https://bashupload.com/{filename}", data=open(file_path, 'rb'), headers=get_headers(), timeout=30).text.split('wget ')[1].split('\n')[0].strip()),
        ("File.io", lambda: requests.post("https://file.io", files={'file': open(file_path, 'rb')}, headers=get_headers(), timeout=30).json()['link'])
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
            print(f"❌ Failed on {provider_name}: {str(e)[:50]}...")
            time.sleep(2) 
            
    trigger_error_alert("All Image Hosting Providers Failed. Unable to upload the generated image.")
    return None

# -------------------------------------------------------------
# 7. MAKE.COM WEBHOOK
# -------------------------------------------------------------
def send_to_make_webhook(title, hashtags, image_url):
    print("Sending data to Make.com Webhook...")
    payload = {"title": title, "hashtags": hashtags, "image_url": image_url}
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
    print("Starting Automation Workflow with 30-Day Cooldown...")
    
    # Step 1: Load History
    history_data = load_history()

    # Step 2: Get Fresh Items (jo 30 din me use nahi hue)
    prompt = get_available_item("prompts", "data/prompts.txt", history_data)
    title = get_available_item("titles", "data/titles.txt", history_data)
    hashtags = get_available_item("hashtags", "data/hashtags.txt", history_data)
    
    # Step 3: Generate
    image_path = generate_image_tensorart(prompt)

    # Step 4: Upload
    final_image_url = upload_file_with_fallback(image_path)

    # Step 5: Webhook to Make.com
    send_to_make_webhook(title, hashtags, final_image_url)
    
    # Step 6: Sab success hone ke baad history update karna
    current_time = time.time()
    history_data["prompts"][prompt] = current_time
    history_data["titles"][title] = current_time
    history_data["hashtags"][hashtags] = current_time
    save_history(history_data)
    
    # Step 7: Success Notification
    host_domain = final_image_url.split('/')[2] if '/' in final_image_url else "Unknown Host"
    success_msg = f"✅ <b>Post Successfully Uploaded!</b>\n\n🌐 <b>Platform:</b> {SOCIAL_MEDIA_NAME}\n🖼️ <b>Host:</b> {host_domain}\n📝 <b>Title:</b> {title}"
    
    if SUCCESS_BOT_TOKEN and SUCCESS_CHAT_ID:
        url = f"https://api.telegram.org/bot{SUCCESS_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": SUCCESS_CHAT_ID, "text": success_msg, "parse_mode": "HTML"}
        requests.post(url, json=payload)
        
    print("Workflow completed successfully. History updated for next run.")

if __name__ == "__main__":
    main()
