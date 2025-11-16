/**
 * Chat Message Component
 * Displays individual messages in the chat with optional visualizations
 */
import { useState } from 'react';
import type { Message } from '@/api/ai-chatbot';
import { User, Bot, Database, Clock, Download, FileSpreadsheet } from 'lucide-react';
import { PlotlyChart } from './PlotlyChart';
import { aiChatbotApi } from '@/api/ai-chatbot';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const [exporting, setExporting] = useState<'csv' | 'excel' | null>(null);

  const handleExport = async (format: 'csv' | 'excel') => {
    if (!message.sql_query) return;

    setExporting(format);
    try {
      const { blob, filename } = await aiChatbotApi.exportData(
        message.sql_query,
        format,
        1, // database_id - could be passed as prop if needed
      );

      // Verify blob is not empty
      if (blob.size === 0) {
        throw new Error('Exported file is empty. Please check your query results.');
      }

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      
      // Clean up after a short delay
      setTimeout(() => {
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }, 100);
    } catch (error) {
      console.error('Export failed:', error);
      alert(error instanceof Error ? error.message : 'Failed to export data');
    } finally {
      setExporting(null);
    }
  };

  return (
    <div className={`flex flex-col gap-2 ${isUser ? 'items-end' : 'items-start'}`}>
      <div className={`flex items-start gap-3 max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white' 
            : 'bg-neutral-800 text-neutral-300'
        }`}>
          {isUser ? <User size={18} /> : <Bot size={18} />}
        </div>
        
        <div className={`flex flex-col gap-2 ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white'
              : 'bg-neutral-800 text-neutral-200'
          }`}>
            <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>

            {/* SQL Query Display */}
            {message.sql_query && (
              <div className="mt-3 bg-black/20 dark:bg-white/10 rounded-lg overflow-hidden">
                <div className="flex items-center justify-between px-3 py-2 bg-black/30 dark:bg-white/20">
                  <div className="flex items-center gap-2">
                    <Database size={14} />
                    <span className="text-xs font-semibold uppercase tracking-wide">Generated SQL Query</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      className="flex items-center gap-1 px-2 py-1 text-xs bg-white/10 hover:bg-white/20 rounded transition-colors disabled:opacity-50"
                      onClick={() => handleExport('csv')}
                      disabled={exporting !== null}
                      title="Export to CSV"
                    >
                      <Download size={12} />
                      {exporting === 'csv' ? 'Exporting...' : 'CSV'}
                    </button>
                    <button
                      className="flex items-center gap-1 px-2 py-1 text-xs bg-white/10 hover:bg-white/20 rounded transition-colors disabled:opacity-50"
                      onClick={() => handleExport('excel')}
                      disabled={exporting !== null}
                      title="Export to Excel"
                    >
                      <FileSpreadsheet size={12} />
                      {exporting === 'excel' ? 'Exporting...' : 'Excel'}
                    </button>
                  </div>
                </div>
                <pre className="px-3 py-2 text-xs overflow-x-auto">
                  <code className="text-blue-300">{message.sql_query}</code>
                </pre>
              </div>
            )}

            {/* Data Preview Table */}
            {message.data_preview && message.data_preview.rows.length > 0 && (
              <div className="mt-3 bg-black/20 dark:bg-white/10 rounded-lg overflow-hidden">
                <div className="px-3 py-2 bg-black/30 dark:bg-white/20">
                  <span className="text-xs font-semibold">
                    Showing {message.data_preview.preview_rows} of {message.data_preview.total_rows} rows
                    {message.data_preview.has_more && (
                      <span className="text-yellow-400 ml-2">(Use export buttons above to get all data)</span>
                    )}
                  </span>
                </div>
                <div className="overflow-x-auto max-h-96">
                  <table className="w-full text-xs">
                    <thead className="bg-black/40 dark:bg-white/10 sticky top-0">
                      <tr>
                        {message.data_preview.columns.map((col, idx) => (
                          <th key={idx} className="px-3 py-2 text-left font-semibold border-b border-white/10">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {message.data_preview.rows.map((row, rowIdx) => (
                        <tr key={rowIdx} className="border-b border-white/5 hover:bg-white/5">
                          {message.data_preview!.columns.map((col, colIdx) => (
                            <td key={colIdx} className="px-3 py-2">
                              {row[col] !== null && row[col] !== undefined
                                ? String(row[col])
                                : '-'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Visualization Display */}
            {message.visualization && message.visualization.enabled && (
              <div className="mt-3">
                <PlotlyChart visualization={message.visualization} />

                {/* Insights */}
                {message.visualization.insights && (
                  <div className="mt-2 px-3 py-2 bg-blue-500/20 rounded-lg">
                    <p className="text-xs text-blue-200">{message.visualization.insights}</p>
                  </div>
                )}
              </div>
            )}

            {/* Execution Time */}
            {message.execution_time_ms !== undefined && (
              <div className="flex items-center gap-1 mt-2 text-xs opacity-70">
                <Clock size={12} />
                <span>{message.execution_time_ms}ms</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

