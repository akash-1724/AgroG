"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { MapPin, Search, Navigation, AlertCircle, Phone, Star } from "lucide-react";
import Link from "next/link";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";

interface NearbyFarmer {
  farmer_id: string;
  full_name: string;
  farm_name?: string;
  latitude: number;
  longitude: number;
  address: string;
  district?: string;
  city?: string;
  state?: string;
  distance_km: number;
  rating: number;
}

export default function NearbyFarmersPage() {
  const { toast } = useToast();
  
  // Default coordinate center (Bengaluru coordinates as fallback)
  const [lat, setLat] = React.useState<number | null>(null);
  const [lon, setLon] = React.useState<number | null>(null);
  const [radius, setRadius] = React.useState(10);
  const [coordsLoading, setCoordsLoading] = React.useState(false);

  // Autofill GPS coordinates on mount
  React.useEffect(() => {
    handleFetchCurrentLocation(false);
  }, []);

  const handleFetchCurrentLocation = (showToast = true) => {
    if (!navigator.geolocation) {
      if (showToast) {
        toast({
          title: "Not Supported",
          description: "Geolocation is not supported by your browser.",
          variant: "destructive",
        });
      }
      // Fallback
      setLat(12.9716);
      setLon(77.5946);
      return;
    }

    setCoordsLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLat(position.coords.latitude);
        setLon(position.coords.longitude);
        setCoordsLoading(false);
        if (showToast) {
          toast({
            title: "GPS Lock Success",
            description: "Center coordinates updated from your browser GPS.",
          });
        }
      },
      (error) => {
        setCoordsLoading(false);
        if (showToast) {
          toast({
            title: "GPS Failed",
            description: error.message || "Failed to get current location coordinates.",
            variant: "destructive",
          });
        }
        // Fallback
        setLat(12.9716);
        setLon(77.5946);
      }
    );
  };

  // Query nearby farmers once coords are populated
  const { data: farmers = [], isLoading, refetch } = useQuery<NearbyFarmer[]>({
    queryKey: ["nearby-farmers", lat, lon, radius],
    queryFn: async () => {
      const response = await api.get("/farmers/nearby", {
        params: { lat, lon, radius },
      });
      return response.data;
    },
    enabled: lat !== null && lon !== null,
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header section */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold tracking-tight text-primary flex items-center gap-2">
          <Navigation className="h-8 w-8 text-primary animate-pulse" /> Discover Nearby Farmers
        </h1>
        <p className="text-muted-foreground mt-1">
          Find local active farmers in your vicinity, check distance approximations, and browse listings.
        </p>
      </div>

      {/* Location config bar */}
      <div className="p-4 rounded-xl border border-secondary/20 bg-secondary/10 shadow-sm flex flex-col md:flex-row gap-4 justify-between items-center mb-8">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center w-full md:w-auto">
          <Button
            onClick={() => handleFetchCurrentLocation(true)}
            disabled={coordsLoading}
            variant="outline"
            className="flex items-center gap-2 font-bold shrink-0 text-xs py-5"
          >
            <MapPin className="h-4 w-4 text-primary" />
            {coordsLoading ? "Locating..." : "Use My Current Location"}
          </Button>

          {lat && lon && (
            <div className="text-xs text-muted-foreground font-semibold">
              Current Center: <span className="text-foreground">{lat.toFixed(4)}, {lon.toFixed(4)}</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto shrink-0 justify-end">
          <label className="text-xs font-bold text-muted-foreground whitespace-nowrap">Search Radius:</label>
          <select
            value={radius}
            onChange={(e) => setRadius(Number(e.target.value))}
            className="border border-input bg-background px-3 py-2 rounded-md text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value={5}>5 km</option>
            <option value={10}>10 km</option>
            <option value={25}>25 km</option>
            <option value={50}>50 km</option>
            <option value={100}>100 km</option>
          </select>
        </div>
      </div>

      {/* Loading state */}
      {isLoading || lat === null ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((n) => (
            <Card key={n} className="border-secondary/20 shadow-sm animate-pulse h-60" />
          ))}
        </div>
      ) : farmers.length === 0 ? (
        <Card className="border-dashed border-2 py-16 text-center">
          <AlertCircle className="h-12 w-12 text-muted/40 mx-auto mb-3" />
          <h3 className="font-bold text-lg text-foreground">No Farmers Nearby</h3>
          <p className="text-muted-foreground text-sm max-w-sm mx-auto mt-1">
            We couldn't find any visible farmers within a {radius}km radius of your coordinates. Try expanding your search radius.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {farmers.map((farmer) => (
            <Card key={farmer.farmer_id} className="border-secondary/20 shadow-md flex flex-col hover:border-primary/40 transition-colors">
              <CardHeader>
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center gap-1.5 text-xs text-primary font-bold">
                    <MapPin className="h-3.5 w-3.5" />
                    <span>{farmer.distance_km} km away</span>
                  </div>
                  <div className="flex items-center gap-0.5 text-amber-500 text-xs font-bold bg-amber-50 px-2 py-0.5 rounded-full border border-amber-100">
                    <Star className="h-3.5 w-3.5 fill-amber-500" />
                    <span>{farmer.rating.toFixed(1)}</span>
                  </div>
                </div>
                <CardTitle className="text-xl font-bold leading-tight">
                  {farmer.farm_name || "Organic Family Farm"}
                </CardTitle>
                <CardDescription className="text-sm font-semibold text-muted-foreground mt-0.5">
                  Farmer: {farmer.full_name}
                </CardDescription>
              </CardHeader>

              <CardContent className="flex-grow space-y-3">
                <div className="text-xs text-foreground bg-secondary/15 border border-secondary/20 rounded-lg p-3">
                  <strong className="text-muted-foreground uppercase text-[8px] tracking-wider block mb-1">Approximate Location:</strong>
                  <p>{farmer.address}</p>
                  {(farmer.city || farmer.state) && (
                    <p className="text-[10px] text-muted-foreground font-semibold mt-1">
                      {farmer.city && `${farmer.city}, `}{farmer.district && `${farmer.district}, `}{farmer.state}
                    </p>
                  )}
                </div>
              </CardContent>

              <CardFooter className="pt-0 border-t border-muted/30 mt-4 flex items-center justify-between">
                <span className="text-[9px] text-muted-foreground font-semibold italic">
                  GPS Truncation active for privacy
                </span>
                <Link href={`/marketplace?farmer_id=${farmer.farmer_id}`}>
                  <Button variant="default" size="sm" className="font-bold text-xs">
                    View Produce
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
