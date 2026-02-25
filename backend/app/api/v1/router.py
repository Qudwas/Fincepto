from fastapi import APIRouter
from app.api.v1 import (
    auth, users, roles, master, accounting, inventory, ar_ap,
    fixed_assets, hrm, crm, projects, farm, manufacturing,
    hospitality, travel, trading, budget, audit, reports,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(master.router, prefix="/master", tags=["master"])
api_router.include_router(accounting.router, prefix="/accounting", tags=["accounting"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(ar_ap.router, prefix="/ar-ap", tags=["ar-ap"])
api_router.include_router(fixed_assets.router, prefix="/fixed-assets", tags=["fixed-assets"])
api_router.include_router(hrm.router, prefix="/hrm", tags=["hrm"])
api_router.include_router(crm.router, prefix="/crm", tags=["crm"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(farm.router, prefix="/farm", tags=["farm"])
api_router.include_router(manufacturing.router, prefix="/manufacturing", tags=["manufacturing"])
api_router.include_router(hospitality.router, prefix="/hospitality", tags=["hospitality"])
api_router.include_router(travel.router, prefix="/travel", tags=["travel"])
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
api_router.include_router(budget.router, prefix="/budget", tags=["budget"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
