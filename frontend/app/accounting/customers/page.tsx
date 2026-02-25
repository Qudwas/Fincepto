"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

interface Customer {
  id: string;
  code: string;
  name: string;
  email: string | null;
  credit_limit: number;
  is_active: boolean;
}

export default function CustomersPage() {
  const [data, setData] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cid = localStorage.getItem("company_id") || "";
    api.get<Customer[]>(`/ar-ap/customers${cid ? `?company_id=${cid}` : ""}`)
      .then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: "code", title: "Code" },
    { key: "name", title: "Name" },
    { key: "email", title: "Email" },
    { key: "credit_limit", title: "Credit Limit" },
    { key: "is_active", title: "Active", render: (r: Customer) => r.is_active ? "✓" : "✗" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Customers</h1>
      <DataTable columns={columns} data={data} loading={loading} />
    </div>
  );
}
