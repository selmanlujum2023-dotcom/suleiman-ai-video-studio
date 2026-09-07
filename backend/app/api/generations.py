"""API endpoints for video generation"""
import secrets
from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional

from ..config import settings
from ..models.generation import GenerationRequest, GenerationResponse, GenerationStatus
from ..services.generation_service import generation_service

router = APIRouter(prefix="/api/v1", tags=["generations"])


async def verify_authorization(authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify authorization header.
    
    In MOCK_MODE, authorization is optional for local testing.
    In production mode (MOCK_MODE=false), validates against configured API_KEY.
    
    Uses constant-time comparison to prevent timing attacks.
    
    Args:
        authorization: The Authorization header value
        
    Returns:
        True if authorized, False otherwise
    """
    if settings.MOCK_MODE:
        # In mock mode, authorization is optional
        return True
    
    # Production mode: validate credentials
    if not authorization:
        return False
    
    # In production, API_KEY must be configured
    if not settings.API_KEY:
        return False
    
    # Extract token (handle "Bearer {token}" format)
    auth_parts = authorization.split()
    if len(auth_parts) == 2 and auth_parts[0].lower() == "bearer":
        token = auth_parts[1]
    else:
        token = authorization
    
    # Constant-time comparison to prevent timing attacks
    return secrets.compare_digest(token, settings.API_KEY)


@router.post("/generations", response_model=GenerationResponse)
async def create_generation(
    request: GenerationRequest,
    _authorized: bool = Depends(verify_authorization)
) -> GenerationResponse:
    """
    Create a new video generation job.
    
    Accepts generation parameters and returns immediately with job_id and status.
    Actual generation runs asynchronously in the background.
    
    Args:
        request: Generation request with prompt, dimensions, media references, etc.
        
    Returns:
        GenerationResponse with job_id and initial status (queued)
        
    Raises:
        HTTPException: If authorization fails or request is invalid
    """
    if not _authorized:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    job_id, status = await generation_service.create_generation(request)
    
    return GenerationResponse(
        job_id=job_id,
        status=status.status
    )


@router.get("/generations/{job_id}", response_model=GenerationStatus)
async def get_generation_status(
    job_id: str,
    _authorized: bool = Depends(verify_authorization)
) -> GenerationStatus:
    """
    Get the current status of a generation job.
    
    Supports states: queued, processing, rendering, completed, failed
    
    Args:
        job_id: The unique job identifier
        
    Returns:
        GenerationStatus with current progress, video_url (when completed), etc.
        
    Raises:
        HTTPException: If job not found (404) or authorization fails (401)
    """
    if not _authorized:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    status = await generation_service.get_generation(job_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return status
