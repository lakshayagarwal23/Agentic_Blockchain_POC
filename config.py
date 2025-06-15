import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///rwa_tokenization.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'
    
    # API Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # NLP Settings
    SPACY_MODEL = 'en_core_web_sm'
    NLTK_DATA_PATH = os.environ.get('NLTK_DATA_PATH') or 'nltk_data'
    
    # Blockchain Settings (Mock)
    NETWORK_NAME = 'RWA-TestNet'
    TOKEN_STANDARD = 'RWA-721'
    
    # Verification Settings
    VERIFICATION_THRESHOLD = 0.7
    ASSET_VALUE_LIMITS = {
        'real_estate': {'min': 10000, 'max': 50000000},
        'vehicle': {'min': 1000, 'max': 2000000},
        'artwork': {'min': 500, 'max': 100000000},
        'equipment': {'min': 100, 'max': 5000000},
        'commodity': {'min': 50, 'max': 10000000}
    }

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Production-specific settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///production_rwa.db'
    
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}