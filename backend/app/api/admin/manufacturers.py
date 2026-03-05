"""Admin Manufacturers API"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_session
from ...dependencies import AccessTokenBearer, RoleChecker
from ...services.admin_service import AdminService
from ...schemas.admin_schemas import (
    ManufacturerCreate,
    ManufacturerUpdate,
    ManufacturerResponse,
    ManufacturerListResponse,
)

admin_manufacturers_router = APIRouter(prefix="/manufacturers", tags=["Admin Manufacturers"])
require_admin = RoleChecker(["admin"])


@admin_manufacturers_router.get("", response_model=ManufacturerListResponse)
async def list_manufacturers(
    page: int = 1,
    page_size: int = 10,
    search: str = None,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """List all manufacturers with pagination and search"""
    manufacturers, total = await AdminService.list_manufacturers(session, page, page_size, search)
    total_pages = AdminService.calculate_total_pages(total, page_size)
    
    return ManufacturerListResponse(
        items=[ManufacturerResponse.model_validate(m) for m in manufacturers],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@admin_manufacturers_router.get("/{manufacturer_id}", response_model=ManufacturerResponse)
async def get_manufacturer(
    manufacturer_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Get a specific manufacturer by ID"""
    manufacturer = await AdminService.get_manufacturer(session, manufacturer_id)
    if not manufacturer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manufacturer not found")
    return ManufacturerResponse.model_validate(manufacturer)


@admin_manufacturers_router.post("", response_model=ManufacturerResponse, status_code=status.HTTP_201_CREATED)
async def create_manufacturer(
    data: ManufacturerCreate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Create a new manufacturer"""
    manufacturer = await AdminService.create_manufacturer(session, data)
    return ManufacturerResponse.model_validate(manufacturer)


@admin_manufacturers_router.put("/{manufacturer_id}", response_model=ManufacturerResponse)
async def update_manufacturer(
    manufacturer_id: UUID,
    data: ManufacturerUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Update a manufacturer"""
    manufacturer = await AdminService.update_manufacturer(session, manufacturer_id, data)
    if not manufacturer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manufacturer not found")
    return ManufacturerResponse.model_validate(manufacturer)


@admin_manufacturers_router.delete("/{manufacturer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_manufacturer(
    manufacturer_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Delete a manufacturer"""
    deleted = await AdminService.delete_manufacturer(session, manufacturer_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manufacturer not found")
    return None
