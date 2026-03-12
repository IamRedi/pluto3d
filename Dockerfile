FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y potrace

COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY backend ./backend

CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT