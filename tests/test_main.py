import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base

# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_home_page(client):
    """Тест главной страницы"""
    response = client.get("/")
    assert response.status_code == 200
    assert "IT Support Assistant" in response.text

def test_health_check(client):
    """Тест проверки здоровья приложения"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data

def test_chat_endpoint(client):
    """Тест отправки сообщения в чат"""
    response = client.post("/chat", data={
        "message": "Тестовое сообщение",
        "user_id": "test_user"
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "timestamp" in data

def test_analytics_page(client):
    """Тест страницы аналитики"""
    response = client.get("/analytics")
    assert response.status_code == 200
    assert "Аналитика IT Support" in response.text

def test_stats_api(client):
    """Тест API статистики"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_conversations" in data
    assert "categories" in data
    assert "sla_metrics" in data
