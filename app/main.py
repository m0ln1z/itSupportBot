from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
from datetime import datetime

from app.database import get_db, init_db
from app.services.chatbot_service import ChatbotService
from app.services.analytics_service import AnalyticsService
from app.models.conversation import Conversation
from app.config import settings

# Инициализация FastAPI приложения
app = FastAPI(
    title="IT Support Chatbot",
    description="Чат-бот для автоматизации ИТ-поддержки",
    version="1.0.0"
)

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Инициализация сервисов
chatbot_service = ChatbotService()
analytics_service = AnalyticsService()

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    init_db()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница с чат-интерфейсом"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(
    message: str = Form(...),
    user_id: str = Form(default="anonymous"),
    db: Session = Depends(get_db)
):
    """Обработка сообщений чата"""
    try:
        # Получение ответа от ИИ
        response = await chatbot_service.get_response(message, user_id)
        
        # Сохранение в базу данных
        conversation = Conversation(
            user_id=user_id,
            user_message=message,
            bot_response=response,
            timestamp=datetime.now(),
            category=chatbot_service.classify_message(message)
        )
        db.add(conversation)
        db.commit()
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "category": conversation.category
        }
    except Exception as e:
        return {
            "response": "Извините, произошла ошибка. Пожалуйста, попробуйте позже или обратитесь к специалисту ИТ-поддержки.",
            "error": str(e)
        }

@app.get("/analytics")
async def analytics(request: Request, db: Session = Depends(get_db)):
    """Страница аналитики"""
    stats = analytics_service.get_statistics(db)
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "stats": stats
    })

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """API для получения статистики"""
    return analytics_service.get_statistics(db)

@app.get("/health")
async def health_check():
    """Проверка состояния приложения"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
