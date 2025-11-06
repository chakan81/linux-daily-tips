import type { Metadata } from 'next'
import './globals.css'
import { Inter } from 'next/font/google'
import { Header, Footer } from '@/components/layout'
import { ErrorBoundary } from '@/components/common'
import { Providers } from '@/components/providers'
import { env } from '@/lib/env'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  metadataBase: new URL(env.NEXT_PUBLIC_BASE_URL),
  title: {
    template: '%s | Linux Daily Tips',
    default: 'Linux Daily Tips - Learn Linux Command Line Every Day',
  },
  description: 'Master Linux command line with daily tips, interactive terminal practice, and comprehensive tutorials. Perfect for beginners and advanced users.',
  keywords: ['linux', 'terminal', 'command line', 'bash', 'shell', 'unix', 'tips', 'tutorial', 'learning'],
  authors: [{ name: 'Linux Daily Tips' }],
  creator: 'Linux Daily Tips',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://linuxdailytips.com',
    title: 'Linux Daily Tips - Learn Linux Command Line Every Day',
    description: 'Master Linux command line with daily tips, interactive terminal practice, and comprehensive tutorials.',
    siteName: 'Linux Daily Tips',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Linux Daily Tips',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Linux Daily Tips - Learn Linux Command Line Every Day',
    description: 'Master Linux command line with daily tips, interactive terminal practice, and comprehensive tutorials.',
    images: ['/og-image.png'],
    creator: '@linuxdailytips',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: env.NEXT_PUBLIC_GOOGLE_VERIFICATION ? {
    google: env.NEXT_PUBLIC_GOOGLE_VERIFICATION,
  } : undefined,
  alternates: {
    canonical: 'https://linuxdailytips.com',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} scroll-smooth`} suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/site.webmanifest" />
        <meta name="theme-color" content="#ffffff" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
      </head>
      <body className={`${inter.className} antialiased min-h-screen gradient-bg`}>
        <ErrorBoundary>
          <Providers>
            <div className="relative flex min-h-screen flex-col">
              <Header />
              <main className="flex-1">
                {children}
              </main>
              <Footer />
            </div>
          </Providers>
        </ErrorBoundary>
      </body>
    </html>
  )
}