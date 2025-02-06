import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Config:
    """
    Configuration settings for the application.
    """

    # API settings
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'

    # JWT settings
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # Other application settings
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    ALLOWED_ORIGINS = ['http://localhost:4200']

    # Chroma Settings
    CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', 'chroma_db')

    if DEBUG_MODE:
        DATABASE_URL = "sqlite:///:memory:"  # In-memory SQLite for debug
    else:
        DATABASE_URL = os.getenv('DATABASE_URL')


config = Config()
