"use client";
import { useAuth } from "@/hooks/useAuth";

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div className="text-sm text-gray-500">
        {new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
      </div>
      <div className="flex items-center gap-4">
        {user && (
          <>
            <span className="text-sm text-gray-700">
              <strong>{user.full_name}</strong>
              {user.is_superuser && (
                <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">Admin</span>
              )}
            </span>
            <button
              onClick={logout}
              className="text-sm text-red-600 hover:text-red-800 transition-colors"
            >
              Logout
            </button>
          </>
        )}
      </div>
    </header>
  );
}
