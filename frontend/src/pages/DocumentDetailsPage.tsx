// src/pages/DocumentDetailsPage.tsx
import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import api from "../api/auth";
import { useAuth } from "../context/AuthContext";
import DocumentChatCard from "../components/documents/details/DocumentChatCard";
import DocumentDetailsHeader from "../components/documents/details/DocumentDetailsHeader";
import DocumentStatusCard from "../components/documents/details/DocumentStatusCard";
import DocumentTextCard from "../components/documents/details/DocumentTextCard";
import DocumentMetadataCard from "../components/documents/details/DocumentMetadataCard";
import DocumentSummaryCard from "../components/documents/details/DocumentSummaryCard";
import SummaryPreviewModal from "../components/documents/details/SummaryPreviewModal";
import type { DocumentSummaryResponse } from "../types/summary";
import { getSummary, regenerateSummary, downloadSummary, previewSummaryFile } from "../api/summary";

import "../styles/document-details.css";

type DocumentDetails = {
  id: number;
  filename: string;
  status: string;
  doc_type: string | null;
  extracted_text: string | null;
  error_message: string | null;
  created_at?: string;
  page_count?: number;
  summary?: DocumentSummaryResponse | null;
  summary_file_name?: string | null;
};

type StatusResponse = {
  id: number;
  status: string;
  processing_step: string | null;
  progress: number;
  error_message: string | null;
};

type TabType = "summary" | "text" | "metadata";

type DocumentOpenState = {
  activeTab?: TabType;
  sourceText?: string;
  sourceLabel?: string;
  sourcePage?: number | null;
};

function buildPreviewSummary(document: DocumentDetails, resolvedDocType: string | null) {
  const text = document.extracted_text || "";
  const overview = text
    .replace(/---\s*PAGES?\s*\d+[-–]\d+\s*---/gi, "")
    .replace(/\[\[PAGE\s*\d+\]\]/gi, "")
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .slice(0, 6)
    .join(" ")
    .slice(0, 900);

  return {
    title: document.filename,
    document_type: resolvedDocType || "Document",
    overview: overview || "Summary is still being generated.",
    key_information: { people: [], organizations: [], dates: [], amounts: [] },
    sections: [],
    statistics: {
      total_items: 0,
      total_pages: document.page_count || 0,
      word_count: text.split(/\s+/).filter(Boolean).length,
      character_count: text.length,
      paragraph_count: text.split(/\n\n+/).filter(Boolean).length,
      generated_at: new Date().toISOString(),
    },
  };
}

function buildSourcePreview(text: string): string {
  const cleaned = text.replace(/\s+/g, " ").trim();
  if (!cleaned) return "";
  return cleaned.length > 260 ? `${cleaned.slice(0, 260).trimEnd()}...` : cleaned;
}

function buildSummaryExportFilename(filename: string, fallbackId?: number) {
  const baseName = filename.replace(/\.[^.]+$/, "").trim();
  const safeBaseName = baseName || (fallbackId ? `document_${fallbackId}` : "document");
  return `${safeBaseName}_summary.md`;
}

export default function DocumentDetailsPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const openState = (location.state || {}) as DocumentOpenState;

  const [document, setDocument] = useState<DocumentDetails | null>(null);
  const [summary, setSummary] = useState<DocumentSummaryResponse | null>(null);
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryPreviewOpen, setSummaryPreviewOpen] = useState(false);
  const [summaryPreviewContent, setSummaryPreviewContent] = useState<string | null>(null);
  const [summaryPreviewLoading, setSummaryPreviewLoading] = useState(false);
  const [summaryPreviewError, setSummaryPreviewError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>(openState.activeTab || "summary");
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    if (!token || !id) return;

    let cancelled = false;
    const headers = { Authorization: `Bearer ${token}` };

    async function loadSummary() {
      if (cancelled) return;
      setSummaryLoading(true);
      try {
        const summaryRes = await getSummary(Number(id));
        if (!cancelled) {
          setSummary(summaryRes);
        }
      } catch (summaryError: any) {
        if (!cancelled && summaryError?.response?.status !== 404 && summaryError?.response?.status !== 400) {
          console.error("Summary load error:", summaryError);
        }
      } finally {
        if (!cancelled) {
          setSummaryLoading(false);
        }
      }
    }

    async function loadDocument() {
      try {
        const [documentRes, statusRes] = await Promise.all([
          api.get(`/documents/${id}`, { headers }),
          api.get(`/documents/${id}/status`, { headers }),
        ]);

        if (cancelled) return;

        setDocument(documentRes.data);
        setStatus(statusRes.data);

        if (statusRes.data.status === "processed") {
          await loadSummary();
        }
        if (!cancelled) {
          setLoading(false);
        }
      } catch (requestError: any) {
        if (!cancelled) {
          setError(requestError?.response?.data?.detail || "Failed to load document");
          setLoading(false);
        }
      }
    }

    async function refreshStatus() {
      try {
        const res = await api.get(`/documents/${id}/status`, { headers });
        if (cancelled) return;

        setStatus(res.data);
        setDocument((prev) => (prev ? { ...prev, status: res.data.status } : prev));

        if (res.data.status === "processed" && !summary) {
          await loadSummary();
        }
      } catch (requestError) {
        console.error("Status refresh error:", requestError);
      }
    }

    loadDocument();

    const interval = setInterval(() => {
      if (document?.status === "processing" || document?.status === "pending" || (document?.status === "processed" && !summary)) {
        refreshStatus();
      }
    }, 3000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [token, id, document?.status, summary]);

  const openChat = async () => {
    if (!token || !id) return;

    try {
      const res = await api.get(`/documents/${id}/chat-session`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      navigate(`/chat/${id}`, {
        state: { session_id: res.data.session_id },
      });
    } catch (requestError) {
      console.error("Failed to open chat:", requestError);
    }
  };

  const goBack = () => {
    navigate("/documents");
  };

  const handleRegenerate = async () => {
    if (!id) return;
    if (!window.confirm("This will regenerate the summary using the latest AI model. Continue?")) {
      return;
    }

    try {
      setRegenerating(true);
      const data = await regenerateSummary(Number(id));
      setDocument((prev) =>
        prev
          ? {
              ...prev,
              summary: data.summary,
              summary_file_name: data.summary_file_name,
            }
          : null
      );
      setSummary(data);
    } catch (requestError) {
      console.error("Failed to regenerate summary:", requestError);
      alert("Failed to regenerate summary");
    } finally {
      setRegenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!id) return;

    try {
      const response = await downloadSummary(Number(id));
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = window.document.createElement("a");
      link.href = url;

      const contentDisposition = response.headers["content-disposition"];
      let filename = "document_" + id + "_summary.md";
      if (contentDisposition) {
        const match = contentDisposition.match(/filename=([^;]+)/);
        if (match) {
          filename = match[1].replace(/["']/g, "");
        }
      }

      link.setAttribute("download", filename);
      window.document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (requestError) {
      console.error("Failed to download summary:", requestError);
      alert("Failed to download summary");
    }
  };

  const handlePreviewSummaryFile = async () => {
    if (!id) return;

    try {
      setSummaryPreviewError(null);
      setSummaryPreviewLoading(true);
      setSummaryPreviewOpen(true);

      const content = await previewSummaryFile(Number(id));
      setSummaryPreviewContent(content);
    } catch (requestError) {
      console.error("Failed to preview summary file:", requestError);
      setSummaryPreviewContent(null);
      setSummaryPreviewError("Failed to load the summary file preview.");
    } finally {
      setSummaryPreviewLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="document-details-page">
        <div className="document-details-container">
          <div className="document-details-loading">
            <div className="loading-skeleton skeleton-header"></div>
            <div className="loading-skeleton skeleton-status"></div>
            <div className="loading-skeleton skeleton-content"></div>
            <div className="loading-skeleton skeleton-actions"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="document-details-page">
        <div className="document-details-container">
          <div className="document-error-state">
            <div className="document-error-icon">?</div>
            <h2>Document Not Found</h2>
            <p>{error || "The document you're looking for doesn't exist or has been removed."}</p>
            <button type="button" onClick={goBack} className="btn-itgate btn-itgate-sm">
              Back to Documents
            </button>
          </div>
        </div>
      </div>
    );
  }

  const isProcessing = document.status === "processing" || document.status === "pending";
  const isProcessed = document.status === "processed";
  const hasError = document.status === "failed";
  const resolvedDocType = document.doc_type ?? summary?.document_type ?? null;
  const displaySummary = summary?.summary || buildPreviewSummary(document, resolvedDocType);
  const summaryStatusNote = summaryLoading && !summary ? "Summary is being prepared. The preview below is based on extracted text." : null;
  const sourcePreview = buildSourcePreview(openState.sourceText || "");

  return (
    <div className="document-details-page">
      <div className="document-details-container">
        <div className="document-details-topbar">
          <button type="button" onClick={goBack} className="document-back-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5" />
              <path d="M12 19l-7-7 7-7" />
            </svg>
            Back to Documents
          </button>
          <div className="document-actions">
            {isProcessed && (
              <button type="button" onClick={openChat} className="btn-itgate btn-itgate-sm">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                Chat with Document
              </button>
            )}
          </div>
        </div>

        <div className="document-details-grid">
          <div className="document-details-main">
            <DocumentDetailsHeader filename={document.filename} docType={resolvedDocType} status={document.status} />

            <DocumentStatusCard
              status={status?.status}
              processingStep={status?.processing_step}
              progress={status?.progress}
              errorMessage={status?.error_message || document.error_message}
            />

            {isProcessed && (
              <div className="document-tabs">
                <button type="button" className={`document-tab ${activeTab === "summary" ? "active" : ""}`} onClick={() => setActiveTab("summary")}>
                  Summary
                </button>
                <button type="button" className={`document-tab ${activeTab === "text" ? "active" : ""}`} onClick={() => setActiveTab("text")}>
                  Text
                </button>
                <button type="button" className={`document-tab ${activeTab === "metadata" ? "active" : ""}`} onClick={() => setActiveTab("metadata")}>
                  Metadata
                </button>
              </div>
            )}

            {isProcessed && activeTab === "summary" && (
              <DocumentSummaryCard
                summary={{
                  ...displaySummary,
                  overview: summaryStatusNote ? `${displaySummary.overview}\n\n${summaryStatusNote}` : displaySummary.overview,
                }}
                onRegenerate={handleRegenerate}
                onDownload={handleDownload}
                onPreviewFile={handlePreviewSummaryFile}
                isRegenerating={regenerating}
                isPreviewing={summaryPreviewLoading}
              />
            )}

            {isProcessed && activeTab === "text" && (
              <>
                {openState.sourceText ? (
                  <div className="mb-4 rounded-xl border border-indigo-100 bg-indigo-50 px-4 py-3">
                    <p className="text-[11px] font-semibold uppercase tracking-wide text-indigo-500">
                      Source from chat
                    </p>
                    <p className="mt-1 text-sm font-medium text-slate-800">
                      {openState.sourceLabel || document.filename}
                    </p>
                    {openState.sourcePage ? (
                      <p className="mt-1 text-[11px] text-indigo-600">Page {openState.sourcePage}</p>
                    ) : null}
                    <p className="mt-2 text-sm leading-relaxed text-slate-600">
                      {sourcePreview}
                    </p>
                  </div>
                ) : null}

                <DocumentTextCard
                  extractedText={document.extracted_text}
                  isLoading={isProcessing}
                  hasError={hasError}
                  initialSearchTerm={openState.sourceText || ""}
                />
              </>
            )}

            {isProcessed && activeTab === "metadata" && (
              <DocumentMetadataCard
                filename={document.filename}
                docType={resolvedDocType || "Document"}
                status={document.status}
                createdAt={document.created_at}
                pageCount={document.page_count}
              />
            )}

            {!isProcessed && (
              <DocumentTextCard extractedText={document.extracted_text} isLoading={isProcessing} hasError={hasError} />
            )}
          </div>

          <div className="document-details-sidebar">
            {activeTab !== "metadata" && (
              <DocumentMetadataCard
                filename={document.filename}
                docType={resolvedDocType || "Document"}
                status={document.status}
                createdAt={document.created_at}
                pageCount={document.page_count}
              />
            )}

            <DocumentChatCard disabled={!isProcessed} onOpenChat={openChat} status={document.status} />
          </div>
        </div>
      </div>


      <SummaryPreviewModal
        isOpen={summaryPreviewOpen}
        onClose={() => setSummaryPreviewOpen(false)}
        onDownload={handleDownload}
        fileName={summary?.summary_file_name ?? document.summary_file_name ?? buildSummaryExportFilename(document.filename, document.id)}
        content={summaryPreviewContent}
        isLoading={summaryPreviewLoading}
        error={summaryPreviewError}
      />
    </div>
  );
}