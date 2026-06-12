"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { BookOpen, Plus, Pencil, Trash2, ArrowLeft, Loader2, FileText, CheckCircle2 } from "lucide-react";
import Link from "next/link";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface Article {
  id: string;
  title: string;
  slug: string;
  summary: string;
  category: string;
  tags: string[];
  language: string;
  status: string;
  created_at: string;
}

export default function AdminResourcesPage() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch all articles (including drafts)
  const { data: articles = [], isLoading } = useQuery<Article[]>({
    queryKey: ["admin-articles"],
    queryFn: async () => {
      const response = await api.get("/educational");
      return response.data;
    },
  });

  // Delete article mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/educational/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-articles"] });
      queryClient.invalidateQueries({ queryKey: ["articles"] });
      toast({
        title: "Resource Deleted",
        description: "Successfully removed educational resource.",
        variant: "default",
      });
    },
    onError: (err: any) => {
      const errMsg = err.response?.data?.detail || "Failed to delete article.";
      toast({
        title: "Deletion Failed",
        description: errMsg,
        variant: "destructive",
      });
    },
  });

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this educational resource?")) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back to Catalog */}
      <Link href="/resources" className="inline-flex items-center gap-2 text-sm font-semibold text-muted-foreground hover:text-primary mb-6 transition-colors">
        <ArrowLeft className="h-4 w-4" /> Back to Catalog
      </Link>

      {/* Header section */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-primary flex items-center gap-2">
            <BookOpen className="h-8 w-8 text-primary" /> Admin CMS Console
          </h1>
          <p className="text-muted-foreground mt-1">
            Create, update, and manage draft or published educational assets.
          </p>
        </div>
        <Link href="/admin/resources/new">
          <Button className="font-bold flex items-center gap-2">
            <Plus className="h-4 w-4" /> Add New Resource
          </Button>
        </Link>
      </div>

      {/* Resource Table List */}
      <Card className="border-secondary/20 shadow-md">
        <CardHeader className="bg-primary/5 rounded-t-xl border-b border-primary/10">
          <CardTitle className="text-lg font-bold">Catalog Index</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary mb-2" />
              <p className="text-xs text-muted-foreground">Loading resource catalogue...</p>
            </div>
          ) : articles.length === 0 ? (
            <div className="text-center py-16">
              <BookOpen className="h-12 w-12 text-muted/40 mx-auto mb-3" />
              <p className="font-bold text-foreground">No resources listed</p>
              <p className="text-xs text-muted-foreground mt-1">Click the button above to add your first article.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-muted/50 border-b border-muted text-xs font-bold text-muted-foreground tracking-wider uppercase">
                    <th className="px-6 py-4">Title</th>
                    <th className="px-6 py-4">Category</th>
                    <th className="px-6 py-4">Language</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-muted/30">
                  {articles.map((article) => (
                    <tr key={article.id} className="hover:bg-secondary/5 transition-colors text-sm">
                      <td className="px-6 py-4">
                        <div className="font-semibold text-foreground leading-normal max-w-md truncate">
                          {article.title}
                        </div>
                        <div className="text-[10px] text-muted-foreground mt-0.5">
                          slug: {article.slug}
                        </div>
                      </td>
                      <td className="px-6 py-4 capitalize font-medium text-foreground">{article.category}</td>
                      <td className="px-6 py-4 uppercase font-semibold text-muted-foreground text-xs">{article.language}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                          article.status === "published"
                            ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-400"
                            : "bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-400"
                        }`}>
                          {article.status === "published" ? (
                            <CheckCircle2 className="h-3 w-3" />
                          ) : (
                            <FileText className="h-3 w-3" />
                          )}
                          {article.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="inline-flex gap-2">
                          <Link href={`/admin/resources/${article.id}/edit`}>
                            <Button variant="outline" size="sm" className="h-8 px-2.5 border-secondary/20">
                              <Pencil className="h-3.5 w-3.5" />
                            </Button>
                          </Link>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(article.id)}
                            className="h-8 px-2.5 border-red-200 text-destructive hover:bg-destructive/10"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
