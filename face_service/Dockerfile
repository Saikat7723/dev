FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn opencv-python numpy httpx pydantic websockets

COPY . .

EXPOSE 8001

CMD ["python", "main.py"]
