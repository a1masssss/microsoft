/**
 * HTTP client with Telegram authentication
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/telegram';

export const createApiClient = (initData: string) => {
  return axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `tma ${initData}`,
    },
    timeout: 10000,
  });
};
