import { useState, type ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";

import api from "../api/auth";
import { useAuth } from "../context/AuthContext";
import UploadHeader from "../components/upload/UploadHeader";
import UploadInfoCards from "../components/upload/UploadInfoCards";
import UploadPanel from "../components/upload/UploadPanel";

export default function UploadPage() {
  const { token } = useAuth();
  const navigate = useNavigate();

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    setError("");

    const selected = e.target.files?.[0];

    if (!selected) {
      return;
    }

    const allowed = ["pdf", "docx", "txt" , "png", "jpg", "jpeg", "csv", "xlsx", "pptx"];
    const extension = selected.name.split(".").pop()?.toLowerCase();

    if (!allowed.includes(extension || "")) {
      setError("Only PDF, DOCX, TXT, PNG, JPG, JPEG, CSV, XLSX and PPTX files are allowed");
      setFile(null);
      return;
    }

    setFile(selected);
  }

  async function uploadDocument() {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    if (!token) {
      return;
    }

    try {
      setLoading(true);
      setError("");

      const formData = new FormData();
      formData.append("file", file);

      const res = await api.post("/documents/upload", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });

      const documentId = res.data.document.id;
      navigate(`/documents/${documentId}`);
    } catch (error: unknown) {
      console.error(error);

      const detail =
        (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Upload failed";
      setError(detail);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <UploadHeader
        title="Upload Document"
        description="Upload a document and let AI analyze it."
        backTo="/dashboard"
        backLabel="Go back to dashboard"
      />

      <UploadPanel
        file={file}
        error={error}
        loading={loading}
        onFileChange={handleFileChange}
        onUpload={uploadDocument}
      />

      <UploadInfoCards />
    </div>
  );
}

