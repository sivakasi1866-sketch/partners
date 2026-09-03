import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Send, Bot, User as UserIcon, Loader2 } from 'lucide-react';
import { api } from '../../services/api';
import { User } from '../../types';

interface AIAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentUser: User;
}

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export const AIAssistantModal: React.FC<AIAssistantModalProps> = ({ isOpen, onClose, currentUser }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: `Hello ${currentUser.name}! I am the Elite Bus AI Transit Assistant powered by Gemini 3.7. Ask me about live arrival times, delays, route connections, or campus shuttle schedules.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickPrompts = [
    "When is the next bus arriving at Central Library?",
    "Is Route R-01 running on time right now?",
    "Which bus goes from South Hostel to Science Quad?",
    "What are the peak traffic hours on campus?"
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isOpen) return null;

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputQuery;
    if (!query.trim() || isLoading) return;

    const userMsg: Message = {
      id: `u-${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setIsLoading(true);

    try {
      const res = await api.askAIAssistant(query, currentUser.role);
      const botMsg: Message = {
        id: `a-${Date.now()}`,
        sender: 'assistant',
        text: res.reply || "I received your query but could not formulate a response. Please check back shortly.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: "The AI Transit service is currently updating live bus locations. Please try your question again in a moment.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-50/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-gray-200 rounded-xl max-w-lg w-full h-[600px] max-h-[90vh] shadow-sm flex flex-col overflow-hidden animate-in fade-in zoom-in-95">
        {/* Header */}
        <div className="p-4 bg-gray-50/80 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                Elite AI Transit Assistant
                <span className="text-[10px] bg-indigo-500/20 text-indigo-300 px-1.5 py-0.5 rounded font-mono">
                  Gemini 3.7
                </span>
              </h3>
              <p className="text-[11px] text-slate-600">Real-time route, delay & timetable intelligence</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-600 hover:text-slate-900 p-1 rounded-lg hover:bg-white"
          >
            ✕
          </button>
        </div>

        {/* Chat History */}
        <div className="flex-1 p-4 overflow-y-auto space-y-3 text-xs">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex items-start gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.sender === 'assistant' && (
                <div className="w-7 h-7 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0 mt-0.5">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div
                className={`max-w-[80%] p-3.5 rounded-lg ${
                  m.sender === 'user'
                    ? 'bg-emerald-600 text-white rounded-tr-none'
                    : 'bg-gray-50 border border-gray-200 text-slate-800 rounded-tl-none leading-relaxed'
                }`}
              >
                <div className="whitespace-pre-wrap">{m.text}</div>
                <div
                  className={`text-[9px] mt-1.5 text-right ${
                    m.sender === 'user' ? 'text-emerald-200' : 'text-slate-500 font-mono'
                  }`}
                >
                  {m.timestamp}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex items-center gap-2 text-indigo-300 text-xs py-2">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
              <span>Analyzing live bus locations & timetable schedules...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick prompt suggestions */}
        <div className="px-4 py-2 bg-gray-50/40 border-t border-gray-200/60 overflow-x-auto flex gap-1.5">
          {quickPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(p)}
              className="px-2.5 py-1 bg-white/80 hover:bg-gray-50 text-slate-700 rounded-lg text-[10px] whitespace-nowrap transition-colors border border-gray-200/60 shrink-0"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="p-3 bg-gray-50 border-t border-gray-200 flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask about bus arrivals, routes, or delays..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={isLoading}
            className="flex-1 bg-white border border-gray-200 text-slate-900 rounded-xl px-3.5 py-2 text-xs focus:outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={isLoading || !inputQuery.trim()}
            className="p-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-colors disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
