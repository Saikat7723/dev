# REST API Documentation

Base Endpoint: `/api`

---

## 1. Authentication (`/api/auth`)

### `POST /api/auth/login`
Authenticates Admin/Librarian and returns JWT Bearer token.
- **Request Body**:
  ```json
  {
    "username_or_email": "admin@library.com",
    "password": "admin123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "<jwt-token-string>",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "full_name": "System Administrator",
      "email": "admin@library.com",
      "role": "admin",
      "is_active": true
    }
  }
  ```

### `GET /api/auth/me`
Returns details of currently authenticated admin session.

---

## 2. Student Management (`/api/students`)

### `GET /api/students`
Lists students with optional filtering by search query, department, course, or status.

### `POST /api/students`
Registers a new student profile.

### `POST /api/students/{id}/photo`
Uploads live captured student photo.
- Performs face verification (verifies exactly 1 face is visible).
- Generates 128-d face embedding vector.
- Stores image path in storage and reference details in MySQL.

---

## 3. Attendance (`/api/attendance`)

### `GET /api/attendance`
Lists attendance session logs with pagination and filters.

### `POST /api/attendance/events`
Receives real-time attendance events from camera recognition service.
- Enforces confidence threshold (`FACE_RECOGNITION_THRESHOLD`).
- Enforces duplicate prevention cooldown (`ATTENDANCE_COOLDOWN_SECONDS`).
- Automatically handles Check-In vs Check-Out logic.

### `GET /api/attendance/student/{id}/calendar`
Returns monthly calendar dataset with visual states (Present, Absent, Holiday, Leave).

### `GET /api/attendance/export/csv`
Exports attendance logs to downloadable CSV format.

---

## 4. Books & Issue Management (`/api/books`, `/api/book-issues`)

### `GET /api/books`
Lists library book inventory with stock levels and shelf locations.

### `POST /api/book-issues`
Issues a book to a student after checking stock availability.

### `POST /api/book-issues/{id}/return`
Processes book return, updates stock, and calculates overdue fines ($5/day).

---

## 5. Dashboard (`/api/dashboard`)

### `GET /api/dashboard/summary`
Calculates total/active students, present/absent today, currently inside library, attendance percentage, total/available/issued/overdue books from MySQL.

### `GET /api/dashboard/attendance-chart`
Returns daily attendance trend data for Recharts rendering.
