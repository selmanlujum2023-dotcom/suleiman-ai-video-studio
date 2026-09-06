"""File storage operations for generated media"""
import subprocess
from pathlib import Path
from typing import Optional

from ..config import settings


class FileStorage:
    """Handle file storage for generated media"""
    
    def __init__(self):
        self.outputs_dir = Path(settings.OUTPUTS_DIR)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
    
    def get_video_path(self, job_id: str) -> Path:
        """Get the full path for a video file"""
        return self.outputs_dir / f"{job_id}.mp4"
    
    def video_exists(self, job_id: str) -> bool:
        """Check if a video file exists"""
        return self.get_video_path(job_id).exists()
    
    def create_placeholder_video(
        self,
        job_id: str,
        width: int,
        height: int,
        fps: int,
        frames: int
    ) -> Optional[str]:
        """
        Create a placeholder MP4 video file.
        
        Uses FFmpeg if available, otherwise returns None to indicate failure.
        
        Creates an H.264 MP4 with yuv420p pixel format for broad Android/Media3 compatibility.
        
        Enforces the exact frame count passed (normalized to LTX 8k+1 pattern).
        
        Args:
            job_id: Unique job identifier
            width: Video width in pixels
            height: Video height in pixels
            fps: Frames per second
            frames: Total number of frames (normalized to LTX 8k+1 pattern)
            
        Returns:
            Path to created video file, or None if creation failed
        """
        video_path = self.get_video_path(job_id)
        
        # Check if FFmpeg is available
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True,
                timeout=5
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return None
        
        try:
            # Create a black video using FFmpeg with Android-compatible settings
            # H.264 + yuv420p + faststart for maximum compatibility
            # Explicitly limit output to the normalized frame count using -frames:v
            cmd = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", f"color=c=black:s={width}x{height}",
                "-vf", f"fps={fps}",
                "-frames:v", str(frames),
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-y",
                str(video_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0 and video_path.exists():
                return str(video_path)
            
            return None
                
        except subprocess.TimeoutExpired:
            return None
    
    def delete_video(self, job_id: str) -> bool:
        """Delete a video file"""
        try:
            video_path = self.get_video_path(job_id)
            if video_path.exists():
                video_path.unlink()
                return True
            return False
        except Exception:
            return False


# Singleton instance
file_storage = FileStorage()
