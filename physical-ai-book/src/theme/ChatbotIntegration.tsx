import React, { useState, useCallback, useEffect, useRef } from 'react';
import ChatbotPanel from '../components/ChatbotPanel/ChatbotPanel';
import { useChatSession } from '../hooks/useChatSession';
import { useTextSelection } from '../hooks/useTextSelection';
import { useChatbotAPI } from '../hooks/useChatbotAPI';
import type { Message } from '../components/ChatbotPanel/ChatbotPanel';

/**
 * ChatbotIntegration - Wrapper component that integrates ChatbotPanel with Docusaurus theme.
 *
 * Responsibilities:
 * - Manages chatbot session state (session ID, conversation history)
 * - Detects text selection on page for selected-text mode
 * - Handles API communication with RAG backend
 * - Coordinates mode switching (full-book vs selected-text)
 * - Manages loading and error states
 * - Detects page navigation and resets context (T048)
 *
 * This component is mounted globally via Root.tsx and persists across page navigations.
 */
export default function ChatbotIntegration(): JSX.Element {
  // Session management (LocalStorage persistence)
  const { sessionId, messages, addMessage, isLoading: sessionLoading } = useChatSession();

  // Text selection detection
  const { selectedText, isValid: isSelectionValid, clearSelection } = useTextSelection();

  // API client
  const { submitQuery, isLoading: apiLoading, error: apiError, clearError } = useChatbotAPI();

  // Mode state (full-book or selected-text)
  const [currentMode, setCurrentMode] = useState<'full-book' | 'selected-text'>('full-book');

  // Track current page URL for navigation detection (T048)
  const currentUrlRef = useRef<string>(typeof window !== 'undefined' ? window.location.pathname : '');

  // Combined loading state
  const isLoading = sessionLoading || apiLoading;

  /**
   * T048: Page navigation detection
   * When user navigates to a different page:
   * 1. Clear any selected text context
   * 2. Reset mode to full-book
   * This ensures chatbot context doesn't carry over between pages
   */
  useEffect(() => {
    const handleUrlChange = () => {
      const newUrl = window.location.pathname;

      // Check if URL has changed
      if (currentUrlRef.current !== newUrl) {
        console.log(`Page navigation detected: ${currentUrlRef.current} → ${newUrl}`);

        // Clear selected text context
        clearSelection();

        // Reset mode to full-book
        if (currentMode === 'selected-text') {
          setCurrentMode('full-book');
        }

        // Update tracked URL
        currentUrlRef.current = newUrl;
      }
    };

    // Check for URL changes on interval (Docusaurus uses client-side routing)
    const intervalId = setInterval(handleUrlChange, 500);

    // Also listen for popstate events (browser back/forward)
    window.addEventListener('popstate', handleUrlChange);

    // Cleanup
    return () => {
      clearInterval(intervalId);
      window.removeEventListener('popstate', handleUrlChange);
    };
  }, [currentMode, clearSelection]);

  /**
   * Handle mode changes from ModeToggle component.
   * If switching to selected-text mode but no valid selection, stay in full-book mode.
   */
  const handleModeChange = useCallback(
    (newMode: 'full-book' | 'selected-text') => {
      // Prevent switching to selected-text mode without valid selection
      if (newMode === 'selected-text' && (!selectedText || !isSelectionValid)) {
        console.warn('Cannot switch to selected-text mode: no valid selection');
        return;
      }

      setCurrentMode(newMode);
      clearError(); // Clear any previous errors when switching modes
    },
    [selectedText, isSelectionValid, clearError]
  );

  /**
   * Handle query submission from ChatInput component.
   *
   * Flow:
   * 1. Validate inputs (query, mode, selection if needed)
   * 2. Submit query to API via useChatbotAPI hook
   * 3. On success: add user query + bot response to conversation history
   * 4. On error: add error message to conversation history
   */
  const handleSendMessage = useCallback(
    async (query: string, mode: 'full-book' | 'selected-text', selectedTextContent?: string) => {
      if (!query.trim()) {
        console.warn('Empty query submitted');
        return;
      }

      if (!sessionId) {
        console.error('Session ID not initialized');
        return;
      }

      // Validate mode requirements
      if (mode === 'selected-text' && !selectedTextContent) {
        console.error('Selected-text mode requires selectedText parameter');
        return;
      }

      try {
        clearError();

        // Submit query to API
        const response = await submitQuery(
          sessionId,
          query,
          mode,
          selectedTextContent,
          window.location.pathname
        );

        // Create message object for conversation history
        const newMessage: Message = {
          id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          query: query,
          answer: response.answer,
          citations: response.citations,
          mode: response.mode,
          timestamp: new Date().toISOString(),
          isError: false,
        };

        // Add to conversation history (persisted to LocalStorage)
        addMessage(newMessage);

      } catch (error) {
        console.error('Failed to submit query:', error);

        // Add error message to conversation history
        const errorMessage: Message = {
          id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          query: query,
          answer: error instanceof Error ? error.message : 'An unexpected error occurred. Please try again.',
          citations: [],
          mode: mode,
          timestamp: new Date().toISOString(),
          isError: true,
        };

        addMessage(errorMessage);
      }
    },
    [sessionId, submitQuery, addMessage, clearError]
  );

  // Don't render until session is loaded
  if (sessionLoading) {
    return null;
  }

  return (
    <ChatbotPanel
      sessionId={sessionId}
      messages={messages}
      onSendMessage={handleSendMessage}
      isLoading={apiLoading}
      currentMode={currentMode}
      onModeChange={handleModeChange}
      selectedText={selectedText}
    />
  );
}
