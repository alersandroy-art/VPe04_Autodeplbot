# Простой образ для FastAPI-приложения
FROM python:3.12-slim

WORKDIR /app

# Сначала зависимости — слой кэшируется при изменении только кода
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Значения по умолчанию (как в main.py); можно переопределить при docker run -e
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=false

EXPOSE 8000

CMD ["python", "main.py"]
