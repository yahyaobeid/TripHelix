/**
 * Home page component for the TripHelix application.
 * This is the main page that renders the chat interface.
 */

import Chat from './components/Chat';

/**
 * The main home page component that renders the chat interface.
 * 
 * @returns JSX.Element - The rendered home page with the chat component
 */
export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100">
      <div className="container mx-auto py-8">
        {/* Page title */}
        <h1 className="text-3xl font-bold text-center mb-8">TripHelix Chat</h1>
        {/* Chat component */}
        <Chat />
      </div>
    </main>
  );
} 