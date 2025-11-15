"use client";

import { useEffect, useRef, useCallback } from "react";
import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import {
    ImageIcon,
    FileUp,
    Figma,
    MonitorIcon,
    ArrowUpIcon,
    Paperclip,
    PlusIcon,
} from "lucide-react";
import { aiChatbotApi, type Message } from "@/api/ai-chatbot";
import { ChatMessage } from "@/components/chat/ChatMessage";

interface UseAutoResizeTextareaProps {
    minHeight: number;
    maxHeight?: number;
}

function useAutoResizeTextarea({
    minHeight,
    maxHeight,
}: UseAutoResizeTextareaProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const adjustHeight = useCallback(
        (reset?: boolean) => {
            const textarea = textareaRef.current;
            if (!textarea) return;

            if (reset) {
                textarea.style.height = `${minHeight}px`;
                return;
            }

            // Temporarily shrink to get the right scrollHeight
            textarea.style.height = `${minHeight}px`;

            // Calculate new height
            const newHeight = Math.max(
                minHeight,
                Math.min(
                    textarea.scrollHeight,
                    maxHeight ?? Number.POSITIVE_INFINITY
                )
            );

            textarea.style.height = `${newHeight}px`;
        },
        [minHeight, maxHeight]
    );

    useEffect(() => {
        // Set initial height
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = `${minHeight}px`;
        }
    }, [minHeight]);

    // Adjust height on window resize
    useEffect(() => {
        const handleResize = () => adjustHeight();
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, [adjustHeight]);

    return { textareaRef, adjustHeight };
}

export function VercelV0Chat() {
    const [value, setValue] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [databaseStatus, setDatabaseStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const { textareaRef, adjustHeight } = useAutoResizeTextarea({
        minHeight: 60,
        maxHeight: 200,
    });

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Check database connection and add welcome message on mount
    useEffect(() => {
        checkDatabaseConnection();
        const welcomeMessage: Message = {
            id: 'welcome',
            role: 'assistant',
            content: 'Hello! I\'m your AI SQL Assistant. Ask me anything about your data in plain English, and I\'ll generate SQL queries and visualizations for you.',
            timestamp: new Date(),
        };
        setMessages([welcomeMessage]);
    }, []);

    const checkDatabaseConnection = async () => {
        try {
            setDatabaseStatus('checking');
            await aiChatbotApi.testConnection(1);
            setDatabaseStatus('connected');
        } catch {
            setDatabaseStatus('disconnected');
        }
    };

    const handleSendMessage = async (content: string) => {
        if (!content.trim() || loading || databaseStatus !== 'connected') return;

        // Add user message
        const userMessage: Message = {
            id: `user-${Date.now()}`,
            role: 'user',
            content,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setValue("");
        adjustHeight(true);
        setLoading(true);
        setError(null);

        try {
            // Send query to AI backend
            const response = await aiChatbotApi.sendQuery(content, 1);

            // Create assistant message
            const assistantMessage: Message = {
                id: `assistant-${Date.now()}`,
                role: 'assistant',
                content: response.result,
                timestamp: new Date(),
                sql_query: response.sql_query,
                visualization: response.visualization,
                execution_time_ms: response.execution_time_ms,
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to process your query');
            
            // Add error message
            const errorMessage: Message = {
                id: `error-${Date.now()}`,
                role: 'assistant',
                content: `Sorry, I encountered an error: ${err instanceof Error ? err.message : 'Unknown error'}. Please try again.`,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (value.trim() && !loading && databaseStatus === 'connected') {
                handleSendMessage(value.trim());
            }
        }
    };

    const handleSubmit = () => {
        if (value.trim() && !loading && databaseStatus === 'connected') {
            handleSendMessage(value.trim());
        }
    };

    return (
        <div className="flex flex-col items-center w-full max-w-4xl mx-auto p-4 space-y-8">
            <h1 className="text-4xl font-bold text-black dark:text-white">
                What can I help you ship?
            </h1>

            {/* Chat Messages */}
            {messages.length > 0 && (
                <div className="w-full max-h-[60vh] overflow-y-auto space-y-4 px-4">
                    {messages.map((message) => (
                        <ChatMessage key={message.id} message={message} />
                    ))}
                    {loading && (
                        <div className="flex items-center gap-2 text-neutral-400">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                            </div>
                            <span className="text-sm">AI is thinking...</span>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="w-full px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                    {error}
                </div>
            )}

            {/* Database Status */}
            {databaseStatus !== 'checking' && (
                <div className={cn(
                    "px-3 py-1 rounded-full text-xs font-medium",
                    databaseStatus === 'connected' 
                        ? "bg-green-500/10 text-green-400 border border-green-500/20"
                        : "bg-red-500/10 text-red-400 border border-red-500/20"
                )}>
                    {databaseStatus === 'connected' ? '✓ Database Connected' : '✗ Database Disconnected'}
                </div>
            )}

            <div className="w-full">
                <div className="relative bg-neutral-900 rounded-xl border border-neutral-800">
                    <div className="overflow-y-auto">
                        <Textarea
                            ref={textareaRef}
                            value={value}
                            onChange={(e) => {
                                setValue(e.target.value);
                                adjustHeight();
                            }}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask me anything about your data..."
                            disabled={loading || databaseStatus !== 'connected'}
                            className={cn(
                                "w-full px-4 py-3",
                                "resize-none",
                                "bg-transparent",
                                "border-none",
                                "text-white text-sm",
                                "focus:outline-none",
                                "focus-visible:ring-0 focus-visible:ring-offset-0",
                                "placeholder:text-neutral-500 placeholder:text-sm",
                                "min-h-[60px]"
                            )}
                            style={{
                                overflow: "hidden",
                            }}
                        />
                    </div>

                    <div className="flex items-center justify-between p-3">
                        <div className="flex items-center gap-2">
                            <button
                                type="button"
                                className="group p-2 hover:bg-neutral-800 rounded-lg transition-colors flex items-center gap-1"
                            >
                                <Paperclip className="w-4 h-4 text-white" />
                                <span className="text-xs text-zinc-400 hidden group-hover:inline transition-opacity">
                                    Attach
                                </span>
                            </button>
                        </div>

                        <div className="flex items-center gap-2">
                            <button
                                type="button"
                                className="px-2 py-1 rounded-lg text-sm text-zinc-400 transition-colors border border-dashed border-zinc-700 hover:border-zinc-600 hover:bg-zinc-800 flex items-center justify-between gap-1"
                            >
                                <PlusIcon className="w-4 h-4" />
                                Project
                            </button>

                            <button
                                type="button"
                                onClick={handleSubmit}
                                disabled={!value.trim() || loading || databaseStatus !== 'connected'}
                                className={cn(
                                    "px-1.5 py-1.5 rounded-lg text-sm transition-colors border border-zinc-700 hover:border-zinc-600 hover:bg-zinc-800 flex items-center justify-between gap-1 disabled:opacity-50 disabled:cursor-not-allowed",
                                    value.trim() && !loading && databaseStatus === 'connected'
                                        ? "bg-white text-black"
                                        : "text-zinc-400"
                                )}
                            >
                                <ArrowUpIcon
                                    className={cn(
                                        "w-4 h-4",
                                        value.trim() && !loading && databaseStatus === 'connected'
                                            ? "text-black"
                                            : "text-zinc-400"
                                    )}
                                />
                                <span className="sr-only">Send</span>
                            </button>
                        </div>
                    </div>
                </div>

                {/* Suggested Queries - Only show when no messages or just welcome */}
                {messages.length <= 1 && (
                    <div className="flex items-center justify-center gap-3 mt-4 flex-wrap">
                        <ActionButton
                            icon={<ImageIcon className="w-4 h-4" />}
                            label="How many transactions in Almaty?"
                            onClick={() => handleSendMessage('How many transactions were made in Almaty?')}
                        />
                        <ActionButton
                            icon={<Figma className="w-4 h-4" />}
                            label="Top 10 cities by transactions"
                            onClick={() => handleSendMessage('Show me top 10 cities by transaction count')}
                        />
                        <ActionButton
                            icon={<FileUp className="w-4 h-4" />}
                            label="Transaction distribution"
                            onClick={() => handleSendMessage('What is the distribution of transaction amounts?')}
                        />
                        <ActionButton
                            icon={<MonitorIcon className="w-4 h-4" />}
                            label="Transactions over time"
                            onClick={() => handleSendMessage('Show transactions over time')}
                        />
                    </div>
                )}
            </div>
        </div>
    );
}

interface ActionButtonProps {
    icon: React.ReactNode;
    label: string;
    onClick?: () => void;
}

function ActionButton({ icon, label, onClick }: ActionButtonProps) {
    return (
        <button
            type="button"
            onClick={onClick}
            className="flex items-center gap-2 px-4 py-2 bg-neutral-900 hover:bg-neutral-800 rounded-full border border-neutral-800 text-neutral-400 hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!onClick}
        >
            {icon}
            <span className="text-xs">{label}</span>
        </button>
    );
}

