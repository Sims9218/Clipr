import os
import random
import requests
import yt_dlp
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

NICHES = [
    "#shorts #techfacts #coding",
    "#shorts #stockmarket #investing",
    "#shorts #cybersecurity #networking",
    "#shorts #motivation #productivity",
    "#shorts #ai #machinelearning"
]

SELECTED_NICHE = random.choice(NICHES)
SEARCH_QUERY = f"ytsearch1:{SELECTED_NICHE}"
OUTPUT_NAME = "output_short.mp4"

def acquire_clip():
    print(f"Searching for: {SELECTED_NICHE}")
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': 'input_video.mp4',
        'noplaylist': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([SEARCH_QUERY])
    return "input_video.mp4"

def process_video(input_path):
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
    final.write_videofile(OUTPUT_NAME, fps=24, codec="libx264", audio_codec="aac")

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
    process_video(file)
    send_to_telegram(OUTPUT_NAME)
