import type { Metadata } from 'next'
import { Inter, Playfair_Display } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const playfair = Playfair_Display({ subsets: ['latin'], variable: '--font-playfair' })

export const metadata: Metadata = {
  title: 'TripHelix - Your Ultimate Travel Companion',
  description: 'Discover, plan, and book your perfect travel experiences with TripHelix.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable}`}>
      <body className="bg-gradient-to-b from-blue-50 to-white min-h-screen">
        {children}
      </body>
    </html>
  )
}
