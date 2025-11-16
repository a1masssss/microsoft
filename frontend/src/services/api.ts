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
    config.headers['Authorization'] = `tma ${initData}`;
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

export type DeepQueryOperation =
  | { type: 'list_tables' }
  | { type: 'table_info'; tables: string[] }
  | { type: 'query'; sql: string };

export interface DeepQueryRequest {
  database_id: number;
  operations: DeepQueryOperation[];
}

export interface DeepQueryResult {
  operation: string;
  index: number;
  success: boolean;
  error?: string;
  skipped?: boolean;
  result?: any;
}

export interface DeepQueryResponse {
  database: {
    id: number;
    name: string;
    type: string;
  };
  results: DeepQueryResult[];
  total_operations: number;
  executed_operations: number;
  successful_operations: number;
  failed_operations: number;
  total_execution_time_ms: number;
  all_successful: boolean;
}

export interface ExportQueryRequest {
  sql_query: string;
  database_id: number;
  format?: 'csv' | 'excel' | 'xlsx';
  filename?: string;
}

export interface ExportQueryResponse {
  blob: Blob;
  filename: string;
  contentType: string;
}

export const aiService = {
  // Send AI query
  sendQuery: async (data: AIQueryRequest): Promise<AIQueryResponse> => {
    const response = await api.post('/api/mcp/ai-query/', data);
    return response.data;
  },

  // Run deep query chain
  runDeepQuery: async (data: DeepQueryRequest): Promise<DeepQueryResponse> => {
    const response = await api.post('/api/mcp/deep-query/', data);
    return response.data;
  },

  // Export query results
  exportQuery: async (data: ExportQueryRequest): Promise<ExportQueryResponse> => {
    try {
      const response = await api.post('/api/mcp/export/', data, {
        responseType: 'blob',
      });

      const contentType = response.headers['content-type'] || '';
      // If backend returned JSON (likely error), parse and throw
      if (contentType.includes('application/json')) {
        const text = await response.data.text();
        const json = JSON.parse(text);
        throw new Error(json?.error || 'Не удалось экспортировать данные');
      }

      const disposition = response.headers['content-disposition'] || '';
      const filenameMatch = disposition.match(/filename\*?=.*?''?([^;]+)/i);
      const filename = filenameMatch
        ? decodeURIComponent(filenameMatch[1].replace(/"/g, ''))
        : data.filename || 'query_results';

      return {
        blob: response.data,
        filename,
        contentType: contentType || 'application/octet-stream',
      };
    } catch (error: any) {
      const blob = error?.response?.data;
      if (blob instanceof Blob) {
        try {
          const text = await blob.text();
          const json = JSON.parse(text);
          throw new Error(json?.error || 'Не удалось экспортировать данные');
        } catch {
          throw new Error('Не удалось экспортировать данные');
        }
      }
      throw error;
    }
  },

  // Get query history
  getHistory: async (limit: number = 10): Promise<HistoryItem[]> => {
    const response = await api.get('/api/telegram/history/', {
      params: { limit },
    });
    return response.data.history;
  },
};
