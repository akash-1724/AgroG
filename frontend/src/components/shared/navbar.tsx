"use client";

import Link from "next/link";
import { useAuth } from "./auth-context";
import { useState } from "react";
import { Menu, X, Leaf, User as UserIcon, LogOut, ShoppingCart } from "lucide-react";

const advisoryLinks = [
  { href: "/recommendations/crop", label: "Crop Advisor" },
  { href: "/recommendations/fertilizer", label: "Fertilizer Planner" },
  { href: "/diagnostics/disease", label: "Disease Scanner" },
  { href: "/prices", label: "Market Prices" },
  { href: "/recommendations/history", label: "AI History" },
];

export function NavBar() {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center gap-2 text-emerald-400 font-bold text-xl">
              <Leaf className="h-6 w-6 text-emerald-500 fill-emerald-500/20" />
              <span>AgroGuide</span>
            </Link>
          </div>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center space-x-6">
            <Link href="/marketplace" className="text-slate-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition">
              Marketplace
            </Link>
            {advisoryLinks.map((link) => (
              <Link key={link.href} href={link.href} className="text-slate-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition">
                {link.label}
              </Link>
            ))}

            {user && (
              <>
                {user.role === "farmer" && (
                  <>
                    <Link href="/farmer/listings" className="text-slate-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition">
                      My Listings
                    </Link>
                    <Link href="/farmer/orders" className="text-slate-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition">
                      Farmer Orders
                    </Link>
                  </>
                )}
                {user.role === "admin" && (
                  <Link href="/admin/dashboard" className="text-slate-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition">
                    Admin Dashboard
                  </Link>
                )}
                {user.role === "customer" && (
                  <>
                    <Link href="/cart" className="text-slate-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition inline-flex items-center gap-1.5">
                      <ShoppingCart className="h-4 w-4" /> Cart
                    </Link>
                    <Link href="/orders" className="text-slate-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition">
                      My Orders
                    </Link>
                  </>
                )}
              </>
            )}
          </div>

          {/* User Profile / Auth Action Button */}
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              <div className="flex items-center gap-4">
                <Link href="/account" className="flex items-center gap-2 text-slate-300 hover:text-white transition text-sm">
                  <UserIcon className="h-4 w-4 text-emerald-400" />
                  <span className="font-medium text-slate-200">{user.full_name || user.email}</span>
                  <span className="text-xs uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded">
                    {user.role}
                  </span>
                </Link>
                <button
                  onClick={logout}
                  className="flex items-center gap-1.5 bg-slate-800 hover:bg-red-900/40 hover:text-red-400 border border-slate-700 hover:border-red-900/50 px-3 py-1.5 rounded-lg text-sm transition"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Log Out</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/login" className="text-slate-300 hover:text-white transition text-sm font-medium">
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-4 py-2 rounded-lg text-sm font-semibold transition"
                >
                  Register
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none"
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      {isOpen && (
        <div className="md:hidden bg-slate-950 border-b border-slate-800 px-2 pt-2 pb-4 space-y-1 sm:px-3">
          <Link
            href="/marketplace"
            onClick={() => setIsOpen(false)}
            className="block text-slate-300 hover:text-white px-3 py-2 rounded-md text-base font-medium"
          >
            Marketplace
          </Link>
          {advisoryLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setIsOpen(false)}
              className="block text-slate-300 hover:text-white px-3 py-2 rounded-md text-base font-medium"
            >
              {link.label}
            </Link>
          ))}

          {user && (
            <>
              {user.role === "farmer" && (
                <>
                  <Link
                    href="/farmer/listings"
                    onClick={() => setIsOpen(false)}
                    className="block text-slate-300 hover:text-white px-3 py-2 rounded-md text-base font-medium"
                  >
                    My Listings
                  </Link>
                  <Link
                    href="/farmer/orders"
                    onClick={() => setIsOpen(false)}
                    className="block text-slate-300 hover:text-white px-3 py-2 rounded-md text-base font-medium"
                  >
                    Farmer Orders
                  </Link>
                </>
              )}
              {user.role === "customer" && (
                <>
                  <Link
                    href="/cart"
                    onClick={() => setIsOpen(false)}
                    className="flex items-center gap-2 text-slate-300 hover:text-white px-3 py-2 rounded-md text-base font-medium"
                  >
                    <ShoppingCart className="h-5 w-5" /> Cart
                  </Link>
                  <Link
                    href="/orders"
                    onClick={() => setIsOpen(false)}
                    className="block text-slate-300 hover:text-white px-3 py-2 rounded-md text-base font-medium"
                  >
                    My Orders
                  </Link>
                </>
              )}
              {user.role === "admin" && (
                <Link
                  href="/admin/dashboard"
                  onClick={() => setIsOpen(false)}
                  className="block text-slate-300 hover:text-white px-3 py-2 rounded-md text-base font-medium"
                >
                  Admin Dashboard
                </Link>
              )}
              <div className="border-t border-slate-800 my-2 pt-2" />
              <Link
                href="/account"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-2 text-slate-300 hover:text-white px-3 py-2 rounded-md text-base font-medium"
              >
                <UserIcon className="h-5 w-5 text-emerald-400" />
                <span>Account ({user.role})</span>
              </Link>
              <button
                onClick={() => {
                  setIsOpen(false);
                  logout();
                }}
                className="w-full flex items-center gap-2 text-left text-red-400 hover:bg-red-950/20 px-3 py-2 rounded-md text-base font-medium"
              >
                <LogOut className="h-5 w-5" />
                <span>Log Out</span>
              </button>
            </>
          )}

          {!user && (
            <div className="grid grid-cols-2 gap-2 pt-2 px-3">
              <Link
                href="/login"
                onClick={() => setIsOpen(false)}
                className="flex items-center justify-center border border-slate-700 text-slate-300 hover:text-white py-2 rounded-lg text-sm font-medium"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                onClick={() => setIsOpen(false)}
                className="flex items-center justify-center bg-emerald-500 text-slate-950 hover:bg-emerald-400 py-2 rounded-lg text-sm font-semibold"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
}
