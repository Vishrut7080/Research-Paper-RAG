import { useEffect, useRef, useState } from "react";
import { askQuestion, fetchHistory } from "../api.js";
import SourcePanel from "./SourcePanel.jsx";

function ChatInterface({ onHistoryChange }) {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    fetchHistory()
      .then(({ data }) => {
        const items = data.flatMap((c) => [
          { role: "user", content: c.query },
          {
            role: "assistant",
            content: c.answer,
            sources: c.sources,
            webResults: c.web_results,
            webSearchUsed: c.web_search_used,
          },
        ]);
        setMessages(items);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;
    const q = query.trim();
    setMessages((m) => [...m, { role: "user", content: q }]);
    setQuery("");
    setLoading(true);
    try {
      const { data } = await askQuestion(q);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          webResults: data.web_results,
          webSearchUsed: data.web_search_used,
        },
      ]);
      onHistoryChange?.();
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Error — could not reach the backend." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full p-4 gap-3">
      <div className="flex-1 bg-white rounded-xl shadow p-4 overflow-y-auto space-y-4 min-h-0">
        {messages.length === 0 && !loading && (
          <p className="text-gray-400 text-sm">
            Ask a question about your research papers…
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-3xl ${
              msg.role === "user" ? "ml-auto" : ""
            }`}
          >
            <div
              className={`rounded-xl px-4 py-3 whitespace-pre-wrap text-sm ${
                msg.role === "user"
                  ? "bg-primary-600 text-white"
                  : "bg-gray-50 border border-gray-200 text-gray-800"
              }`}
            >
              {msg.content}
            </div>
            {msg.role === "assistant" && (
              <SourcePanel
                sources={msg.sources}
                webResults={msg.webResults}
                webSearchUsed={msg.webSearchUsed}
              />
            )}
          </div>
        ))}
        {loading && (
          <div className="bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-500 w-fit">
            Loading…
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your papers…"
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        <button
          type="submit"
          disabled={!query.trim() || loading}
          className="bg-primary-600 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatInterface;