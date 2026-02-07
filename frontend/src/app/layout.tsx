import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Meridian - AI Trading Journal',
  description: 'AI-powered trading journal and research assistant',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
          {children}
        </div>
      </body>
    </html>
  );
}
