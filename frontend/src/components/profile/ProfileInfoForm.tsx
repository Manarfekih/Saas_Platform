// src/components/profile/ProfileInfoForm.tsx

import React, { useState } from 'react';

interface ProfileInfoFormProps {
  name: string;
  email: string;
  loading: boolean;
  onNameChange: (value: string) => void;
  onEmailChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onReset: () => void;
}

export default function ProfileInfoForm({
  name,
  email,
  loading,
  onNameChange,
  onEmailChange,
  onSubmit,
  onReset,
}: ProfileInfoFormProps) {
  const [isDirty, setIsDirty] = useState(false);

  const handleFieldChange = (field: 'name' | 'email', value: string) => {
    setIsDirty(true);
    if (field === 'name') onNameChange(value);
    else onEmailChange(value);
  };

  const handleReset = () => {
    setIsDirty(false);
    onReset();
  };

  const handleSubmit = (e: React.FormEvent) => {
    setIsDirty(false);
    onSubmit(e);
  };

  // Dynamic member since (you can get this from backend)
  const memberSince = new Date().toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric'
  });

  return (
    <div className="profile-info-card">
      <div className="profile-info-header">
        <div className="profile-info-header-left">
          <div className="profile-info-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12Z"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M20.5899 22C20.5899 18.13 16.7399 15 11.9999 15C7.25991 15 3.40991 18.13 3.40991 22"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div>
            <h3 className="profile-info-title">Personal Information</h3>
            <p className="profile-info-subtitle">
              Update your personal details and contact information
            </p>
          </div>
        </div>
        <div className="profile-info-badge">
          <span className="badge-verified">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path
                d="M20 6L9 17L4 12"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            Verified
          </span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="profile-info-form">
        <div className="profile-info-grid">
          {/* Full Name Field */}
          <div className="form-field-group">
            <label htmlFor="fullName" className="form-field-label">
              Full Name
              <span className="required-star">*</span>
            </label>
            <div className="form-field-input-wrapper">
              <span className="form-field-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12Z"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  />
                  <path
                    d="M20.5899 22C20.5899 18.13 16.7399 15 11.9999 15C7.25991 15 3.40991 18.13 3.40991 22"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  />
                </svg>
              </span>
              <input
                id="fullName"
                type="text"
                value={name}
                onChange={(e) => handleFieldChange('name', e.target.value)}
                placeholder="Enter your full name"
                disabled={loading}
                className="form-field-input"
                autoComplete="name"
              />
              {!loading && name && (
                <button
                  type="button"
                  className="form-field-clear"
                  onClick={() => handleFieldChange('name', '')}
                  aria-label="Clear name"
                >
                  ✕
                </button>
              )}
            </div>
            <span className="form-field-hint">Enter your full legal name</span>
          </div>

          {/* Email Field */}
          <div className="form-field-group">
            <label htmlFor="email" className="form-field-label">
              Email Address
              <span className="required-star">*</span>
            </label>
            <div className="form-field-input-wrapper">
              <span className="form-field-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M4 4H20C21.1 4 22 4.9 22 6V18C22 19.1 21.1 20 20 20H4C2.9 20 2 19.1 2 18V6C2 4.9 2.9 4 4 4Z"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M22 6L12 13L2 6"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => handleFieldChange('email', e.target.value)}
                placeholder="Enter your email address"
                disabled={loading}
                className="form-field-input"
                autoComplete="email"
              />
              {!loading && email && (
                <button
                  type="button"
                  className="form-field-clear"
                  onClick={() => handleFieldChange('email', '')}
                  aria-label="Clear email"
                >
                  ✕
                </button>
              )}
            </div>
            <span className="form-field-hint">We'll send notifications to this email</span>
          </div>

          {/* Account Info - Read Only */}
          <div className="form-field-group form-field-group-full">
            <div className="form-field-account-info">
              <div className="account-info-item">
                <span className="account-info-label">Account Status</span>
                <span className="account-info-value account-status-active">
                  <span className="status-dot"></span>
                  Active
                </span>
              </div>
              <div className="account-info-divider"></div>
              <div className="account-info-item">
                <span className="account-info-label">Member Since</span>
                <span className="account-info-value">{memberSince}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Form Actions */}
        <div className="profile-info-actions">
          <div className="profile-info-actions-left">
            {isDirty && (
              <span className="dirty-indicator">
                <span className="dirty-dot"></span>
                Unsaved changes
              </span>
            )}
          </div>
          <div className="profile-info-actions-right">
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
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}