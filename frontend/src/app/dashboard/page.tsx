"use client";

import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { 
  LayoutDashboard, ShoppingBag, Sprout, BookOpen, 
  Plus, Check, X, Truck, LogOut, Loader2, Trash2 
} from "lucide-react";

import { useAuth } from "@/components/shared/auth-context";
import { api } from "@/lib/api";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { useToast } from "@/components/ui/toast";

interface DashboardOrder {
  id: string;
  customer_id: string;
  status: string;
  total_amount: number;
  created_at: string;
  items?: {
    crop_listing_id: string;
    quantity: number;
    price_at_purchase: number;
  }[];
}

interface DashboardListing {
  id: string;
  farmer_id: string;
  title: string;
  description: string;
  price_per_unit: number;
  unit: string;
  available_quantity: number;
  status: string;
}

interface DashboardArticle {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
}

export default function UnifiedDashboard() {
  const router = useRouter();
  const { user, logout, isLoading: authLoading } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = React.useState<string>("overview");
  const [showAddListingModal, setShowAddListingModal] = React.useState(false);
  const [showAddArticleModal, setShowAddArticleModal] = React.useState(false);

  // Form states for Listing creation
  const [listingTitle, setListingTitle] = React.useState("");
  const [listingDesc, setListingDesc] = React.useState("");
  const [listingPrice, setListingPrice] = React.useState(0);
  const [listingUnit, setListingUnit] = React.useState("kg");
  const [listingQty, setListingQty] = React.useState(100);

  // Form states for Article creation
  const [articleTitle, setArticleTitle] = React.useState("");
  const [articleContent, setArticleContent] = React.useState("");
  const [articleCategory, setArticleCategory] = React.useState("Guides");

  // Protect route
  React.useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  // Fetch orders (For Customer/Farmer/Admin)
  const { data: orders = [], isLoading: ordersLoading } = useQuery<DashboardOrder[]>({
    queryKey: ["dashboardOrders"],
    queryFn: async () => {
      const response = await api.get("/marketplace/orders");
      return response.data;
    },
    enabled: !!user,
  });

  // Fetch all crop listings (Farmers can view/manage their listings, admins see all)
  const { data: listings = [], isLoading: listingsLoading } = useQuery<DashboardListing[]>({
    queryKey: ["dashboardListings"],
    queryFn: async () => {
      const response = await api.get("/marketplace");
      return response.data;
    },
    enabled: !!user,
  });

  // Fetch educational articles (For Admin CMS)
  const { data: articles = [], isLoading: articlesLoading } = useQuery<DashboardArticle[]>({
    queryKey: ["dashboardArticles"],
    queryFn: async () => {
      const response = await api.get("/educational");
      return response.data;
    },
    enabled: !!user && user.role === "admin",
  });

  // Create listing mutation
  const createListingMutation = useMutation({
    mutationFn: async (payload: Omit<DashboardListing, "id" | "farmer_id">) => {
      return await api.post("/marketplace/listings", payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboardListings"] });
      toast({ title: "Listing Created", description: "Your crop listing has been published." });
      setShowAddListingModal(false);
      // Reset form
      setListingTitle("");
      setListingDesc("");
      setListingPrice(0);
      setListingQty(100);
    },
    onError: (err: unknown) => {
      const errMsg = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Failed to create listing.";
      toast({ title: "Error", description: errMsg, variant: "destructive" });
    },
  });

  // Delete listing mutation
  const deleteListingMutation = useMutation({
    mutationFn: async (id: string) => {
      return await api.delete(`/marketplace/listings/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboardListings"] });
      toast({ title: "Listing Removed", description: "Crop listing was successfully deleted." });
    },
    onError: () => {
      toast({ title: "Error", description: "You must initialize a Farmer Profile or own this listing.", variant: "destructive" });
    },
  });

  // Create article mutation
  const createArticleMutation = useMutation({
    mutationFn: async (payload: Omit<DashboardArticle, "id">) => {
      return await api.post("/educational", payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboardArticles"] });
      toast({ title: "Article Published", description: "The educational material is now live." });
      setShowAddArticleModal(false);
      setArticleTitle("");
      setArticleContent("");
    },
    onError: () => {
      toast({ title: "Error", description: "Failed to create article.", variant: "destructive" });
    },
  });

  // Delete article mutation
  const deleteArticleMutation = useMutation({
    mutationFn: async (id: string) => {
      return await api.delete(`/educational/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboardArticles"] });
      toast({ title: "Article Removed", description: "Article deleted from CMS." });
    },
  });

  // Update order status mutation
  const updateOrderStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => {
      return await api.patch(`/marketplace/orders/${id}`, { status });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboardOrders"] });
      toast({ title: "Order Updated", description: "Order status was updated successfully." });
    },
    onError: (err: unknown) => {
      toast({ title: "Error", description: "Failed to update order status.", variant: "destructive" });
    },
  });

  if (authLoading || !user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-3">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground text-sm font-medium">Validating dashboard credentials...</p>
      </div>
    );
  }

  // Filter listings for farmer
  const farmerListings = user.role === "farmer" 
    ? listings.filter((item) => item.farmer_id === user.id) 
    : listings;

  return (
    <div className="min-h-screen flex bg-zinc-50/50">
      {/* Sidebar navigation */}
      <aside className="w-64 bg-white border-r border-zinc-200 hidden md:flex flex-col justify-between p-6">
        <div className="space-y-6">
          <div className="flex items-center gap-2 px-2">
            <Sprout className="h-6 w-6 text-primary" />
            <span className="font-extrabold text-xl tracking-tight text-primary">AgroGuide</span>
          </div>

          <div className="h-px bg-zinc-100" />

          {/* User Profile Info */}
          <div className="flex items-center gap-3 bg-zinc-100/50 p-3 rounded-xl">
            <div className="h-10 w-10 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold">
              {user.full_name[0].toUpperCase()}
            </div>
            <div className="overflow-hidden">
              <h4 className="text-sm font-bold text-zinc-900 truncate">{user.full_name}</h4>
              <p className="text-[10px] font-semibold tracking-wider text-primary uppercase mt-0.5">{user.role}</p>
            </div>
          </div>

          <nav className="space-y-1">
            <button
              onClick={() => setActiveTab("overview")}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-bold transition-all ${
                activeTab === "overview" ? "bg-primary text-white shadow-sm" : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
              }`}
            >
              <LayoutDashboard className="h-4 w-4" /> Overview
            </button>

            {user.role === "farmer" && (
              <>
                <button
                  onClick={() => setActiveTab("listings")}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-bold transition-all ${
                    activeTab === "listings" ? "bg-primary text-white shadow-sm" : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                  }`}
                >
                  <Sprout className="h-4 w-4" /> My Crop Listings
                </button>
                <button
                  onClick={() => setActiveTab("orders")}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-bold transition-all ${
                    activeTab === "orders" ? "bg-primary text-white shadow-sm" : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                  }`}
                >
                  <ShoppingBag className="h-4 w-4" /> Received Orders
                </button>
              </>
            )}

            {user.role === "customer" && (
              <button
                onClick={() => setActiveTab("orders")}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-bold transition-all ${
                  activeTab === "orders" ? "bg-primary text-white shadow-sm" : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                }`}
              >
                <ShoppingBag className="h-4 w-4" /> My Purchases
              </button>
            )}

            {user.role === "admin" && (
              <button
                onClick={() => setActiveTab("articles")}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-bold transition-all ${
                  activeTab === "articles" ? "bg-primary text-white shadow-sm" : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                }`}
              >
                <BookOpen className="h-4 w-4" /> Educational CMS
              </button>
            )}
          </nav>
        </div>

        <Button 
          onClick={() => {
            logout();
            router.push("/login");
          }} 
          variant="outline" 
          className="w-full flex items-center justify-center gap-2 border-zinc-200 font-bold"
        >
          <LogOut className="h-4 w-4" /> Log Out
        </Button>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-6 sm:p-10 overflow-y-auto">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-extrabold tracking-tight text-primary capitalize">{activeTab} Dashboard</h2>
            <p className="text-muted-foreground text-sm">Welcome back, {user.full_name}</p>
          </div>
          
          {user.role === "farmer" && activeTab === "listings" && (
            <Button onClick={() => setShowAddListingModal(true)} className="font-bold flex items-center gap-2 shadow-sm">
              <Plus className="h-4 w-4" /> Add Crop Listing
            </Button>
          )}

          {user.role === "admin" && activeTab === "articles" && (
            <Button onClick={() => setShowAddArticleModal(true)} className="font-bold flex items-center gap-2 shadow-sm">
              <Plus className="h-4 w-4" /> Write Article
            </Button>
          )}
        </header>

        {/* Tab 1: Overview Panel */}
        {activeTab === "overview" && (
          <div className="space-y-6 animate-in fade-in-50 duration-200">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <Card className="border-secondary/20 shadow-sm">
                <CardHeader className="pb-2">
                  <CardDescription className="text-xs font-semibold uppercase">Account Role</CardDescription>
                  <CardTitle className="text-2xl font-black text-primary capitalize">{user.role}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">Access controls and dashboard actions are dynamic.</p>
                </CardContent>
              </Card>

              <Card className="border-secondary/20 shadow-sm">
                <CardHeader className="pb-2">
                  <CardDescription className="text-xs font-semibold uppercase">Active Orders</CardDescription>
                  <CardTitle className="text-2xl font-black text-primary">{orders.length}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">Orders involving your registered account profile.</p>
                </CardContent>
              </Card>

              {user.role === "farmer" && (
                <Card className="border-secondary/20 shadow-sm">
                  <CardHeader className="pb-2">
                    <CardDescription className="text-xs font-semibold uppercase">My Listings</CardDescription>
                    <CardTitle className="text-2xl font-black text-primary">{farmerListings.length}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-xs text-muted-foreground">Crops currently posted on public marketplace.</p>
                  </CardContent>
                </Card>
              )}
            </div>

            <Card className="border-secondary/20 shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg font-bold">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-wrap gap-4">
                <Link href="/marketplace">
                  <Button variant="outline" className="font-bold">Browse Marketplace</Button>
                </Link>
                <Link href="/recommendations/crop">
                  <Button variant="outline" className="font-bold">Soil Crop Predictor</Button>
                </Link>
                <Link href="/recommendations/fertilizer">
                  <Button variant="outline" className="font-bold">Fertilizer prescription</Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Tab 2: My Crop Listings (Farmer only) */}
        {activeTab === "listings" && user.role === "farmer" && (
          <div className="space-y-6 animate-in fade-in-50 duration-200">
            {listingsLoading ? (
              <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
            ) : farmerListings.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-xl border border-zinc-200">
                <p className="text-muted-foreground font-semibold">You haven&apos;t posted any crop listings yet.</p>
                <Button onClick={() => setShowAddListingModal(true)} className="mt-4 font-bold flex items-center gap-2 mx-auto">
                  <Plus className="h-4 w-4" /> Create First Listing
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {farmerListings.map((item) => (
                  <Card key={item.id} className="flex flex-col justify-between hover:shadow-md transition-shadow">
                    <CardHeader>
                      <CardTitle className="text-base font-bold line-clamp-1">{item.title}</CardTitle>
                      <CardDescription className="text-xs line-clamp-2">{item.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="pb-4 pt-0">
                      <div className="flex justify-between items-baseline">
                        <span className="text-primary font-black">${item.price_per_unit} / {item.unit}</span>
                        <span className="text-xs text-muted-foreground font-medium">Stock: {item.available_quantity}</span>
                      </div>
                    </CardContent>
                    <CardFooter className="bg-zinc-50 border-t border-zinc-100 rounded-b-xl px-4 py-3 flex justify-end">
                      <Button
                        onClick={() => deleteListingMutation.mutate(item.id)}
                        disabled={deleteListingMutation.isPending}
                        variant="destructive"
                        size="sm"
                        className="flex items-center gap-2 font-semibold"
                      >
                        <Trash2 className="h-4 w-4" /> Delete
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Orders Board (Customer & Farmer) */}
        {activeTab === "orders" && (
          <div className="space-y-6 animate-in fade-in-50 duration-200">
            {ordersLoading ? (
              <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
            ) : orders.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-xl border border-zinc-200">
                <p className="text-muted-foreground font-semibold">No orders found.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {orders.map((order) => (
                  <Card key={order.id} className="border-secondary/20 shadow-sm hover:shadow-md transition-shadow">
                    <CardHeader className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 pb-3">
                      <div>
                        <CardTitle className="text-sm font-extrabold tracking-wide uppercase text-zinc-500">Order ID: {order.id.slice(0, 8)}</CardTitle>
                        <CardDescription className="text-xs mt-0.5">Created at: {new Date(order.created_at).toLocaleDateString()}</CardDescription>
                      </div>
                      <div>
                        <span className={`px-2.5 py-1 rounded-full text-xs font-bold capitalize ${
                          order.status === "completed"
                            ? "bg-emerald-100 text-emerald-800"
                            : order.status === "shipped"
                            ? "bg-sky-100 text-sky-800"
                            : order.status === "cancelled"
                            ? "bg-red-100 text-red-800"
                            : "bg-amber-100 text-amber-800 animate-pulse"
                        }`}>
                          {order.status}
                        </span>
                      </div>
                    </CardHeader>
                    <CardContent className="pb-4">
                      <div className="space-y-3">
                        <div className="text-sm font-bold text-zinc-800">Order Amount: <span className="text-primary font-black">${order.total_amount.toFixed(2)}</span></div>
                        <div className="border border-zinc-100 rounded-lg overflow-hidden">
                          <table className="min-w-full divide-y divide-zinc-200 text-xs text-left">
                            <thead className="bg-zinc-50">
                              <tr>
                                <th className="px-4 py-2 font-bold text-zinc-600">Crop ID</th>
                                <th className="px-4 py-2 font-bold text-zinc-600">Qty Ordered</th>
                                <th className="px-4 py-2 font-bold text-zinc-600">Price At Purchase</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-zinc-200 bg-white">
                              {order.items?.map((item: { crop_listing_id: string; quantity: number; price_at_purchase: number }) => (
                                <tr key={item.crop_listing_id}>
                                  <td className="px-4 py-2 font-mono">{item.crop_listing_id.slice(0, 8)}</td>
                                  <td className="px-4 py-2">{item.quantity}</td>
                                  <td className="px-4 py-2">${item.price_at_purchase}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </CardContent>
                    
                    {/* Role specific order actions */}
                    {order.status === "pending" && (
                      <CardFooter className="bg-zinc-50 border-t border-zinc-100 rounded-b-xl px-6 py-3 flex justify-end gap-3">
                        {user.role === "farmer" && (
                          <>
                            <Button
                              onClick={() => updateOrderStatusMutation.mutate({ id: order.id, status: "shipped" })}
                              variant="outline"
                              size="sm"
                              className="flex items-center gap-1.5 font-bold"
                            >
                              <Truck className="h-3.5 w-3.5" /> Ship Order
                            </Button>
                            <Button
                              onClick={() => updateOrderStatusMutation.mutate({ id: order.id, status: "cancelled" })}
                              variant="destructive"
                              size="sm"
                              className="flex items-center gap-1.5 font-bold"
                            >
                              <X className="h-3.5 w-3.5" /> Reject Order
                            </Button>
                          </>
                        )}
                        {user.role === "customer" && (
                          <Button
                            onClick={() => updateOrderStatusMutation.mutate({ id: order.id, status: "cancelled" })}
                            variant="destructive"
                            size="sm"
                            className="flex items-center gap-1.5 font-bold"
                          >
                            <X className="h-3.5 w-3.5" /> Cancel Order
                          </Button>
                        )}
                      </CardFooter>
                    )}

                    {order.status === "shipped" && user.role === "farmer" && (
                      <CardFooter className="bg-zinc-50 border-t border-zinc-100 rounded-b-xl px-6 py-3 flex justify-end">
                        <Button
                          onClick={() => updateOrderStatusMutation.mutate({ id: order.id, status: "completed" })}
                          size="sm"
                          className="flex items-center gap-1.5 font-bold"
                        >
                          <Check className="h-3.5 w-3.5" /> Mark Completed
                        </Button>
                      </CardFooter>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 4: Admin CMS Articles (Admin only) */}
        {activeTab === "articles" && user.role === "admin" && (
          <div className="space-y-6 animate-in fade-in-50 duration-200">
            {articlesLoading ? (
              <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
            ) : articles.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-xl border border-zinc-200">
                <p className="text-muted-foreground font-semibold">No educational articles found in system database.</p>
                <Button onClick={() => setShowAddArticleModal(true)} className="mt-4 font-bold flex items-center gap-2 mx-auto">
                  <Plus className="h-4 w-4" /> Create First Article
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {articles.map((art) => (
                  <Card key={art.id} className="border-secondary/20 shadow-sm flex flex-col justify-between">
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg font-bold">{art.title}</CardTitle>
                          <CardDescription className="text-xs font-semibold text-primary uppercase mt-0.5">{art.category}</CardDescription>
                        </div>
                        <Button
                          onClick={() => deleteArticleMutation.mutate(art.id)}
                          variant="ghost"
                          size="icon"
                          className="text-destructive hover:bg-destructive/10"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="pb-4">
                      <p className="text-sm text-zinc-600 line-clamp-3 leading-relaxed">{art.content}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* MODAL 1: Create Crop Listing (Farmer only) */}
      {showAddListingModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-lg shadow-2xl animate-in zoom-in-95 duration-150">
            <CardHeader className="flex flex-row justify-between items-center border-b border-zinc-100 pb-4">
              <div>
                <CardTitle className="text-lg font-extrabold text-primary">New Crop Listing</CardTitle>
                <CardDescription>Advertise your crop inventory on the public catalog.</CardDescription>
              </div>
              <Button onClick={() => setShowAddListingModal(false)} variant="ghost" size="icon" className="rounded-full">
                <X className="h-5 w-5" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              <div className="space-y-1">
                <label className="text-xs font-bold text-zinc-500 uppercase">Crop Title</label>
                <Input value={listingTitle} onChange={(e) => setListingTitle(e.target.value)} placeholder="e.g. Organic Winter Wheat" />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-bold text-zinc-500 uppercase">Description</label>
                <textarea
                  value={listingDesc}
                  onChange={(e) => setListingDesc(e.target.value)}
                  placeholder="Provide harvest details, crop quality, location etc."
                  className="w-full min-h-[80px] text-sm rounded-lg border border-zinc-200 p-3 bg-white focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-bold text-zinc-500 uppercase">Price per unit ($)</label>
                  <Input type="number" step="0.01" value={listingPrice} onChange={(e) => setListingPrice(parseFloat(e.target.value) || 0)} />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-bold text-zinc-500 uppercase">Measurement Unit</label>
                  <Select defaultValue="kg" onValueChange={setListingUnit}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="kg">Kilograms (kg)</SelectItem>
                      <SelectItem value="lbs">Pounds (lbs)</SelectItem>
                      <SelectItem value="ton">Tons</SelectItem>
                      <SelectItem value="bag">Bags</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-bold text-zinc-500 uppercase">Available Inventory Quantity</label>
                <Input type="number" value={listingQty} onChange={(e) => setListingQty(parseInt(e.target.value) || 0)} />
              </div>
            </CardContent>
            <CardFooter className="border-t border-zinc-100 pt-4 flex justify-end gap-3">
              <Button onClick={() => setShowAddListingModal(false)} variant="outline" className="font-semibold">Cancel</Button>
              <Button
                onClick={() => {
                  createListingMutation.mutate({
                    title: listingTitle,
                    description: listingDesc,
                    price_per_unit: listingPrice,
                    unit: listingUnit,
                    available_quantity: listingQty,
                    status: "active",
                  });
                }}
                disabled={createListingMutation.isPending || !listingTitle}
                className="font-bold"
              >
                {createListingMutation.isPending ? "Publishing..." : "Publish Listing"}
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}

      {/* MODAL 2: Create Article (Admin only) */}
      {showAddArticleModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-lg shadow-2xl animate-in zoom-in-95 duration-150">
            <CardHeader className="flex flex-row justify-between items-center border-b border-zinc-100 pb-4">
              <div>
                <CardTitle className="text-lg font-extrabold text-primary">New Educational Article</CardTitle>
                <CardDescription>Write tutorials, crop disease tips, or farming guidance material.</CardDescription>
              </div>
              <Button onClick={() => setShowAddArticleModal(false)} variant="ghost" size="icon" className="rounded-full">
                <X className="h-5 w-5" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              <div className="space-y-1">
                <label className="text-xs font-bold text-zinc-500 uppercase">Article Title</label>
                <Input value={articleTitle} onChange={(e) => setArticleTitle(e.target.value)} placeholder="e.g. Modern Crop Rotation Methods" />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-bold text-zinc-500 uppercase">Article Content</label>
                <textarea
                  value={articleContent}
                  onChange={(e) => setArticleContent(e.target.value)}
                  placeholder="Draft the article markdown or body text here..."
                  className="w-full min-h-[160px] text-sm rounded-lg border border-zinc-200 p-3 bg-white focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-bold text-zinc-500 uppercase">Category</label>
                <Select defaultValue="Guides" onValueChange={setArticleCategory}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Guides">Farming Guides</SelectItem>
                    <SelectItem value="Pests">Pests & Diseases</SelectItem>
                    <SelectItem value="Economics">Market Economics</SelectItem>
                    <SelectItem value="Fertilizers">Fertilizers & Nutrients</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
            <CardFooter className="border-t border-zinc-100 pt-4 flex justify-end gap-3">
              <Button onClick={() => setShowAddArticleModal(false)} variant="outline" className="font-semibold">Cancel</Button>
              <Button
                onClick={() => {
                  createArticleMutation.mutate({
                    title: articleTitle,
                    content: articleContent,
                    category: articleCategory,
                    tags: [articleCategory.toLowerCase()],
                  });
                }}
                disabled={createArticleMutation.isPending || !articleTitle || !articleContent}
                className="font-bold"
              >
                {createArticleMutation.isPending ? "Publishing..." : "Publish Article"}
              </Button>
            </CardFooter>
          </Card>
        </div>
      )}
    </div>
  );
}
