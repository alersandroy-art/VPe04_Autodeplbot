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
        "endpoints": {
            "time": "/time",
            "date": "/date",
            "date_iso": "/date/iso",
            "date_ru": "/date/ru",
        },
    }


@app.get("/time")
def get_server_time():
    """Возвращает текущее время сервера в формате UTC."""
    now = datetime.now(timezone.utc)
    return {
        "utc": now.isoformat(),  # ISO 8601, например: 2026-05-17T14:27:17+00:00
        "timestamp": now.timestamp(),  # Unix-время в секундах
    }


@app.get("/date")
def get_server_date():
    """Возвращает текущую дату сервера (UTC) и её компоненты."""
    today = datetime.now(timezone.utc).date()
    return {
        "utc": today.isoformat(),
        "year": today.year,
        "month": today.month,
        "day": today.day,
        "weekday": today.isoweekday(),  # 1 — понедельник, 7 — воскресенье
    }


@app.get("/date/iso")
def get_server_date_iso():
    """Возвращает дату в формате ISO 8601 (YYYY-MM-DD)."""
    today = datetime.now(timezone.utc).date()
    return {"date": today.isoformat()}


@app.get("/date/ru")
def get_server_date_ru():
    """Возвращает дату в формате ДД.ММ.ГГГГ."""
    today = datetime.now(timezone.utc).date()
    return {"date": today.strftime("%d.%m.%Y")}


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
