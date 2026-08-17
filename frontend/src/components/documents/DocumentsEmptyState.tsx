import { Link } from "react-router-dom";

export default function DocumentsEmptyState() {
  return (
    <div className="p-12 text-center">
      <h3 className="font-semibold text-slate-700">No documents</h3>
      <p className="text-sm text-slate-400 mt-2">Upload a document to start.</p>

      <Link
        to="/upload"
        className="inline-block mt-5 bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-semibold" style={{ color: "white" }}
      >
        Upload
      </Link>
    </div>
  );
}
