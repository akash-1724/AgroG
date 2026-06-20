"use client";

import * as React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { Loader2, ShoppingCart, Trash2 } from "lucide-react";

import ProtectedRoute from "@/components/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { api } from "@/lib/api";

interface CartItem {
  id: string;
  crop_listing_id: string;
  title: string;
  farmer_id: string;
  farmer_name: string;
  unit_price: number;
  unit: string;
  quantity: number;
  available_quantity: number;
  status: string;
  image_urls?: string;
  subtotal: number;
}

interface Cart {
  id: string;
  items: CartItem[];
  estimated_total: number;
}

export default function CartPage() {
  return (
    <ProtectedRoute allowedRoles={["customer"]}>
      <CartContent />
    </ProtectedRoute>
  );
}

function CartContent() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: cart, isLoading, error } = useQuery<Cart>({
    queryKey: ["cart"],
    queryFn: async () => (await api.get("/cart")).data,
  });

  const updateItem = useMutation({
    mutationFn: async ({ id, quantity }: { id: string; quantity: number }) => (await api.patch(`/cart/items/${id}`, { quantity })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cart"] }),
    onError: (err: unknown) => toast((err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Could not update cart item.", "error"),
  });

  const removeItem = useMutation({
    mutationFn: async (id: string) => api.delete(`/cart/items/${id}`),
    onSuccess: () => {
      toast("Item removed from cart.", "success");
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
  });

  const clearCart = useMutation({
    mutationFn: async () => api.delete("/cart/clear"),
    onSuccess: () => {
      toast("Cart cleared.", "success");
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
  });

  const checkout = useMutation({
    mutationFn: async () => (await api.post("/cart/checkout")).data,
    onSuccess: () => {
      toast("Checkout complete. Your order is pending farmer confirmation.", "success");
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      queryClient.invalidateQueries({ queryKey: ["customerOrders"] });
    },
    onError: (err: unknown) => toast((err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Checkout failed. Please review your cart.", "error"),
  });

  if (isLoading) {
    return <div className="min-h-[50vh] flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-emerald-600" /></div>;
  }

  if (error) {
    return <div className="max-w-4xl mx-auto px-4 py-12 text-red-600 font-semibold">Failed to load cart.</div>;
  }

  const items = cart?.items || [];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between gap-4 sm:items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900">Your Cart</h1>
          <p className="text-sm text-slate-500 mt-1">Review stock, quantities, and totals before checkout.</p>
        </div>
        <Link href="/marketplace"><Button variant="outline">Continue Shopping</Button></Link>
      </div>

      {items.length === 0 ? (
        <Card className="text-center py-16">
          <CardContent className="space-y-4">
            <ShoppingCart className="h-12 w-12 text-slate-300 mx-auto" />
            <div>
              <h2 className="text-xl font-bold text-slate-900">Cart is empty</h2>
              <p className="text-sm text-slate-500 mt-1">Add crops from the marketplace to start checkout.</p>
            </div>
            <Link href="/marketplace"><Button className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold">Browse Marketplace</Button></Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
          <div className="space-y-4">
            {items.map((item) => (
              <Card key={item.id} className="overflow-hidden">
                <CardContent className="p-4 flex flex-col md:flex-row gap-4 md:items-center">
                  <div className="h-24 w-full md:w-32 rounded-xl bg-slate-100 overflow-hidden flex items-center justify-center text-slate-400">
                    {item.image_urls ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={item.image_urls.split(",")[0]} alt={item.title} className="h-full w-full object-cover" />
                    ) : "No image"}
                  </div>
                  <div className="flex-1 space-y-1">
                    <Link href={`/marketplace/${item.crop_listing_id}`} className="font-bold text-slate-900 hover:text-emerald-700">{item.title}</Link>
                    <div className="text-sm text-slate-500">Farmer: <Link className="underline" href={`/farmers/${item.farmer_id}`}>{item.farmer_name}</Link></div>
                    <div className="text-sm text-slate-600">${item.unit_price} / {item.unit} · {item.available_quantity} available</div>
                  </div>
                  <div className="flex md:flex-col items-center md:items-end gap-3">
                    <Input
                      type="number"
                      min={1}
                      max={item.available_quantity}
                      value={item.quantity}
                      onChange={(event) => {
                        const quantity = Number(event.target.value);
                        if (quantity > 0) updateItem.mutate({ id: item.id, quantity });
                      }}
                      className="w-24 text-center"
                    />
                    <div className="font-extrabold text-slate-900">${item.subtotal.toFixed(2)}</div>
                    <Button variant="outline" size="sm" onClick={() => removeItem.mutate(item.id)} disabled={removeItem.isPending}>
                      <Trash2 className="h-4 w-4 mr-1" /> Remove
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="h-fit sticky top-20">
            <CardHeader><CardTitle>Order Summary</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between text-sm text-slate-600"><span>Items</span><span>{items.length}</span></div>
              <div className="flex justify-between text-lg font-extrabold"><span>Estimated Total</span><span>${(cart?.estimated_total || 0).toFixed(2)}</span></div>
              <Button className="w-full bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold" onClick={() => checkout.mutate()} disabled={checkout.isPending}>
                {checkout.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null} Checkout
              </Button>
              <Button variant="outline" className="w-full" onClick={() => clearCart.mutate()} disabled={clearCart.isPending}>Clear Cart</Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
