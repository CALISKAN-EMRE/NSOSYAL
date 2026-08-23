import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NSosyal Pusula | Yapay Zekâ Destekli Bağlam ve Şeffaf Öneri Sistemi",
  description:
    "TEKNOFEST 2026 Projesi - Sosyal medya paylaşımlarında bağlam kartları, şeffaf öneri skorlaması ve açıklanabilir içerik güvenliği sinyalleri.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr" className="dark">
      <body className="bg-[#090d16] text-slate-100 antialiased selection:bg-blue-600 selection:text-white">
        {children}
      </body>
    </html>
  );
}
