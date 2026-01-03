import React, { useEffect, useRef } from 'react';
import styles from './MessageList.module.css';
import CitationLink from './CitationLink';
import type { Message } from './ChatbotPanel';

export interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export default function MessageList({
  messages,
  isLoading,
}: MessageListProps): JSX.Element {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className={styles.container}>
      {/* Empty State */}
      {messages.length === 0 && !isLoading && (
        <div className={styles.emptyState}>
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            className={styles.emptyIcon}
          >
            <path
              d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H6L4 18V4H20V16Z"
              fill="currentColor"
            />
            <path
              d="M7 9H17V11H7V9ZM7 12H14V14H7V12ZM7 6H17V8H7V6Z"
              fill="currentColor"
            />
          </svg>
          <h4 className={styles.emptyTitle}>Welcome!</h4>
          <p className={styles.emptyDescription}>
            I can answer questions about the Physical AI book. Ask about any topic or select text for focused answers.
          </p>
        </div>
      )}

      {/* Messages */}
      {messages.map((message) => (
        <div key={message.id} className={styles.messageGroup}>
          {/* User Query */}
          <div className={styles.userMessage}>
            <div className={styles.messageBubble}>
              <p className={styles.messageText}>{message.query}</p>
              <div className={styles.messageMetadata}>
                <span className={styles.modeLabel}>
                  {message.mode === 'full-book' ? '🔍 Full-book' : '📝 Selected-text'}
                </span>
                <span className={styles.timestamp}>
                  {new Date(message.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
            </div>
          </div>

          {/* Bot Response */}
          <div className={styles.botMessage}>
            <div className={`${styles.messageBubble} ${message.isError ? styles.error : ''}`}>
              <p className={styles.messageText}>{message.answer}</p>

              {/* Citations */}
              {message.citations && message.citations.length > 0 && (
                <div className={styles.citations}>
                  <div className={styles.citationsLabel}>Sources:</div>
                  <div className={styles.citationsList}>
                    {message.citations.map((citation, index) => (
                      <CitationLink
                        key={index}
                        text={citation.text}
                        url={citation.url}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}

      {/* Loading Indicator */}
      {isLoading && (
        <div className={styles.botMessage}>
          <div className={styles.messageBubble}>
            <div className={styles.loadingDots}>
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}

      {/* Scroll Anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
}
