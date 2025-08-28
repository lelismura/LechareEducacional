FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080

CMD exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app --bind :$PORT
