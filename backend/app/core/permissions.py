from enum import Enum
from typing import List, Set
from fastapi import HTTPException, status


class Role(str, Enum):
    INSTITUTION_OPERATOR = "institution_operator"
    INSTITUTION_ADMIN = "institution_admin"
    CENTRAL_REVIEWER = "central_reviewer"
    AUTHORIZED_VERIFIER = "authorized_verifier"
    SYSTEM_ADMIN = "system_admin"
    # Also support alias used in Lovable frontend:
    DATA_OFFICER = "data_officer"


class Permission(str, Enum):
    VIEW_STUDENTS = "students:view"
    CREATE_STUDENT = "students:create"
    EDIT_STUDENT = "students:edit"
    IMPORT_CSV = "csv:import"
    VIEW_FINDINGS = "findings:view"
    REVIEW_FINDING = "findings:review"
    CONFIGURE_INTAKE = "intake:configure"
    VERIFY_APAAR = "apaar:verify"
    EXPORT_REPORTS = "reports:export"
    VIEW_AUDIT = "audit:view"
    MANAGE_INSTITUTIONS = "institutions:manage"
    MANAGE_ROLES = "roles:manage"


ROLE_PERMISSIONS: dict[str, Set[Permission]] = {
    Role.INSTITUTION_OPERATOR: {
        Permission.VIEW_STUDENTS,
        Permission.CREATE_STUDENT,
        Permission.EDIT_STUDENT,
        Permission.IMPORT_CSV,
        Permission.VIEW_FINDINGS,
        Permission.VERIFY_APAAR,
        Permission.EXPORT_REPORTS,
    },
    Role.DATA_OFFICER: {
        Permission.VIEW_STUDENTS,
        Permission.CREATE_STUDENT,
        Permission.EDIT_STUDENT,
        Permission.IMPORT_CSV,
        Permission.VIEW_FINDINGS,
        Permission.VERIFY_APAAR,
        Permission.EXPORT_REPORTS,
    },
    Role.INSTITUTION_ADMIN: {
        Permission.VIEW_STUDENTS,
        Permission.CREATE_STUDENT,
        Permission.EDIT_STUDENT,
        Permission.IMPORT_CSV,
        Permission.VIEW_FINDINGS,
        Permission.REVIEW_FINDING,
        Permission.CONFIGURE_INTAKE,
        Permission.VERIFY_APAAR,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_AUDIT,
    },
    Role.CENTRAL_REVIEWER: {
        Permission.VIEW_STUDENTS,
        Permission.VIEW_FINDINGS,
        Permission.REVIEW_FINDING,
        Permission.VERIFY_APAAR,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_AUDIT,
    },
    Role.AUTHORIZED_VERIFIER: {
        Permission.VERIFY_APAAR,
        Permission.VIEW_STUDENTS,
    },
    Role.SYSTEM_ADMIN: {
        Permission.VIEW_STUDENTS,
        Permission.CREATE_STUDENT,
        Permission.EDIT_STUDENT,
        Permission.IMPORT_CSV,
        Permission.VIEW_FINDINGS,
        Permission.REVIEW_FINDING,
        Permission.CONFIGURE_INTAKE,
        Permission.VERIFY_APAAR,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_AUDIT,
        Permission.MANAGE_INSTITUTIONS,
        Permission.MANAGE_ROLES,
    },
}


def check_permission(user_role: str, permission: Permission) -> bool:
    """Check if given role has the requested permission."""
    permissions = ROLE_PERMISSIONS.get(user_role, set())
    return permission in permissions


def require_institution_access(current_user, target_institution_id: str):
    """
    Enforce tenant isolation:
    Non-central/system users can only access records matching their own institution.
    """
    if current_user.role in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
        return True
    if current_user.institution_id != target_institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot access data from another institution.",
        )
    return True
