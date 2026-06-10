"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";
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
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const {
    register: formRegister,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      role: "customer"
    }
  });

  const selectedRole = watch("role");

  const onSubmit = async (data: RegisterFormValues) => {
    setIsSubmitting(true);
    
    // Prepare payload matching the UserCreate schema
    const payload: any = {
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
    } catch (error: any) {
      const msg = error.response?.data?.detail || "Registration failed. Try again.";
      toast(msg, "error");
    } finally {
      setIsSubmitting(false);
    }
  };

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
                <Select {...formRegister("role")}>
                  <option value="customer">Buyer / Customer</option>
                  <option value="farmer">Farmer / Seller</option>
                </Select>
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
        </CardContent>
        <CardFooter className="flex flex-wrap items-center justify-center gap-1 text-sm">
          <span>Already have an account?</span>
          <Link href="/login" className="text-primary hover:underline font-medium">
            Log in here
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
