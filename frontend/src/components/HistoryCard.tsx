import { motion } from 'framer-motion';
import { Clock, CheckCircle, XCircle } from 'lucide-react';
import type { HistoryItem } from '../services/api';

interface HistoryCardProps {
  item: HistoryItem;
  onClick?: () => void;
}

export const HistoryCard = ({ item, onClick }: HistoryCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -3 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="relative cursor-pointer rounded-2xl border border-gray-100 bg-white p-4 shadow-sm transition-all hover:shadow-md"
    >
      <div className="mb-3 flex items-start justify-between">
        <div className="flex items-center gap-2">
          {item.success ? (
            <CheckCircle className="w-5 h-5 text-emerald-500" />
          ) : (
            <XCircle className="w-5 h-5 text-red-400" />
          )}
          <span className="flex items-center gap-1 text-xs text-gray-400">
            <Clock className="w-3 h-3" />
            {new Date(item.created_at).toLocaleDateString('ru-RU', {
              day: 'numeric',
              month: 'short',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
      </div>

      <h3 className="mb-2 line-clamp-2 font-medium text-gray-900">{item.query}</h3>
      <p className="line-clamp-3 text-sm text-gray-500">{item.response}</p>
    </motion.div>
  );
};
