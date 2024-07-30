"use client"
import Providers from "@/components/layout/providers";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { queryClient } from "@/lib/query";
import { Toaster } from "@/components/ui/toaster";
import "@uploadthing/react/styles.css";
import type { Metadata } from "next";
import NextTopLoader from "nextjs-toploader";
import { Inter } from "next/font/google";
import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/client";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({ children }: { children: React.ReactNode }) {
    const supabase = createClient();

    const data = {};
    return (
        <html lang="en" suppressHydrationWarning>
            <body className={`${inter.className} overflow-hidden`}>
                <NextTopLoader />
                <QueryClientProvider client={queryClient}>
                    <Providers session={data}>
                        <Toaster />
                        {children}
                        <ReactQueryDevtools initialIsOpen={false} />
                    </Providers>
                </QueryClientProvider>
            </body>
        </html>
    );
}
