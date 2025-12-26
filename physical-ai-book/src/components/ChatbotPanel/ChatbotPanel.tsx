import React, { useState } from 'react';
import styles from './ChatbotPanel.module.css';
import ChatInput from './ChatInput';
import MessageList from './MessageList';
import ModeToggle from './ModeToggle';
import HelpDialog from './HelpDialog';

export interface Message {
  id: string;
  query: string;
  answer: string;
  citations: Array<{
    text: string;
    url: string;
  }>;
  mode: 'full-book' | 'selected-text';
  timestamp: string;
  isError?: boolean;
}

export interface ChatbotPanelProps {
  sessionId: string;
  messages: Message[];
  onSendMessage: (query: string, mode: 'full-book' | 'selected-text', selectedText?: string) => Promise<void>;
  isLoading: boolean;
  currentMode: 'full-book' | 'selected-text';
  onModeChange: (mode: 'full-book' | 'selected-text') => void;
  selectedText: string | null;
}

export default function ChatbotPanel({
  sessionId,
  messages,
  onSendMessage,
  isLoading,
  currentMode,
  onModeChange,
  selectedText,
}: ChatbotPanelProps): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  const togglePanel = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setIsMinimized(false);
    }
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const toggleHelp = () => {
    setIsHelpOpen(!isHelpOpen);
  };

  const handleSendMessage = async (query: string) => {
    await onSendMessage(query, currentMode, selectedText || undefined);
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <button
          className={styles.fab}
          onClick={togglePanel}
          aria-label="Open chatbot"
          title="Ask a question about the Physical AI book"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
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
        </button>
      )}

      {/* Chatbot Panel */}
      {isOpen && (
        <div className={`${styles.panel} ${isMinimized ? styles.minimized : ''}`}>
          {/* Header */}
          <div className={styles.header}>
            <div className={styles.headerContent}>
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                className={styles.headerIcon}
              >
                <path
                  d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z"
                  fill="currentColor"
                />
              </svg>
              <h3 className={styles.title}>Physical AI Assistant</h3>
            </div>
            <div className={styles.headerActions}>
              <button
                className={styles.iconButton}
                onClick={toggleHelp}
                aria-label="Help"
                title="Help"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z" />
                </svg>
              </button>
              <button
                className={styles.iconButton}
                onClick={toggleMinimize}
                aria-label={isMinimized ? 'Maximize' : 'Minimize'}
                title={isMinimized ? 'Maximize' : 'Minimize'}
              >
                {isMinimized ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 14h12v2H6z" />
                  </svg>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 19h12v2H6z" />
                  </svg>
                )}
              </button>
              <button
                className={styles.iconButton}
                onClick={togglePanel}
                aria-label="Close chatbot"
                title="Close"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
                </svg>
              </button>
            </div>
          </div>

          {/* Mode Toggle */}
          {!isMinimized && (
            <ModeToggle
              currentMode={currentMode}
              onModeChange={onModeChange}
              selectedText={selectedText}
            />
          )}

          {/* Message List */}
          {!isMinimized && (
            <MessageList
              messages={messages}
              isLoading={isLoading}
            />
          )}

          {/* Chat Input */}
          {!isMinimized && (
            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              currentMode={currentMode}
              selectedText={selectedText}
            />
          )}

          {/* Session Info (for debugging, can be removed in production) */}
          {!isMinimized && process.env.NODE_ENV === 'development' && (
            <div className={styles.sessionInfo}>
              Session: {sessionId.substring(0, 8)}...
            </div>
          )}
        </div>
      )}

      {/* Help Dialog */}
      <HelpDialog isOpen={isHelpOpen} onClose={toggleHelp} />
    </>
  );
}
