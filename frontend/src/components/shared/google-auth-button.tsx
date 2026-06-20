"use client";

import * as React from "react";
import Script from "next/script";

import { api } from "@/lib/api";

type GoogleButtonText = "signin_with" | "signup_with" | "continue_with";

type GoogleCredentialResponse = {
  credential?: string;
};

type GoogleConfigStatus = "loading" | "ready" | "missing" | "error";

type GoogleAccountsId = {
  initialize: (options: {
    client_id: string;
    callback: (response: GoogleCredentialResponse) => void;
  }) => void;
  renderButton: (
    parent: HTMLElement,
    options: {
      theme: "outline";
      size: "large";
      text: GoogleButtonText;
      width: number;
    }
  ) => void;
};

declare global {
  interface Window {
    google?: {
      accounts?: {
        id?: GoogleAccountsId;
      };
    };
  }
}

export type GoogleAuthTokenData = {
  access_token: string;
  refresh_token: string;
  token_type?: string;
  role?: "customer" | "farmer" | "admin";
};

interface GoogleAuthButtonProps {
  text: GoogleButtonText;
  onAuthenticated: (tokenData: GoogleAuthTokenData) => Promise<void>;
  onError: (message: string) => void;
  getAdditionalPayload?: () => Promise<Record<string, unknown> | null> | Record<string, unknown> | null;
}

const bundledGoogleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

export function GoogleAuthButton({ text, onAuthenticated, onError, getAdditionalPayload }: GoogleAuthButtonProps) {
  const containerRef = React.useRef<HTMLDivElement | null>(null);
  const [clientId, setClientId] = React.useState<string | null>(() => bundledGoogleClientId || null);
  const [scriptReady, setScriptReady] = React.useState(false);
  const [configStatus, setConfigStatus] = React.useState<GoogleConfigStatus>(() =>
    bundledGoogleClientId ? "ready" : "loading"
  );

  const handleCredential = React.useCallback(
    async (response: GoogleCredentialResponse) => {
      if (!response.credential) {
        onError("Google did not return a credential. Try again.");
        return;
      }

      try {
        const additionalPayload = getAdditionalPayload ? await getAdditionalPayload() : {};
        if (additionalPayload === null) {
          return;
        }

        const apiResponse = await api.post<GoogleAuthTokenData>("/auth/google", {
          id_token: response.credential,
          ...additionalPayload,
        });
        await onAuthenticated(apiResponse.data);
      } catch (error: unknown) {
        const err = error as { response?: { data?: { detail?: string } } };
        onError(err.response?.data?.detail || "Google authentication failed.");
      }
    },
    [getAdditionalPayload, onAuthenticated, onError]
  );

  React.useEffect(() => {
    let cancelled = false;

    if (bundledGoogleClientId) {
      return;
    }

    api
      .get<{ client_id: string; configured: boolean }>("/auth/google/client-id")
      .then((response) => {
        if (cancelled) {
          return;
        }

        if (response.data.configured && response.data.client_id) {
          setClientId(response.data.client_id);
          setConfigStatus("ready");
        } else {
          setConfigStatus("missing");
        }
      })
      .catch(() => {
        if (!cancelled) {
          setConfigStatus("error");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  React.useEffect(() => {
    const container = containerRef.current;
    const google = window.google?.accounts?.id;

    if (!scriptReady || !clientId || !container || !google) {
      return;
    }

    container.replaceChildren();
    google.initialize({
      client_id: clientId,
      callback: (response) => {
        void handleCredential(response);
      },
    });
    google.renderButton(container, {
      theme: "outline",
      size: "large",
      text,
      width: Math.max(container.clientWidth, 320),
    });
  }, [clientId, handleCredential, scriptReady, text]);

  const statusMessage = React.useMemo(() => {
    if (configStatus === "missing") {
      return "Google sign-in is not configured on the backend.";
    }
    if (configStatus === "error") {
      return "Unable to load Google sign-in configuration.";
    }
    if (!scriptReady) {
      return "Loading Google sign-in...";
    }
    return "";
  }, [configStatus, scriptReady]);

  return (
    <div className="w-full">
      <div ref={containerRef} className="flex min-h-[40px] w-full justify-center" />
      {statusMessage && <p className="mt-2 text-center text-xs text-muted-foreground">{statusMessage}</p>}
      <Script
        src="https://accounts.google.com/gsi/client"
        onReady={() => setScriptReady(true)}
        strategy="lazyOnload"
      />
    </div>
  );
}
