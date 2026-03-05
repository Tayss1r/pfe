"""Admin Dashboard API"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_session
from ...dependencies import AccessTokenBearer, get_current_user, RoleChecker
from ...db.models import User
from ...services.admin_service import AdminService
from ...schemas.admin_schemas import DashboardStats, RecentIntervention

admin_dashboard_router = APIRouter(prefix="/dashboard", tags=["Admin Dashboard"])

# Require admin role
require_admin = RoleChecker(["admin"])


@admin_dashboard_router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Get dashboard statistics for admin overview"""
    return await AdminService.get_dashboard_stats(session)


@admin_dashboard_router.get("/recent-interventions", response_model=List[RecentIntervention])
async def get_recent_interventions(
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(AccessTokenBearer()),
    __: bool = Depends(require_admin),
):
    """Get recent interventions"""
    interventions = await AdminService.get_recent_interventions(session, limit)
    return [
        RecentIntervention(
            id=i.id,
            equipment_serial=i.equipment.serial_number if i.equipment else "N/A",
            technician_name=i.technician.fullname if i.technician else "N/A",
            status=i.status,
            created_at=i.created_at,
        )
        for i in interventions
    ]
