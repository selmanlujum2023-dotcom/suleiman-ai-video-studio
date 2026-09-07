"""Configuration for Sahlaan AI Backend"""
from pathlib import Path
from pydantic_settings import BaseSettings


# Get the backend directory (parent of this config file)
BACKEND_DIR = Path(__file__).parent.parent.absolute()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Sahlaan AI Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Mock mode
    MOCK_MODE: bool = True
    
    # API Configuration
    API_BASE_URL: str = ""
    API_KEY: str = ""
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Storage - resolved relative to backend directory
    OUTPUTS_DIR: Path = Path(BACKEND_DIR) / "outputs"
    
    class Config:
        env_file = BACKEND_DIR / ".env"
        case_sensitive = True


settings = Settings()
