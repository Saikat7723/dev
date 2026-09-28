# Setup & Installation Guide

Production-Ready **Library Management + Student Attendance System** with OpenCV Face Recognition.

---

## 1. Quick Start with Docker Compose (Recommended)

Run the complete multi-container system (MySQL, FastAPI Backend, Face Recognition Service, React Frontend):

```bash
docker-compose -f docker/docker-compose.yml up --build
```

Access Services:
- **Frontend SaaS UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI REST API**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Face Recognition Microservice**: [http://localhost:8001](http://localhost:8001)

---

## 2. Local Manual Setup

### Prerequisites
- Python 3.12+
- Node.js v18+ & npm
- MySQL Server (Optional - automatic SQLite fallback included for instant local testing)

### Step A: Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt

# Seed initial admin credentials & test data:
python seed.py

# Start FastAPI server:
uvicorn app.main:app --reload --port 8000
```

### Step B: Face Recognition Microservice Setup
```bash
cd face_service
python main.py
```

### Step C: Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 3. Seed Credentials

Development environment credentials initialized by `python seed.py`:

| Role | Email | Password | Access Rights |
| ---- | ----- | -------- | ------------- |
| **System Admin** | `admin@library.com` | `admin123` | Full privileges (Students, Books, System Settings, Audit Logs) |
| **Librarian** | `librarian@library.com` | `lib123` | Book management, Issue/Return, Attendance views |

---

## 4. Running Tests

Execute backend API and business logic unit tests:

```bash
pytest tests/test_api.py
```
