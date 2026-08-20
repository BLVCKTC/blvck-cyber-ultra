import { AuthProvider } from "@/lib/auth-session";
import { QueryProvider } from "@/components/providers/query-provider";
import { Toaster } from "sonner";
import { Analytics } from '@vercel/analytics/next';
import type { Metadata, Viewport } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';

const geistSans = Geist({ subsets: ['latin'], variable: '--font-sans' });
const geistMono = Geist_Mono({ subsets: ['latin'], variable: '--font-mono' });

// Enhanced cyber-themed metadata matching your previous configurations
export const metadata: Metadata = {
    title: 'BLVCK CYBER — Secure your environment',
  description:
    'AI-powered SOC, threat intelligence, and compliance built for African organizations. Detect, investigate, and respond in seconds.',
  generator: 'v0.app',
  authors: [{ name: "BLVCK One" }],
  openGraph: {
  title: 'BLVCK CYBER — Secure your environment',
    description: 'AI-powered SOC, threat intel and compliance built for African organizations.',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
  },
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
};

export const viewport: Viewport = {
  colorScheme: 'dark',
  themeColor: '#05090b',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html 
      lang="en" 
      className={`dark bg-background ${geistSans.variable} ${geistMono.variable}`}
      suppressHydrationWarning // Prevents browser extension warning clashes
    >
      <body className="bg-background text-foreground font-sans antialiased selection:bg-primary/25 selection:text-foreground">
        <AuthProvider>
          <QueryProvider>
            {children}
            
            {/* Dark themed toaster alert notification module global configuration */}
            <Toaster theme="dark" position="top-right" closeButton richColors />
          </QueryProvider>
        </AuthProvider>
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  );
}
