/**
 * API methods for AI SQL Chatbot
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sql_query?: string;
  visualization?: VisualizationData;
  execution_time_ms?: number;
}

export interface VisualizationData {
  enabled: boolean;
  chart_type: string;
  plotly_json: string;
  insights?: string;
  metadata?: {
    chart_type: string;
    truncated?: boolean;
    original_rows?: number;
    sampled?: boolean;
    sample_size?: number;
  };
  config?: {
    title: string;
  };
}

export interface AIQueryResponse {
  success: boolean;
  user_query: string;
  sql_query?: string;
  result: string;
  execution_time_ms: number;
  visualization?: VisualizationData;
  database?: {
    id: number;
    name: string;
    type: string;
  };
  error?: string;
}

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/mcp`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds for AI queries
});

export const aiChatbotApi = {
  /**
   * Send a natural language query to the AI chatbot
   */
  sendQuery: async (query: string, databaseId: number = 1): Promise<AIQueryResponse> => {
    try {
      const response = await api.post('/ai-query/', {
        query,
        database_id: databaseId,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.error || 'Failed to process query');
      }
      throw error;
    }
  },

  /**
   * Get list of available databases
   */
  getDatabases: async () => {
    try {
      const response = await api.get('/databases/');
      return response.data;
    } catch (error) {
      console.error('Error fetching databases:', error);
      return [];
    }
  },

  /**
   * Test database connection
   */
  testConnection: async (databaseId: number) => {
    try {
      const response = await api.post(`/databases/${databaseId}/test_connection/`);
      return response.data;
    } catch (error) {
      console.error('Error testing connection:', error);
      throw error;
    }
  },
};
