
interface RegenerateConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isRegenerating: boolean;
}

export default function RegenerateConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  isRegenerating,
}: RegenerateConfirmationModalProps) {
  if (!isOpen) return null;

  return (
    <div className="delete-modal-overlay" onClick={onClose}>
      <div className="delete-modal" onClick={(e) => e.stopPropagation()}>
        {/* Close Button */}
        <button
          type="button"
          className="delete-modal-close"
          onClick={onClose}
          disabled={isRegenerating}
          aria-label="Close"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="delete-modal-icon" style={{ background: 'rgba(0, 68, 235, 0.08)', color: '#0044eb' }}>
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
          </svg>
        </div>

        <h2 className="delete-modal-title">Regenerate Summary</h2>

        <p className="delete-modal-message">
          This will regenerate the document summary using the latest AI model.
        </p>

        <p className="delete-modal-warning">
          ⚠️ Any changes or custom notes in the current summary will be lost. The new summary will be generated from the original document content.
        </p>

        
        <div className="delete-modal-actions">
          <button
            type="button"
            className="delete-modal-btn delete-modal-btn-secondary"
            onClick={onClose}
            disabled={isRegenerating}
          >
            Cancel
          </button>
          <button
            type="button"
            className="delete-modal-btn"
            style={{
              background: '#0044eb',
              color: '#ffffff',
            }}
            onClick={onConfirm}
            disabled={isRegenerating}
          >
            {isRegenerating ? (
              <>
                <span className="delete-modal-spinner" />
                Regenerating...
              </>
            ) : (
              'Regenerate Summary'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}