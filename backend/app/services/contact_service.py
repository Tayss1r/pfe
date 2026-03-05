"""
Contact Service Layer

Handles sending emails to manufacturers and clients with proper validation
and attachment handling.
"""

import os
from typing import List, Optional
from uuid import UUID
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.models import (
    Equipment,
    Intervention,
    TechnicalDocument,
    EmailLog,
)
from ..services.equipment_service import EquipmentService


class ContactService:
    """Service class for contact-related operations"""

    # Base path for uploaded files and documents
    UPLOAD_BASE_PATH = Path("uploads")
    DOCUMENTS_PATH = UPLOAD_BASE_PATH / "documents"
    PHOTOS_PATH = UPLOAD_BASE_PATH / "photos"
    REPORTS_PATH = UPLOAD_BASE_PATH / "reports"

    @staticmethod
    async def validate_manufacturer_contact(
        session: AsyncSession,
        equipment_id: UUID,
        technical_document_ids: List[UUID],
    ) -> dict:
        """
        Validate manufacturer contact request.
        
        Returns dict with:
        - equipment: Equipment object
        - manufacturer_email: str
        - documents: List of TechnicalDocument objects
        """
        # Get equipment with manufacturer
        equipment = await EquipmentService.get_equipment_by_id(session, equipment_id)
        
        if not equipment:
            return {"error": "Equipment not found", "status_code": 404}

        if not equipment.manufacturer:
            return {"error": "No manufacturer associated with this equipment", "status_code": 400}

        if not equipment.manufacturer.support_email:
            return {"error": "Manufacturer does not have a support email configured", "status_code": 400}

        # Validate technical document IDs if provided
        documents = []
        if technical_document_ids:
            documents = await EquipmentService.get_technical_documents_by_ids(
                session, technical_document_ids
            )
            
            # Verify all documents belong to this equipment
            for doc in documents:
                if doc.equipment_id != equipment_id:
                    return {
                        "error": f"Document {doc.id} does not belong to this equipment",
                        "status_code": 400,
                    }

            if len(documents) != len(technical_document_ids):
                return {"error": "One or more technical documents not found", "status_code": 404}

        return {
            "equipment": equipment,
            "manufacturer_email": equipment.manufacturer.support_email,
            "documents": documents,
        }

    @staticmethod
    async def validate_client_contact(
        session: AsyncSession,
        equipment_id: UUID,
        intervention_id: Optional[UUID],
        include_intervention_report: bool,
    ) -> dict:
        """
        Validate client contact request.
        
        Returns dict with:
        - equipment: Equipment object
        - client_email: str
        - intervention: Intervention object (if needed for report)
        """
        # Get equipment with client
        equipment = await EquipmentService.get_equipment_by_id(session, equipment_id)
        
        if not equipment:
            return {"error": "Equipment not found", "status_code": 404}

        if not equipment.client.email:
            return {"error": "Client does not have an email configured", "status_code": 400}

        intervention = None
        if include_intervention_report:
            if not intervention_id:
                return {
                    "error": "Intervention ID required when including report",
                    "status_code": 400,
                }

            # Get intervention
            query = select(Intervention).where(Intervention.id == intervention_id)
            result = await session.execute(query)
            intervention = result.scalar_one_or_none()

            if not intervention:
                return {"error": "Intervention not found", "status_code": 404}

            if intervention.equipment_id != equipment_id:
                return {
                    "error": "Intervention does not belong to this equipment",
                    "status_code": 400,
                }

        return {
            "equipment": equipment,
            "client_email": equipment.client.email,
            "intervention": intervention,
        }

    @staticmethod
    async def log_email(
        session: AsyncSession,
        intervention_id: UUID,
        recipient_type: str,
        recipient_email: str,
        subject: str,
        body: Optional[str] = None,
    ) -> EmailLog:
        """
        Log an email that was sent.
        
        Args:
            intervention_id: UUID of the related intervention
            recipient_type: MANUFACTURER, CLIENT, or COMPANY
            recipient_email: Email address of the recipient
            subject: Email subject
            body: Email body content
        """
        email_log = EmailLog(
            intervention_id=intervention_id,
            recipient_type=recipient_type,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
        )
        session.add(email_log)
        await session.commit()
        await session.refresh(email_log)
        return email_log

    @staticmethod
    def build_manufacturer_email_body(
        equipment,
        message: str,
        technician_name: str,
    ) -> str:
        """Build HTML email body for manufacturer contact"""
        return f"""
        <html>
        <body>
            <h2>Technical Support Request</h2>
            
            <h3>Equipment Information</h3>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Serial Number:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{equipment.serial_number}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Brand:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{equipment.brand or 'N/A'}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Model:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{equipment.model or 'N/A'}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Type:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{equipment.type or 'N/A'}</td>
                </tr>
            </table>
            
            <h3>Message from Technician</h3>
            <p style="white-space: pre-wrap;">{message}</p>
            
            <hr>
            <p style="color: #666; font-size: 12px;">
                This email was sent by {technician_name} via the Repair Management System.
            </p>
        </body>
        </html>
        """

    @staticmethod
    def build_client_email_body(
        equipment,
        message: str,
        technician_name: str,
        include_intervention_info: bool = False,
        intervention=None,
    ) -> str:
        """Build HTML email body for client contact"""
        intervention_section = ""
        if include_intervention_info and intervention:
            intervention_section = f"""
            <h3>Intervention Status</h3>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Status:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{intervention.status}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Diagnostic:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{intervention.diagnostic or 'N/A'}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Actions Taken:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{intervention.actions_taken or 'N/A'}</td>
                </tr>
            </table>
            """

        return f"""
        <html>
        <body>
            <h2>Service Update</h2>
            
            <h3>Equipment Information</h3>
            <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Serial Number:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{equipment.serial_number}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Type:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{equipment.type or 'N/A'}</td>
                </tr>
            </table>
            
            {intervention_section}
            
            <h3>Message</h3>
            <p style="white-space: pre-wrap;">{message}</p>
            
            <hr>
            <p style="color: #666; font-size: 12px;">
                This email was sent by {technician_name} from our service team.
            </p>
        </body>
        </html>
        """

    @staticmethod
    def get_attachment_paths(document_ids: List[TechnicalDocument]) -> List[str]:
        """Get file paths for technical documents"""
        return [doc.file_path for doc in document_ids if os.path.exists(doc.file_path)]
