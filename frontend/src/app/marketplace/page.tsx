"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

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
}

export default function MarketplacePage() {
  const [search, setSearch] = React.useState("");
  const [debouncedSearch, setDebouncedSearch] = React.useState("");

  // Debounce search input
  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
    }, 500);
    return () => clearTimeout(handler);
  }, [search]);

  // Fetch active marketplace listings
  const { data: listings = [], isLoading, error } = useQuery<CropListing[]>({
    queryKey: ["marketplaceListings", debouncedSearch],
    queryFn: async () => {
      const response = await api.get("/marketplace", {
        params: { search: debouncedSearch || undefined }
      });
      return response.data;
    }
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-primary">AgroGuide Marketplace</h1>
          <p className="text-muted-foreground mt-1">Buy fresh crops directly from local verified farmers</p>
        </div>
        <div className="w-full md:w-80">
          <Input
            placeholder="Search crops, grains, fruits..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Grid Loader / Error Handler */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse h-[320px] bg-muted/20" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-destructive font-medium">Failed to load crop listings. Please check back later.</p>
        </div>
      ) : listings.length === 0 ? (
        <div className="text-center py-12">
          <h3 className="text-lg font-bold">No crops available</h3>
          <p className="text-muted-foreground mt-1">There are no listings matching your search at this moment.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {listings.map((item) => (
            <Card key={item.id} className="flex flex-col h-full hover:shadow-md transition-shadow">
              {/* Product Image Placeholder */}
              <div className="h-44 w-full bg-secondary/30 rounded-t-xl flex items-center justify-center text-secondary-foreground font-bold text-sm">
                {item.image_urls ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={item.image_urls.split(",")[0]}
                    alt={item.title}
                    className="h-full w-full object-cover rounded-t-xl"
                  />
                ) : (
                  <span>🌱 {item.title}</span>
                )}
              </div>
              <CardHeader className="p-4 flex-grow">
                <CardTitle className="text-base font-bold line-clamp-1">{item.title}</CardTitle>
                <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{item.description}</p>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <div className="flex justify-between items-baseline">
                  <span className="text-lg font-extrabold text-primary">
                    ${item.price_per_unit} <span className="text-xs font-normal text-muted-foreground">/ {item.unit}</span>
                  </span>
                  <span className="text-xs text-muted-foreground">
                    Qty: {item.available_quantity} {item.unit}
                  </span>
                </div>
              </CardContent>
              <CardFooter className="p-4 pt-0">
                <Link href={`/marketplace/${item.id}`} className="w-full">
                  <Button variant="outline" className="w-full">View Details</Button>
                </Link>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
