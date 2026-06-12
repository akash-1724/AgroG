"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { BookOpen, Search, Filter, Eye, ArrowRight, BookOpenCheck } from "lucide-react";
import Link from "next/link";

import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from "@/components/ui/card";

interface Article {
  id: string;
  title: string;
  slug: string;
  summary: string;
  category: string;
  tags: string[];
  crop_tags: string[];
  media_url?: string;
  language: string;
  status: string;
  created_at: string;
}

export default function ResourcesPage() {
  const [search, setSearch] = React.useState("");
  const [selectedCategory, setSelectedCategory] = React.useState("All");
  const [selectedLanguage, setSelectedLanguage] = React.useState("en");

  // Fetch articles from backend API
  const { data: articles = [], isLoading, error } = useQuery<Article[]>({
    queryKey: ["articles", selectedCategory, selectedLanguage, search],
    queryFn: async () => {
      const params: any = {};
      if (selectedCategory !== "All") params.category = selectedCategory.toLowerCase();
      if (selectedLanguage) params.language = selectedLanguage;
      if (search) params.search = search;
      
      const response = await api.get("/educational", { params });
      return response.data;
    },
  });

  const categories = ["All", "Crops", "Soil", "Pests", "Marketing"];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-primary flex items-center gap-2">
            <BookOpen className="h-8 w-8 text-primary" /> Educational Resources
          </h1>
          <p className="text-muted-foreground mt-1">
            Access verified guides, crop tutorials, and agricultural best practices.
          </p>
        </div>
        <Link href="/admin/resources">
          <Button variant="outline" className="font-semibold flex items-center gap-2">
            <BookOpenCheck className="h-4 w-4" /> Manage Resources
          </Button>
        </Link>
      </div>

      {/* Filters & Search controls */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="relative flex-grow">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search resources by title, topic, or crop..."
            className="pl-9"
          />
        </div>
        <div className="flex gap-2 shrink-0">
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="border border-input bg-background px-3 py-2 rounded-md text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="en">English</option>
            <option value="es">Español</option>
            <option value="hi">हिन्दी</option>
          </select>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex flex-wrap gap-2 mb-8 border-b border-muted pb-4">
        {categories.map((cat) => (
          <Button
            key={cat}
            variant={selectedCategory === cat ? "default" : "outline"}
            onClick={() => setSelectedCategory(cat)}
            className="rounded-full font-bold px-5 text-xs"
          >
            {cat}
          </Button>
        ))}
      </div>

      {/* Resources grid listing */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((n) => (
            <Card key={n} className="border-secondary/20 shadow-sm animate-pulse h-80" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-12 text-destructive font-semibold">
          Failed to load educational resources. Please try again.
        </div>
      ) : articles.length === 0 ? (
        <Card className="border-dashed border-2 py-16 text-center">
          <BookOpen className="h-12 w-12 text-muted/40 mx-auto mb-3" />
          <h3 className="font-bold text-lg text-foreground">No Resources Found</h3>
          <p className="text-muted-foreground text-sm max-w-sm mx-auto mt-1">
            We couldn't find any articles matching your search or filters.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {articles.map((article) => (
            <Card key={article.id} className="border-secondary/20 shadow-md flex flex-col hover:border-primary/40 transition-colors">
              {article.media_url && (
                <div className="h-40 overflow-hidden bg-secondary/15 relative">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={article.media_url}
                    alt={article.title}
                    className="h-full w-full object-cover"
                  />
                  <span className="absolute top-3 right-3 bg-background/95 backdrop-blur-sm text-primary text-[10px] font-bold px-2 py-0.5 rounded-full border border-primary/10 capitalize">
                    {article.category}
                  </span>
                </div>
              )}
              <CardHeader className={article.media_url ? "pt-4" : "pt-6"}>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] text-muted-foreground font-bold tracking-wider uppercase">
                    Language: {article.language}
                  </span>
                  {!article.media_url && (
                    <span className="bg-primary/10 text-primary text-[10px] font-bold px-2.5 py-0.5 rounded-full capitalize">
                      {article.category}
                    </span>
                  )}
                </div>
                <CardTitle className="text-lg font-bold leading-snug line-clamp-2">
                  {article.title}
                </CardTitle>
                <CardDescription className="line-clamp-3 mt-2 text-xs text-muted-foreground">
                  {article.summary}
                </CardDescription>
              </CardHeader>
              <div className="flex-grow" />
              <CardFooter className="pt-0 border-t border-muted/30 mt-4 flex items-center justify-between">
                <div className="flex flex-wrap gap-1 max-w-[70%]">
                  {article.crop_tags?.slice(0, 2).map((crop) => (
                    <span key={crop} className="bg-emerald-50 text-emerald-700 text-[9px] font-semibold px-2 py-0.5 rounded">
                      {crop}
                    </span>
                  ))}
                </div>
                <Link href={`/resources/${article.slug}`}>
                  <Button variant="link" className="text-primary font-bold text-xs flex items-center gap-1.5 p-0">
                    Read Guide <ArrowRight className="h-3 w-3" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
