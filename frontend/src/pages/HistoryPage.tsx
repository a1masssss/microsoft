import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Loader2, RefreshCw, Clock } from 'lucide-react';
import { HistoryCard } from '../components/HistoryCard';
import { aiService } from '../services/api';
import { useTelegram } from '../hooks/useTelegram';
import type { HistoryItem } from '../services/api';

export const HistoryPage = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { hapticFeedback, showAlert } = useTelegram();

  const loadHistory = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await aiService.getHistory(20);
      setHistory(data);
      hapticFeedback('light');
    } catch (err: any) {
      setError(err.message || 'Не удалось загрузить историю');
      showAlert('Ошибка загрузки истории');
      hapticFeedback('heavy');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleRefresh = () => {
    hapticFeedback('medium');
    loadHistory();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gray-100">
              <Clock className="w-5 h-5 text-gray-800" />
            </div>
            <div>
              <h1 className="font-semibold text-gray-900">История запросов</h1>
              <p className="text-xs text-gray-500">Ваши предыдущие запросы</p>
            </div>
          </div>

          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleRefresh}
            disabled={isLoading}
            className="rounded-full border border-gray-200 p-2 text-gray-700 transition-colors hover:bg-gray-100 disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
          </motion.button>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-gray-400 animate-spin" />
          </div>
        ) : error ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-20"
          >
            <p className="text-red-500 mb-4">{error}</p>
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={handleRefresh}
              className="px-6 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 shadow-sm transition-all hover:shadow-md"
            >
              Попробовать снова
            </motion.button>
          </motion.div>
        ) : history.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-20"
          >
            <p className="text-gray-600 mb-2">История пуста</p>
            <p className="text-sm text-gray-500">Задайте первый вопрос в чате!</p>
          </motion.div>
        ) : (
          <div className="grid gap-4">
            {history.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <HistoryCard item={item} onClick={() => hapticFeedback('light')} />
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
