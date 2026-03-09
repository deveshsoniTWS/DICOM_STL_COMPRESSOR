import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MedZip - Medical File Compression",
  description: "Compress and decompress DICOM and STL medical files",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
