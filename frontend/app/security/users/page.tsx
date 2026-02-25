"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import DataTable from "@/components/ui/DataTable";

interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export default function UsersPage() {
  const [data, setData] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<User[]>("/users/")
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: "email", title: "Email" },
    { key: "full_name", title: "Full Name" },
    { key: "is_active", title: "Active", render: (r: User) => r.is_active ? "✅" : "❌" },
    { key: "is_superuser", title: "Admin", render: (r: User) => r.is_superuser ? "✅" : "" },
    { key: "created_at", title: "Created", render: (r: User) => new Date(r.created_at).toLocaleDateString() },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Users</h1>
      <DataTable columns={columns} data={data} loading={loading} />
    </div>
  );
}
