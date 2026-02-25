"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

export default function Page() {
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const companyId = localStorage.getItem("company_id") || "";
    api.get<Record<string, unknown>[]>(`/hrm/employees${companyId ? "?company_id=${companyId}" : ""}`)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns = [{key:"employee_number",title:"Emp #"},{key:"first_name",title:"First Name"},{key:"last_name",title:"Last Name"},{key:"job_title",title:"Title"},{key:"employment_type",title:"Type"},{key:"basic_salary",title:"Salary"},{key:"is_active",title:"Active"}];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Employees</h1>
      <DataTable columns={columns} data={data} loading={loading} />
    </div>
  );
}
