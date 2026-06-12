"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { BookOpen, ArrowLeft, Loader2, Save } from "lucide-react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";

import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";

const resourceFormSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters").max(255),
  slug: z.string().min(3, "Slug must be at least 3 characters").max(255).regex(/^[a-z0-9-]+$/, "Slug must be lowercase alphanumeric and hyphens only"),
  summary: z.string().max(1000, "Summary must be under 1000 characters"),
  content: z.string().min(20, "Content must be at least 20 characters"),
  category: z.string().min(2).max(100),
  tags_raw: z.string().optional(),
  crop_tags_raw: z.string().optional(),
  media_url: z.string().url("Must be a valid URL").or(z.literal("")).optional(),
  language: z.string().default("en"),
  status: z.string().default("draft"),
});

type ResourceFormValues = z.infer<typeof resourceFormSchema>;

export default function EditResourcePage() {
  const { id } = useParams();
  const { toast } = useToast();
  const router = useRouter();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<ResourceFormValues>({
    resolver: zodResolver(resourceFormSchema as unknown as Parameters<typeof zodResolver>[0]),
    defaultValues: {
      title: "",
      slug: "",
      summary: "",
      content: "",
      category: "crops",
      tags_raw: "",
      crop_tags_raw: "",
      media_url: "",
      language: "en",
      status: "draft",
    },
  });

  // Fetch current resource details
  const { data: resource, isLoading } = useQuery({
    queryKey: ["admin-article", id],
    queryFn: async () => {
      const response = await api.get(`/educational/${id}`);
      return response.data;
    },
    enabled: !!id,
  });

  // Load database values into the react hook form once fetched
  React.useEffect(() => {
    if (resource) {
      reset({
        title: resource.title || "",
        slug: resource.slug || "",
        summary: resource.summary || "",
        content: resource.content || "",
        category: resource.category || "crops",
        tags_raw: resource.tags ? resource.tags.join(", ") : "",
        crop_tags_raw: resource.crop_tags ? resource.crop_tags.join(", ") : "",
        media_url: resource.media_url || "",
        language: resource.language || "en",
        status: resource.status || "draft",
      });
    }
  }, [resource, reset]);

  const updateMutation = useMutation({
    mutationFn: async (payload: { title: string; slug: string; summary: string; content: string; category: string; tags: string[]; crop_tags: string[]; media_url: string | null; language: string; status: string; }) => {
      const response = await api.patch(`/educational/${id}`, payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-articles"] });
      queryClient.invalidateQueries({ queryKey: ["admin-article", id] });
      queryClient.invalidateQueries({ queryKey: ["articles"] });
      queryClient.invalidateQueries({ queryKey: ["article", resource?.slug] });
      toast({
        title: "Resource Updated",
        description: "Successfully saved educational resource updates.",
      });
      router.push("/admin/resources");
    },
    onError: (err: unknown) => {
      const errMsg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Failed to update resource.";
      toast({
        title: "Update Failed",
        description: errMsg,
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data: ResourceFormValues) => {
    // Parse tags arrays
    const tags = data.tags_raw
      ? data.tags_raw.split(",").map((t) => t.trim()).filter((t) => t.length > 0)
      : [];
    const crop_tags = data.crop_tags_raw
      ? data.crop_tags_raw.split(",").map((t) => t.trim()).filter((t) => t.length > 0)
      : [];

    const payload = {
      title: data.title,
      slug: data.slug,
      summary: data.summary,
      content: data.content,
      category: data.category,
      tags,
      crop_tags,
      media_url: data.media_url || null,
      language: data.language,
      status: data.status,
    };

    updateMutation.mutate(payload);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary mb-2" />
        <p className="text-xs text-muted-foreground">Loading resource details...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      {/* Back link */}
      <Link href="/admin/resources" className="inline-flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-primary mb-6 transition-colors">
        <ArrowLeft className="h-4 w-4" /> Cancel and Go Back
      </Link>

      <Card className="border-secondary/20 shadow-md">
        <CardHeader className="bg-primary/5 rounded-t-xl border-b border-primary/10">
          <CardTitle className="text-xl font-bold text-primary flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" /> Edit Educational Resource
          </CardTitle>
          <CardDescription>Update title, category, tags, or draft/published visibility.</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Title */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Article Title</label>
              <Input {...register("title")} placeholder="e.g. Managing Soil Nitrogen Levels" />
              {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
            </div>

            {/* Slug */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Unique Slug</label>
              <Input {...register("slug")} placeholder="managing-soil-nitrogen-levels" />
              {errors.slug && <p className="text-xs text-destructive">{errors.slug.message}</p>}
            </div>

            {/* Summary */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Short Summary</label>
              <textarea
                {...register("summary")}
                rows={2}
                placeholder="Provide a 1-2 sentence overview of the resource..."
                className="w-full min-h-[60px] border border-input bg-background px-3 py-2 rounded-md text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
              {errors.summary && <p className="text-xs text-destructive">{errors.summary.message}</p>}
            </div>

            {/* Content */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Markdown Content</label>
              <textarea
                {...register("content")}
                rows={8}
                placeholder="Markdown text goes here..."
                className="w-full min-h-[200px] border border-input bg-background px-3 py-2 rounded-md text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              />
              {errors.content && <p className="text-xs text-destructive">{errors.content.message}</p>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Category */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Category</label>
                <select
                  {...register("category")}
                  className="w-full border border-input bg-background px-3 py-2 rounded-md text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="crops">Crops</option>
                  <option value="soil">Soil</option>
                  <option value="pests">Pests</option>
                  <option value="marketing">Marketing</option>
                </select>
              </div>

              {/* Language */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Language</label>
                <select
                  {...register("language")}
                  className="w-full border border-input bg-background px-3 py-2 rounded-md text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="hi">हिन्दी</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Status */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Status</label>
                <select
                  {...register("status")}
                  className="w-full border border-input bg-background px-3 py-2 rounded-md text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                </select>
              </div>

              {/* Media URL */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Media Cover Image URL (Optional)</label>
                <Input {...register("media_url")} placeholder="https://example.com/banner.jpg" />
                {errors.media_url && <p className="text-xs text-destructive">{errors.media_url.message}</p>}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Tags raw */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Tags (comma-separated)</label>
                <Input {...register("tags_raw")} placeholder="organic, nitrogen, fertilizer" />
              </div>

              {/* Crop tags raw */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Crop Tags (comma-separated)</label>
                <Input {...register("crop_tags_raw")} placeholder="rice, wheat, corn" />
              </div>
            </div>

            {/* Actions */}
            <div className="pt-4 border-t border-muted/55 flex justify-end">
              <Button
                type="submit"
                disabled={updateMutation.isPending}
                className="font-bold flex items-center gap-2 px-6 py-5"
              >
                {updateMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" /> Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" /> Update Article
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
