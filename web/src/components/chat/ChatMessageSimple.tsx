/**
 * Simple Chat Message Component
 * Displays only the text content (no SQL/visualization)
 */
import type { Message } from '@/api/ai-chatbot';
import { User, Bot, PanelRight } from 'lucide-react';

interface ChatMessageSimpleProps {
  message: Message;
  onSelect?: () => void;
  isSelected?: boolean;
  hasCanvas?: boolean;
}

export function ChatMessageSimple({ message, onSelect, isSelected, hasCanvas }: ChatMessageSimpleProps) {
  const isUser = message.role === 'user';
  const hasDetails = message.sql_query || message.visualization;

  return (
    <div 
      className={`flex flex-col gap-2 ${isUser ? 'items-end' : 'items-start'} transition-all ${
        hasDetails ? 'cursor-pointer' : 'cursor-default'
      } ${isSelected ? 'opacity-100' : 'opacity-90 hover:opacity-100'}`}
      onClick={hasDetails ? onSelect : undefined}
    >
      <div className={`flex items-start gap-3 max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white' 
            : 'bg-neutral-800 text-neutral-300'
        }`}>
          {isUser ? <User size={18} /> : <Bot size={18} />}
        </div>
        
        <div className={`flex flex-col gap-2 ${isUser ? 'items-end' : 'items-start'} flex-1`}>
          <div className={`px-4 py-3 rounded-2xl relative ${
            isUser
              ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white'
              : 'bg-neutral-800 text-neutral-200'
          } ${isSelected && hasCanvas ? 'ring-2 ring-blue-500 shadow-lg shadow-blue-500/20' : ''} transition-all`}>
            <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
            
            {/* Show indicator if message has SQL/visualization */}
            {hasDetails && (
              <div className="mt-2 pt-2 border-t border-white/10 dark:border-neutral-700">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 text-xs opacity-70">
                    <PanelRight size={12} />
                    <span>View in canvas</span>
                  </div>
                  {isSelected && hasCanvas && (
                    <span className="px-2 py-0.5 text-xs bg-blue-500/20 text-blue-300 rounded border border-blue-500/30">
                      Active
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

