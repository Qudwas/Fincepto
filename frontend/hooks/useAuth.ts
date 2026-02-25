"use client";
import { useState, useEffect, useCallback } from "react";
import { getCurrentUser, logout as doLogout, User } from "@/lib/auth";
import { useRouter } from "next/navigation";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }
    getCurrentUser()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("access_token");
      })
      .finally(() => setLoading(false));
  }, []);

  const logout = useCallback(async () => {
    await doLogout();
    setUser(null);
    router.push("/auth/login");
  }, [router]);

  return { user, loading, logout };
}
