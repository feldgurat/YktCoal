FROM python:3.14-slim

WORKDIR /app

COPY common /common
RUN pip install --no-cache-dir /common

COPY Order/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Order/ .

ENV APP_PORT=8001
EXPOSE ${APP_PORT}

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${APP_PORT} --reload"]
