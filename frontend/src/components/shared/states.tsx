"use client";

import { Loader2, AlertCircle, Inbox, HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export function LoadingSpinner({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 gap-3 text-slate-500">
      <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
      <span className="text-sm font-medium">{message}</span>
    </div>
  );
}

export function ErrorBanner({ message = "Something went wrong. Please try again." }: { message?: string }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3 max-w-2xl mx-auto my-6">
      <AlertCircle className="h-5 w-5 text-red-600 shrink-0 mt-0.5" />
      <div>
        <h3 className="font-bold text-red-950 text-sm">Action Error</h3>
        <p className="text-red-700 text-xs mt-0.5 leading-relaxed">{message}</p>
      </div>
    </div>
  );
}

export function EmptyState({
  title = "No items found",
  description = "Check back later or try adjusting your search parameters.",
  actionLabel,
  onAction,
}: {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl p-8 max-w-md mx-auto my-6">
      <Inbox className="h-12 w-12 text-slate-300 mx-auto mb-3" />
      <h3 className="text-lg font-bold text-slate-800">{title}</h3>
      <p className="text-slate-500 text-sm mt-1 leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} className="mt-4 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
