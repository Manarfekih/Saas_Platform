import api from "../../api/auth";
import type { Source } from "../../pages/chatTypes";

type CitationSourcesProps = {
  sources: Source[];
  documentId?: number;
  maxSources?: number;
};

function cleanContent(raw: string): string {
  return raw
    .replace(/---\s*PAGES?\s*\d+[-–]\d+\s*---/gi, "")
    .replace(/\[\[PAGE\s*\d+\]\]/gi, "")
    .replace(/^#{1,6}\s*/gm, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .join(" ");
}

function buildSnippet(content?: string): string {
  if (!content) return "No excerpt available";

  const cleaned = cleanContent(content).replace(/\s+/g, " ").trim();
  if (!cleaned) return "No excerpt available";

  return cleaned.length > 140 ? `${cleaned.slice(0, 140).trimEnd()}...` : cleaned;
}

function getDisplayName(source: Source): string {
  if (source.filename) return source.filename.replace(/\.[^.]+$/, "");
  return "Document";
}

function buildFileUrl(documentId: number, pageNumber?: number | null): string {
  const baseUrl = api.defaults.baseURL || "http://localhost:8000";
  const token = window.localStorage.getItem("token") || "";
  const fileUrl = `${baseUrl}/documents/${documentId}/file?token=${encodeURIComponent(token)}`;

  if (pageNumber) {
    return `${fileUrl}#page=${pageNumber}`;
  }

  return fileUrl;
}

export default function CitationSources({
  sources,
  documentId,
  maxSources = 3,
}: CitationSourcesProps) {
  if (!sources || sources.length === 0) return null;

  const ranked = [...sources]
    .sort((a, b) => (a.distance ?? Number.POSITIVE_INFINITY) - (b.distance ?? Number.POSITIVE_INFINITY))
    .filter((source, index, allSources) =>
      allSources.findIndex((candidate) => candidate.chunk_id === source.chunk_id) === index,
    )
    .slice(0, maxSources);

  return (
    <div className="mt-3 rounded-xl border border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-100 px-3 py-2">
        <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
          Best Sources ({ranked.length})
        </p>
        <p className="text-[10px] text-slate-400">Top ranked matches from the uploaded file</p>
      </div>

      <ul className="divide-y divide-slate-100">
        {ranked.map((source, index) => {
          const targetDocumentId = source.document_id ?? documentId;

          return (
            <li key={source.chunk_id ?? index} className="px-3 py-3">
              <div className="flex items-start gap-3">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-50 text-[11px] font-semibold text-indigo-600">
                  {index + 1}
                </span>

                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-medium text-slate-800">
                      {getDisplayName(source)}
                    </span>

                    {source.page_number ? (
                      <span className="rounded-md border border-indigo-100 bg-indigo-50 px-1.5 py-0.5 text-[10px] font-medium text-indigo-600">
                        Page {source.page_number}
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate-400">Page unavailable</span>
                    )}

                    <span className="rounded-md border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[10px] font-medium text-slate-500">
                      Rank #{index + 1}
                    </span>
                  </div>

                  <p className="mt-1 text-[12px] leading-relaxed text-slate-500">
                    {buildSnippet(source.content)}
                  </p>

                  {targetDocumentId ? (
                    <a
                      href={buildFileUrl(targetDocumentId, source.page_number)}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-2 inline-flex items-center gap-1 rounded-md border border-indigo-100 bg-indigo-50 px-2 py-1 text-[11px] font-medium text-indigo-700 hover:bg-indigo-100"
                    >
                      View uploaded doc
                    </a>
                  ) : null}
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
