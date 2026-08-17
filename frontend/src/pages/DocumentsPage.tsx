import { useEffect, useMemo, useState } from "react";
import api from "../api/auth";
import { useAuth } from "../context/AuthContext";
import DocumentsEmptyState from "../components/documents/DocumentsEmptyState";
import DocumentsHeader from "../components/documents/DocumentsHeader";
import DocumentsLoadingState from "../components/documents/DocumentsLoadingState";
import DocumentsList, { type DocumentType } from "../components/documents/DocumentsList";
import DocumentsSearchInput from "../components/documents/DocumentsSearchInput";
import DeleteConfirmationModal from "../components/documents/DeleteConfirmationModal";

export default function DocumentsPage() {
  const { token } = useAuth();

  const [documents, setDocuments] = useState<DocumentType[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deletingDoc, setDeletingDoc] = useState<DocumentType | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadDocuments() {
      if (!token) return;

      setLoading(true);

      try {
        const res = await api.get("/documents/", {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!cancelled) {
          setDocuments(res.data);
        }
      } catch (error) {
        console.error(error);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDocuments();

    return () => {
      cancelled = true;
    };
  }, [token]);

  const filteredDocuments = useMemo(
    () => documents.filter((doc) =>
      doc.filename.toLowerCase().includes(search.toLowerCase())
    ),
    [documents, search]
  );

  async function handleDelete(doc: DocumentType) {
    if (!token) return;

    setIsDeleting(true);
    try {
      await api.delete(`/documents/${doc.id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setDocuments((prev) => prev.filter((item) => item.id !== doc.id));
      setDeleteModalOpen(false);
      setDeletingDoc(null);
    } catch (error) {
      console.error("Delete error:", error);
      alert("Failed to delete document. Please try again.");
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

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <DocumentsHeader
        title="Documents"
        description="Manage your AI processed documents."
      />

      <DocumentsSearchInput value={search} onChange={setSearch} />

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <DocumentsLoadingState />
        ) : filteredDocuments.length === 0 ? (
          <DocumentsEmptyState />
        ) : (
          <DocumentsList 
            documents={filteredDocuments} 
            onDelete={(document) => {
              openDeleteModal(document);
            }} 
          />
        )}
      </div>

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