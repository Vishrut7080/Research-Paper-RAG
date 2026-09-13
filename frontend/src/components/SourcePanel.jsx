import { PaperIcon, WebIcon } from "./Icons.jsx";

function ReferencePill({ icon, tone, title, score, url }) {
  const tones = {
    paper: "bg-blue-50 border-blue-200 text-blue-900 hover:bg-blue-100",
    web: "bg-emerald-50 border-emerald-200 text-emerald-900 hover:bg-emerald-100",
  };
  const scoreTones = {
    paper: "text-blue-600",
    web: "text-emerald-600",
  };
  const inner = (
    <>
      {icon}
      <span className="shrink-0 font-semibold">
        {tone === "paper" ? "Paper" : "Web"}
      </span>
      <span className="flex-1 min-w-0 truncate">{title}</span>
      {score != null && (
        <span className={`shrink-0 whitespace-nowrap font-medium ${scoreTones[tone]}`}>
          • {score.toFixed(3)}
        </span>
      )}
    </>
  );
  const className = `inline-flex max-w-sm items-center gap-1.5 rounded-full border px-3 py-1 text-xs ${tones[tone]}`;
  if (url) {
    return (
      <a
        href={url}
        target="_blank"
        rel="noreferrer"
        title={title}
        className={className}
      >
        {inner}
      </a>
    );
  }
  return (
    <span title={title} className={className}>
      {inner}
    </span>
  );
}

function SourcePanel({ sources, webResults, webSearchUsed }) {
  if (!sources?.length && !webResults?.length) return null;

  return (
    <div className="mt-3 space-y-2">
      {webSearchUsed && (
        <p className="inline-block text-xs font-semibold text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-3 py-1">
          Web search was used
        </p>
      )}

      <div className="flex flex-wrap gap-1.5">
        {sources?.map((s, i) => (
          <ReferencePill
            key={`pdf-${i}`}
            icon={<PaperIcon />}
            tone="paper"
            title={s.doc_title}
            score={s.score}
            url={s.url}
          />
        ))}

        {webResults?.map((r, i) => (
          <ReferencePill
            key={`web-${i}`}
            icon={<WebIcon />}
            tone="web"
            title={r.title}
            url={r.url}
          />
        ))}
      </div>
    </div>
  );
}

export default SourcePanel;