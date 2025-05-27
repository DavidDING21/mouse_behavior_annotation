import os
import subprocess
import uuid

def extract_video_segment(video_path, start_frame, end_frame, fps=50, output_dir='static/clips'):
    """
    Extract specific frame range from a video to a new file
    
    Parameters:
        video_path: Path to the original video
        start_frame: Starting frame number
        end_frame: Ending frame number
        fps: Video frame rate
        output_dir: Output directory
    
    Returns:
        Path to the generated video clip
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate time range
    start_time = start_frame / fps
    duration = (end_frame - start_frame) / fps
    
    # Generate unique filename
    output_filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(output_dir, output_filename)
    
    # Use FFmpeg to extract segment
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite existing files
        '-ss', str(start_time),
        '-i', video_path,
        '-t', str(duration),
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error extracting video segment: {e}")
        print(f"Error output: {e.stderr.decode()}")
        return None