import subprocess
import os
import time
from moviepy.editor import VideoFileClip
from rembg.bg import remove, new_session
from PIL import Image
import io
import shutil 
import argparse
from multiprocessing import Pool

# Moved to top level
def process_frames(args):
    model_name, start_frame, end_frame, input_video_path, start_time, end_time, processed_frames_dir = args
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

def process_video_background(input_video_path, output_video_path, start_time, end_time, processed_frames_dir='processed_frames', workers=4):
    # Ensure directories exist
    os.makedirs(processed_frames_dir, exist_ok=True)

    # Setup multiprocessing
    clip = VideoFileClip(input_video_path).subclip(start_time, end_time)
    total_frames = int((end_time - start_time) * clip.fps)
    frames_per_worker = total_frames // workers
    # work_segments = [('u2netp', i * frames_per_worker, (i + 1) * frames_per_worker, input_video_path, start_time, end_time) for i in range(workers)]
    work_segments = [('u2netp', i * frames_per_worker, (i + 1) * frames_per_worker, input_video_path, start_time, end_time, processed_frames_dir) for i in range(workers)]

    # Process frames in parallel
    with Pool(workers) as pool:
        pool.map(process_frames, work_segments)

    # After processing frames, use FFmpeg directly to create the WebM video with transparency
    ffmpeg_command = [
        'ffmpeg', '-y',
        '-framerate', str(clip.fps),  # Use the same framerate as the source clip
        '-i', os.path.join(processed_frames_dir, 'frame_%04d.png'),  # Input files
        '-c:v', 'libvpx-vp9',  # Video codec
        '-pix_fmt', 'yuva420p',  # Pixel format for transparency
        '-auto-alt-ref', '0',  # Necessary for some VP9 profiles to ensure compatibility
        output_video_path  # Output file
    ]
    
    try:
        
        with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) as process:
            for line in process.stdout:
                # Print logs as they are generated
                print(line, end='')  # Flush output for real-time updates

            exit_code = process.wait()  # Wait for completion and get exit code

            print(f"Process completed for video from {start_time} to {end_time} seconds.")

            try:
                shutil.rmtree(processed_frames_dir)
                print(f"Removed temporary directory {processed_frames_dir}.")
            except Exception as e:
                print(f"Error removing temporary directory: {e}")

            # return exit_code  # Return the exit code from ffmpeg
            return 200  # Return the exit code from ffmpeg
        
    except Exception as e:
        print(f"An error occurred during video processing: {e}")
        return 501


def main():
    parser = argparse.ArgumentParser(description='Process video background.')
    parser.add_argument('--input_video_path', type=str, required=True, help='Path to input video')
    parser.add_argument('--output_video_path', type=str, required=True, help='Path for output video')
    parser.add_argument('--start_time', type=float, required=True, help='Start time for processing')
    parser.add_argument('--end_time', type=float, required=True, help='End time for processing')

    args = parser.parse_args()

    start_process = time.time()
    process_video_background(
        input_video_path=args.input_video_path,
        output_video_path=args.output_video_path,
        start_time=args.start_time,
        end_time=args.end_time
    )
    end_process = time.time()
    print(f"Total time of process: {end_process - start_process} seconds")


if __name__ == '__main__':
    main()

# Example of how to call the function:
# if __name__ == '__main__':
#     start_process = time.time()
#     process_video_background(
#         input_video_path='/Users/top_g/Desktop/react/ai_studio_v3/public/tate_pier.mp4',
#         output_video_path='/Users/top_g/Desktop/react/ai_studio_v3/public/segmented.webm',
#         start_time=0,
#         end_time=10
#     )
#     end_process = time.time()
#     print(f"Total time of process: {end_process - start_process} seconds")

