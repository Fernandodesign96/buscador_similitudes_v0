import type { Metadata } from "next";
import { Roboto, Roboto_Slab } from "next/font/google";
import { copy } from "@/lib/copy";
import "./globals.css";

const roboto = Roboto({
  variable: "--font-roboto",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
});

const robotoSlab = Roboto_Slab({
  variable: "--font-roboto-slab",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
});

export const metadata: Metadata = {
  title: copy.meta.title,
  description: copy.meta.description,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className={`${roboto.variable} ${robotoSlab.variable} h-full`}>
      <body className="flex min-h-full flex-col bg-white font-[family-name:var(--font-roboto)] text-inapi-text antialiased">
        {children}
      </body>
    </html>
  );
}
