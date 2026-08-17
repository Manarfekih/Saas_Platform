import { Link } from "react-router-dom";

type UploadHeaderProps = {
  title: string;
  description: string;
  backTo: string;
  backLabel: string;
};

export default function UploadHeader({
  title,
  description,
  backTo,
  backLabel,
}: UploadHeaderProps) {
  return (
    <div>
      <Link to={backTo} className="text-sm text-indigo-600">
        {backLabel}
      </Link>

      <h1 className="text-3xl font-bold text-slate-900 mt-4">{title}</h1>
      <p className="text-slate-500 mt-2">{description}</p>
    </div>
  );
}
