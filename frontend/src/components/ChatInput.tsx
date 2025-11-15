import { useState, useRef } from 'react';
import type { ChangeEvent, KeyboardEvent } from 'react';
import { motion } from 'framer-motion';
/**
 * Chat Input Component
 * Text input for sending messages to the AI chatbot
 */
import { useState, type KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

export const ChatInput = ({ onSend, isLoading, placeholder = 'Задайте вопрос...' }: ChatInputProps) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (message.trim() && !isLoading) {
      onSend(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
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

  const handleInput = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    // Auto-resize textarea
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
  };

  return (
    <div className="bg-white border-t border-gray-200 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-end gap-2">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading}
            rows={1}
            className="flex-1 bg-gray-50 text-gray-900 placeholder-gray-400 resize-none outline-none max-h-[120px] min-h-[40px] px-4 py-2 rounded-xl border border-gray-200 focus:border-mastercard-orange focus:ring-1 focus:ring-mastercard-orange transition-all"
          />

          <motion.button
            onClick={handleSend}
            disabled={!message.trim() || isLoading}
            whileTap={{ scale: 0.95 }}
            className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all ${
              message.trim() && !isLoading
                ? 'bg-gradient-to-r from-mastercard-orange to-mastercard-red hover:shadow-lg hover:shadow-mastercard-orange/50'
                : 'bg-gray-300 cursor-not-allowed'
            }`}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 text-white animate-spin" />
            ) : (
              <Send className="w-5 h-5 text-white" />
            )}
          </motion.button>
        </div>
      </div>
    </div>
  );
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
