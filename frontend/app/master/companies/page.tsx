"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

export default function Page() {
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.get<Record<string, unknown>[]>("/master/companies")
      .then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Companies</h1>
      <DataTable columns={[{key:"name",title:"Name"},{key:"code",title:"Code"},{key:"is_active",title:"Active"}]} data={data} loading={loading} />
    </div>
  );
}
