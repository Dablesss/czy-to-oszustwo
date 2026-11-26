FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static
RUN mkdir -p data

# Railway i Fly podają port w zmiennej PORT.
# --no-access-log: uvicorn nie zapisuje adresów IP ani adresów stron (w adresie może być treść
# udostępnionej wiadomości). Logi aplikacji z samym werdyktem zostają.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*' --no-access-log"]
