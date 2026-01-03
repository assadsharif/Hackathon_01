import React, { useState, useEffect } from 'react';
import SignupModal from './SignupModal';
import styles from './AuthButton.module.css';

export default function AuthButton(): JSX.Element {
  const [isSignupOpen, setIsSignupOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('chatkit_session_token');
    if (token) {
      checkSession(token);
    }
  }, []);

  const checkSession = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/session-check', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setIsAuthenticated(true);
        setUserEmail(data.email || 'User');
      } else {
        // Token invalid, clear it
        localStorage.removeItem('chatkit_session_token');
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Session check failed:', error);
      setIsAuthenticated(false);
    }
  };

  const handleSignupSuccess = (token: string) => {
    localStorage.setItem('chatkit_session_token', token);
    setIsAuthenticated(true);
    setIsSignupOpen(false);
    // Refresh the page to update the widget
    window.location.reload();
  };

  const handleSignOut = () => {
    localStorage.removeItem('chatkit_session_token');
    setIsAuthenticated(false);
    setUserEmail(null);
    // Refresh the page
    window.location.reload();
  };

  if (isAuthenticated) {
    return (
      <div className={styles.authContainer}>
        <span className={styles.userInfo}>
          {userEmail}
        </span>
        <button onClick={handleSignOut} className={styles.signOutButton}>
          Sign Out
        </button>
      </div>
    );
  }

  return (
    <>
      <button
        onClick={() => setIsSignupOpen(true)}
        className={styles.signUpButton}
      >
        Sign Up / Sign In
      </button>

      <SignupModal
        isOpen={isSignupOpen}
        onClose={() => setIsSignupOpen(false)}
        onSignupSuccess={handleSignupSuccess}
      />
    </>
  );
}
