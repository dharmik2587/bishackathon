// API configuration - uses environment variable or defaults to localhost
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  query: `${API_URL}/api/query`,
  results: `${API_URL}/api/results`,
  evaluate: `${API_URL}/api/evaluate`,
};
