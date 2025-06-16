"use client";

import * as React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Provider } from "jotai";
import { Toaster } from "@/components/ui/sonner";

export function Providers({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  const [queryClient] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <Provider>
        <NextThemesProvider {...props}>
          <TooltipProvider delayDuration={0}>{children}</TooltipProvider>
          <Toaster />
        </NextThemesProvider>
      </Provider>
    </QueryClientProvider>
  );
}
