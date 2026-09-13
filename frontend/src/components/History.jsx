import { useEffect, useState } from "react";
import { fetchHistory } from "../api.js";

function History({ refreshKey = 0 }) {
  const [history, setHistory] = useState([]);
  const [search, setSearch] = useState("");

  const load = () => {
    fetchHistory()
      .then(({ data }) => setHistory(data))
      .catch(() => {});
  };

  useEffect(load, [refreshKey]);

  const filtered = history.filter((h) =>
    h.query.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <section className="bg-white rounded-xl shadow p-4 flex flex-col gap-3 min-h-0 flex-1">
      <div className="flex items-center gap-2">
        <h2 className="font-semibold text-gray-800">History</h2>
        <button
          onClick={load}
          className="ml-auto text-xs text-primary-600 hover:underline"
        >
          Refresh
        </button>
      </div>
      <input
        type="text"
        placeholder="Search past queries…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
      />
      <ul className="space-y-2 overflow-y-auto flex-1 min-h-0">
        {filtered.length === 0 && (
          <li className="text-xs text-gray-400">No history yet.</li>
        )}
        {filtered.map((h) => (
          <li
            key={h.id}
            onClick={() =>
              document
                .getElementById(h.id)
                ?.scrollIntoView({ behavior: "smooth", block: "center" })
            }
            className="text-sm bg-gray-50 border rounded p-2 cursor-pointer hover:bg-gray-100"
          >
            <p className="font-medium text-gray-800 truncate">{h.query}</p>
            <p className="text-xs text-gray-500">
              {h.timestamp ? new Date(h.timestamp).toLocaleString() : ""}
              {h.web_search_used ? " • web" : ""}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default History;