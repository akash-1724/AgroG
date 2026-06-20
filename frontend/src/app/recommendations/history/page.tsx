"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Clock, Loader2 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { api } from "@/lib/api";

type HistoryItem = {
  id: string;
  recommendation_type: string;
  model_status?: string;
  used_weather: boolean;
  created_at: string;
};

export default function RecommendationHistoryPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["recommendation-history"],
    queryFn: async () => (await api.get("/recommendations/history")).data as HistoryItem[],
  });

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-primary flex items-center gap-2">
          <Clock className="h-8 w-8" /> Recommendation History
        </h1>
        <p className="text-muted-foreground mt-1">Review your saved crop, fertilizer, and disease recommendations.</p>
      </div>

      {isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground"><Loader2 className="h-4 w-4 animate-spin" /> Loading history...</div>
      ) : error ? (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">Sign in to view recommendation history.</div>
      ) : !data?.length ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">No saved recommendations yet.</div>
      ) : (
        <div className="space-y-3">
          {data.map((item) => (
            <Link key={item.id} href={`/recommendations/history/${item.id}`}>
              <Card className="hover:border-primary/40 hover:shadow-md transition">
                <CardHeader>
                  <CardTitle className="capitalize">{item.recommendation_type} recommendation</CardTitle>
                  <CardDescription>{new Date(item.created_at).toLocaleString()}</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-2 text-xs font-bold">
                  <span className="rounded-full bg-slate-100 px-2 py-1 text-slate-700">Model: {item.model_status || "unknown"}</span>
                  <span className={`rounded-full px-2 py-1 ${item.used_weather ? "bg-sky-100 text-sky-900" : "bg-slate-100 text-slate-700"}`}>
                    Weather {item.used_weather ? "used" : "not used"}
                  </span>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
