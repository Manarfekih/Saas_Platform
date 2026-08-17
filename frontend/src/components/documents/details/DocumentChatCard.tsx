import { type ReactElement } from 'react';

type DocumentChatCardProps = {
  disabled: boolean;
  onOpenChat: () => void;
  status: string;
};

export default function DocumentChatCard({
  disabled,
  onOpenChat,
  status,
}: DocumentChatCardProps): ReactElement {
  const isReady = status === 'processed';

  return (
    <div className="document-chat-card">
      <div className="document-chat-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          <path d="M8 10h.01" strokeWidth="2.5" />
          <path d="M12 10h.01" strokeWidth="2.5" />
          <path d="M16 10h.01" strokeWidth="2.5" />
        </svg>
      </div>
      <div className="document-chat-content">
        <h4 className="document-chat-title">Chat with Document</h4>
        <p className="document-chat-description">
          {isReady 
            ? 'Ask questions about this document using AI' 
            : 'Document needs to be processed before chatting'}
        </p>
      </div>
      <button
        type="button"
        onClick={onOpenChat}
        disabled={disabled}
        className={`document-chat-btn ${isReady ? 'ready' : 'disabled'}`}
      >
        {isReady ? (
          <>
            <span>Start Chat</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14" />
              <path d="M12 5l7 7-7 7" />
            </svg>
          </>
        ) : (
          <span>Processing...</span>
        )}
      </button>
    </div>
  );
}