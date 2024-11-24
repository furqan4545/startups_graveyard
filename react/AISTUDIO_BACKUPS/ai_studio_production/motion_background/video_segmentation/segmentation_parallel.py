import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageSequenceClip
from rembg.bg import remove, new_session
from PIL import Image
import io
import os
from multiprocessing import Pool, freeze_support
import numpy as np
import time

# Settings
input_video_path = 'DemoTestFilter.mp4'
output_video_path = 'DemoTestFilter_clip-unet.webm'
start_time = 0  # Start time in seconds
end_time = 27  # End time in seconds

processed_frames_dir = 'processed_frames'
workers = 4  # Number of workers (cores) to use
# Incorrect workers sometimes freeze Windows; and you might have to force restart
# Use atleast one less than the available cores for Windows to avoid freezing

# Ensure directories exist
os.makedirs(processed_frames_dir, exist_ok=True)

# Function to process a range of frames
def process_frames(args):
    model_name, start_frame, end_frame = args
    session = new_session(model_name)
    clip = VideoFileClip(input_video_path).subclip(start_time, end_time)
    total_frames = int((end_time - start_time) * clip.fps)

    def remove_background(image):
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes = image_bytes.getvalue()
        result_bytes = remove(image_bytes, alpha_matting=True, alpha_matting_foreground_threshold=270, alpha_matting_background_threshold=20, alpha_matting_erode_size=11, session=session)
        result_image = Image.open(io.BytesIO(result_bytes)).convert('RGBA')
        return result_image

    for i in range(start_frame, min(end_frame, total_frames)):
        frame = clip.get_frame(i / clip.fps)
        pil_image = Image.fromarray(frame)
        pil_image_without_bg = remove_background(pil_image)
        processed_frame_filename = os.path.join(processed_frames_dir, f'frame_{i:04d}.png')
        pil_image_without_bg.save(processed_frame_filename)

def main():
    clip = VideoFileClip(input_video_path).subclip(start_time, end_time)
    total_frames = int((end_time - start_time) * clip.fps)
    frames_per_worker = total_frames // workers
    work_segments = [('u2netp', i * frames_per_worker, (i + 1) * frames_per_worker) for i in range(workers)]

    # Process frames in parallel
    with Pool(workers) as pool:
        pool.map(process_frames, work_segments)

    # After processing frames, use FFmpeg directly to create the WebM video with transparency
    ffmpeg_command = [
        'ffmpeg',
        '-framerate', str(clip.fps),  # Use the same framerate as the source clip
        '-i', os.path.join(processed_frames_dir, 'frame_%04d.png'),  # Input files
        '-c:v', 'libvpx-vp9',  # Video codec
        '-pix_fmt', 'yuva420p',  # Pixel format for transparency
        '-auto-alt-ref', '0',  # Necessary for some VP9 profiles to ensure compatibility
        output_video_path  # Output file
    ]

    subprocess.run(ffmpeg_command)

    print(f"Process completed.")

if __name__ == '__main__':
    # Calculate time of process

    start = time.time()
    freeze_support()  # For Windows support
    main()
    
    # Calculate time of process
    end = time.time()
    print(f"Time of process: {end - start} seconds")
