import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Sparkles } from 'lucide-react';
import { ChatMessage } from '../components/ChatMessage';
import { ChatInput } from '../components/ChatInput';
import { aiService } from '../services/api';
import { useTelegram } from '../hooks/useTelegram';
import type { Message } from '../types';

export const ChatPage = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { hapticFeedback, showAlert } = useTelegram();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
    };
    setMessages((prev) => [...prev, loadingMessage]);

    hapticFeedback('light');
    setIsLoading(true);

    try {
      const response = await aiService.sendQuery({
        query: content,
        database_id: 1,
      });

      setMessages((prev) => prev.filter((m) => m.id !== loadingMessage.id));

      const aiMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: response.success
          ? response.result || 'Запрос выполнен успешно!'
          : response.error || 'Произошла ошибка',
        timestamp: new Date(),
        sql: response.sql_query,
        result: response.result,
      };

      setMessages((prev) => [...prev, aiMessage]);
      hapticFeedback('medium');
    } catch (error: any) {
      setMessages((prev) => prev.filter((m) => m.id !== loadingMessage.id));

      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: `Ошибка: ${error.message || 'Не удалось выполнить запрос'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);

      hapticFeedback('heavy');
      showAlert('Произошла ошибка при выполнении запроса');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-mastercard-orange to-mastercard-red text-white p-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-semibold">SQL Assistant</h1>
            <p className="text-xs text-white/80">AI-powered database queries</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="h-full flex flex-col items-center justify-center text-center px-6"
          >
            <div className="w-16 h-16 rounded-full bg-gradient-to-r from-mastercard-orange to-mastercard-red flex items-center justify-center mb-4">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Задайте вопрос</h2>
            <p className="text-gray-600 max-w-md mb-6">
              Используйте естественный язык для получения данных из базы
            </p>

            <div className="grid gap-2 w-full max-w-md">
              {[
                'Сколько транзакций было в Алматы?',
                'Топ-5 клиентов по сумме покупок',
                'Средний чек за последний месяц',
              ].map((example, i) => (
                <motion.button
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleSendMessage(example)}
                  className="bg-white border border-gray-200 rounded-xl px-4 py-3 text-left text-sm text-gray-700 hover:border-mastercard-orange hover:bg-orange-50 transition-all"
                >
                  {example}
                </motion.button>
              ))}
            </div>
          </motion.div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t border-gray-200">
        <ChatInput
          onSend={handleSendMessage}
          isLoading={isLoading}
          placeholder="Задайте вопрос..."
        />
      </div>
    </div>
  );
};
