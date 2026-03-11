import os
import yt_dlp
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def download_trending_clip(url):
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': 'input_video.mp4',
        'max_filesize': 50000000,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "input_video.mp4"

def process_video(input_path):
    model = whisper.load_model("tiny")
    result = model.transcribe(input_path)
    
    video = VideoFileClip(input_path)
    
    w, h = video.size
    target_ratio = 9/16
    target_w = h * target_ratio
    video_cropped = video.crop(x_center=w/2, width=target_w)
    
    clips = [video_cropped]
    for segment in result['segments']:
        duration = segment['end'] - segment['start']
        if duration <= 0: continue
        
        txt = TextClip(
            segment['text'].upper(),
            fontsize=70,
            color='yellow',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(video_cropped.w * 0.8, None)
        ).set_start(segment['start']).set_duration(duration).set_position('center')
        
        clips.append(txt)

    final_video = CompositeVideoClip(clips)
    final_video.write_videofile("output_short.mp4", fps=24, codec="libx264")

if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=YOUR_TARGET_VIDEO" 
    video_file = download_trending_clip(test_url)
    process_video(video_file)
