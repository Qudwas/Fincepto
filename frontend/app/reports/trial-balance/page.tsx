"use client";
import { useState } from "react";
import { api } from "@/lib/api";

interface TBData {
  as_of_date: string;
  lines: Array<{account_id: string; code: string; name: string; account_type: string; debit: number; credit: number; balance: number}>;
  total_debit: number;
  total_credit: number;
}

export default function TrialBalancePage() {
  const [data, setData] = useState<TBData | null>(null);
  const [loading, setLoading] = useState(false);
  const [asOfDate, setAsOfDate] = useState(new Date().toISOString().split("T")[0]);

  const run = async () => {
    const companyId = localStorage.getItem("company_id") || "";
    if (!companyId) return alert("Set company_id in localStorage first");
    setLoading(true);
    try {
      setData(await api.get<TBData>(`/reports/trial-balance?company_id=${companyId}&as_of_date=${asOfDate}`));
    } finally { setLoading(false); }
  };

  const fmt = (n: number) => new Intl.NumberFormat("en-US", {minimumFractionDigits: 2}).format(n);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Trial Balance</h1>
      <div className="bg-white p-4 rounded-lg shadow-sm border mb-6 flex gap-4 items-end">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">As of Date</label>
          <input type="date" value={asOfDate} onChange={e => setAsOfDate(e.target.value)} className="border rounded px-3 py-1.5 text-sm" />
        </div>
        <button onClick={run} disabled={loading} className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Loading..." : "Run Report"}
        </button>
      </div>
      {data && (
        <div className="bg-white rounded-lg shadow-sm border overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Code</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Account</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Type</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Debit</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Credit</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase">Balance</th>
              </tr>
            </thead>
            <tbody>
              {data.lines.map((l, i) => (
                <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="px-4 py-2">{l.code}</td>
                  <td className="px-4 py-2">{l.name}</td>
                  <td className="px-4 py-2 text-gray-500">{l.account_type}</td>
                  <td className="px-4 py-2 text-right">{l.debit ? fmt(l.debit) : "-"}</td>
                  <td className="px-4 py-2 text-right">{l.credit ? fmt(l.credit) : "-"}</td>
                  <td className={`px-4 py-2 text-right font-medium ${l.balance < 0 ? "text-red-600" : ""}`}>{fmt(l.balance)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-gray-50 font-semibold">
              <tr>
                <td colSpan={3} className="px-4 py-3">Total</td>
                <td className="px-4 py-3 text-right">{fmt(data.total_debit)}</td>
                <td className="px-4 py-3 text-right">{fmt(data.total_credit)}</td>
                <td className="px-4 py-3 text-right">{fmt(data.total_debit - data.total_credit)}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </div>
  );
}
