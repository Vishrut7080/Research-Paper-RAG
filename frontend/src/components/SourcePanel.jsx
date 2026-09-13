function SourcePanel({ sources, webResults, webSearchUsed }) {
  if (!sources?.length && !webResults?.length) return null;

  return (
    <div className="mt-3 space-y-2">
      {webSearchUsed && (
        <p className="text-xs font-semibold text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1">
          Web search was used — the corpus alone may not cover this question.
        </p>
      )}

      {sources?.map((s, i) => (
        <div
          key={`pdf-${i}`}
          className="text-xs bg-gray-50 border-l-4 border-primary-500 rounded p-2"
        >
          <span className="font-semibold text-gray-800">[Paper]</span>{" "}
          <span className="text-gray-700">{s.doc_title}</span>
          <span className="text-gray-500"> — score {s.score.toFixed(3)}</span>
          <p className="text-gray-600 mt-1">{s.text}…</p>
        </div>
      ))}

      {webResults?.map((r, i) => (
        <div
          key={`web-${i}`}
          className="text-xs bg-emerald-50 border-l-4 border-emerald-500 rounded p-2"
        >
          <span className="font-semibold text-emerald-800">[Web]</span>{" "}
          <a
            href={r.url}
            target="_blank"
            rel="noreferrer"
            className="text-primary-700 hover:underline"
          >
            {r.title}
          </a>
          <p className="text-gray-600 mt-1">{r.content?.slice(0, 150)}…</p>
        </div>
      ))}
    </div>
  );
}

export default SourcePanel;