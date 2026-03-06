import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { AdminLayout } from "@/components/layout/admin-layout";

const inter = Inter({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "GoDrive Admin",
  description: "Painel Administrativo do GoDrive",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className={`${inter.className} antialiased`}>
        <Providers>
          <AdminLayout>
            {children}
          </AdminLayout>
        </Providers>
      </body>
    </html>
  );
}
