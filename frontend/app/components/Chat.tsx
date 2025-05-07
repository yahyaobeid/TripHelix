/**
 * Chat component for the TripHelix application.
 * Streams messages from the backend and renders ASSISTANT replies as HTML.
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { Calendar } from 'react-date-range';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import 'react-date-range/dist/styles.css';
import 'react-date-range/dist/theme/default.css';

/* ────────────────────  types ──────────────────── */
// Configure marked options
marked.setOptions({
  breaks: true,
  gfm: true,
});


interface Message {
  role: 'user' | 'assistant';
  content: string;
  type?: 'text' | 'calendar' | 'html';
  data?: any;
}

interface Location {
  lat: number;
  lng: number;
  name: string;
}

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  itinerary: string | null;
  onItineraryUpdate?: (newItinerary: string) => void;
}

const Modal = ({ isOpen, onClose, children, itinerary, onItineraryUpdate }: ModalProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState<string | null>(null);

  useEffect(() => {
    if (itinerary) {
      setEditedContent(itinerary);
    }
  }, [itinerary]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    if (editedContent && onItineraryUpdate) {
      onItineraryUpdate(editedContent);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedContent(itinerary);
    setIsEditing(false);
  };

  const handleContentChange = (e: React.ChangeEvent<HTMLDivElement>) => {
    setEditedContent(e.currentTarget.innerHTML);
  };

  const handleDownloadItinerary = () => {
    if (!editedContent) return;
    
    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Trip Itinerary</title>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
            .itinerary-table {
              width: 100%;
              border-collapse: collapse;
              margin: 20px 0;
              font-size: 14px;
            }
            .itinerary-table th,
            .itinerary-table td {
              border: 1px solid #ddd;
              padding: 12px;
              vertical-align: top;
            }
            .itinerary-table th {
              background-color: #f5f5f5;
              font-weight: bold;
              text-align: left;
            }
            .itinerary-table tr:nth-child(even) {
              background-color: #f9f9f9;
            }
            .itinerary-table strong {
              color: #2c3e50;
              display: block;
              margin-bottom: 8px;
              font-size: 16px;
            }
            .itinerary-table ul {
              margin: 0;
              padding-left: 20px;
            }
            .itinerary-table li {
              margin: 4px 0;
            }
            .itinerary-table td {
              min-width: 200px;
            }
          </style>
        </head>
        <body>
          ${editedContent}
        </body>
      </html>
    `;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = 'trip-itinerary.html';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-6xl h-[90vh] flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-800">Your Itinerary</h2>
          <div className="flex items-center gap-2">
            {!isEditing ? (
              <button
                onClick={handleEdit}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Edit Itinerary
              </button>
            ) : (
              <>
                <button
                  onClick={handleSave}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  Save Changes
                </button>
                <button
                  onClick={handleCancel}
                  className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
              </>
            )}
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          <style>
            {`
              .itinerary-container {
                font-family: Arial, sans-serif;
                line-height: 1.6;
              }
              .itinerary-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 14px;
              }
              .itinerary-table th,
              .itinerary-table td {
                border: 1px solid #ddd;
                padding: 12px;
                vertical-align: top;
              }
              .itinerary-table th {
                background-color: #f5f5f5;
                font-weight: bold;
                text-align: left;
                position: sticky;
                top: 0;
                z-index: 1;
              }
              .itinerary-table tr:nth-child(even) {
                background-color: #f9f9f9;
              }
              .itinerary-table strong {
                color: #2c3e50;
                display: block;
                margin-bottom: 8px;
                font-size: 16px;
              }
              .itinerary-table ul {
                margin: 0;
                padding-left: 20px;
              }
              .itinerary-table li {
                margin: 4px 0;
              }
              .itinerary-table td {
                min-width: 200px;
              }
              .editable {
                outline: 2px solid #3b82f6;
                outline-offset: -2px;
              }
              .editable:focus {
                outline: 2px solid #2563eb;
              }
            `}
          </style>
          <div 
            className="itinerary-container"
            contentEditable={isEditing}
            onBlur={handleContentChange}
            suppressContentEditableWarning
            dangerouslySetInnerHTML={{ __html: editedContent || '' }}
          />
        </div>
        <div className="mt-4 flex justify-end border-t pt-4">
          <button
            onClick={handleDownloadItinerary}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            Download Itinerary
          </button>
        </div>
      </div>
    </div>
  );
};

/* ────────────────────  component ──────────────────── */

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [currentItinerary, setCurrentItinerary] = useState<string | null>(null);
  const [showItinerary, setShowItinerary] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasInitialized = useRef(false);

  /* ───────────────── auto‑scroll ───────────────── */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /* ─────────────── initial assistant msg ────────── */
  useEffect(() => {
    if (!hasInitialized.current) {
      hasInitialized.current = true;
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content:
            "Hello! I'm your personal travel assistant. Do you have a specific destination in mind?",
          type: 'text',
        },
      ]);
    }
  }, []);

  /* ─────────────── date selection ──────────────── */
  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
    handleSubmit(new Event('submit') as any, date.toISOString());
  };

  /* ─────────────── send a message ──────────────── */
  const handleSubmit = async (e: React.FormEvent, date?: string) => {
    e.preventDefault();
    const messageToSend = date || input.trim();
    if (!messageToSend || isLoading) return;

    /* add user bubble */
    setMessages(prev => [
      ...prev,
      {
        role: 'user',
        content: messageToSend,
        type: date ? 'calendar' : 'text',
      },
    ]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageToSend,
          session_id: 'test_session',
        }),
      });
      if (!res.body) throw new Error('No response body');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let fullResponse = '';

      /* placeholder assistant bubble */
      setMessages(prev => [...prev, { role: 'assistant', content: '', type: 'text' }]);

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          const chunk = decoder.decode(value);
          if (chunk) {
            fullResponse += chunk;
            /* show raw text while streaming */
            setMessages(prev => {
              const copy = [...prev];
              const last = { ...copy.at(-1)! };
              if (last.role === 'assistant') {
                last.content = fullResponse;
                copy[copy.length - 1] = last;
              }
              return copy;
            });
          }
        }
      }

      /* ───────── after the stream finishes ───────── */

      let md = fullResponse.trim()

      /* 1️⃣  ensure a newline before any heading symbols (##, ###, etc.)        */
      .replace(/([^\n])(\s*#+\s)/g, '$1\n\n$2')

      /* 2️⃣  ensure a newline before any bullet that's glued to a word          */
      .replace(/([^\n])(\s*-\s)/g, '$1\n$2')

      /* 3️⃣  turn **all** Markdown headings (#, ##, ### …) into bold lines      */
      .replace(/^#+\s*(.*)$/gm, '**$1**')

      /* 4️⃣  add blank line after each "Day N:" header */
      .replace(/^\*Day\s*\d+.*\*/gm, match => `${match}\n`)

      /* 5️⃣  add blank line after each time-of-day header */
      .replace(/^\*(Morning|Afternoon|Evening)/gm, match => `${match}\n`)

      /* 6️⃣  remove exactly 3 consecutive newlines              */
      .replace(/\n{3}/g, '\n\n')

      /* 7️⃣  ensure only one newline after bullet points */
      .replace(/(\n\s*-\s*.*)\n+/g, '$1\n');

      // Convert to safe HTML
      const rawHtml = await marked.parse(md);
      const html = DOMPurify.sanitize(rawHtml);

      // Convert the HTML to a table format
      const tableHtml = html.replace(
        /<strong>Day\s*(\d+):\s*(.*?)<\/strong>([\s\S]*?)(?=<strong>Day\s*\d+:|$)/g,
        (match, dayNum, date, content) => {
          const morning = content.match(/<strong>Morning<\/strong>([\s\S]*?)(?=<strong>Afternoon|Evening|$)/)?.[1] || '';
          const afternoon = content.match(/<strong>Afternoon<\/strong>([\s\S]*?)(?=<strong>Evening|$)/)?.[1] || '';
          const evening = content.match(/<strong>Evening<\/strong>([\s\S]*?)$/)?.[1] || '';

          return `
            <tr>
              <td><strong>Day ${dayNum}: ${date}</strong></td>
              <td><strong>Morning</strong>${morning}</td>
              <td><strong>Afternoon</strong>${afternoon}</td>
              <td><strong>Evening</strong>${evening}</td>
            </tr>
          `;
        }
      );

      const finalHtml = `
        <table class="itinerary-table">
          <thead>
            <tr>
              <th>Day</th>
              <th>Morning</th>
              <th>Afternoon</th>
              <th>Evening</th>
            </tr>
          </thead>
          <tbody>
            ${tableHtml}
          </tbody>
        </table>
      `;

      setMessages(prev => {
        const copy = [...prev];
        const last = { ...copy.at(-1)! };
        last.content = finalHtml;
        last.type = 'html';
        copy[copy.length - 1] = last;
        return copy;
      });

      /* save itinerary for download btn */
      if (html.toLowerCase().includes('itinerary')) {
        setCurrentItinerary(finalHtml);
        setShowItinerary(true);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: '❌ Sorry, something went wrong.', type: 'text' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleItineraryUpdate = (newItinerary: string) => {
    setCurrentItinerary(newItinerary);
  };

  /* ──────────────────── render ─────────────────── */
  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-4 rounded-lg max-w-[80%] ${
              m.role === 'user'
                ? 'bg-blue-500 text-white ml-auto'
                : 'bg-gray-100 text-gray-800'
            }`}
          >
            {m.type === 'calendar' ? (
              <Calendar
                date={selectedDate || new Date()}
                onChange={handleDateSelect}
                className="border rounded-lg shadow-lg"
              />
            ) : m.type === 'html' ? (
              <div
                className="prose prose-slate max-w-none whitespace-pre-wrap"
                dangerouslySetInnerHTML={{ __html: m.content }}
              />
            ) : (
              <div
                className="prose prose-slate max-w-none whitespace-pre-wrap"
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(marked.parse(m.content) as string),
                }}
              />
            )}

            {m.type === 'html' && i === messages.length - 1 && currentItinerary && (
              <button
                onClick={() => setShowItinerary(true)}
                className="mt-4 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
              >
                View Itinerary
              </button>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

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

      <Modal 
        isOpen={showItinerary} 
        onClose={() => setShowItinerary(false)}
        itinerary={currentItinerary}
        onItineraryUpdate={handleItineraryUpdate}
      >
        <div className="itinerary-container">
          <div dangerouslySetInnerHTML={{ __html: currentItinerary || '' }} />
        </div>
      </Modal>
    </div>
  );
}
