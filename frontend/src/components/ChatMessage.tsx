/**
 * Chat Message Component
 * Displays individual messages in the chat with optional visualizations
 */
import type { Message } from '../api/ai-chatbot';
import { User, Bot, Database, Clock } from 'lucide-react';
import PlotlyChart from './PlotlyChart';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

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
