from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.core.audit import log_audit_event
from backend.app.core.dependencies import get_current_user
from backend.app.core.security import create_access_token, verify_password
from backend.app.database import get_db
from backend.app.models.institution import Institution
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest, TokenResponse, UserProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter((User.username == payload.user) | (User.email == payload.user))
        .first()
    )
    if not user or not verify_password(payload.pass_, user.hashed_password):
        # Record failed login attempt for audit
        log_audit_event(
            db=db,
            action="Signed in",
            actor_name=payload.user or "Unknown",
            actor_role="Anonymous",
            ref="—",
            result="Failed",
            details="Invalid username or password",
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    # Issue access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user.id, "role": user.role, "institution_id": user.institution_id},
        expires_delta=access_token_expires,
    )

    # Set HttpOnly cookie for browser sessions
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=not settings.DEBUG,
    )

    institution_name = None
    if user.institution_id:
        inst = db.query(Institution).filter(Institution.id == user.institution_id).first()
        if inst:
            institution_name = inst.name

    user_profile = UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        institution_id=user.institution_id,
        institution_name=institution_name,
    )

    # Record successful login audit event
    log_audit_event(
        db=db,
        action="Signed in",
        actor_name=user.full_name,
        actor_role=user.role,
        actor_id=user.id,
        institution_id=user.institution_id,
        ref="—",
        result="Success",
    )
    db.commit()

    return TokenResponse(access_token=token, token_type="bearer", user=user_profile)


@router.post("/logout")
def logout(response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    response.delete_cookie(key="access_token")
    log_audit_event(
        db=db,
        action="Signed out",
        actor_name=current_user.full_name,
        actor_role=current_user.role,
        actor_id=current_user.id,
        institution_id=current_user.institution_id,
        ref="—",
        result="Success",
    )
    db.commit()
    return {"message": "Successfully signed out."}


@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    institution_name = None
    if current_user.institution_id:
        inst = db.query(Institution).filter(Institution.id == current_user.institution_id).first()
        if inst:
            institution_name = inst.name

    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        institution_id=current_user.institution_id,
        institution_name=institution_name,
    )
