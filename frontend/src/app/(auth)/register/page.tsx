"use client";

import * as React from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Script from "next/script";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";
import { useAuth } from "@/components/shared/auth-context";
import { api } from "@/lib/api";

const registerSchema = z.object({
  email: z.string().email({ message: "Invalid email address" }),
  password: z.string().min(6, { message: "Password must be at least 6 characters" }),
  full_name: z.string().min(2, { message: "Name must be at least 2 characters" }),
  phone_number: z.string().optional(),
  role: z.enum(["customer", "farmer"]),
  farm_name: z.string().optional(),
  latitude: z.string().optional(),
  longitude: z.string().optional(),
  address: z.string().optional(),
}).refine((data) => {
  if (data.role === "farmer") {
    return !!data.farm_name && !!data.latitude && !!data.longitude && !!data.address;
  }
  return true;
}, {
  message: "Farmer details are required when registering as a farmer",
  path: ["farm_name"],
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { login } = useAuth();
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const {
    register: formRegister,
    handleSubmit,
    watch,
    control,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema as unknown as Parameters<typeof zodResolver>[0]),
    defaultValues: {
      role: "customer"
    }
  });

  const selectedRole = watch("role");

  const onSubmit = async (data: RegisterFormValues) => {
    setIsSubmitting(true);
    
    // Prepare payload matching the UserCreate schema
    const payload: Record<string, unknown> = {
      email: data.email,
      password: data.password,
      full_name: data.full_name,
      phone_number: data.phone_number || null,
      role: data.role,
    };

    if (data.role === "farmer") {
      payload.farmer_details = {
        farm_name: data.farm_name,
        latitude: parseFloat(data.latitude || "0"),
        longitude: parseFloat(data.longitude || "0"),
        address: data.address,
        description: "",
      };
    }

    try {
      await api.post("/auth/register", payload);
      toast("Account registered successfully! Please log in.", "success");
      router.push("/login");
    } catch (error: unknown) {
      const msg = (error as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Registration failed. Try again.";
      toast(msg, "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleCredentialResponse = React.useCallback(
    async (response: any) => {
      try {
        const apiResponse = await api.post("/auth/google", {
          id_token: response.credential,
        });
        await login(apiResponse.data);
        toast("Google Registration/Login successful!", "success");

        const role = apiResponse.data.role || "customer";
        if (role === "farmer") {
          router.push("/farmer/listings");
        } else {
          router.push("/marketplace");
        }
      } catch (error: unknown) {
        const err = error as { response?: { data?: { detail?: string } } };
        const msg = err.response?.data?.detail || "Google authentication failed.";
        toast(msg, "error");
      }
    },
    [login, router, toast]
  );

  const initGoogleAuth = React.useCallback(() => {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
    if (!clientId) {
      console.warn("NEXT_PUBLIC_GOOGLE_CLIENT_ID is not defined in the environment");
      return;
    }

    const google = (window as any).google;
    if (google?.accounts?.id) {
      google.accounts.id.initialize({
        client_id: clientId,
        callback: handleGoogleCredentialResponse,
      });
      google.accounts.id.renderButton(
        document.getElementById("google-signin-btn"),
        { theme: "outline", size: "large", width: "100%", text: "signup_with" }
      );
    }
  }, [handleGoogleCredentialResponse]);

  React.useEffect(() => {
    initGoogleAuth();
  }, [initGoogleAuth]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8">
      <Card className="w-full max-w-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl text-center font-bold text-primary">Join AgroGuide</CardTitle>
          <CardDescription className="text-center">
            Create an account to browse products or access agricultural analytics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Full Name</label>
                <Input placeholder="John Doe" {...formRegister("full_name")} />
                {errors.full_name && <p className="text-xs text-destructive">{errors.full_name.message}</p>}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Role</label>
                <Controller
                  control={control}
                  name="role"
                  render={({ field }) => (
                    <Select value={field.value} onValueChange={field.onChange}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a role" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="customer">Buyer / Customer</SelectItem>
                        <SelectItem value="farmer">Farmer / Seller</SelectItem>
                      </SelectContent>
                    </Select>
                  )}
                />
                {errors.role && <p className="text-xs text-destructive">{errors.role.message}</p>}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Email</label>
                <Input type="email" placeholder="example@email.com" {...formRegister("email")} />
                {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Phone Number</label>
                <Input placeholder="+1234567890" {...formRegister("phone_number")} />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Password</label>
              <Input type="password" placeholder="••••••••" {...formRegister("password")} />
              {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
            </div>

            {selectedRole === "farmer" && (
              <div className="mt-4 p-4 border border-dashed rounded-lg bg-muted/40 space-y-4">
                <h3 className="text-sm font-bold text-primary">Farmer Details</h3>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Farm Name</label>
                  <Input placeholder="Green Valley Farm" {...formRegister("farm_name")} />
                  {errors.farm_name && <p className="text-xs text-destructive">{errors.farm_name.message}</p>}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Latitude</label>
                    <Input placeholder="28.6139" {...formRegister("latitude")} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Longitude</label>
                    <Input placeholder="77.2090" {...formRegister("longitude")} />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Farm Address</label>
                  <Input placeholder="Sector 12, Farm Lane, New Delhi" {...formRegister("address")} />
                </div>
              </div>
            )}

            <Button type="submit" className="w-full mt-4" disabled={isSubmitting}>
              {isSubmitting ? "Creating Account..." : "Create Account"}
            </Button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">Or continue with</span>
            </div>
          </div>

          <div className="w-full flex justify-center min-h-[40px]">
            <div id="google-signin-btn" className="w-full"></div>
          </div>
        </CardContent>
        <CardFooter className="flex flex-wrap items-center justify-center gap-1 text-sm">
          <span>Already have an account?</span>
          <Link href="/login" className="text-primary hover:underline font-medium">
            Log in here
          </Link>
        </CardFooter>
      </Card>
      <Script
        src="https://accounts.google.com/gsi/client"
        onReady={initGoogleAuth}
        strategy="lazyOnload"
      />
    </div>
  );
}
