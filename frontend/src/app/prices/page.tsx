"use client";

import * as React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { BarChart3, Loader2, Search } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

type PriceCrop = {
  crop_name: string;
  latest_recorded_date?: string;
  markets: string[];
  states: string[];
  is_sample: boolean;
  source: string;
};

export default function PricesPage() {
  const [search, setSearch] = React.useState("");
  const { data, isLoading, error } = useQuery({
    queryKey: ["price-crops"],
    queryFn: async () => (await api.get("/prices/crops")).data as { crops: PriceCrop[]; provider_status: string; disclaimer?: string },
  });

  const crops = (data?.crops || []).filter((item) => item.crop_name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-primary flex items-center gap-2">
          <BarChart3 className="h-8 w-8" /> Crop Price Trends
        </h1>
        <p className="text-muted-foreground mt-1">Browse available crop price records with source and sample/live labels.</p>
      </div>

      {data?.disclaimer && <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm font-medium text-amber-900">{data.disclaimer}</div>}

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input value={search} onChange={(event) => setSearch(event.target.value)} className="pl-9" placeholder="Search crops" />
      </div>

      {isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground"><Loader2 className="h-4 w-4 animate-spin" /> Loading prices...</div>
      ) : error ? (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">Unable to load price data.</div>
      ) : crops.length === 0 ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">No price records are available for this search.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {crops.map((item) => (
            <Link key={item.crop_name} href={`/prices/${encodeURIComponent(item.crop_name)}`}>
              <Card className="h-full hover:border-primary/40 hover:shadow-md transition">
                <CardHeader>
                  <CardTitle className="capitalize">{item.crop_name}</CardTitle>
                  <CardDescription>{item.markets.length} market(s), latest {item.latest_recorded_date || "unknown"}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  <p><strong>States:</strong> {item.states.join(", ") || "Unknown"}</p>
                  <p><strong>Source:</strong> {item.source}</p>
                  <span className={`inline-flex rounded-full px-2 py-1 text-xs font-bold ${item.is_sample ? "bg-amber-100 text-amber-900" : "bg-emerald-100 text-emerald-900"}`}>
                    {item.is_sample ? "Sample/demo data" : "Live/imported data"}
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
