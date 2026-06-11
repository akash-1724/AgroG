"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, Edit, Trash2, Tag, ShoppingBag, Eye, EyeOff } from "lucide-react";

import ProtectedRoute from "@/components/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";
import { useAuth } from "@/components/shared/auth-context";
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
  status: "active" | "inactive" | "sold_out";
}

export default function FarmerListingsPage() {
  return (
    <ProtectedRoute allowedRoles={["farmer"]}>
      <FarmerListingsContent />
    </ProtectedRoute>
  );
}

function FarmerListingsContent() {
  const { user } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch all listings (we use status: "all" to fetch active, inactive, sold_out)
  const { data: allListings = [], isLoading, error } = useQuery<CropListing[]>({
    queryKey: ["farmerListings"],
    queryFn: async () => {
      const response = await api.get("/marketplace", {
        params: { status: "all", limit: 100 }
      });
      return response.data;
    }
  });

  // Filter listings belonging to current logged-in farmer
  const farmerListings = allListings.filter(item => item.farmer_id === user?.id);

  // Delete listing mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/marketplace/listings/${id}`);
    },
    onSuccess: () => {
      toast("Listing deleted successfully.", "success");
      queryClient.invalidateQueries({ queryKey: ["farmerListings"] });
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || "Failed to delete listing.";
      toast(msg, "error");
    }
  });

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this crop listing?")) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Farmer Catalog</h1>
          <p className="text-slate-500 text-sm mt-1">Manage, update, and publish your fresh crop offerings</p>
        </div>
        <Link href="/farmer/listings/new">
          <Button className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold flex items-center gap-2">
            <Plus className="h-5 w-5" /> Add New Listing
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2].map(i => (
            <Card key={i} className="animate-pulse h-[200px] bg-slate-200/50 rounded-xl" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl">
          <p className="text-red-500 font-medium">Failed to load listings. Check your connection.</p>
        </div>
      ) : farmerListings.length === 0 ? (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl max-w-2xl mx-auto">
          <ShoppingBag className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-800">No Listings Yet</h3>
          <p className="text-slate-500 text-sm mt-1">Start selling your harvest by adding your first crop listing.</p>
          <Link href="/farmer/listings/new" className="mt-4 inline-block">
            <Button variant="outline">Create a Listing</Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {farmerListings.map((listing) => (
            <Card key={listing.id} className="flex flex-col sm:flex-row border border-slate-200/80 bg-white shadow-sm rounded-xl overflow-hidden hover:shadow-md transition">
              {/* Image box */}
              <div className="w-full sm:w-44 h-40 bg-slate-100 flex items-center justify-center text-slate-400 font-bold relative shrink-0">
                {listing.image_urls ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={listing.image_urls.split(",")[0]}
                    alt={listing.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-3xl">🌾</span>
                )}
                <span className={`absolute top-2 left-2 text-[10px] uppercase font-extrabold px-2 py-0.5 rounded shadow ${
                  listing.status === "active"
                    ? "bg-emerald-500 text-slate-950"
                    : listing.status === "sold_out"
                    ? "bg-amber-500 text-slate-950"
                    : "bg-slate-500 text-white"
                }`}>
                  {listing.status}
                </span>
              </div>

              {/* Details card content */}
              <div className="p-5 flex-grow flex flex-col justify-between">
                <div className="space-y-1">
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
                      {listing.category}
                    </span>
                    <span className="text-xs text-slate-500 font-semibold">
                      Qty: {listing.available_quantity} {listing.unit}
                    </span>
                  </div>
                  <h3 className="font-bold text-slate-900 text-lg">{listing.title}</h3>
                  <p className="text-slate-500 text-xs line-clamp-1">{listing.description}</p>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-slate-100 mt-4">
                  <span className="text-base font-extrabold text-slate-900">
                    ${listing.price_per_unit} <span className="text-xs font-normal text-slate-500">/ {listing.unit}</span>
                  </span>
                  
                  <div className="flex items-center gap-2">
                    <Link href={`/farmer/listings/${listing.id}/edit`}>
                      <Button size="icon" variant="outline" className="h-8 w-8 hover:text-emerald-600">
                        <Edit className="h-4 w-4" />
                      </Button>
                    </Link>
                    <Button
                      size="icon"
                      variant="outline"
                      onClick={() => handleDelete(listing.id)}
                      className="h-8 w-8 text-red-500 hover:bg-red-50 hover:border-red-200"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
