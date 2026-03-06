"""
Intervention API Router

Provides endpoints for:
- Creating interventions
- Updating interventions
- Completing interventions
- Getting intervention details
- Getting intervention history by equipment
- Uploading intervention attachments (photos)
- Uploading signature
"""

import os
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_session
from ..dependencies import AccessTokenBearer, get_current_user
from ..db.models import User
from ..schemas.intervention_schemas import (
    InterventionCreate,
    InterventionUpdate,
    InterventionComplete,
    InterventionDetail,
    InterventionHistory,
    InterventionAttachmentOut,
)
from ..services.intervention_service import InterventionService

intervention_router = APIRouter()

# File upload directories
UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
PHOTOS_DIR = UPLOADS_DIR / "photos"
SIGNATURES_DIR = UPLOADS_DIR / "signatures"

# Ensure directories exist
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
SIGNATURES_DIR.mkdir(parents=True, exist_ok=True)


@intervention_router.post("", response_model=InterventionDetail, status_code=status.HTTP_201_CREATED)
async def create_intervention(
    data: InterventionCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new intervention.

    - Technician can create intervention for any equipment
    - Sets status to IN_PROGRESS automatically
    - Records start time
    """
    try:
        intervention = await InterventionService.create_intervention(
            session=session,
            equipment_id=data.equipment_id,
            technician_id=current_user.id,
            diagnostic=data.diagnostic,
            actions_taken=data.actions_taken,
        )

        # Refresh to load relationships
        intervention = await InterventionService.get_intervention_by_id(
            session, intervention.id
        )

        return InterventionDetail(
            id=intervention.id,
            equipment_id=intervention.equipment_id,
            equipment_serial=intervention.equipment.serial_number,
            equipment_brand=intervention.equipment.brand,
            equipment_model=intervention.equipment.model,
            technician_id=intervention.technician_id,
            technician_name=intervention.technician.fullname,
            status=intervention.status,
            diagnostic=intervention.diagnostic,
            actions_taken=intervention.actions_taken,
            result=intervention.result,
            failure_reason=intervention.failure_reason,
            started_at=intervention.started_at,
            completed_at=intervention.completed_at,
            signature_image_path=intervention.signature_image_path,
            created_at=intervention.created_at,
            attachments=[
                InterventionAttachmentOut(
                    id=att.id,
                    intervention_id=att.intervention_id,
                    file_path=att.file_path,
                    attachment_type=att.attachment_type,
                    created_at=att.created_at,
                )
                for att in intervention.attachments
            ],
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create intervention: {str(e)}",
        )


@intervention_router.get("/{intervention_id}", response_model=InterventionDetail)
async def get_intervention(
    intervention_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
):
    """Get intervention details by ID"""
    intervention = await InterventionService.get_intervention_by_id(
        session, intervention_id
    )

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found",
        )

    return InterventionDetail(
        id=intervention.id,
        equipment_id=intervention.equipment_id,
        equipment_serial=intervention.equipment.serial_number,
        equipment_brand=intervention.equipment.brand,
        equipment_model=intervention.equipment.model,
        technician_id=intervention.technician_id,
        technician_name=intervention.technician.fullname,
        status=intervention.status,
        diagnostic=intervention.diagnostic,
        actions_taken=intervention.actions_taken,
        result=intervention.result,
        failure_reason=intervention.failure_reason,
        started_at=intervention.started_at,
        completed_at=intervention.completed_at,
        signature_image_path=intervention.signature_image_path,
        created_at=intervention.created_at,
        attachments=[
            InterventionAttachmentOut(
                id=att.id,
                intervention_id=att.intervention_id,
                file_path=att.file_path,
                attachment_type=att.attachment_type,
                created_at=att.created_at,
            )
            for att in intervention.attachments
        ],
    )


@intervention_router.put("/{intervention_id}", response_model=InterventionDetail)
async def update_intervention(
    intervention_id: UUID,
    data: InterventionUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Update intervention fields.

    - Only technician who created the intervention can update it
    - Cannot update completed interventions
    """
    intervention = await InterventionService.get_intervention_by_id(
        session, intervention_id
    )

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found",
        )

    # Check authorization (only creator or admin can update)
    is_admin = any(role.name == "admin" for role in current_user.roles)
    if intervention.technician_id != current_user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own interventions",
        )

    # Prevent updating completed interventions
    if intervention.status in ["COMPLETED", "NOT_REPAIRED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update completed intervention",
        )

    updated_intervention = await InterventionService.update_intervention(
        session=session,
        intervention_id=intervention_id,
        diagnostic=data.diagnostic,
        actions_taken=data.actions_taken,
        result=data.result,
        failure_reason=data.failure_reason,
        status=data.status,
    )

    return InterventionDetail(
        id=updated_intervention.id,
        equipment_id=updated_intervention.equipment_id,
        equipment_serial=updated_intervention.equipment.serial_number,
        equipment_brand=updated_intervention.equipment.brand,
        equipment_model=updated_intervention.equipment.model,
        technician_id=updated_intervention.technician_id,
        technician_name=updated_intervention.technician.fullname,
        status=updated_intervention.status,
        diagnostic=updated_intervention.diagnostic,
        actions_taken=updated_intervention.actions_taken,
        result=updated_intervention.result,
        failure_reason=updated_intervention.failure_reason,
        started_at=updated_intervention.started_at,
        completed_at=updated_intervention.completed_at,
        signature_image_path=updated_intervention.signature_image_path,
        created_at=updated_intervention.created_at,
        attachments=[
            InterventionAttachmentOut(
                id=att.id,
                intervention_id=att.intervention_id,
                file_path=att.file_path,
                attachment_type=att.attachment_type,
                created_at=att.created_at,
            )
            for att in updated_intervention.attachments
        ],
    )


@intervention_router.post("/{intervention_id}/complete", response_model=InterventionDetail)
async def complete_intervention(
    intervention_id: UUID,
    data: InterventionComplete,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Complete an intervention.

    - Sets status to COMPLETED or NOT_REPAIRED
    - Records completion time
    - If NOT_REPAIRED, failure_reason is required
    """
    intervention = await InterventionService.get_intervention_by_id(
        session, intervention_id
    )

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found",
        )

    # Check authorization
    is_admin = any(role.name == "admin" for role in current_user.roles)
    if intervention.technician_id != current_user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only complete your own interventions",
        )

    # Check if already completed
    if intervention.status in ["COMPLETED", "NOT_REPAIRED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Intervention is already completed",
        )

    try:
        completed = await InterventionService.complete_intervention(
            session=session,
            intervention_id=intervention_id,
            status=data.status,
            result=data.result,
            failure_reason=data.failure_reason,
        )

        return InterventionDetail(
            id=completed.id,
            equipment_id=completed.equipment_id,
            equipment_serial=completed.equipment.serial_number,
            equipment_brand=completed.equipment.brand,
            equipment_model=completed.equipment.model,
            technician_id=completed.technician_id,
            technician_name=completed.technician.fullname,
            status=completed.status,
            diagnostic=completed.diagnostic,
            actions_taken=completed.actions_taken,
            result=completed.result,
            failure_reason=completed.failure_reason,
            started_at=completed.started_at,
            completed_at=completed.completed_at,
            signature_image_path=completed.signature_image_path,
            created_at=completed.created_at,
            attachments=[
                InterventionAttachmentOut(
                    id=att.id,
                    intervention_id=att.intervention_id,
                    file_path=att.file_path,
                    attachment_type=att.attachment_type,
                    created_at=att.created_at,
                )
                for att in completed.attachments
            ],
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@intervention_router.get("/equipment/{equipment_id}/history", response_model=List[InterventionHistory])
async def get_equipment_intervention_history(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
):
    """Get intervention history for an equipment"""
    interventions = await InterventionService.get_interventions_by_equipment(
        session, equipment_id
    )

    return [
        InterventionHistory(
            id=intervention.id,
            technician_name=intervention.technician.fullname,
            status=intervention.status,
            diagnostic=intervention.diagnostic,
            result=intervention.result,
            started_at=intervention.started_at,
            completed_at=intervention.completed_at,
            created_at=intervention.created_at,
        )
        for intervention in interventions
    ]


@intervention_router.get("/equipment/{equipment_id}/active", response_model=Optional[InterventionDetail])
async def get_active_intervention_for_equipment(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
):
    """Get active (IN_PROGRESS) intervention for equipment, if any"""
    intervention = await InterventionService.get_active_intervention_for_equipment(
        session, equipment_id
    )

    if not intervention:
        return None

    return InterventionDetail(
        id=intervention.id,
        equipment_id=intervention.equipment_id,
        equipment_serial=intervention.equipment.serial_number,
        equipment_brand=intervention.equipment.brand,
        equipment_model=intervention.equipment.model,
        technician_id=intervention.technician_id,
        technician_name=intervention.technician.fullname,
        status=intervention.status,
        diagnostic=intervention.diagnostic,
        actions_taken=intervention.actions_taken,
        result=intervention.result,
        failure_reason=intervention.failure_reason,
        started_at=intervention.started_at,
        completed_at=intervention.completed_at,
        signature_image_path=intervention.signature_image_path,
        created_at=intervention.created_at,
        attachments=[
            InterventionAttachmentOut(
                id=att.id,
                intervention_id=att.intervention_id,
                file_path=att.file_path,
                attachment_type=att.attachment_type,
                created_at=att.created_at,
            )
            for att in intervention.attachments
        ],
    )


@intervention_router.post("/{intervention_id}/upload-photo", response_model=InterventionAttachmentOut)
async def upload_intervention_photo(
    intervention_id: UUID,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a photo attachment for an intervention.

    Supports: JPG, PNG, HEIC
    Max size: 10MB
    """
    # Validate intervention exists and user has access
    intervention = await InterventionService.get_intervention_by_id(
        session, intervention_id
    )

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found",
        )

    is_admin = any(role.name == "admin" for role in current_user.roles)
    if intervention.technician_id != current_user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload photos to your own interventions",
        )

    # Validate file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".heic"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}",
        )

    # Create intervention-specific directory
    intervention_dir = PHOTOS_DIR / str(intervention_id)
    intervention_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    import uuid
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = intervention_dir / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )

    # Create attachment record
    relative_path = f"uploads/photos/{intervention_id}/{unique_filename}"
    attachment = await InterventionService.add_attachment(
        session=session,
        intervention_id=intervention_id,
        file_path=relative_path,
        attachment_type="PHOTO",
    )

    return InterventionAttachmentOut(
        id=attachment.id,
        intervention_id=attachment.intervention_id,
        file_path=attachment.file_path,
        attachment_type=attachment.attachment_type,
        created_at=attachment.created_at,
    )


@intervention_router.post("/{intervention_id}/upload-signature")
async def upload_signature(
    intervention_id: UUID,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Upload technician signature for intervention.

    Supports: PNG
    """
    # Validate intervention exists and user has access
    intervention = await InterventionService.get_intervention_by_id(
        session, intervention_id
    )

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found",
        )

    is_admin = any(role.name == "admin" for role in current_user.roles)
    if intervention.technician_id != current_user.id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload signature to your own interventions",
        )

    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext != ".png":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signature must be PNG format",
        )

    # Generate unique filename
    import uuid
    unique_filename = f"signature_{intervention_id}_{uuid.uuid4()}.png"
    file_path = SIGNATURES_DIR / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save signature: {str(e)}",
        )

    # Update intervention with signature path
    relative_path = f"uploads/signatures/{unique_filename}"
    intervention.signature_image_path = relative_path

    await session.commit()

    return {"message": "Signature uploaded successfully", "file_path": relative_path}

