"use client";
import { useState } from "react";
import { api } from "@/lib/api";

export default function Page() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [fromDate, setFromDate] = useState(new Date(new Date().getFullYear(), 0, 1).toISOString().split("T")[0]);
  const [toDate, setToDate] = useState(new Date().toISOString().split("T")[0]);

  const run = async () => {
    setLoading(true);
    const cid = localStorage.getItem("company_id") || "";
    const url = `/reports/cash-flow?company_id=${cid}&from_date=${fromDate}&to_date=${toDate}`;
    try { setData(await api.get(url)); } finally { setLoading(false); }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Cash Flow</h1>
      <div className="bg-white p-4 rounded-lg shadow-sm border mb-6 flex gap-4 items-end flex-wrap">
        <div><label className="block text-xs font-medium text-gray-600 mb-1">From Date</label><input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} className="border rounded px-3 py-1.5 text-sm" /></div>
        <div><label className="block text-xs font-medium text-gray-600 mb-1">To Date</label>
        <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} className="border rounded px-3 py-1.5 text-sm" /></div>
        <button onClick={run} disabled={loading} className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Loading..." : "Run Report"}
        </button>
      </div>
      {data && (
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <pre className="text-xs text-gray-600 overflow-auto max-h-96">{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
