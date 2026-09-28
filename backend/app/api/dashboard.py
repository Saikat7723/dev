from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.database.session import get_db
from app.models.student import Student
from app.models.attendance import AttendanceSession
from app.models.book import Book, BookIssue, BookCategory
from app.schemas.dashboard import DashboardSummaryResponse, AttendanceChartResponse, LibrarySummaryResponse
from app.core.security import get_current_user, Admin

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    today = date.today()

    # Students metrics
    total_students = db.query(func.count(Student.id)).scalar() or 0
    active_students = db.query(func.count(Student.id)).filter(Student.status == "Active").scalar() or 0

    # Today's attendance
    today_sessions = db.query(AttendanceSession).filter(AttendanceSession.session_date == today).all()
    present_today_student_ids = set(s.student_id for s in today_sessions if s.status in ["Present", "Late"])
    present_today = len(present_today_student_ids)

    absent_today = max(0, active_students - present_today)
    today_pct = round((present_today / active_students * 100), 1) if active_students > 0 else 0.0

    # Currently inside library (checked in today, check_out_time IS NULL)
    currently_inside = db.query(func.count(AttendanceSession.id))\
        .filter(
            AttendanceSession.session_date == today,
            AttendanceSession.check_out_time.is_(None)
        ).scalar() or 0

    # Library metrics
    total_books_sum = db.query(func.sum(Book.total_copies)).scalar() or 0
    available_books_sum = db.query(func.sum(Book.available_copies)).scalar() or 0
    issued_books_count = db.query(func.count(BookIssue.id)).filter(BookIssue.status == "ISSUED").scalar() or 0
    
    overdue_books_count = db.query(func.count(BookIssue.id))\
        .filter(
            BookIssue.status.in_(["ISSUED", "OVERDUE"]),
            BookIssue.due_date < today,
            BookIssue.return_date.is_(None)
        ).scalar() or 0

    return {
        "total_students": total_students,
        "active_students": active_students,
        "present_today": present_today,
        "absent_today": absent_today,
        "currently_inside": currently_inside,
        "today_attendance_percentage": today_pct,
        "total_books": total_books_sum,
        "available_books": available_books_sum,
        "issued_books": issued_books_count,
        "overdue_books": overdue_books_count
    }

@router.get("/attendance-chart", response_model=AttendanceChartResponse)
def get_attendance_chart(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    active_students = db.query(func.count(Student.id)).filter(Student.status == "Active").scalar() or 1

    chart_points = []
    curr = start_date
    while curr <= end_date:
        present_count = db.query(func.count(func.distinct(AttendanceSession.student_id)))\
            .filter(AttendanceSession.session_date == curr).scalar() or 0
        
        absent_count = max(0, active_students - present_count)
        pct = round((present_count / active_students) * 100, 1)

        chart_points.append({
            "date": curr.strftime("%b %d"),
            "present": present_count,
            "absent": absent_count,
            "percentage": pct
        })
        curr += timedelta(days=1)

    return {
        "daily": chart_points,
        "period": f"Last {days} Days"
    }

@router.get("/library-summary", response_model=LibrarySummaryResponse)
def get_library_summary(
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    today = date.today()
    available = db.query(func.sum(Book.available_copies)).scalar() or 0
    issued = db.query(func.count(BookIssue.id)).filter(BookIssue.status == "ISSUED").scalar() or 0
    overdue = db.query(func.count(BookIssue.id))\
        .filter(BookIssue.due_date < today, BookIssue.return_date.is_(None)).scalar() or 0

    categories = db.query(BookCategory).all()
    cat_dist = {}
    for c in categories:
        count = db.query(func.sum(Book.total_copies)).filter(Book.category_id == c.id).scalar() or 0
        cat_dist[c.name] = count

    return {
        "available": available,
        "issued": issued,
        "overdue": overdue,
        "category_distribution": cat_dist
    }
