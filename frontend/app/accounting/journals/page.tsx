"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

interface Journal {
  id: string;
  reference: string;
  journal_date: string;
  description: string;
  status: string;
  exchange_rate: number;
  created_at: string;
}

export default function JournalsPage() {
  const [journals, setJournals] = useState<Journal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cid = localStorage.getItem("company_id") || "";
    api.get<Journal[]>(`/accounting/journals${cid ? `?company_id=${cid}` : ""}`)
      .then(setJournals)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: "reference", title: "Reference" },
    { key: "journal_date", title: "Date" },
    { key: "description", title: "Description" },
    { key: "status", title: "Status", render: (r: Journal) => (
      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${r.status === "POSTED" ? "bg-green-100 text-green-800" : r.status === "REVERSED" ? "bg-red-100 text-red-800" : "bg-yellow-100 text-yellow-800"}`}>
        {r.status}
      </span>
    )},
    { key: "created_at", title: "Created", render: (r: Journal) => new Date(r.created_at).toLocaleDateString() },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Journals</h1>
      <DataTable columns={columns} data={journals} loading={loading} />
    </div>
  );
}
