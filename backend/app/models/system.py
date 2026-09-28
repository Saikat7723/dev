from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    admin_email = Column(String(120), nullable=True)
    action = Column(String(100), nullable=False, index=True) # e.g., STUDENT_REGISTERED, ATTENDANCE_MANUAL_EDIT, BOOK_ISSUED
    target_type = Column(String(50), nullable=True) # e.g., Student, AttendanceSession, BookIssue
    target_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
