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
      whileHover={{ scale: 1.02, y: -4 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-4 cursor-pointer hover:bg-white/15 transition-all"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          {item.success ? (
            <CheckCircle className="w-5 h-5 text-green-400" />
          ) : (
            <XCircle className="w-5 h-5 text-red-400" />
          )}
          <span className="text-xs text-gray-400 flex items-center gap-1">
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

      {/* Query */}
      <h3 className="text-white font-medium mb-2 line-clamp-2">{item.query}</h3>

      {/* Response Preview */}
      <p className="text-sm text-gray-400 line-clamp-3">{item.response}</p>

      {/* Gradient Border Effect */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500/0 via-purple-500/0 to-pink-500/0 group-hover:from-blue-500/20 group-hover:via-purple-500/20 group-hover:to-pink-500/20 transition-all duration-300 pointer-events-none" />
    </motion.div>
  );
};
