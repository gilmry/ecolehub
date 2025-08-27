FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies based on stage
ARG STAGE=0
COPY requirements*.txt ./
RUN if [ "$STAGE" = "2" ]; then \
        pip install --no-cache-dir -r requirements.stage2.txt; \
    elif [ "$STAGE" = "1" ]; then \
        pip install --no-cache-dir -r requirements.stage1.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

COPY app/ ./app/

EXPOSE 8000

# Run appropriate main file based on stage
CMD if [ "${STAGE:-0}" = "2" ]; then \
        uvicorn app.main_stage2:app --host 0.0.0.0 --port 8000 --ws-ping-interval 20 --ws-ping-timeout 10; \
    elif [ "${STAGE:-0}" = "1" ]; then \
        uvicorn app.main_stage1:app --host 0.0.0.0 --port 8000; \
    else \
        uvicorn app.main:app --host 0.0.0.0 --port 8000; \
    fi