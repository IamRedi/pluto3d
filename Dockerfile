FROM python:3.11

WORKDIR /app

RUN apt-get update
RUN apt-get install -y potrace

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]