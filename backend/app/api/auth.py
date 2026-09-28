from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import Admin
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.core.security import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Admin).filter(
        (Admin.email == login_req.username_or_email)
    ).first()

    if not user or not verify_password(login_req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    token = create_access_token(data={"sub": user.email, "role": user.role.value, "id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/logout")
def logout(current_user: Admin = Depends(get_current_user)):
    return {"success": True, "message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: Admin = Depends(get_current_user)):
    return current_user
