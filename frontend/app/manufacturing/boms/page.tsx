"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

export default function Page() {
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const companyId = localStorage.getItem("company_id") || "";
    api.get<Record<string, unknown>[]>(`/manufacturing/boms${companyId ? "?company_id=${companyId}" : ""}`)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns = [{key:"version",title:"Version"},{key:"is_active",title:"Active"},{key:"finished_item_id",title:"Finished Item"}];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Bill of Materials</h1>
      <DataTable columns={columns} data={data} loading={loading} />
    </div>
  );
}
