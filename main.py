import os
import requests
import random
import json
import time
from moviepy.editor import VideoFileClip, AudioFileClip

# --- CONFIGURATION ---
PIXABAY_KEY = os.getenv('PIXABAY_KEY')
FREESOUND_KEY = os.getenv('FREESOUND_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
HISTORY_FILE = "history.txt"

def load_history():
    if not os.path.exists(HISTORY_FILE): return []
    with open(HISTORY_FILE, "r") as f: return f.read().splitlines()

def save_history(video_id):
    with open(HISTORY_FILE, "a") as f: f.write(f"{str(video_id)}\n")

# 1. DOWNLOAD CONTENT
def get_content():
    print(">>> STEP 1: Content Download...")
    # Video
    used_ids = load_history()
    page = random.randint(1, 10)
    v_url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q=nature&per_page=10&page={page}"
    try:
        hits = requests.get(v_url).json().get('hits', [])
        video = next((v for v in hits if str(v['id']) not in used_ids), random.choice(hits) if hits else None)
        if not video: raise Exception("No Video Found")
        
        save_history(video['id'])
        v_data = requests.get(video['videos']['large']['url']).content
        with open("input_video.mp4", "wb") as f: f.write(v_data)
        tags = video.get('tags', 'nature')
    except Exception as e:
        raise Exception(f"Pixabay Error: {e}")

    # Audio
    try:
        a_url = f"https://freesound.org/apiv2/search/text/?query=nature&fields=id,name,previews&token={FREESOUND_KEY}&filter=duration:[10 TO 60]"
        results = requests.get(a_url).json().get('results', [])
        if results:
            a_data = requests.get(random.choice(results)['previews']['preview-hq-mp3']).content
            with open("input_audio.mp3", "wb") as f: f.write(a_data)
    except: pass # Audio fail ho to silent video chalega

    return "input_video.mp4", "input_audio.mp3" if os.path.exists("input_audio.mp3") else None, tags

# 2. EDIT VIDEO
def process_video(v_path, a_path):
    print(">>> STEP 2: Editing Video...")
    clip = VideoFileClip(v_path)
    
    # Duration & Crop
    duration = min(clip.duration, 7.5)
    
    # 9:16 Crop
    if clip.w > clip.h:
        new_w = int(clip.h * (9/16))
        clip = clip.crop(x1=clip.w/2 - new_w/2, width=new_w, height=clip.h)
    
    clip = clip.resize(height=1280).subclip(0, duration)
    
    if a_path:
        audio = AudioFileClip(a_path).subclip(0, duration)
        clip = clip.set_audio(audio)
        
    clip.write_videofile("final.mp4", codec="libx264", audio_codec="aac", threads=4, preset='ultrafast')
    return "final.mp4"

# 3. GENERATE CAPTION
def get_caption(tags):
    keywords = [t.strip().replace(" ", "") for t in tags.split(',')]
    safe_tags = [f"#{k}" for k in keywords if k.isalpha()]
    nature_tags = ["#nature", "#wildlife", "#green", "#peace", "#earth"]
    final_tags = random.sample(list(set(safe_tags + nature_tags)), min(8, len(safe_tags + nature_tags)))
    return f"Nature Vibes 🌿\n\n{' '.join(final_tags)}"

# 4. UPLOAD & SEND
def upload_and_send(file_path, caption):
    print(">>> STEP 3: Uploading & Sending...")
    
    # A. Telegram (File)
    if TELEGRAM_TOKEN:
        with open(file_path, 'rb') as f:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo",
                files={'video': f},
                data={'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            )
            print("✅ Telegram Sent")

    # B. Webhook (Link)
    if WEBHOOK_URL:
        # Upload to Catbox
        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    "https://catbox.moe/user/api.php",
                    data={'reqtype': 'fileupload'},
                    files={'fileToUpload': f}
                )
            
            if response.status_code == 200:
                video_url = response.text.strip()
                print(f"✅ Catbox URL: {video_url}")
                
                # Send JSON to Make.com
                payload = {"video_url": video_url, "caption": caption}
                r = requests.post(WEBHOOK_URL, json=payload)
                print(f"✅ Webhook Response: {r.status_code}")
            else:
                print(f"❌ Catbox Failed: {response.text}")
        except Exception as e:
            print(f"❌ Upload Error: {e}")

if __name__ == "__main__":
    try:
        v, a, t = get_content()
        final_video = process_video(v, a)
        caption_text = get_caption(t)
        upload_and_send(final_video, caption_text)
        print(">>> WORKFLOW COMPLETED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        exit(1)
