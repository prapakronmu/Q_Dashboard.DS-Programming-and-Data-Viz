import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Premium Movie Analytics',
  description: 'Live-action movie dashboard with Apple Vision Pro aesthetic',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-black text-white antialiased min-h-screen overflow-x-hidden`}>
        {/* Cinematic Background Layer */}
        <div className="fixed inset-0 z-[-1]">
          {/* Abstract colorful blobs (จำลองแสงฉากหลัง Cinematic ก่อนใส่รูปจริง) */}
          <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] bg-brandAccent/20 rounded-full blur-[100px]"></div>
          <div className="absolute bottom-[-10%] right-[-10%] w-[60vw] h-[60vw] bg-blue-900/20 rounded-full blur-[120px]"></div>
          
          {/* Dark Overlay with Heavy Blur (visionDark effect) */}
          <div className="absolute inset-0 bg-black/60 backdrop-blur-bgCinematic"></div>
        </div>

        {/* Main Application Container */}
        <main className="relative z-10 w-full min-h-screen p-6">
          {children}
        </main>
      </body>
    </html>
  );
}
