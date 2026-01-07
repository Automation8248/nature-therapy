import os
import requests
import random
import time
import json
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
    print("--- Step 1: Fetching Video ---")
    used_ids = load_history()
    page = random.randint(1, 20)
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q=nature&per_page=10&page={page}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        hits = data.get('hits', [])
    except Exception as e:
        raise Exception(f"Pixabay API Error: {e}")
    
    selected_video = None
    for video in hits:
        if str(video['id']) not in used_ids:
            selected_video = video
            break
            
    if not selected_video and hits:
        selected_video = random.choice(hits)
    elif not hits:
        raise Exception("No videos found on Pixabay.")

    save_history(selected_video['id'])
    tags = selected_video.get('tags', 'nature')
    download_url = selected_video['videos']['large']['url']
    
    print(f"Downloading Video ID: {selected_video['id']}")
    v_content = requests.get(download_url).content
    with open("input_video.mp4", "wb") as f:
        f.write(v_content)
    
    return "input_video.mp4", tags

def get_nature_audio():
    print("--- Step 2: Fetching Audio ---")
    url = f"https://freesound.org/apiv2/search/text/?query=nature&fields=id,name,previews&token={FREESOUND_KEY}&filter=duration:[10 TO 60]"
    try:
        response = requests.get(url)
        data = response.json()
        results = data.get('results', [])
    except Exception as e:
        print(f"Freesound API Error: {e}")
        return None # Handle gracefully
    
    if not results:
        raise Exception("No audio found on Freesound.")
    
    audio_data = random.choice(results)
    download_url = audio_data['previews']['preview-hq-mp3']
    
    print(f"Downloading Audio: {audio_data['name']}")
    a_content = requests.get(download_url).content
    with open("input_audio.mp3", "wb") as f:
        f.write(a_content)
    return "input_audio.mp3"

def process_media(video_path, audio_path):
    print("--- Step 3: Processing Media ---")
    video_clip = VideoFileClip(video_path)
    
    # Logic: 7.5s Duration & 9:16 Crop
    target_duration = 7.5
    if video_clip.duration < 7:
         target_duration = video_clip.duration
    
    # Crop to 9:16
    target_ratio = 9/16
    current_ratio = video_clip.w / video_clip.h

    if current_ratio > target_ratio:
        new_width = int(video_clip.h * target_ratio)
        center_x = video_clip.w / 2
        video_clip = video_clip.crop(x1=center_x - (new_width/2), y1=0, width=new_width, height=video_clip.h)
    
    video_clip = video_clip.resize(height=1280)
    final_video = video_clip.subclip(0, target_duration)
    
    # Audio Logic
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
    # Uses 'ultrafast' preset for GitHub Actions speed
    final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", threads=4, preset='ultrafast')
    
    return output_filename

def generate_caption(tags_string):
    raw_tags = [t.strip() for t in tags_string.split(',')]
    main_subject = raw_tags[0].title() if raw_tags else "Nature"
    
    titles = [
        f"Relaxing {main_subject} Moments 🌿",
        f"Pure {main_subject} Vibes ✨",
        f"Nature's Beauty: {main_subject} 🌍",
        f"Serene {main_subject} View 🌧️"
    ]
    title_text = random.choice(titles)
    
    nature_keywords = [
        "#nature", "#naturelovers", "#wildlife", "#forest", "#mountains", 
        "#ocean", "#rain", "#sky", "#flowers", "#trees", 
        "#landscape", "#earth", "#river", "#green"
    ]
    
    video_specific = [f"#{t.replace(' ', '')}" for t in raw_tags if t.replace(' ', '').isalpha()]
    pool = list(set(video_specific + nature_keywords))
    final_tags = random.sample(pool, min(8, len(pool)))
    
    return f"{title_text}\n\n{' '.join(final_tags)}"

def upload_to_catbox(file_path):
    print("--- Step 4: Uploading to Catbox ---")
    url = "https://catbox.moe/user/api.php"
    
    if not os.path.exists(file_path):
        raise Exception("File not found to upload!")

    try:
        with open(file_path, "rb") as f:
            payload = {'reqtype': 'fileupload'}
            files = {'fileToUpload': f}
            response = requests.post(url, data=payload, files=files)
            
            if response.status_code == 200:
                result_url = response.text.strip()
                print(f"SUCCESS: Catbox URL generated: {result_url}")
                return result_url
            else:
                raise Exception(f"Catbox Upload Failed: {response.text}")
    except Exception as e:
        raise Exception(f"Catbox Connection Error: {e}")

def send_notifications(file_path, caption_text, video_url):
    print("--- Step 5: Sending Notifications ---")
    
    # 1. Telegram (Send FILE)
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        print(">> Sending File to Telegram...")
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
        with open(file_path, 'rb') as f:
            files = {'video': ('nature_shorts.mp4', f, 'video/mp4')}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption_text}
            requests.post(url, files=files, data=data)

    # 2. Webhook (Send URL + Caption)
    if WEBHOOK_URL:
        print(f">> Sending URL to Webhook: {WEBHOOK_URL}")
        
        # Strictly JSON Payload
        payload = {
            "video_url": video_url,
            "caption": caption_text,
            "status": "ready"
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            r = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)
            print(f"Webhook Response Code: {r.status_code}")
            print(f"Webhook Response Body: {r.text}")
            
            if r.status_code >= 400:
                print("!! WEBHOOK FAILED !! Check Make.com logs.")
        except Exception as e:
            print(f"Webhook Connection Error: {e}")

if __name__ == "__main__":
    try:
        v_path, v_tags = get_nature_video()
        a_path = get_nature_audio()
        final_video = process_media(v_path, a_path)
        full_caption = generate_caption(v_tags)
        
        # Critical Step: Get URL first
        catbox_url = upload_to_catbox(final_video)
        
        if catbox_url:
            send_notifications(final_video, full_caption, catbox_url)
        else:
            print("ERROR: Could not generate URL, skipping Webhook.")
            
        print("Workflow Completed Successfully!")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        exit(1)
