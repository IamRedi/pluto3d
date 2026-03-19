FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y potrace

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]