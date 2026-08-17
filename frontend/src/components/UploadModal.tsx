import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function UploadModal() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    const handleOpen = () => {
      setIsOpen(true);
      setErrorMsg("");
      setFile(null);
    };
    window.addEventListener("open-upload-modal", handleOpen);
    return () => {
      window.removeEventListener("open-upload-modal", handleOpen);
    };
  }, []);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setErrorMsg("");
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post("/documents/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });

      const { document } = response.data;
      setIsOpen(false);
      
      navigate(`/documents/${document.id}`);
      
      window.dispatchEvent(new CustomEvent("refresh-documents"));
    } catch (err: any) {
      console.error(err);
      setErrorMsg(
        err.response?.data?.detail || "Upload failed. Verify that it is a valid PDF, DOCX, or text file."
      );
    } finally {
      setUploading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-6 relative overflow-hidden border border-slate-100">
        
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-800">Upload Enterprise Asset</h3>
          <button
            onClick={() => setIsOpen(false)}
            className="text-slate-400 hover:text-slate-600 transition-colors p-1 hover:bg-slate-50 rounded-lg"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        {errorMsg && (
          <div className="p-3.5 bg-rose-50 border border-rose-100 text-rose-600 rounded-xl text-sm font-medium">
            {errorMsg}
          </div>
        )}

        {/* Drag and Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-2xl p-8 text-center flex flex-col items-center justify-center transition-all ${
            dragActive ? "border-indigo-600 bg-indigo-50/50" : "border-slate-200 bg-slate-50"
          }`}
        >
          <div className="bg-white p-4 rounded-full shadow-sm border border-slate-100 mb-4 text-indigo-600">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>

          {file ? (
            <div className="space-y-1">
              <p className="font-semibold text-slate-800 text-sm max-w-xs truncate mx-auto">{file.name}</p>
              <p className="text-xs text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          ) : (
            <div className="space-y-1">
              <p className="text-sm font-semibold text-slate-800">
                Drag and drop your file here, or{" "}
                <label className="text-indigo-600 hover:text-indigo-700 cursor-pointer underline font-bold transition-colors">
                  browse
                  <input
                    type="file"
                    className="hidden"
                    onChange={handleFileChange}
                    accept=".pdf,.docx,.txt , .png,.jpg,.jpeg,.csv,.xlsx,.pptx"
                  />
                </label>
              </p>
              <p className="text-xs text-slate-400">Supports PDF, DOCX, TXT ... up to 25MB</p>
            </div>
          )}
        </div>

        {/* Buttons */}
        <div className="flex items-center justify-end space-x-3 pt-2">
          <button
            onClick={() => setIsOpen(false)}
            className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold shadow-md disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all flex items-center space-x-2"
          >
            {uploading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Uploading...</span>
              </>
            ) : (
              <span>Confirm & Ingest</span>
            )}
          </button>
        </div>

      </div>
    </div>
  );
}
