import { useState } from 'react';
import { motion } from 'framer-motion';
import { Layers, CheckCircle2, AlertCircle } from 'lucide-react';
import { aiService } from '../services/api';
import type { DeepQueryResponse } from '../services/api';

interface AdvancedToolsProps {
  databaseId: number;
  hapticFeedback: (type?: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
  showAlert: (message: string) => void;
}

export const AdvancedTools = ({ databaseId, hapticFeedback, showAlert }: AdvancedToolsProps) => {
  const [deepSql, setDeepSql] = useState('');
  const [deepTables, setDeepTables] = useState('');
  const [includeListTables, setIncludeListTables] = useState(true);
  const [includeTableInfo, setIncludeTableInfo] = useState(false);
  const [deepResult, setDeepResult] = useState<DeepQueryResponse | null>(null);
  const [isDeepLoading, setIsDeepLoading] = useState(false);

  const handleDeepQuery = async (event: React.FormEvent) => {
    event.preventDefault();
    const trimmedSql = deepSql.trim();
    if (!trimmedSql) {
      showAlert('Введите SQL для глубокого запроса');
      return;
    }

    const operations = [];
    if (includeListTables) {
      operations.push({ type: 'list_tables' } as const);
    }
    if (includeTableInfo) {
      const tables = deepTables
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);
      if (tables.length === 0) {
        showAlert('Укажите минимум одну таблицу для операции Table Info или выключите её');
        return;
      }
      operations.push({ type: 'table_info', tables } as const);
    }
    operations.push({ type: 'query', sql: trimmedSql } as const);

    setIsDeepLoading(true);
    try {
      const response = await aiService.runDeepQuery({
        database_id: databaseId,
        operations,
      });
      setDeepResult(response);
      hapticFeedback('medium');
      showAlert(response.all_successful ? 'Глубокий запрос выполнен' : 'Есть ошибки в цепочке');
    } catch (error: any) {
      hapticFeedback('heavy');
      showAlert(error?.response?.data?.error || 'Ошибка при выполнении Deep Query');
    } finally {
      setIsDeepLoading(false);
    }
  };

  return (
    <div className="mt-10 space-y-6">
      <div className="flex items-center gap-2 text-xs uppercase tracking-widest text-gray-500">
        <span className="h-px flex-1 bg-gray-200" />
        Advanced SQL Tools
        <span className="h-px flex-1 bg-gray-200" />
      </div>

      <div className="grid gap-4">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-gray-100 bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="rounded-2xl bg-gradient-to-r from-[#ff9966] to-[#ff5e62] p-2 text-white">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Глубокий запрос</h3>
              <p className="text-sm text-gray-500">Цепочка list/table info/query</p>
            </div>
          </div>

          <form className="space-y-3" onSubmit={handleDeepQuery}>
            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={includeListTables}
                onChange={(e) => setIncludeListTables(e.target.checked)}
                className="rounded border-gray-300 text-[#ff5e62] focus:ring-[#ff5e62]"
              />
              Включить List Tables
            </label>

            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={includeTableInfo}
                onChange={(e) => setIncludeTableInfo(e.target.checked)}
                className="rounded border-gray-300 text-[#ff5e62] focus:ring-[#ff5e62]"
              />
              Включить Table Info
            </label>

            {includeTableInfo && (
              <input
                type="text"
                value={deepTables}
                onChange={(e) => setDeepTables(e.target.value)}
                placeholder="users, transactions"
                className="w-full rounded-2xl border border-gray-200 bg-gray-50 px-3 py-2 text-sm focus:border-gray-400 focus:bg-white focus:outline-none"
              />
            )}

            <textarea
              value={deepSql}
              onChange={(e) => setDeepSql(e.target.value)}
              placeholder="SELECT * FROM transactions LIMIT 10;"
              className="w-full rounded-2xl border border-gray-200 bg-gray-50 px-3 py-2 text-sm focus:border-gray-400 focus:bg-white focus:outline-none"
              rows={4}
            />

            <motion.button
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isDeepLoading}
              className="w-full rounded-2xl bg-gray-900 px-4 py-2 text-white transition-colors hover:bg-gray-800 disabled:opacity-50"
            >
              {isDeepLoading ? 'Выполнение...' : 'Запустить цепочку'}
            </motion.button>
          </form>

          {deepResult && (
            <div className="mt-4 rounded-2xl border border-gray-100 bg-gray-50 p-3 text-sm text-gray-700 space-y-2">
              <div className="flex items-center gap-2 font-semibold">
                {deepResult.all_successful ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-red-500" />
                )}
                {deepResult.all_successful ? 'Успешно' : 'Есть ошибки'}
              </div>
              <p>Операций: {deepResult.executed_operations}</p>
              <p>Успешно: {deepResult.successful_operations}</p>
              <p>Провалено: {deepResult.failed_operations}</p>
            </div>
          )}
        </motion.div>

      </div>
    </div>
  );
};
