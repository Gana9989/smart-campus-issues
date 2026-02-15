"""Application configuration."""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Flask configuration."""
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'campus_issues.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    PROFILE_IMAGES_FOLDER = os.path.join(BASE_DIR, "uploads", "profile_images")
    PROFILE_IMAGE_MAX_SIZE = 2 * 1024 * 1024  # 2MB max for profile pics
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
