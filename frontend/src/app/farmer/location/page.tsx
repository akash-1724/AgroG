"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery, useMutation } from "@tanstack/react-query";
import { MapPin, Loader2, Save, Eye, EyeOff } from "lucide-react";

import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";

const locationFormSchema = z.object({
  latitude: z.coerce.number().min(-90.0, "Latitude must be between -90 and 90").max(90.0, "Latitude must be between -90 and 90"),
  longitude: z.coerce.number().min(-180.0, "Longitude must be between -180 and 180").max(180.0, "Longitude must be between -180 and 180"),
  address: z.string().min(5, "Address must be at least 5 characters").max(500),
  district: z.string().max(100).optional(),
  city: z.string().max(100).optional(),
  state: z.string().max(100).optional(),
  location_visibility: z.boolean().default(true),
});

type LocationFormValues = z.infer<typeof locationFormSchema>;

export default function FarmerLocationPage() {
  const { toast } = useToast();

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    watch,
    formState: { errors },
  } = useForm<LocationFormValues>({
    resolver: zodResolver(locationFormSchema as unknown as Parameters<typeof zodResolver>[0]),
    defaultValues: {
      latitude: 0.0,
      longitude: 0.0,
      address: "",
      district: "",
      city: "",
      state: "",
      location_visibility: true,
    },
  });

  const locationVisibility = watch("location_visibility");

  // Fetch current farmer profile to populate fields
  const { data: profile, isLoading } = useQuery({
    queryKey: ["my-farmer-profile"],
    queryFn: async () => {
      // The current authenticated user endpoint in auth gives full details,
      // but let's query the location directly or read from active context.
      const response = await api.get("/auth/me");
      return response.data.farmer_profile;
    },
  });

  React.useEffect(() => {
    if (profile) {
      reset({
        latitude: profile.latitude ?? 0.0,
        longitude: profile.longitude ?? 0.0,
        address: profile.address ?? "",
        district: profile.district ?? "",
        city: profile.city ?? "",
        state: profile.state ?? "",
        location_visibility: profile.location_visibility ?? true,
      });
    }
  }, [profile, reset]);

  const updateLocationMutation = useMutation({
    mutationFn: async (values: LocationFormValues) => {
      const response = await api.patch("/farmers/me/location", values);
      return response.data;
    },
    onSuccess: () => {
      toast({
        title: "Location Updated",
        description: "Successfully updated your farm coordinate visibility and details.",
      });
    },
    onError: (err: unknown) => {
      const errMsg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Failed to update location.";
      toast({
        title: "Update Failed",
        description: errMsg,
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data: LocationFormValues) => {
    updateLocationMutation.mutate(data);
  };

  const handleGetBrowserLocation = () => {
    if (!navigator.geolocation) {
      toast({
        title: "Not Supported",
        description: "Geolocation is not supported by your browser.",
        variant: "destructive",
      });
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setValue("latitude", position.coords.latitude, { shouldValidate: true });
        setValue("longitude", position.coords.longitude, { shouldValidate: true });
        toast({
          title: "Coordinates Synced",
          description: "Latitude and Longitude populated from GPS coordinates.",
        });
      },
      (error) => {
        toast({
          title: "GPS Lock Failed",
          description: error.message || "Failed to fetch geolocation coordinates.",
          variant: "destructive",
        });
      }
    );
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary mb-2" />
        <p className="text-xs text-muted-foreground">Loading farm coordinates profile...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <Card className="border-secondary/20 shadow-md">
        <CardHeader className="bg-primary/5 rounded-t-xl border-b border-primary/10">
          <CardTitle className="text-xl font-bold text-primary flex items-center gap-2">
            <MapPin className="h-6 w-6 text-primary" /> Farm Location Settings
          </CardTitle>
          <CardDescription>
            Update your farm&apos;s coordinate visibility and addresses to help local customers discover your listings.
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            
            <div className="grid grid-cols-2 gap-4">
              {/* Latitude */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Latitude</label>
                <Input {...register("latitude")} type="number" step="any" placeholder="e.g. 12.9716" />
                {errors.latitude && <p className="text-xs text-destructive">{errors.latitude.message}</p>}
              </div>

              {/* Longitude */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Longitude</label>
                <Input {...register("longitude")} type="number" step="any" placeholder="e.g. 77.5946" />
                {errors.longitude && <p className="text-xs text-destructive">{errors.longitude.message}</p>}
              </div>
            </div>

            <Button
              type="button"
              variant="outline"
              onClick={handleGetBrowserLocation}
              className="w-full font-bold flex items-center justify-center gap-2 text-xs"
            >
              <MapPin className="h-4 w-4" /> Autofill GPS Coordinates
            </Button>

            {/* Address */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Farm Address</label>
              <textarea
                {...register("address")}
                rows={3}
                placeholder="Specify street address, landmark, block..."
                className="w-full border border-input bg-background px-3 py-2 rounded-md text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2"
              />
              {errors.address && <p className="text-xs text-destructive">{errors.address.message}</p>}
            </div>

            <div className="grid grid-cols-3 gap-3">
              {/* District */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">District / County</label>
                <Input {...register("district")} placeholder="e.g. Kolar" />
              </div>

              {/* City */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">City</label>
                <Input {...register("city")} placeholder="e.g. Bangalore" />
              </div>

              {/* State */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">State</label>
                <Input {...register("state")} placeholder="e.g. Karnataka" />
              </div>
            </div>

            {/* Visibility Toggle */}
            <div className="p-4 rounded-xl border border-muted bg-muted/20 flex items-center justify-between gap-4 mt-2">
              <div className="space-y-0.5">
                <div className="text-xs font-bold text-foreground flex items-center gap-1.5">
                  {locationVisibility ? (
                    <>
                      <Eye className="h-4 w-4 text-emerald-600" /> Location Public
                    </>
                  ) : (
                    <>
                      <EyeOff className="h-4 w-4 text-amber-600" /> Location Hidden
                    </>
                  )}
                </div>
                <div className="text-[10px] text-muted-foreground">
                  When enabled, buyers can discover your farm details in nearby search results.
                </div>
              </div>
              <input
                type="checkbox"
                {...register("location_visibility")}
                className="h-5 w-5 rounded border-gray-350 text-primary focus:ring-primary shrink-0 cursor-pointer"
              />
            </div>

            {/* Submit Button */}
            <div className="pt-4 border-t border-muted/55 flex justify-end">
              <Button
                type="submit"
                disabled={updateLocationMutation.isPending}
                className="font-bold flex items-center gap-2 px-6"
              >
                {updateLocationMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" /> Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" /> Save Settings
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
