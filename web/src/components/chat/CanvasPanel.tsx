/**
 * Canvas Panel Component
 * Displays SQL query and Visualization in a side panel (like Gemini/Claude)
 */
import { useState } from 'react';
import type { Message } from '@/api/ai-chatbot';
import { Database, Download, FileSpreadsheet, X, Clock } from 'lucide-react';
import { PlotlyChart } from './PlotlyChart';
import { aiChatbotApi } from '@/api/ai-chatbot';

interface CanvasPanelProps {
  message: Message | null;
  onClose?: () => void;
}

export function CanvasPanel({ message, onClose }: CanvasPanelProps) {
  const [exporting, setExporting] = useState<'csv' | 'excel' | null>(null);

  if (!message) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-neutral-900/50 border-l border-neutral-800">
        <div className="text-center text-neutral-500">
          <p className="text-sm">Select a message to view SQL query and visualization</p>
        </div>
      </div>
    );
  }

  const handleExport = async (format: 'csv' | 'excel') => {
    if (!message.sql_query) return;

    setExporting(format);
    try {
      const { blob, filename } = await aiChatbotApi.exportData(
        message.sql_query,
        format,
        1,
      );

      if (blob.size === 0) {
        throw new Error('Exported file is empty. Please check your query results.');
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      
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
    <div className="w-full h-full bg-neutral-900 border-l border-neutral-800 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-800 bg-neutral-900/50">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <Database size={16} className="text-neutral-400 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-neutral-200 truncate">Query Details</h3>
            {message.timestamp && (
              <p className="text-xs text-neutral-500 mt-0.5">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            )}
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 hover:bg-neutral-800 rounded transition-colors flex-shrink-0 ml-2"
            title="Close panel"
          >
            <X size={16} className="text-neutral-400" />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* SQL Query */}
        {message.sql_query && (
          <div className="bg-black/40 rounded-lg overflow-hidden border border-neutral-800">
            <div className="flex items-center justify-between px-3 py-2 bg-black/60 border-b border-neutral-800">
              <div className="flex items-center gap-2">
                <Database size={14} className="text-neutral-400" />
                <span className="text-xs font-semibold text-neutral-300 uppercase tracking-wide">
                  Generated SQL Query
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  className="flex items-center gap-1 px-2 py-1 text-xs bg-neutral-800 hover:bg-neutral-700 rounded transition-colors disabled:opacity-50"
                  onClick={() => handleExport('csv')}
                  disabled={exporting !== null}
                  title="Export to CSV"
                >
                  <Download size={12} />
                  {exporting === 'csv' ? 'Exporting...' : 'CSV'}
                </button>
                <button
                  className="flex items-center gap-1 px-2 py-1 text-xs bg-neutral-800 hover:bg-neutral-700 rounded transition-colors disabled:opacity-50"
                  onClick={() => handleExport('excel')}
                  disabled={exporting !== null}
                  title="Export to Excel"
                >
                  <FileSpreadsheet size={12} />
                  {exporting === 'excel' ? 'Exporting...' : 'Excel'}
                </button>
              </div>
            </div>
            <pre className="px-4 py-3 text-xs overflow-x-auto">
              <code className="text-blue-300 font-mono">{message.sql_query}</code>
            </pre>
          </div>
        )}

        {/* Data Preview Table */}
        {message.data_preview && message.data_preview.rows.length > 0 && (
          <div className="bg-black/40 rounded-lg overflow-hidden border border-neutral-800">
            <div className="px-3 py-2 bg-black/60 border-b border-neutral-800">
              <span className="text-xs font-semibold text-neutral-300">
                Showing {message.data_preview.preview_rows} of {message.data_preview.total_rows} rows
                {message.data_preview.has_more && (
                  <span className="text-yellow-400 ml-2">(Use export buttons above to get all data)</span>
                )}
              </span>
            </div>
            <div className="overflow-x-auto max-h-96">
              <table className="w-full text-xs">
                <thead className="bg-black/60 sticky top-0">
                  <tr>
                    {message.data_preview.columns.map((col, idx) => (
                      <th key={idx} className="px-3 py-2 text-left font-semibold text-neutral-300 border-b border-neutral-700">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {message.data_preview.rows.map((row, rowIdx) => (
                    <tr key={rowIdx} className="border-b border-neutral-800 hover:bg-neutral-800/30 transition-colors">
                      {message.data_preview!.columns.map((col, colIdx) => (
                        <td key={colIdx} className="px-3 py-2 text-neutral-400">
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

        {/* Visualization */}
        {message.visualization && message.visualization.enabled && (
          <div className="space-y-2">
            <PlotlyChart visualization={message.visualization} />
            
            {/* Insights */}
            {message.visualization.insights && (
              <div className="px-3 py-2 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                <p className="text-xs text-blue-300">{message.visualization.insights}</p>
              </div>
            )}
          </div>
        )}

        {/* Execution Time */}
        {message.execution_time_ms !== undefined && (
          <div className="flex items-center gap-2 text-xs text-neutral-400">
            <Clock size={12} />
            <span>Execution time: {message.execution_time_ms}ms</span>
          </div>
        )}

        {/* Empty State */}
        {!message.sql_query && !message.visualization && (
          <div className="text-center text-neutral-500 py-8">
            <p className="text-sm">No SQL query or visualization available for this message</p>
          </div>
        )}
      </div>
    </div>
  );
}

