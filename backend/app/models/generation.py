"""Generation request and response models"""
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


def normalize_dimensions(v: int) -> int:
    """Normalize dimensions to multiples of 32 (LTX requirement)"""
    return (v // 32) * 32


def normalize_frame_count(duration: int, fps: int) -> int:
    """
    Normalize frame count to LTX-compatible 8k + 1 pattern.
    
    The LTX-2.3 model requires frame counts following: 8k + 1
    Examples: 1, 9, 17, 25, 33, 41, 49, 57, 65, 73, 81, 89, 97, ...
    
    Args:
        duration: Video duration in seconds
        fps: Frames per second
        
    Returns:
        Normalized frame count following 8k + 1 pattern
    """
    total_frames = duration * fps
    
    # Find the largest k such that 8k + 1 <= total_frames
    k = (total_frames - 1) // 8
    normalized_frames = 8 * k + 1
    
    return normalized_frames


class GenerationRequest(BaseModel):
    """Request model for video generation"""
    
    prompt: str = Field(..., min_length=1, max_length=1000, description="Text prompt for video generation")
    duration: int = Field(..., ge=1, le=60, description="Video duration in seconds")
    width: int = Field(default=1024, ge=256, le=2048, description="Video width in pixels")
    height: int = Field(default=576, ge=256, le=2048, description="Video height in pixels")
    fps: int = Field(default=24, ge=1, le=60, description="Frames per second")
    reference_image: Optional[str] = Field(default=None, description="Base64 or file path to reference image")
    reference_video: Optional[str] = Field(default=None, description="Base64 or file path to reference video")
    voice_sample: Optional[str] = Field(default=None, description="Base64 or file path to voice sample")
    audio_enabled: bool = Field(default=True, description="Whether to enable audio generation")
    seed: Optional[int] = Field(default=None, ge=0, description="Random seed for reproducibility")
    
    @field_validator('width', 'height', mode='after')
    @classmethod
    def validate_dimensions(cls, v):
        """Normalize dimensions to multiples of 32 (LTX requirement)"""
        return normalize_dimensions(v)


class GenerationResponse(BaseModel):
    """Response model for generation creation"""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: Literal["queued", "processing", "rendering", "completed", "failed"] = Field(..., description="Current job status")


class GenerationStatus(BaseModel):
    """Response model for generation status"""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: Literal["queued", "processing", "rendering", "completed", "failed"] = Field(..., description="Current job status")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Generation progress percentage")
    video_url: Optional[str] = Field(default=None, description="URL to generated video (when completed)")
    thumbnail_url: Optional[str] = Field(default=None, description="URL to video thumbnail (when available)")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: str = Field(..., description="ISO 8601 timestamp of creation")
    updated_at: str = Field(..., description="ISO 8601 timestamp of last update")
