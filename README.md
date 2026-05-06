# 🍽️ Kitchen Display System (KDS)

A real-time Kitchen Display System built using FastAPI, WebSockets, and SQLite, designed to simulate operations of an on-demand food delivery platform.

---

## 🚀 Live Features

- 📦 Place orders with quantity  
- ✅ Mark items as DONE (partial or full)  
- 📊 Track Created-till-now (Produced) vs Predicted  
- 🔄 Real-time sync across multiple screens using WebSockets  
- ⚠️ Smart status detection (4 states):
  - ⚪ IDLE (no activity)
  - 🟢 OK (under capacity)
  - 🟡 LIMIT (at capacity)
  - 🔴 OVERLOAD (exceeds capacity)  
- 🧠 Advanced logic using total production (pending + completed) vs predicted  
- 📥 Download production report (CSV)  
- 🔍 Dish name autocomplete  
- ✨ Auto-formatting of dish names (e.g., pizza → Pizza)

---

## 🖥️ Kitchen Display Behavior

- Open the UI in multiple tabs/screens  
- When any user clicks DONE, all screens update instantly  
- Designed for large kitchen displays with real-time feedback  
- Helps kitchen staff prioritize workload dynamically  

---

## 🧠 System Design Highlights

### 🔹 Real-Time Architecture
- Implemented using WebSockets  
- Broadcast-based update system  
- Eliminates polling → reduces latency  

### 🔹 Scalable Backend
- Built with FastAPI  
- Uses dependency injection (get_db)  
- Easily extensible to PostgreSQL  

### 🔹 Smart Status Logic

Status is calculated using:

total = pending + completed

| Condition | Status |
|----------|--------|
| total = 0 and predicted = 0 | IDLE |
| total < predicted | OK |
| total = predicted | LIMIT |
| total > predicted | OVERLOAD |

---

### 🔹 Data Model

| Field       | Description                     |
|------------|---------------------------------|
| pending    | Orders yet to be prepared       |
| completed  | Created-till-now (Produced)     |
| predicted  | Expected demand                 |

---

## 📡 API Endpoints

### ➤ Create Order
POST /order
{
  "name": "pizza",
  "quantity": 2
}

### ➤ Mark as Done
POST /done
{
  "name": "pizza",
  "quantity": 1
}

### ➤ Set Prediction
POST /prediction
{
  "name": "pizza",
  "predicted": 50
}

### ➤ Get All Dishes
GET /dishes

### ➤ Download Report
GET /report

### ➤ WebSocket
/ws

---

## ⚙️ Setup Instructions

### 1. Clone Repository
git clone <your-repo-url>  
cd kitchen-display  

### 2. Install Dependencies
pip install -r requirements.txt  

### 3. Run Server
uvicorn app.main:app --reload  

### 4. Open in Browser
http://127.0.0.1:8000/

---

## ☁️ Deployment

This project can be deployed on:

- Render (recommended)  
- AWS EC2  
- DigitalOcean  
- Heroku  

Uses environment variable DATABASE_URL for production database configuration.

---

## 📈 Scalability Considerations

- Replace SQLite with PostgreSQL  
- Use Redis Pub/Sub for multi-instance WebSocket sync  
- Add load balancer with sticky sessions  
- Implement caching layer if needed  

---

## ⚠️ Limitations

- SQLite not suitable for high concurrency  
- No authentication layer  
- UI is basic (can be enhanced using React)  

---

## 👨‍💻 Author

Hritviz Soni  

QA Automation Engineer (SDET)  
Skilled in Python, FastAPI, Automation, and System Design  

---

## 📌 Notes

- Developed as part of a backend system design assignment  
- Focused on real-time updates and scalability  
- Includes enhanced logic for better operational decision-making  
- Easily extensible for production-grade systems  

---