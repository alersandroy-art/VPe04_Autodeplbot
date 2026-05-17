"""Простой тестовый бэкенд: возвращает текущее время сервера."""

import os
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI

# Экземпляр приложения FastAPI
app = FastAPI(
    title="API времени",
    description="Тестовый бэкенд с текущим временем сервера",
    version="1.0.0",
)


@app.get("/")
def root():
    """Корневой эндпоинт — краткая информация об API."""
    return {
        "message": "API времени",
        "docs": "/docs",
    }


@app.get("/time")
def get_server_time():
    """Возвращает текущее время сервера в формате UTC."""
    now = datetime.now(timezone.utc)
    return {
        "utc": now.isoformat(),  # ISO 8601, например: 2026-05-17T14:27:17+00:00
        "timestamp": now.timestamp(),  # Unix-время в секундах
    }


if __name__ == "__main__":
    # Получаем настройки из переменных окружения
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
    )
