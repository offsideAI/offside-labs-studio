"use client";

import * as React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useRouter } from "next/navigation";

import { setAuthFailureHandler } from "../lib/api";
import { ThemeProvider } from "../lib/theme";

export const Providers = ({ children }: { children: React.ReactNode }) => {
  const router = useRouter();
  const [client] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30 * 1000,
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      }),
  );

  React.useEffect(() => {
    setAuthFailureHandler(() => {
      router.replace("/login");
    });
  }, [router]);

  return (
    <ThemeProvider>
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    </ThemeProvider>
  );
};
