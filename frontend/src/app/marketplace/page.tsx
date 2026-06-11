"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Search, SlidersHorizontal, ChevronLeft, ChevronRight, Tag } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { api } from "@/lib/api";

interface CropListing {
  id: string;
  farmer_id: string;
  title: string;
  description: string;
  price_per_unit: number;
  unit: string;
  available_quantity: number;
  image_urls?: string;
  category: string;
  status: string;
}

const CATEGORIES = ["All", "Vegetables", "Fruits", "Grains", "Pulses", "Spices", "Other"];
const LIMIT = 8;

export default function MarketplacePage() {
  const [search, setSearch] = React.useState("");
  const [debouncedSearch, setDebouncedSearch] = React.useState("");
  const [selectedCategory, setSelectedCategory] = React.useState("All");
  const [sortOrder, setSortOrder] = React.useState("latest");
  const [page, setPage] = React.useState(1);

  // Debounce search
  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1); // Reset page on search
    }, 400);
    return () => clearTimeout(handler);
  }, [search]);

  const offset = (page - 1) * LIMIT;

  // Fetch active marketplace listings
  const { data: listings = [], isLoading, error } = useQuery<CropListing[]>({
    queryKey: ["marketplaceListings", debouncedSearch, selectedCategory, sortOrder, page],
    queryFn: async () => {
      const response = await api.get("/marketplace", {
        params: {
          search: debouncedSearch || undefined,
          category: selectedCategory === "All" ? undefined : selectedCategory,
          sort: sortOrder,
          status: "active",
          limit: LIMIT,
          offset: offset,
        }
      });
      return response.data;
    }
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-emerald-800 to-teal-900 rounded-2xl p-6 md:p-10 text-white shadow-md relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_20%,rgba(16,185,129,0.15),transparent)]" />
        <div className="max-w-xl space-y-2 relative z-10">
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">AgroGuide Marketplace</h1>
          <p className="text-emerald-100/90 text-sm md:text-base">
            Sourced directly from certified farmers. Freshness and pricing transparency guaranteed.
          </p>
        </div>
      </div>

      {/* Search and Filters Controls */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          {/* Search bar */}
          <div className="relative w-full md:max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              className="pl-9 bg-slate-50 border-slate-200 focus:bg-white transition"
              placeholder="Search crops, grains, fruits..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {/* Sorting / Limit Selector */}
          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <div className="flex items-center gap-2 text-sm text-slate-500 font-medium whitespace-nowrap">
              <SlidersHorizontal className="h-4 w-4" /> Sort by
            </div>
            <select
              value={sortOrder}
              onChange={(e) => {
                setSortOrder(e.target.value);
                setPage(1);
              }}
              className="bg-slate-50 border border-slate-200 rounded-lg text-sm px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500 transition"
            >
              <option value="latest">Latest Arrivals</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
            </select>
          </div>
        </div>

        {/* Categories Pills */}
        <div className="border-t border-slate-100 pt-4">
          <div className="flex flex-wrap gap-2">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => {
                  setSelectedCategory(cat);
                  setPage(1);
                }}
                className={`px-4 py-1.5 rounded-full text-xs font-semibold border transition ${
                  selectedCategory === cat
                    ? "bg-emerald-500 border-emerald-500 text-slate-950 font-bold"
                    : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Grid List */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <Card key={i} className="animate-pulse h-[340px] bg-slate-200/50 rounded-xl" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl">
          <p className="text-red-500 font-medium">Failed to load marketplace listings. Ensure the backend is running.</p>
        </div>
      ) : listings.length === 0 ? (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl">
          <Tag className="h-12 w-12 mx-auto text-slate-300 mb-3" />
          <h3 className="text-lg font-bold text-slate-800">No active listings</h3>
          <p className="text-slate-500 text-sm mt-1">There are no listings matching your search at this moment.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {listings.map((item) => (
              <Card key={item.id} className="flex flex-col h-full hover:shadow-lg hover:border-emerald-500/30 transition-all duration-300 bg-white border border-slate-200/80 rounded-xl overflow-hidden group">
                {/* Product Image Placeholder */}
                <div className="h-44 w-full bg-slate-100 flex items-center justify-center text-slate-400 font-bold text-sm relative overflow-hidden">
                  {item.image_urls ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={item.image_urls.split(",")[0]}
                      alt={item.title}
                      className="h-full w-full object-cover group-hover:scale-105 transition duration-500"
                    />
                  ) : (
                    <span className="text-4xl">🌱</span>
                  )}
                  <span className="absolute top-2.5 right-2.5 bg-slate-900/80 backdrop-blur-sm text-white text-[10px] uppercase font-bold tracking-wide px-2 py-0.5 rounded">
                    {item.category}
                  </span>
                </div>
                <CardHeader className="p-4 flex-grow space-y-1">
                  <CardTitle className="text-base font-bold text-slate-900 line-clamp-1 group-hover:text-emerald-600 transition">
                    {item.title}
                  </CardTitle>
                  <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                    {item.description}
                  </p>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  <div className="flex justify-between items-baseline">
                    <span className="text-lg font-extrabold text-slate-950">
                      ${item.price_per_unit}{" "}
                      <span className="text-xs font-normal text-slate-500">/ {item.unit}</span>
                    </span>
                    <span className="text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full font-medium">
                      Qty: {item.available_quantity}
                    </span>
                  </div>
                </CardContent>
                <CardFooter className="p-4 pt-0">
                  <Link href={`/marketplace/${item.id}`} className="w-full">
                    <Button className="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold transition">
                      View Details
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>

          {/* Pagination Controls */}
          <div className="flex items-center justify-center gap-4 pt-6 border-t border-slate-200">
            <Button
              variant="outline"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              className="flex items-center gap-1.5"
            >
              <ChevronLeft className="h-4 w-4" /> Previous
            </Button>
            <span className="text-sm font-semibold text-slate-700">
              Page {page}
            </span>
            <Button
              variant="outline"
              disabled={listings.length < LIMIT}
              onClick={() => setPage(page + 1)}
              className="flex items-center gap-1.5"
            >
              Next <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
