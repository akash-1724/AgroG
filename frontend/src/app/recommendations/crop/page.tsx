"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useMutation } from "@tanstack/react-query";
import { Sprout, AlertCircle, ArrowRight, Loader2, RefreshCw } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { api } from "@/lib/api";

const cropFormSchema = z.object({
  nitrogen: z.coerce.number().min(0, "Must be >= 0").max(200, "Must be <= 200"),
  phosphorus: z.coerce.number().min(0, "Must be >= 0").max(200, "Must be <= 200"),
  potassium: z.coerce.number().min(0, "Must be >= 0").max(200, "Must be <= 200"),
  ph: z.coerce.number().min(3.5, "pH must be between 3.5 and 9.0").max(9.0, "pH must be between 3.5 and 9.0"),
  temperature: z.coerce.number().min(0, "Must be >= 0").max(50, "Must be <= 50"),
  humidity: z.coerce.number().min(10, "Humidity must be 10-100%").max(100, "Humidity must be 10-100%"),
  rainfall: z.coerce.number().min(10, "Rainfall must be >= 10mm").max(500, "Rainfall must be <= 500mm"),
});

type CropFormValues = z.infer<typeof cropFormSchema>;

export default function CropRecommendationPage() {
  const { toast } = useToast();
  const [recommendations, setRecommendations] = React.useState<string[] | null>(null);
  const [modelStatus, setModelStatus] = React.useState<string | null>(null);
  const [disclaimer, setDisclaimer] = React.useState<string | null>(null);
  const [limitations, setLimitations] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CropFormValues>({
    resolver: zodResolver(cropFormSchema as unknown as Parameters<typeof zodResolver>[0]),
    defaultValues: {
      nitrogen: 50,
      phosphorus: 50,
      potassium: 50,
      ph: 6.5,
      temperature: 25,
      humidity: 60,
      rainfall: 100,
    },
  });

  const recommendationMutation = useMutation({
    mutationFn: async (values: CropFormValues) => {
      const response = await api.post("/recommendations/crop", values);
      return response.data;
    },
    onSuccess: (data) => {
      setRecommendations(data.recommendations || data.recommended_crops || []);
      setModelStatus(data.model_status || "demo");
      setDisclaimer(data.disclaimer || "");
      setLimitations(data.limitations || "");
      toast({
        title: "Analysis Complete",
        description: "Successfully processed soil and climate parameters.",
        variant: "default",
      });
    },
    onError: (err: unknown) => {
      const errMsg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "ML model recommendation failed.";
      toast({
        title: "Recommendation Failed",
        description: errMsg,
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data: CropFormValues) => {
    recommendationMutation.mutate(data);
  };

  const handleReset = () => {
    reset();
    setRecommendations(null);
    setModelStatus(null);
    setDisclaimer(null);
    setLimitations(null);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-primary flex items-center gap-2">
          <Sprout className="h-8 w-8 text-primary" /> Crop Recommendation System
        </h1>
        <p className="text-muted-foreground mt-1">
          Input your soil chemistry metrics and weather values to find the most suitable crops to plant.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Form Column */}
        <Card className="border-secondary/20 shadow-md">
          <CardHeader>
            <CardTitle className="text-lg font-bold">Soil & Climate Parameters</CardTitle>
            <CardDescription>All fields are required to calculate predictions.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Nitrogen (N)</label>
                  <Input {...register("nitrogen")} type="number" step="any" placeholder="N" />
                  {errors.nitrogen && <p className="text-[10px] text-destructive">{errors.nitrogen.message}</p>}
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Phosphorus (P)</label>
                  <Input {...register("phosphorus")} type="number" step="any" placeholder="P" />
                  {errors.phosphorus && <p className="text-[10px] text-destructive">{errors.phosphorus.message}</p>}
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Potassium (K)</label>
                  <Input {...register("potassium")} type="number" step="any" placeholder="K" />
                  {errors.potassium && <p className="text-[10px] text-destructive">{errors.potassium.message}</p>}
                </div>
              </div>

              <div className="h-px bg-muted my-2" />

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">pH Level</label>
                  <Input {...register("ph")} type="number" step="0.1" placeholder="3.5 - 9.0" />
                  {errors.ph && <p className="text-[10px] text-destructive">{errors.ph.message}</p>}
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Temperature (°C)</label>
                  <Input {...register("temperature")} type="number" step="any" placeholder="e.g. 25" />
                  {errors.temperature && <p className="text-[10px] text-destructive">{errors.temperature.message}</p>}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Humidity (%)</label>
                  <Input {...register("humidity")} type="number" step="any" placeholder="10 - 100" />
                  {errors.humidity && <p className="text-[10px] text-destructive">{errors.humidity.message}</p>}
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Rainfall (mm)</label>
                  <Input {...register("rainfall")} type="number" step="any" placeholder="Rainfall in mm" />
                  {errors.rainfall && <p className="text-[10px] text-destructive">{errors.rainfall.message}</p>}
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  disabled={recommendationMutation.isPending}
                  className="flex-1 font-bold flex items-center justify-center gap-2"
                >
                  {recommendationMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" /> Analyzing...
                    </>
                  ) : (
                    <>
                      Get Recommendation <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </Button>
                {recommendations && (
                  <Button type="button" variant="outline" onClick={handleReset}>
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Results Column */}
        <div className="flex flex-col justify-start space-y-4">
          <Card className="h-full border-secondary/20 shadow-md flex flex-col">
            <CardHeader className="bg-primary/5 rounded-t-xl">
              <CardTitle className="text-lg font-bold text-primary flex items-center gap-2">
                🌱 Recommendation Diagnostic
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-grow flex flex-col items-center justify-center p-6 text-center">
              {recommendationMutation.isPending ? (
                <div className="space-y-3">
                  <Loader2 className="h-10 w-10 animate-spin text-primary mx-auto" />
                  <p className="text-sm text-muted-foreground">Feeding metrics into AgroGuide ML Engine...</p>
                </div>
              ) : recommendations ? (
                <div className="w-full text-left space-y-4">
                  {modelStatus === "demo" && (
                    <div className="p-3 bg-amber-50 text-amber-900 border border-amber-200 rounded-lg text-xs font-semibold flex items-start gap-2">
                      <span className="shrink-0 mt-0.5 text-base">⚠️</span>
                      <div>
                        <p className="font-bold text-amber-950">Baseline Demo Mode Active</p>
                        <p className="text-[10px] text-amber-800 font-medium mt-0.5">Predictions are rule-based baseline mocks for local evaluation.</p>
                      </div>
                    </div>
                  )}

                  <h3 className="text-sm font-extrabold text-muted-foreground tracking-wider uppercase">
                    Crops Ranked by AI Confidence
                  </h3>
                  <div className="space-y-3">
                    {recommendations.length > 0 ? (
                      recommendations.map((crop: string | { crop: string; probability?: number }, index) => {
                        const cropName = typeof crop === "string" ? crop : crop.crop;
                        const probability = typeof crop === "object" && crop?.probability !== undefined ? crop.probability : null;
                        
                        return (
                          <div
                            key={cropName}
                            className="flex items-center justify-between p-3 rounded-lg border border-primary/10 bg-primary/5 hover:bg-primary/10 transition-colors"
                          >
                            <span className="font-semibold text-foreground capitalize flex items-center gap-2">
                              <span className="text-xs bg-primary/20 text-primary h-5 w-5 rounded-full flex items-center justify-center font-bold">
                                {index + 1}
                              </span>
                              {cropName}
                            </span>
                            <span className="text-xs font-semibold text-emerald-600">
                              {probability !== null ? `Confidence: ${(probability * 100).toFixed(1)}%` : "Optimal Soil Affinity"}
                            </span>
                          </div>
                        );
                      })
                    ) : (
                      <div className="flex items-center gap-2 text-destructive bg-destructive/10 p-3 rounded-lg">
                        <AlertCircle className="h-5 w-5" />
                        <span className="text-xs font-medium">No suitable crop recommendations found for these values.</span>
                      </div>
                    )}
                  </div>
                  
                  {disclaimer && (
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-[10px] text-slate-500 italic mt-4 leading-normal">
                      <strong className="text-slate-700 not-italic block uppercase text-[8px] tracking-wider mb-0.5">Disclaimer:</strong>
                      {disclaimer}
                    </div>
                  )}

                  {limitations && (
                    <div className="text-[10px] text-slate-400 pl-1">
                      Limitations: {limitations}
                    </div>
                  )}
                  
                  <div className="pt-2 text-xs text-muted-foreground italic">
                    Note: Cross-reference this analysis with regional weather trends before purchasing seed stocks.
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <Sprout className="h-12 w-12 text-muted/40 mx-auto" />
                  <p className="text-sm text-muted-foreground max-w-xs mx-auto">
                    Fill out the soil metrics form on the left and submit to view your recommendations.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
