"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

interface Role {
  id: string;
  name: string;
  description: string;
  company_id: string;
}

export default function RolesPage() {
  const [data, setData] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<Role[]>("/roles/")
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Roles</h1>
      <DataTable
        columns={[{key:"name",title:"Role Name"},{key:"description",title:"Description"}]}
        data={data}
        loading={loading}
      />
    </div>
  );
}
