# Fincepto — Enterprise ERP Accounting System

A production-ready, full-stack ERP system built with FastAPI (Python), Next.js (TypeScript), and PostgreSQL.

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Technology Stack](#technology-stack)
- [Modules](#modules)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Manual Installation](#manual-installation)
- [Database Migrations](#database-migrations)
- [Admin Bootstrap](#admin-bootstrap)
- [Environment Variables](#environment-variables)
- [Running Reports & Forecasts](#running-reports--forecasts)
- [Module-Specific Reports](#module-specific-reports)
- [API Documentation](#api-documentation)
- [Branch Structure](#branch-structure)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
fincepto/
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── core/     # Config, DB, security, dependencies
│   │   ├── models/   # SQLAlchemy ORM models
│   │   ├── schemas/  # Pydantic v2 schemas
│   │   ├── crud/     # Database operations
│   │   ├── services/ # Business logic layer
│   │   └── api/v1/   # REST API endpoints
│   └── alembic/      # Database migrations
├── frontend/         # Next.js 14 frontend
│   └── src/
│       ├── app/      # App Router pages
│       ├── components/
│       ├── hooks/
│       └── lib/
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Technology Stack

| Layer      | Technology                                  |
|------------|---------------------------------------------|
| Backend    | Python 3.11, FastAPI, SQLAlchemy 2.x        |
| Database   | PostgreSQL 15                               |
| Migrations | Alembic                                     |
| Auth       | JWT (access + refresh), Argon2 hashing      |
| Frontend   | Next.js 14, React 18, TypeScript, Tailwind  |
| Charts     | Recharts                                    |
| DevOps     | Docker, Docker Compose                      |

---

## Modules

| Module               | Features                                                              |
|----------------------|-----------------------------------------------------------------------|
| **Accounting**       | GL, AR, AP, Chart of Accounts, Double-entry Journals, Tax Engine      |
| **Inventory**        | Items, Warehouses, Stock Movements, Valuation (FIFO/Avg/Standard)    |
| **Fixed Assets**     | Asset register, Depreciation schedules, Disposal                      |
| **HRM**              | Employees, Payroll, Leave, Attendance                                 |
| **CRM**              | Leads, Opportunities, Sales Orders                                    |
| **Projects**         | Tasks, Timesheets, Billing                                            |
| **Farm & Livestock** | Farms, Batches, Feed Records, Production, Mortality                   |
| **Manufacturing**    | BOM, Production Orders, Material Consumption                          |
| **Hospitality**      | Rooms, Reservations, POS Sales                                        |
| **Travel & Tour**    | Packages, Suppliers, Bookings                                         |
| **Trading/Retail**   | Purchase Orders, Goods Receipts, Price Lists                          |
| **Budgeting**        | Budgets, Budget Lines, Budget vs Actual                               |
| **Reports**          | All modules + Financial statements + Forecasting                      |
| **Security**         | RBAC, Users, Roles, Permissions, Audit Trail                          |

---

## Prerequisites

- Docker 24+ and Docker Compose v2
- OR: Python 3.11+, Node.js 18+, PostgreSQL 15+

---

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/Qudwas/Fincepto.git
cd Fincepto

# 2. Copy and configure environment
cp .env.example .env
# Edit .env with your settings (see Environment Variables section)

# 3. Start all services
docker-compose up -d

# 4. Run database migrations
docker-compose exec backend alembic upgrade head

# 5. Bootstrap first admin user
docker-compose exec backend python -m app.scripts.bootstrap

# 6. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Manual Installation

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your database URL and secrets

# Run migrations
alembic upgrade head

# Bootstrap admin user
python -m app.scripts.bootstrap

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Start development server
npm run dev

# Build for production
npm run build
npm start
```

---

## Database Migrations

```bash
# Run all pending migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "describe your change"

# Downgrade one step
alembic downgrade -1

# Check current revision
alembic current

# Show migration history
alembic history
```

---

## Admin Bootstrap

On first run, the system automatically creates:
- An admin user with email/password from `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD`
- A "Super Admin" role with all permissions
- All default permissions for every module

To manually re-run bootstrap:
```bash
docker-compose exec backend python -m app.scripts.bootstrap
```

Default admin credentials (change immediately after first login):
- **Email**: `admin@fincepto.com`
- **Password**: `Admin@1234`

---

## Environment Variables

### Backend (`.env`)

```env
# Database
DATABASE_URL=postgresql://erp_user:erp_pass@localhost:5432/erp_db

# Security
SECRET_KEY=your-very-long-random-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# First Admin
FIRST_ADMIN_EMAIL=admin@fincepto.com
FIRST_ADMIN_PASSWORD=Admin@1234
```

### Frontend (`.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Running Reports & Forecasts

All reports are available via REST API and the frontend Reports section.

### Financial Reports

| Report               | API Endpoint                                      |
|----------------------|---------------------------------------------------|
| Trial Balance        | `GET /api/v1/reports/trial-balance`               |
| Income Statement     | `GET /api/v1/reports/income-statement`            |
| Balance Sheet        | `GET /api/v1/reports/balance-sheet`               |
| Cash Flow            | `GET /api/v1/reports/cash-flow`                   |
| Aged Receivables     | `GET /api/v1/reports/aged-receivables`            |
| Aged Payables        | `GET /api/v1/reports/aged-payables`               |
| Segment Report       | `GET /api/v1/reports/segment`                     |
| KPI Dashboard        | `GET /api/v1/reports/dashboard/kpis`              |

### Forecasting & Budgeting

| Feature              | API Endpoint                                      |
|----------------------|---------------------------------------------------|
| Budget vs Actual     | `GET /api/v1/reports/budget-vs-actual`            |
| Forecasted P&L       | `GET /api/v1/reports/forecast/pl`                 |

All report endpoints accept query parameters:
- `company_id` (required)
- `from_date` / `to_date` or `as_of_date`
- `department_id`, `cost_center_id`, `project_id` (optional dimensions)

---

## Module-Specific Reports

### Farm & Livestock
- `GET /api/v1/reports/farm/batch-performance` — Mortality, FCR, ADG, cost per kg
- `GET /api/v1/reports/farm/feed-consumption` — Feed by batch, farm, period
- `GET /api/v1/reports/farm/production-output` — Eggs, meat, crops volume & value

### Manufacturing
- `GET /api/v1/reports/manufacturing/production-orders` — Status, planned vs actual
- `GET /api/v1/reports/manufacturing/material-variance` — BOM vs actual consumption

### Hospitality
- `GET /api/v1/reports/hospitality/occupancy` — Occupancy %, ADR, RevPAR
- `GET /api/v1/reports/hospitality/revenue-by-segment` — Rooms, F&B, other
- `GET /api/v1/reports/hospitality/pos-sales` — By outlet, product, period

### Travel & Tour
- `GET /api/v1/reports/travel/booking-pipeline` — Booked vs confirmed vs cancelled
- `GET /api/v1/reports/travel/revenue-by-package` — Revenue by package/destination

### Trading / Retail
- `GET /api/v1/reports/trading/sales` — By item, category, customer, channel
- `GET /api/v1/reports/trading/gross-margin` — Margin analysis
- `GET /api/v1/reports/trading/inventory-aging` — Stock aging

### HRM
- `GET /api/v1/reports/hrm/headcount` — By company, department, location
- `GET /api/v1/reports/hrm/payroll-summary` — Salaries, tax, deductions
- `GET /api/v1/reports/hrm/leave` — Leave balances and usage
- `GET /api/v1/reports/hrm/attendance` — Tardiness, overtime, absence

### CRM
- `GET /api/v1/reports/crm/pipeline` — Opportunities by stage
- `GET /api/v1/reports/crm/conversion` — Lead to opportunity to customer conversion

### Projects
- `GET /api/v1/reports/projects/status` — Progress, budget vs actual
- `GET /api/v1/reports/projects/timesheet` — Hours by project, employee
- `GET /api/v1/reports/projects/profitability` — Revenue, costs, margin

### Inventory
- `GET /api/v1/reports/inventory/stock-on-hand` — By item, warehouse
- `GET /api/v1/reports/inventory/valuation` — By costing method

### Security & Audit
- `GET /api/v1/reports/security/user-roles` — User & role assignments
- `GET /api/v1/audit/logs` — Full audit log (filterable)

---

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Branch Structure

| Branch                          | Purpose                                        |
|---------------------------------|------------------------------------------------|
| `main`                          | Production-ready releases                      |
| `develop`                       | Integration branch for all features            |
| `feature/backend-core`          | Core backend: auth, RBAC, audit, master data   |
| `feature/accounting`            | GL, AR, AP, journals, tax engine               |
| `feature/inventory`             | Inventory, fixed assets                        |
| `feature/hrm`                   | HRM: employees, payroll, leave, attendance     |
| `feature/crm`                   | CRM: leads, opportunities, sales orders        |
| `feature/projects`              | Project management: tasks, timesheets          |
| `feature/farm-livestock`        | Farm & livestock module                        |
| `feature/manufacturing`         | Manufacturing: BOM, production orders          |
| `feature/hospitality`           | Hotel rooms, reservations, POS                 |
| `feature/travel-tour`           | Travel packages, bookings                      |
| `feature/trading-retail`        | Purchase orders, goods receipts                |
| `feature/reports-forecasting`   | Reports, budgeting & forecasting               |
| `feature/frontend`              | Next.js frontend application                   |
| `feature/devops`                | Docker, CI/CD, deployment configs              |

---

## Troubleshooting

### Database connection refused
```bash
# Check PostgreSQL is running
docker-compose ps db

# Check connection string in .env
echo $DATABASE_URL
```

### Migration fails
```bash
# Reset and re-run
alembic downgrade base
alembic upgrade head
```

### Frontend can't reach backend
```bash
# Verify NEXT_PUBLIC_API_URL in frontend .env.local
# Check backend is running on port 8000
curl http://localhost:8000/health
```

### Permission denied errors
```bash
# Ensure admin user has correct roles
docker-compose exec backend python -m app.scripts.bootstrap
```

### Port already in use
```bash
# Change ports in docker-compose.yml or stop conflicting services
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:3000 | xargs kill -9
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
