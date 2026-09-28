import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import engine, SessionLocal, Base
from app.models.user import Admin, UserRole
from app.models.academic import Department, Course
from app.models.student import Student, StudentFaceProfile
from app.models.attendance import Camera, AttendanceSetting, AttendanceSession, AttendanceEvent, Holiday
from app.models.book import BookCategory, BookAuthor, Book, BookIssue
from app.core.security import get_password_hash

def reset_db_minimal():
    print("Recreating database tables from scratch...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("1. Creating System Admins...")
        admin = Admin(
            full_name="System Administrator",
            email="admin@library.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        librarian = Admin(
            full_name="Chief Librarian",
            email="librarian@library.com",
            hashed_password=get_password_hash("lib123"),
            role=UserRole.LIBRARIAN,
            is_active=True
        )
        db.add_all([admin, librarian])
        db.commit()

        print("2. Creating Departments & Courses...")
        dept_cs = Department(code="CS", name="Computer Science & Engineering", description="Department of Computer Science")
        dept_it = Department(code="IT", name="Information Technology", description="Department of Information Technology")
        db.add_all([dept_cs, dept_it])
        db.commit()
        db.refresh(dept_cs)
        db.refresh(dept_it)

        course_cs = Course(code="BTECH-CS", name="B.Tech Computer Science", department_id=dept_cs.id, duration_years=4)
        course_it = Course(code="BTECH-IT", name="B.Tech Information Technology", department_id=dept_it.id, duration_years=4)
        db.add_all([course_cs, course_it])
        db.commit()

        print("3. Creating Attendance Settings & Camera Config...")
        settings_defaults = [
            ("FACE_RECOGNITION_THRESHOLD", "0.60", "Minimum confidence required for automatic attendance matching"),
            ("ATTENDANCE_COOLDOWN_SECONDS", "300", "Cooldown period in seconds to prevent duplicate attendance"),
            ("AUTO_CHECKOUT_HOURS", "8", "Automatic check-out after N hours if unclosed")
        ]
        for key, val, desc in settings_defaults:
            db.add(AttendanceSetting(setting_key=key, setting_value=val, description=desc))
        
        camera = Camera(
            camera_code="CAM-MAIN-ENTRANCE-01",
            name="Main Entrance Camera 01",
            location="Main Gate Entrance",
            stream_url_or_index="0",
            status="Active"
        )
        db.add(camera)
        db.commit()

        print("4. Creating Base Book Categories...")
        categories = [
            BookCategory(name="Computer Science", code="CS", description="Computer Systems, Software & AI"),
            BookCategory(name="Information Technology", code="IT", description="IT, Networks & Security"),
            BookCategory(name="General Electronics", code="EC", description="Electronics & Communication")
        ]
        db.add_all(categories)
        db.commit()

        print("Database successfully reset!")
        print("NO mock students, NO mock face embeddings, NO mock books/issues in database.")
        print("Ready for real Student Face Registration and Book addition!")
        print("\nLogin Credentials:")
        print("  Admin:     admin@library.com / admin123")
        print("  Librarian: librarian@library.com / lib123")

    except Exception as e:
        db.rollback()
        print(f"Error resetting database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    reset_db_minimal()
