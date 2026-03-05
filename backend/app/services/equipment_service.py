"""
Equipment Service Layer

Handles business logic for equipment search, retrieval, and related operations.
"""

from typing import Optional, List
from uuid import UUID
from math import ceil

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.models import (
    Equipment,
    Client,
    Manufacturer,
    TechnicalDocument,
    SparePart,
)
from ..schemas.equipment_schemas import (
    EquipmentSearchParams,
    EquipmentSearchResponse,
    EquipmentSummary,
    EquipmentCreate,
    EquipmentUpdate,
)


class EquipmentService:
    """Service class for equipment-related operations"""

    @staticmethod
    async def global_search(
        session: AsyncSession,
        query_text: str,
        page: int = 1,
        page_size: int = 10,
    ) -> EquipmentSearchResponse:
        """
        Global search across all equipment fields.
        
        Searches across:
        - Serial number
        - Brand
        - Model
        - Equipment type
        - Client name
        """
        # Base query with client join
        query = (
            select(Equipment)
            .join(Client, Equipment.client_id == Client.id)
            .options(selectinload(Equipment.client))
        )

        # Build OR conditions for global search
        if query_text and query_text.strip():
            search_term = f"%{query_text.strip()}%"
            query = query.where(
                or_(
                    Equipment.serial_number.ilike(search_term),
                    Equipment.brand.ilike(search_term),
                    Equipment.model.ilike(search_term),
                    Equipment.type.ilike(search_term),
                    Client.name.ilike(search_term),
                )
            )

        # Count total results
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Equipment.serial_number)

        # Execute query
        result = await session.execute(query)
        equipment_list = result.scalars().all()

        # Convert to response format
        items = [
            EquipmentSummary(
                id=eq.id,
                serial_number=eq.serial_number,
                brand=eq.brand,
                model=eq.model,
                type=eq.type,
                image=eq.image,
                client_name=eq.client.name,
            )
            for eq in equipment_list
        ]

        total_pages = ceil(total / page_size) if total > 0 else 1

        return EquipmentSearchResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def search_equipment(
        session: AsyncSession,
        params: EquipmentSearchParams,
        page: int = 1,
        page_size: int = 20,
    ) -> EquipmentSearchResponse:
        """
        Search for equipment with multiple filter options.
        
        Supports filtering by:
        - Serial number (partial match)
        - Client name or ID
        - Brand (partial match)
        - Model (partial match)
        - Equipment type (partial match)
        """
        # Base query with client join for name filtering
        query = (
            select(Equipment)
            .join(Client, Equipment.client_id == Client.id)
            .options(selectinload(Equipment.client))
        )

        # Build filter conditions
        conditions = []

        if params.serial_number:
            conditions.append(
                Equipment.serial_number.ilike(f"%{params.serial_number}%")
            )

        if params.client_id:
            conditions.append(Equipment.client_id == params.client_id)
        elif params.client_name:
            conditions.append(Client.name.ilike(f"%{params.client_name}%"))

        if params.brand:
            conditions.append(Equipment.brand.ilike(f"%{params.brand}%"))

        if params.model:
            conditions.append(Equipment.model.ilike(f"%{params.model}%"))

        if params.equipment_type:
            conditions.append(Equipment.type.ilike(f"%{params.equipment_type}%"))

        # Apply conditions
        if conditions:
            query = query.where(*conditions)

        # Count total results
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Equipment.serial_number)

        # Execute query
        result = await session.execute(query)
        equipment_list = result.scalars().all()

        # Convert to response format
        items = [
            EquipmentSummary(
                id=eq.id,
                serial_number=eq.serial_number,
                brand=eq.brand,
                model=eq.model,
                type=eq.type,
                image=eq.image,
                client_name=eq.client.name,
            )
            for eq in equipment_list
        ]

        total_pages = ceil(total / page_size) if total > 0 else 1

        return EquipmentSearchResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def get_equipment_by_id(
        session: AsyncSession, equipment_id: UUID
    ) -> Optional[Equipment]:
        """
        Get equipment by ID with all related data for dashboard view.
        
        Eagerly loads:
        - Client
        - Manufacturer
        - Technical documents
        - Spare parts
        """
        query = (
            select(Equipment)
            .where(Equipment.id == equipment_id)
            .options(
                selectinload(Equipment.client),
                selectinload(Equipment.manufacturer),
                selectinload(Equipment.technical_documents),
                selectinload(Equipment.spare_parts),
            )
        )

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_equipment_by_serial(
        session: AsyncSession, serial_number: str
    ) -> Optional[Equipment]:
        """Get equipment by serial number"""
        query = (
            select(Equipment)
            .where(Equipment.serial_number == serial_number)
            .options(
                selectinload(Equipment.client),
                selectinload(Equipment.manufacturer),
                selectinload(Equipment.technical_documents),
                selectinload(Equipment.spare_parts),
            )
        )

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_technical_documents(
        session: AsyncSession, equipment_id: UUID
    ) -> List[TechnicalDocument]:
        """Get all technical documents for an equipment"""
        query = select(TechnicalDocument).where(
            TechnicalDocument.equipment_id == equipment_id
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_spare_parts(
        session: AsyncSession, equipment_id: UUID
    ) -> List[SparePart]:
        """Get all spare parts for an equipment"""
        query = select(SparePart).where(SparePart.equipment_id == equipment_id)
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_technical_document_by_id(
        session: AsyncSession, document_id: UUID
    ) -> Optional[TechnicalDocument]:
        """Get a specific technical document by ID"""
        query = select(TechnicalDocument).where(TechnicalDocument.id == document_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_technical_documents_by_ids(
        session: AsyncSession, document_ids: List[UUID]
    ) -> List[TechnicalDocument]:
        """Get multiple technical documents by their IDs"""
        if not document_ids:
            return []

        query = select(TechnicalDocument).where(
            TechnicalDocument.id.in_(document_ids)
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    # ==========================================================================
    # CRUD Operations (for admin use)
    # ==========================================================================

    @staticmethod
    async def create_equipment(
        session: AsyncSession, data: EquipmentCreate
    ) -> Equipment:
        """Create new equipment"""
        equipment = Equipment(**data.model_dump())
        session.add(equipment)
        await session.commit()
        await session.refresh(equipment)
        return equipment

    @staticmethod
    async def update_equipment(
        session: AsyncSession, equipment_id: UUID, data: EquipmentUpdate
    ) -> Optional[Equipment]:
        """Update equipment"""
        equipment = await EquipmentService.get_equipment_by_id(session, equipment_id)
        if not equipment:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(equipment, key, value)

        await session.commit()
        await session.refresh(equipment)
        return equipment

    @staticmethod
    async def delete_equipment(
        session: AsyncSession, equipment_id: UUID
    ) -> bool:
        """Delete equipment by ID"""
        equipment = await EquipmentService.get_equipment_by_id(session, equipment_id)
        if not equipment:
            return False

        await session.delete(equipment)
        await session.commit()
        return True


class ClientService:
    """Service class for client-related operations"""

    @staticmethod
    async def get_client_by_id(
        session: AsyncSession, client_id: UUID
    ) -> Optional[Client]:
        """Get client by ID"""
        query = select(Client).where(Client.id == client_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_clients(session: AsyncSession) -> List[Client]:
        """Get all clients"""
        query = select(Client).order_by(Client.name)
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def search_clients(
        session: AsyncSession, search_term: str
    ) -> List[Client]:
        """Search clients by name"""
        query = (
            select(Client)
            .where(Client.name.ilike(f"%{search_term}%"))
            .order_by(Client.name)
            .limit(20)
        )
        result = await session.execute(query)
        return list(result.scalars().all())


class ManufacturerService:
    """Service class for manufacturer-related operations"""

    @staticmethod
    async def get_manufacturer_by_id(
        session: AsyncSession, manufacturer_id: UUID
    ) -> Optional[Manufacturer]:
        """Get manufacturer by ID"""
        query = select(Manufacturer).where(Manufacturer.id == manufacturer_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_manufacturers(session: AsyncSession) -> List[Manufacturer]:
        """Get all manufacturers"""
        query = select(Manufacturer).order_by(Manufacturer.name)
        result = await session.execute(query)
        return list(result.scalars().all())
