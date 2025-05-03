'use client';

/**
 * Home page component for the TripHelix application.
 * This is the main page that renders the chat interface.
 */

import Image from 'next/image'
import Chat from './components/Chat'
import { useRef } from 'react'

/**
 * The main home page component that renders the chat interface.
 * 
 * @returns JSX.Element - The rendered home page with the chat component
 */
export default function Home() {
  const chatSectionRef = useRef<HTMLDivElement>(null);

  const scrollToChat = () => {
    chatSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative h-[80vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <Image
            src="/hero-bg.jpg"
            alt="Travel background"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-black/40" />
        </div>
        
        <div className="relative z-10 text-center px-4">
          <h1 className="font-playfair text-5xl md:text-7xl font-bold text-white mb-6">
            Discover Your Next Adventure
          </h1>
          <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
            Let TripHelix be your guide to unforgettable travel experiences. Plan, book, and explore with confidence.
          </p>
          <button 
            onClick={scrollToChat}
            className="bg-white text-blue-600 px-8 py-3 rounded-full font-semibold hover:bg-blue-50 transition-colors"
          >
            Start Planning
          </button>
        </div>
      </section>

      {/* Chat Section */}
      <section ref={chatSectionRef} className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="font-playfair text-3xl font-bold text-center mb-8">
            Your Personal Travel Assistant
          </h2>
          <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-lg p-6">
            <Chat />
          </div>
        </div>
      </section>
    </main>
  )
} 