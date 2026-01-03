import React, { useEffect } from 'react';

/**
 * Root - Docusaurus theme component that wraps the entire application.
 *
 * This component is mounted globally and persists across all page navigations.
 * We use it to mount the ChatKit widget (Web Component), making the chatbot
 * available on every page of the documentation site.
 *
 * Docusaurus automatically swizzles this component if it exists in src/theme/.
 *
 * @see https://docusaurus.io/docs/swizzling#wrapper-your-site-with-root
 */
export default function Root({ children }: { children: React.ReactNode }): JSX.Element {
  useEffect(() => {
    // Add ChatKit widget element to the page
    if (!document.querySelector('chatkit-widget')) {
      const widget = document.createElement('chatkit-widget');
      document.body.appendChild(widget);
    }
  }, []);

  return <>{children}</>;
}
