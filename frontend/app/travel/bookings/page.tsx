"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

export default function Page() {
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const companyId = localStorage.getItem("company_id") || "";
    api.get<Record<string, unknown>[]>(`/travel/bookings${companyId ? "?company_id=${companyId}" : ""}`)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns = [{key:"booking_number",title:"Ref #"},{key:"customer_name",title:"Customer"},{key:"travel_date",title:"Travel Date"},{key:"pax_count",title:"Pax"},{key:"total_amount",title:"Amount"},{key:"status",title:"Status"}];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Travel Bookings</h1>
      <DataTable columns={columns} data={data} loading={loading} />
    </div>
  );
}
