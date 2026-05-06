# 🍽️ Kitchen Display System (KDS)

A real-time Kitchen Display System built using **FastAPI, WebSockets, and SQLite/PostgreSQL**, designed to simulate operations of an on-demand food delivery platform.

This system enables kitchen staff to track incoming orders, production progress, and predicted demand — all in real-time across multiple screens.

---

## 🚀 Live Demo

🔗 **Live Application:** <your-deployed-link>
📂 **GitHub Repository:** <your-repo-link>

---

## 🚀 Features

* 📦 Place orders with quantity
* ✅ Mark items as DONE (supports partial completion)
* 📊 Track **Created-till-now (Produced)** vs **Predicted demand**
* 🔄 Real-time sync across multiple screens using **WebSockets**
* ⚠️ Smart status detection:

  * ⚪ NO DATA (no prediction)
  * 🟢 OK (under capacity)
  * 🟡 LIMIT (at capacity)
  * 🔴 OVERLOAD (exceeds capacity)
* 📥 Download production report (CSV)
* 🔍 Dish name autocomplete (typeahead suggestions)
* 🔢 DONE with quantity validation (prevents over-processing)
* 🚫 DONE button auto-disabled when no pending items
* ✨ Auto-formatting of dish names
* 🖥️ Optimized UI for large kitchen displays

---

## 🖥️ Kitchen Display Behavior

* Open the UI in multiple tabs/screens
* When any user clicks **DONE**, all screens update instantly
* Ensures **real-time synchronization across kitchen displays**
* Helps staff prioritize workload dynamically

---

## 🧠 System Design

### 🔹 Real-Time Architecture

* Implemented using **WebSockets**
* Broadcast-based update system
* Eliminates polling → reduces latency

### 🔹 Backend

* Built with **FastAPI**
* REST + WebSocket hybrid architecture
* Uses dependency injection (`get_db`)

### 🔹 Database

* Default: **SQLite (local development)**
* Production-ready: **PostgreSQL**
* Connection pooling supported

---

## 📊 Core Logic

### Created-till-now Calculation

> Created-till-now = sum of quantities marked as DONE

### Status Logic

```text
total = pending + completed
```

| Condition         | Status   |
| ----------------- | -------- |
| predicted = 0     | NO DATA  |
| total < predicted | OK       |
| total = predicted | LIMIT    |
| total > predicted | OVERLOAD |

---

## 🗄️ Data Model

| Field     | Description                          |
| --------- | ------------------------------------ |
| pending   | Orders yet to be prepared            |
| completed | Created-till-now (Produced quantity) |
| predicted | Expected demand                      |

---

## 📡 API Endpoints

### ➤ Create Order

POST /order

```json
{
  "name": "pizza",
  "quantity": 2
}
```

---

### ➤ Mark as Done

POST /done

```json
{
  "name": "pizza",
  "quantity": 1
}
```

---

### ➤ Set Prediction

POST /prediction

```json
{
  "name": "pizza",
  "predicted": 50
}
```

---

### ➤ Get All Dishes

GET /dishes

---

### ➤ Download Report

GET /report

---

### ➤ Autocomplete

GET /suggest?q=piz

---

### ➤ WebSocket

/ws

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd kitchen-display
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Server

```bash
uvicorn app.main:app --reload
```

### 4. Open in Browser

```
http://127.0.0.1:8000/
```

---

## ☁️ Deployment

Supported platforms:

* Render (recommended)
* AWS EC2
* DigitalOcean
* Heroku

### 🔧 Environment Variable

```bash
DATABASE_URL=<your-database-url>
```

Example:

```
postgresql://user:password@host:port/dbname
```

---

## 📈 Scalability Considerations

* Replace SQLite with PostgreSQL
* Use **Redis Pub/Sub** for multi-instance WebSocket sync
* Add load balancer with sticky sessions
* Introduce caching layer (Redis)
* Containerize using Docker

---

## ⚠️ Limitations

* SQLite not suitable for high concurrency
* No authentication layer
* WebSocket manager is in-memory (single-instance)
* UI is basic (can be upgraded using React)

---

## 🔮 Future Improvements

* Authentication & role-based access
* Order history tracking
* Analytics dashboard
* Mobile/tablet optimization
* Microservices architecture

---

## 👨‍💻 Author

**Hritviz Soni**
QA Automation Engineer (SDET)
Skilled in Python, FastAPI, Automation, and System Design

---

## 📌 Notes

* Developed as part of a backend/system design assignment
* Focused on **real-time updates and scalability**
* Implements **multi-screen synchronization using WebSockets**
* Includes enhancements beyond assignment requirements

---

## ⭐ Final Thought

This project demonstrates not just API development, but **real-time system design, scalability thinking, and production readiness**.
