import { type ReactElement } from 'react';

type DocumentDetailsHeaderProps = {
  filename: string;
  docType: string | null;
  status?: string;
};

export default function DocumentDetailsHeader({
  filename,
  docType,
  status,
}: DocumentDetailsHeaderProps): ReactElement {
  const getStatusBadge = (status?: string): string => {
    switch (status) {
      case 'processed': return 'ready';
      case 'processing': return 'processing';
      case 'pending': return 'processing';
      case 'failed': return 'failed';
      default: return 'unknown';
    }
  };

  return (
    <div className="document-details-header">
      <div className="document-details-header-content">
        <div className="document-details-header-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
        </div>
        <div>
          <h1 className="document-details-header-title">{filename}</h1>
          <div className="document-details-header-meta">
            <span className="document-details-header-type">{docType || 'Document'}</span>
            {status && (
              <span className={`document-details-header-badge badge-${getStatusBadge(status)}`}>
                {status}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}