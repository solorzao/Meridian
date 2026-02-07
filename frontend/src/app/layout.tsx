import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Meridian - AI Trading Journal',
  description: 'AI-powered trading journal and research assistant. We help you find your way.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased bg-meridian-surface text-meridian-text">
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}
