"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

export default function Page() {
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const companyId = localStorage.getItem("company_id") || "";
    api.get<Record<string, unknown>[]>(`/trading/purchase-orders${companyId ? "?company_id=${companyId}" : ""}`)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns = [{key:"order_number",title:"PO #"},{key:"order_date",title:"Date"},{key:"status",title:"Status"},{key:"total_amount",title:"Total"}];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Purchase Orders</h1>
      <DataTable columns={columns} data={data} loading={loading} />
    </div>
  );
}
