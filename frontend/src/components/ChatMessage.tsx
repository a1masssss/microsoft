/**
 * Chat Message Component
 * Displays individual messages in the chat with optional visualizations
 */
import { useState } from 'react';
import type { Message } from '../api/ai-chatbot';
import { User, Bot, Database, Clock, Download, FileSpreadsheet } from 'lucide-react';
import PlotlyChart from './PlotlyChart';
import { aiChatbotApi } from '../api/ai-chatbot';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
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
    <div className={`chat-message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-header">
        <div className="message-avatar">
          {isUser ? (
            <User size={20} />
          ) : (
            <Bot size={20} />
          )}
        </div>
        <div className="message-meta">
          <span className="message-role">{isUser ? 'You' : 'AI Assistant'}</span>
          <span className="message-time">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>

      <div className="message-content">
        <p>{message.content}</p>

        {/* SQL Query Display */}
        {message.sql_query && (
          <div className="sql-query">
            <div className="sql-header">
              <Database size={16} />
              <span>Generated SQL Query</span>
              <div className="export-buttons">
                <button
                  className="export-btn export-csv"
                  onClick={() => handleExport('csv')}
                  disabled={exporting !== null}
                  title="Export to CSV"
                >
                  <Download size={14} />
                  {exporting === 'csv' ? 'Exporting...' : 'CSV'}
                </button>
                <button
                  className="export-btn export-excel"
                  onClick={() => handleExport('excel')}
                  disabled={exporting !== null}
                  title="Export to Excel"
                >
                  <FileSpreadsheet size={14} />
                  {exporting === 'excel' ? 'Exporting...' : 'Excel'}
                </button>
              </div>
            </div>
            <pre><code>{message.sql_query}</code></pre>
          </div>
        )}

        {/* Visualization Display */}
        {message.visualization && message.visualization.enabled && (
          <div className="visualization-container">
            <PlotlyChart visualization={message.visualization} />

            {/* Insights */}
            {message.visualization.insights && (
              <div className="insights">
                <p>{message.visualization.insights}</p>
              </div>
            )}
          </div>
        )}

        {/* Execution Time */}
        {message.execution_time_ms !== undefined && (
          <div className="execution-time">
            <Clock size={14} />
            <span>{message.execution_time_ms}ms</span>
          </div>
        )}
      </div>
    </div>
  );
}
