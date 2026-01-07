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
    v_url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q=nature&per_page=5"
    res = requests.get(v_url).json()['hits'][0]
    with open("v.mp4", "wb") as f: f.write(requests.get(res['videos']['large']['url']).content)
    return "v.mp4", res.get('tags', 'nature')

def process(v):
    clip = VideoFileClip(v).subclip(0, 7.5)
    if clip.w > clip.h:
        new_w = int(clip.h * (9/16))
        clip = clip.crop(x1=clip.w/2 - new_w/2, width=new_w, height=clip.h)
    clip.resize(height=1280).write_videofile("final.mp4", codec="libx264", audio_codec="aac", fps=24, preset='ultrafast')
    return "final.mp4"

def send_data(file, tags):
    caption = f"Nature Vibes 🌿\n\n#nature #forest"

    # 1. Catbox Upload (URL banane ke liye)
    with open(file, "rb") as f:
        res = requests.post("https://catbox.moe/user/api.php", data={'reqtype': 'fileupload'}, files={'fileToUpload': f})
        video_url = res.text.strip()
    
    # Check karein ki URL bana ya nahi
    print(f"✅ VIDEO URL GENERATED: {video_url}")

    # 2. Webhook (Sirf URL bhej raha hai)
    if WEBHOOK_URL and "https://" in video_url:
        payload = {
            "video_url": video_url,
            "caption": caption
        }
        # JSON format ensure karta hai ki Make.com link ko pakad le
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f">>> Webhook Status: {response.status_code}")
    
    # 3. Telegram (Hamesha ki tarah file bhejega)
    with open(file, 'rb') as f:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo", files={'video': f}, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption})

if __name__ == "__main__":
    v_f, t = get_video()
    final = process(v_f)
    send_data(final, t)
