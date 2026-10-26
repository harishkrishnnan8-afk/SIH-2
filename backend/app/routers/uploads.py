import csv
import io
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user, require_permission
from backend.app.core.masking import sanitize_csv_cell
from backend.app.core.permissions import Permission, Role, require_institution_access
from backend.app.database import get_db
from backend.app.models.upload import UploadBatch, UploadRowResult
from backend.app.models.user import User
from backend.app.schemas.upload import CsvValidationResult, ImportBatchResponse, RowErrorResponse
from backend.app.services.csv_service import process_csv_upload

router = APIRouter(prefix="/uploads", tags=["CSV Uploads"])


@router.get("", response_model=List[ImportBatchResponse])
def list_batches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(UploadBatch)
    if current_user.role not in (Role.CENTRAL_REVIEWER.value, Role.SYSTEM_ADMIN.value):
        query = query.filter(UploadBatch.institution_id == current_user.institution_id)

    batches = query.order_by(UploadBatch.created_at.desc()).all()
    return [
        ImportBatchResponse(
            id=b.id,
            file=b.filename,
            uploadedBy=b.uploaded_by_name,
            at=b.created_at.isoformat(),
            total=b.total,
            accepted=b.accepted,
            rejected=b.rejected,
            status=b.status,
        )
        for b in batches
    ]


@router.get("/{batch_id}", response_model=ImportBatchResponse)
def get_batch(
    batch_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    batch = db.query(UploadBatch).filter(UploadBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload batch '{batch_id}' not found.",
        )

    require_institution_access(current_user, batch.institution_id)

    return ImportBatchResponse(
        id=batch.id,
        file=batch.filename,
        uploadedBy=batch.uploaded_by_name,
        at=batch.created_at.isoformat(),
        total=batch.total,
        accepted=batch.accepted,
        rejected=batch.rejected,
        status=batch.status,
    )


@router.get("/{batch_id}/errors", response_model=List[RowErrorResponse])
def get_batch_errors(
    batch_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    batch = db.query(UploadBatch).filter(UploadBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload batch '{batch_id}' not found.",
        )

    require_institution_access(current_user, batch.institution_id)

    errors = (
        db.query(UploadRowResult)
        .filter(UploadRowResult.batch_id == batch_id, UploadRowResult.is_error == True)
        .order_by(UploadRowResult.row_number.asc())
        .all()
    )

    return [
        RowErrorResponse(
            row=e.row_number,
            field=e.field or "",
            value=e.raw_value or "",
            rule=e.rule,
        )
        for e in errors
    ]


@router.get("/{batch_id}/errors.csv")
def download_batch_errors_csv(
    batch_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    batch = db.query(UploadBatch).filter(UploadBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")

    require_institution_access(current_user, batch.institution_id)

    errors = (
        db.query(UploadRowResult)
        .filter(UploadRowResult.batch_id == batch_id, UploadRowResult.is_error == True)
        .order_by(UploadRowResult.row_number.asc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["row", "field", "value", "rule"])
    for e in errors:
        writer.writerow([
            e.row_number,
            sanitize_csv_cell(e.field or ""),
            sanitize_csv_cell(e.raw_value or ""),
            sanitize_csv_cell(e.rule),
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{batch_id}_errors.csv"'},
    )


@router.post("", response_model=CsvValidationResult)
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission(Permission.IMPORT_CSV)),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV (.csv).",
        )

    target_inst = current_user.institution_id or "INS-001"
    content = await file.read()

    # File size validation (15MB limit)
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="CSV file exceeds maximum allowed size of 15MB.",
        )

    try:
        batch, errors = process_csv_upload(
            db=db,
            file_bytes=content,
            filename=file.filename,
            institution_id=target_inst,
            current_user=current_user,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return CsvValidationResult(
        accepted=batch.accepted,
        rejected=batch.rejected,
        total=batch.total,
        errors=[
            RowErrorResponse(
                row=err["row"],
                field=err["field"],
                value=err["value"],
                rule=err["rule"],
            )
            for err in errors
        ],
        batch_id=batch.id,
        persisted=True,
    )
