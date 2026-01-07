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
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return f.read().splitlines()

def save_history(video_id):
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{str(video_id)}\n")

def get_nature_video():
    print(">>> Step 1: Video download kar rahe hain...")
    used_ids = load_history()
    page = random.randint(1, 20)
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q=nature&per_page=10&page={page}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        hits = response.json().get('hits', [])
    except Exception as e:
        raise Exception(f"Pixabay Error: {e}")
    
    selected_video = None
    for video in hits:
        if str(video['id']) not in used_ids:
            selected_video = video
            break
            
    if not selected_video:
        if not hits: raise Exception("Pixabay par koi video nahi mila.")
        selected_video = random.choice(hits)

    save_history(selected_video['id'])
    tags = selected_video.get('tags', 'nature')
    download_url = selected_video['videos']['large']['url']
    
    v_content = requests.get(download_url).content
    with open("input_video.mp4", "wb") as f:
        f.write(v_content)
    
    return "input_video.mp4", tags

def get_nature_audio():
    print(">>> Step 2: Audio download kar rahe hain...")
    url = f"https://freesound.org/apiv2/search/text/?query=nature&fields=id,name,previews&token={FREESOUND_KEY}&filter=duration:[10 TO 60]"
    try:
        response = requests.get(url)
        results = response.json().get('results', [])
    except:
        return None 
    
    if not results: return None
    
    audio_data = random.choice(results)
    download_url = audio_data['previews']['preview-hq-mp3']
    
    a_content = requests.get(download_url).content
    with open("input_audio.mp3", "wb") as f:
        f.write(a_content)
    return "input_audio.mp3"

def process_media(video_path, audio_path):
    print(">>> Step 3: Video edit kar rahe hain (Shorts format)...")
    video_clip = VideoFileClip(video_path)
    
    target_duration = 7.5
    if video_clip.duration < 7: target_duration = video_clip.duration
    
    # 9:16 Crop Logic
    target_ratio = 9/16
    current_ratio = video_clip.w / video_clip.h

    if current_ratio > target_ratio:
        new_width = int(video_clip.h * target_ratio)
        center_x = video_clip.w / 2
        video_clip = video_clip.crop(x1=center_x - (new_width/2), y1=0, width=new_width, height=video_clip.h)
    
    video_clip = video_clip.resize(height=1280)
    final_video = video_clip.subclip(0, target_duration)
    
    if audio_path:
        audio_clip = AudioFileClip(audio_path)
        if audio_clip.duration < target_duration:
            from moviepy.audio.fx.all import audio_loop
            final_audio = audio_loop(audio_clip, duration=target_duration)
        else:
            final_audio = audio_clip.subclip(0, target_duration)
        final_clip = final_video.set_audio(final_audio)
    else:
        final_clip = final_video
    
    output_filename = "final_output.mp4"
    final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", threads=4, preset='ultrafast')
    
    return output_filename

def generate_caption(tags_string):
    raw_tags = [t.strip() for t in tags_string.split(',')]
    main_subject = raw_tags[0].title() if raw_tags else "Nature"
    
    titles = [f"Relaxing {main_subject} 🌿", f"Pure {main_subject} Vibes ✨", f"Nature: {main_subject} 🌍"]
    title_text = random.choice(titles)
    
    nature_keywords = ["#nature", "#wildlife", "#forest", "#mountains", "#rain", "#sky", "#trees", "#green"]
    video_specific = [f"#{t.replace(' ', '')}" for t in raw_tags if t.replace(' ', '').isalpha()]
    
    pool = list(set(video_specific + nature_keywords))
    final_tags = random.sample(pool, min(8, len(pool)))
    
    return f"{title_text}\n\n{' '.join(final_tags)}"

def upload_to_catbox(file_path):
    print(">>> Step 4: Video Upload kar rahe hain (Catbox)...")
    url = "https://catbox.moe/user/api.php"
    
    if not os.path.exists(file_path):
        raise Exception("Video file nahi mili!")

    try:
        with open(file_path, "rb") as f:
            payload = {'reqtype': 'fileupload'}
            files = {'fileToUpload': f}
            response = requests.post(url, data=payload, files=files)
            
            if response.status_code == 200:
                result_url = response.text.strip()
                # LOG MEIN URL PRINT KARENGE
                print(f"\n==========================================")
                print(f"✅ VIDEO URL GENERATED: {result_url}")
                print(f"==========================================\n")
                return result_url
            else:
                raise Exception(f"Catbox Fail hua: {response.text}")
    except Exception as e:
        raise Exception(f"Catbox Error: {e}")

def send_webhook_json(url, caption, webhook_url):
    print(f">>> Step 5: Webhook par URL bhej rahe hain...")
    
    # JSON Payload Structure
    payload = {
        "video_url": url,
        "caption": caption,
        "status": "success"
    }
    
    # Headers zaroori hain taaki Make.com isse JSON samjhe
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        print(f"Webhook Status Code: {response.status_code}")
        print(f"Webhook Response: {response.text}")
    except Exception as e:
        print(f"Webhook Error: {e}")

def send_telegram_file(file_path, caption):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        print(">>> Telegram par File bhej rahe hain...")
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
        with open(file_path, 'rb') as f:
            files = {'video': ('nature_shorts.mp4', f, 'video/mp4')}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            requests.post(url, files=files, data=data)

if __name__ == "__main__":
    try:
        v_path, v_tags = get_nature_video()
        a_path = get_nature_audio()
        final_video = process_media(v_path, a_path)
        full_caption = generate_caption(v_tags)
        
        # 1. Telegram (File)
        send_telegram_file(final_video, full_caption)

        # 2. Webhook (URL) - Yeh sabse important part hai
        if WEBHOOK_URL:
            video_url = upload_to_catbox(final_video) # URL Generate
            if video_url:
                send_webhook_json(video_url, full_caption, WEBHOOK_URL)
            else:
                print("❌ URL Generate nahi hua, Webhook skip kar rahe hain.")
        
        print("Workflow Complete!")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        exit(1)
