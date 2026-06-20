"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ShoppingBag, Calendar, DollarSign, Package } from "lucide-react";

import ProtectedRoute from "@/components/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { useToast } from "@/components/ui/toast";
import { api } from "@/lib/api";

type FulfillmentStatus = "pending" | "accepted" | "ready" | "completed" | "rejected" | "cancelled";

interface OrderItem {
  id: string;
  order_id: string;
  crop_listing_id: string;
  quantity: number;
  price_at_purchase: number;
  status: FulfillmentStatus;
}

interface Order {
  id: string;
  customer_id: string;
  status: FulfillmentStatus;
  total_amount: number;
  created_at: string;
  items: OrderItem[];
}

const itemStatusActions: Record<FulfillmentStatus, FulfillmentStatus[]> = {
  pending: ["accepted", "rejected"],
  accepted: ["ready", "rejected"],
  ready: ["completed"],
  completed: [],
  rejected: [],
  cancelled: [],
};

export default function FarmerOrdersPage() {
  return (
    <ProtectedRoute allowedRoles={["farmer"]}>
      <FarmerOrdersContent />
    </ProtectedRoute>
  );
}

function FarmerOrdersContent() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch farmer incoming orders
  const { data: orders = [], isLoading, error } = useQuery<Order[]>({
    queryKey: ["farmerOrders"],
    queryFn: async () => {
      const response = await api.get("/marketplace/orders");
      return response.data;
    }
  });

  const updateStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: FulfillmentStatus }) => {
      const response = await api.patch(`/marketplace/order-items/${id}/status`, { status });
      return response.data;
    },
    onSuccess: (data) => {
      toast(`Item status updated. Order is now ${data.status}.`, "success");
      queryClient.invalidateQueries({ queryKey: ["farmerOrders"] });
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Failed to update order status.";
      toast(msg, "error");
    }
  });

  const handleStatusUpdate = (id: string, nextStatus: FulfillmentStatus) => {
    updateStatusMutation.mutate({ id, status: nextStatus });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Marketplace Orders</h1>
        <p className="text-slate-500 text-sm mt-1">Accept incoming purchases and update fulfillment cycles</p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <Card key={i} className="animate-pulse h-[140px] bg-slate-200/50 rounded-xl" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl">
          <p className="text-red-500 font-medium">Failed to load orders. Please make sure the backend is active.</p>
        </div>
      ) : orders.length === 0 ? (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl max-w-2xl mx-auto">
          <ShoppingBag className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-800">No Orders Recieved</h3>
          <p className="text-slate-500 text-sm mt-1">Incoming orders from customers buying your crops will show up here.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {orders.map((order) => (
            <Card key={order.id} className="border border-slate-200/80 bg-white shadow-sm rounded-xl overflow-hidden">
              {/* Header metadata bar */}
              <div className="bg-slate-50 px-6 py-4 border-b border-slate-100 flex flex-wrap justify-between items-center gap-4">
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 font-medium">
                  <div className="flex items-center gap-1.5">
                    <Package className="h-4 w-4 text-emerald-600" />
                    <span>Order: <span className="font-semibold text-slate-800">{order.id.slice(0, 8)}...</span></span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Calendar className="h-4 w-4" />
                    <span>Placed: {new Date(order.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-800 font-bold bg-emerald-50 border border-emerald-200/50 px-2.5 py-0.5 rounded">
                    <DollarSign className="h-3.5 w-3.5 -mr-1 text-emerald-600" />
                    <span>Total: {order.total_amount.toFixed(2)}</span>
                  </div>
                </div>

                {/* Status Badge */}
                <div>
                  <span className={`text-xs uppercase font-extrabold tracking-wide px-3 py-1 rounded-full ${
                    order.status === "pending"
                      ? "bg-amber-100 text-amber-800 border border-amber-200"
                      : order.status === "accepted"
                      ? "bg-blue-100 text-blue-800 border border-blue-200"
                      : order.status === "ready"
                      ? "bg-purple-100 text-purple-800 border border-purple-200"
                      : order.status === "completed"
                      ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                      : "bg-red-100 text-red-800 border border-red-200"
                  }`}>
                    {order.status}
                  </span>
                </div>
              </div>

                <div className="p-6 flex flex-col gap-6">
                <div className="space-y-3 flex-grow">
                  <h4 className="text-xs font-bold text-slate-400 tracking-wider uppercase">Order Contents</h4>
                  <div className="space-y-3">
                    {order.items.map((item) => (
                      <div key={item.id} className="flex flex-col gap-3 rounded-lg border border-slate-100 bg-slate-50 p-3 sm:flex-row sm:items-center sm:justify-between">
                        <div className="text-sm text-slate-700 flex flex-wrap items-center gap-2">
                          <span className="font-semibold text-slate-900">Qty: {item.quantity}</span>
                          <span>x</span>
                          <span className="text-xs text-slate-400">Listing Reference ({item.crop_listing_id.slice(0, 8)})</span>
                          <span className="text-slate-400">@ ${item.price_at_purchase} / unit</span>
                          <span className="rounded-full bg-white px-2 py-0.5 text-[10px] font-bold uppercase text-slate-600">{item.status}</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {itemStatusActions[item.status].map((nextStatus) => (
                            <Button
                              key={nextStatus}
                              size="sm"
                              variant={nextStatus === "rejected" ? "outline" : "default"}
                              onClick={() => handleStatusUpdate(item.id, nextStatus)}
                              disabled={updateStatusMutation.isPending}
                              className={nextStatus === "rejected" ? "text-red-500 hover:bg-red-50 hover:border-red-200" : "bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold"}
                            >
                              Mark {nextStatus}
                            </Button>
                          ))}
                          {itemStatusActions[item.status].length === 0 && (
                            <span className="text-xs font-semibold text-slate-400 italic">No further actions</span>
                          )}
                        </div>
                      </div>
                    ))}
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
