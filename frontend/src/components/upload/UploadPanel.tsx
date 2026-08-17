import type { ChangeEvent } from "react";

type UploadPanelProps = {
  file: File | null;
  error: string;
  loading: boolean;
  onFileChange: (e: ChangeEvent<HTMLInputElement>) => void;
  onUpload: () => void;
};

export default function UploadPanel({
  file,
  error,
  loading,
  onFileChange,
  onUpload,
}: UploadPanelProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-8">
      <label className="block border-2 border-dashed border-slate-300 rounded-2xl p-10 text-center cursor-pointer hover:border-indigo-400 transition">
        <input type="file" className="hidden" onChange={onFileChange} />

        {file ? (
          <div>
            <p className="font-semibold text-slate-800">{file.name}</p>
            <p className="text-sm text-slate-400 mt-2">Ready to upload</p>
          </div>
        ) : (
          <div>
            <p className="font-semibold text-slate-700">Click to select file</p>
            <p className="text-sm text-slate-400 mt-2">PDF, DOCX, TXT ... supported</p>
          </div>
        )}
      </label>

      {error && (
        <div className="mt-5 bg-rose-50 text-rose-700 rounded-xl p-4 text-sm">{error}</div>
      )}

      <button
        onClick={onUpload}
        disabled={loading}
        className="mt-6 w-full bg-indigo-600 text-white py-3 rounded-xl font-semibold hover:bg-indigo-700 disabled:opacity-50 transition"
      >
        {loading ? "Uploading..." : "Upload Document"}
      </button>
    </div>
  );
}

