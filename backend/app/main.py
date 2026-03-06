from fastapi import FastAPI

from .api.auth import auth_router
from .api.equipment import equipment_router
from .api.contact import contact_router
from .api.intervention import intervention_router
from .api.admin import (
    admin_dashboard_router,
    admin_equipment_router,
    admin_clients_router,
    admin_manufacturers_router,
    admin_documents_router,
    admin_spare_parts_router,
)
from .middleware import register_middleware
from .errors import register_all_errors

API_VERSION = "v1"
app = FastAPI(
    version=API_VERSION,
)

# Register middleware (CORS, etc.)
register_middleware(app)

# Register custom exception handlers
register_all_errors(app)

# Include authentication router
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include equipment router
app.include_router(equipment_router, prefix="/equipment", tags=["Equipment"])

# Include intervention router
app.include_router(intervention_router, prefix="/interventions", tags=["Interventions"])

# Include contact router
app.include_router(contact_router, prefix="/contact", tags=["Contact"])

# Include admin routers
app.include_router(admin_dashboard_router, prefix="/admin", tags=["Admin"])
app.include_router(admin_equipment_router, prefix="/admin", tags=["Admin"])
app.include_router(admin_clients_router, prefix="/admin", tags=["Admin"])
app.include_router(admin_manufacturers_router, prefix="/admin", tags=["Admin"])
app.include_router(admin_documents_router, prefix="/admin", tags=["Admin"])
app.include_router(admin_spare_parts_router, prefix="/admin", tags=["Admin"])
