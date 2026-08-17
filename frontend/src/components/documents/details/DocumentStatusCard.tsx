type DocumentStatusCardProps = {
  status: string | undefined;
  processingStep: string | null | undefined;
  progress: number | undefined;
  errorMessage: string | null | undefined;
};

export default function DocumentStatusCard({
  status,
  processingStep,
  progress,
  errorMessage,
}: DocumentStatusCardProps) {
  const progressValue = progress || 0;

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
      <div className="flex justify-between items-center">
        <h2 className="font-bold text-slate-800">Processing Status</h2>
        <span className="text-sm font-semibold text-indigo-600">{status}</span>
      </div>

      <div className="mt-5">
        <div className="flex justify-between text-xs text-slate-400 mb-2">
          <span>{processingStep}</span>
          <span>{progressValue}%</span>
        </div>

        <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
          <div
            style={{ width: `${progressValue}%` }}
            className="h-full bg-indigo-600 transition-all"
          />
        </div>
      </div>

      {errorMessage && (
        <div className="mt-5 p-4 rounded-xl bg-rose-50 text-rose-700 text-sm">
          {errorMessage}
        </div>
      )}
    </div>
  );
}
