from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date

class DashboardSummaryResponse(BaseModel):
    total_students: int
    active_students: int
    present_today: int
    absent_today: int
    currently_inside: int
    today_attendance_percentage: float
    total_books: int
    available_books: int
    issued_books: int
    overdue_books: int

class DailyAttendancePoint(BaseModel):
    date: str
    present: int
    absent: int
    percentage: float

class AttendanceChartResponse(BaseModel):
    daily: List[DailyAttendancePoint]
    period: str

class LibrarySummaryResponse(BaseModel):
    available: int
    issued: int
    overdue: int
    category_distribution: Dict[str, int]
