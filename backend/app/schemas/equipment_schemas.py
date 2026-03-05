"""
Equipment-related Pydantic schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# =============================================================================
# Base Schemas
# =============================================================================

class ClientBase(BaseModel):
    """Base schema for Client data"""
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ManufacturerBase(BaseModel):
    """Base schema for Manufacturer data"""
    name: str
    support_email: Optional[EmailStr] = None
    support_phone: Optional[str] = None


class TechnicalDocumentBase(BaseModel):
    """Base schema for Technical Document"""
    title: str
    file_path: str
    document_type: str  # PDF, VIDEO, IMAGE


class SparePartBase(BaseModel):
    """Base schema for Spare Part"""
    name: str
    reference_code: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None


# =============================================================================
# Response Schemas
# =============================================================================

class ClientOut(ClientBase):
    """Client response schema"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ManufacturerOut(ManufacturerBase):
    """Manufacturer response schema"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TechnicalDocumentOut(TechnicalDocumentBase):
    """Technical Document response schema"""
    id: UUID
    equipment_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SparePartOut(SparePartBase):
    """Spare Part response schema"""
    id: UUID
    equipment_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class EquipmentSummary(BaseModel):
    """Minimal equipment data for search results"""
    id: UUID
    serial_number: str
    brand: Optional[str] = None
    model: Optional[str] = None
    type: Optional[str] = None
    image: Optional[str] = None
    client_name: str

    class Config:
        from_attributes = True


class EquipmentDetail(BaseModel):
    """Full equipment data for dashboard view"""
    id: UUID
    serial_number: str
    brand: Optional[str] = None
    model: Optional[str] = None
    type: Optional[str] = None
    image: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related entities
    client: ClientOut
    manufacturer: Optional[ManufacturerOut] = None
    technical_documents: List[TechnicalDocumentOut] = []
    spare_parts: List[SparePartOut] = []

    class Config:
        from_attributes = True


# =============================================================================
# Search/Filter Schemas
# =============================================================================

class EquipmentSearchParams(BaseModel):
    """Parameters for equipment search"""
    serial_number: Optional[str] = Field(None, description="Filter by serial number (partial match)")
    client_name: Optional[str] = Field(None, description="Filter by client name (partial match)")
    client_id: Optional[UUID] = Field(None, description="Filter by client ID (exact match)")
    brand: Optional[str] = Field(None, description="Filter by brand (partial match)")
    model: Optional[str] = Field(None, description="Filter by model (partial match)")
    equipment_type: Optional[str] = Field(None, description="Filter by equipment type (partial match)")


class EquipmentSearchResponse(BaseModel):
    """Response for equipment search"""
    items: List[EquipmentSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# Contact/Email Schemas
# =============================================================================

class AttachmentInfo(BaseModel):
    """Information about an attachment"""
    filename: str
    content_type: str
    file_path: Optional[str] = None  # For technical docs from DB
    # For uploaded photos, the actual file is handled via multipart form


class ManufacturerContactRequest(BaseModel):
    """Request to contact manufacturer"""
    equipment_id: UUID
    subject: str = Field(..., min_length=1, max_length=512)
    message: str = Field(..., min_length=1)
    # Attachments can include:
    # - Photos taken by technician (uploaded separately)
    # - Technical document IDs from the database
    technical_document_ids: List[UUID] = Field(default_factory=list)
    intervention_id: Optional[UUID] = None


class ClientContactRequest(BaseModel):
    """Request to contact client"""
    equipment_id: UUID
    subject: str = Field(..., min_length=1, max_length=512)
    message: str = Field(..., min_length=1)
    # Attachments for client emails:
    # - Photos taken by technician (uploaded separately)
    # - Current intervention report (if one exists)
    intervention_id: Optional[UUID] = None
    include_intervention_report: bool = False
    # Note: Technical documents are NOT allowed for client emails


class EmailSendResponse(BaseModel):
    """Response for email send operations"""
    success: bool
    message: str
    email_log_id: Optional[UUID] = None


# =============================================================================
# Create/Update Schemas (for admin use)
# =============================================================================

class EquipmentCreate(BaseModel):
    """Schema for creating new equipment"""
    serial_number: str = Field(..., min_length=1, max_length=128)
    brand: Optional[str] = Field(None, max_length=128)
    model: Optional[str] = Field(None, max_length=128)
    type: Optional[str] = Field(None, max_length=128)
    image: Optional[str] = None
    client_id: UUID
    manufacturer_id: Optional[UUID] = None


class EquipmentUpdate(BaseModel):
    """Schema for updating equipment"""
    serial_number: Optional[str] = Field(None, min_length=1, max_length=128)
    brand: Optional[str] = Field(None, max_length=128)
    model: Optional[str] = Field(None, max_length=128)
    type: Optional[str] = Field(None, max_length=128)
    image: Optional[str] = None
    client_id: Optional[UUID] = None
    manufacturer_id: Optional[UUID] = None


class ClientCreate(BaseModel):
    """Schema for creating new client"""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=64)
    address: Optional[str] = None


class ManufacturerCreate(BaseModel):
    """Schema for creating new manufacturer"""
    name: str = Field(..., min_length=1, max_length=255)
    support_email: Optional[EmailStr] = None
    support_phone: Optional[str] = Field(None, max_length=64)


class SparePartCreate(BaseModel):
    """Schema for creating spare part"""
    equipment_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    reference_code: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = None
    image: Optional[str] = None


class TechnicalDocumentCreate(BaseModel):
    """Schema for creating technical document"""
    equipment_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    file_path: str
    document_type: str = Field(..., pattern="^(PDF|VIDEO|IMAGE)$")
