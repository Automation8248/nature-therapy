import os
import json
import random
import requests
import datetime

# --- CONFIGURATION ---
VIDEO_FOLDER = "videos"
HISTORY_FILE = "history.json"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# Yahan maine image se dekh kar aapka exact Repo Name daal diya hai
GITHUB_REPO = "Automation8248/nature-therapy" 
BRANCH_NAME = "main"

# --- DATA GRID (Pre-saved Titles & Captions) ---

# List 1: Titles (Har bar inme se koi ek randomly select hoga)
TITLES_GRID = [
    "Nature Never Fails to Heal",
    "Peace Hidden in the Wild",
    "Where Silence Speaks",
    "The Earth Breathing Slowly",
    "Moments of Pure Nature",
    "Lost in Natural Beauty",
    "Nature's Calm Therapy",
    "The Language of the Earth",
    "Soul Resting in Nature",
    "Whispers of the Wilderness",
    "Serenity Beyond Words",
    "The Art of Nature",
    "Nature is the Best Escape",
    "A Walk Through Tranquility",
    "Feel the Earth Alive",
    "Nature's Gentle Magic",
    "Pure Peace, Pure Nature",
    "Wild Beauty Unfiltered",
    "The World Before Humans",
    "Harmony of the Planet",
    "Calmness in Every Corner",
    "The Rhythm of the Wild",
    "Nature Speaks Softly",
    "Life in Its Purest Form",
    "The Planet at Peace",
    "Earth’s Quiet Moments",
    "Timeless Beauty of Nature",
    "Nature’s Healing Energy",
    "Breathing With the Earth",
    "Stillness of the Natural World",
    "Wild Yet Peaceful",
    "Simple Beauty Everywhere",
    "A World Without Noise",
    "Nature Never Rushes",
    "Calm Beyond the City",
    "Untouched and Unbothered",
    "Beauty Without Effort",
    "The Soft Side of Earth",
    "Nature’s Daily Miracle",
    "Where Time Slows Down",
    "Peace Found Outdoors",
    "Nature's Gentle Flow",
    "Alive and Free",
    "The Quiet Planet",
    "Every Leaf Tells a Story",
    "Natural Wonders Around Us",
    "Rest Your Mind Here",
    "Beyond Human Chaos",
    "The Calm We Forget",
    "Nature’s Perfect Balance",
    "Relax Into the Wild",
    "Nothing But Nature",
    "Escape to Simplicity",
    "Earth’s Endless Beauty",
    "Feel the Freshness",
    "Moments Made by Nature",
    "The World in Harmony",
    "Nature is Enough",
    "Watch the Earth Live",
    "The Peace We Need",
    "Born From Nature",
    "Simple Scenes, Deep Peace",
    "Nature's Pure Presence",
    "The Gentle Planet",
    "Calm Found Naturally",
    "Nature Over Everything",
    "Where Life Feels Real",
    "The Wild is Calling",
    "Nature Without Filters",
    "The Beauty We Belong To",
    "Earth’s Quiet Power",
    "The Soft Touch of Nature",
    "Return to the Natural",
    "Nature’s Endless Story",
    "Relax, It's Nature",
    "The World as It Should Be",
    "Peace Grows Here",
    "Unseen Natural Moments",
    "Nature’s Perfect Mood",
    "Life Moves Naturally"
]


# List 2: Captions (Har bar inme se koi ek randomly select hoga)
CAPTIONS_GRID = [
    "Let nature slow you down",
    "Just breathe and listen",
    "Peace lives here",
    "No noise, only calm",
    "Nature understands silence",
    "Stay where the earth feels alive",
    "Calm begins here",
    "Lost but peaceful",
    "The world feels lighter here",
    "Quiet moments matter",
    "Nature resets the mind",
    "Find yourself outside",
    "Time moves softer here",
    "Where worries fade",
    "Simple and beautiful",
    "The earth never hurries",
    "Fresh air, fresh thoughts",
    "Let the wind guide you",
    "Everything feels right here",
    "Healing without words",
    "Silence you can hear",
    "Nature clears the mind",
    "Peace over pressure",
    "Slow living feels better",
    "Let the earth comfort you",
    "A gentle reminder to pause",
    "Calm is natural",
    "Nothing artificial here",
    "The sky says relax",
    "Stay present",
    "The quiet we needed",
    "Nature is enough today",
    "Just exist for a moment",
    "Feel the stillness",
    "No filters needed",
    "The soft side of life",
    "Take a deep breath",
    "Peace grows slowly",
    "Where thoughts rest",
    "Every second feels longer",
    "Listen to the leaves",
    "Free your mind",
    "Earth feels alive",
    "Rest your eyes",
    "Gentle moments",
    "Pause and feel",
    "Let nature speak",
    "Breathe deeper",
    "The calm place",
    "Stillness is powerful",
    "Find comfort outside",
    "The day feels softer",
    "Unwind naturally",
    "Beauty without effort",
    "Let the mind wander",
    "Peace over everything",
    "Watch, don’t rush",
    "Nature heals quietly",
    "Drift into calm",
    "Just be here",
    "Soft and slow",
    "The world is gentle here",
    "Silence feels full",
    "Nature welcomes you",
    "Relax your thoughts",
    "Flow with the moment",
    "The earth is patient",
    "Feel grounded",
    "Nothing to prove here",
    "Calm feels better",
    "Peace in motion",
    "Let your mind rest",
    "Quiet outside, quiet inside",
    "The natural rhythm",
    "Stay soft",
    "The pause we needed",
    "Live this moment",
    "Nature holds the answer",
    "Slow is beautiful"
]


# List 3: Fixed Hashtags (Ye har video me SAME rahega)
FIXED_HASHTAGS = """
.
.
.
.
.
#viral #trending #fyp #foryou #reels #short #shorts #ytshorts #explore #explorepage #viralvideo #trend #newvideo #content #creator #dailycontent #entertainment #fun #interesting #watchtillend #mustwatch #reality #real #moment #life #daily #people #reaction #vibes #share #support"""

# Isse AFFILIATE_HASHTAGS se badal kar INSTA_HASHTAGS kar diya hai
INSTA_HASHTAGS = """
.
.
.
.
"#viral #fyp #reels #explorepage #trending"
"""
YOUTUBE_HASHTAGS = """
.
.
.
"#shorts #youtubeshorts #viral #trending #fyp #explore #ytshorts #subscribe #contentcreator #newvideo #mustwatch #popular #reels #watchnow #entertainment #share #like #dailyvideos #creator #youtubevideo"
"""

FACEBOOK_HASHTAGS = """
.
.
.
"#viral #fyp #trending #reels #explore #explorepage #share #like #follow #instagood #facebookreels #reelsvideo #newpost #contentcreator #dailycontent #watchnow #mustwatch #popular #entertainment #fbreels"
"""

# --- HELPER FUNCTIONS ---

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_history(data):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- MAIN LOGIC ---

def run_automation():
    # 1. DELETE OLD FILES (15 Days Logic)
    history = load_history()
    today = datetime.date.today()
    new_history = []
    
    print("Checking for expired videos...")
    for entry in history:
        sent_date = datetime.date.fromisoformat(entry['date_sent'])
        days_diff = (today - sent_date).days
        
        file_path = os.path.join(VIDEO_FOLDER, entry['filename'])
        
        if days_diff >= 15:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"DELETED EXPIRED: {entry['filename']}")
        else:
            new_history.append(entry)
    
    save_history(new_history)
    history = new_history 

    # 2. PICK NEW VIDEO
    if not os.path.exists(VIDEO_FOLDER):
        os.makedirs(VIDEO_FOLDER)
        
    all_videos = [f for f in os.listdir(VIDEO_FOLDER) if f.lower().endswith(('.mp4', '.mov', '.mkv'))]
    sent_filenames = [entry['filename'] for entry in history]
    
    available_videos = [v for v in all_videos if v not in sent_filenames]
    
    if not available_videos:
        print("No new videos to send.")
        return

    video_to_send = random.choice(available_videos)
    video_path = os.path.join(VIDEO_FOLDER, video_to_send)
    
    print(f"Selected Video File: {video_to_send}")

    # 3. RANDOM SELECTION (Grid System)
    selected_title = random.choice(TITLES_GRID)
    selected_caption = random.choice(CAPTIONS_GRID)
    
    # Combine content
    full_telegram_caption = f"{selected_title}\n\n{selected_caption}\n{FIXED_HASHTAGS}"
    
    print(f"Generated Title: {selected_title}")
    print(f"Generated Caption: {selected_caption}")

    # 4. SEND TO TELEGRAM
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        print("Sending to Telegram...")
        
        # Server time ko automatically Indian Standard Time (IST) mein convert karna
        ist_now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
        
        # Format: DD MONTH HH:MM:SS AM/PM YYYY aur sabko CAPITAL karna
        time_string = ist_now.strftime("%d %b %I:%M:%S %p %Y").upper()
        
        # Sirf bold date aur time, koi title/hashtag nahi
        telegram_caption = f"<b>{time_string}</b>"

        with open(video_path, 'rb') as video_file:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
            payload = {
                'chat_id': TELEGRAM_CHAT_ID, 
                'caption': telegram_caption,
                'parse_mode': 'HTML' # <b> tag se text ko bold karne ke liye zaroori hai
            }
            files = {'video': video_file}
            try:
                requests.post(url, data=payload, files=files)
            except Exception as e:
                print(f"Telegram Error: {e}")

    # 5. SEND TO WEBHOOK
    if WEBHOOK_URL:
        print("Sending to Webhook...")
        # URL construction with your specific repo name
        raw_video_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{BRANCH_NAME}/{VIDEO_FOLDER}/{video_to_send}"
        # Encode spaces if any
        raw_video_url = raw_video_url.replace(" ", "%20")
        
        webhook_data = {
            "video_url": raw_video_url,
            "title": selected_title,
            "caption": selected_caption,
            "hashtags": FIXED_HASHTAGS,
            "insta_hashtags": INSTA_HASHTAGS,
            "youtube_hashtags": YOUTUBE_HASHTAGS, # Naya add kiya gaya
            "facebook_hashtags": FACEBOOK_HASHTAGS, # Naya add kiya gaya
            "source": "AffiliateBot"
        }
        try:
            requests.post(WEBHOOK_URL, json=webhook_data)
            print(f"Webhook Sent: {raw_video_url}")
        except Exception as e:
            print(f"Webhook Error: {e}")

    # 6. UPDATE HISTORY
    new_history.append({
        "filename": video_to_send,
        "date_sent": today.isoformat()
    })
    save_history(new_history)
    print("Automation Complete.")

if __name__ == "__main__":
    run_automation()
