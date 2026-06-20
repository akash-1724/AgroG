"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { ChevronRight, XOctagon, Calendar, ClipboardList } from "lucide-react";

import ProtectedRoute from "@/components/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { api } from "@/lib/api";

interface OrderItem {
  id: string;
  order_id: string;
  crop_listing_id: string;
  quantity: number;
  price_at_purchase: number;
  status: "pending" | "accepted" | "ready" | "completed" | "rejected" | "cancelled";
}

interface Order {
  id: string;
  customer_id: string;
  status: "pending" | "accepted" | "ready" | "completed" | "rejected" | "cancelled";
  total_amount: number;
  created_at: string;
  items: OrderItem[];
}

export default function CustomerOrdersPage() {
  return (
    <ProtectedRoute allowedRoles={["customer"]}>
      <CustomerOrdersContent />
    </ProtectedRoute>
  );
}

function CustomerOrdersContent() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [reviewingItemId, setReviewingItemId] = React.useState<string | null>(null);
  const [reviewRating, setReviewRating] = React.useState(5);
  const [reviewComment, setReviewComment] = React.useState("");

  // Fetch customer orders
  const { data: orders = [], isLoading, error } = useQuery<Order[]>({
    queryKey: ["customerOrders"],
    queryFn: async () => {
      const response = await api.get("/marketplace/orders");
      return response.data;
    }
  });

  // Cancel order mutation (customer allowed to cancel pending orders)
  const cancelOrderMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await api.patch(`/marketplace/orders/${id}`, { status: "cancelled" });
      return response.data;
    },
    onSuccess: () => {
      toast("Order has been cancelled successfully.", "success");
      queryClient.invalidateQueries({ queryKey: ["customerOrders"] });
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Failed to cancel order.";
      toast(msg, "error");
    }
  });

  const createReviewMutation = useMutation({
    mutationFn: async (payload: { rating: number; comment: string; listing_id: string; order_item_id: string }) => {
      const response = await api.post("/reviews", payload);
      return response.data;
    },
    onSuccess: () => {
      toast("Review submitted successfully.", "success");
      setReviewingItemId(null);
      setReviewRating(5);
      setReviewComment("");
      queryClient.invalidateQueries({ queryKey: ["customerOrders"] });
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Failed to submit review.";
      toast(msg, "error");
    },
  });

  const handleSubmitReview = (item: OrderItem) => {
    if (reviewComment.trim().length < 3) {
      toast("Review comment must be at least 3 characters.", "error");
      return;
    }
    createReviewMutation.mutate({
      rating: reviewRating,
      comment: reviewComment.trim(),
      listing_id: item.crop_listing_id,
      order_item_id: item.id,
    });
  };

  const handleCancelOrder = (id: string) => {
    if (confirm("Are you sure you want to cancel this order? This will restore crop listing stock immediately.")) {
      cancelOrderMutation.mutate(id);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">My Orders</h1>
          <p className="text-slate-500 text-sm mt-1">Track crop order progress and purchase receipts</p>
        </div>
        <Link href="/marketplace">
          <Button variant="outline" className="flex items-center gap-1">
            Back to Shop <ChevronRight className="h-4 w-4" />
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <Card key={i} className="animate-pulse h-[120px] bg-slate-200/50 rounded-xl" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl">
          <p className="text-red-500 font-medium">Failed to load orders. Please make sure the backend is active.</p>
        </div>
      ) : orders.length === 0 ? (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl max-w-xl mx-auto">
          <ClipboardList className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-800">No Orders Placed Yet</h3>
          <p className="text-slate-500 text-sm mt-1">Crops you buy from the marketplace will show up here.</p>
          <Link href="/marketplace" className="mt-4 inline-block">
            <Button className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold">
              Shop Marketplace
            </Button>
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Card key={order.id} className="border border-slate-200/80 bg-white shadow-sm rounded-xl overflow-hidden">
              <div className="p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                {/* Details */}
                <div className="space-y-3">
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="text-sm font-bold text-slate-900">
                      Order: #{order.id.slice(0, 8)}
                    </span>
                    <span className="text-xs text-slate-400 flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {new Date(order.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Items list */}
                  <div className="space-y-1 pl-1 border-l-2 border-emerald-500">
                    {order.items.map((item) => (
                      <div key={item.id} className="text-xs text-slate-600 space-y-2 py-1">
                        <div>
                          Listing Ref: <Link className="underline" href={`/marketplace/${item.crop_listing_id}`}>{item.crop_listing_id.slice(0, 8)}</Link> —{" "}
                          <span className="font-semibold text-slate-800">
                            Qty: {item.quantity}
                          </span>{" "}
                          @ ${item.price_at_purchase}
                          <span className="ml-2 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold uppercase text-slate-600">{item.status}</span>
                        </div>
                        {item.status === "completed" && (
                          <div className="space-y-2 rounded-lg border border-slate-200 bg-slate-50 p-3">
                            {reviewingItemId === item.id ? (
                              <>
                                <div className="flex flex-col sm:flex-row gap-2">
                                  <select
                                    value={reviewRating}
                                    onChange={(event) => setReviewRating(Number(event.target.value))}
                                    className="rounded-md border border-slate-200 bg-white px-2 py-2 text-sm"
                                  >
                                    {[5, 4, 3, 2, 1].map((rating) => (
                                      <option key={rating} value={rating}>{rating} stars</option>
                                    ))}
                                  </select>
                                  <Input
                                    value={reviewComment}
                                    onChange={(event) => setReviewComment(event.target.value)}
                                    placeholder="Write a short review"
                                    className="text-sm"
                                  />
                                </div>
                                <div className="flex gap-2">
                                  <Button size="sm" onClick={() => handleSubmitReview(item)} disabled={createReviewMutation.isPending}>Submit Review</Button>
                                  <Button size="sm" variant="outline" onClick={() => setReviewingItemId(null)}>Cancel</Button>
                                </div>
                              </>
                            ) : (
                              <Button size="sm" variant="outline" onClick={() => setReviewingItemId(item.id)}>Review this purchase</Button>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="text-sm font-extrabold text-slate-900">
                    Total Amount: ${order.total_amount.toFixed(2)}
                  </div>
                </div>

                {/* Status and Action Cancel button */}
                <div className="flex flex-col sm:flex-row md:flex-col items-start md:items-end gap-3 self-stretch md:self-auto justify-between md:justify-center">
                  <span className={`text-xs uppercase font-extrabold tracking-wide px-3 py-1 rounded-full border ${
                    order.status === "pending"
                      ? "bg-amber-50 text-amber-700 border-amber-200"
                      : order.status === "accepted"
                      ? "bg-blue-50 text-blue-700 border-blue-200"
                      : order.status === "ready"
                      ? "bg-purple-50 text-purple-700 border-purple-200"
                      : order.status === "completed"
                      ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                      : "bg-slate-100 text-slate-700 border-slate-200"
                  }`}>
                    {order.status}
                  </span>

                  {order.status === "pending" && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleCancelOrder(order.id)}
                      disabled={cancelOrderMutation.isPending}
                      className="text-red-500 hover:bg-red-50 hover:border-red-150 border-red-200/50 flex items-center gap-1.5"
                    >
                      <XOctagon className="h-4 w-4" /> Cancel Order
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
