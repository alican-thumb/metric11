import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { trTR } from "@clerk/localizations";
import { Analytics } from "@vercel/analytics/next";
import { NavBar } from "@/components/nav-bar";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const SITE_URL = "https://tahmin.metric11.com";
const TITLE = "metric11 Tahmin | Süper Lig Tahmin Oyunu";
const DESCRIPTION = "Kendi maç tahminlerini gir, puan topla, liderlik tablosunda yarış.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: TITLE,
  description: DESCRIPTION,
  applicationName: "metric11 Tahmin",
  openGraph: {
    title: TITLE,
    description: DESCRIPTION,
    url: SITE_URL,
    siteName: "metric11 Tahmin",
    locale: "tr_TR",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
  },
};

export const viewport: Viewport = {
  themeColor: "#091810",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <ClerkProvider localization={trTR} signInUrl="/sign-in" signUpUrl="/sign-up" afterSignOutUrl="/">
      <html
        lang="tr"
        className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      >
        <body className="min-h-full flex flex-col bg-slate-950 text-slate-100">
          <NavBar />
          <main className="flex-1 mx-auto w-full max-w-4xl px-4 py-6">{children}</main>
          <Analytics />
        </body>
      </html>
    </ClerkProvider>
  );
}
