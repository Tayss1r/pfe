"""Admin Equipment API"""
import os
import uuid as uuid_lib
from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_session
from ...dependencies import AccessTokenBearer, RoleChecker
from ...services.admin_service import AdminService
from ...schemas.admin_schemas import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentListResponse,
)

admin_equipment_router = APIRouter(prefix="/equipment", tags=["Admin Equipment"])
require_admin = RoleChecker(["admin"])

UPLOAD_DIR = Path("uploads/equipment")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def ensure_upload_dir():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@admin_equipment_router.get("", response_model=EquipmentListResponse)
async def list_equipment(
    page: int = 1,
    page_size: int = 10,
    search: str = None,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """List all equipment with pagination and search"""
    equipment_list, total = await AdminService.list_equipment(session, page, page_size, search)
    total_pages = AdminService.calculate_total_pages(total, page_size)
    
    items = []
    for eq in equipment_list:
        items.append(EquipmentResponse(
            id=eq.id,
            serial_number=eq.serial_number,
            brand=eq.brand,
            model=eq.model,
            type=eq.type,
            image=eq.image,
            client_id=eq.client_id,
            client_name=eq.client.name if eq.client else "N/A",
            manufacturer_id=eq.manufacturer_id,
            manufacturer_name=eq.manufacturer.name if eq.manufacturer else None,
            created_at=eq.created_at,
            updated_at=eq.updated_at,
        ))
    
    return EquipmentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@admin_equipment_router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Get specific equipment by ID"""
    eq = await AdminService.get_equipment(session, equipment_id)
    if not eq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    
    return EquipmentResponse(
        id=eq.id,
        serial_number=eq.serial_number,
        brand=eq.brand,
        model=eq.model,
        type=eq.type,
        image=eq.image,
        client_id=eq.client_id,
        client_name=eq.client.name if eq.client else "N/A",
        manufacturer_id=eq.manufacturer_id,
        manufacturer_name=eq.manufacturer.name if eq.manufacturer else None,
        created_at=eq.created_at,
        updated_at=eq.updated_at,
    )


@admin_equipment_router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    data: EquipmentCreate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Create new equipment"""
    try:
        eq = await AdminService.create_equipment(session, data)
        return EquipmentResponse(
            id=eq.id,
            serial_number=eq.serial_number,
            brand=eq.brand,
            model=eq.model,
            type=eq.type,
            image=eq.image,
            client_id=eq.client_id,
            client_name=eq.client.name if eq.client else "N/A",
            manufacturer_id=eq.manufacturer_id,
            manufacturer_name=eq.manufacturer.name if eq.manufacturer else None,
            created_at=eq.created_at,
            updated_at=eq.updated_at,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@admin_equipment_router.put("/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(
    equipment_id: UUID,
    data: EquipmentUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Update equipment"""
    eq = await AdminService.update_equipment(session, equipment_id, data)
    if not eq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    
    return EquipmentResponse(
        id=eq.id,
        serial_number=eq.serial_number,
        brand=eq.brand,
        model=eq.model,
        type=eq.type,
        image=eq.image,
        client_id=eq.client_id,
        client_name=eq.client.name if eq.client else "N/A",
        manufacturer_id=eq.manufacturer_id,
        manufacturer_name=eq.manufacturer.name if eq.manufacturer else None,
        created_at=eq.created_at,
        updated_at=eq.updated_at,
    )


@admin_equipment_router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Delete equipment"""
    deleted = await AdminService.delete_equipment(session, equipment_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    return None


@admin_equipment_router.post("/{equipment_id}/image")
async def upload_equipment_image(
    equipment_id: UUID,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Upload image for equipment"""
    ensure_upload_dir()
    
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )
    
    # Read and validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum: {MAX_FILE_SIZE // (1024*1024)}MB",
        )
    
    # Generate unique filename
    ext = Path(file.filename or "image").suffix or ".jpg"
    filename = f"{equipment_id}_{uuid_lib.uuid4()}{ext}"
    file_path = UPLOAD_DIR / filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Update equipment image path
    from ...schemas.admin_schemas import EquipmentUpdate
    await AdminService.update_equipment(
        session, equipment_id, EquipmentUpdate(image=str(file_path))
    )
    
    return {"filename": filename, "path": str(file_path)}
