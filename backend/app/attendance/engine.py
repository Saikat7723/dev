import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.attendance import AttendanceSession, AttendanceEvent, AttendanceSetting
from app.core.config import settings

logger = logging.getLogger("attendance.engine")

class AttendanceEngine:
    @staticmethod
    def get_setting(db: Session, key: str, default_val: Any) -> Any:
        setting = db.query(AttendanceSetting).filter(AttendanceSetting.setting_key == key).first()
        if setting:
            if isinstance(default_val, float):
                return float(setting.setting_value)
            elif isinstance(default_val, int):
                return int(setting.setting_value)
            return setting.setting_value
        return default_val

    @classmethod
    def process_recognition_event(
        cls,
        db: Session,
        student_id: int,
        confidence: float,
        camera_id: str,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        if timestamp is None:
            timestamp = datetime.utcnow()

        today_date = timestamp.date()

        # Load thresholds
        min_confidence = cls.get_setting(db, "FACE_RECOGNITION_THRESHOLD", settings.FACE_RECOGNITION_THRESHOLD)
        cooldown_sec = cls.get_setting(db, "ATTENDANCE_COOLDOWN_SECONDS", settings.ATTENDANCE_COOLDOWN_SECONDS)

        # 1. Validate confidence
        if confidence < min_confidence:
            event = AttendanceEvent(
                student_id=student_id,
                event_type="LOW_CONFIDENCE",
                timestamp=timestamp,
                confidence=confidence,
                camera_id=camera_id,
                raw_info=f"Confidence {confidence:.2f} below threshold {min_confidence:.2f}"
            )
            db.add(event)
            db.commit()
            return {
                "success": False,
                "action": "IGNORED_LOW_CONFIDENCE",
                "message": f"Confidence {confidence:.2f} below required threshold {min_confidence:.2f}"
            }

        # 2. Cooldown check - inspect most recent event for this student
        recent_event = db.query(AttendanceEvent)\
            .filter(AttendanceEvent.student_id == student_id)\
            .order_by(AttendanceEvent.timestamp.desc())\
            .first()

        if recent_event:
            elapsed_seconds = (timestamp - recent_event.timestamp).total_seconds()
            if elapsed_seconds < cooldown_sec:
                # In cooldown window
                event = AttendanceEvent(
                    student_id=student_id,
                    event_type="COOLDOWN_SKIPPED",
                    timestamp=timestamp,
                    confidence=confidence,
                    camera_id=camera_id,
                    raw_info=f"Ignored due to cooldown ({int(elapsed_seconds)}s < {cooldown_sec}s)"
                )
                db.add(event)
                db.commit()
                return {
                    "success": True,
                    "action": "COOLDOWN_ACTIVE",
                    "message": f"Recognized student, but in cooldown window ({int(elapsed_seconds)}s elapsed)"
                }

        # 3. Process Attendance Session (Check-In / Check-Out)
        student = db.query(Student).filter(Student.id == student_id, Student.status == "Active").first()
        if not student:
            return {
                "success": False,
                "action": "INACTIVE_STUDENT",
                "message": "Student is inactive or deleted"
            }

        # Check for open session today
        open_session = db.query(AttendanceSession)\
            .filter(
                AttendanceSession.student_id == student_id,
                AttendanceSession.session_date == today_date,
                AttendanceSession.check_out_time.is_(None)
            )\
            .order_by(AttendanceSession.check_in_time.desc())\
            .first()

        if open_session is None:
            # Create NEW Check-In Session
            new_session = AttendanceSession(
                student_id=student_id,
                session_date=today_date,
                check_in_time=timestamp,
                check_out_time=None,
                duration_minutes=0,
                status="Present",
                confidence=confidence,
                camera_id=camera_id
            )
            db.add(new_session)
            db.flush()

            # Record event
            event = AttendanceEvent(
                student_id=student_id,
                event_type="CHECK_IN",
                timestamp=timestamp,
                confidence=confidence,
                camera_id=camera_id,
                raw_info=f"Session #{new_session.id} Check-In created"
            )
            db.add(event)
            db.commit()

            return {
                "success": True,
                "action": "CHECK_IN",
                "message": f"Successfully checked in {student.full_name} ({student.student_id})",
                "student": {
                    "id": student.id,
                    "student_id": student.student_id,
                    "full_name": student.full_name,
                    "photo": student.profile_photo_path
                },
                "session_id": new_session.id,
                "timestamp": timestamp.isoformat()
            }
        else:
            # Complete Check-Out on open session if minimum interval (60 seconds) has elapsed
            duration_sec = (timestamp - open_session.check_in_time).total_seconds()
            if duration_sec < 60:
                # Too soon to check out
                return {
                    "success": True,
                    "action": "CHECK_IN_ALREADY_ACTIVE",
                    "message": f"{student.full_name} is already checked in"
                }

            open_session.check_out_time = timestamp
            open_session.duration_minutes = max(1, int(duration_sec / 60))
            db.add(open_session)

            # Record event
            event = AttendanceEvent(
                student_id=student_id,
                event_type="CHECK_OUT",
                timestamp=timestamp,
                confidence=confidence,
                camera_id=camera_id,
                raw_info=f"Session #{open_session.id} Check-Out (Duration: {open_session.duration_minutes}m)"
            )
            db.add(event)
            db.commit()

            return {
                "success": True,
                "action": "CHECK_OUT",
                "message": f"Successfully checked out {student.full_name} ({student.student_id})",
                "student": {
                    "id": student.id,
                    "student_id": student.student_id,
                    "full_name": student.full_name,
                    "photo": student.profile_photo_path
                },
                "session_id": open_session.id,
                "duration_minutes": open_session.duration_minutes,
                "timestamp": timestamp.isoformat()
            }
