import os
import yt_dlp
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

SEARCH_QUERY = "ytsearch1:#shorts #viral #podcast"
OUTPUT_NAME = "output_short.mp4"

def acquire_clip():
    print("Searching for trending clip...")
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
            fontsize=50,
            color='yellow',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=1.5,
            method='caption',
            size=(video_cropped.w * 0.8, None)
        ).set_start(segment['start']).set_duration(segment['end'] - segment['start']).set_position(('center', 0.7), relative=True)
        
        clips.append(txt)

    final = CompositeVideoClip(clips)
    final.write_videofile(OUTPUT_NAME, fps=24, codec="libx264", audio_codec="aac")
    print(f"Finished! Saved as {OUTPUT_NAME}")

if __name__ == "__main__":
    file = acquire_clip()
    process_video(file)
