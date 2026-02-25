"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

interface Account {
  id: string;
  code: string;
  name: string;
  is_active: boolean;
  is_control_account: boolean;
}

export default function AccountsPage() {
  const [data, setData] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cid = localStorage.getItem("company_id") || "";
    api.get<Account[]>(`/accounting/accounts${cid ? `?company_id=${cid}` : ""}`)
      .then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: "code", title: "Code" },
    { key: "name", title: "Name" },
    { key: "is_active", title: "Active", render: (r: Account) => r.is_active ? "✓" : "✗" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Chart of Accounts</h1>
      <DataTable columns={columns} data={data} loading={loading} />
    </div>
  );
}
