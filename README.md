# Distributed Retail Intelligence Platform

A scalable retail analytics platform simulating 96 stores and 1,000+ products
with real-time inventory monitoring, sales analytics, and automated replenishment workflows.

## Tech Stack
- **Backend:** FastAPI, Python 3.11, SQLAlchemy 2.0 (async)
- **Database:** PostgreSQL 15
- **Cache:** Redis 7
- **Containerization:** Docker + Docker Compose
- **Frontend:** HTML5, Chart.js

## Features
- 96 stores across 6 US regions
- 1,000 products across 10 categories
- 57,600+ inventory records
- Real-time transaction simulation
- Automated replenishment engine
- Analytics dashboard with live charts

## Quick Start

### Prerequisites
- Docker Desktop
- Python 3.11

### Run with Docker
```bash
docker compose up --build
```

### Run locally
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Seed the database

POST http://localhost:8000/api/v1/simulator/seed

## API Docs
Visit `http://localhost:8000/docs` for full Swagger UI

## Dashboard
Open `frontend/index.html` via a local server on port 3000
