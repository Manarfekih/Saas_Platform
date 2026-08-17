type DocumentsStatusBadgeProps = {
  status: string;
};

export default function DocumentsStatusBadge({ status }: DocumentsStatusBadgeProps) {
  switch (status) {
    case "processed":
      return (
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700">
          Ready
        </span>
      );
    case "failed":
      return (
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700">
          Failed
        </span>
      );
    default:
      return (
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 animate-pulse">
          Processing
        </span>
      );
  }
}
