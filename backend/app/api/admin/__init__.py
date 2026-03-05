"""Admin API Module"""
from .equipment import admin_equipment_router
from .clients import admin_clients_router
from .manufacturers import admin_manufacturers_router
from .documents import admin_documents_router
from .spare_parts import admin_spare_parts_router
from .dashboard import admin_dashboard_router

__all__ = [
    "admin_equipment_router",
    "admin_clients_router", 
    "admin_manufacturers_router",
    "admin_documents_router",
    "admin_spare_parts_router",
    "admin_dashboard_router",
]
