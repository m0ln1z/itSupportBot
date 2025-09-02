from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

from app.database import Base

class Conversation(Base):
    """Модель для хранения диалогов с пользователями"""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    category = Column(String, nullable=True)  # Категория запроса (пароль, доступ, документы и т.д.)
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id='{self.user_id}', category='{self.category}')>"
