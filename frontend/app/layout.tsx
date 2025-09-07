import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "DeFAI - Autonomous DeFi AI Agents",
  description: "Advanced DeFi yield optimization platform powered by AI agents on Solana",
  keywords: "DeFi, AI, Solana, yield farming, autonomous trading, crypto",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.className} min-h-screen bg-gradient-dark antialiased`}
      >
        <div className="relative flex min-h-screen">
          {/* Background effects */}
          <div className="fixed inset-0 bg-gradient-to-br from-defi-primary/5 via-background to-defi-secondary/5" />
          <div className="fixed inset-0 bg-[url('/grid.svg')] opacity-10" />
          
          {/* Main content */}
          <main className="relative flex-1 flex flex-col">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
