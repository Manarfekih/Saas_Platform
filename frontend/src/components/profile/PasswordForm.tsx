
import React, { useState } from 'react';
import type { PasswordStrength } from "../../utils/passwordUtils"; // Assuming this type is defined in the utility file';

interface PasswordFormProps {
  currentPwd: string;
  newPwd: string;
  confirmPwd: string;
  loading: boolean;
  pwdStrength: PasswordStrength;
  onCurrentChange: (value: string) => void;
  onNewChange: (value: string) => void;
  onConfirmChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onClear: () => void;
}

export default function PasswordForm({
  currentPwd,
  newPwd,
  confirmPwd,
  loading,
  pwdStrength,
  onCurrentChange,
  onNewChange,
  onConfirmChange,
  onSubmit,
  onClear,
}: PasswordFormProps) {
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isDirty, setIsDirty] = useState(false);

  const handleChange = (field: string, value: string) => {
    setIsDirty(true);
    switch (field) {
      case 'current':
        onCurrentChange(value);
        break;
      case 'new':
        onNewChange(value);
        break;
      case 'confirm':
        onConfirmChange(value);
        break;
    }
  };

  const handleReset = () => {
    setIsDirty(false);
    onClear();
  };

  const handleSubmit = (e: React.FormEvent) => {
    setIsDirty(false);
    onSubmit(e);
  };

  const passwordsMatch = newPwd === confirmPwd && newPwd.length > 0;

  return (
    <div className="profile-password-card">
      <div className="profile-password-header">
        <div className="profile-password-header-left">
          <div className="profile-password-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" strokeWidth="1.5" />
              <path d="M7 11V7C7 4.23858 9.23858 2 12 2C14.7614 2 17 4.23858 17 7V11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>
          <div>
            <h3 className="profile-password-title">Security & Password</h3>
            <p className="profile-password-subtitle">
              Update your password and keep your account secure
            </p>
          </div>
        </div>
        <div className="profile-password-badge">
          <span className="badge-security">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M9 12L11 14L15 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Secure
          </span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="profile-password-form">
        <div className="profile-password-grid">
          {/* Current Password */}
          <div className="password-field-group">
            <label htmlFor="currentPassword" className="password-field-label">
              Current Password
              <span className="required-star">*</span>
            </label>
            <div className="password-input-wrapper">
              <span className="password-input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" strokeWidth="1.5" />
                  <path d="M7 11V7C7 4.23858 9.23858 2 12 2C14.7614 2 17 4.23858 17 7V11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </span>
              <input
                id="currentPassword"
                type={showCurrent ? 'text' : 'password'}
                value={currentPwd}
                onChange={(e) => handleChange('current', e.target.value)}
                placeholder="Enter current password"
                disabled={loading}
                className="password-field-input"
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowCurrent(!showCurrent)}
                tabIndex={-1}
              >
                {showCurrent ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {/* New Password */}
          <div className="password-field-group">
            <label htmlFor="newPassword" className="password-field-label">
              New Password
              <span className="required-star">*</span>
            </label>
            <div className="password-input-wrapper">
              <span className="password-input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" strokeWidth="1.5" />
                  <path d="M7 11V7C7 4.23858 9.23858 2 12 2C14.7614 2 17 4.23858 17 7V11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </span>
              <input
                id="newPassword"
                type={showNew ? 'text' : 'password'}
                value={newPwd}
                onChange={(e) => handleChange('new', e.target.value)}
                placeholder="Enter new password"
                disabled={loading}
                className="password-field-input"
                autoComplete="new-password"
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowNew(!showNew)}
                tabIndex={-1}
              >
                {showNew ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                )}
              </button>
            </div>
            {newPwd && (
              <div className="password-strength-container">
                <div className="password-strength-bar">
                  <div
                    className="password-strength-bar-fill"
                    style={{
                      width: pwdStrength.width,
                      background: pwdStrength.color,
                    }}
                  />
                </div>
                <span
                  className="password-strength-label"
                  style={{ color: pwdStrength.color }}
                >
                  {pwdStrength.label} password
                </span>
              </div>
            )}
          </div>

          {/* Confirm Password */}
          <div className="password-field-group">
            <label htmlFor="confirmPassword" className="password-field-label">
              Confirm Password
              <span className="required-star">*</span>
            </label>
            <div className="password-input-wrapper">
              <span className="password-input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
              <input
                id="confirmPassword"
                type={showConfirm ? 'text' : 'password'}
                value={confirmPwd}
                onChange={(e) => handleChange('confirm', e.target.value)}
                placeholder="Confirm new password"
                disabled={loading}
                className="password-field-input"
                autoComplete="new-password"
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowConfirm(!showConfirm)}
                tabIndex={-1}
              >
                {showConfirm ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                )}
              </button>
            </div>
            {confirmPwd && (
              <span className={`password-match-hint ${passwordsMatch ? 'match' : 'no-match'}`}>
                {passwordsMatch ? (
                  <>
                    <span className="match-icon">✓</span>
                    Passwords match
                  </>
                ) : (
                  <>
                    <span className="no-match-icon">✗</span>
                    Passwords do not match
                  </>
                )}
              </span>
            )}
          </div>
        </div>

        {/* Form Actions */}
        <div className="profile-password-actions">
          <div className="profile-password-actions-left">
            <span className="dirty-indicator">
              {isDirty && (
                <>
                  <span className="dirty-dot"></span>
                  Unsaved changes
                </>
              )}
            </span>
          </div>
          <div className="profile-password-actions-right">
            <button
              type="button"
              onClick={handleReset}
              className="btn-profile btn-profile-secondary"
              disabled={loading || !isDirty}
            >
              Reset
            </button>
            <button
              type="submit"
              className="btn-profile btn-profile-primary"
              disabled={loading || !isDirty}
            >
              {loading ? (
                <>
                  <span className="btn-spinner"></span>
                  Updating...
                </>
              ) : (
                'Update Password'
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}