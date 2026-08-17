// src/pages/StructuredAnswerView.tsx

import type {
  StructuredAnswer,
  ListAnswer,
  CountAnswer,
  OverviewAnswer,
  FactAnswer,
} from "./chatTypes";

function FactAnswerView({ answer }: { answer: FactAnswer }) {
  return <p className="text-[15px] leading-relaxed">{answer.text}</p>;
}

function CountAnswerView({ answer }: { answer: CountAnswer }) {
  return (
    <div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold text-indigo-600 leading-none">
          {answer.number}
        </span>
        <span className="text-[15px] font-medium text-slate-700">
          {answer.label}
        </span>
      </div>

      {answer.items && answer.items.length > 0 && (
        <ul className="mt-3 space-y-1.5">
          {answer.items.map((item, i) => (
            <li
              key={i}
              className="flex items-start gap-2 text-[14px] text-slate-600"
            >
              <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-indigo-300 shrink-0" />
              <span>
                <span className="font-medium text-slate-800">{item.title}</span>
                {item.subtitle && (
                  <span className="text-slate-500"> — {item.subtitle}</span>
                )}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function ListAnswerView({ answer }: { answer: ListAnswer }) {
  return (
    <div>
      {answer.intro && (
        <p className="text-[14px] text-slate-600 mb-3">{answer.intro}</p>
      )}

      <div className="space-y-2.5">
        {answer.items.map((item, i) => (
          <div
            key={i}
            className="rounded-xl border border-slate-200 bg-white px-4 py-3"
          >
            <div className="flex items-baseline gap-2">
              <span className="text-[12px] font-semibold text-indigo-400 tabular-nums">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className="text-[15px] font-semibold text-slate-900">
                {item.title}
              </span>
            </div>

            {item.subtitle && (
              <p className="mt-1 text-[14px] text-slate-600 pl-7">
                {item.subtitle}
              </p>
            )}

            {item.tags && item.tags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5 pl-7">
                {item.tags.map((tag, ti) => (
                  <span
                    key={ti}
                    className="text-[11px] font-medium text-indigo-700 bg-indigo-50 rounded-md px-2 py-0.5"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {item.details && (
              <p className="mt-2 text-[13px] text-slate-500 pl-7 leading-relaxed">
                {item.details}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function OverviewAnswerView({ answer }: { answer: OverviewAnswer }) {
  return (
    <div>
      <p className="text-[15px] leading-relaxed text-slate-800">
        {answer.summary}
      </p>

      {answer.sections && answer.sections.length > 0 && (
        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
          {answer.sections.map((section, i) => (
            <div
              key={i}
              className="rounded-lg bg-slate-50 border border-slate-200 px-3 py-2"
            >
              <p className="text-[11px] font-semibold uppercase tracking-wide text-indigo-500">
                {section.label}
              </p>
              <p className="mt-0.5 text-[13.5px] text-slate-700 leading-snug">
                {section.text}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function StructuredAnswerView({
  answer,
}: {
  answer: StructuredAnswer;
}) {
  switch (answer.type) {
    case "fact":
      return <FactAnswerView answer={answer} />;
    case "count":
      return <CountAnswerView answer={answer} />;
    case "list":
      return <ListAnswerView answer={answer} />;
    case "overview":
      return <OverviewAnswerView answer={answer} />;
    default:
      return (
        <p className="text-[15px] leading-relaxed">
          {JSON.stringify(answer)}
        </p>
      );
  }
}