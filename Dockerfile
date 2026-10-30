FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN useradd -m app && chown -R app /app
USER app
ENV PYTHONUNBUFFERED=1
# Domyślnie nic nie jest wysyłane na zewnątrz; ustaw DRY_RUN=0, gdy podasz klucze.
ENV DRY_RUN=1
# Domyślnie uruchamia demona 24/7 (pojedynczy cykl: python engine.py)
CMD ["python", "run_daemon.py"]
