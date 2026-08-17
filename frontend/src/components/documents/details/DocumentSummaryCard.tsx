import { useState, type ReactElement } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { DocumentSummary } from '../../../types/summary';
import RegenerateConfirmationModal from '../RegenerateConfirmationModal';

type DocumentSummaryCardProps = {
  summary: DocumentSummary;
  onRegenerate: () => Promise<void>;
  onDownload: () => Promise<void>;
  onPreviewFile: () => Promise<void>;
  isRegenerating: boolean;
  isPreviewing: boolean;
};

function formatGeneratedAt(value?: string | null) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function splitOverviewText(overview: string) {
  return overview
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);
}

export default function DocumentSummaryCard({
  summary,
  onRegenerate,
  onDownload,
  onPreviewFile,
  isRegenerating,
  isPreviewing,
}: DocumentSummaryCardProps): ReactElement {
  const [showRegenerateModal, setShowRegenerateModal] = useState(false);
  
  const hasKeyInfo = Object.values(summary.key_information).some((items) => items.length > 0);
  const generatedAt = formatGeneratedAt(summary.statistics?.generated_at);
  const overviewLines = splitOverviewText(summary.overview || '');


  const handleRegenerateClick = () => {
    setShowRegenerateModal(true);
  };

  const handleRegenerateConfirm = async () => {
    setShowRegenerateModal(false);
    await onRegenerate();
  };

  const buildMarkdownContent = () => {
    const lines = [];
    
    lines.push(`# ${summary.title || 'Document Summary'}`);
    lines.push('');
    lines.push(`**Document Type:** ${summary.document_type || 'Unknown'}`);
    lines.push('');
    
    lines.push('## Overview');
    if (overviewLines.length > 0) {
      lines.push(overviewLines.join('\n'));
    } else {
      lines.push('No overview available.');
    }
    lines.push('');
    
    if (hasKeyInfo) {
      lines.push('## Key Information');
      for (const [key, values] of Object.entries(summary.key_information)) {
        if (values.length > 0) {
          const label = key.replace('_', ' ').toUpperCase();
          lines.push(`**${label}:** ${values.join(', ')}`);
        }
      }
      lines.push('');
    }
    
    if (summary.sections.length > 0) {
      lines.push('## Detailed Sections');
      lines.push('');
      for (const section of summary.sections) {
        lines.push(`### ${section.title}`);
        for (const item of section.items) {
          if (typeof item === 'string') {
            lines.push(`- ${item}`);
          } else {
            const description = item.description ? `: ${item.description}` : '';
            lines.push(`- **${item.name}**${description}`);
          }
        }
        lines.push('');
      }
    }
    
    if (summary.statistics) {
      lines.push('## Statistics');
      for (const [key, value] of Object.entries(summary.statistics)) {
        if (key !== 'generated_at') {
          const label = key.replace('_', ' ').toUpperCase();
          lines.push(`- **${label}:** ${value}`);
        }
      }
      if (generatedAt) {
        lines.push(`- **Generated At:** ${generatedAt}`);
      }
    }
    
    return lines.join('\n');
  };

  const markdownContent = buildMarkdownContent();

  return (
    <>
      <div className="premium-summary-card">
        <div className="premium-summary-header">
          <div className="title-area">
            <div className="document-icon-wrapper">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="doc-icon">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
            </div>
            <div>
              <h2 className="premium-summary-title">{summary.title || 'Document Summary'}</h2>
              {summary.document_type && (
                <span className="premium-summary-badge">{summary.document_type}</span>
              )}
            </div>
          </div>

          <div className="premium-summary-actions">
            <button
              type="button"
              onClick={handleRegenerateClick}
              disabled={isRegenerating}
              className="btn-premium btn-regenerate"
              title="Regenerate summary using latest AI model"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className={`btn-icon ${isRegenerating ? 'spin' : ''}`}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
              <span>{isRegenerating ? 'Regenerating...' : 'Regenerate'}</span>
            </button>

            <button
              type="button"
              onClick={onPreviewFile}
              disabled={isPreviewing}
              className="btn-premium-outline btn-preview"
              title="Preview the exact summary file content"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className={`btn-icon ${isPreviewing ? 'spin' : ''}`}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12s3.75-6.75 9.75-6.75S21.75 12 21.75 12 18 18.75 12 18.75 2.25 12 2.25 12z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 15.75a3.75 3.75 0 1 0 0-7.5 3.75 3.75 0 0 0 0 7.5z" />
              </svg>
              <span>{isPreviewing ? 'Loading...' : 'Preview file'}</span>
            </button>

            <button
              type="button"
              onClick={onDownload}
              className="btn-premium-outline btn-download"
              title="Download Summary as Markdown"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="btn-icon">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
              </svg>
              <span>Download</span>
            </button>
          </div>
        </div>

        

            <div className="premium-summary-resume">
          <div className="resume-content-area">
            <div className="resume-markdown-container">
              <div className="resume-markdown-content">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({ children }) => (
                      <h1 className="markdown-h1">{children}</h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="markdown-h2">{children}</h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="markdown-h3">{children}</h3>
                    ),
                    p: ({ children }) => (
                      <p className="markdown-p">{children}</p>
                    ),
                    ul: ({ children }) => (
                      <ul className="markdown-ul">{children}</ul>
                    ),
                    li: ({ children }) => (
                      <li className="markdown-li">{children}</li>
                    ),
                    strong: ({ children }) => (
                      <strong className="markdown-strong">{children}</strong>
                    ),
                  }}
                >
                  {markdownContent}
                </ReactMarkdown>
              </div>
            </div>

            

            

            {summary.statistics && (
              <div className="resume-quick-stats">
                
                <div className="quick-stat-divider"></div>
                <div className="quick-stat">
                  <span className="quick-stat-value">{summary.statistics.word_count || 0}</span>
                  <span className="quick-stat-label">Words</span>
                </div>
                <div className="quick-stat-divider"></div>
                <div className="quick-stat">
                  <span className="quick-stat-value">{summary.statistics.total_pages || 0}</span>
                  <span className="quick-stat-label">Pages</span>
                </div>
                {generatedAt && (
                  <>
                    <div className="quick-stat-divider"></div>
                    <div className="quick-stat quick-stat-date">
                      <span className="quick-stat-label">Generated</span>
                      <span className="quick-stat-value-date">{generatedAt}</span>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        {hasKeyInfo && (
          <div className="premium-summary-keyinfo">
            <h3 className="sub-section-title">Key Information</h3>
            <div className="keyinfo-grid">
              {summary.key_information.people.length > 0 && (
                <div className="keyinfo-box keyinfo-people">
                  <div className="keyinfo-header">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="box-icon">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
                    </svg>
                    <span>People</span>
                  </div>
                  <div className="keyinfo-pills">
                    {summary.key_information.people.map((person, index) => (
                      <span key={index} className="premium-pill pill-people">{person}</span>
                    ))}
                  </div>
                </div>
              )}

              {summary.key_information.organizations.length > 0 && (
                <div className="keyinfo-box keyinfo-orgs">
                  <div className="keyinfo-header">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="box-icon">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21h10.5V3.75c0-.621-.504-1.125-1.125-1.125H7.875c-.621 0-1.125.504-1.125 1.125V21z" />
                    </svg>
                    <span>Organizations</span>
                  </div>
                  <div className="keyinfo-pills">
                    {summary.key_information.organizations.map((org, index) => (
                      <span key={index} className="premium-pill pill-orgs">{org}</span>
                    ))}
                  </div>
                </div>
              )}

              {summary.key_information.dates.length > 0 && (
                <div className="keyinfo-box keyinfo-dates">
                  <div className="keyinfo-header">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="box-icon">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5m-9-6h.008v.008H12v-.008zM12 15h.008v.008H12V15zm0 2.25h.008v.008H12v-.008zM9.75 15h.008v.008H9.75V15zm0 2.25h.008v.008H9.75v-.008zM7.5 15h.008v.008H7.5V15zm0 2.25h.008v.008H7.5v-.008zm6.75-4.5h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V15zm0 2.25h.008v.008h-.008v-.008zm2.25-4.5h.008v.008H16.5v-.008zm0 2.25h.008v.008H16.5V15z" />
                    </svg>
                    <span>Dates</span>
                  </div>
                  <div className="keyinfo-pills">
                    {summary.key_information.dates.map((date, index) => (
                      <span key={index} className="premium-pill pill-dates">{date}</span>
                    ))}
                  </div>
                </div>
              )}

              {summary.key_information.amounts.length > 0 && (
                <div className="keyinfo-box keyinfo-amounts">
                  <div className="keyinfo-header">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="box-icon">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.214.075a8.204 8.204 0 001.98.318c1.656 0 3-.624 3-1.5s-1.344-1.5-3-1.5c-1.656 0-3-.624-3-1.5s1.344-1.5 3-1.5c.894 0 1.705.278 2.22.766M8 5.902a8.004 8.004 0 0110.196 0m-10.196 0L8 5.902z" />
                    </svg>
                    <span>Amounts</span>
                  </div>
                  <div className="keyinfo-pills">
                    {summary.key_information.amounts.map((amount, index) => (
                      <span key={index} className="premium-pill pill-amounts">{amount}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {generatedAt && (
          <div className="premium-summary-footer">
            <span>Analysis generated on {generatedAt}</span>
          </div>
        )}
      </div>

      <RegenerateConfirmationModal
        isOpen={showRegenerateModal}
        onClose={() => setShowRegenerateModal(false)}
        onConfirm={handleRegenerateConfirm}
        isRegenerating={isRegenerating}
      />
    </>
  );
}

