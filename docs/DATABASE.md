# Database Schema & Data Models

Normalized MySQL relational database schema for Library Management and Student Attendance System.

---

## Entity Relationship Summary

```
[admins] -------< [audit_logs]
   |
   +------------< [book_issues] >----------- [books] >--- [book_categories]
                      |                        |
[departments]         |                        +--------- [book_authors]
   |                  |
   +---< [students] --+--< [student_face_profiles]
   |         |
[courses]    +-----------< [attendance_sessions]
             |
             +-----------< [attendance_events]
```

---

## Primary Tables

1. **`admins`**: User accounts (Admin, Librarian) with Argon2/bcrypt password hashes.
2. **`students`**: Student demographics, Roll Number (`student_id`), status (Active/Inactive).
3. **`student_face_profiles`**: 128-d face embedding vectors (JSON), face bounding boxes, image file paths.
4. **`attendance_sessions`**: Daily sessions (`student_id`, `session_date`, `check_in_time`, `check_out_time`, `duration_minutes`, `status`, `confidence`).
5. **`attendance_events`**: Audit trail of face recognition events (`event_type`, `timestamp`, `confidence`, `camera_id`).
6. **`books`**: Book catalogue (`isbn`, `title`, `author_id`, `category_id`, `total_copies`, `available_copies`, `shelf_location`, `status`).
7. **`book_issues`**: Borrowing records (`student_id`, `book_id`, `issue_date`, `due_date`, `return_date`, `fine_amount`, `status`).
8. **`cameras`**: Camera definitions and stream locations.
9. **`attendance_settings`**: Configurable system parameters (Cooldown duration, confidence threshold).
10. **`audit_logs`**: Administrative action logs.
