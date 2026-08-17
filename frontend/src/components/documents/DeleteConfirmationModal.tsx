import { useEffect, useRef, type MouseEvent } from "react";
import { createPortal } from "react-dom";

type DeleteConfirmationModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  filename: string;
  isDeleting?: boolean;
};

export default function DeleteConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  filename,
  isDeleting = false,
}: DeleteConfirmationModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen && !isDeleting) {
        onClose();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, isDeleting, onClose]);

  // Focus trap
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

  const handleBackdropClick = (e: MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget && !isDeleting) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <div
      className="delete-modal-overlay"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-modal-title"
    >
      <div className="delete-modal" ref={modalRef}>
        {/* Close button */}
        <button type="button"
          className="delete-modal-close"
          onClick={onClose}
          disabled={isDeleting}
          aria-label="Close dialog"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Icon */}
        <div className="delete-modal-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>

        {/* Content */}
        <h2 id="delete-modal-title" className="delete-modal-title">
          Delete Document
        </h2>
        
        <p className="delete-modal-message">
          Are you sure you want to delete <strong>"{filename}"</strong>?
        </p>
        
        <p className="delete-modal-warning">
          This action cannot be undone. All associated data, including embeddings and chat history, will be permanently removed.
        </p>

        {/* Actions */}
        <div className="delete-modal-actions">
          <button type="button"
            className="delete-modal-btn delete-modal-btn-secondary"
            onClick={onClose}
            disabled={isDeleting}
          >
            Cancel
          </button>
          <button type="button"
            className="delete-modal-btn delete-modal-btn-danger"
            onClick={onConfirm}
            disabled={isDeleting}
          >
            {isDeleting ? (
              <>
                <span className="delete-modal-spinner"></span>
                Deleting...
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete Document
              </>
            )}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}