"""Backend configuration settings"""

import os
from pathlib import Path

class Config:
    """Application configuration"""
    
    # Flask settings
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Agent settings
    AGENTS_BASE_PATH = Path(__file__).parent.parent
    EQUIPMENT_MODELS_PATH = AGENTS_BASE_PATH / 'agents' / 'equipment_utility' / 'models'
    FORECASTING_MODELS_PATH = AGENTS_BASE_PATH / 'agents' / 'forecasting_agent' / 'models'
    
    # API settings
    API_PREFIX = '/api'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}