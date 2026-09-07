"""Mock worker for simulating video generation"""
import asyncio
from typing import Optional, Dict, Any

from ..storage.files import file_storage


class MockWorker:
    """
    Mock worker that simulates the LTX-2.3 generation pipeline.
    
    This is a placeholder for the eventual real inference engine.
    It progresses through realistic states and creates actual placeholder MP4 files.
    """
    
    # Simulated duration for each phase (in seconds)
    PROCESSING_DELAY = 2.0
    RENDERING_DELAY = 3.0
    
    async def generate(
        self,
        job_id: str,
        request_data: Dict[str, Any],
        progress_callback: Optional[callable] = None
    ) -> bool:
        """
        Simulate video generation.
        
        Progresses through: queued → processing → rendering → completed
        
        Creates an actual playable placeholder MP4 file.
        
        Args:
            job_id: Unique job identifier
            request_data: Generation request parameters (includes normalized frame count)
            progress_callback: Optional callback to report progress
            
        Returns:
            True if generation succeeded, False otherwise
        """
        try:
            # Phase 1: Processing (preparing inputs, analyzing prompt)
            if progress_callback:
                await progress_callback(job_id, "processing", 25.0)
            
            await asyncio.sleep(self.PROCESSING_DELAY)
            
            # Phase 2: Rendering (generating frames)
            if progress_callback:
                await progress_callback(job_id, "rendering", 50.0)
            
            await asyncio.sleep(self.RENDERING_DELAY)
            
            # Phase 3: Create actual placeholder video
            width = request_data.get("width", 1024)
            height = request_data.get("height", 576)
            fps = request_data.get("fps", 24)
            # Use the normalized frame count passed from the service
            frames = request_data.get("frames", 24)
            
            video_path = file_storage.create_placeholder_video(
                job_id,
                width,
                height,
                fps,
                frames
            )
            
            if not video_path:
                # FFmpeg not available or failed
                if progress_callback:
                    await progress_callback(
                        job_id,
                        "failed",
                        100.0,
                        error="Video encoding failed: FFmpeg not available or encoding error"
                    )
                return False
            
            # Success
            if progress_callback:
                await progress_callback(job_id, "completed", 100.0)
            
            return True
            
        except Exception as e:
            if progress_callback:
                await progress_callback(
                    job_id,
                    "failed",
                    100.0,
                    error=f"Generation error: {str(e)}"
                )
            return False


# Singleton instance
mock_worker = MockWorker()
