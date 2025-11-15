import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for Telegram auth
api.interceptors.request.use((config) => {
  const initData = (window as any).Telegram?.WebApp?.initData;
  if (initData) {
    config.headers['X-Telegram-Init-Data'] = initData;
  }
  return config;
});

export interface AIQueryRequest {
  query: string;
  database_id: number;
}

export interface AIQueryResponse {
  success: boolean;
  query: string;
  sql_query?: string;
  result?: any;
  error?: string;
  execution_time?: number;
}

export interface HistoryItem {
  id: number;
  query: string;
  response: string;
  success: boolean;
  created_at: string;
}

export const aiService = {
  // Send AI query
  sendQuery: async (data: AIQueryRequest): Promise<AIQueryResponse> => {
    const response = await api.post('/api/mcp/ai-query/', data);
    return response.data;
  },

  // Get query history
  getHistory: async (limit: number = 10): Promise<HistoryItem[]> => {
    const response = await api.get('/api/telegram/history/', {
      params: { limit },
    });
    return response.data.history;
  },
};
