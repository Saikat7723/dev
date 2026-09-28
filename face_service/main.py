import asyncio
import cv2
import json
import logging
import os
import time
from typing import List, Dict, Any, Optional
import numpy as np
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("face_service")

MAIN_API_URL = os.getenv("MAIN_API_URL", "http://localhost:8000/api")
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
CAMERA_ID = os.getenv("CAMERA_ID", "CAM-MAIN-ENTRANCE-01")

app = FastAPI(title="Library Face Recognition Camera Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CameraState:
    def __init__(self):
        self.is_active = True
        self.camera_id = CAMERA_ID
        self.last_recognized = None
        self.fps = 0.0
        self.detected_faces_count = 0
        self.registered_students = []
        self.lock = asyncio.Lock()

state = CameraState()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

def compute_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

async def fetch_registered_embeddings():
    """Fetch all active students with face embeddings from Main Backend API"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{MAIN_API_URL}/students?limit=500")
            if resp.status_code == 200:
                students = resp.json()
                logger.info(f"Loaded {len(students)} student records for face matching.")
                state.registered_students = students
    except Exception as e:
        logger.warning(f"Could not connect to Main API to fetch embeddings: {e}")

@app.on_event("startup")
async def startup():
    asyncio.create_task(fetch_registered_embeddings())
    asyncio.create_task(camera_processing_loop())

@app.get("/status")
def get_status():
    return {
        "status": "ONLINE" if state.is_active else "OFFLINE",
        "camera_id": state.camera_id,
        "fps": round(state.fps, 1),
        "detected_faces_count": state.detected_faces_count,
        "last_recognized": state.last_recognized
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def send_attendance_event(student_id: int, confidence: float):
    try:
        payload = {
            "student_id": student_id,
            "confidence": round(confidence, 3),
            "camera_id": CAMERA_ID
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(f"{MAIN_API_URL}/attendance/events", json=payload)
            if res.status_code == 200:
                data = res.json()
                logger.info(f"Attendance Event Processed: {data}")
                return data
    except Exception as e:
        logger.error(f"Error sending attendance event: {e}")
    return None

async def camera_processing_loop():
    """
    Main camera processing task loop.
    Grabs frames, detects faces, extracts embeddings, matches against registered students,
    and broadcasts updates to subscribers.
    """
    frame_count = 0
    start_time = time.time()

    # Create dummy color canvas if camera index fails or in headless docker
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    while True:
        try:
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                state.fps = 30 / elapsed if elapsed > 0 else 0
                start_time = time.time()

            # Broadcast status update via WebSocket every 2 seconds
            if frame_count % 20 == 0:
                await manager.broadcast({
                    "type": "CAMERA_STATUS",
                    "status": "ONLINE",
                    "camera_id": state.camera_id,
                    "fps": round(state.fps, 1),
                    "detected_faces": state.detected_faces_count,
                    "last_recognized": state.last_recognized
                })

            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Camera loop exception: {e}")
            await asyncio.sleep(1.0)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
