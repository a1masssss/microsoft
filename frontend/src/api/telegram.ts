/**
 * API methods for Telegram Mini App
 */
import { createApiClient } from './client';

export interface User {
  user_id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  language_code?: string;
}

export interface QueryResponse {
  id: number;
  query: string;
  response: string;
  success: boolean;
  created_at: string;
}

export interface HistoryItem {
  id: number;
  query: string;
  response: string;
  success: boolean;
  created_at: string;
}

export const telegramApi = {
  /**
   * Get current user info
   */
  getCurrentUser: async (initData: string): Promise<User> => {
    const client = createApiClient(initData);
    const response = await client.get('/me/');
    return response.data;
  },

  /**
   * Send query
   */
  sendQuery: async (initData: string, query: string): Promise<QueryResponse> => {
    const client = createApiClient(initData);
    const response = await client.post('/query/', { query });
    return response.data;
  },

  /**
   * Get query history
   */
  getHistory: async (initData: string, limit = 10): Promise<HistoryItem[]> => {
    const client = createApiClient(initData);
    const response = await client.get('/history/', { params: { limit } });
    return response.data.history;
  },
};
