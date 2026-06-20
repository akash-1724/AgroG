"use client";

import * as React from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ShoppingCart, Loader2, Star } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
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
  primary_image_url?: string | null;
  images?: { id: string; image_url: string; is_primary: boolean }[];
  average_rating?: number | null;
  review_count: number;
}

interface Review {
  id: string;
  rating: number;
  comment: string;
  reviewer_name?: string;
  created_at: string;
}

export default function ListingDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const { user } = useAuth();
  const listingId = params.id as string;
  const [quantity, setQuantity] = React.useState<number>(1);

  // Fetch listing details
  const { data: listing, isLoading, error } = useQuery<CropListing>({
    queryKey: ["listingDetails", listingId],
    queryFn: async () => {
      const response = await api.get(`/marketplace/listings/${listingId}`);
      return response.data;
    },
    enabled: !!listingId,
  });

  const { data: reviews = [] } = useQuery<Review[]>({
    queryKey: ["listingReviews", listingId],
    queryFn: async () => (await api.get(`/reviews/listings/${listingId}`)).data,
    enabled: !!listingId,
  });

  const addToCartMutation = useMutation({
    mutationFn: async (payload: { crop_listing_id: string; quantity: number }) => {
      const response = await api.post("/cart/items", payload);
      return response.data;
    },
    onSuccess: () => {
      toast({
        title: "Added to Cart",
        description: "Review your cart before checkout.",
        variant: "default",
      });
      router.push("/cart");
    },
    onError: (err: unknown) => {
      const errMsg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Failed to place order. Please try again.";
      toast({
        title: "Add to Cart Failed",
        description: errMsg,
        variant: "destructive",
      });
    },
  });

  const handleAddToCart = () => {
    if (!user) {
      toast({
        title: "Authentication Required",
        description: "Please log in to add crop listings to your cart.",
        variant: "destructive",
      });
      router.push(`/login?redirect=/marketplace/${listingId}`);
      return;
    }

    if (user.role !== "customer") {
      toast({
        title: "Action Restricted",
        description: "Only customer accounts can purchase marketplace items.",
        variant: "destructive",
      });
      return;
    }

    if (quantity <= 0) {
      toast({
        title: "Invalid Quantity",
        description: "Please enter a valid quantity of 1 or more.",
        variant: "destructive",
      });
      return;
    }

    if (listing && quantity > listing.available_quantity) {
      toast({
        title: "Insufficient Stock",
        description: `Only ${listing.available_quantity} ${listing.unit} available.`,
        variant: "destructive",
      });
      return;
    }

    addToCartMutation.mutate({ crop_listing_id: listingId, quantity });
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground text-sm">Loading crop listing details...</p>
      </div>
    );
  }

  if (error || !listing) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold text-destructive">Listing Not Found</h2>
        <p className="text-muted-foreground mt-2">
          The requested crop listing does not exist or may have been deleted by the farmer.
        </p>
        <Link href="/marketplace" className="inline-block mt-6">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Marketplace
          </Button>
        </Link>
      </div>
    );
  }

  const maxQty = listing.available_quantity;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Navigation breadcrumb */}
      <div className="mb-6">
        <Link href="/marketplace" className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Marketplace
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left Side: Product Image Display */}
        <div className="w-full h-[350px] md:h-[450px] bg-secondary/20 rounded-2xl flex items-center justify-center overflow-hidden border border-secondary/30 relative">
          {listing.primary_image_url || listing.image_urls ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={listing.primary_image_url || listing.image_urls?.split(",")[0]}
              alt={listing.title}
              className="w-full h-full object-cover transition-transform hover:scale-105 duration-300"
            />
          ) : (
            <div className="flex flex-col items-center gap-2">
              <span className="text-6xl">🌱</span>
              <span className="text-muted-foreground text-sm font-semibold">No Image Provided</span>
            </div>
          )}
        </div>

        {listing.images?.length ? (
          <div className="md:hidden grid grid-cols-3 gap-2">
            {listing.images.slice(0, 3).map((image) => (
              // eslint-disable-next-line @next/next/no-img-element
              <img key={image.id} src={image.image_url} alt={listing.title} className="h-20 w-full rounded-lg object-cover border border-slate-200" />
            ))}
          </div>
        ) : null}

        {/* Right Side: Product Details & Order Card */}
        <div className="flex flex-col justify-between h-full space-y-6">
          <div className="space-y-4">
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-primary">
              {listing.title}
            </h1>
            
            <div className="flex flex-wrap gap-4 items-center">
              <span className="text-3xl font-extrabold text-primary">
                ${listing.price_per_unit}
                <span className="text-lg font-normal text-muted-foreground"> / {listing.unit}</span>
              </span>
              <div className="px-3 py-1 bg-primary/10 text-primary font-semibold text-xs rounded-full">
                Verified Farmer Listing
              </div>
              <Link href={`/farmers/${listing.farmer_id}`} className="px-3 py-1 bg-emerald-50 text-emerald-700 font-semibold text-xs rounded-full hover:bg-emerald-100">
                View Farmer Profile
              </Link>
            </div>

            <div className="inline-flex items-center gap-1 text-sm text-slate-600">
              <Star className="h-4 w-4 text-amber-500" />
              {listing.average_rating ? `${listing.average_rating}/5 (${listing.review_count} reviews)` : "No reviews yet"}
            </div>

            <div className="h-px bg-muted" />

            <div className="space-y-2">
              <h3 className="text-sm font-bold tracking-wide text-muted-foreground uppercase">Description</h3>
              <p className="text-base text-foreground leading-relaxed">
                {listing.description}
              </p>
            </div>
          </div>

          <Card className="border-secondary/20 shadow-md">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg font-bold">Add to Cart</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Stock Status:</span>
                <span className={`text-sm font-semibold ${maxQty > 0 ? "text-emerald-600" : "text-destructive"}`}>
                  {maxQty > 0 ? `${maxQty} ${listing.unit} Available` : "Out of Stock"}
                </span>
              </div>

              {maxQty > 0 && (
                <div className="space-y-2">
                  <label htmlFor="quantity" className="text-sm font-semibold text-muted-foreground">
                    Quantity ({listing.unit})
                  </label>
                  <div className="flex items-center gap-3">
                    <Input
                      id="quantity"
                      type="number"
                      min={1}
                      max={maxQty}
                      value={quantity}
                      onChange={(e) => {
                        const val = parseInt(e.target.value);
                        if (!isNaN(val)) {
                          setQuantity(Math.min(Math.max(1, val), maxQty));
                        }
                      }}
                      className="w-24 text-center font-bold"
                    />
                    <span className="text-sm font-medium text-muted-foreground">
                      Total: <span className="text-primary font-bold text-base">${(listing.price_per_unit * quantity).toFixed(2)}</span>
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
            <CardFooter>
              <Button
                onClick={handleAddToCart}
                disabled={maxQty <= 0 || addToCartMutation.isPending}
                className="w-full flex items-center justify-center gap-2 font-bold py-6 text-base"
              >
                {addToCartMutation.isPending ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" /> Adding...
                  </>
                ) : (
                  <>
                    <ShoppingCart className="h-5 w-5" /> Add to Cart
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-2xl font-extrabold text-slate-900 mb-4">Reviews</h2>
        {reviews.length === 0 ? (
          <Card><CardContent className="p-6 text-slate-500">No reviews yet.</CardContent></Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {reviews.map((review) => (
              <Card key={review.id}>
                <CardContent className="p-4 space-y-2">
                  <div className="font-bold flex items-center gap-1"><Star className="h-4 w-4 text-amber-500" /> {review.rating}/5</div>
                  <p className="text-sm text-slate-600">{review.comment}</p>
                  <p className="text-xs text-slate-400">{review.reviewer_name || "Customer"} · {new Date(review.created_at).toLocaleDateString()}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
