import React from 'react';
import styles from './HelpDialog.module.css';

export interface HelpDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * HelpDialog - Modal component explaining chatbot capabilities and modes.
 *
 * Features:
 * - Explains full-book vs selected-text modes with examples
 * - Provides usage tips and best practices
 * - Modal overlay with close button and ESC key support
 */
export default function HelpDialog({ isOpen, onClose }: HelpDialogProps): JSX.Element | null {
  // Don't render if not open
  if (!isOpen) return null;

  // Handle ESC key to close
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scrolling when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'auto';
    };
  }, [isOpen, onClose]);

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.dialog} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <h2 className={styles.title}>How to Use the Chatbot</h2>
          <button
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close help dialog"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className={styles.content}>
          {/* Introduction */}
          <section className={styles.section}>
            <p className={styles.intro}>
              This chatbot helps you explore the Physical AI & Humanoid Robotics book using
              Retrieval-Augmented Generation (RAG). You can ask questions in two different modes:
            </p>
          </section>

          {/* Full-book Mode */}
          <section className={styles.section}>
            <div className={styles.modeHeader}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"
                  fill="currentColor"
                />
              </svg>
              <h3 className={styles.modeTitle}>Full-book Mode</h3>
            </div>
            <p className={styles.modeDescription}>
              Searches the entire book to find relevant content and answer your question.
            </p>
            <div className={styles.exampleBox}>
              <div className={styles.exampleLabel}>Example questions:</div>
              <ul className={styles.exampleList}>
                <li>"What is embodied intelligence?"</li>
                <li>"How do humanoid robots perceive their environment?"</li>
                <li>"Explain the difference between symbolic and subsymbolic AI"</li>
              </ul>
            </div>
            <div className={styles.tip}>
              <strong>Best for:</strong> General questions, concept explanations, comparisons across
              different topics
            </div>
          </section>

          {/* Selected-text Mode */}
          <section className={styles.section}>
            <div className={styles.modeHeader}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path
                  d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"
                  fill="currentColor"
                />
              </svg>
              <h3 className={styles.modeTitle}>Selected-text Mode</h3>
            </div>
            <p className={styles.modeDescription}>
              Answers questions based <strong>only</strong> on the text you've selected on the page.
              Requires at least 50 characters of selected text.
            </p>
            <div className={styles.exampleBox}>
              <div className={styles.exampleLabel}>How to use:</div>
              <ol className={styles.stepList}>
                <li>Highlight any text passage on the page (minimum 50 characters)</li>
                <li>Switch to "Selected-text" mode in the chatbot</li>
                <li>Ask questions about the highlighted passage</li>
              </ol>
            </div>
            <div className={styles.exampleBox}>
              <div className={styles.exampleLabel}>Example questions:</div>
              <ul className={styles.exampleList}>
                <li>"Summarize this section"</li>
                <li>"What does this paragraph mean?"</li>
                <li>"Can you explain this concept in simpler terms?"</li>
              </ul>
            </div>
            <div className={styles.tip}>
              <strong>Best for:</strong> Understanding specific passages, clarifying terminology,
              getting focused explanations
            </div>
          </section>

          {/* Tips */}
          <section className={styles.section}>
            <h3 className={styles.tipsTitle}>Tips for Best Results</h3>
            <ul className={styles.tipsList}>
              <li>
                <strong>Be specific:</strong> Instead of "Tell me about robots," try "What are the
                main challenges in humanoid locomotion?"
              </li>
              <li>
                <strong>Use selected-text for deep dives:</strong> Highlight complex passages and ask
                for clarification or summaries
              </li>
              <li>
                <strong>Session persistence:</strong> Your conversation history is saved locally for 7
                days (up to 20 messages)
              </li>
              <li>
                <strong>Boundaries:</strong> The chatbot can only answer questions about content in
                this book - it won't generate code or discuss unrelated topics
              </li>
            </ul>
          </section>
        </div>

        {/* Footer */}
        <div className={styles.footer}>
          <button className={styles.gotItButton} onClick={onClose}>
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
}
