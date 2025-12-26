import React from 'react';
import styles from './ModeToggle.module.css';

export interface ModeToggleProps {
  currentMode: 'full-book' | 'selected-text';
  onModeChange: (mode: 'full-book' | 'selected-text') => void;
  selectedText: string | null;
}

export default function ModeToggle({
  currentMode,
  onModeChange,
  selectedText,
}: ModeToggleProps): JSX.Element {
  return (
    <div className={styles.container}>
      <div className={styles.toggleGroup}>
        <button
          className={`${styles.toggleButton} ${
            currentMode === 'full-book' ? styles.active : ''
          }`}
          onClick={() => onModeChange('full-book')}
          title="Search the entire Physical AI book"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            className={styles.icon}
          >
            <path
              d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"
              fill="currentColor"
            />
          </svg>
          <span className={styles.label}>Full-book</span>
        </button>

        <button
          className={`${styles.toggleButton} ${
            currentMode === 'selected-text' ? styles.active : ''
          } ${!selectedText ? styles.disabled : ''}`}
          onClick={() => selectedText && onModeChange('selected-text')}
          disabled={!selectedText}
          title={
            selectedText
              ? 'Ask about your selected text'
              : 'Select text on the page to enable this mode'
          }
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            className={styles.icon}
          >
            <path
              d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"
              fill="currentColor"
            />
          </svg>
          <span className={styles.label}>Selected-text</span>
          {selectedText && (
            <span className={styles.badge}>{selectedText.length} chars</span>
          )}
        </button>
      </div>

      {/* Mode Description */}
      <div className={styles.description}>
        {currentMode === 'full-book' ? (
          <>
            <span className={styles.descriptionIcon}>🔍</span>
            <span className={styles.descriptionText}>
              Searching entire book for relevant content
            </span>
          </>
        ) : (
          <>
            <span className={styles.descriptionIcon}>📝</span>
            <span className={styles.descriptionText}>
              Answers constrained to selected text only
            </span>
          </>
        )}
      </div>
    </div>
  );
}
