import { useState } from 'react';
import { Header } from './components/Header';
import { HomePage } from './pages/HomePage';
import { ChatPage } from './pages/ChatPage';
import { HistoryPage } from './pages/HistoryPage';
import { ContactsPage } from './pages/ContactsPage';
import { useTelegram } from './hooks/useTelegram';

type Page = 'home' | 'chat' | 'history' | 'contacts';

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const { isReady } = useTelegram();

  // Wait for Telegram to be ready
  if (!isReady) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 rounded-full bg-mastercard-red animate-pulse" />
            <div className="w-12 h-12 rounded-full bg-mastercard-orange -ml-6 animate-pulse" />
          </div>
          <p className="text-gray-600">Загрузка...</p>
        </div>
      </div>
    );
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage />;
      case 'chat':
        return <ChatPage />;
      case 'history':
        return <HistoryPage />;
      case 'contacts':
        return <ContactsPage />;
      default:
        return <HomePage />;
/**
 * AI SQL Chatbot - Main Application
 * Provides natural language interface to query databases
 */
import { useState, useEffect, useRef } from 'react';
import { aiChatbotApi, type Message } from './api/ai-chatbot';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import { Database, AlertCircle, CheckCircle2 } from 'lucide-react';
import './App.css';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [databaseStatus, setDatabaseStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Check database connection on mount
  useEffect(() => {
    checkDatabaseConnection();

    // Add welcome message
    const welcomeMessage: Message = {
      id: 'welcome',
      role: 'assistant',
      content: 'Hello! I\'m your AI SQL Assistant. Ask me anything about your data in plain English, and I\'ll generate SQL queries and visualizations for you.',
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, []);

  const checkDatabaseConnection = async () => {
    try {
      setDatabaseStatus('checking');
      await aiChatbotApi.testConnection(1); // Default database ID
      setDatabaseStatus('connected');
    } catch {
      setDatabaseStatus('disconnected');
    }
  };

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      // Send query to AI backend
      const response = await aiChatbotApi.sendQuery(content, 1);

      // Create assistant message
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.result,
        timestamp: new Date(),
        sql_query: response.sql_query,
        visualization: response.visualization,
        execution_time_ms: response.execution_time_ms,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process your query');

      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${err instanceof Error ? err.message : 'Unknown error'}. Please try again.`,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header currentPage={currentPage} onNavigate={setCurrentPage} />
      {renderPage()}
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <Database size={24} />
            <h1>AI SQL Chatbot</h1>
          </div>
          <div className={`database-status status-${databaseStatus}`}>
            {databaseStatus === 'connected' ? (
              <>
                <CheckCircle2 size={16} />
                <span>Connected</span>
              </>
            ) : databaseStatus === 'disconnected' ? (
              <>
                <AlertCircle size={16} />
                <span>Disconnected</span>
              </>
            ) : (
              <span>Checking...</span>
            )}
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="chat-container">
        <div className="messages-container">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {loading && (
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="error-banner">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Input */}
        <ChatInput
          onSend={handleSendMessage}
          disabled={databaseStatus !== 'connected'}
          loading={loading}
        />
      </div>

      {/* Suggested Queries */}
      {messages.length === 1 && (
        <div className="suggested-queries">
          <h3>Try asking:</h3>
          <div className="suggestions">
            <button
              onClick={() => handleSendMessage('How many transactions were made in Almaty?')}
              className="suggestion-button"
            >
              How many transactions in Almaty?
            </button>
            <button
              onClick={() => handleSendMessage('Show me top 10 cities by transaction count')}
              className="suggestion-button"
            >
              Top 10 cities by transactions
            </button>
            <button
              onClick={() => handleSendMessage('What is the distribution of transaction amounts?')}
              className="suggestion-button"
            >
              Transaction amount distribution
            </button>
            <button
              onClick={() => handleSendMessage('Show transactions over time')}
              className="suggestion-button"
            >
              Transactions over time
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
