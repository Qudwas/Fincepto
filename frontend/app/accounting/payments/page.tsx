"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";
export default function Page() {
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const cid = localStorage.getItem("company_id") || "";
    api.get<Record<string, unknown>[]>("/ar-ap/payments" + (cid ? "?company_id=" + cid : ""))
      .then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Payments</h1>
      <DataTable columns={Object.keys(data[0] || {}).slice(0,6).map(k => ({key:k,title:k}))} data={data} loading={loading} />
    </div>
  );
}
