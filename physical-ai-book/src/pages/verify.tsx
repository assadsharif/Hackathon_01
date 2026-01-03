import React, { useEffect, useState } from 'react';
import Layout from '@theme/Layout';
import styles from './verify.module.css';

export default function VerifyEmail(): JSX.Element {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [userEmail, setUserEmail] = useState('');

  useEffect(() => {
    const verifyEmail = async () => {
      // Get token from URL query params
      const params = new URLSearchParams(window.location.search);
      const token = params.get('token');

      if (!token) {
        setStatus('error');
        setMessage('Invalid verification link. No token provided.');
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/verify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error?.message || 'Verification failed');
        }

        // Success! Save the session token
        localStorage.setItem('chatkit_session_token', data.session_token);
        setUserEmail(data.user_profile.email);
        setStatus('success');
        setMessage('Your email has been verified successfully!');

        // Redirect to home page after 3 seconds
        setTimeout(() => {
          window.location.href = '/Hackathon_01/';
        }, 3000);
      } catch (error) {
        setStatus('error');
        setMessage(error instanceof Error ? error.message : 'Verification failed. Please try again.');
      }
    };

    verifyEmail();
  }, []);

  return (
    <Layout
      title="Email Verification"
      description="Verify your email address"
    >
      <div className={styles.container}>
        <div className={styles.card}>
          {status === 'loading' && (
            <>
              <div className={styles.spinner}></div>
              <h1>Verifying your email...</h1>
              <p>Please wait while we confirm your email address.</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className={styles.successIcon}>✓</div>
              <h1>Email Verified!</h1>
              <p className={styles.email}>{userEmail}</p>
              <p className={styles.message}>{message}</p>
              <p className={styles.redirect}>
                Redirecting you to the home page...
              </p>
              <a href="/Hackathon_01/" className={styles.button}>
                Go to Home Page Now
              </a>
            </>
          )}

          {status === 'error' && (
            <>
              <div className={styles.errorIcon}>✗</div>
              <h1>Verification Failed</h1>
              <p className={styles.errorMessage}>{message}</p>
              <div className={styles.errorHelp}>
                <h3>What can I do?</h3>
                <ul>
                  <li>Check if the link is complete (copy the full URL)</li>
                  <li>The verification link expires after 10 minutes</li>
                  <li>Request a new verification email from the signup page</li>
                </ul>
              </div>
              <a href="/Hackathon_01/" className={styles.button}>
                Return to Home Page
              </a>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}
