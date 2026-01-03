import React, { useState } from 'react';
import styles from './SignupModal.module.css';

interface SignupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSignupSuccess: (token: string) => void;
}

export default function SignupModal({ isOpen, onClose, onSignupSuccess }: SignupModalProps): JSX.Element | null {
  const [email, setEmail] = useState('');
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'signup' | 'verification'>('signup');
  const [verificationSent, setVerificationSent] = useState(false);

  if (!isOpen) return null;

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          consent_data_storage: consent,
          migrate_session: false, // TODO: Implement session migration
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error?.message || 'Signup failed');
      }

      setVerificationSent(true);
      setStep('verification');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendVerification = async () => {
    setError(null);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/resend-verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error('Failed to resend verification email');
      }

      alert('Verification email resent! Please check your inbox.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resend email');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setEmail('');
    setConsent(false);
    setError(null);
    setStep('signup');
    setVerificationSent(false);
    onClose();
  };

  return (
    <div className={styles.modalOverlay} onClick={handleClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={handleClose} aria-label="Close">
          ×
        </button>

        {step === 'signup' ? (
          <div className={styles.signupForm}>
            <h2>Sign Up for Free</h2>
            <p className={styles.subtitle}>
              Save your conversation history and sync across devices
            </p>

            <form onSubmit={handleSignup}>
              <div className={styles.formGroup}>
                <label htmlFor="email">Email Address</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="you@example.com"
                  disabled={loading}
                  className={styles.input}
                />
              </div>

              <div className={styles.consentGroup}>
                <label className={styles.checkboxLabel}>
                  <input
                    type="checkbox"
                    checked={consent}
                    onChange={(e) => setConsent(e.target.checked)}
                    required
                    disabled={loading}
                  />
                  <span>
                    I consent to data storage and agree to the{' '}
                    <a href="/privacy" target="_blank" rel="noopener noreferrer">
                      Privacy Policy
                    </a>
                  </span>
                </label>
              </div>

              {error && (
                <div className={styles.error} role="alert">
                  {error}
                </div>
              )}

              <button
                type="submit"
                className={styles.submitButton}
                disabled={loading || !consent}
              >
                {loading ? 'Sending...' : 'Sign Up'}
              </button>
            </form>

            <div className={styles.footer}>
              <p className={styles.tierInfo}>
                <strong>Tier 1: Lightweight</strong> - Email verification, conversation sync
              </p>
              <p className={styles.privacyNote}>
                📧 We'll send a verification email. Your data is encrypted and never sold.
              </p>
            </div>
          </div>
        ) : (
          <div className={styles.verificationStep}>
            <div className={styles.successIcon}>✓</div>
            <h2>Check Your Email!</h2>
            <p className={styles.verificationMessage}>
              We've sent a verification email to:
            </p>
            <p className={styles.emailDisplay}>{email}</p>

            <div className={styles.verificationInstructions}>
              <h3>Next Steps:</h3>
              <ol>
                <li>Open the email from Physical AI Book</li>
                <li>Click the verification link</li>
                <li>You'll be automatically logged in</li>
              </ol>
            </div>

            <div className={styles.resendSection}>
              <p>Didn't receive the email?</p>
              <button
                onClick={handleResendVerification}
                className={styles.resendButton}
                disabled={loading}
              >
                {loading ? 'Resending...' : 'Resend Verification Email'}
              </button>
            </div>

            <button onClick={handleClose} className={styles.doneButton}>
              Done
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
