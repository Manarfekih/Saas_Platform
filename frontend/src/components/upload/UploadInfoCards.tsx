const CARDS = [
  {
    title: "Extraction",
    description: "AI extracts document content.",
  },
  {
    title: "Classification",
    description: "Detects document type.",
  },
  {
    title: "AI Chat",
    description: "Ask questions later.",
  },
];

export default function UploadInfoCards() {
  return (
    <div className="grid md:grid-cols-3 gap-5">
      {CARDS.map((card) => (
        <div key={card.title} className="bg-slate-50 rounded-xl p-5">
          <p className="font-semibold text-slate-800">{card.title}</p>
          <p className="text-sm text-slate-500 mt-2">{card.description}</p>
        </div>
      ))}
    </div>
  );
}
