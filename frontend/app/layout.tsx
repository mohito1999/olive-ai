import Providers from "@/components/layout/providers";
import { Toaster } from "@/components/ui/toaster";
import type { Metadata } from "next";
import NextTopLoader from "nextjs-toploader";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Olive AI",
    description: "Automate Call Campaigns With Human-Like Voice AI"
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
   return (
        <html lang="en" suppressHydrationWarning>
            <body className={`${inter.className} overflow-hidden`}>
                <NextTopLoader />
                <Providers>
                    <Toaster />
                    {children}
                </Providers>
            </body>
        </html>
    );
}
