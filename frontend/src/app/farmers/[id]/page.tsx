"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, Loader2, MapPin, Star } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

interface PublicListing {
  id: string;
  title: string;
  description: string;
  price_per_unit: number;
  unit: string;
  available_quantity: number;
  image_urls?: string;
  category: string;
}

interface PublicReview {
  id: string;
  rating: number;
  comment: string;
  reviewer_name?: string;
  created_at: string;
}

interface PublicFarmerProfile {
  farmer_id: string;
  full_name: string;
  farm_name?: string;
  address?: string;
  district?: string;
  city?: string;
  state?: string;
  description?: string;
  average_rating?: number;
  review_count: number;
  active_listings: PublicListing[];
  recent_reviews: PublicReview[];
}

export default function FarmerProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = React.use(params);
  const { data: profile, isLoading, error } = useQuery<PublicFarmerProfile>({
    queryKey: ["farmerProfile", id],
    queryFn: async () => (await api.get(`/farmers/${id}/public`)).data,
    enabled: !!id,
  });

  if (isLoading) {
    return <div className="min-h-[50vh] flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-emerald-600" /></div>;
  }

  if (error || !profile) {
    return <div className="max-w-4xl mx-auto px-4 py-12"><Link href="/marketplace"><Button variant="outline"><ArrowLeft className="h-4 w-4 mr-2" /> Back</Button></Link><p className="mt-6 text-red-600 font-semibold">Farmer profile not found.</p></div>;
  }

  const location = [profile.address, profile.district, profile.city, profile.state].filter(Boolean).join(", ");

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <Link href="/marketplace" className="inline-flex items-center text-sm text-slate-500 hover:text-emerald-700"><ArrowLeft className="h-4 w-4 mr-2" /> Back to Marketplace</Link>

      <div className="rounded-3xl bg-gradient-to-br from-emerald-800 to-slate-950 text-white p-8 md:p-10 shadow-lg">
        <div className="max-w-3xl space-y-4">
          <div className="text-sm uppercase tracking-widest text-emerald-200 font-bold">Public Farmer Profile</div>
          <h1 className="text-4xl font-extrabold">{profile.farm_name || `${profile.full_name}'s Farm`}</h1>
          <p className="text-emerald-50 text-lg">Managed by {profile.full_name}</p>
          <div className="flex flex-wrap gap-3 text-sm">
            <span className="inline-flex items-center bg-white/10 px-3 py-1 rounded-full"><Star className="h-4 w-4 mr-1 text-amber-300" /> {profile.average_rating ? `${profile.average_rating}/5` : "Unrated"} · {profile.review_count} reviews</span>
            {location ? <span className="inline-flex items-center bg-white/10 px-3 py-1 rounded-full"><MapPin className="h-4 w-4 mr-1" /> {location}</span> : null}
          </div>
          {profile.description ? <p className="text-emerald-50/90 leading-relaxed">{profile.description}</p> : null}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-6">
        <section className="space-y-4">
          <h2 className="text-2xl font-extrabold text-slate-900">Active Listings</h2>
          {profile.active_listings.length === 0 ? (
            <Card><CardContent className="p-8 text-slate-500">No active listings from this farmer right now.</CardContent></Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {profile.active_listings.map((listing) => (
                <Card key={listing.id} className="overflow-hidden">
                  <div className="h-40 bg-slate-100 flex items-center justify-center text-slate-400">
                    {listing.image_urls ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={listing.image_urls.split(",")[0]} alt={listing.title} className="h-full w-full object-cover" />
                    ) : "No image"}
                  </div>
                  <CardContent className="p-4 space-y-2">
                    <h3 className="font-bold text-slate-900">{listing.title}</h3>
                    <p className="text-sm text-slate-500 line-clamp-2">{listing.description}</p>
                    <div className="flex justify-between items-center text-sm">
                      <span className="font-extrabold text-slate-900">${listing.price_per_unit} / {listing.unit}</span>
                      <Link href={`/marketplace/${listing.id}`}><Button size="sm">View</Button></Link>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </section>

        <section className="space-y-4">
          <h2 className="text-2xl font-extrabold text-slate-900">Recent Reviews</h2>
          {profile.recent_reviews.length === 0 ? (
            <Card><CardContent className="p-8 text-slate-500">No reviews yet.</CardContent></Card>
          ) : profile.recent_reviews.map((review) => (
            <Card key={review.id}>
              <CardHeader className="pb-2"><CardTitle className="text-base flex items-center gap-2"><Star className="h-4 w-4 text-amber-500" /> {review.rating}/5</CardTitle></CardHeader>
              <CardContent className="text-sm text-slate-600 space-y-2">
                <p>{review.comment}</p>
                <p className="text-xs text-slate-400">{review.reviewer_name || "Customer"} · {new Date(review.created_at).toLocaleDateString()}</p>
              </CardContent>
            </Card>
          ))}
        </section>
      </div>
    </div>
  );
}
