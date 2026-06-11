"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useMutation } from "@tanstack/react-query";
import { Droplet, AlertCircle, ArrowRight, Loader2, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { useToast } from "@/components/ui/toast";
import { api } from "@/lib/api";

const fertilizerFormSchema = z.object({
  nitrogen: z.coerce.number().min(0, "Must be >= 0").max(200, "Must be <= 200"),
  phosphorus: z.coerce.number().min(0, "Must be >= 0").max(200, "Must be <= 200"),
  potassium: z.coerce.number().min(0, "Must be >= 0").max(200, "Must be <= 200"),
  crop_type: z.string().min(1, "Target crop is required"),
});

type FertilizerFormValues = z.infer<typeof fertilizerFormSchema>;

export default function FertilizerRecommendationPage() {
  const { toast } = useToast();
  const [recommendation, setRecommendation] = React.useState<{
    recommended_fertilizer: string;
    guideline: string;
  } | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
    reset,
  } = useForm<FertilizerFormValues>({
    resolver: zodResolver(fertilizerFormSchema as any),
    defaultValues: {
      nitrogen: 50,
      phosphorus: 50,
      potassium: 50,
      crop_type: "rice",
    },
  });

  const recommendationMutation = useMutation({
    mutationFn: async (values: FertilizerFormValues) => {
      const response = await api.post("/recommendations/fertilizer", values);
      return response.data;
    },
    onSuccess: (data) => {
      setRecommendation({
        recommended_fertilizer: data.recommended_fertilizer,
        guideline: data.guideline,
      });
      toast({
        title: "Analysis Complete",
        description: "Fertilizer prescription generated successfully.",
        variant: "default",
      });
    },
    onError: (err: any) => {
      const errMsg = err.response?.data?.detail || "ML model recommendation failed.";
      toast({
        title: "Recommendation Failed",
        description: errMsg,
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data: FertilizerFormValues) => {
    recommendationMutation.mutate(data);
  };

  const handleReset = () => {
    reset();
    setRecommendation(null);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-primary flex items-center gap-2">
          <Droplet className="h-8 w-8 text-primary" /> Fertilizer Recommendation System
        </h1>
        <p className="text-muted-foreground mt-1">
          Provide your soil's NPK values along with the target crop to generate a customized fertilizer formula.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Form Column */}
        <Card className="border-secondary/20 shadow-md">
          <CardHeader>
            <CardTitle className="text-lg font-bold">Soil Composition & Crop</CardTitle>
            <CardDescription>Specify the current soil chemical stats and what you want to grow.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Nitrogen Ratio (N)</label>
                <Input {...register("nitrogen")} type="number" step="any" placeholder="N ratio" />
                {errors.nitrogen && <p className="text-xs text-destructive">{errors.nitrogen.message}</p>}
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Phosphorus Ratio (P)</label>
                <Input {...register("phosphorus")} type="number" step="any" placeholder="P ratio" />
                {errors.phosphorus && <p className="text-xs text-destructive">{errors.phosphorus.message}</p>}
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Potassium Ratio (K)</label>
                <Input {...register("potassium")} type="number" step="any" placeholder="K ratio" />
                {errors.potassium && <p className="text-xs text-destructive">{errors.potassium.message}</p>}
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Target Crop</label>
                <Select
                  defaultValue="rice"
                  onValueChange={(val) => setValue("crop_type", val)}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select Crop" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="rice">Rice</SelectItem>
                    <SelectItem value="maize">Maize</SelectItem>
                    <SelectItem value="chickpea">Chickpea</SelectItem>
                    <SelectItem value="kidneybeans">Kidney Beans</SelectItem>
                    <SelectItem value="pigeonpeas">Pigeon Peas</SelectItem>
                    <SelectItem value="mothbeans">Moth Beans</SelectItem>
                    <SelectItem value="mungbean">Mung Bean</SelectItem>
                    <SelectItem value="blackgram">Blackgram</SelectItem>
                    <SelectItem value="lentil">Lentil</SelectItem>
                    <SelectItem value="pomegranate">Pomegranate</SelectItem>
                    <SelectItem value="banana">Banana</SelectItem>
                    <SelectItem value="mango">Mango</SelectItem>
                    <SelectItem value="grapes">Grapes</SelectItem>
                    <SelectItem value="watermelon">Watermelon</SelectItem>
                    <SelectItem value="muskmelon">Muskmelon</SelectItem>
                    <SelectItem value="apple">Apple</SelectItem>
                    <SelectItem value="orange">Orange</SelectItem>
                    <SelectItem value="papaya">Papaya</SelectItem>
                    <SelectItem value="coconut">Coconut</SelectItem>
                    <SelectItem value="cotton">Cotton</SelectItem>
                    <SelectItem value="jute">Jute</SelectItem>
                    <SelectItem value="coffee">Coffee</SelectItem>
                  </SelectContent>
                </Select>
                {errors.crop_type && <p className="text-xs text-destructive">{errors.crop_type.message}</p>}
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  disabled={recommendationMutation.isPending}
                  className="flex-1 font-bold flex items-center justify-center gap-2"
                >
                  {recommendationMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" /> Calculating...
                    </>
                  ) : (
                    <>
                      Calculate Formulation <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </Button>
                {recommendation && (
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
                🧪 Formulation Diagnostic
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-grow flex flex-col items-center justify-center p-6 text-center">
              {recommendationMutation.isPending ? (
                <div className="space-y-3">
                  <Loader2 className="h-10 w-10 animate-spin text-primary mx-auto" />
                  <p className="text-sm text-muted-foreground">Evaluating soil chemical stats...</p>
                </div>
              ) : recommendation ? (
                <div className="w-full text-left space-y-5">
                  <div>
                    <h3 className="text-xs font-extrabold text-muted-foreground tracking-wider uppercase mb-1">
                      Recommended Fertilizer Formula
                    </h3>
                    <div className="p-4 rounded-xl border border-primary/20 bg-primary/10 text-primary flex items-center justify-center">
                      <span className="text-2xl font-black tracking-wider">
                        {recommendation.recommended_fertilizer}
                      </span>
                    </div>
                  </div>

                  <div className="h-px bg-muted" />

                  <div className="space-y-2">
                    <h3 className="text-xs font-extrabold text-muted-foreground tracking-wider uppercase">
                      Application Guidelines
                    </h3>
                    <p className="text-sm text-foreground leading-relaxed p-3 bg-secondary/20 border border-secondary/30 rounded-lg">
                      {recommendation.guideline}
                    </p>
                  </div>

                  <div className="text-xs text-muted-foreground italic">
                    Tip: For best absorption, apply before light watering or right before expected mild rainfall.
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <Droplet className="h-12 w-12 text-muted/40 mx-auto" />
                  <p className="text-sm text-muted-foreground max-w-xs mx-auto">
                    Fill out the soil NPK composition stats on the left to see recommended fertilizer treatments.
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
