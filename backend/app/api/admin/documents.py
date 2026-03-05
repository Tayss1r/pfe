"""Admin Technical Documents API"""
import uuid as uuid_lib
from uuid import UUID
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_session
from ...dependencies import AccessTokenBearer, RoleChecker
from ...services.admin_service import AdminService
from ...schemas.admin_schemas import (
    DocumentResponse,
    DocumentListResponse,
)

admin_documents_router = APIRouter(prefix="/documents", tags=["Admin Documents"])
require_admin = RoleChecker(["admin"])

UPLOAD_DIR = Path("uploads/documents")
ALLOWED_TYPES = {
    "application/pdf": "PDF",
    "video/mp4": "VIDEO",
    "video/webm": "VIDEO",
    "video/quicktime": "VIDEO",
    "image/jpeg": "IMAGE",
    "image/png": "IMAGE",
    "image/gif": "IMAGE",
    "image/webp": "IMAGE",
}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB for videos


def ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@admin_documents_router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = 1,
    page_size: int = 10,
    equipment_id: Optional[UUID] = None,
    search: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """List all documents with pagination"""
    documents, total = await AdminService.list_documents(
        session, page, page_size, equipment_id, search
    )
    total_pages = AdminService.calculate_total_pages(total, page_size)
    
    items = []
    for doc in documents:
        items.append(DocumentResponse(
            id=doc.id,
            equipment_id=doc.equipment_id,
            equipment_serial=doc.equipment.serial_number if doc.equipment else "N/A",
            title=doc.title,
            file_path=doc.file_path,
            document_type=doc.document_type,
            created_at=doc.created_at,
        ))
    
    return DocumentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@admin_documents_router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Get a specific document by ID"""
    doc = await AdminService.get_document(session, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    return DocumentResponse(
        id=doc.id,
        equipment_id=doc.equipment_id,
        equipment_serial=doc.equipment.serial_number if doc.equipment else "N/A",
        title=doc.title,
        file_path=doc.file_path,
        document_type=doc.document_type,
        created_at=doc.created_at,
    )


@admin_documents_router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    equipment_id: UUID = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Upload a new document"""
    ensure_upload_dir()
    
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: PDF, IMAGE, VIDEO",
        )
    
    document_type = ALLOWED_TYPES[file.content_type]
    
    # Read content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum: {MAX_FILE_SIZE // (1024*1024)}MB",
        )
    
    # Generate filename and save
    ext = Path(file.filename or "file").suffix
    filename = f"{equipment_id}_{uuid_lib.uuid4()}{ext}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create document record
    doc = await AdminService.create_document(
        session,
        equipment_id=equipment_id,
        title=title,
        file_path=str(file_path),
        document_type=document_type,
    )
    
    return DocumentResponse(
        id=doc.id,
        equipment_id=doc.equipment_id,
        equipment_serial=doc.equipment.serial_number if doc.equipment else "N/A",
        title=doc.title,
        file_path=doc.file_path,
        document_type=doc.document_type,
        created_at=doc.created_at,
    )


@admin_documents_router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Delete a document"""
    # Get document first to delete file
    doc = await AdminService.get_document(session, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    # Delete file if exists
    if doc.file_path and Path(doc.file_path).exists():
        Path(doc.file_path).unlink()
    
    # Delete record
    await AdminService.delete_document(session, document_id)
    return None
