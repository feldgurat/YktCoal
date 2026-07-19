FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Каталог для загруженных документов (license, passport и т.д.).
# В docker-compose монтируется как volume.
RUN mkdir -p /data/uploads

ENV APP_PORT=8002
EXPOSE ${APP_PORT}

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${APP_PORT} --reload"]
