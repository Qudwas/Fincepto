"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface KPI {
  total_revenue: number;
  total_expense: number;
  net_profit: number;
  total_receivables: number;
  total_payables: number;
}

const StatCard = ({ title, value, color }: { title: string; value: string; color: string }) => (
  <div className={`bg-white rounded-lg border-l-4 ${color} p-5 shadow-sm`}>
    <p className="text-sm text-gray-500">{title}</p>
    <p className="text-2xl font-bold mt-1">{value}</p>
  </div>
);

const formatCurrency = (n: number) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n);

export default function DashboardPage() {
  const [kpi, setKpi] = useState<KPI | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const today = new Date().toISOString().split("T")[0];
    const firstDay = new Date(new Date().getFullYear(), 0, 1).toISOString().split("T")[0];
    const companyId = localStorage.getItem("company_id") || "";
    if (!companyId) {
      setLoading(false);
      return;
    }
    api
      .get<KPI>(`/reports/dashboard/kpis?company_id=${companyId}&from_date=${firstDay}&to_date=${today}`)
      .then(setKpi)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
      {loading ? (
        <div className="text-gray-500">Loading KPIs...</div>
      ) : kpi ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-8">
          <StatCard title="Total Revenue (YTD)" value={formatCurrency(kpi.total_revenue)} color="border-blue-500" />
          <StatCard title="Total Expenses (YTD)" value={formatCurrency(kpi.total_expense)} color="border-red-500" />
          <StatCard title="Net Profit (YTD)" value={formatCurrency(kpi.net_profit)} color={kpi.net_profit >= 0 ? "border-green-500" : "border-red-500"} />
          <StatCard title="Receivables" value={formatCurrency(kpi.total_receivables)} color="border-yellow-500" />
          <StatCard title="Payables" value={formatCurrency(kpi.total_payables)} color="border-purple-500" />
        </div>
      ) : (
        <div className="bg-blue-50 text-blue-700 p-4 rounded-md mb-6 text-sm">
          Select a company to view KPI data. Configure your company in Master Data → Companies.
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { title: "Accounting", desc: "Journals, AR/AP, Tax", href: "/accounting/journals", icon: "💰" },
          { title: "Inventory", desc: "Stock, Movements", href: "/inventory/items", icon: "📦" },
          { title: "HRM", desc: "Employees, Payroll", href: "/hrm/employees", icon: "👥" },
          { title: "CRM", desc: "Leads, Opportunities", href: "/crm/leads", icon: "🤝" },
          { title: "Projects", desc: "Tasks, Timesheets", href: "/projects", icon: "📋" },
          { title: "Reports", desc: "Financial Statements", href: "/reports/income-statement", icon: "📈" },
        ].map((m) => (
          <a key={m.href} href={m.href} className="bg-white p-5 rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-100">
            <div className="text-3xl mb-2">{m.icon}</div>
            <h3 className="font-semibold text-gray-900">{m.title}</h3>
            <p className="text-sm text-gray-500 mt-1">{m.desc}</p>
          </a>
        ))}
      </div>
    </div>
  );
}
