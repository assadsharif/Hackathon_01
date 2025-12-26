import { useState, useEffect } from 'react';
import type { Message } from '../components/ChatbotPanel/ChatbotPanel';

const SESSION_ID_KEY = 'chatbot_session_id';
const CONVERSATION_HISTORY_KEY = 'chatbot_conversation_history';
const MAX_MESSAGES = 20;
const MAX_AGE_DAYS = 7;

interface ConversationHistory {
  session_id: string;
  messages: Message[];
  created_at: string;
  last_activity: string;
}

/**
 * Custom hook for managing chatbot session and conversation history in LocalStorage.
 *
 * Features:
 * - Generates and persists session UUID
 * - Stores conversation history (last 20 messages)
 * - Auto-prunes messages older than 7 days
 * - Clears history on demand
 */
export function useChatSession() {
  const [sessionId, setSessionId] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Generate UUID v4
  const generateUUID = (): string => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  };

  // Check if message is older than max age
  const isMessageExpired = (timestamp: string): boolean => {
    const messageDate = new Date(timestamp);
    const now = new Date();
    const diffDays = (now.getTime() - messageDate.getTime()) / (1000 * 60 * 60 * 24);
    return diffDays > MAX_AGE_DAYS;
  };

  // Prune old messages
  const pruneMessages = (messages: Message[]): Message[] => {
    // Remove messages older than 7 days
    const validMessages = messages.filter(msg => !isMessageExpired(msg.timestamp));

    // Keep only last 20 messages
    if (validMessages.length > MAX_MESSAGES) {
      return validMessages.slice(-MAX_MESSAGES);
    }

    return validMessages;
  };

  // Load or create session
  useEffect(() => {
    try {
      // Get or create session ID
      let storedSessionId = localStorage.getItem(SESSION_ID_KEY);
      if (!storedSessionId) {
        storedSessionId = generateUUID();
        localStorage.setItem(SESSION_ID_KEY, storedSessionId);
      }
      setSessionId(storedSessionId);

      // Load conversation history
      const historyStr = localStorage.getItem(CONVERSATION_HISTORY_KEY);
      if (historyStr) {
        try {
          const history: ConversationHistory = JSON.parse(historyStr);

          // Verify session matches
          if (history.session_id === storedSessionId) {
            // Prune old messages
            const prunedMessages = pruneMessages(history.messages);
            setMessages(prunedMessages);

            // Update storage if messages were pruned
            if (prunedMessages.length !== history.messages.length) {
              const updatedHistory: ConversationHistory = {
                ...history,
                messages: prunedMessages,
                last_activity: new Date().toISOString(),
              };
              localStorage.setItem(CONVERSATION_HISTORY_KEY, JSON.stringify(updatedHistory));
            }
          } else {
            // Session mismatch - start fresh
            setMessages([]);
          }
        } catch (error) {
          console.error('Error parsing conversation history:', error);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error('Error initializing session:', error);
      // Fallback to in-memory session
      setSessionId(generateUUID());
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Save conversation history to LocalStorage
  const saveHistory = (updatedMessages: Message[]) => {
    try {
      const history: ConversationHistory = {
        session_id: sessionId,
        messages: updatedMessages,
        created_at: localStorage.getItem(CONVERSATION_HISTORY_KEY)
          ? JSON.parse(localStorage.getItem(CONVERSATION_HISTORY_KEY)!).created_at
          : new Date().toISOString(),
        last_activity: new Date().toISOString(),
      };
      localStorage.setItem(CONVERSATION_HISTORY_KEY, JSON.stringify(history));
    } catch (error) {
      console.error('Error saving conversation history:', error);
      // If storage is full, try to clear old data
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        console.warn('LocalStorage quota exceeded, clearing old messages');
        const trimmedMessages = updatedMessages.slice(-10); // Keep only last 10
        try {
          const history: ConversationHistory = {
            session_id: sessionId,
            messages: trimmedMessages,
            created_at: new Date().toISOString(),
            last_activity: new Date().toISOString(),
          };
          localStorage.setItem(CONVERSATION_HISTORY_KEY, JSON.stringify(history));
        } catch (retryError) {
          console.error('Failed to save even after trimming:', retryError);
        }
      }
    }
  };

  // Add a new message to history
  const addMessage = (message: Message) => {
    setMessages(prevMessages => {
      const updatedMessages = [...prevMessages, message];
      const prunedMessages = pruneMessages(updatedMessages);
      saveHistory(prunedMessages);
      return prunedMessages;
    });
  };

  // Clear conversation history
  const clearHistory = () => {
    setMessages([]);
    try {
      localStorage.removeItem(CONVERSATION_HISTORY_KEY);
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  };

  // Reset session (generate new ID and clear history)
  const resetSession = () => {
    const newSessionId = generateUUID();
    setSessionId(newSessionId);
    setMessages([]);
    try {
      localStorage.setItem(SESSION_ID_KEY, newSessionId);
      localStorage.removeItem(CONVERSATION_HISTORY_KEY);
    } catch (error) {
      console.error('Error resetting session:', error);
    }
  };

  return {
    sessionId,
    messages,
    isLoading,
    addMessage,
    clearHistory,
    resetSession,
  };
}
