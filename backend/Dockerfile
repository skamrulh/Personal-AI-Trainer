FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# FIX 12: Added --timeout 120 so LLM calls (can take 5-30s) are not killed
# by gunicorn's default 30s worker timeout. Also added --log-level info.
CMD ["gunicorn", "app:app", \
     "-b", "0.0.0.0:5000", \
     "--workers", "2", \
     "--timeout", "120", \
     "--log-level", "info"]
