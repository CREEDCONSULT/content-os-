import type { Metadata, Viewport } from "next";

import { AppProviders } from "@/components/app-providers";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Mezie BrandOS",
    template: "%s · Mezie BrandOS",
  },
  description:
    "The operating system for Mr. C. Mezie's brand intelligence, content production, and growth.",
  applicationName: "Mezie BrandOS",
};

export const viewport: Viewport = {
  colorScheme: "dark",
  themeColor: "#06080c",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
