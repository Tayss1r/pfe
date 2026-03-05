"""Admin Spare Parts API"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_session
from ...dependencies import AccessTokenBearer, RoleChecker
from ...services.admin_service import AdminService
from ...schemas.admin_schemas import (
    SparePartCreate,
    SparePartUpdate,
    SparePartResponse,
    SparePartListResponse,
)

admin_spare_parts_router = APIRouter(prefix="/spare-parts", tags=["Admin Spare Parts"])
require_admin = RoleChecker(["admin"])


@admin_spare_parts_router.get("", response_model=SparePartListResponse)
async def list_spare_parts(
    page: int = 1,
    page_size: int = 10,
    equipment_id: Optional[UUID] = None,
    search: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """List all spare parts with pagination"""
    spare_parts, total = await AdminService.list_spare_parts(
        session, page, page_size, equipment_id, search
    )
    total_pages = AdminService.calculate_total_pages(total, page_size)
    
    items = []
    for sp in spare_parts:
        items.append(SparePartResponse(
            id=sp.id,
            equipment_id=sp.equipment_id,
            equipment_serial=sp.equipment.serial_number if sp.equipment else "N/A",
            name=sp.name,
            reference_code=sp.reference_code,
            description=sp.description,
            image=sp.image,
            created_at=sp.created_at,
        ))
    
    return SparePartListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@admin_spare_parts_router.get("/{spare_part_id}", response_model=SparePartResponse)
async def get_spare_part(
    spare_part_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Get a specific spare part by ID"""
    sp = await AdminService.get_spare_part(session, spare_part_id)
    if not sp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spare part not found")
    
    return SparePartResponse(
        id=sp.id,
        equipment_id=sp.equipment_id,
        equipment_serial=sp.equipment.serial_number if sp.equipment else "N/A",
        name=sp.name,
        reference_code=sp.reference_code,
        description=sp.description,
        image=sp.image,
        created_at=sp.created_at,
    )


@admin_spare_parts_router.post("", response_model=SparePartResponse, status_code=status.HTTP_201_CREATED)
async def create_spare_part(
    data: SparePartCreate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Create a new spare part"""
    try:
        sp = await AdminService.create_spare_part(session, data)
        return SparePartResponse(
            id=sp.id,
            equipment_id=sp.equipment_id,
            equipment_serial=sp.equipment.serial_number if sp.equipment else "N/A",
            name=sp.name,
            reference_code=sp.reference_code,
            description=sp.description,
            image=sp.image,
            created_at=sp.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@admin_spare_parts_router.put("/{spare_part_id}", response_model=SparePartResponse)
async def update_spare_part(
    spare_part_id: UUID,
    data: SparePartUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Update a spare part"""
    sp = await AdminService.update_spare_part(session, spare_part_id, data)
    if not sp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spare part not found")
    
    return SparePartResponse(
        id=sp.id,
        equipment_id=sp.equipment_id,
        equipment_serial=sp.equipment.serial_number if sp.equipment else "N/A",
        name=sp.name,
        reference_code=sp.reference_code,
        description=sp.description,
        image=sp.image,
        created_at=sp.created_at,
    )


@admin_spare_parts_router.delete("/{spare_part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spare_part(
    spare_part_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Delete a spare part"""
    deleted = await AdminService.delete_spare_part(session, spare_part_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spare part not found")
    return None
