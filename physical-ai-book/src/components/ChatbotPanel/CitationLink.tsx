import React from 'react';
import Link from '@docusaurus/Link';
import styles from './CitationLink.module.css';

export interface CitationLinkProps {
  text: string;
  url: string;
}

export default function CitationLink({ text, url }: CitationLinkProps): JSX.Element {
  return (
    <Link
      to={url}
      className={styles.link}
      title={`Go to: ${text}`}
    >
      <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        className={styles.icon}
      >
        <path
          d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
          fill="currentColor"
        />
      </svg>
      <span className={styles.text}>{text}</span>
      <svg
        width="12"
        height="12"
        viewBox="0 0 24 24"
        fill="none"
        className={styles.arrow}
      >
        <path
          d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"
          fill="currentColor"
        />
      </svg>
    </Link>
  );
}
