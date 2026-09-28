import sys
import os
from datetime import datetime, date, timedelta
import json
import numpy as np

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import engine, SessionLocal, Base
from app.models.user import Admin, UserRole
from app.models.academic import Department, Course
from app.models.student import Student, StudentFaceProfile
from app.models.attendance import Camera, AttendanceSetting, AttendanceSession, AttendanceEvent, Holiday
from app.models.book import BookCategory, BookAuthor, Book, BookIssue
from app.core.security import get_password_hash
from app.face_recognition.engine import face_engine

def seed_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("Seeding Admins...")
        admin = db.query(Admin).filter(Admin.email == "admin@library.com").first()
        if not admin:
            admin = Admin(
                full_name="System Administrator",
                email="admin@library.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)

        librarian = db.query(Admin).filter(Admin.email == "librarian@library.com").first()
        if not librarian:
            librarian = Admin(
                full_name="Chief Librarian",
                email="librarian@library.com",
                hashed_password=get_password_hash("lib123"),
                role=UserRole.LIBRARIAN,
                is_active=True
            )
            db.add(librarian)

        db.commit()

        print("Seeding Departments & Courses...")
        dept_cs = db.query(Department).filter(Department.code == "CS").first()
        if not dept_cs:
            dept_cs = Department(code="CS", name="Computer Science & Engineering", description="Department of Computer Science")
            db.add(dept_cs)
            db.commit()
            db.refresh(dept_cs)

        dept_it = db.query(Department).filter(Department.code == "IT").first()
        if not dept_it:
            dept_it = Department(code="IT", name="Information Technology", description="Department of Information Technology")
            db.add(dept_it)
            db.commit()
            db.refresh(dept_it)

        course_cs = db.query(Course).filter(Course.code == "BTECH-CS").first()
        if not course_cs:
            course_cs = Course(code="BTECH-CS", name="B.Tech Computer Science", department_id=dept_cs.id, duration_years=4)
            db.add(course_cs)
            db.commit()
            db.refresh(course_cs)

        course_it = db.query(Course).filter(Course.code == "BTECH-IT").first()
        if not course_it:
            course_it = Course(code="BTECH-IT", name="B.Tech Information Technology", department_id=dept_it.id, duration_years=4)
            db.add(course_it)
            db.commit()
            db.refresh(course_it)

        print("Seeding Attendance Settings & Camera...")
        settings_defaults = [
            ("FACE_RECOGNITION_THRESHOLD", "0.60", "Minimum confidence required for automatic attendance matching"),
            ("ATTENDANCE_COOLDOWN_SECONDS", "300", "Cooldown period in seconds to prevent duplicate attendance"),
            ("AUTO_CHECKOUT_HOURS", "8", "Automatic check-out after N hours if unclosed")
        ]
        for key, val, desc in settings_defaults:
            st = db.query(AttendanceSetting).filter(AttendanceSetting.setting_key == key).first()
            if not st:
                db.add(AttendanceSetting(setting_key=key, setting_value=val, description=desc))
        db.commit()

        camera = db.query(Camera).filter(Camera.camera_code == "CAM-MAIN-ENTRANCE-01").first()
        if not camera:
            camera = Camera(
                camera_code="CAM-MAIN-ENTRANCE-01",
                name="Main Entrance Camera 01",
                location="Main Gate Entrance",
                stream_url_or_index="0",
                status="Active"
            )
            db.add(camera)
            db.commit()

        print("Seeding Book Categories & Authors...")
        cat_cs = db.query(BookCategory).filter(BookCategory.code == "CS").first()
        if not cat_cs:
            cat_cs = BookCategory(name="Computer Science", code="CS", description="Computer Systems, Software & AI")
            db.add(cat_cs)
            db.commit()
            db.refresh(cat_cs)

        author_bob = db.query(BookAuthor).filter(BookAuthor.name == "Robert C. Martin").first()
        if not author_bob:
            author_bob = BookAuthor(name="Robert C. Martin", bio="Software Craftsman and Author")
            db.add(author_bob)
            db.commit()
            db.refresh(author_bob)

        author_tanen = db.query(BookAuthor).filter(BookAuthor.name == "Andrew S. Tanenbaum").first()
        if not author_tanen:
            author_tanen = BookAuthor(name="Andrew S. Tanenbaum", bio="Computer Scientist & Author")
            db.add(author_tanen)
            db.commit()
            db.refresh(author_tanen)

        print("Seeding Books...")
        b1 = db.query(Book).filter(Book.isbn == "978-0132350884").first()
        if not b1:
            b1 = Book(
                isbn="978-0132350884",
                title="Clean Code: A Handbook of Agile Software Craftsmanship",
                author_id=author_bob.id,
                category_id=cat_cs.id,
                publisher="Prentice Hall",
                description="A handbook of agile software craftsmanship",
                edition="1st",
                publication_year=2008,
                total_copies=5,
                available_copies=4,
                shelf_location="Shelf CS-A1",
                status="Available"
            )
            db.add(b1)

        b2 = db.query(Book).filter(Book.isbn == "978-0133591620").first()
        if not b2:
            b2 = Book(
                isbn="978-0133591620",
                title="Modern Operating Systems",
                author_id=author_tanen.id,
                category_id=cat_cs.id,
                publisher="Pearson",
                description="Operating Systems principles and design",
                edition="4th",
                publication_year=2014,
                total_copies=3,
                available_copies=2,
                shelf_location="Shelf CS-B2",
                status="Available"
            )
            db.add(b2)
        db.commit()

        print("Seeding Sample Students with Face Embeddings...")
        sample_students_data = [
            ("STU001", "Rahul Kumar", "rahul.kumar@student.edu", "9876543210", dept_cs.id, course_cs.id),
            ("STU002", "Priya Sharma", "priya.sharma@student.edu", "9876543211", dept_cs.id, course_cs.id),
            ("STU003", "Amit Patel", "amit.patel@student.edu", "9876543212", dept_it.id, course_it.id),
            ("STU004", "Sneha Roy", "sneha.roy@student.edu", "9876543213", dept_it.id, course_it.id),
        ]

        created_students = []
        for sid, name, email, phone, d_id, c_id in sample_students_data:
            stu = db.query(Student).filter(Student.student_id == sid).first()
            if not stu:
                stu = Student(
                    student_id=sid,
                    full_name=name,
                    email=email,
                    phone=phone,
                    department_id=d_id,
                    course_id=c_id,
                    dob=date(2003, 5, 14),
                    gender="Male" if "kumar" in email or "patel" in email else "Female",
                    date_of_joining=date(2023, 8, 1),
                    address="University Student Hostel",
                    status="Active"
                )
                db.add(stu)
                db.commit()
                db.refresh(stu)

                # Create seed face embedding (128-d unit vector seeded deterministically)
                np.random.seed(stu.id * 42)
                vec = np.random.randn(128).astype(np.float32)
                vec = (vec / np.linalg.norm(vec)).tolist()

                face_prof = StudentFaceProfile(
                    student_id=stu.id,
                    embedding_vector=vec,
                    face_bounding_box={"x": 50, "y": 50, "w": 100, "h": 100},
                    reference_image_path=f"/uploads/profiles/seed_{stu.student_id}.jpg",
                    is_active=True
                )
                db.add(face_prof)
                db.commit()

            created_students.append(stu)

        print("Seeding Sample Attendance & Book Issues...")
        today = date.today()
        # Create attendance sessions for past 5 days
        for i in range(5):
            past_date = today - timedelta(days=i)
            for stu in created_students[:3]: # Rahul, Priya, Amit present
                existing_sess = db.query(AttendanceSession).filter(
                    AttendanceSession.student_id == stu.id,
                    AttendanceSession.session_date == past_date
                ).first()
                if not existing_sess:
                    check_in = datetime.combine(past_date, datetime.strptime("09:02:15", "%H:%M:%S").time())
                    check_out = datetime.combine(past_date, datetime.strptime("12:45:30", "%H:%M:%S").time())
                    sess = AttendanceSession(
                        student_id=stu.id,
                        session_date=past_date,
                        check_in_time=check_in,
                        check_out_time=check_out if i > 0 else None, # Today session remains open (inside)
                        duration_minutes=223 if i > 0 else 0,
                        status="Present",
                        confidence=0.92,
                        camera_id="CAM-MAIN-ENTRANCE-01"
                    )
                    db.add(sess)

        # Issue book to STU001
        stu1 = created_students[0]
        book1 = db.query(Book).first()
        if stu1 and book1:
            existing_issue = db.query(BookIssue).filter(BookIssue.student_id == stu1.id, BookIssue.book_id == book1.id).first()
            if not existing_issue:
                issue = BookIssue(
                    student_id=stu1.id,
                    book_id=book1.id,
                    issue_date=today - timedelta(days=7),
                    due_date=today + timedelta(days=7),
                    status="ISSUED",
                    issued_by_admin_id=admin.id
                )
                db.add(issue)

        db.commit()
        print("Database seeding completed successfully!")
        print("Default Credentials:")
        print("  Admin:     admin@library.com / admin123")
        print("  Librarian: librarian@library.com / lib123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
