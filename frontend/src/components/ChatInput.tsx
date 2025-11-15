/**
 * Chat Input Component
 * Text input for sending messages to the AI chatbot
 */
import { useState, type KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  loading?: boolean;
}

export default function ChatInput({ onSend, disabled, loading }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled && !loading) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-input-container">
      <div className="chat-input-wrapper">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your data... (e.g., How many transactions in Almaty?)"
          disabled={disabled || loading}
          rows={1}
          className="chat-input"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || disabled || loading}
          className="send-button"
          aria-label="Send message"
        >
          {loading ? (
            <Loader2 size={20} className="spinner" />
          ) : (
            <Send size={20} />
          )}
        </button>
      </div>
      <div className="input-hint">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
}
