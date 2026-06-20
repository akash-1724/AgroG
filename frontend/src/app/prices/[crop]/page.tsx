"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Loader2 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

type PriceRecord = {
  id: string;
  crop_name: string;
  market: string;
  district?: string;
  state: string;
  min_price: number;
  max_price: number;
  modal_price: number;
  unit: string;
  recorded_date: string;
  source: string;
  is_sample: boolean;
};

export default function CropPriceDetailPage() {
  const params = useParams<{ crop: string }>();
  const crop = decodeURIComponent(params.crop);
  const [state, setState] = React.useState("");
  const [market, setMarket] = React.useState("");
  const { data, isLoading, error } = useQuery({
    queryKey: ["price-trends", crop, state, market],
    queryFn: async () => {
      const search = new URLSearchParams({ crop });
      if (state) search.set("state", state);
      if (market) search.set("market", market);
      return (await api.get(`/prices/trends?${search.toString()}`)).data as { records: PriceRecord[]; provider_status: string; is_sample: boolean; disclaimer?: string };
    },
  });

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <Link href="/prices" className="inline-flex items-center gap-2 text-sm font-semibold text-primary"><ArrowLeft className="h-4 w-4" /> Back to prices</Link>
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-primary capitalize">{crop} Price Trend</h1>
        <p className="text-muted-foreground mt-1">Filter by simple market/state values where records exist.</p>
      </div>

      {data?.disclaimer && <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm font-medium text-amber-900">{data.disclaimer}</div>}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl">
        <Input value={state} onChange={(event) => setState(event.target.value)} placeholder="State filter" />
        <Input value={market} onChange={(event) => setMarket(event.target.value)} placeholder="Market filter" />
      </div>

      {isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground"><Loader2 className="h-4 w-4 animate-spin" /> Loading trend...</div>
      ) : error ? (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">Unable to load trend records.</div>
      ) : !data?.records.length ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">No price records are available for this crop/filter. No prices were invented.</div>
      ) : (
        <div className="space-y-3">
          {data.records.map((record) => (
            <Card key={record.id}>
              <CardHeader>
                <CardTitle className="text-lg">{record.market}, {record.state}</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <p><strong>Modal:</strong> ₹{record.modal_price}/{record.unit}</p>
                <p><strong>Range:</strong> ₹{record.min_price} - ₹{record.max_price}</p>
                <p><strong>Date:</strong> {record.recorded_date}</p>
                <p><strong>Source:</strong> {record.source}</p>
                <span className={`w-fit rounded-full px-2 py-1 text-xs font-bold ${record.is_sample ? "bg-amber-100 text-amber-900" : "bg-emerald-100 text-emerald-900"}`}>
                  {record.is_sample ? "Sample/demo" : "Live/imported"}
                </span>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
