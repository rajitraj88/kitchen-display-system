# Kitchen Display System

A real-time Kitchen Display System built using FastAPI, WebSockets, and SQLite.

---

## Features

* Add orders with quantity
* Mark orders as DONE
* Real-time sync across multiple tabs/screens (WebSocket)
* Set predicted values for dishes
* Status tracking (OK / LIMIT / OVERLOAD)
* Download production report (CSV)

---

## Setup Instructions

### 1. Open Project Folder

cd kitchen-display

---

### 2. Install Dependencies

pip install -r requirements.txt

---

### 3. Run Server

uvicorn app.main:app --reload

---

### 4. Open in Browser

http://127.0.0.1:8000/

---

## APIs

POST /order → Add new order
POST /done → Mark order as completed
POST /prediction → Set predicted values
GET /dishes → Get all dishes
GET /report → Download CSV report
WS /ws → Real-time updates

---

## Architecture

Backend: FastAPI
Database: SQLite
ORM: SQLAlchemy
Frontend: HTML + JavaScript
Real-time: WebSocket

---

## Notes

* Database is automatically created on first run
* Open multiple browser tabs to test real-time updates
* WebSocket ensures instant sync between all screens

---

## Author

Hritviz Soni
