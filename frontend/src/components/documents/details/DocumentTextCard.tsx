import { type ReactElement, useEffect, useState } from 'react';

type DocumentTextCardProps = {
  extractedText: string | null;
  isLoading?: boolean;
  hasError?: boolean;
  initialSearchTerm?: string;
};

export default function DocumentTextCard({
  extractedText,
  isLoading = false,
  hasError = false,
  initialSearchTerm = '',
}: DocumentTextCardProps): ReactElement {
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchTerm, setSearchTerm] = useState(initialSearchTerm);

  const text = extractedText || '';
  const wordCount = text ? text.split(/\s+/).length : 0;
  const charCount = text ? text.length : 0;

  useEffect(() => {
    if (initialSearchTerm) {
      setSearchTerm(initialSearchTerm);
      setIsExpanded(true);
    }
  }, [initialSearchTerm]);

  const getTextPreview = (): string => {
    if (!text) return '';
    const preview = text.slice(0, 500);
    return preview + (text.length > 500 ? '...' : '');
  };

  const highlightText = (value: string, term: string): string => {
    if (!term.trim()) return value;
    const regex = new RegExp(`(${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return value.replace(regex, '<mark class="text-highlight">$1</mark>');
  };

  const displayedText = isExpanded ? text : getTextPreview();

  if (isLoading) {
    return (
      <div className="document-text-card">
        <div className="document-text-header">
          <h3 className="document-text-title">Extracted Text</h3>
          <span className="document-text-badge processing">Processing...</span>
        </div>
        <div className="document-text-loading">
          <div className="loading-line"></div>
          <div className="loading-line"></div>
          <div className="loading-line short"></div>
        </div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="document-text-card">
        <div className="document-text-header">
          <h3 className="document-text-title">Extracted Text</h3>
          <span className="document-text-badge error">Failed</span>
        </div>
        <div className="document-text-error">
          <span className="error-icon">⚠️</span>
          <p>Text extraction failed for this document.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="document-text-card">
      <div className="document-text-header">
        <div className="document-text-header-left">
          <h3 className="document-text-title">Extracted Text</h3>
          <span className="document-text-stats">
            {wordCount} words • {charCount} characters
          </span>
        </div>
        <div className="document-text-header-right">
          <button
            type="button"
            className="document-text-toggle"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? 'Show Less' : 'Show More'}
          </button>
        </div>
      </div>

      {text ? (
        <>
          <div className="document-text-search">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
            <input
              type="text"
              placeholder="Search in text..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="document-text-search-input"
            />
          </div>

          <div className="document-text-content">
            <pre
              className="document-text-pre"
              dangerouslySetInnerHTML={{
                __html: highlightText(displayedText, searchTerm),
              }}
            />
          </div>

          {!isExpanded && text.length > 500 && (
            <div className="document-text-expand-hint">
              <button type="button" onClick={() => setIsExpanded(true)}>
                Read full text →
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="document-text-empty">
          <span className="empty-icon">📝</span>
          <p>No text extracted from this document.</p>
          <span className="empty-hint">The document may be empty or in an unsupported format.</span>
        </div>
      )}
    </div>
  );
}
