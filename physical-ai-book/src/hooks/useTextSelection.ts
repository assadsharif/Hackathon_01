import { useState, useEffect, useCallback } from 'react';

const MIN_SELECTION_LENGTH = 50; // Minimum characters for valid selection

interface TextSelectionState {
  selectedText: string | null;
  isValid: boolean;
  selectionStart: number;
  selectionEnd: number;
}

/**
 * Custom hook for detecting and managing browser text selection.
 *
 * Features:
 * - Detects when user selects text on the page
 * - Validates selection length (minimum 50 characters)
 * - Extracts selection start/end offsets
 * - Auto-clears selection on page navigation
 * - Debounces selection events
 */
export function useTextSelection() {
  const [selection, setSelection] = useState<TextSelectionState>({
    selectedText: null,
    isValid: false,
    selectionStart: 0,
    selectionEnd: 0,
  });

  // Handle selection change
  const handleSelectionChange = useCallback(() => {
    const windowSelection = window.getSelection();

    if (!windowSelection || windowSelection.rangeCount === 0) {
      // No selection
      setSelection({
        selectedText: null,
        isValid: false,
        selectionStart: 0,
        selectionEnd: 0,
      });
      return;
    }

    const selectedText = windowSelection.toString().trim();

    if (!selectedText || selectedText.length === 0) {
      // Empty selection
      setSelection({
        selectedText: null,
        isValid: false,
        selectionStart: 0,
        selectionEnd: 0,
      });
      return;
    }

    // Get selection range for offsets
    const range = windowSelection.getRangeAt(0);
    const preSelectionRange = range.cloneRange();
    preSelectionRange.selectNodeContents(document.body);
    preSelectionRange.setEnd(range.startContainer, range.startOffset);
    const selectionStart = preSelectionRange.toString().length;
    const selectionEnd = selectionStart + selectedText.length;

    // Validate selection length
    const isValid = selectedText.length >= MIN_SELECTION_LENGTH;

    setSelection({
      selectedText,
      isValid,
      selectionStart,
      selectionEnd,
    });
  }, []);

  // Debounced selection handler
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    const debouncedHandler = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        handleSelectionChange();
      }, 300); // 300ms debounce
    };

    // Listen for selection changes
    document.addEventListener('selectionchange', debouncedHandler);
    document.addEventListener('mouseup', debouncedHandler);
    document.addEventListener('keyup', debouncedHandler);

    return () => {
      clearTimeout(timeoutId);
      document.removeEventListener('selectionchange', debouncedHandler);
      document.removeEventListener('mouseup', debouncedHandler);
      document.removeEventListener('keyup', debouncedHandler);
    };
  }, [handleSelectionChange]);

  // Clear selection programmatically
  const clearSelection = useCallback(() => {
    window.getSelection()?.removeAllRanges();
    setSelection({
      selectedText: null,
      isValid: false,
      selectionStart: 0,
      selectionEnd: 0,
    });
  }, []);

  return {
    selectedText: selection.selectedText,
    isValid: selection.isValid,
    selectionStart: selection.selectionStart,
    selectionEnd: selection.selectionEnd,
    minLength: MIN_SELECTION_LENGTH,
    clearSelection,
  };
}
