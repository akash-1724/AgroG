"use client";

import * as React from "react";
import { api } from "@/lib/api";

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone_number?: string;
  role: "customer" | "farmer" | "admin";
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (tokenData: { access_token: string; refresh_token: string }) => Promise<void>;
  logout: () => void;
  fetchProfile: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  const fetchProfile = React.useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    
    try {
      // Decode JWT token directly on client for immediate role matching
      const parts = token.split(".");
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        setUser({
          id: payload.sub,
          email: "", // Will fetch or parse from profile route if needed
          full_name: payload.full_name || "Active User",
          role: payload.role || "customer",
        });
      }
    } catch (e) {
      localStorage.removeItem("access_token");
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = async (tokenData: { access_token: string; refresh_token: string }) => {
    localStorage.setItem("access_token", tokenData.access_token);
    localStorage.setItem("refresh_token", tokenData.refresh_token);
    await fetchProfile();
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  };

  React.useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, fetchProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
