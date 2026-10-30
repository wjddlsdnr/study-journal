FROM node:22-bookworm-slim AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
ENV VITE_API_BASE=/api
RUN npm run build

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 STUDY_DATA_DIR=/data OCR_BACKEND=google SEARCH_BACKEND=keyword
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-kor && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend /build/dist ./static
RUN mkdir -p /data
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn main:web --host 0.0.0.0 --port ${PORT:-8000}"]
