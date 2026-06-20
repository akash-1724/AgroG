"use client";

import { useQuery } from "@tanstack/react-query";
import { BarChart3, Loader2 } from "lucide-react";

import ProtectedRoute from "@/components/ProtectedRoute";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

type AnalyticsOverview = {
  users: { total: number; by_role: Record<string, number>; new_over_time: { date: string; count: number }[] };
  listings: { total: number; by_status: Record<string, number>; by_category: Record<string, number> };
  orders: { total: number; by_status: Record<string, number>; gross_value: number; average_value: number };
  advisory: { crop_recommendations: number; fertilizer_recommendations: number; disease_detections: number; recommendation_history: number };
  content: { educational_resources: number };
  trust: { reviews: number; average_rating?: number | null };
};

function MetricCard({ title, value, note }: { title: string; value: string | number; note?: string }) {
  return (
    <Card>
      <CardHeader className="pb-2"><CardTitle className="text-sm text-slate-500">{title}</CardTitle></CardHeader>
      <CardContent><div className="text-3xl font-extrabold text-slate-950">{value}</div>{note && <p className="text-xs text-slate-500 mt-1">{note}</p>}</CardContent>
    </Card>
  );
}

function Breakdown({ title, data }: { title: string; data: Record<string, number> }) {
  return (
    <Card>
      <CardHeader><CardTitle>{title}</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {Object.keys(data).length === 0 ? <p className="text-sm text-slate-500">No data yet.</p> : Object.entries(data).map(([key, value]) => (
          <div key={key} className="flex items-center justify-between border-b border-slate-100 pb-2 text-sm">
            <span className="capitalize text-slate-600">{key}</span>
            <span className="font-bold text-slate-900">{value}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

export default function AdminDashboardPage() {
  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <AdminDashboardContent />
    </ProtectedRoute>
  );
}

function AdminDashboardContent() {
  const { data, isLoading, error } = useQuery<AnalyticsOverview>({
    queryKey: ["admin-analytics-overview"],
    queryFn: async () => (await api.get("/admin/analytics/overview")).data,
  });

  if (isLoading) return <div className="flex items-center justify-center min-h-[50vh] gap-2 text-slate-500"><Loader2 className="h-5 w-5 animate-spin" /> Loading analytics...</div>;
  if (error || !data) return <div className="max-w-3xl mx-auto p-8 text-red-600">Unable to load admin analytics.</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 flex items-center gap-2"><BarChart3 className="h-8 w-8 text-emerald-600" /> Admin Dashboard</h1>
        <p className="text-slate-500 text-sm mt-1">Real database-backed operational overview.</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Users" value={data.users.total} note="Registered accounts" />
        <MetricCard title="Listings" value={data.listings.total} note="Marketplace listings" />
        <MetricCard title="Orders" value={data.orders.total} note={`Gross $${data.orders.gross_value.toFixed(2)}`} />
        <MetricCard title="Reviews" value={data.trust.reviews} note={data.trust.average_rating ? `Avg ${data.trust.average_rating}/5` : "No rating average"} />
        <MetricCard title="Crop AI" value={data.advisory.crop_recommendations} />
        <MetricCard title="Fertilizer AI" value={data.advisory.fertilizer_recommendations} />
        <MetricCard title="Disease Scans" value={data.advisory.disease_detections} />
        <MetricCard title="Resources" value={data.content.educational_resources} />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Breakdown title="Users by Role" data={data.users.by_role} />
        <Breakdown title="Listings by Status" data={data.listings.by_status} />
        <Breakdown title="Orders by Status" data={data.orders.by_status} />
      </div>
      <Breakdown title="Listings by Category" data={data.listings.by_category} />
    </div>
  );
}
