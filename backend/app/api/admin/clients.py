"""Admin Clients API"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_session
from ...dependencies import AccessTokenBearer, RoleChecker
from ...services.admin_service import AdminService
from ...schemas.admin_schemas import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
)

admin_clients_router = APIRouter(prefix="/clients", tags=["Admin Clients"])
require_admin = RoleChecker(["admin"])


@admin_clients_router.get("", response_model=ClientListResponse)
async def list_clients(
    page: int = 1,
    page_size: int = 10,
    search: str = None,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """List all clients with pagination and search"""
    clients, total = await AdminService.list_clients(session, page, page_size, search)
    total_pages = AdminService.calculate_total_pages(total, page_size)
    
    return ClientListResponse(
        items=[ClientResponse.model_validate(c) for c in clients],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@admin_clients_router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Get a specific client by ID"""
    client = await AdminService.get_client(session, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return ClientResponse.model_validate(client)


@admin_clients_router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: ClientCreate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Create a new client"""
    client = await AdminService.create_client(session, data)
    return ClientResponse.model_validate(client)


@admin_clients_router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    data: ClientUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Update a client"""
    client = await AdminService.update_client(session, client_id, data)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return ClientResponse.model_validate(client)


@admin_clients_router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Delete a client"""
    deleted = await AdminService.delete_client(session, client_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return None
