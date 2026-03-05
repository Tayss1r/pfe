"""Admin Service - CRUD operations for all entities"""
import math
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.models import (
    Client,
    Manufacturer,
    Equipment,
    TechnicalDocument,
    SparePart,
    Intervention,
    User,
)
from ..schemas.admin_schemas import (
    ClientCreate,
    ClientUpdate,
    ManufacturerCreate,
    ManufacturerUpdate,
    EquipmentCreate,
    EquipmentUpdate,
    SparePartCreate,
    SparePartUpdate,
    DashboardStats,
)


class AdminService:
    """Admin service for CRUD operations"""

    # ============== Dashboard ==============
    @staticmethod
    async def get_dashboard_stats(session: AsyncSession) -> DashboardStats:
        """Get dashboard statistics"""
        # Count equipment
        equipment_count = await session.scalar(select(func.count(Equipment.id)))
        
        # Count clients
        clients_count = await session.scalar(select(func.count(Client.id)))
        
        # Count manufacturers
        manufacturers_count = await session.scalar(select(func.count(Manufacturer.id)))
        
        # Count interventions
        interventions_count = await session.scalar(select(func.count(Intervention.id)))
        
        # Count spare parts
        spare_parts_count = await session.scalar(select(func.count(SparePart.id)))
        
        # Count documents
        documents_count = await session.scalar(select(func.count(TechnicalDocument.id)))
        
        # Count interventions by status
        in_progress = await session.scalar(
            select(func.count(Intervention.id)).where(Intervention.status == "IN_PROGRESS")
        )
        completed = await session.scalar(
            select(func.count(Intervention.id)).where(Intervention.status == "COMPLETED")
        )
        not_repaired = await session.scalar(
            select(func.count(Intervention.id)).where(Intervention.status == "NOT_REPAIRED")
        )

        return DashboardStats(
            total_equipment=equipment_count or 0,
            total_clients=clients_count or 0,
            total_manufacturers=manufacturers_count or 0,
            total_interventions=interventions_count or 0,
            total_spare_parts=spare_parts_count or 0,
            total_documents=documents_count or 0,
            interventions_in_progress=in_progress or 0,
            interventions_completed=completed or 0,
            interventions_not_repaired=not_repaired or 0,
        )

    @staticmethod
    async def get_recent_interventions(
        session: AsyncSession, limit: int = 10
    ) -> List[Intervention]:
        """Get recent interventions"""
        stmt = (
            select(Intervention)
            .options(selectinload(Intervention.equipment), selectinload(Intervention.technician))
            .order_by(Intervention.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    # ============== Clients ==============
    @staticmethod
    async def list_clients(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
    ) -> Tuple[List[Client], int]:
        """List clients with pagination and search"""
        stmt = select(Client)
        count_stmt = select(func.count(Client.id))

        if search:
            search_filter = or_(
                Client.name.ilike(f"%{search}%"),
                Client.email.ilike(f"%{search}%"),
                Client.phone.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = await session.scalar(count_stmt) or 0

        stmt = stmt.order_by(Client.name).offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(stmt)
        return list(result.scalars().all()), total

    @staticmethod
    async def get_client(session: AsyncSession, client_id: UUID) -> Optional[Client]:
        """Get client by ID"""
        return await session.get(Client, client_id)

    @staticmethod
    async def create_client(session: AsyncSession, data: ClientCreate) -> Client:
        """Create a new client"""
        client = Client(**data.model_dump())
        session.add(client)
        await session.commit()
        await session.refresh(client)
        return client

    @staticmethod
    async def update_client(
        session: AsyncSession, client_id: UUID, data: ClientUpdate
    ) -> Optional[Client]:
        """Update a client"""
        client = await session.get(Client, client_id)
        if not client:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)

        await session.commit()
        await session.refresh(client)
        return client

    @staticmethod
    async def delete_client(session: AsyncSession, client_id: UUID) -> bool:
        """Delete a client"""
        client = await session.get(Client, client_id)
        if not client:
            return False

        await session.delete(client)
        await session.commit()
        return True

    # ============== Manufacturers ==============
    @staticmethod
    async def list_manufacturers(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
    ) -> Tuple[List[Manufacturer], int]:
        """List manufacturers with pagination and search"""
        stmt = select(Manufacturer)
        count_stmt = select(func.count(Manufacturer.id))

        if search:
            search_filter = or_(
                Manufacturer.name.ilike(f"%{search}%"),
                Manufacturer.support_email.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = await session.scalar(count_stmt) or 0

        stmt = stmt.order_by(Manufacturer.name).offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(stmt)
        return list(result.scalars().all()), total

    @staticmethod
    async def get_manufacturer(session: AsyncSession, manufacturer_id: UUID) -> Optional[Manufacturer]:
        """Get manufacturer by ID"""
        return await session.get(Manufacturer, manufacturer_id)

    @staticmethod
    async def create_manufacturer(session: AsyncSession, data: ManufacturerCreate) -> Manufacturer:
        """Create a new manufacturer"""
        manufacturer = Manufacturer(**data.model_dump())
        session.add(manufacturer)
        await session.commit()
        await session.refresh(manufacturer)
        return manufacturer

    @staticmethod
    async def update_manufacturer(
        session: AsyncSession, manufacturer_id: UUID, data: ManufacturerUpdate
    ) -> Optional[Manufacturer]:
        """Update a manufacturer"""
        manufacturer = await session.get(Manufacturer, manufacturer_id)
        if not manufacturer:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(manufacturer, field, value)

        await session.commit()
        await session.refresh(manufacturer)
        return manufacturer

    @staticmethod
    async def delete_manufacturer(session: AsyncSession, manufacturer_id: UUID) -> bool:
        """Delete a manufacturer"""
        manufacturer = await session.get(Manufacturer, manufacturer_id)
        if not manufacturer:
            return False

        await session.delete(manufacturer)
        await session.commit()
        return True

    # ============== Equipment ==============
    @staticmethod
    async def list_equipment(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
    ) -> Tuple[List[Equipment], int]:
        """List equipment with pagination and search"""
        stmt = select(Equipment).options(
            selectinload(Equipment.client),
            selectinload(Equipment.manufacturer),
        )
        count_stmt = select(func.count(Equipment.id))

        if search:
            search_filter = or_(
                Equipment.serial_number.ilike(f"%{search}%"),
                Equipment.brand.ilike(f"%{search}%"),
                Equipment.model.ilike(f"%{search}%"),
                Equipment.type.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = await session.scalar(count_stmt) or 0

        stmt = stmt.order_by(Equipment.serial_number).offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(stmt)
        return list(result.scalars().all()), total

    @staticmethod
    async def get_equipment(session: AsyncSession, equipment_id: UUID) -> Optional[Equipment]:
        """Get equipment by ID"""
        stmt = (
            select(Equipment)
            .options(selectinload(Equipment.client), selectinload(Equipment.manufacturer))
            .where(Equipment.id == equipment_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_equipment(session: AsyncSession, data: EquipmentCreate) -> Equipment:
        """Create new equipment"""
        equipment = Equipment(**data.model_dump())
        session.add(equipment)
        await session.commit()
        await session.refresh(equipment)
        
        # Reload with relationships
        return await AdminService.get_equipment(session, equipment.id)

    @staticmethod
    async def update_equipment(
        session: AsyncSession, equipment_id: UUID, data: EquipmentUpdate
    ) -> Optional[Equipment]:
        """Update equipment"""
        equipment = await session.get(Equipment, equipment_id)
        if not equipment:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(equipment, field, value)

        await session.commit()
        return await AdminService.get_equipment(session, equipment_id)

    @staticmethod
    async def delete_equipment(session: AsyncSession, equipment_id: UUID) -> bool:
        """Delete equipment"""
        equipment = await session.get(Equipment, equipment_id)
        if not equipment:
            return False

        await session.delete(equipment)
        await session.commit()
        return True

    # ============== Technical Documents ==============
    @staticmethod
    async def list_documents(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        equipment_id: Optional[UUID] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[TechnicalDocument], int]:
        """List documents with pagination"""
        stmt = select(TechnicalDocument).options(selectinload(TechnicalDocument.equipment))
        count_stmt = select(func.count(TechnicalDocument.id))

        if equipment_id:
            stmt = stmt.where(TechnicalDocument.equipment_id == equipment_id)
            count_stmt = count_stmt.where(TechnicalDocument.equipment_id == equipment_id)

        if search:
            search_filter = TechnicalDocument.title.ilike(f"%{search}%")
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = await session.scalar(count_stmt) or 0

        stmt = stmt.order_by(TechnicalDocument.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(stmt)
        return list(result.scalars().all()), total

    @staticmethod
    async def get_document(session: AsyncSession, document_id: UUID) -> Optional[TechnicalDocument]:
        """Get document by ID"""
        stmt = (
            select(TechnicalDocument)
            .options(selectinload(TechnicalDocument.equipment))
            .where(TechnicalDocument.id == document_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_document(
        session: AsyncSession,
        equipment_id: UUID,
        title: str,
        file_path: str,
        document_type: str,
    ) -> TechnicalDocument:
        """Create a new document"""
        document = TechnicalDocument(
            equipment_id=equipment_id,
            title=title,
            file_path=file_path,
            document_type=document_type,
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)
        return await AdminService.get_document(session, document.id)

    @staticmethod
    async def delete_document(session: AsyncSession, document_id: UUID) -> bool:
        """Delete a document"""
        document = await session.get(TechnicalDocument, document_id)
        if not document:
            return False

        await session.delete(document)
        await session.commit()
        return True

    # ============== Spare Parts ==============
    @staticmethod
    async def list_spare_parts(
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        equipment_id: Optional[UUID] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[SparePart], int]:
        """List spare parts with pagination"""
        stmt = select(SparePart).options(selectinload(SparePart.equipment))
        count_stmt = select(func.count(SparePart.id))

        if equipment_id:
            stmt = stmt.where(SparePart.equipment_id == equipment_id)
            count_stmt = count_stmt.where(SparePart.equipment_id == equipment_id)

        if search:
            search_filter = or_(
                SparePart.name.ilike(f"%{search}%"),
                SparePart.reference_code.ilike(f"%{search}%"),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        total = await session.scalar(count_stmt) or 0

        stmt = stmt.order_by(SparePart.name).offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(stmt)
        return list(result.scalars().all()), total

    @staticmethod
    async def get_spare_part(session: AsyncSession, spare_part_id: UUID) -> Optional[SparePart]:
        """Get spare part by ID"""
        stmt = (
            select(SparePart)
            .options(selectinload(SparePart.equipment))
            .where(SparePart.id == spare_part_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_spare_part(session: AsyncSession, data: SparePartCreate) -> SparePart:
        """Create a new spare part"""
        spare_part = SparePart(**data.model_dump())
        session.add(spare_part)
        await session.commit()
        await session.refresh(spare_part)
        return await AdminService.get_spare_part(session, spare_part.id)

    @staticmethod
    async def update_spare_part(
        session: AsyncSession, spare_part_id: UUID, data: SparePartUpdate
    ) -> Optional[SparePart]:
        """Update a spare part"""
        spare_part = await session.get(SparePart, spare_part_id)
        if not spare_part:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(spare_part, field, value)

        await session.commit()
        return await AdminService.get_spare_part(session, spare_part_id)

    @staticmethod
    async def delete_spare_part(session: AsyncSession, spare_part_id: UUID) -> bool:
        """Delete a spare part"""
        spare_part = await session.get(SparePart, spare_part_id)
        if not spare_part:
            return False

        await session.delete(spare_part)
        await session.commit()
        return True

    # ============== Helpers ==============
    @staticmethod
    def calculate_total_pages(total: int, page_size: int) -> int:
        """Calculate total pages"""
        return math.ceil(total / page_size) if total > 0 else 1
