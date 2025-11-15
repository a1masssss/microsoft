import { motion } from 'framer-motion';
import { User, Bot, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import type { Message } from '../types';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage = ({ message }: ChatMessageProps) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.type === 'user';

  const handleCopy = async (text: string) => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-4`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-gradient-to-r from-mastercard-orange to-mastercard-red'
            : 'bg-gray-200'
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-gray-600" />
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-gradient-to-r from-mastercard-orange to-mastercard-red text-white rounded-tr-sm'
              : 'bg-white border border-gray-200 text-gray-900 rounded-tl-sm'
          }`}
        >
          {/* Loading animation */}
          {message.isLoading ? (
            <div className="flex gap-1 py-2">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className={`w-2 h-2 rounded-full ${isUser ? 'bg-white/50' : 'bg-mastercard-orange/50'}`}
                  animate={{
                    y: [0, -10, 0],
                  }}
                  transition={{
                    duration: 0.6,
                    repeat: Infinity,
                    delay: i * 0.1,
                  }}
                />
              ))}
            </div>
          ) : (
            <>
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

              {/* SQL Query Display */}
              {message.sql && (
                <div className="mt-3 rounded-lg bg-gray-100 p-3 relative">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono text-gray-600">SQL Query</span>
                    <button
                      onClick={() => handleCopy(message.sql!)}
                      className="p-1 hover:bg-gray-200 rounded transition-colors"
                    >
                      {copied ? (
                        <Check className="w-4 h-4 text-green-600" />
                      ) : (
                        <Copy className="w-4 h-4 text-gray-500" />
                      )}
                    </button>
                  </div>
                  <pre className="text-xs font-mono text-mastercard-orange overflow-x-auto">
                    {message.sql}
                  </pre>
                </div>
              )}

              {/* Result Display */}
              {message.result && (
                <div className="mt-3 rounded-lg bg-gray-50 p-3">
                  <span className="text-xs font-mono text-gray-600 mb-2 block">Result</span>
                  <pre className="text-xs font-mono text-gray-700 overflow-x-auto max-h-40">
                    {JSON.stringify(message.result, null, 2)}
                  </pre>
                </div>
              )}
            </>
          )}
        </div>

        {/* Timestamp */}
        <p className={`text-xs text-gray-500 mt-1 px-2 ${isUser ? 'text-right' : 'text-left'}`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </motion.div>
  );
};
