// Types for AI service errors
export interface AIServiceError extends Error {
  code: 'RATE_LIMIT' | 'INVALID_INPUT' | 'API_ERROR' | 'UNKNOWN';
  details?: unknown;
}

