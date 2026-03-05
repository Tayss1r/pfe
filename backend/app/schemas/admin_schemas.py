"""Admin Schemas for CRUD operations"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# ============== Client Schemas ==============
class ClientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=64)
    address: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=64)
    address: Optional[str] = None


class ClientResponse(BaseModel):
    id: UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    items: List[ClientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== Manufacturer Schemas ==============
class ManufacturerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    support_email: Optional[EmailStr] = None
    support_phone: Optional[str] = Field(None, max_length=64)


class ManufacturerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    support_email: Optional[EmailStr] = None
    support_phone: Optional[str] = Field(None, max_length=64)


class ManufacturerResponse(BaseModel):
    id: UUID
    name: str
    support_email: Optional[str]
    support_phone: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ManufacturerListResponse(BaseModel):
    items: List[ManufacturerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== Equipment Schemas ==============
class EquipmentCreate(BaseModel):
    serial_number: str = Field(..., min_length=1, max_length=128)
    brand: Optional[str] = Field(None, max_length=128)
    model: Optional[str] = Field(None, max_length=128)
    type: Optional[str] = Field(None, max_length=128)
    client_id: UUID
    manufacturer_id: Optional[UUID] = None
    image: Optional[str] = None


class EquipmentUpdate(BaseModel):
    serial_number: Optional[str] = Field(None, min_length=1, max_length=128)
    brand: Optional[str] = Field(None, max_length=128)
    model: Optional[str] = Field(None, max_length=128)
    type: Optional[str] = Field(None, max_length=128)
    client_id: Optional[UUID] = None
    manufacturer_id: Optional[UUID] = None
    image: Optional[str] = None


class EquipmentResponse(BaseModel):
    id: UUID
    serial_number: str
    brand: Optional[str]
    model: Optional[str]
    type: Optional[str]
    image: Optional[str]
    client_id: UUID
    client_name: str
    manufacturer_id: Optional[UUID]
    manufacturer_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EquipmentListResponse(BaseModel):
    items: List[EquipmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== Technical Document Schemas ==============
class DocumentCreate(BaseModel):
    equipment_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field(..., pattern="^(PDF|VIDEO|IMAGE)$")


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)


class DocumentResponse(BaseModel):
    id: UUID
    equipment_id: UUID
    equipment_serial: str
    title: str
    file_path: str
    document_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== Spare Part Schemas ==============
class SparePartCreate(BaseModel):
    equipment_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    reference_code: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = None
    image: Optional[str] = None


class SparePartUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    reference_code: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = None
    image: Optional[str] = None


class SparePartResponse(BaseModel):
    id: UUID
    equipment_id: UUID
    equipment_serial: str
    name: str
    reference_code: Optional[str]
    description: Optional[str]
    image: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SparePartListResponse(BaseModel):
    items: List[SparePartResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== Dashboard Schemas ==============
class DashboardStats(BaseModel):
    total_equipment: int
    total_clients: int
    total_manufacturers: int
    total_interventions: int
    total_spare_parts: int
    total_documents: int
    interventions_in_progress: int
    interventions_completed: int
    interventions_not_repaired: int


class RecentIntervention(BaseModel):
    id: UUID
    equipment_serial: str
    technician_name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
