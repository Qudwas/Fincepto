"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

interface AuditLog {
  id: string;
  user_email: string;
  timestamp: string;
  action: string;
  entity_type: string;
  entity_id: string;
  module: string;
  ip_address: string;
}

export default function AuditPage() {
  const [data, setData] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<AuditLog[]>("/audit/logs?limit=200")
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: "timestamp", title: "Timestamp", render: (r: AuditLog) => new Date(r.timestamp).toLocaleString() },
    { key: "user_email", title: "User" },
    { key: "action", title: "Action" },
    { key: "entity_type", title: "Entity Type" },
    { key: "entity_id", title: "Entity ID" },
    { key: "module", title: "Module" },
    { key: "ip_address", title: "IP Address" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Audit Log</h1>
      <p className="text-sm text-gray-500 mb-4">Read-only immutable audit trail of all system actions</p>
      <DataTable columns={columns} data={data} loading={loading} />
    </div>
  );
}
