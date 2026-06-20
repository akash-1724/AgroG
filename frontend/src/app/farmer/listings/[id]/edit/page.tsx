"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useRouter, useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";

import ProtectedRoute from "@/components/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";
import { api } from "@/lib/api";

const listingSchema = z.object({
  title: z.string().min(3, { message: "Title must be at least 3 characters" }),
  description: z.string().min(10, { message: "Description must be at least 10 characters" }),
  price_per_unit: z.preprocess((val) => parseFloat(val as string), z.number().positive({ message: "Price must be positive" })),
  unit: z.string().min(1, { message: "Unit is required" }),
  available_quantity: z.preprocess((val) => parseInt(val as string), z.number().int().positive({ message: "Quantity must be positive" })),
  category: z.string().min(1, { message: "Category is required" }),
  image_urls: z.string().optional(),
  status: z.enum(["active", "inactive", "sold_out"]),
});

type ListingFormValues = z.infer<typeof listingSchema>;

export default function EditListingPage() {
  return (
    <ProtectedRoute allowedRoles={["farmer"]}>
      <EditListingContent />
    </ProtectedRoute>
  );
}

function EditListingContent() {
  const router = useRouter();
  const params = useParams();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const listingId = params.id as string;
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [imageFiles, setImageFiles] = React.useState<FileList | null>(null);

  const {
    register: formRegister,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<ListingFormValues>({
    resolver: zodResolver(listingSchema as unknown as Parameters<typeof zodResolver>[0]),
  });

  // Query to fetch current listing values
  const { data: listingData, isLoading: isLoadingData } = useQuery({
    queryKey: ["editListing", listingId],
    queryFn: async () => {
      const response = await api.get(`/marketplace/listings/${listingId}`);
      const data = response.data;
      // Populate fields
      setValue("title", data.title);
      setValue("description", data.description);
      setValue("price_per_unit", data.price_per_unit);
      setValue("unit", data.unit);
      setValue("available_quantity", data.available_quantity);
      setValue("category", data.category || "Vegetables");
      setValue("image_urls", data.image_urls || "");
      setValue("status", data.status || "active");
      return data;
    },
    enabled: !!listingId,
  });

  const uploadImagesMutation = useMutation({
    mutationFn: async () => {
      if (!imageFiles?.length) return;
      for (const file of Array.from(imageFiles)) {
        const formData = new FormData();
        formData.append("file", file);
        await api.post(`/marketplace/listings/${listingId}/images`, formData, { headers: { "Content-Type": "multipart/form-data" } });
      }
    },
    onSuccess: async () => {
      toast("Listing image uploaded successfully.", "success");
      setImageFiles(null);
      await queryClient.invalidateQueries({ queryKey: ["editListing", listingId] });
    },
    onError: (error: unknown) => {
      const msg = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Failed to upload listing image.";
      toast(msg, "error");
    },
  });

  const deleteImageMutation = useMutation({
    mutationFn: async (imageId: string) => api.delete(`/marketplace/listings/${listingId}/images/${imageId}`),
    onSuccess: async () => {
      toast("Listing image deleted.", "success");
      await queryClient.invalidateQueries({ queryKey: ["editListing", listingId] });
    },
    onError: (error: unknown) => {
      const msg = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Failed to delete listing image.";
      toast(msg, "error");
    },
  });

  const onSubmit = async (data: ListingFormValues) => {
    setIsSubmitting(true);
    try {
      await api.put(`/marketplace/listings/${listingId}`, data);
      toast("Crop listing updated successfully!", "success");
      router.push("/farmer/listings");
    } catch (error: unknown) {
      const msg = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Failed to update crop listing.";
      toast(msg, "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3 text-slate-500">
        <Loader2 className="h-10 w-10 animate-spin text-emerald-500" />
        <span className="text-sm font-medium">Loading crop listing metadata...</span>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div>
        <Link href="/farmer/listings" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-slate-800 transition">
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Listings
        </Link>
      </div>

      <Card className="border-slate-200/80 shadow-sm bg-white rounded-xl">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-slate-900">Edit Crop Listing</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Listing Title</label>
              <Input placeholder="Fresh Organic Tomatoes" {...formRegister("title")} />
              {errors.title && <p className="text-xs text-red-500">{errors.title.message}</p>}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Category</label>
                <select
                  {...formRegister("category")}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg text-sm px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500 transition"
                >
                  <option value="Vegetables">Vegetables</option>
                  <option value="Fruits">Fruits</option>
                  <option value="Grains">Grains</option>
                  <option value="Pulses">Pulses</option>
                  <option value="Spices">Spices</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Measurement Unit</label>
                <Input placeholder="kg, lbs, tons, crate" {...formRegister("unit")} />
                {errors.unit && <p className="text-xs text-red-500">{errors.unit.message}</p>}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Status</label>
                <select
                  {...formRegister("status")}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg text-sm px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500 transition"
                >
                  <option value="active">Active (Visible)</option>
                  <option value="inactive">Inactive (Hidden)</option>
                  <option value="sold_out">Sold Out</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Price per Unit ($)</label>
                <Input type="number" step="0.01" placeholder="2.50" {...formRegister("price_per_unit")} />
                {errors.price_per_unit && <p className="text-xs text-red-500">{errors.price_per_unit.message}</p>}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Available Quantity</label>
                <Input type="number" placeholder="100" {...formRegister("available_quantity")} />
                {errors.available_quantity && <p className="text-xs text-red-500">{errors.available_quantity.message}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Description</label>
              <textarea
                rows={4}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg text-sm p-3 outline-none focus:ring-2 focus:ring-emerald-500 transition"
                placeholder="Describe your crop condition, harvest date, organic practices..."
                {...formRegister("description")}
              />
              {errors.description && <p className="text-xs text-red-500">{errors.description.message}</p>}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Legacy Image URL (Optional)</label>
              <Input placeholder="https://example.com/tomatoes.jpg" {...formRegister("image_urls")} />
            </div>

            <div className="space-y-3 rounded-xl border border-slate-200 bg-slate-50 p-3">
              <label className="text-sm font-medium text-slate-700">Uploaded Images</label>
              {listingData?.images?.length ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {listingData.images.map((image: { id: string; image_url: string; is_primary: boolean }) => (
                    <div key={image.id} className="space-y-2">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={image.image_url} alt="Listing" className="h-24 w-full rounded-lg object-cover border border-slate-200" />
                      <Button type="button" size="sm" variant="outline" onClick={() => deleteImageMutation.mutate(image.id)} disabled={deleteImageMutation.isPending}>
                        Delete {image.is_primary ? "Primary" : ""}
                      </Button>
                    </div>
                  ))}
                </div>
              ) : <p className="text-xs text-slate-500">No uploaded images yet.</p>}
              <Input type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={(event) => setImageFiles(event.target.files)} />
              <Button type="button" variant="outline" onClick={() => uploadImagesMutation.mutate()} disabled={!imageFiles?.length || uploadImagesMutation.isPending}>
                {uploadImagesMutation.isPending ? "Uploading..." : "Upload Selected Images"}
              </Button>
            </div>

            <Button type="submit" className="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" /> Saving Changes...
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
