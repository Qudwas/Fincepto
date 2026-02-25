"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

interface Invoice {
  id: string;
  invoice_number: string;
  invoice_type: string;
  invoice_date: string;
  total_amount: number;
  paid_amount: number;
  status: string;
}

export default function InvoicesPage() {
  const [data, setData] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [type, setType] = useState("CUSTOMER");

  useEffect(() => {
    const cid = localStorage.getItem("company_id") || "";
    api.get<Invoice[]>(`/ar-ap/invoices${cid ? `?company_id=${cid}&invoice_type=${type}` : ""}`)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [type]);

  const fmt = (n: number) => new Intl.NumberFormat("en-US", {minimumFractionDigits: 2}).format(n);

  const columns = [
    { key: "invoice_number", title: "Invoice #" },
    { key: "invoice_type", title: "Type" },
    { key: "invoice_date", title: "Date" },
    { key: "total_amount", title: "Total", render: (r: Invoice) => fmt(r.total_amount) },
    { key: "paid_amount", title: "Paid", render: (r: Invoice) => fmt(r.paid_amount) },
    { key: "status", title: "Status", render: (r: Invoice) => (
      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${r.status === "PAID" ? "bg-green-100 text-green-800" : r.status === "POSTED" ? "bg-blue-100 text-blue-800" : "bg-yellow-100 text-yellow-800"}`}>
        {r.status}
      </span>
    )},
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
        <div className="flex gap-2">
          {["CUSTOMER", "SUPPLIER"].map(t => (
            <button key={t} onClick={() => setType(t)} className={`px-3 py-1.5 rounded text-sm ${type === t ? "bg-blue-600 text-white" : "bg-gray-100 hover:bg-gray-200"}`}>{t}</button>
          ))}
        </div>
      </div>
      <DataTable columns={columns} data={data} loading={loading} />
    </div>
  );
}
