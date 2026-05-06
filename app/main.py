from fastapi import FastAPI, Depends, Request, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import asyncio
import csv
import tempfile
import os

from .database import engine, Base, get_db
from .models import Dish

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# create tables
Base.metadata.create_all(bind=engine)


# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass


manager = ConnectionManager()


# UI - Home Page
@app.get("/", response_class=HTMLResponse)
def get_ui(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request}
    )


# Order API
@app.post("/order")
async def create_order(name: str, quantity: int, db: Session = Depends(get_db)):
    name = name.strip().lower()

    if not name or quantity <= 0:
        return {"error": "Invalid input"}
    dish = db.query(Dish).filter(Dish.name == name).first()

    if dish:
        dish.pending += quantity
    else:
        dish = Dish(name=name, pending=quantity)
        db.add(dish)

    db.commit()
    db.refresh(dish)

    await manager.broadcast("update")

    return {
        "message": "Order added",
        "dish": dish.name,
        "pending": dish.pending
    }


# Get Dishes
@app.get("/dishes")
def get_dishes(db: Session = Depends(get_db)):
    dishes = db.query(Dish).all()

    return [
        {
            "name": dish.name,
            "pending": dish.pending,
            "completed": dish.completed,
            "predicted": dish.predicted
        }
        for dish in dishes
    ]


# Prediction API
@app.post("/prediction")
async def set_prediction(name: str, predicted: int, db: Session = Depends(get_db)):
    name = name.strip().lower()

    if not name or predicted < 0:
        return {"error": "Invalid input"}
    dish = db.query(Dish).filter(Dish.name == name).first()

    if not dish:
        dish = Dish(name=name, predicted=predicted)
        db.add(dish)
    else:
        dish.predicted = predicted

    db.commit()
    db.refresh(dish)

    await manager.broadcast("update")

    return {
        "message": "Prediction set",
        "dish": dish.name,
        "predicted": dish.predicted
    }


# Done API
@app.post("/done")
async def mark_done(name: str, quantity: int = 1, db: Session = Depends(get_db)):
    name = name.strip().lower()

    if quantity <= 0:
        return {"error": "Invalid quantity"}
    dish = db.query(Dish).filter(Dish.name == name).first()

    if not dish:
        return {"error": "Dish not found"}

    # Move from pending to completed (handle overflow)
    done_qty = min(quantity, dish.pending)
    dish.pending -= done_qty
    dish.completed += done_qty

    db.commit()
    db.refresh(dish)

    await manager.broadcast("update")

    return {
        "message": "Marked as done",
        "dish": dish.name,
        "pending": dish.pending,
        "completed": dish.completed
    }


# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Report Download
@app.get("/report")
async def download_report(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    dishes = db.query(Dish).all()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")

    with open(temp.name, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Dish Name", "Produced", "Predicted"])

        for dish in dishes:
            writer.writerow([dish.name, dish.completed, dish.predicted])

    # auto delete after response
    background_tasks.add_task(os.remove, temp.name)

    return FileResponse(temp.name, media_type='text/csv', filename="report.csv")

@app.get("/suggest")
def suggest_dishes(q: str = "", db: Session = Depends(get_db)):
    q = q.strip().lower()
    dishes = db.query(Dish).filter(Dish.name.ilike(f"%{q}%")).limit(5).all()
    return [dish.name for dish in dishes]