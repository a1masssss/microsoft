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
      <div className="bg-gradient-to-r from-mastercard-orange to-mastercard-red text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-semibold">История запросов</h1>
              <p className="text-xs text-white/80">Ваши предыдущие запросы</p>
            </div>
          </div>

          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleRefresh}
            disabled={isLoading}
            className="p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
          </motion.button>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-mastercard-orange animate-spin" />
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
              className="px-6 py-3 bg-gradient-to-r from-mastercard-orange to-mastercard-red text-white rounded-xl hover:shadow-lg transition-all"
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
