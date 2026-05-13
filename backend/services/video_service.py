import os
import subprocess
import logging

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self, frame_dir: str):
        self.frame_dir = frame_dir

    def extract_frames(self, video_id: str, video_path: str, interval: int = 3):
        """
        Extracts frames from a video every `interval` seconds using FFmpeg.
        Returns a list of extracted frame paths and their corresponding timestamps.
        """
        output_folder = os.path.join(self.frame_dir, video_id)
        os.makedirs(output_folder, exist_ok=True)

        # Output pattern: frame_0001.jpg, frame_0002.jpg, etc.
        # We use -vf "fps=1/interval" to get one frame every N seconds
        output_pattern = os.path.join(output_folder, "frame_%04d.jpg")
        
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"fps=1/{interval}",
            "-q:v", "2",  # High quality
            output_pattern,
            "-y"  # Overwrite
        ]

        try:
            logger.info(f"Starting frame extraction for {video_id} at {video_path}")
            subprocess.run(command, check=True, capture_output=True)
            
            # List generated files to get metadata
            frames = []
            files = sorted(os.listdir(output_folder))
            for i, filename in enumerate(files):
                if filename.endswith(".jpg"):
                    frames.append({
                        "timestamp": i * interval,
                        "path": os.path.join(output_folder, filename),
                        "filename": filename
                    })
            
            logger.info(f"Extracted {len(frames)} frames for {video_id}")
            return frames
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise Exception(f"Failed to extract frames: {e.stderr.decode()}")

# Singleton instance will be initialized in main.py
