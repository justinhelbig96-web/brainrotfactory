import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Brainrot Video Factory',
  description: 'Erstelle virale TikTok Brainrot Videos automatisch',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  );
}
