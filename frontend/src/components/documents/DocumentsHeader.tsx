type DocumentsHeaderProps = {
  title: string;
  description: string;
};

export default function DocumentsHeader({ title, description }: DocumentsHeaderProps) {
  return (
    <div>
      <h1 className="text-3xl font-bold text-slate-900">{title}</h1>
      <p className="mt-2 text-slate-500">{description}</p>
    </div>
  );
}
