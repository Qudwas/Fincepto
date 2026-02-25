"use client";
import { useState } from "react";
import { api } from "@/lib/api";

const REPORTS: Record<string, {label: string; endpoint: string}[]> = {
  farm: [
    {label: "Batch Performance", endpoint: "/reports/farm/batch-performance"},
    {label: "Feed Consumption", endpoint: "/reports/farm/feed-consumption"},
    {label: "Production Output", endpoint: "/reports/farm/production-output"},
  ],
  hrm: [
    {label: "Headcount", endpoint: "/reports/hrm/headcount"},
    {label: "Payroll Summary", endpoint: "/reports/hrm/payroll-summary"},
    {label: "Leave Report", endpoint: "/reports/hrm/leave"},
    {label: "Attendance", endpoint: "/reports/hrm/attendance"},
  ],
  crm: [
    {label: "Pipeline", endpoint: "/reports/crm/pipeline"},
    {label: "Conversion Rate", endpoint: "/reports/crm/conversion"},
  ],
};

export default function Page() {
  const [selected, setSelected] = useState(0);
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [fromDate, setFromDate] = useState(new Date(new Date().getFullYear(), 0, 1).toISOString().split("T")[0]);
  const [toDate, setToDate] = useState(new Date().toISOString().split("T")[0]);
  const reports = REPORTS["crm"];
  const modTitle = "crm".toUpperCase();

  const run = async () => {
    setLoading(true);
    const ep = reports[selected].endpoint;
    const cid = localStorage.getItem("company_id") || "";
    const url = `${ep}?company_id=${cid}&from_date=${fromDate}&to_date=${toDate}`;
    try { setData(await api.get(url)); } catch { setData(null); } finally { setLoading(false); }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">{modTitle} Reports</h1>
      <div className="bg-white p-4 rounded-lg shadow-sm border mb-6">
        <div className="flex gap-2 mb-4 flex-wrap">
          {reports.map((r, i) => (
            <button key={i} onClick={() => setSelected(i)} className={`px-3 py-1.5 rounded text-sm ${selected === i ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"}`}>
              {r.label}
            </button>
          ))}
        </div>
        <div className="flex gap-4 items-end">
          <div><label className="block text-xs font-medium text-gray-600 mb-1">From</label><input type="date" value={fromDate} onChange={e => setFromDate(e.target.value)} className="border rounded px-3 py-1.5 text-sm" /></div>
          <div><label className="block text-xs font-medium text-gray-600 mb-1">To</label><input type="date" value={toDate} onChange={e => setToDate(e.target.value)} className="border rounded px-3 py-1.5 text-sm" /></div>
          <button onClick={run} disabled={loading} className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50">{loading ? "Loading..." : "Run"}</button>
        </div>
      </div>
      {data && (
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <pre className="text-xs text-gray-600 overflow-auto max-h-96">{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
