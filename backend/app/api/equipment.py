"""
Equipment API Router

Provides endpoints for:
- Equipment search with multiple filters
- Equipment detail/dashboard view
- Technical documents access
- Spare parts list
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_session
from ..dependencies import AccessTokenBearer, get_current_user
from ..db.models import User
from ..schemas.equipment_schemas import (
    EquipmentSearchParams,
    EquipmentSearchResponse,
    EquipmentDetail,
    TechnicalDocumentOut,
    SparePartOut,
    ClientOut,
    ManufacturerOut,
)
from ..services.equipment_service import (
    EquipmentService,
    ClientService,
    ManufacturerService,
)


equipment_router = APIRouter()


@equipment_router.get("/search", response_model=EquipmentSearchResponse)
async def search_equipment(
    q: Optional[str] = Query(None, description="Search query across all fields"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
):
    """
    Global search for equipment.
    
    Searches across:
    - Serial number
    - Brand
    - Model
    - Equipment type
    - Client name
    
    Returns paginated results. Ideal for live/autocomplete search.
    """
    return await EquipmentService.global_search(
        session=session,
        query_text=q or "",
        page=page,
        page_size=page_size,
    )


@equipment_router.get("/{equipment_id}", response_model=EquipmentDetail)
async def get_equipment_detail(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
):
    """
    Get detailed equipment information for dashboard view.
    
    Returns:
    - Equipment basic info (serial, brand, model, type, image)
    - Client information with contact details
    - Manufacturer information with support contact
    - List of technical documents (PDFs, videos, images)
    - List of spare parts
    """
    equipment = await EquipmentService.get_equipment_by_id(session, equipment_id)

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    return EquipmentDetail(
        id=equipment.id,
        serial_number=equipment.serial_number,
        brand=equipment.brand,
        model=equipment.model,
        type=equipment.type,
        image=equipment.image,
        created_at=equipment.created_at,
        updated_at=equipment.updated_at,
        client=ClientOut(
            id=equipment.client.id,
            name=equipment.client.name,
            email=equipment.client.email,
            phone=equipment.client.phone,
            address=equipment.client.address,
            created_at=equipment.client.created_at,
            updated_at=equipment.client.updated_at,
        ),
        manufacturer=ManufacturerOut(
            id=equipment.manufacturer.id,
            name=equipment.manufacturer.name,
            support_email=equipment.manufacturer.support_email,
            support_phone=equipment.manufacturer.support_phone,
            created_at=equipment.manufacturer.created_at,
            updated_at=equipment.manufacturer.updated_at,
        ) if equipment.manufacturer else None,
        technical_documents=[
            TechnicalDocumentOut(
                id=doc.id,
                equipment_id=doc.equipment_id,
                title=doc.title,
                file_path=doc.file_path,
                document_type=doc.document_type,
                created_at=doc.created_at,
            )
            for doc in equipment.technical_documents
        ],
        spare_parts=[
            SparePartOut(
                id=part.id,
                equipment_id=part.equipment_id,
                name=part.name,
                reference_code=part.reference_code,
                description=part.description,
                image=part.image,
                created_at=part.created_at,
            )
            for part in equipment.spare_parts
        ],
    )


@equipment_router.get(
    "/{equipment_id}/documents",
    response_model=list[TechnicalDocumentOut],
)
async def get_equipment_documents(
    equipment_id: UUID,
    document_type: Optional[str] = Query(
        None,
        description="Filter by type: PDF, VIDEO, IMAGE",
    ),
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
):
    """
    Get technical documents for an equipment.
    
    Optionally filter by document type:
    - PDF: PDF documents
    - VIDEO: Video files
    - IMAGE: Image files
    """
    # Verify equipment exists
    equipment = await EquipmentService.get_equipment_by_id(session, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    documents = await EquipmentService.get_technical_documents(session, equipment_id)

    # Filter by type if specified
    if document_type:
        documents = [doc for doc in documents if doc.document_type == document_type.upper()]

    return [
        TechnicalDocumentOut(
            id=doc.id,
            equipment_id=doc.equipment_id,
            title=doc.title,
            file_path=doc.file_path,
            document_type=doc.document_type,
            created_at=doc.created_at,
        )
        for doc in documents
    ]


@equipment_router.get(
    "/{equipment_id}/spare-parts",
    response_model=list[SparePartOut],
)
async def get_equipment_spare_parts(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
):
    """
    Get the list of spare parts for an equipment.
    """
    # Verify equipment exists
    equipment = await EquipmentService.get_equipment_by_id(session, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    spare_parts = await EquipmentService.get_spare_parts(session, equipment_id)

    return [
        SparePartOut(
            id=part.id,
            equipment_id=part.equipment_id,
            name=part.name,
            reference_code=part.reference_code,
            description=part.description,
            image=part.image,
            created_at=part.created_at,
        )
        for part in spare_parts
    ]


@equipment_router.get("/{equipment_id}/client", response_model=ClientOut)
async def get_equipment_client(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
):
    """
    Get client contact information for an equipment.
    
    Returns client name, email, phone, and address.
    """
    equipment = await EquipmentService.get_equipment_by_id(session, equipment_id)
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found",
        )

    return ClientOut(
        id=equipment.client.id,
        name=equipment.client.name,
        email=equipment.client.email,
        phone=equipment.client.phone,
        address=equipment.client.address,
        created_at=equipment.client.created_at,
        updated_at=equipment.client.updated_at,
    )


@equipment_router.get("/{equipment_id}/manufacturer", response_model=ManufacturerOut)
async def get_equipment_manufacturer(
    equipment_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
):
    """
    Get manufacturer contact information for an equipment.
    
    Returns manufacturer name, support email, and support phone.
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

    return ManufacturerOut(
        id=equipment.manufacturer.id,
        name=equipment.manufacturer.name,
        support_email=equipment.manufacturer.support_email,
        support_phone=equipment.manufacturer.support_phone,
        created_at=equipment.manufacturer.created_at,
        updated_at=equipment.manufacturer.updated_at,
    )
