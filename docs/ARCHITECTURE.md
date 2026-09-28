# System Architecture & Design Specification

## Overview

The **Library Management + Student Attendance System** is an enterprise-grade web application combining book inventory management with automated camera-based face recognition attendance tracking.

```
+------------------+         WebSockets / HTTP        +----------------------------+
| React.js Frontend| <=============================> | Camera / Face Service      |
| (Vite + Tailwind)|                                  | (OpenCV / Python)          |
+------------------+                                  +----------------------------+
        ||                                                         ||
        || HTTP REST APIs                                          || HTTP Attendance Events
        \/                                                         \/
+----------------------------------------------------------------------------------+
|                              FastAPI Backend Application                         |
|                         (SQLAlchemy ORM + Attendance Engine)                    |
+----------------------------------------------------------------------------------+
                                        ||
                                        \/
+----------------------------------------------------------------------------------+
|                                 MySQL Database                                   |
|               (Students, Embeddings, Sessions, Books, Issues, Audits)            |
+----------------------------------------------------------------------------------+
```

---

## Key Technical Subsystems

1. **Face Recognition & Enrollment Engine**:
   - Single-face validation during registration.
   - Extracts 128-dimensional unit-normalized feature vector.
   - Compares vectors using Cosine Similarity against threshold (default `0.60`).
   - Profile images saved to file system (`uploads/profiles/`); vectors & references stored in MySQL.

2. **Attendance Engine Logic**:
   - Check-In / Check-Out automatic determination.
   - Duplicate prevention cooldown (default 300 seconds) configured via admin settings.
   - Session duration calculation in minutes.

3. **Security & Data Privacy**:
   - Passwords hashed using Argon2 / Bcrypt.
   - Stateless JWT tokens for authentication.
   - Biometric reference safety: raw video frames are **NEVER** stored in MySQL.
