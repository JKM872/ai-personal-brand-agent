FROM python:3.12-slim

WORKDIR /app

COPY . /app

ENV PYTHONUNBUFFERED=1

# Domyślnie uruchamia ciągłego demona 24/7 (lub pojedynczy cykl w Cloud Run Jobs przez: python engine.py)
CMD ["python", "run_daemon.py"]
