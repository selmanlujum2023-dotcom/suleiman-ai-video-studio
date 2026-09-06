# Sahlaan AI Backend - Mock Implementation

This is a mock backend for Sahlaan AI that provides the same API contract as the eventual real generation backend.

It does **not** connect to Runway, Replicate, ElevenLabs, AWS AI services, or any external AI providers. Instead, it simulates the video generation pipeline and creates placeholder MP4 files.

## Architecture

The mock implementation is designed to be replaced later with real LTX-2.3 inference without changing the Android API contract.

```
FastAPI
  ↓
GenerationService (business logic layer)
  ↓
MockWorker (generation engine - replaceable)
  ↓
Placeholder MP4 (via FFmpeg)
  ↓
Static file serving
```

## Installation

1. **Install Python 3.9+**

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Optional: Install FFmpeg** (required for actual placeholder video generation)
   ```bash
   # On Ubuntu/Debian:
   sudo apt-get install ffmpeg
   
   # On macOS with Homebrew:
   brew install ffmpeg
   
   # On Windows (with Chocolatey):
   choco install ffmpeg
   ```

   Without FFmpeg, video generation will fail gracefully with a meaningful error.

## Configuration

Create a `.env` file in the `backend/` directory (copy from `.env.example`):

```bash
cp backend/.env.example backend/.env
```

Default configuration for mock mode:
```
MOCK_MODE=true
API_BASE_URL=
API_KEY=
```

The outputs directory is automatically created at `backend/outputs/` based on the backend directory location.

In `MOCK_MODE=true`, authorization is optional and the backend works without credentials.

For production mode (`MOCK_MODE=false`), set a secure `API_KEY` and the backend will validate it against Authorization headers.

## Running the Server

**From the project root:**

```bash
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Or from within the backend directory:**

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Both commands work identically due to package-relative imports in the backend code.

The server will start at `http://localhost:8000`

Health check:
```bash
curl http://localhost:8000/health
```

## API Endpoints

### 1. Create Generation Job

**POST** `/api/v1/generations`

Request:
```json
{
  "prompt": "A cinematic shot of mountains at sunset",
  "duration": 5,
  "width": 1024,
  "height": 576,
  "fps": 24,
  "audio_enabled": true
}
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

### 2. Get Generation Status

**GET** `/api/v1/generations/{job_id}`

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 50.0,
  "video_url": null,
  "thumbnail_url": null,
  "error": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:02"
}
```

When completed:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100.0,
  "video_url": "/api/v1/outputs/550e8400-e29b-41d4-a716-446655440000.mp4",
  "thumbnail_url": null,
  "error": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:05"
}
```

## Job States

- **queued**: Job created, waiting to start
- **processing**: Analyzing inputs and preparing generation
- **rendering**: Generating frames and compositing
- **completed**: Video successfully generated
- **failed**: Generation failed (check `error` field for details)

## Generated Output

Generated MP4 files are stored in `backend/outputs/` with the filename pattern:
```
{job_id}.mp4
```

They are served via:
```
http://localhost:8000/api/v1/outputs/{job_id}.mp4
```

## MP4 Compatibility

Generated MP4 files use:
- **Video Codec**: H.264
- **Pixel Format**: yuv420p (maximum Android/Media3 compatibility)
- **Container**: MP4 with faststart (optimized for streaming)
- **Frame Count**: Normalized to LTX-2.3 pattern (8k+1)

## Frame Count Normalization

Generated videos follow the LTX-2.3 compatible frame count pattern: `8k + 1`

This means valid frame counts are: 1, 9, 17, 25, 33, 41, 49, 57, 65, 73, 81, 89, 97...

The normalization is automatic based on duration and FPS and is:
1. Calculated in the service layer
2. Passed through the entire generation pipeline
3. Explicitly enforced in FFmpeg using the `-frames:v` parameter

This ensures the mock pipeline produces videos with the exact frame counts required by LTX-2.3.

Examples:
- 5 seconds @ 24 fps = 120 frames → normalized to 113 frames (8×14+1)
- 3 seconds @ 24 fps = 72 frames → normalized to 65 frames (8×8+1)
- 10 seconds @ 30 fps = 300 frames → normalized to 297 frames (8×37+1)

## Authorization

### Mock Mode (MOCK_MODE=true)
- Authorization header is optional
- No API key required
- Perfect for local Android testing

### Production Mode (MOCK_MODE=false)
- Requires Authorization header
- Must supply token matching configured API_KEY
- Supports "Bearer {token}" format or direct token
- Uses constant-time comparison to prevent timing attacks

Example with curl:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/api/v1/generations/...
```

## Testing

### Test 1: Create a generation
```bash
curl -X POST http://localhost:8000/api/v1/generations \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test video",
    "duration": 3,
    "width": 1024,
    "height": 576,
    "fps": 24
  }'
```

### Test 2: Poll for status
```bash
# Replace JOB_ID with the job_id from the response above
curl http://localhost:8000/api/v1/generations/JOB_ID
```

### Test 3: Download the generated video
```bash
# Once status is "completed", download the video:
curl http://localhost:8000/api/v1/outputs/JOB_ID.mp4 --output video.mp4
```

## Future Integration

This mock backend is designed to be replaced without changing the API contract.

Future implementations can:
1. Replace `MockWorker` with `LTX23Engine`
2. Add Redis for job queuing
3. Add database persistence (PostgreSQL)
4. Add real inference logic
5. Support multiple generation engines

The `GenerationService` abstraction allows swapping the worker implementation without touching the API layer.

## Troubleshooting

**Issue**: "Video encoding failed: FFmpeg not available or encoding error"
- **Solution**: Install FFmpeg (see Installation section)

**Issue**: Cannot connect to localhost:8000
- **Solution**: Check that the server is running and port 8000 is not in use

**Issue**: Job stays in "processing" state
- **Solution**: Check server logs for errors. Mock generation should complete in ~5 seconds.

**Issue**: 401 Unauthorized in production mode
- **Solution**: Set MOCK_MODE=true for local testing, or configure a valid API_KEY and Authorization header

**Issue**: ModuleNotFoundError when running from project root
- **Solution**: Ensure all backend/app files have relative imports (using `from ..` syntax)

## Development Notes

- In-memory job storage is used for this mock phase. Jobs are lost when the server restarts.
- Future: Add PostgreSQL/Redis for persistence.
- Video parameters are normalized to LTX-compatible values (dimensions as multiples of 32, frame counts as 8k+1).
- Frame normalization happens in the service layer and is passed to the worker.
- FFmpeg frame count is explicitly enforced using the `-frames:v` parameter.
- Authorization uses constant-time comparison to prevent timing attacks.
- Relative imports allow the backend to work regardless of current working directory.
