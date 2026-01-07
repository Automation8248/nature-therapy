import os
import requests
import random
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
    """Fetches unique nature video and its tags"""
    used_ids = load_history()
    page = random.randint(1, 20)
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q=nature&per_page=10&page={page}"
    response = requests.get(url).json()
    hits = response.get('hits', [])
    
    selected_video = None
    
    # Unique video dhoondo
    for video in hits:
        if str(video['id']) not in used_ids:
            selected_video = video
            break
            
    if not selected_video:
        print("Warning: Repeats possible, picking random.")
        selected_video = random.choice(hits)

    save_history(selected_video['id'])
    
    # Video details extract karo
    tags = selected_video.get('tags', 'nature, beauty') # Tags: "forest, trees, green"
    download_url = selected_video['videos']['large']['url']
    
    print(f"Downloading video ID: {selected_video['id']}...")
    v_content = requests.get(download_url).content
    with open("input_video.mp4", "wb") as f:
        f.write(v_content)
    
    return "input_video.mp4", tags

def get_nature_audio():
    url = f"https://freesound.org/apiv2/search/text/?query=nature&fields=id,name,previews&token={FREESOUND_KEY}&filter=duration:[10 TO 60]"
    response = requests.get(url).json()
    results = response.get('results', [])
    
    if not results:
        raise Exception("No audio found.")
    
    audio_data = random.choice(results)
    download_url = audio_data['previews']['preview-hq-mp3']
    
    print(f"Downloading audio: {audio_data['name']}...")
    a_content = requests.get(download_url).content
    with open("input_audio.mp3", "wb") as f:
        f.write(a_content)
    return "input_audio.mp3"

def process_media(video_path, audio_path):
    print("Processing (Trim 7-8s)...")
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)

    target_duration = 7.5
    if video_clip.duration < 7:
         target_duration = video_clip.duration
    
    final_video = video_clip.subclip(0, target_duration)
    
    if audio_clip.duration < target_duration:
        from moviepy.audio.fx.all import audio_loop
        final_audio = audio_loop(audio_clip, duration=target_duration)
    else:
        final_audio = audio_clip.subclip(0, target_duration)

    final_clip = final_video.set_audio(final_audio)
    output_filename = "final_output.mp4"
    final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", threads=4, preset='ultrafast')
    
    return output_filename

def upload_to_catbox(file_path):
    print("Uploading to Catbox...")
    url = "https://catbox.moe/user/api.php"
    with open(file_path, "rb") as f:
        payload = {'reqtype': 'fileupload'}
        files = {'fileToUpload': f}
        response = requests.post(url, data=payload, files=files)
    return response.text

def generate_smart_caption(tags_string):
    """Generates Title (<50 chars) and exactly 8 Hashtags"""
    
    # 1. Tags ko list mein convert karo
    tags = [t.strip() for t in tags_string.split(',')]
    main_tag = tags[0].title() if tags else "Nature"
    secondary_tag = tags[1].title() if len(tags) > 1 else "Peace"

    # 2. Dynamic Title Templates (Max 50 Chars logic)
    titles = [
        f"Beautiful {main_tag} Vibes",
        f"Relaxing with {main_tag} & {secondary_tag}",
        f"Daily Dose of {main_tag}",
        f"Nature's Beauty: {main_tag}",
        f"Peaceful {main_tag} Moment",
        f"Just {main_tag} & {secondary_tag}",
        f"Serene {main_tag} Scenery"
    ]
    
    selected_title = random.choice(titles)
    # Safety cut ensure karo (Max 50 chars)
    if len(selected_title) > 50:
        selected_title = selected_title[:47] + "..."

    # 3. Exactly 8 Hashtags Logic
    # Pool of generic hashtags
    generic_hashtags = ["#nature", "#earth", "#wildlife", "#peace", "#travel", "#explore", "#reels", "#daily", "#calm", "#green", "#outdoor"]
    
    # Video specific hashtags banalo
    video_hashtags = [f"#{t.replace(' ', '')}" for t in tags]
    
    # Dono lists ko milao aur duplicates hatao
    all_tags_pool = list(set(video_hashtags + generic_hashtags))
    
    # Agar 8 se kam hain toh generic repeat mat karo, bas utne lo. 
    # Agar zyada hain to random 8 pick karo.
    if len(all_tags_pool) >= 8:
        final_tags = random.sample(all_tags_pool, 8)
    else:
        # Fallback agar tags kam pad gaye
        final_tags = all_tags_pool + random.sample(generic_hashtags, 8 - len(all_tags_pool))
        
    tags_string = " ".join(final_tags)
    
    return selected_title, tags_string

def send_notifications(video_url, title, hashtags):
    # Caption Format
    full_message = f"{title}\n\n{video_url}\n\n{hashtags}"
    
    print(f"Sending Message:\n{full_message}")
    
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      json={"chat_id": TELEGRAM_CHAT_ID, "text": full_message})

    if WEBHOOK_URL:
        # Webhook ke liye structured data bhej sakte hain
        requests.post(WEBHOOK_URL, json={
            "content": full_message,
            "title": title,
            "url": video_url,
            "hashtags": hashtags
        })

if __name__ == "__main__":
    try:
        v_path, v_tags = get_nature_video() # Tags bhi fetch kiye
        a_path = get_nature_audio()
        final_video = process_media(v_path, a_path)
        catbox_url = upload_to_catbox(final_video)
        
        # Caption Generate
        title, hashtags = generate_smart_caption(v_tags)
        
        send_notifications(catbox_url, title, hashtags)
        print("Workflow Completed Successfully!")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
