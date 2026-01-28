import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Web Scraper Demo - AWS Bedrock Agent",
  description: "Demo application showcasing web scraping using AWS Bedrock Agent and Lambda",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
