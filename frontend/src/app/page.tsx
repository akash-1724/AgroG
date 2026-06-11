import Link from "next/link";
import { ArrowRight, Leaf, ShoppingBag, ShieldCheck, Users, TrendingUp, HelpCircle } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-emerald-900 via-emerald-800 to-teal-950 py-24 px-6 md:px-12 text-white">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,rgba(16,185,129,0.1),transparent)]" />
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center relative z-10">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-sm font-medium">
              <Leaf className="h-4 w-4" /> Smart Agriculture Ecosystem
            </div>
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight leading-tight">
              Bridging the Gap Between <span className="text-emerald-400">Farmers</span> and Consumers
            </h1>
            <p className="text-lg text-slate-200 max-w-xl">
              AgroGuide empowers farmers to showcase their premium crops directly to customers. Experience transparent pricing, verified farmers, and fresh products.
            </p>
            <div className="flex flex-wrap gap-4 pt-4">
              <Link
                href="/marketplace"
                className="inline-flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold px-6 py-3 rounded-lg shadow-lg hover:shadow-emerald-500/20 transition duration-300"
              >
                Browse Marketplace <ShoppingBag className="h-5 w-5" />
              </Link>
              <Link
                href="/register"
                className="inline-flex items-center gap-2 bg-slate-900/60 hover:bg-slate-900/80 border border-slate-700 text-white font-medium px-6 py-3 rounded-lg transition duration-300"
              >
                Join as a Farmer <ArrowRight className="h-5 w-5" />
              </Link>
            </div>
          </div>
          <div className="hidden md:block relative">
            <div className="aspect-[4/3] rounded-2xl bg-emerald-950/40 border border-emerald-500/20 shadow-2xl overflow-hidden flex items-center justify-center p-8">
              <div className="space-y-6 w-full">
                <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800 flex items-center gap-4">
                  <div className="p-3 rounded-lg bg-emerald-500/20 text-emerald-400">
                    <TrendingUp className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-100 text-sm">Direct Farm Sales</h3>
                    <p className="text-xs text-slate-400">Eliminate middlemen, keep 100% crop price profits.</p>
                  </div>
                </div>
                <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800 flex items-center gap-4">
                  <div className="p-3 rounded-lg bg-emerald-500/20 text-emerald-400">
                    <ShieldCheck className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-100 text-sm">Secure RBAC Authentication</h3>
                    <p className="text-xs text-slate-400">Safe logins for customers, farmers, and administrative staff.</p>
                  </div>
                </div>
                <div className="bg-slate-900/80 rounded-xl p-4 border border-slate-800 flex items-center gap-4">
                  <div className="p-3 rounded-lg bg-emerald-500/20 text-emerald-400">
                    <Users className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-100 text-sm">Active Farmer Community</h3>
                    <p className="text-xs text-slate-400">Discover local growers and support high-quality agriculture.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section className="py-20 px-6 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center text-slate-900 mb-12">
          Why Choose AgroGuide?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-xl border border-slate-200/80 shadow-sm space-y-4 hover:shadow-md transition">
            <div className="inline-flex p-3 rounded-lg bg-emerald-100 text-emerald-700">
              <ShoppingBag className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-950">Direct Marketplace</h3>
            <p className="text-slate-600">
              Customers can discover crop listings in real-time, view verified farmer info, and place orders directly.
            </p>
          </div>
          <div className="bg-white p-8 rounded-xl border border-slate-200/80 shadow-sm space-y-4 hover:shadow-md transition">
            <div className="inline-flex p-3 rounded-lg bg-emerald-100 text-emerald-700">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-950">Verified Transactions</h3>
            <p className="text-slate-600">
              Transparent states for orders. Farmers approve, ship, and complete order cycles with robust checks.
            </p>
          </div>
          <div className="bg-white p-8 rounded-xl border border-slate-200/80 shadow-sm space-y-4 hover:shadow-md transition">
            <div className="inline-flex p-3 rounded-lg bg-emerald-100 text-emerald-700">
              <Users className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-950">Farmer Showcases</h3>
            <p className="text-slate-600">
              Growers can easily manage their catalogs, update pricing, describe farming practices, and track orders.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-slate-900 text-white py-16 px-6 md:px-12 text-center rounded-2xl max-w-6xl mx-auto mb-20 relative overflow-hidden">
        <div className="max-w-2xl mx-auto space-y-6 relative z-10">
          <h2 className="text-3xl md:text-4xl font-bold">Ready to Elevate Your Agriculture Trade?</h2>
          <p className="text-slate-300">
            Sign up now as a customer to buy high-quality organic crops, or join as a farmer to boost your distribution.
          </p>
          <div className="flex justify-center gap-4 pt-4">
            <Link
              href="/register"
              className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold px-6 py-3 rounded-lg transition"
            >
              Get Started
            </Link>
            <Link
              href="/login"
              className="bg-slate-800 hover:bg-slate-700 text-white font-medium px-6 py-3 rounded-lg border border-slate-700 transition"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
