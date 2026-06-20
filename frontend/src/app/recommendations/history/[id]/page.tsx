"use client";

import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";
import { api } from "@/lib/api";

type HistoryDetail = {
  id: string;
  recommendation_type: string;
  model_status?: string;
  used_weather: boolean;
  created_at: string;
  input_payload: Record<string, unknown>;
  result_payload: Record<string, unknown>;
};

export default function RecommendationHistoryDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { data, isLoading, error } = useQuery({
    queryKey: ["recommendation-history", params.id],
    queryFn: async () => (await api.get(`/recommendations/history/${params.id}`)).data as HistoryDetail,
  });

  const deleteMutation = useMutation({
    mutationFn: async () => api.delete(`/recommendations/history/${params.id}`),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["recommendation-history"] });
      toast({ title: "History deleted", description: "Recommendation history item was removed." });
      router.push("/recommendations/history");
    },
    onError: () => {
      toast({ title: "Delete failed", description: "Could not delete this history item.", variant: "destructive" });
    },
  });

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <Link href="/recommendations/history" className="inline-flex items-center gap-2 text-sm font-semibold text-primary"><ArrowLeft className="h-4 w-4" /> Back to history</Link>

      {isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground"><Loader2 className="h-4 w-4 animate-spin" /> Loading history item...</div>
      ) : error || !data ? (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">History item not found or you do not have access.</div>
      ) : (
        <>
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-primary capitalize">{data.recommendation_type} recommendation</h1>
              <p className="text-muted-foreground mt-1">{new Date(data.created_at).toLocaleString()} · Model: {data.model_status || "unknown"} · Weather {data.used_weather ? "used" : "not used"}</p>
            </div>
            <Button variant="destructive" onClick={() => deleteMutation.mutate()} disabled={deleteMutation.isPending}>
              {deleteMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />} Delete
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Saved Input</CardTitle>
                <CardDescription>Request payload saved for this recommendation.</CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="overflow-auto rounded-lg bg-slate-950 p-4 text-xs text-slate-100">{JSON.stringify(data.input_payload, null, 2)}</pre>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Saved Result</CardTitle>
                <CardDescription>Recommendation result returned by AgroGuide.</CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="overflow-auto rounded-lg bg-slate-950 p-4 text-xs text-slate-100">{JSON.stringify(data.result_payload, null, 2)}</pre>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
