"""
Contact API Router

Provides endpoints for:
- Contacting manufacturers (with photos and technical documents)
- Contacting clients (with photos and intervention reports only)
- File upload for photos
"""

import os
import uuid as uuid_lib
import mimetypes
from typing import List, Optional
from uuid import UUID
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
)
from fastapi_mail import MessageSchema, MessageType
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_session
from ..dependencies import AccessTokenBearer, get_current_user
from ..db.models import User
from ..schemas.equipment_schemas import (
    ManufacturerContactRequest,
    ClientContactRequest,
    EmailSendResponse,
)
from ..services.contact_service import ContactService
from ..services.equipment_service import EquipmentService
from ..mail import mail, send_email_with_attachments
from ..celery_tasks import send_email


contact_router = APIRouter()


# Configuration
UPLOAD_DIR = Path("uploads")
PHOTOS_DIR = UPLOAD_DIR / "photos"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def collect_photo_attachments(photos: List[UploadFile]) -> List[dict]:
    """
    Process uploaded photos and return attachment dictionaries.
    
    Returns list of dicts with 'file', 'filename', and 'content_type'.
    """
    attachments = []
    
    for photo in photos:
        if not photo.content_type or photo.content_type not in ALLOWED_IMAGE_TYPES:
            continue

        content = await photo.read()
        if len(content) > MAX_FILE_SIZE:
            continue

        # Reset file position for potential re-reading
        await photo.seek(0)
        
        attachments.append({
            "file": content,
            "filename": photo.filename or f"photo_{uuid_lib.uuid4()}.jpg",
            "content_type": photo.content_type,
        })
    
    return attachments


def collect_file_attachments(file_paths: List[str]) -> List[dict]:
    """
    Read files from paths and return attachment dictionaries.
    """
    attachments = []
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            continue
            
        filename = os.path.basename(file_path)
        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        
        with open(file_path, "rb") as f:
            content = f.read()
        
        attachments.append({
            "file": content,
            "filename": filename,
            "content_type": content_type,
        })
    
    return attachments


def ensure_upload_dirs():
    """Ensure upload directories exist"""
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)


@contact_router.post("/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    intervention_id: Optional[UUID] = Form(None),
    _: dict = Depends(AccessTokenBearer()),
):
    """
    Upload a photo taken by the technician.
    
    Supports photos from:
    - Smartphone
    - Tablet
    - PC camera
    
    Returns the file path for use in email attachments.
    """
    ensure_upload_dirs()
    
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )

    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    # Generate unique filename
    file_ext = Path(file.filename or "photo").suffix or ".jpg"
    unique_filename = f"{uuid_lib.uuid4()}{file_ext}"
    
    # Create subdirectory for intervention if provided
    if intervention_id:
        save_dir = PHOTOS_DIR / str(intervention_id)
    else:
        save_dir = PHOTOS_DIR / "temp"
    
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / unique_filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": unique_filename,
        "file_path": str(file_path),
        "content_type": file.content_type,
        "size": len(content),
    }


@contact_router.post("/manufacturer", response_model=EmailSendResponse)
async def contact_manufacturer(
    equipment_id: UUID = Form(...),
    subject: str = Form(..., min_length=1, max_length=512),
    message: str = Form(..., min_length=1),
    technical_document_ids: Optional[str] = Form(None, description="Comma-separated UUIDs"),
    intervention_id: Optional[UUID] = Form(None),
    photos: List[UploadFile] = File(default=[]),
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
    current_user: User = Depends(get_current_user),
):
    """
    Send email to equipment manufacturer.
    
    Allowed attachments:
    - Photos taken by technician (smartphone, tablet, PC camera)
    - Technical documents from the system database
    
    This helps explain the failure to the manufacturer.
    """
    ensure_upload_dirs()
    
    # Parse technical document IDs
    doc_ids = []
    if technical_document_ids:
        try:
            doc_ids = [UUID(id.strip()) for id in technical_document_ids.split(",") if id.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid technical document ID format",
            )

    # Validate request
    validation = await ContactService.validate_manufacturer_contact(
        session, equipment_id, doc_ids
    )

    if "error" in validation:
        raise HTTPException(
            status_code=validation["status_code"],
            detail=validation["error"],
        )

    equipment = validation["equipment"]
    manufacturer_email = validation["manufacturer_email"]
    technical_documents = validation["documents"]

    # Get technician name
    technician_name = current_user.fullname or current_user.username

    # Build email body
    email_body = ContactService.build_manufacturer_email_body(
        equipment=equipment,
        message=message,
        technician_name=technician_name,
    )

    # Collect attachment paths
    attachment_paths = []

    # Add technical documents
    for doc in technical_documents:
        if os.path.exists(doc.file_path):
            attachment_paths.append(doc.file_path)

    # Save and add uploaded photos
    saved_photos = []
    for photo in photos:
        if photo.content_type not in ALLOWED_IMAGE_TYPES:
            continue

        content = await photo.read()
        if len(content) > MAX_FILE_SIZE:
            continue

        file_ext = Path(photo.filename or "photo").suffix or ".jpg"
        unique_filename = f"{uuid_lib.uuid4()}{file_ext}"
        
        if intervention_id:
            save_dir = PHOTOS_DIR / str(intervention_id)
        else:
            save_dir = PHOTOS_DIR / "temp"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        file_path = save_dir / unique_filename

        with open(file_path, "wb") as f:
            f.write(content)

        attachment_paths.append(str(file_path))
        saved_photos.append(str(file_path))

    # Send email with attachments
    try:
        # Build attachment list from paths
        attachments = collect_file_attachments(attachment_paths)
        
        # Send email with proper attachment handling
        await send_email_with_attachments(
            recipients=[manufacturer_email],
            subject=subject,
            body=email_body,
            attachments=attachments if attachments else None,
        )

        # Log email if intervention exists
        email_log = None
        if intervention_id:
            email_log = await ContactService.log_email(
                session=session,
                intervention_id=intervention_id,
                recipient_type="MANUFACTURER",
                recipient_email=manufacturer_email,
                subject=subject,
                body=message,
            )

        return EmailSendResponse(
            success=True,
            message=f"Email sent to manufacturer ({manufacturer_email})",
            email_log_id=email_log.id if email_log else None,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}",
        )


@contact_router.post("/client", response_model=EmailSendResponse)
async def contact_client(
    equipment_id: UUID = Form(...),
    subject: str = Form(..., min_length=1, max_length=512),
    message: str = Form(..., min_length=1),
    intervention_id: Optional[UUID] = Form(None),
    include_intervention_report: bool = Form(False),
    photos: List[UploadFile] = File(default=[]),
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(AccessTokenBearer()),
    current_user: User = Depends(get_current_user),
):
    """
    Send email to equipment client.
    
    Allowed attachments:
    - Photos taken by technician
    - Current intervention report (if one exists)
    
    NOT allowed:
    - Technical documents from the internal database
    """
    ensure_upload_dirs()

    # Validate request
    validation = await ContactService.validate_client_contact(
        session=session,
        equipment_id=equipment_id,
        intervention_id=intervention_id,
        include_intervention_report=include_intervention_report,
    )

    if "error" in validation:
        raise HTTPException(
            status_code=validation["status_code"],
            detail=validation["error"],
        )

    equipment = validation["equipment"]
    client_email = validation["client_email"]
    intervention = validation.get("intervention")

    # Get technician name
    technician_name = current_user.fullname or current_user.username

    # Build email body
    email_body = ContactService.build_client_email_body(
        equipment=equipment,
        message=message,
        technician_name=technician_name,
        include_intervention_info=include_intervention_report,
        intervention=intervention,
    )

    # Collect attachment paths (NO technical documents allowed)
    attachment_paths = []

    # Add intervention report if requested
    if include_intervention_report and intervention:
        # Check if there's a signature/report file
        if intervention.signature_image_path and os.path.exists(intervention.signature_image_path):
            attachment_paths.append(intervention.signature_image_path)

    # Save and add uploaded photos
    for photo in photos:
        if photo.content_type not in ALLOWED_IMAGE_TYPES:
            continue

        content = await photo.read()
        if len(content) > MAX_FILE_SIZE:
            continue

        file_ext = Path(photo.filename or "photo").suffix or ".jpg"
        unique_filename = f"{uuid_lib.uuid4()}{file_ext}"
        
        if intervention_id:
            save_dir = PHOTOS_DIR / str(intervention_id)
        else:
            save_dir = PHOTOS_DIR / "temp"
        
        save_dir.mkdir(parents=True, exist_ok=True)
        file_path = save_dir / unique_filename

        with open(file_path, "wb") as f:
            f.write(content)

        attachment_paths.append(str(file_path))

    # Send email
    try:
        # Build attachment list from paths
        attachments = collect_file_attachments(attachment_paths)
        
        await send_email_with_attachments(
            recipients=[client_email],
            subject=subject,
            body=email_body,
            attachments=attachments if attachments else None,
        )

        # Log email if intervention exists
        email_log = None
        if intervention_id:
            email_log = await ContactService.log_email(
                session=session,
                intervention_id=intervention_id,
                recipient_type="CLIENT",
                recipient_email=client_email,
                subject=subject,
                body=message,
            )

        return EmailSendResponse(
            success=True,
            message=f"Email sent to client ({client_email})",
            email_log_id=email_log.id if email_log else None,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}",
        )


@contact_router.get("/manufacturer/{equipment_id}/info")
async def get_manufacturer_contact_info(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
):
    """
    Get manufacturer contact information for an equipment.
    
    Returns email and phone contact details.
    """
    equipment = await EquipmentService.get_equipment_by_id(session, equipment_id)

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    if not equipment.manufacturer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No manufacturer associated with this equipment",
        )

    return {
        "manufacturer_name": equipment.manufacturer.name,
        "support_email": equipment.manufacturer.support_email,
        "support_phone": equipment.manufacturer.support_phone,
    }


@contact_router.get("/client/{equipment_id}/info")
async def get_client_contact_info(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
):
    """
    Get client contact information for an equipment.
    
    Returns email, phone, and address contact details.
    """
    equipment = await EquipmentService.get_equipment_by_id(session, equipment_id)

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    return {
        "client_name": equipment.client.name,
        "email": equipment.client.email,
        "phone": equipment.client.phone,
        "address": equipment.client.address,
    }
