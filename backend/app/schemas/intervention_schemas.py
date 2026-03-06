"""
Intervention Schemas

Pydantic models for intervention API requests and responses
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


# Intervention Attachment Schemas
class InterventionAttachmentOut(BaseModel):
    id: UUID
    intervention_id: UUID
    file_path: str
    attachment_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# Intervention Schemas
class InterventionCreate(BaseModel):
    equipment_id: UUID
    diagnostic: Optional[str] = None
    actions_taken: Optional[str] = None


class InterventionUpdate(BaseModel):
    diagnostic: Optional[str] = None
    actions_taken: Optional[str] = None
    result: Optional[str] = None
    failure_reason: Optional[str] = None
    status: Optional[str] = None


class InterventionComplete(BaseModel):
    status: str = Field(..., pattern="^(COMPLETED|NOT_REPAIRED)$")
    result: Optional[str] = None
    failure_reason: Optional[str] = None


class InterventionOut(BaseModel):
    id: UUID
    equipment_id: UUID
    technician_id: UUID
    status: str
    diagnostic: Optional[str]
    actions_taken: Optional[str]
    result: Optional[str]
    failure_reason: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    signature_image_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class InterventionDetail(BaseModel):
    id: UUID
    equipment_id: UUID
    equipment_serial: str
    equipment_brand: Optional[str]
    equipment_model: Optional[str]
    technician_id: UUID
    technician_name: str
    status: str
    diagnostic: Optional[str]
    actions_taken: Optional[str]
    result: Optional[str]
    failure_reason: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    signature_image_path: Optional[str]
    created_at: datetime
    attachments: List[InterventionAttachmentOut] = []

    class Config:
        from_attributes = True


class InterventionHistory(BaseModel):
    id: UUID
    technician_name: str
    status: str
    diagnostic: Optional[str]
    result: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

