from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import csv
import tempfile
import os
import asyncio

from .database import engine, Base, get_db
from .models import Dish

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# ---------------------------
# Schemas
# ---------------------------

class OrderRequest(BaseModel):
    name: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


class PredictionRequest(BaseModel):
    name: str = Field(..., min_length=1)
    predicted: int = Field(..., ge=0)


class DoneRequest(BaseModel):
    name: str = Field(..., min_length=1)
    quantity: int = Field(default=1, gt=0)


# ---------------------------
# WebSocket Manager
# ---------------------------

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self.lock:
            self.active_connections.append(ws)

    async def disconnect(self, ws: WebSocket):
        async with self.lock:
            if ws in self.active_connections:
                self.active_connections.remove(ws)

    async def broadcast(self):
        async with self.lock:
            connections = self.active_connections.copy()

        for ws in connections:
            try:
                await ws.send_text("update")
            except:
                await self.disconnect(ws)


manager = ConnectionManager()


# ---------------------------
# UI Route (NO JINJA)
# ---------------------------

@app.get("/")
def get_ui():
    return FileResponse(os.path.join("templates", "index.html"))


# ---------------------------
# Order API
# ---------------------------

@app.post("/order")
async def create_order(req: OrderRequest, db: Session = Depends(get_db)):
    name = req.name.strip().title()
    qty = req.quantity

    dish = db.query(Dish).filter(Dish.name == name).first()

    if dish:
        dish.pending += qty
    else:
        dish = Dish(name=name, pending=qty)
        db.add(dish)

    db.commit()
    await manager.broadcast()

    return {"message": "Order added"}


# ---------------------------
# Get Dishes
# ---------------------------

@app.get("/dishes")
def get_dishes(db: Session = Depends(get_db)):
    dishes = db.query(Dish).all()

    return [
        {
            "name": d.name,
            "pending": d.pending,
            "completed": d.completed,
            "predicted": d.predicted
        }
        for d in dishes
    ]


# ---------------------------
# Prediction API (FIXED CASE ISSUE)
# ---------------------------

@app.post("/prediction")
async def set_prediction(req: PredictionRequest, db: Session = Depends(get_db)):
    name = req.name.strip().title()   # 🔥 FIX (was lower)

    dish = db.query(Dish).filter(Dish.name == name).first()

    if not dish:
        dish = Dish(name=name, predicted=req.predicted)
        db.add(dish)
    else:
        dish.predicted = req.predicted

    db.commit()
    await manager.broadcast()

    return {"message": "Prediction set"}


# ---------------------------
# Done API (FIXED CASE ISSUE)
# ---------------------------

@app.post("/done")
async def mark_done(req: DoneRequest, db: Session = Depends(get_db)):
    name = req.name.strip().title()   # 🔥 FIX (was lower)
    qty = req.quantity

    dish = db.query(Dish).filter(Dish.name == name).first()

    if not dish:
        raise HTTPException(404, "Dish not found")

    if dish.pending == 0:
        raise HTTPException(400, "Nothing pending")

    done_qty = min(qty, dish.pending)
    dish.pending -= done_qty
    dish.completed += done_qty

    db.commit()
    await manager.broadcast()

    return {"message": "Marked as done"}


# ---------------------------
# WebSocket
# ---------------------------

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(ws)


# ---------------------------
# Report
# ---------------------------

@app.get("/report")
async def download_report(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    dishes = db.query(Dish).all()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")

    with open(tmp.name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Dish Name", "Produced", "Predicted"])

        for d in dishes:
            writer.writerow([d.name, d.completed, d.predicted])

    background_tasks.add_task(os.remove, tmp.name)

    return FileResponse(tmp.name, filename="report.csv")


# ---------------------------
# Suggest API
# ---------------------------

@app.get("/suggest")
def suggest_dishes(q: str = "", db: Session = Depends(get_db)):
    q = q.strip().lower()

    dishes = db.query(Dish)\
        .filter(Dish.name.ilike(f"%{q}%"))\
        .limit(5)\
        .all()

    return [d.name for d in dishes]