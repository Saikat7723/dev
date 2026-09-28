import os
import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.session import get_db
from app.models.student import Student, StudentFaceProfile
from app.models.academic import Department, Course
from app.models.system import AuditLog
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.core.security import get_current_user, Admin
from app.core.config import settings
from app.face_recognition.engine import face_engine

router = APIRouter(prefix="/students", tags=["Students"])
logger = logging.getLogger("api.students")

@router.get("", response_model=List[StudentResponse])
def list_students(
    search: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    course_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    query = db.query(Student)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Student.full_name.ilike(search_term),
                Student.student_id.ilike(search_term),
                Student.email.ilike(search_term)
            )
        )

    if department_id:
        query = query.filter(Student.department_id == department_id)
    if course_id:
        query = query.filter(Student.course_id == course_id)
    if status_filter:
        query = query.filter(Student.status == status_filter)

    students = query.order_by(Student.created_at.desc()).offset(skip).limit(limit).all()

    # Annotate has_face_profile
    result = []
    for s in students:
        resp = StudentResponse.model_validate(s)
        resp.has_face_profile = bool(s.face_profile is not None and s.face_profile.is_active)
        result.append(resp)

    return result

@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    # Check duplicate student_id or email
    existing_id = db.query(Student).filter(Student.student_id == student_in.student_id).first()
    if existing_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student ID / Roll Number '{student_in.student_id}' already exists."
        )

    existing_email = db.query(Student).filter(Student.email == student_in.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student Email '{student_in.email}' already exists."
        )

    student = Student(**student_in.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)

    # Log action
    audit = AuditLog(
        admin_id=current_user.id,
        admin_email=current_user.email,
        action="STUDENT_CREATE",
        target_type="Student",
        target_id=str(student.id),
        details=f"Created student {student.full_name} ({student.student_id})"
    )
    db.add(audit)
    db.commit()

    resp = StudentResponse.model_validate(student)
    resp.has_face_profile = False
    return resp

@router.get("/{id}", response_model=StudentResponse)
def get_student(id: int, db: Session = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    resp = StudentResponse.model_validate(student)
    resp.has_face_profile = bool(student.face_profile is not None and student.face_profile.is_active)
    return resp

@router.put("/{id}", response_model=StudentResponse)
def update_student(
    id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = student_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(student, field, val)

    db.add(student)
    db.commit()
    db.refresh(student)

    audit = AuditLog(
        admin_id=current_user.id,
        admin_email=current_user.email,
        action="STUDENT_UPDATE",
        target_type="Student",
        target_id=str(student.id),
        details=f"Updated student {student.full_name}"
    )
    db.add(audit)
    db.commit()

    resp = StudentResponse.model_validate(student)
    resp.has_face_profile = bool(student.face_profile is not None and student.face_profile.is_active)
    return resp

@router.delete("/{id}")
def delete_student(id: int, db: Session = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Soft delete / set status to Inactive
    student.status = "Inactive"
    if student.face_profile:
        student.face_profile.is_active = False

    db.add(student)
    db.commit()

    audit = AuditLog(
        admin_id=current_user.id,
        admin_email=current_user.email,
        action="STUDENT_DEACTIVATE",
        target_type="Student",
        target_id=str(student.id),
        details=f"Deactivated student {student.full_name}"
    )
    db.add(audit)
    db.commit()

    return {"success": True, "message": f"Student {student.full_name} deactivated successfully"}

@router.post("/{id}/photo", response_model=StudentResponse)
async def upload_student_photo(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    """
    Upload and validate student profile photo.
    Validates face visibility: rejects images with no detectable face or multiple faces.
    Extracts face embedding vector and updates StudentFaceProfile.
    """
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # 1. Detect faces
    faces = face_engine.detect_faces(image_bytes)
    if len(faces) == 0:
        raise HTTPException(
            status_code=400,
            detail="FACE_VERIFICATION_FAILED: No face detected in the photo. Please capture a clear face photo."
        )
    elif len(faces) > 1:
        raise HTTPException(
            status_code=400,
            detail=f"FACE_VERIFICATION_FAILED: Multiple faces ({len(faces)}) detected in photo. Ensure only 1 student is in frame."
        )

    # 2. Extract embedding vector
    try:
        bbox = faces[0]
        embedding = face_engine.extract_embedding(image_bytes, face_bbox=bbox)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not extract face embedding: {str(e)}")

    # 3. Save profile image to external storage directory
    os.makedirs(settings.PROFILES_DIR, exist_ok=True)
    filename = f"student_{student.student_id}_{uuid.uuid4().hex[:8]}.jpg"
    filepath = os.path.join(settings.PROFILES_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    # Normalize relative image path URL
    rel_path = f"/uploads/profiles/{filename}"

    # 4. Update Student and StudentFaceProfile in MySQL
    student.profile_photo_path = rel_path
    db.add(student)

    # Upsert StudentFaceProfile
    face_profile = db.query(StudentFaceProfile).filter(StudentFaceProfile.student_id == student.id).first()
    if face_profile:
        face_profile.embedding_vector = embedding
        face_profile.face_bounding_box = {"x": bbox[0], "y": bbox[1], "w": bbox[2], "h": bbox[3]}
        face_profile.reference_image_path = rel_path
        face_profile.is_active = True
    else:
        face_profile = StudentFaceProfile(
            student_id=student.id,
            embedding_vector=embedding,
            face_bounding_box={"x": bbox[0], "y": bbox[1], "w": bbox[2], "h": bbox[3]},
            reference_image_path=rel_path,
            is_active=True
        )
        db.add(face_profile)

    db.commit()
    db.refresh(student)

    audit = AuditLog(
        admin_id=current_user.id,
        admin_email=current_user.email,
        action="STUDENT_FACE_REGISTER",
        target_type="Student",
        target_id=str(student.id),
        details=f"Registered face embedding & photo for {student.full_name}"
    )
    db.add(audit)
    db.commit()

    resp = StudentResponse.model_validate(student)
    resp.has_face_profile = True
    return resp
