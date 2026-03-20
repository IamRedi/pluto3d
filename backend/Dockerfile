FROM python:3.11

WORKDIR /app

# install system deps
RUN apt-get update && apt-get install -y \
    potrace \
    openscad \
    && echo "force rebuild v1" \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}