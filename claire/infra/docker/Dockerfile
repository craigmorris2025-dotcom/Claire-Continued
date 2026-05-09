FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r src/backend/requirements.txt

CMD ["uvicorn", "src.backend.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
