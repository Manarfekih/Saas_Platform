import { type ReactElement } from 'react';

type DocumentMetadataCardProps = {
  filename: string;
  docType: string | null;
  status: string;
  createdAt?: string;
  pageCount?: number;
};

export default function DocumentMetadataCard({
  filename,
  docType,
  status,
  createdAt,
  pageCount,
}: DocumentMetadataCardProps): ReactElement {

  const formatDate = (date?: string): string => {
    if (!date) return '—';
    return new Date(date).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getStatusDisplay = (status: string): string => {
    switch (status) {
      case 'processed': return '✅ Ready';
      case 'processing': return '⏳ Processing';
      case 'pending': return '⏳ Pending';
      case 'failed': return '❌ Failed';
      default: return status;
    }
  };

  const metadataItems: Array<{ label: string; value: string }> = [
    { label: 'File Name', value: filename },
    { label: 'Document Type', value: docType || 'Unknown' },
    { label: 'Status', value: getStatusDisplay(status) },
    { label: 'Uploaded', value: formatDate(createdAt) },
    { label: 'Pages', value: pageCount ? String(pageCount) : '—' },
  ];

  return (
    <div className="document-metadata-card">
      <div className="document-metadata-header">
        <h3 className="document-metadata-title">Document Details</h3>
        <span className={`document-metadata-status status-${status}`}>
          {getStatusDisplay(status)}
        </span>
      </div>
      <div className="document-metadata-list">
        {metadataItems.map((item) => (
          <div key={item.label} className="document-metadata-item">
            <span className="document-metadata-label">{item.label}</span>
            <span className="document-metadata-value" title={item.value}>
              {item.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
