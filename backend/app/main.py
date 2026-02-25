from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _bootstrap_admin()
    yield


def _bootstrap_admin():
    from app.core.database import SessionLocal
    from app.core.config import settings
    from app.crud.auth import get_user_by_email, create_user, create_role, create_permission, assign_permission_to_role, assign_role_to_user

    db = SessionLocal()
    try:
        all_permissions = [
            ("ACCOUNTING_VIEW", "View accounting data", "ACCOUNTING"),
            ("ACCOUNTING_POST", "Post journals and invoices", "ACCOUNTING"),
            ("ACCOUNTING_REPORTS_VIEW", "View accounting reports", "ACCOUNTING"),
            ("ACCOUNTING_FORECASTS_MANAGE", "Manage budgets and forecasts", "ACCOUNTING"),
            ("PAYROLL_RUN", "Run payroll", "HRM"),
            ("HR_VIEW", "View HR data", "HRM"),
            ("HR_REPORTS_VIEW", "View HR reports", "HRM"),
            ("CRM_MANAGE", "Manage CRM", "CRM"),
            ("CRM_REPORTS_VIEW", "View CRM reports", "CRM"),
            ("PROJECTS_MANAGE", "Manage projects", "PROJECTS"),
            ("PROJECTS_REPORTS_VIEW", "View project reports", "PROJECTS"),
            ("FARM_MANAGE", "Manage farm", "FARM"),
            ("FARM_REPORTS_VIEW", "View farm reports", "FARM"),
            ("MANUFACTURING_MANAGE", "Manage manufacturing", "MANUFACTURING"),
            ("MANUFACTURING_REPORTS_VIEW", "View manufacturing reports", "MANUFACTURING"),
            ("HOSPITALITY_MANAGE", "Manage hospitality", "HOSPITALITY"),
            ("HOSPITALITY_REPORTS_VIEW", "View hospitality reports", "HOSPITALITY"),
            ("TRAVEL_MANAGE", "Manage travel", "TRAVEL"),
            ("TRAVEL_REPORTS_VIEW", "View travel reports", "TRAVEL"),
            ("TRADING_MANAGE", "Manage trading", "TRADING"),
            ("TRADING_REPORTS_VIEW", "View trading reports", "TRADING"),
            ("INVENTORY_MANAGE", "Manage inventory", "INVENTORY"),
            ("INVENTORY_REPORTS_VIEW", "View inventory reports", "INVENTORY"),
            ("AUDIT_VIEW", "View audit logs", "SECURITY"),
            ("SYSTEM_ADMIN", "System administration", "SYSTEM"),
        ]
        perms = []
        for name, desc, module in all_permissions:
            p = create_permission(db, name, desc, module)
            perms.append(p)

        from app.models.auth import Role
        admin_role = db.query(Role).filter(Role.name == "Super Admin").first()
        if not admin_role:
            admin_role = create_role(db, "Super Admin", "Full system access")
            for p in perms:
                assign_permission_to_role(db, admin_role.id, p.id)

        admin = get_user_by_email(db, settings.FIRST_ADMIN_EMAIL)
        if not admin:
            admin = create_user(db, settings.FIRST_ADMIN_EMAIL, "System Administrator", settings.FIRST_ADMIN_PASSWORD, is_superuser=True)
            assign_role_to_user(db, admin.id, admin_role.id)
    finally:
        db.close()


app = FastAPI(
    title="Fincepto ERP",
    description="Enterprise ERP Accounting System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "fincepto-erp"}
