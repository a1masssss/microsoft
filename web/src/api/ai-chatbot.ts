/**
 * API methods for AI SQL Chatbot
 */
import axios from 'axios';

// Use relative URL (empty string) when VITE_API_BASE_URL is not set
// This works in production where nginx proxies /api/ to the backend
// Only use absolute URL (like http://localhost:8000) when explicitly set for dev
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export interface DataPreview {
  columns: string[];
  rows: Record<string, any>[];
  total_rows: number;
  preview_rows: number;
  has_more: boolean;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sql_query?: string;
  data_preview?: DataPreview;
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
    correlation?: number;
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
  data_preview?: DataPreview;
  execution_time_ms: number;
  visualization?: VisualizationData;
  database?: {
    id: number;
    name: string;
    type: string;
  };
  error?: string;
}

export interface DatabaseExploreResponse {
  database: {
    id: number;
    name: string;
    type: string;
  };
  tables: string[];
  table_count: number;
  table_info?: string;
  tables_queried?: string[];
  total_execution_time_ms: number;
  error?: string;
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
  tables?: string[];
  count?: number;
  tables_queried?: string[];
  sql?: string;
  execution_time_ms?: number;
  tool_execution_id?: number;
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

// Construct baseURL: if empty, use relative path /api/mcp (works with nginx proxy)
// If set, use absolute URL (e.g., http://localhost:8000/api/mcp for dev)
const apiBaseURL = API_BASE_URL ? `${API_BASE_URL}/api/mcp` : '/api/mcp';

const api = axios.create({
  baseURL: apiBaseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 120 seconds (2 minutes) for AI queries - increased for large datasets
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

  /**
   * Transcribe audio to text using Gemini
   */
  transcribeAudio: async (audioBlob: Blob): Promise<{ success: boolean; transcript: string; error?: string }> => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      const response = await api.post('/transcribe/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 seconds for transcription
      });
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.error || 'Failed to transcribe audio');
      }
      throw error;
    }
  },

  /**
   * Explore database schema - get tables and structure
   */
  exploreDatabase: async (databaseId: number): Promise<DatabaseExploreResponse> => {
    try {
      const response = await api.post('/quick/explore/', {
        database_id: databaseId,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.error || 'Failed to explore database');
      }
      throw error;
    }
  },

  /**
   * Run deep query chain - execute multiple operations in sequence
   */
  runDeepQuery: async (request: DeepQueryRequest): Promise<DeepQueryResponse> => {
    try {
      const response = await api.post('/deep-query/', request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.error || 'Failed to execute deep query');
      }
      throw error;
    }
  },

  /**
   * Export query results to CSV or Excel
   * Returns both the blob and the filename extracted from headers
   */
  exportData: async (
    sqlQuery: string,
    format: 'csv' | 'excel',
    databaseId: number = 1,
    filename?: string
  ): Promise<{ blob: Blob; filename: string }> => {
    try {
      const response = await api.post(
        '/export/',
        {
          sql_query: sqlQuery,
          format: format,
          database_id: databaseId,
          filename: filename,
        },
        {
          responseType: 'blob', // Important for file downloads
        }
      );

      // Extract filename from Content-Disposition header
      let extractedFilename = filename || `query_results_${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}`;
      const contentDisposition = response.headers['content-disposition'] || response.headers['Content-Disposition'];

      if (contentDisposition) {
        // Try to extract from filename* (RFC 5987) first, then fallback to filename
        const filenameStarMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
        if (filenameStarMatch && filenameStarMatch[1]) {
          try {
            extractedFilename = decodeURIComponent(filenameStarMatch[1]);
          } catch {
            // If decoding fails, try regular filename
            const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
            if (filenameMatch && filenameMatch[1]) {
              extractedFilename = filenameMatch[1];
            }
          }
        } else {
          // Try regular filename
          const filenameMatch = contentDisposition.match(/filename="?([^";]+)"?/i);
          if (filenameMatch && filenameMatch[1]) {
            extractedFilename = filenameMatch[1];
          }
        }
      }

      // If no extension, add it based on format
      if (!extractedFilename.endsWith('.csv') && !extractedFilename.endsWith('.xlsx')) {
        extractedFilename += format === 'excel' ? '.xlsx' : '.csv';
      }

      return {
        blob: response.data,
        filename: extractedFilename
      };
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        // Try to parse error message from blob
        try {
          const errorText = await error.response.data.text();
          const errorJson = JSON.parse(errorText);
          throw new Error(errorJson.error || 'Failed to export data');
        } catch {
          throw new Error('Failed to export data');
        }
      }
      throw error;
    }
  },
};

