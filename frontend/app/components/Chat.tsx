/**
 * Chat component for the TripHelix application.
 * This component provides a chat interface that communicates with the backend API
 * and displays messages in a streaming fashion.
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { Calendar } from 'react-date-range';
import 'react-date-range/dist/styles.css';
import 'react-date-range/dist/theme/default.css';

// Define the Message interface for type safety
interface Message {
  role: 'user' | 'assistant';  // The role of the message sender
  content: string;             // The content of the message
  type?: 'text' | 'calendar' | 'itinerary';  // Type of message content
  data?: any;                  // Additional data for special message types
}

export default function Chat() {
  // State management for messages, input, and loading state
  const [messages, setMessages] = useState<Message[]>([]);  // Array of chat messages
  const [input, setInput] = useState('');                   // Current input value
  const [isLoading, setIsLoading] = useState(false);        // Loading state indicator
  const [showCalendar, setShowCalendar] = useState(false);  // Calendar visibility
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);  // Selected date
  const [currentItinerary, setCurrentItinerary] = useState<string | null>(null);  // Current itinerary
  const messagesEndRef = useRef<HTMLDivElement>(null);      // Reference to the end of messages container
  const hasInitialized = useRef(false);                     // Track if initial message has been sent

  // Auto-scroll to the bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send initial message when component mounts
  useEffect(() => {
    if (!hasInitialized.current) {
      hasInitialized.current = true;
      // Add the initial assistant message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Hello! I'm your personal travel assistant. I'd love to help you plan your next adventure. Do you have a specific destination in mind for your trip?",
        type: 'text'
      }]);
    }
  }, []);

  // Handle date selection from calendar
  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
    setShowCalendar(false);
    // Send the selected date to the backend
    handleSubmit(new Event('submit') as any, date.toISOString());
  };

  // Handle itinerary download
  const handleDownloadItinerary = () => {
    if (!currentItinerary) return;
    
    // Create a blob with the itinerary content
    const blob = new Blob([currentItinerary], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    
    // Create a temporary link and trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = 'trip-itinerary.html';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  /**
   * Handles the submission of a new message.
   * Sends the message to the backend API and processes the streaming response.
   */
  const handleSubmit = async (e: React.FormEvent, date?: string) => {
    e.preventDefault();
    const messageToSend = date || input.trim();
    if (!messageToSend || isLoading) return;

    // Add the user's message to the chat
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: messageToSend,
      type: date ? 'calendar' : 'text'
    }]);
    setInput('');
    setIsLoading(true);

    try {
      // Make a POST request to the chat stream endpoint
      const res = await fetch('http://localhost:8000/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: messageToSend, 
          session_id: 'test_session' 
        }),
      });
      if (!res.body) throw new Error('No response body');

      // Set up streaming response handling
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let fullResponse = '';

      // Add a placeholder for the assistant's response
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      // Process the stream chunk by chunk
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          const chunk = decoder.decode(value);
          if (chunk) {
            fullResponse += chunk;
            // Update the last assistant message with the new chunk
            setMessages(prev => {
              const copy = [...prev];
              const last = { ...copy.at(-1)! };
              if (last.role === 'assistant') {
                last.content = fullResponse;
                // Check if the response contains calendar request
                if (fullResponse.toLowerCase().includes('select a date')) {
                  last.type = 'calendar';
                }
                // Check if the response contains itinerary
                else if (fullResponse.toLowerCase().includes('itinerary')) {
                  last.type = 'itinerary';
                  setCurrentItinerary(fullResponse);
                }
                copy[copy.length - 1] = last;
              }
              return copy;
            });
          }
        }
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: '❌ Sorry, something went wrong.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Render the chat interface
  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      {/* Messages container with auto-scrolling */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-4 rounded-lg ${
              m.role === 'user'
                ? 'bg-blue-500 text-white ml-auto'
                : 'bg-gray-200 text-gray-800'
            } max-w-[80%]`}
          >
            {m.type === 'calendar' ? (
              <div className="text-center">
                <Calendar
                  date={selectedDate || new Date()}
                  onChange={handleDateSelect}
                  className="border rounded-lg shadow-lg"
                />
              </div>
            ) : m.type === 'itinerary' ? (
              <div>
                <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: m.content }} />
                <button
                  onClick={handleDownloadItinerary}
                  className="mt-4 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  Download Itinerary
                </button>
              </div>
            ) : (
              m.content
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Message input form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          className="flex-1 p-2 border rounded-lg"
          disabled={isLoading}
          placeholder="Type your message…"
          value={input}
          onChange={e => setInput(e.target.value)}
        />
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50"
        >
          {isLoading ? 'Sending…' : 'Send'}
        </button>
      </form>
    </div>
  );
}
