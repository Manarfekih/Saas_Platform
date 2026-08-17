type DocumentsSearchInputProps = {
  value: string;
  onChange: (value: string) => void;
};

export default function DocumentsSearchInput({
  value,
  onChange,
}: DocumentsSearchInputProps) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Search documents..."
      className="w-full md:w-96 px-4 py-3 rounded-xl border border-slate-200 outline-none focus:ring-2 focus:ring-indigo-500"
    />
  );
}
