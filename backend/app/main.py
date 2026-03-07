from fastapi import FastAPI

from .api.auth import auth_router
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


