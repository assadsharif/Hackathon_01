import { useState, useCallback } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

interface QueryRequest {
  session_id: string;
  query: string;
  mode: 'full-book' | 'selected-text';
  selected_text?: string;
  current_page_url?: string;
}

interface Citation {
  text: string;
  url: string;
}

interface QueryResponse {
  answer: string;
  citations: Citation[];
  mode: 'full-book' | 'selected-text';
  latency_ms: number;
  error_code?: string;
  error_message?: string;
}

interface APIError {
  error_code: string;
  error_message: string;
  retry_after_seconds?: number;
}

/**
 * Custom hook for interacting with the RAG chatbot API.
 *
 * Features:
 * - POST /v1/query with type-safe request/response
 * - Automatic retry on transient failures (503, timeout)
 * - Error handling with user-friendly messages
 * - Rate limit detection (429)
 * - Loading state management
 */
export function useChatbotAPI() {
  const { siteConfig } = useDocusaurusContext();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<APIError | null>(null);

  // Get API URL from config
  const getApiUrl = (): string => {
    const customFields = siteConfig.customFields as { chatbotApiUrl?: string };
    return customFields.chatbotApiUrl || 'http://localhost:8000/v1';
  };

  // Delay helper for retry logic
  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  // Submit query to chatbot API
  const submitQuery = useCallback(
    async (
      sessionId: string,
      query: string,
      mode: 'full-book' | 'selected-text',
      selectedText?: string,
      currentPageUrl?: string,
      maxRetries: number = 2
    ): Promise<QueryResponse> => {
      setIsLoading(true);
      setError(null);

      const apiUrl = getApiUrl();
      const requestBody: QueryRequest = {
        session_id: sessionId,
        query,
        mode,
        selected_text: selectedText,
        current_page_url: currentPageUrl || window.location.pathname,
      };

      let lastError: APIError | null = null;

      for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
          const response = await fetch(`${apiUrl}/query`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
          });

          // Handle rate limiting
          if (response.status === 429) {
            const errorData: APIError = await response.json();
            lastError = errorData;
            setError(errorData);
            setIsLoading(false);
            throw new Error(errorData.error_message);
          }

          // Handle server errors with retry
          if (response.status === 503 && attempt < maxRetries) {
            console.warn(`Server unavailable, retrying... (${attempt + 1}/${maxRetries})`);
            await delay(1000 * (attempt + 1)); // Exponential backoff
            continue;
          }

          // Handle other errors
          if (!response.ok) {
            const errorData: APIError = await response.json();
            lastError = errorData;
            setError(errorData);
            setIsLoading(false);
            throw new Error(errorData.error_message || `HTTP ${response.status}`);
          }

          // Success
          const data: QueryResponse = await response.json();
          setIsLoading(false);
          return data;

        } catch (err) {
          // Network errors or timeout
          if (err instanceof TypeError && err.message.includes('fetch')) {
            lastError = {
              error_code: 'NETWORK_ERROR',
              error_message: 'Could not connect to chatbot service. Please check your connection.',
            };

            if (attempt < maxRetries) {
              console.warn(`Network error, retrying... (${attempt + 1}/${maxRetries})`);
              await delay(1000 * (attempt + 1));
              continue;
            }
          } else {
            // Re-throw non-network errors
            setIsLoading(false);
            throw err;
          }
        }
      }

      // All retries exhausted
      setError(lastError || {
        error_code: 'UNKNOWN_ERROR',
        error_message: 'An unexpected error occurred. Please try again.',
      });
      setIsLoading(false);
      throw new Error(lastError?.error_message || 'Request failed after retries');
    },
    []
  );

  // Check service health
  const checkHealth = useCallback(async (): Promise<boolean> => {
    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/health`, {
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        return data.status === 'healthy' || data.status === 'degraded';
      }

      return false;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }, []);

  // Clear error state
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    submitQuery,
    checkHealth,
    isLoading,
    error,
    clearError,
  };
}
