import { useEffect, useRef, type MouseEvent, type ReactElement } from "react";
import { createPortal } from "react-dom";

type SummaryPreviewModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onDownload: () => void;
  fileName: string | null;
  content: string | null;
  isLoading: boolean;
  error: string | null;
};

export default function SummaryPreviewModal({
  isOpen,
  onClose,
  onDownload,
  fileName,
  content,
  isLoading,
  error,
}: SummaryPreviewModalProps): ReactElement | null {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isOpen && !isLoading) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, isLoading, onClose]);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      const focusable = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      if (focusable.length > 0) {
        (focusable[0] as HTMLElement).focus();
      }
    }
  }, [isOpen]);

  const handleBackdropClick = (event: MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget && !isLoading) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <div
      className="summary-preview-modal-overlay"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="summary-preview-modal-title"
    >
      <div className="summary-preview-modal" ref={modalRef}>
        <button
          type="button"
          className="summary-preview-modal-close"
          onClick={onClose}
          disabled={isLoading}
          aria-label="Close dialog"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="summary-preview-modal-icon">
          <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9z" />
          </svg>
        </div>

        <h2 id="summary-preview-modal-title" className="summary-preview-modal-title">
          Summary File Preview
        </h2>

        <p className="summary-preview-modal-message">
          Review the exact content that will be downloaded before you save it.
        </p>

        {fileName ? (
          <p className="summary-preview-modal-filename">
            <strong>File:</strong> {fileName}
          </p>
        ) : null}

        <div className="summary-preview-modal-body">
          {isLoading ? (
            <div className="summary-preview-modal-loading">
              <span className="summary-preview-modal-spinner" />
              <span>Loading summary file content...</span>
            </div>
          ) : error ? (
            <div className="summary-preview-modal-error">
              {error}
            </div>
          ) : (
            <pre className="summary-preview-modal-content">{content || "No preview content available."}</pre>
          )}
        </div>

        <div className="summary-preview-modal-actions">
          <button
            type="button"
            className="summary-preview-modal-btn summary-preview-modal-btn-secondary"
            onClick={onClose}
            disabled={isLoading}
          >
            Close
          </button>
          <button
            type="button"
            className="summary-preview-modal-btn summary-preview-modal-btn-primary"
            onClick={onDownload}
            disabled={isLoading || !!error}
          >
            Download Summary
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
