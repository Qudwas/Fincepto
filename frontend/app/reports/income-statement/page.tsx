"use client";
import { useState } from "react";
import { api } from "@/lib/api";

interface PLData {
  from_date: string;
  to_date: string;
  revenue: Array<{code: string; name: string; amount: number}>;
  expenses: Array<{code: string; name: string; amount: number}>;
  total_revenue: number;
  total_expense: number;
  net_profit: number;
}

export default function IncomeStatementPage() {
  const [data, setData] = useState<PLData | null>(null);
  const [loading, setLoading] = useState(false);
  const [fromDate, setFromDate] = useState(new Date(new Date().getFullYear(), 0, 1).toISOString().split("T")[0]);
  const [toDate, setToDate] = useState(new Date().toISOString().split("T")[0]);

  const run = async () => {
    const companyId = localStorage.getItem("company_id") || "";
    if (!companyId) return alert("Set company_id in localStorage first");
    setLoading(true);
    try {
      const result = await api.get<PLData>(`/reports/income-statement?company_id=${companyId}&from_date=${fromDate}&to_date=${toDate}`);
      setData(result);
    } finally {
      setLoading(false);
    }
  };

  const fmt = (n: number) => new Intl.NumberFormat("en-US", {minimumFractionDigits: 2}).format(n);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Income Statement (P&L)</h1>
      <div className="bg-white p-4 rounded-lg shadow-sm border mb-6 flex gap-4 items-end">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">From Date</label>
          <input type="date" value={fromDate} onChange={e => setFromDate(e.target.value)} className="border rounded px-3 py-1.5 text-sm" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">To Date</label>
          <input type="date" value={toDate} onChange={e => setToDate(e.target.value)} className="border rounded px-3 py-1.5 text-sm" />
        </div>
        <button onClick={run} disabled={loading} className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Loading..." : "Run Report"}
        </button>
      </div>
      {data && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-center mb-4">Income Statement</h2>
          <p className="text-sm text-center text-gray-500 mb-6">{data.from_date} to {data.to_date}</p>
          <div className="max-w-2xl mx-auto">
            <h3 className="font-semibold text-green-700 mb-2">Revenue</h3>
            {data.revenue.map((r, i) => (
              <div key={i} className="flex justify-between py-1 text-sm border-b border-gray-50">
                <span className="text-gray-600">{r.code} - {r.name}</span>
                <span>{fmt(r.amount)}</span>
              </div>
            ))}
            <div className="flex justify-between py-2 font-semibold text-green-700 border-t mt-2">
              <span>Total Revenue</span><span>{fmt(data.total_revenue)}</span>
            </div>
            <h3 className="font-semibold text-red-700 mb-2 mt-6">Expenses</h3>
            {data.expenses.map((e, i) => (
              <div key={i} className="flex justify-between py-1 text-sm border-b border-gray-50">
                <span className="text-gray-600">{e.code} - {e.name}</span>
                <span>{fmt(e.amount)}</span>
              </div>
            ))}
            <div className="flex justify-between py-2 font-semibold text-red-700 border-t mt-2">
              <span>Total Expenses</span><span>{fmt(data.total_expense)}</span>
            </div>
            <div className={`flex justify-between py-3 font-bold text-lg border-t-2 mt-4 ${data.net_profit >= 0 ? "text-green-700" : "text-red-700"}`}>
              <span>Net Profit / (Loss)</span><span>{fmt(data.net_profit)}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
