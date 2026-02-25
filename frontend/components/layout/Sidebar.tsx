"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: "📊" },
  {
    name: "Accounting",
    icon: "💰",
    children: [
      { name: "Chart of Accounts", href: "/accounting/accounts" },
      { name: "Journals", href: "/accounting/journals" },
      { name: "Customers", href: "/accounting/customers" },
      { name: "Suppliers", href: "/accounting/suppliers" },
      { name: "Invoices", href: "/accounting/invoices" },
      { name: "Payments", href: "/accounting/payments" },
      { name: "Tax Codes", href: "/accounting/tax-codes" },
      { name: "Fiscal Years", href: "/accounting/fiscal-years" },
    ],
  },
  {
    name: "Inventory",
    icon: "📦",
    children: [
      { name: "Items", href: "/inventory/items" },
      { name: "Warehouses", href: "/inventory/warehouses" },
      { name: "Stock Movements", href: "/inventory/movements" },
    ],
  },
  {
    name: "HRM",
    icon: "👥",
    children: [
      { name: "Employees", href: "/hrm/employees" },
      { name: "Leave Requests", href: "/hrm/leave" },
      { name: "Attendance", href: "/hrm/attendance" },
      { name: "Payroll", href: "/hrm/payroll" },
    ],
  },
  {
    name: "CRM",
    icon: "🤝",
    children: [
      { name: "Leads", href: "/crm/leads" },
      { name: "Opportunities", href: "/crm/opportunities" },
      { name: "Sales Orders", href: "/crm/sales-orders" },
    ],
  },
  {
    name: "Projects",
    icon: "📋",
    children: [
      { name: "Projects", href: "/projects" },
      { name: "Tasks", href: "/projects/tasks" },
      { name: "Timesheets", href: "/projects/timesheets" },
    ],
  },
  {
    name: "Farm",
    icon: "🌾",
    children: [
      { name: "Farms", href: "/farm/farms" },
      { name: "Livestock Batches", href: "/farm/batches" },
      { name: "Feed Records", href: "/farm/feed" },
      { name: "Production", href: "/farm/production" },
    ],
  },
  {
    name: "Manufacturing",
    icon: "🏭",
    children: [
      { name: "Bill of Materials", href: "/manufacturing/boms" },
      { name: "Production Orders", href: "/manufacturing/orders" },
    ],
  },
  {
    name: "Hospitality",
    icon: "🏨",
    children: [
      { name: "Rooms", href: "/hospitality/rooms" },
      { name: "Reservations", href: "/hospitality/reservations" },
      { name: "POS Sales", href: "/hospitality/pos" },
    ],
  },
  {
    name: "Travel",
    icon: "✈️",
    children: [
      { name: "Packages", href: "/travel/packages" },
      { name: "Bookings", href: "/travel/bookings" },
    ],
  },
  {
    name: "Trading",
    icon: "🛒",
    children: [
      { name: "Purchase Orders", href: "/trading/purchase-orders" },
      { name: "Goods Receipts", href: "/trading/goods-receipts" },
    ],
  },
  {
    name: "Reports",
    icon: "📈",
    children: [
      { name: "Trial Balance", href: "/reports/trial-balance" },
      { name: "Income Statement", href: "/reports/income-statement" },
      { name: "Balance Sheet", href: "/reports/balance-sheet" },
      { name: "Cash Flow", href: "/reports/cash-flow" },
      { name: "Aged Receivables", href: "/reports/aged-receivables" },
      { name: "Aged Payables", href: "/reports/aged-payables" },
      { name: "Budget vs Actual", href: "/reports/budget-vs-actual" },
      { name: "Forecast P&L", href: "/reports/forecast" },
      { name: "Farm Reports", href: "/reports/farm" },
      { name: "HR Reports", href: "/reports/hrm" },
      { name: "CRM Reports", href: "/reports/crm" },
    ],
  },
  {
    name: "Security",
    icon: "🔒",
    children: [
      { name: "Users", href: "/security/users" },
      { name: "Roles", href: "/security/roles" },
      { name: "Audit Log", href: "/audit" },
    ],
  },
  {
    name: "Master Data",
    icon: "⚙️",
    children: [
      { name: "Companies", href: "/master/companies" },
      { name: "Currencies", href: "/master/currencies" },
      { name: "Departments", href: "/master/departments" },
      { name: "Cost Centers", href: "/master/cost-centers" },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-gray-900 text-white min-h-screen flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold text-blue-400">Fincepto ERP</h1>
        <p className="text-xs text-gray-400 mt-1">Enterprise Management System</p>
      </div>
      <nav className="flex-1 overflow-y-auto p-2">
        {navigation.map((item) => (
          <div key={item.name} className="mb-1">
            {item.href ? (
              <Link
                href={item.href}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  pathname === item.href
                    ? "bg-blue-600 text-white"
                    : "text-gray-300 hover:bg-gray-700 hover:text-white"
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.name}
              </Link>
            ) : (
              <details className="group" open={item.children?.some((c) => pathname.startsWith(c.href))}>
                <summary className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white cursor-pointer list-none">
                  <span className="mr-2">{item.icon}</span>
                  {item.name}
                  <span className="ml-auto">▸</span>
                </summary>
                <div className="ml-4 mt-1 space-y-1">
                  {item.children?.map((child) => (
                    <Link
                      key={child.href}
                      href={child.href}
                      className={`block px-3 py-1.5 rounded-md text-xs transition-colors ${
                        pathname === child.href || pathname.startsWith(child.href + "/")
                          ? "bg-blue-600 text-white"
                          : "text-gray-400 hover:bg-gray-700 hover:text-white"
                      }`}
                    >
                      {child.name}
                    </Link>
                  ))}
                </div>
              </details>
            )}
          </div>
        ))}
      </nav>
    </aside>
  );
}
