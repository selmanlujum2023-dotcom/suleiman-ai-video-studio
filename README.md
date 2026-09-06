# Suleiman AI Video Studio

🎬 An Android APK for AI-powered video generation - Turn ideas into cinematic videos with AI.

## Features

✨ **Core Features:**
- 📝 **Text to Video** - Generate videos from text prompts
- 🖼️ **Image to Video** - Animate static images into videos
- 🎥 **Video to Video** - Transform and enhance existing videos
- 🔊 **AI Audio Generation** - Create AI-generated voiceovers and soundtracks
- 📚 **Video Library** - Browse and manage your creations
- 💎 **Premium Features** - Advanced options and models

## Tech Stack

### Frontend
- **Language:** Kotlin
- **Framework:** Android Jetpack
- **UI:** Jetpack Compose / Material Design 3
- **State Management:** ViewModel + LiveData/Flow
- **Storage:** Room Database, SharedPreferences

### Backend
- **Language:** Python
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Cache:** Redis
- **Queue:** Celery

### AI Services
- **Video Generation:** Runway ML API / Replicate
- **Image Generation:** Stable Diffusion / DALL-E
- **Audio Generation:** ElevenLabs / Google TTS
- **Video Processing:** FFmpeg

### Hosting & Deployment
- **Backend:** AWS / Google Cloud / Railway
- **Database:** PostgreSQL (Managed)
- **Storage:** AWS S3 / Google Cloud Storage
- **CI/CD:** GitHub Actions

## Getting Started

### Prerequisites
- Android Studio (latest)
- Python 3.10+
- Docker
- Git

### Quick Start
```bash
# Clone the repository
git clone https://github.com/selmanlujum2023-dotcom/suleiman-ai-video-studio.git
cd suleiman-ai-video-studio

# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app/main.py

# Android Setup (in new terminal)
cd android
./gradlew build
./gradlew installDebug
```

## API Configuration

The app supports configurable API endpoints and keys:
```kotlin
// In app configuration
API_BASE_URL = "http://your-api-domain.com/api"
API_KEY = "your-api-key-here"
```

## Contributing

Pull requests are welcome!

## License

MIT License - see LICENSE file for details
