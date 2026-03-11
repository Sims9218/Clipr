import os
import random
import requests
import yt_dlp
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

NICHES = ["#shorts #techfacts", "#shorts #stockmarket", "#shorts #coding"]
SELECTED_NICHE = random.choice(NICHES)
SEARCH_QUERY = f"ytsearch1:{SELECTED_NICHE}"
COOKIE_FILE = "youtube_cookies.txt"

def acquire_clip():
    cookies = os.getenv("YT_COOKIES")
    if cookies:
        with open(COOKIE_FILE, "w", encoding='utf-8') as f:
            f.write(cookies)
        print("Cookies loaded from environment.")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': 'input_video.mp4',
        'noplaylist': True,
        'quiet': False,
        'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([SEARCH_QUERY])
            if os.path.exists("input_video.mp4"):
                return "input_video.mp4"
        except Exception as e:
            print(f"Download failed: {e}")
    
    return None

def process_video(input_path):
    if input_path is None or not os.path.exists(input_path):
        print("Error: No video file found to process.")
        return False

    print("Transcribing and editing...")
    model = whisper.load_model("tiny")
    result = model.transcribe(input_path)
    
    video = VideoFileClip(input_path).subclip(0, 59)
    w, h = video.size
    target_ratio = 9/16
    target_w = h * target_ratio
    video_cropped = video.crop(x_center=w/2, width=target_w)
    
    clips = [video_cropped]
    
    for segment in result['segments']:
        if segment['start'] > 59: break
        txt = TextClip(
            segment['text'].upper().strip(),
            fontsize=60,
            color='yellow',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(video_cropped.w * 0.9, None)
        ).set_start(segment['start']).set_duration(segment['end'] - segment['start']).set_position(('center', 'center'))
        clips.append(txt)

    final = CompositeVideoClip(clips)
    final.write_videofile("output_short.mp4", fps=24, codec="libx264", audio_codec="aac")
    return True

def send_to_telegram(file_path):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id: return

    url = f"https://api.telegram.org/bot{token}/sendVideo"
    with open(file_path, 'rb') as video:
        payload = {'chat_id': chat_id, 'caption': f"🎬 Topic: {SELECTED_NICHE}"}
        files = {'video': video}
        requests.post(url, data=payload, files=files)

if __name__ == "__main__":
    file = acquire_clip()
    if file:
        success = process_video(file)
        if success:
            send_to_telegram("output_short.mp4")
    else:
        print("Workflow stopped because the video could not be downloaded.")
