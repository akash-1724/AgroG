"use client";

import * as React from "react";
import { LogOut, User, Mail, Shield, Smartphone, ArrowRight } from "lucide-react";
import Link from "next/link";

import ProtectedRoute from "@/components/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { useAuth } from "@/components/shared/auth-context";

export default function AccountPage() {
  return (
    <ProtectedRoute>
      <AccountContent />
    </ProtectedRoute>
  );
}

function AccountContent() {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <div className="max-w-3xl mx-auto px-4 py-12 space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Account Profile</h1>
        <p className="text-slate-500 text-sm mt-1">Manage credentials and dashboard access</p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Info card */}
        <Card className="border-slate-200/80 shadow-sm bg-white rounded-xl">
          <CardHeader>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              <User className="h-5 w-5 text-emerald-500" />
              <span>Personal Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-2.5 border-b border-slate-100">
              <span className="text-sm font-semibold text-slate-500 flex items-center gap-2">
                <User className="h-4 w-4" /> Full Name
              </span>
              <span className="text-sm font-bold text-slate-900 mt-1 sm:mt-0">
                {user.full_name || "N/A"}
              </span>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-2.5 border-b border-slate-100">
              <span className="text-sm font-semibold text-slate-500 flex items-center gap-2">
                <Mail className="h-4 w-4" /> Email Address
              </span>
              <span className="text-sm text-slate-900 font-medium mt-1 sm:mt-0">
                {user.email || "N/A"}
              </span>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-2.5 border-b border-slate-100">
              <span className="text-sm font-semibold text-slate-500 flex items-center gap-2">
                <Shield className="h-4 w-4" /> Access Role
              </span>
              <span className="text-xs font-bold uppercase tracking-wider bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full mt-1 sm:mt-0">
                {user.role}
              </span>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-2.5 border-b border-slate-100">
              <span className="text-sm font-semibold text-slate-500 flex items-center gap-2">
                <Smartphone className="h-4 w-4" /> Phone Number
              </span>
              <span className="text-sm text-slate-900 font-medium mt-1 sm:mt-0">
                {user.phone_number || "Not provided"}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Dashboard Actions and Sign out */}
        <Card className="border-slate-200/80 shadow-sm bg-white rounded-xl">
          <CardHeader>
            <CardTitle className="text-lg font-bold">Quick Shortcuts</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {user.role === "farmer" ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Link href="/farmer/listings">
                  <Button className="w-full flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold">
                    Go to Crop Catalog <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/farmer/orders">
                  <Button variant="outline" className="w-full">
                    View Incoming Orders
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Link href="/marketplace">
                  <Button className="w-full flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold">
                    Shop Marketplace <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/orders">
                  <Button variant="outline" className="w-full">
                    Track Orders History
                  </Button>
                </Link>
              </div>
            )}

            <div className="border-t border-slate-100 pt-4 mt-2">
              <Button
                onClick={logout}
                variant="outline"
                className="w-full text-red-500 hover:bg-red-50 hover:border-red-200 flex items-center justify-center gap-2"
              >
                <LogOut className="h-4 w-4" /> Log Out Account
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
