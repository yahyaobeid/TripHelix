/**
 * Chat component for the TripHelix application.
 * This component provides a chat interface that communicates with the backend API
 * and displays messages in a streaming fashion.
 */

'use client';

import { useState, useRef, useEffect } from 'react';

// Define the Message interface for type safety
interface Message {
  role: 'user' | 'assistant';  // The role of the message sender
  content: string;             // The content of the message
}

export default function Chat() {
  // State management for messages, input, and loading state
  const [messages, setMessages] = useState<Message[]>([]);  // Array of chat messages
  const [input, setInput] = useState('');                   // Current input value
  const [isLoading, setIsLoading] = useState(false);        // Loading state indicator
  const messagesEndRef = useRef<HTMLDivElement>(null);      // Reference to the end of messages container

  // Auto-scroll to the bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Handles the submission of a new message.
   * Sends the message to the backend API and processes the streaming response.
   * 
   * @param e - The form submission event
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Add the user's message to the chat
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setIsLoading(true);

    try {
      // Make a POST request to the chat stream endpoint
      const res = await fetch('http://localhost:8000/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, session_id: 'test_session' }),
      });
      if (!res.body) throw new Error('No response body');

      // Set up streaming response handling
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      // Add a placeholder for the assistant's response
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      // Process the stream chunk by chunk
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          const chunk = decoder.decode(value);
          // Update the last assistant message with the new chunk
          setMessages(prev => {
            const copy = [...prev];
            const last = { ...copy.at(-1)! };           // Create a copy to avoid mutation
            if (last.role === 'assistant') {
              last.content += chunk;
              copy[copy.length - 1] = last;
            }
            return copy;
          });
        }
      }
    } catch (err) {
      console.error(err);
      // Show error message if something goes wrong
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: '❌ Sorry, something went wrong.' },
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
            {m.content}
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
