import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/auth";
import { useAuth } from "../context/AuthContext";
import DeleteConfirmationModal from "../components/documents/DeleteConfirmationModal";

type DashboardStats = {
  documents: number;
  processed: number;
  in_queue: number;
  failed: number;
  chats: number;
};

type DocumentType = {
  id: number;
  filename: string;
  status: string;
  doc_type?: string | null;
  created_at: string;
};

type StatCardProps = {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
};

function StatCard({ title, value, icon, color, bgColor }: StatCardProps) {
  return (
    <div className="stat-card-itgate" style={{ cursor: "default" }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "16px" }}>
        <div style={{
          width: "44px", height: "44px",
          borderRadius: "12px",
          background: bgColor,
          display: "flex", alignItems: "center", justifyContent: "center",
          flexShrink: 0,
        }}>
          {icon}
        </div>
      </div>
      <div style={{ fontSize: "36px", fontWeight: 800, color, lineHeight: 1, marginBottom: "6px" }}>
        {value}
      </div>
      <p style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.8px", color: "var(--body-color)", opacity: 0.65, margin: 0 }}>
        {title}
      </p>
    </div>
  );
}

function formatUploadDate(value?: string | null) {
  if (!value) return "N/A";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "N/A";
  return parsed.toLocaleDateString();
}

export default function DashboardPage() {
  const { token, userName } = useAuth();

  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats>({
    documents: 0, processed: 0, in_queue: 0, failed: 0, chats: 0,
  });
  const [documents, setDocuments] = useState<DocumentType[]>([]);
  
  // Delete modal state
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deletingDoc, setDeletingDoc] = useState<DocumentType | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (!token) { setLoading(false); return; }
    const headers = { Authorization: `Bearer ${token}` };
    Promise.all([
      api.get("/dashboard/stats", { headers }),
      api.get("/documents/", { headers }),
    ])
      .then(([statsRes, docsRes]) => {
        setStats(statsRes.data);
        setDocuments(docsRes.data);
      })
      .catch((err) => console.error("Dashboard loading error:", err))
      .finally(() => setLoading(false));
  }, [token]);

  async function handleDelete(doc: DocumentType) {
    if (!token) return;

    setIsDeleting(true);
    try {
      await api.delete(`/documents/${doc.id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      // Update the dashboard immediately so the deleted row disappears even if refresh is slow.
      setDocuments((prev) => prev.filter((item) => item.id !== doc.id));
      setDeleteModalOpen(false);
      setDeletingDoc(null);

      const headers = { Authorization: `Bearer ${token}` };
      const [statsRes, docsRes] = await Promise.all([
        api.get("/dashboard/stats", { headers }),
        api.get("/documents/", { headers }),
      ]);
      setStats(statsRes.data);
      setDocuments(docsRes.data);
    } catch (error) {
      console.error("Delete error:", error);
    } finally {
      setIsDeleting(false);
    }
  }

  function openDeleteModal(doc: DocumentType) {
    setDeletingDoc(doc);
    setDeleteModalOpen(true);
  }

  function closeDeleteModal() {
    if (!isDeleting) {
      setDeleteModalOpen(false);
      setDeletingDoc(null);
    }
  }

  const recentDocuments = documents.slice(0, 5);

  const statCards = [
    {
      title: "Total Documents",
      value: stats.documents,
      color: "var(--primary)",
      bgColor: "rgba(0,68,235,0.10)",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="var(--primary)" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
    },
    {
      title: "Processed",
      value: stats.processed,
      color: "var(--success)",
      bgColor: "rgba(71,177,106,0.10)",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="var(--success)" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      title: "In Queue",
      value: stats.in_queue,
      color: "var(--warning)",
      bgColor: "rgba(243,163,56,0.10)",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="var(--warning)" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      title: "Failed",
      value: stats.failed,
      color: "var(--danger)",
      bgColor: "rgba(242,111,77,0.10)",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="var(--danger)" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
    },
    {
      title: "Chat Sessions",
      value: stats.chats,
      color: "var(--info)",
      bgColor: "rgba(35,186,191,0.10)",
      icon: (
        <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="var(--info)" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h8M8 14h5m6 7l-3-3H7a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v10a2 2 0 01-.586 1.414L19 21z" />
        </svg>
      ),
    },
  ];

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "28px" }}>

      {/* Header */}
      <div className="animate-fadeInDown">
        <div style={{
          display: "inline-flex", alignItems: "center", gap: "8px",
          padding: "5px 14px",
          background: "rgba(0,68,235,0.08)",
          border: "1px solid rgba(0,68,235,0.15)",
          borderRadius: "50px",
          fontSize: "12px", fontWeight: 600, letterSpacing: "0.8px",
          textTransform: "uppercase",
          color: "var(--primary)",
          marginBottom: "12px",
        }}>
          <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--success)", display: "inline-block" }} />
          Live Dashboard
        </div>
        <h1 style={{ fontSize: "28px", fontWeight: 800, color: "var(--dark)", margin: 0, lineHeight: 1.2 }}>
          Welcome back, {userName}!
        </h1>
        <p style={{ fontSize: "14px", color: "var(--body-color)", margin: "6px 0 0", opacity: 0.75 }}>
          Here's an overview of your AI document workspace.
        </p>
      </div>

      {/* Stats Grid */}
      {loading ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "18px" }}>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton" style={{ height: "120px" }} />
          ))}
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "18px" }} className="animate-fadeInUp">
          {statCards.map((card, i) => (
            <StatCard key={i} {...card} />
          ))}
        </div>
      )}

      {/* Recent Documents Table */}
      <div className="card-itgate" style={{ overflow: "hidden" }}>
        <div style={{
          padding: "20px 24px",
          borderBottom: "1.5px solid var(--border-color)",
          display: "flex", alignItems: "center", justifyContent: "space-between",
        }}>
          <div>
            <h2 style={{ fontSize: "16px", fontWeight: 800, color: "var(--dark)", margin: 0 }}>
              Recent Documents
            </h2>
            <p style={{ fontSize: "13px", color: "var(--body-color)", margin: "3px 0 0", opacity: 0.65 }}>
              Your latest uploaded documents
            </p>
          </div>
          <Link
            to="/documents"
            className="btn-itgate-outline btn-itgate-sm"
            style={{ textDecoration: "none" }}
          >
            View All
          </Link>
        </div>

        {loading ? (
          <div style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "12px" }}>
            {[...Array(4)].map((_, i) => (
              <div key={i} className="skeleton" style={{ height: "52px" }} />
            ))}
          </div>
        ) : recentDocuments.length === 0 ? (
          <div style={{ padding: "60px 24px", textAlign: "center" }}>
            <div style={{
              width: "64px", height: "64px", borderRadius: "18px",
              background: "rgba(0,68,235,0.08)",
              display: "flex", alignItems: "center", justifyContent: "center",
              margin: "0 auto 18px",
            }}>
              <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="var(--primary)" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p style={{ fontWeight: 700, color: "var(--dark)", marginBottom: "6px" }}>No documents uploaded yet</p>
            <p style={{ fontSize: "14px", color: "var(--body-color)", marginBottom: "24px", opacity: 0.65 }}>
              Upload your first document to start chatting with AI.
            </p>
            <Link to="/upload" className="btn-itgate" style={{ textDecoration: "none" }}>
              Upload Document
            </Link>
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="itgate-table">
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Type</th>
                  <th>Uploaded</th>
                  <th>Status</th>
                  <th style={{ textAlign: "right" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentDocuments.map((doc) => {
                  const status = doc.status.toLowerCase();
                  const ready = status === "completed" || status === "processed";
                  const failed = status === "failed";
                  return (
                    <tr key={doc.id}>
                      <td>
                        <div style={{ fontWeight: 600, color: "var(--dark)", fontSize: "14px" }}>
                          {doc.filename}
                        </div>
                      </td>
                      <td style={{ fontSize: "13px" }}>{doc.doc_type || "Document"}</td>
                      <td style={{ fontSize: "13px" }}>{formatUploadDate(doc.created_at)}</td>
                      <td>
                        {ready && <span className="badge-success">✓ Ready</span>}
                        {failed && <span className="badge-danger">✗ Failed</span>}
                        {!ready && !failed && <span className="badge-warning">⏳ Processing</span>}
                      </td>
                      <td>
                        <div style={{ display: "flex", justifyContent: "flex-end", alignItems: "center", gap: "8px" }}>
                          {ready && (
                            <Link
                              to={`/chat/${doc.id}`}
                              className="btn-itgate btn-itgate-sm"
                              style={{ textDecoration: "none", padding: "7px 16px", fontSize: "12px" }}
                            >
                              Chat
                            </Link>
                          )}
                          <Link
                            to={`/documents/${doc.id}`}
                            className="btn-itgate-outline btn-itgate-sm"
                            style={{ textDecoration: "none", padding: "6px 16px", fontSize: "12px" }}
                          >
                            View
                          </Link>
                          <button
                            onClick={() => openDeleteModal(doc)}
                            style={{
                              padding: "7px 16px", fontSize: "12px",
                              fontWeight: 600, letterSpacing: "0.4px",
                              textTransform: "uppercase",
                              background: "rgba(242,111,77,0.08)",
                              color: "var(--danger)",
                              border: "1px solid rgba(242,111,77,0.25)",
                              borderRadius: "50px",
                              cursor: "pointer",
                              transition: "var(--transition)",
                            }}
                            onMouseEnter={e => {
                              (e.currentTarget as HTMLButtonElement).style.background = "rgba(242,111,77,0.16)";
                            }}
                            onMouseLeave={e => {
                              (e.currentTarget as HTMLButtonElement).style.background = "rgba(242,111,77,0.08)";
                            }}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "18px" }}>
        <Link
          to="/upload"
          className="card-itgate"
          style={{ padding: "28px", textDecoration: "none", display: "block" }}
        >
          <div style={{
            width: "48px", height: "48px", borderRadius: "14px",
            background: "rgba(0,68,235,0.10)",
            display: "flex", alignItems: "center", justifyContent: "center",
            marginBottom: "16px",
          }}>
            <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="var(--primary)" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
          <h3 style={{ fontSize: "16px", fontWeight: 800, color: "var(--dark)", margin: "0 0 6px" }}>
            Upload Document
          </h3>
          <p style={{ fontSize: "13px", color: "var(--body-color)", margin: 0, opacity: 0.70, lineHeight: 1.6 }}>
            Upload PDF, DOCX and TXT files for AI processing.
          </p>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: "6px",
            marginTop: "16px", fontSize: "13px", fontWeight: 700,
            color: "var(--primary)",
          }}>
            Get Started
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </div>
        </Link>

        <Link
          to="/documents"
          className="card-itgate"
          style={{ padding: "28px", textDecoration: "none", display: "block" }}
        >
          <div style={{
            width: "48px", height: "48px", borderRadius: "14px",
            background: "rgba(35,186,191,0.10)",
            display: "flex", alignItems: "center", justifyContent: "center",
            marginBottom: "16px",
          }}>
            <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="var(--info)" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
            </svg>
          </div>
          <h3 style={{ fontSize: "16px", fontWeight: 800, color: "var(--dark)", margin: "0 0 6px" }}>
            Browse Documents
          </h3>
          <p style={{ fontSize: "13px", color: "var(--body-color)", margin: 0, opacity: 0.70, lineHeight: 1.6 }}>
            View and interact with your uploaded files.
          </p>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: "6px",
            marginTop: "16px", fontSize: "13px", fontWeight: 700,
            color: "var(--info)",
          }}>
            Browse All
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </div>
        </Link>
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        isOpen={deleteModalOpen}
        onClose={closeDeleteModal}
        onConfirm={() => {
          if (deletingDoc) {
            void handleDelete(deletingDoc);
          }
        }}
        filename={deletingDoc?.filename || ""}
        isDeleting={isDeleting}
      />
    </div>
  );
}