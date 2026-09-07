"""Generation service - orchestrates video generation operations"""
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any

from ..models.generation import GenerationRequest, GenerationStatus, normalize_frame_count
from .mock_worker import mock_worker
from ..storage.files import file_storage


class GenerationJob:
    """In-memory representation of a generation job"""
    
    def __init__(self, job_id: str, request: GenerationRequest):
        self.job_id = job_id
        self.request = request
        self.status = "queued"
        self.progress = 0.0
        self.error: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.task: Optional[asyncio.Task] = None
    
    def to_status_response(self) -> GenerationStatus:
        """Convert to API response model"""
        response = GenerationStatus(
            job_id=self.job_id,
            status=self.status,
            progress=self.progress,
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat(),
        )
        
        # Add video URL if completed
        if self.status == "completed" and file_storage.video_exists(self.job_id):
            response.video_url = f"/api/v1/outputs/{self.job_id}.mp4"
        
        # Add error if failed
        if self.error:
            response.error = self.error
        
        return response


class GenerationService:
    """
    Business logic for generation operations.
    
    Abstracts between API and worker implementation.
    Future architecture:
    FastAPI → GenerationService → GenerationEngine/Worker → Output
    """
    
    def __init__(self):
        # In-memory job storage (will be replaced with database later)
        self.jobs: Dict[str, GenerationJob] = {}
    
    async def create_generation(self, request: GenerationRequest) -> tuple[str, GenerationStatus]:
        """
        Create a new generation job.
        
        Returns immediately with queued status.
        Generation runs asynchronously in background.
        
        Args:
            request: Generation request with prompt, dimensions, etc.
            
        Returns:
            Tuple of (job_id, status_response)
        """
        job_id = str(uuid.uuid4())
        job = GenerationJob(job_id, request)
        self.jobs[job_id] = job
        
        # Start background generation task
        task = asyncio.create_task(
            self._run_generation(job_id)
        )
        job.task = task
        
        return job_id, job.to_status_response()
    
    async def get_generation(self, job_id: str) -> Optional[GenerationStatus]:
        """
        Get current status of a generation job.
        
        Args:
            job_id: The job identifier
            
        Returns:
            Generation status or None if job not found
        """
        if job_id not in self.jobs:
            return None
        
        return self.jobs[job_id].to_status_response()
    
    async def _run_generation(self, job_id: str) -> None:
        """
        Background task that runs the actual generation.
        
        Progresses through states and calls mock worker.
        Includes normalized frame count in worker request.
        """
        job = self.jobs[job_id]
        
        try:
            # Calculate normalized frame count for LTX compatibility
            normalized_frames = normalize_frame_count(job.request.duration, job.request.fps)
            
            # Prepare request data with normalized frame count
            request_data = job.request.model_dump()
            request_data["frames"] = normalized_frames
            
            # Run the mock worker
            success = await mock_worker.generate(
                job_id,
                request_data,
                progress_callback=self._update_progress
            )
            
            if not success:
                job.status = "failed"
                if not job.error:
                    job.error = "Video encoding failed: FFmpeg not available or encoding error"
        
        except Exception as e:
            job.status = "failed"
            job.error = f"Unexpected error: {str(e)}"
        
        finally:
            job.updated_at = datetime.utcnow()
    
    async def _update_progress(
        self,
        job_id: str,
        status: str,
        progress: float,
        error: Optional[str] = None
    ) -> None:
        """
        Update job progress (called by worker).
        
        Args:
            job_id: Job identifier
            status: Current status
            progress: Progress percentage (0-100)
            error: Optional error message
        """
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = status
            job.progress = progress
            if error:
                job.error = error
            job.updated_at = datetime.utcnow()


# Singleton instance
generation_service = GenerationService()
