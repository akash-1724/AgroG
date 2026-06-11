"use client";

import { useAuth } from "@/components/shared/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Loader2, ShieldAlert } from "lucide-react";

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: Array<"customer" | "farmer" | "admin">;
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3 text-slate-500">
        <Loader2 className="h-10 w-10 animate-spin text-emerald-500" />
        <span className="text-sm font-medium">Verifying credentials...</span>
      </div>
    );
  }

  if (!user) {
    return null; // Redirecting to /login via useEffect
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return (
      <div className="max-w-md mx-auto my-16 p-8 bg-white border border-slate-200 rounded-2xl shadow-sm text-center space-y-4">
        <div className="inline-flex p-3 rounded-full bg-red-50 text-red-600">
          <ShieldAlert className="h-8 w-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Access Denied</h2>
        <p className="text-slate-600 text-sm">
          Your account role (<span className="font-semibold uppercase">{user.role}</span>) does not have permission to access this page.
        </p>
        <button
          onClick={() => router.push(user.role === "farmer" ? "/farmer/listings" : "/marketplace")}
          className="bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium px-5 py-2 rounded-lg transition"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  return <>{children}</>;
}
