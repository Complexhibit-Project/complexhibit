import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Complexhibit · Semantic Cultural Heritage Explorer",
    template: "%s · Complexhibit",
  },
  description:
    "Explore the OntoExhibit knowledge graph: exhibitions, artworks, people and institutions connected through their semantic relationships.",
  keywords: ["knowledge graph", "OntoExhibit", "exhibitions", "cultural heritage", "linked data", "SPARQL", "semantic web"],
  openGraph: {
    title: "Complexhibit · Semantic Cultural Heritage Explorer",
    description:
      "Explore the OntoExhibit knowledge graph: exhibitions, artworks, people and institutions connected through their semantic relationships.",
    type: "website",
    siteName: "Complexhibit",
  },
  twitter: {
    card: "summary_large_image",
    title: "Complexhibit · Semantic Cultural Heritage Explorer",
    description: "Explore the OntoExhibit knowledge graph through its semantic relationships.",
  },
};

import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Suspense } from "react";
import { AuthProvider } from "@/hooks/useAuth";
import { AnalyticsTracker } from "@/components/AnalyticsTracker";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}>
        <AuthProvider>
          <Suspense fallback={null}>
            <AnalyticsTracker />
          </Suspense>
          <Navbar />
          <main className="flex-grow bg-gray-50">
            {children}
          </main>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
