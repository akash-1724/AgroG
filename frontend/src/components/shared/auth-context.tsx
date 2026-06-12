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
      const response = await api.get("/auth/me");
      setUser(response.data);
    } catch (e) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
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
    const timer = setTimeout(() => {
      fetchProfile();
    }, 0);
    return () => clearTimeout(timer);
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
