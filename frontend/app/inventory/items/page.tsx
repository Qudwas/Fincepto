"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

export default function Page() {
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const companyId = localStorage.getItem("company_id") || "";
    api.get<Record<string, unknown>[]>(`/inventory/items${companyId ? "?company_id=${companyId}" : ""}`)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns = [{key:"code",title:"Code"},{key:"name",title:"Name"},{key:"unit_of_measure",title:"UOM"},{key:"costing_method",title:"Costing"},{key:"sale_price",title:"Sale Price"}];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Items</h1>
      <DataTable columns={columns} data={data} loading={loading} />
    </div>
  );
}
