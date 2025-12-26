import React, { useState, useRef, useEffect } from 'react';
import styles from './ChatInput.module.css';

export interface ChatInputProps {
  onSendMessage: (query: string) => Promise<void>;
  isLoading: boolean;
  currentMode: 'full-book' | 'selected-text';
  selectedText: string | null;
}

export default function ChatInput({
  onSendMessage,
  isLoading,
  currentMode,
  selectedText,
}: ChatInputProps): JSX.Element {
  const [query, setQuery] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [query]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedQuery = query.trim();
    if (!trimmedQuery || isLoading) {
      return;
    }

    // Validate selected-text mode
    if (currentMode === 'selected-text' && !selectedText) {
      alert('Please select some text on the page to use selected-text mode, or switch to full-book mode.');
      return;
    }

    try {
      await onSendMessage(trimmedQuery);
      setQuery(''); // Clear input after successful send
    } catch (error) {
      console.error('Error sending message:', error);
      // Error handling is done in parent component
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (but allow Shift+Enter for new line)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const placeholder =
    currentMode === 'full-book'
      ? 'Ask a question about the Physical AI book...'
      : selectedText
      ? 'Ask about the selected text...'
      : 'Select text on the page first...';

  const isDisabled = isLoading || (currentMode === 'selected-text' && !selectedText);

  return (
    <form className={styles.container} onSubmit={handleSubmit}>
      {/* Selected Text Indicator */}
      {currentMode === 'selected-text' && selectedText && (
        <div className={styles.selectedTextIndicator}>
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            className={styles.icon}
          >
            <path
              d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"
              fill="currentColor"
            />
          </svg>
          <span className={styles.indicatorText}>
            {selectedText.length > 60
              ? `${selectedText.substring(0, 60)}...`
              : selectedText}
          </span>
        </div>
      )}

      {/* Input Container */}
      <div className={styles.inputContainer}>
        <textarea
          ref={textareaRef}
          className={styles.textarea}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isDisabled}
          rows={1}
          maxLength={5000}
          aria-label="Chat input"
        />
        <button
          type="submit"
          className={styles.sendButton}
          disabled={isDisabled || !query.trim()}
          aria-label="Send message"
          title="Send (Enter)"
        >
          {isLoading ? (
            <svg
              className={styles.spinner}
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="3"
                strokeDasharray="31.4 31.4"
                strokeLinecap="round"
              />
            </svg>
          ) : (
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
            >
              <path
                d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"
                fill="currentColor"
              />
            </svg>
          )}
        </button>
      </div>

      {/* Character Count */}
      {query.length > 4500 && (
        <div className={styles.charCount}>
          {query.length} / 5000 characters
        </div>
      )}
    </form>
  );
}
