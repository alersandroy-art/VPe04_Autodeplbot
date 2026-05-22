"""Простой тестовый бэкенд: возвращает текущее время сервера."""

import logging
import os
import time
from datetime import datetime, timezone

import requests
import uvicorn
from fastapi import FastAPI, Request


def send_log_to_loki(message, job="time-api", level="INFO"):
    """Отправляет лог в Grafana Loki."""
    loki_url = "http://89.111.169.142:3100/loki/api/v1/push"

    timestamp = str(int(time.time() * 1_000_000_000))

    payload = {
        "streams": [
            {
                "stream": {
                    "job": job,
                    "level": level,
                    "service": "time-api",
                },
                "values": [[timestamp, message]],
            }
        ]
    }

    try:
        response = requests.post(loki_url, json=payload, timeout=3)
        if response.status_code == 204:
            print(f"[OK] [{level}] {message}")
        else:
            print(f"[ERR] Ошибка отправки в Loki: {response.status_code}")
    except Exception as e:
        print(f"[ERR] Loki: {e}")


# Настройка логирования приложения
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Экземпляр приложения FastAPI
app = FastAPI(
    title="API времени",
    description="Тестовый бэкенд с текущим временем сервера",
    version="1.0.0",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирует каждый HTTP-запрос и ответ."""
    start = time.perf_counter()
    logger.info("Запрос: %s %s", request.method, request.url.path)

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "Ответ: %s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.on_event("startup")
async def on_startup():
    """Лог при старте сервера."""
    send_log_to_loki("API времени запущен", "time-api", "INFO")
    logger.info("API времени запущен (уровень логов: %s)", LOG_LEVEL)


@app.on_event("shutdown")
async def on_shutdown():
    """Лог при остановке сервера."""
    send_log_to_loki("API времени остановлен", "time-api", "INFO")
    logger.info("API времени остановлен")


@app.get("/")
def root():
    """Корневой эндпоинт — краткая информация об API."""
    send_log_to_loki("Запрошен корневой эндпоинт /", "time-api", "INFO")
    logger.debug("Отдаём список эндпоинтов")
    return {
        "message": "API времени",
        "docs": "/docs",
        "endpoints": {
            "time": "/time",
            "date": "/date",
            "date_iso": "/date/iso",
            "date_ru": "/date/ru",
            "datetime": "/datetime",
            "health": "/health",
        },
    }


@app.get("/time")
def get_server_time():
    """Возвращает текущее время сервера в формате UTC."""
    send_log_to_loki("Запрошен эндпоинт /time", "time-api", "INFO")
    now = datetime.now(timezone.utc)
    logger.info("Время UTC: %s", now.isoformat())
    return {
        "utc": now.isoformat(),  # ISO 8601, например: 2026-05-17T14:27:17+00:00
        "timestamp": now.timestamp(),  # Unix-время в секундах
    }


@app.get("/date")
def get_server_date():
    """Возвращает текущую дату сервера (UTC) и её компоненты."""
    send_log_to_loki("Запрошен эндпоинт /date", "time-api", "INFO")
    today = datetime.now(timezone.utc).date()
    logger.info("Дата UTC: %s", today.isoformat())
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
    send_log_to_loki("Запрошен эндпоинт /date/iso", "time-api", "INFO")
    today = datetime.now(timezone.utc).date()
    logger.info("Дата ISO: %s", today.isoformat())
    return {"date": today.isoformat()}


@app.get("/date/ru")
def get_server_date_ru():
    """Возвращает дату в формате ДД.ММ.ГГГГ."""
    send_log_to_loki("Запрошен эндпоинт /date/ru", "time-api", "INFO")
    today = datetime.now(timezone.utc).date()
    date_ru = today.strftime("%d.%m.%Y")
    logger.info("Дата RU: %s", date_ru)
    return {"date": date_ru}


@app.get("/datetime")
def get_server_datetime():
    """Возвращает текущие дату и время сервера (UTC)."""
    send_log_to_loki("Запрошен эндпоинт /datetime", "time-api", "INFO")
    now = datetime.now(timezone.utc)
    logger.info("Дата и время UTC: %s", now.isoformat())
    return {
        "utc": now.isoformat(),
        "date": now.date().isoformat(),
        "time": now.strftime("%H:%M:%S"),
        "timestamp": now.timestamp(),
    }


@app.get("/health")
def health_check():
    """Проверка работоспособности сервиса."""
    send_log_to_loki("Запрошен health check /health", "time-api", "INFO")
    logger.debug("Health check: ok")
    return {"status": "ok"}


if __name__ == "__main__":
    # Получаем настройки из переменных окружения
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    logger.info("Запуск Uvicorn на %s:%s", host, port)
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level=LOG_LEVEL.lower(),
        access_log=True,
    )
