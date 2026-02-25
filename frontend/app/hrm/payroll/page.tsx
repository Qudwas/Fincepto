"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

export default function Page() {
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const companyId = localStorage.getItem("company_id") || "";
    api.get<Record<string, unknown>[]>(`/hrm/payroll-runs${companyId ? "?company_id=${companyId}" : ""}`)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns = [{key:"period_start",title:"Period Start"},{key:"period_end",title:"Period End"},{key:"status",title:"Status"},{key:"total_gross",title:"Gross"},{key:"total_net",title:"Net"}];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Payroll Runs</h1>
      <DataTable columns={columns} data={data} loading={loading} />
    </div>
  );
}
