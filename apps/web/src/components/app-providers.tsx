"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { flushOfflineIdeas } from "@/lib/offline-ideas";

export function AppProviders({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 20_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  useEffect(() => {
    if (
      process.env.NODE_ENV === "production" &&
      "serviceWorker" in navigator
    ) {
      void navigator.serviceWorker.register("/sw.js");
    }

    const replay = async () => {
      if (!navigator.onLine) return;
      const result = await flushOfflineIdeas(api.createIdea);
      if (result.sent > 0) {
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: ["ideas"] }),
          queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
        ]);
      }
    };

    void replay();
    window.addEventListener("online", replay);
    return () => window.removeEventListener("online", replay);
  }, [queryClient]);

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
