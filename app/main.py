from fastapi import FastAPI, Depends, Request, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import csv
import tempfile
import os

from .database import engine, Base, get_db
from .models import Dish

app = FastAPI()

# ---------------------------
# FIXED TEMPLATE PATH (for your structure)
# ---------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Create tables
Base.metadata.create_all(bind=engine)

# ---------------------------
# Pydantic Schemas
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
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

# ---------------------------
# UI Route
# ---------------------------

@app.get("/", response_class=HTMLResponse)
def get_ui(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request}
    )

# ---------------------------
# Order API
# ---------------------------

@app.post("/order")
async def create_order(req: OrderRequest, db: Session = Depends(get_db)):
    name = req.name.strip().lower()
    quantity = req.quantity

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

# ---------------------------
# Get Dishes
# ---------------------------

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

# ---------------------------
# Prediction API
# ---------------------------

@app.post("/prediction")
async def set_prediction(req: PredictionRequest, db: Session = Depends(get_db)):
    name = req.name.strip().lower()

    dish = db.query(Dish).filter(Dish.name == name).first()

    if not dish:
        dish = Dish(name=name, predicted=req.predicted)
        db.add(dish)
    else:
        dish.predicted = req.predicted

    db.commit()
    db.refresh(dish)

    await manager.broadcast("update")

    return {
        "message": "Prediction set",
        "dish": dish.name,
        "predicted": dish.predicted
    }

# ---------------------------
# Done API
# ---------------------------

@app.post("/done")
async def mark_done(req: DoneRequest, db: Session = Depends(get_db)):
    name = req.name.strip().lower()
    quantity = req.quantity

    dish = db.query(Dish).filter(Dish.name == name).first()

    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

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

# ---------------------------
# WebSocket Endpoint
# ---------------------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ---------------------------
# Report Download
# ---------------------------

@app.get("/report")
async def download_report(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    dishes = db.query(Dish).all()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")

    with open(temp.name, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Dish Name", "Produced", "Predicted"])

        for dish in dishes:
            writer.writerow([dish.name, dish.completed, dish.predicted])

    background_tasks.add_task(os.remove, temp.name)

    return FileResponse(
        temp.name,
        media_type="text/csv",
        filename="report.csv"
    )

# ---------------------------
# Suggest API
# ---------------------------

@app.get("/suggest")
def suggest_dishes(q: str = "", db: Session = Depends(get_db)):
    q = q.strip().lower()

    dishes = db.query(Dish).filter(Dish.name.ilike(f"%{q}%")).limit(5).all()

    return [dish.name for dish in dishes]