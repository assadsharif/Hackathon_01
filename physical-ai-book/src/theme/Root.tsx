import React from 'react';
import ChatbotIntegration from './ChatbotIntegration';

/**
 * Root - Docusaurus theme component that wraps the entire application.
 *
 * This component is mounted globally and persists across all page navigations.
 * We use it to mount the ChatbotIntegration component, making the chatbot
 * available on every page of the documentation site.
 *
 * Docusaurus automatically swizzles this component if it exists in src/theme/.
 *
 * @see https://docusaurus.io/docs/swizzling#wrapper-your-site-with-root
 */
export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  return (
    <>
      {children}
      <ChatbotIntegration />
    </>
  );
}
