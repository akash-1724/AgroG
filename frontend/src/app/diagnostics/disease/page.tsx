"use client";

import * as React from "react";
import { useMutation } from "@tanstack/react-query";
import { Upload, FileImage, ShieldAlert, CheckCircle, Loader2, Sparkles, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";

interface DiseaseDetectionResult {
  id: string;
  image_url: string;
  predicted_disease: string;
  confidence: number;
  remedy: string;
  created_at: string;
  model_status?: string;
  disclaimer?: string;
  limitations?: string;
}

export default function DiseaseDiagnosisPage() {
  const { toast } = useToast();
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = React.useState<string | null>(null);
  const [diagnosis, setDiagnosis] = React.useState<DiseaseDetectionResult | null>(null);
  const [isDragActive, setIsDragActive] = React.useState(false);

  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const diagnoseMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const response = await api.post("/recommendations/disease/detect", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    },
    onSuccess: (data: DiseaseDetectionResult) => {
      setDiagnosis(data);
      toast({
        title: "Scan Completed",
        description: "Plant disease classification and remedy details fetched.",
        variant: "default",
      });
    },
    onError: (err: unknown) => {
      const errMsg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Plant disease scan failed.";
      toast({
        title: "Scan Failed",
        description: errMsg,
        variant: "destructive",
      });
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith("image/")) {
        toast({
          title: "Unsupported File Type",
          description: "Please select a JPEG or PNG image of a plant leaf.",
          variant: "destructive",
        });
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        toast({
          title: "File Too Large",
          description: "Please select an image smaller than 5MB.",
          variant: "destructive",
        });
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setDiagnosis(null);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = () => {
    setIsDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      if (!file.type.startsWith("image/")) {
        toast({
          title: "Unsupported File Type",
          description: "Please drop a JPEG or PNG image.",
          variant: "destructive",
        });
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        toast({
          title: "File Too Large",
          description: "Please drop an image smaller than 5MB.",
          variant: "destructive",
        });
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setDiagnosis(null);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setDiagnosis(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleScan = () => {
    if (selectedFile) {
      diagnoseMutation.mutate(selectedFile);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-primary flex items-center gap-2">
          <Sparkles className="h-8 w-8 text-primary" /> Leaf Disease Diagnosis
        </h1>
        <p className="text-muted-foreground mt-1">
          Upload an image of a plant leaf to detect disease pathogens and get immediate chemical/organic remedies.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Dropzone/Upload Column */}
        <Card className="border-secondary/20 shadow-md">
          <CardHeader>
            <CardTitle className="text-lg font-bold">Image Upload</CardTitle>
            <CardDescription>Select or drop an image of the affected plant leaf.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/jpeg,image/png,image/jpg"
              className="hidden"
            />

            {!previewUrl ? (
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl h-64 flex flex-col items-center justify-center cursor-pointer transition-colors p-6 text-center ${
                  isDragActive
                    ? "border-primary bg-primary/5"
                    : "border-muted-foreground/20 hover:border-primary/50 hover:bg-secondary/15"
                }`}
              >
                <Upload className="h-10 w-10 text-muted-foreground mb-3" />
                <p className="text-sm font-semibold text-foreground">Drag and drop leaf image here</p>
                <p className="text-xs text-muted-foreground mt-1">or click to browse local files</p>
                <p className="text-[10px] text-muted-foreground/80 mt-4">Supports JPEG, PNG up to 5MB</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative border border-secondary/20 rounded-xl h-64 overflow-hidden bg-secondary/10 flex items-center justify-center">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={previewUrl} alt="Leaf Preview" className="h-full w-full object-contain" />
                  <Button
                    onClick={handleClear}
                    variant="destructive"
                    size="icon"
                    className="absolute top-3 right-3 rounded-full shadow-md"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>

                <div className="flex gap-3">
                  <Button
                    onClick={handleScan}
                    disabled={diagnoseMutation.isPending}
                    className="flex-1 font-bold flex items-center justify-center gap-2 py-5"
                  >
                    {diagnoseMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" /> Diagnosing Leaf...
                      </>
                    ) : (
                      <>
                        <FileImage className="h-4 w-4" /> Run AI Diagnostic
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Diagnostic Results Column */}
        <div className="flex flex-col justify-start">
          <Card className="h-full border-secondary/20 shadow-md flex flex-col">
            <CardHeader className="bg-primary/5 rounded-t-xl border-b border-primary/10">
              <CardTitle className="text-lg font-bold text-primary flex items-center gap-2">
                🛡️ AI Diagnostic Report
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-grow flex flex-col items-center justify-center p-6 text-center">
              {diagnoseMutation.isPending ? (
                <div className="space-y-3">
                  <Loader2 className="h-10 w-10 animate-spin text-primary mx-auto" />
                  <p className="text-sm text-muted-foreground">Running computer vision analytics...</p>
                </div>
              ) : diagnosis ? (
                <div className="w-full text-left space-y-5">
                  {diagnosis.model_status === "demo" && (
                    <div className="p-3 bg-amber-50 text-amber-900 border border-amber-200 rounded-lg text-xs font-semibold flex items-start gap-2">
                      <span className="shrink-0 mt-0.5 text-base">⚠️</span>
                      <div>
                        <p className="font-bold text-amber-950">Baseline Demo Mode Active</p>
                        <p className="text-[10px] text-amber-800 font-medium mt-0.5">Classification generated using a heuristic lookup. Real trained models are disabled.</p>
                      </div>
                    </div>
                  )}

                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-xs font-extrabold text-muted-foreground tracking-wider uppercase mb-1">
                        Detected Condition
                      </h3>
                      <p className="text-xl font-bold text-foreground">
                        {diagnosis.predicted_disease}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-extrabold text-muted-foreground tracking-wider uppercase block mb-1">
                        Confidence
                      </span>
                      <span className={`text-lg font-extrabold px-2.5 py-1 rounded-full ${
                        diagnosis.confidence > 0.8
                          ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-400"
                          : "bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-400"
                      }`}>
                        {(diagnosis.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div className="h-px bg-muted" />

                  <div className="space-y-3">
                    <div className="flex gap-2.5 items-start">
                      {diagnosis.predicted_disease === "Healthy Leaf" ? (
                        <>
                          <CheckCircle className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
                          <div>
                            <h4 className="text-sm font-bold text-foreground">Plant is Healthy</h4>
                            <p className="text-xs text-muted-foreground mt-0.5">
                              No action is needed. Keep up standard maintenance.
                            </p>
                          </div>
                        </>
                      ) : (
                        <>
                          <ShieldAlert className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
                          <div>
                            <h4 className="text-sm font-bold text-foreground">Recommended Remedy</h4>
                            <p className="text-xs text-foreground bg-secondary/35 border border-secondary/40 rounded-lg p-3 mt-1.5 leading-relaxed">
                              {diagnosis.remedy}
                            </p>
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  {diagnosis.disclaimer && (
                    <div className="p-3 bg-red-50/50 border border-red-200/50 rounded-lg text-[10px] text-red-800 font-medium">
                      <strong className="text-red-950 uppercase text-[8px] tracking-wider block mb-0.5">⚠️ Diagnostic Limitation:</strong>
                      {diagnosis.disclaimer}
                    </div>
                  )}

                  {diagnosis.limitations && (
                    <div className="text-[10px] text-slate-400 pl-1">
                      Limitations: {diagnosis.limitations}
                    </div>
                  )}

                  <div className="text-[10px] text-muted-foreground italic pt-4 border-t border-muted">
                    Disclaimer: Diagnostic results are generated by an AI model and should be validated with agricultural extension experts.
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <FileImage className="h-12 w-12 text-muted/40 mx-auto" />
                  <p className="text-sm text-muted-foreground max-w-xs mx-auto">
                    Select or drag-and-drop a leaf image and click &quot;Run AI Diagnostic&quot; to view findings.
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
