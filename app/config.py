from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    APP_NAME: str = "IT Support Chatbot"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./it_support.db")
    
    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Безопасность
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # Настройки чат-бота
    MAX_CONVERSATION_HISTORY: int = 10
    DEFAULT_RESPONSE_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"

# Создаем экземпляр настроек
settings = Settings()
