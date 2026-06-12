"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { BookOpen, Calendar, ArrowLeft, Globe, Tag, Sprout } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";

interface Article {
  id: string;
  title: string;
  slug: string;
  summary: string;
  content: string;
  category: string;
  tags: string[];
  crop_tags: string[];
  media_url?: string;
  language: string;
  created_at: string;
}

export default function ArticleDetailPage() {
  const { slug } = useParams();

  // Fetch article from backend API by ID or slug
  const { data: article, isLoading, error } = useQuery<Article>({
    queryKey: ["article", slug],
    queryFn: async () => {
      const response = await api.get(`/educational/${slug}`);
      return response.data;
    },
    enabled: !!slug,
  });

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 animate-pulse space-y-6">
        <div className="h-6 w-24 bg-muted rounded" />
        <div className="h-10 w-3/4 bg-muted rounded" />
        <div className="h-5 w-1/2 bg-muted rounded" />
        <div className="h-64 bg-muted rounded-xl" />
        <div className="space-y-3">
          <div className="h-4 w-full bg-muted rounded" />
          <div className="h-4 w-full bg-muted rounded" />
          <div className="h-4 w-5/6 bg-muted rounded" />
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h2 className="text-2xl font-bold text-destructive">Guide Not Found</h2>
        <p className="text-muted-foreground mt-2">The article you are looking for does not exist or has been removed.</p>
        <Link href="/resources" className="inline-block mt-6">
          <Button>Back to Resources</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      {/* Back button */}
      <Link href="/resources" className="inline-flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-primary mb-6 transition-colors">
        <ArrowLeft className="h-4 w-4" /> Back to Educational Catalog
      </Link>

      <article className="space-y-6">
        {/* Title Header */}
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <span className="bg-primary/10 text-primary text-xs font-bold px-3 py-0.5 rounded-full capitalize">
              {article.category}
            </span>
            <span className="flex items-center gap-1 text-xs text-muted-foreground font-semibold">
              <Globe className="h-3.5 w-3.5" /> {article.language.toUpperCase()}
            </span>
            <span className="flex items-center gap-1 text-xs text-muted-foreground font-semibold">
              <Calendar className="h-3.5 w-3.5" /> {new Date(article.created_at).toLocaleDateString()}
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-foreground tracking-tight leading-tight">
            {article.title}
          </h1>
          <p className="text-lg text-muted-foreground leading-relaxed italic border-l-4 border-primary/30 pl-4">
            {article.summary}
          </p>
        </div>

        {/* Media Banner */}
        {article.media_url && (
          <div className="w-full h-80 sm:h-96 rounded-2xl overflow-hidden border border-secondary/20 bg-secondary/15 relative">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={article.media_url} alt={article.title} className="w-full h-full object-cover" />
          </div>
        )}

        {/* Content body */}
        <Card className="border-secondary/20 shadow-md">
          <CardContent className="pt-6 sm:p-8 prose dark:prose-invert max-w-none">
            {/* Split on double newlines to render paragraphs */}
            {article.content.split("\n\n").map((para, idx) => (
              <p key={idx} className="text-foreground leading-relaxed mb-4 text-sm whitespace-pre-line">
                {para}
              </p>
            ))}
          </CardContent>
        </Card>

        {/* Footer Meta: Tags */}
        <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center pt-4 border-t border-muted">
          {article.crop_tags && article.crop_tags.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <Sprout className="h-4 w-4 text-emerald-600 shrink-0" />
              <span className="text-xs font-bold text-muted-foreground uppercase mr-1">Target Crops:</span>
              {article.crop_tags.map((crop) => (
                <span key={crop} className="bg-emerald-50 text-emerald-700 text-xs font-semibold px-2.5 py-0.5 rounded border border-emerald-100">
                  {crop}
                </span>
              ))}
            </div>
          )}
          {article.tags && article.tags.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <Tag className="h-4 w-4 text-primary shrink-0" />
              <span className="text-xs font-bold text-muted-foreground uppercase mr-1">Tags:</span>
              {article.tags.map((tag) => (
                <span key={tag} className="bg-secondary/30 text-secondary-foreground text-xs font-semibold px-2.5 py-0.5 rounded border border-secondary/40">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </article>
    </div>
  );
}
