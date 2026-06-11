import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/shared/query-provider";
import { AuthProvider } from "@/components/shared/auth-context";
import { ToastProvider } from "@/components/ui/toast";
import { NavBar } from "@/components/shared/navbar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AgroGuide - Direct Farmer Marketplace",
  description: "Seamless crop recommendation, leaf disease diagnosis, and localized farmer marketplace.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900">
        <QueryProvider>
          <AuthProvider>
            <ToastProvider>
              <NavBar />
              <main className="flex-grow flex flex-col">
                {children}
              </main>
              <footer className="bg-slate-900 text-slate-400 border-t border-slate-800 py-8 px-4 text-center text-sm">
                <div className="max-w-7xl mx-auto">
                  <p>© {new Date().getFullYear()} AgroGuide Ecosystem. Built for organic farm transparency.</p>
                  <p className="mt-2 text-slate-500 text-xs">Empowering direct-to-consumer agriculture trade.</p>
                </div>
              </footer>
            </ToastProvider>
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
