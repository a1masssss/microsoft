import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  MessageSquare,
  Sparkles,
} from 'lucide-react';
import { ChatMessage } from '../components/ChatMessage';
import { aiService } from '../services/api';
import { useTelegram } from '../hooks/useTelegram';
import type { Message } from '../types';
import AnimatedBackground from '../components/ui/animated-background';
import { PromptBox } from '../components/ui/chatgpt-prompt-input';

export const ChatPage = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [promptVersion, setPromptVersion] = useState(0);
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

  const quickExamples = [
    {
      id: 'almaty',
      title: 'Город Алматы',
      description: 'Сколько транзакций обработано за неделю?',
      prompt: 'Сколько транзакций было в Алматы за последнюю неделю?',
    },
    {
      id: 'topClients',
      title: 'Топ клиентов',
      description: 'Кто лидирует по сумме покупок за месяц?',
      prompt: 'Покажи топ 5 клиентов по сумме покупок за месяц',
    },
    {
      id: 'avgCheck',
      title: 'Средний чек',
      description: 'Динамика среднего чека по городам',
      prompt: 'Средний чек по городам за последний месяц',
    },
  ];

  const handleFormSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const message = (formData.get('message') as string | null)?.trim();
    if (!message || isLoading) return;
    handleSendMessage(message);
    setPromptVersion((prev) => prev + 1);
    event.currentTarget.reset();
  };

  const handlePromptKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      const form = (event.target as HTMLTextAreaElement).form;
      form?.requestSubmit();
    }
  };

  const handleVoiceResult = (transcript: string) => {
    const cleaned = transcript.trim();
    if (!cleaned || isLoading) return;
    hapticFeedback('medium');
    handleSendMessage(cleaned);
  };

  return (
    <div className="flex h-screen flex-col bg-white">
      <section className="border-b border-gray-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-gradient-to-r from-[#ff9966] to-[#ff5e62] p-3 shadow-sm">
              <MessageSquare className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-widest text-gray-500">SQL Assistant</p>
              <h1 className="text-2xl font-semibold text-gray-900">Чат аналитики</h1>
            </div>
          </div>
        </div>
      </section>

      <div className="flex-1 overflow-y-auto bg-gray-50">
        <div className="mx-auto flex h-full w-full max-w-4xl flex-col gap-6 px-4 py-6">
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-3xl border border-gray-100 bg-white p-6 shadow-xl"
            >
              <div className="flex items-start gap-4">
                <div className="rounded-2xl bg-gradient-to-r from-[#ff9966] to-[#ff5e62] p-3">
                  <Sparkles className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Задайте вопрос</h2>
                  <p className="text-sm text-gray-600">
                    Используйте естественный язык, чтобы получить SQL и ответы мгновенно.
                  </p>
                </div>
              </div>
              <div className="mt-6 grid gap-3">
                <AnimatedBackground
                  enableHover
                  className="rounded-2xl bg-gradient-to-r from-[#ffede2] to-[#ffe7e0]"
                  transition={{ type: 'spring', bounce: 0.2, duration: 0.3 }}
                >
                  {quickExamples.map((example) => (
                    <button
                      key={example.id}
                      data-id={example.id}
                      onClick={() => handleSendMessage(example.prompt)}
                      className="w-full overflow-hidden rounded-2xl border border-gray-200 bg-white p-4 text-left shadow-sm transition-all hover:shadow-md data-[checked=true]:border-transparent data-[checked=true]:text-white"
                    >
                      <p className="text-sm font-semibold text-gray-900 data-[checked=true]:text-white">
                        {example.title}
                      </p>
                      <p className="text-sm text-gray-500 data-[checked=true]:text-white/90">
                        {example.description}
                      </p>
                    </button>
                  ))}
                </AnimatedBackground>
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
      </div>

      <div className="border-t border-gray-200 bg-white/90 backdrop-blur py-4 shadow-[0_-8px_30px_rgba(15,23,42,0.08)]">
        <form
          onSubmit={handleFormSubmit}
          className="mx-auto w-full max-w-3xl px-4"
          key={promptVersion}
        >
          <PromptBox
            name="message"
            placeholder="Напишите, что хотите узнать..."
            onKeyDown={handlePromptKeyDown}
            onVoiceResult={handleVoiceResult}
            onVoiceError={(message) => {
              showAlert(message);
              hapticFeedback('heavy');
            }}
          />
        </form>
      </div>
    </div>
  );
};
