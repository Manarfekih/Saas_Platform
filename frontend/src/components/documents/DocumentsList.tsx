import { Link } from "react-router-dom";

export type DocumentType = {
  id: number;
  filename: string;
  status: string;
  doc_type: string | null;
  created_at: string;
};

type DocumentsListProps = {
  documents: DocumentType[];
  onDelete: (doc: DocumentType) => void;
};

function formatDate(value: string) {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "N/A";
  return parsed.toLocaleDateString();
}

export default function DocumentsList({ documents, onDelete }: DocumentsListProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-100">
            <th className="text-left text-xs font-semibold uppercase tracking-wider text-slate-500 py-4 px-6">
              Document
            </th>
            <th className="text-left text-xs font-semibold uppercase tracking-wider text-slate-500 py-4 px-6">
              Type
            </th>
            <th className="text-left text-xs font-semibold uppercase tracking-wider text-slate-500 py-4 px-6">
              Uploaded
            </th>
            <th className="text-left text-xs font-semibold uppercase tracking-wider text-slate-500 py-4 px-6">
              Status
            </th>
            <th className="text-right text-xs font-semibold uppercase tracking-wider text-slate-500 py-4 px-6">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => {
            const isReady = doc.status === "processed" || doc.status === "completed";
            const isFailed = doc.status === "failed";

            return (
              <tr key={doc.id} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                <td className="py-4 px-6">
                  <div className="font-medium text-slate-800">{doc.filename}</div>
                </td>
                <td className="py-4 px-6 text-sm text-slate-600">
                  {doc.doc_type || "Document"}
                </td>
                <td className="py-4 px-6 text-sm text-slate-600">
                  {formatDate(doc.created_at)}
                </td>
                <td className="py-4 px-6">
                  {isReady && <span className="badge-success">✓ Ready</span>}
                  {isFailed && <span className="badge-danger">✗ Failed</span>}
                  {!isReady && !isFailed && <span className="badge-warning">⏳ Processing</span>}
                </td>
                <td className="py-4 px-6">
                  <div className="flex justify-end items-center gap-2">
                    {isReady && (
                      <Link
                        to={`/chat/${doc.id}`}
                        className="btn-itgate btn-itgate-sm"
                      >
                        Chat
                      </Link>
                    )}
                    <Link
                      to={`/documents/${doc.id}`}
                      className="btn-itgate-outline btn-itgate-sm"
                    >
                      View
                    </Link>
                    <button
                      onClick={() => onDelete(doc)}
                      className="btn-delete-sm"
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
  );
}