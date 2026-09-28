import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Library Management & Student Attendance System"
    API_V1_STR: str = "/api"
    
    # Database configuration
    # Default to MySQL, fallback to SQLite if needed for local testing
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:rootpassword@localhost:3306/library_db"
    )
    SQLITE_FALLBACK_URL: str = "sqlite:///./library_system.db"
    USE_SQLITE_FALLBACK_IF_MYSQL_UNAVAILABLE: bool = True
    
    # JWT security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "SUPER_SECRET_JWT_KEY_987654321_LIBRARY_SYSTEM_2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Face Recognition & Attendance Settings
    FACE_RECOGNITION_THRESHOLD: float = float(os.getenv("FACE_RECOGNITION_THRESHOLD", "0.60"))
    ATTENDANCE_COOLDOWN_SECONDS: int = int(os.getenv("ATTENDANCE_COOLDOWN_SECONDS", "300")) # 5 mins default
    AUTO_CHECKOUT_HOURS: int = 8
    
    # Storage
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", "uploads")
    PROFILES_DIR: str = os.path.join("uploads", "profiles")
    
    # Camera
    CAMERA_ID: str = os.getenv("CAMERA_ID", "CAM-MAIN-ENTRANCE-01")
    
    class Config:
        case_sensitive = True

settings = Settings()
