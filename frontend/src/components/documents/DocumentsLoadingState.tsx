export default function DocumentsLoadingState() {
  return (
    <div className="p-8 space-y-4">
      {[1, 2, 3].map((item) => (
        <div key={item} className="h-16 rounded-xl bg-slate-100 animate-pulse" />
      ))}
    </div>
  );
}
