from typing import List, Optional
from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.permissions import Role, check_permission, Permission
from backend.app.core.security import decode_access_token
from backend.app.database import get_db
from backend.app.models.user import User


def get_current_user(
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and validate current authenticated user.
    Supports Authorization: Bearer <token> or access_token cookie.
    Deny-by-default if unauthenticated.
    """
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or not found.",
        )

    return user


def require_roles(allowed_roles: List[str]):
    """Dependency enforcing role-based access control."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Check direct role match or system_admin override
        if current_user.role == Role.SYSTEM_ADMIN.value or current_user.role in allowed_roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}.",
        )
    return role_checker


def require_permission(perm: Permission):
    """Dependency enforcing specific granular permission."""
    def perm_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role == Role.SYSTEM_ADMIN.value or check_permission(current_user.role, perm):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Missing permission: {perm.value}.",
        )
    return perm_checker
