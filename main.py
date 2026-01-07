import os
import requests
import random
import json
import time

# --- MoviePy Fix ---
try:
    from moviepy.editor import VideoFileClip, AudioFileClip
except ImportError:
    print("❌ Error: MoviePy library properly install nahi hui. Check requirements.txt")
    exit(1)

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

# 1. CONTENT FETCHING
def get_content():
    print(">>> Step 1: Video aur Audio download ho raha hai...")
    used_ids = load_history()
    page = random.randint(1, 20)
    
    # Pixabay Video
    v_url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q=nature&per_page=10&page={page}"
    v_res = requests.get(v_url).json().get('hits', [])
    video = next((v for v in v_res if str(v['id']) not in used_ids), random.choice(v_res) if v_res else None)
    
    if not video: raise Exception("Pixabay video download fail.")
    save_history(video['id'])
    
    with open("in_v.mp4", "wb") as f: f.write(requests.get(video['videos']['large']['url']).content)
    
    # Freesound Audio
    try:
        a_url = f"https://freesound.org/apiv2/search/text/?query=nature&fields=id,previews&token={FREESOUND_KEY}&filter=duration:[10 TO 60]"
        a_res = requests.get(a_url).json().get('results', [])
        if a_res:
            with open("in_a.mp3", "wb") as f: f.write(requests.get(random.choice(a_res)['previews']['preview-hq-mp3']).content)
    except: print("Audio skip kiya gaya.")
    
    return "in_v.mp4", "in_a.mp3" if os.path.exists("in_a.mp3") else None, video.get('tags', 'nature')

# 2. VIDEO PROCESSING (9:16 Shorts)
def process_video(v, a):
    print(">>> Step 2: Video edit ho raha hai (Shorts format)...")
    clip = VideoFileClip(v)
    duration = min(clip.duration, 7.5)
    
    # Center Crop to 9:16
    if clip.w / clip.h > 9/16:
        new_w = int(clip.h * (9/16))
        clip = clip.crop(x1=clip.w/2 - new_w/2, width=new_w, height=clip.h)
    
    clip = clip.resize(height=1280).subclip(0, duration)
    if a:
        audio = AudioFileClip(a).subclip(0, duration)
        clip = clip.set_audio(audio)
        
    clip.write_videofile("out.mp4", codec="libx264", audio_codec="aac", threads=4, preset='ultrafast')
    return "out.mp4"

# 3. SMART CAPTION
def get_caption(tags):
    keywords = [t.strip().replace(" ", "") for t in tags.split(',')]
    pool = list(set(["#"+t for t in keywords if t.isalpha()] + ["#nature", "#forest", "#calm", "#earth"]))
    hashtags = " ".join(random.sample(pool, min(8, len(pool))))
    return f"Nature Peace 🌿\n\n{hashtags}"

# 4. DISTRIBUTION (TELEGRAM FILE + WEBHOOK URL)
def distribute(file, cap):
    print(">>> Step 3: Sending to Telegram aur Webhook...")
    
    # Telegram: Seed File
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        with open(file, 'rb') as f:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo", 
                          files={'video': f}, data={'chat_id': TELEGRAM_CHAT_ID, 'caption': cap})
        print("✅ Telegram Sent")

    # Webhook: Send URL
    if WEBHOOK_URL:
        # Upload to Catbox for link
        with open(file, "rb") as f:
            res = requests.post("https://catbox.moe/user/api.php", data={'reqtype': 'fileupload'}, files={'fileToUpload': f})
        
        if res.status_code == 200:
            v_url = res.text.strip()
            print(f"✅ Catbox URL: {v_url}")
            
            # Send exactly what Make.com needs
            payload = {"video_url": v_url, "caption": cap}
            headers = {'Content-Type': 'application/json'}
            requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)
            print("✅ Make.com Webhook Sent")
        else:
            print("❌ Catbox Upload Failed")

if __name__ == "__main__":
    try:
        v, a, t = get_content()
        final = process_video(v, a)
        caption = get_caption(t)
        distribute(final, caption)
        print("🎉 SUCCESS: Project Ready!")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
