import os
import requests
import random
import json
from moviepy.editor import VideoFileClip, AudioFileClip

# --- SETTINGS ---
PIXABAY_KEY = os.getenv('PIXABAY_KEY')
FREESOUND_KEY = os.getenv('FREESOUND_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

def get_video():
    print(">>> Step 1: Video download...")
    v_url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q=nature&per_page=5"
    res = requests.get(v_url).json()['hits'][0]
    with open("v.mp4", "wb") as f: f.write(requests.get(res['videos']['large']['url']).content)
    return "v.mp4", res.get('tags', 'nature')

def process(v):
    print(">>> Step 2: Editing...")
    clip = VideoFileClip(v).subclip(0, 7.5)
    # 9:16 Crop logic
    if clip.w > clip.h:
        new_w = int(clip.h * (9/16))
        clip = clip.crop(x1=clip.w/2 - new_w/2, width=new_w, height=clip.h)
    clip.resize(height=1280).write_videofile("final.mp4", codec="libx264", audio_codec="aac", fps=24, preset='ultrafast')
    return "final.mp4"

def upload_and_post(file, tags):
    print(">>> Step 3: Sending results...")
    
    # Generate Caption
    caption = f"Nature Beauty 🌿\n\n#nature #peace #forest"

    # 1. Catbox Upload (Yahan URL generate hota hai)
    with open(file, "rb") as f:
        upload_res = requests.post("https://catbox.moe/user/api.php", data={'reqtype': 'fileupload'}, files={'fileToUpload': f})
        video_url = upload_res.text.strip()
    
    # --- CRITICAL LOG ---
    print(f"✅ VIDEO URL GENERATED: {video_url}")

    # 2. Webhook Send (JSON Format)
    if WEBHOOK_URL and "https://" in video_url:
        payload = {"video_url": video_url, "caption": caption}
        headers = {'Content-Type': 'application/json'}
        r = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        print(f">>> Webhook Status: {r.status_code}")
    else:
        print("❌ URL missing, Webhook skip kiya gaya.")

    # 3. Telegram Send (File)
    if TELEGRAM_TOKEN:
        with open(file, 'rb') as f:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo", files={'video': f}, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption})

if __name__ == "__main__":
    v_file, tags = get_video()
    final_v = process(v_file)
    upload_and_post(final_v, tags)
    print("SUCCESS!")
