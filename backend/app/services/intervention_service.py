"""
Intervention Service

Handles intervention CRUD operations and business logic
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.models import Intervention, Equipment, InterventionAttachment


class InterventionService:
    """Service for intervention operations"""

    @staticmethod
    async def create_intervention(
        session: AsyncSession,
        equipment_id: UUID,
        technician_id: UUID,
        diagnostic: Optional[str] = None,
        actions_taken: Optional[str] = None,
    ) -> Intervention:
        """Create a new intervention"""
        # Verify equipment exists
        equipment_stmt = select(Equipment).where(Equipment.id == equipment_id)
        equipment_result = await session.execute(equipment_stmt)
        equipment = equipment_result.scalar_one_or_none()

        if not equipment:
            raise ValueError("Equipment not found")

        # Create intervention
        intervention = Intervention(
            equipment_id=equipment_id,
            technician_id=technician_id,
            status="IN_PROGRESS",
            diagnostic=diagnostic,
            actions_taken=actions_taken,
            started_at=datetime.now(timezone.utc),
        )

        session.add(intervention)
        await session.commit()
        await session.refresh(intervention)

        return intervention

    @staticmethod
    async def get_intervention_by_id(
        session: AsyncSession, intervention_id: UUID
    ) -> Optional[Intervention]:
        """Get intervention by ID with relationships"""
        stmt = (
            select(Intervention)
            .options(
                selectinload(Intervention.equipment),
                selectinload(Intervention.technician),
                selectinload(Intervention.attachments),
            )
            .where(Intervention.id == intervention_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_interventions_by_equipment(
        session: AsyncSession, equipment_id: UUID
    ) -> List[Intervention]:
        """Get all interventions for an equipment"""
        stmt = (
            select(Intervention)
            .options(
                selectinload(Intervention.technician),
                selectinload(Intervention.attachments),
            )
            .where(Intervention.equipment_id == equipment_id)
            .order_by(Intervention.created_at.desc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_active_intervention_for_equipment(
        session: AsyncSession, equipment_id: UUID
    ) -> Optional[Intervention]:
        """Get active (IN_PROGRESS) intervention for equipment"""
        stmt = (
            select(Intervention)
            .options(
                selectinload(Intervention.equipment),
                selectinload(Intervention.technician),
                selectinload(Intervention.attachments),
            )
            .where(
                Intervention.equipment_id == equipment_id,
                Intervention.status == "IN_PROGRESS"
            )
            .order_by(Intervention.created_at.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def update_intervention(
        session: AsyncSession,
        intervention_id: UUID,
        diagnostic: Optional[str] = None,
        actions_taken: Optional[str] = None,
        result: Optional[str] = None,
        failure_reason: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[Intervention]:
        """Update intervention fields"""
        intervention = await InterventionService.get_intervention_by_id(
            session, intervention_id
        )

        if not intervention:
            return None

        if diagnostic is not None:
            intervention.diagnostic = diagnostic
        if actions_taken is not None:
            intervention.actions_taken = actions_taken
        if result is not None:
            intervention.result = result
        if failure_reason is not None:
            intervention.failure_reason = failure_reason
        if status is not None:
            intervention.status = status
            if status in ["COMPLETED", "NOT_REPAIRED"]:
                intervention.completed_at = datetime.now(timezone.utc)

        await session.commit()
        await session.refresh(intervention)

        return intervention

    @staticmethod
    async def complete_intervention(
        session: AsyncSession,
        intervention_id: UUID,
        status: str,  # COMPLETED or NOT_REPAIRED
        result: Optional[str] = None,
        failure_reason: Optional[str] = None,
        signature_path: Optional[str] = None,
    ) -> Optional[Intervention]:
        """Complete an intervention"""
        if status not in ["COMPLETED", "NOT_REPAIRED"]:
            raise ValueError("Invalid status. Must be COMPLETED or NOT_REPAIRED")

        if status == "NOT_REPAIRED" and not failure_reason:
            raise ValueError("Failure reason required for NOT_REPAIRED status")

        intervention = await InterventionService.get_intervention_by_id(
            session, intervention_id
        )

        if not intervention:
            return None

        intervention.status = status
        intervention.result = result
        intervention.failure_reason = failure_reason
        intervention.signature_image_path = signature_path
        intervention.completed_at = datetime.now(timezone.utc)

        await session.commit()
        await session.refresh(intervention)

        return intervention

    @staticmethod
    async def add_attachment(
        session: AsyncSession,
        intervention_id: UUID,
        file_path: str,
        attachment_type: str = "PHOTO",
    ) -> InterventionAttachment:
        """Add attachment to intervention"""
        attachment = InterventionAttachment(
            intervention_id=intervention_id,
            file_path=file_path,
            attachment_type=attachment_type,
        )

        session.add(attachment)
        await session.commit()
        await session.refresh(attachment)

        return attachment

    @staticmethod
    async def get_interventions_by_technician(
        session: AsyncSession, technician_id: UUID, limit: int = 10
    ) -> List[Intervention]:
        """Get recent interventions by technician"""
        stmt = (
            select(Intervention)
            .options(
                selectinload(Intervention.equipment),
            )
            .where(Intervention.technician_id == technician_id)
            .order_by(Intervention.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

