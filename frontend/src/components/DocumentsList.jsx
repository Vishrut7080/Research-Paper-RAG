import { useEffect, useState } from "react";
import { documentFileUrl, fetchDocuments } from "../api.js";

function DocumentsList() {
  const [docs, setDocs] = useState([]);

  const load = () => {
    fetchDocuments()
      .then(({ data }) => setDocs(data))
      .catch(() => {});
  };

  useEffect(load, []);

  return (
    <section className="bg-white rounded-xl shadow p-4 flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <h2 className="font-semibold text-gray-800">Your documents</h2>
        <button
          onClick={load}
          className="ml-auto text-xs text-primary-600 hover:underline"
        >
          Refresh
        </button>
      </div>
      <ul className="space-y-2 overflow-y-auto max-h-64">
        {docs.length === 0 && (
          <li className="text-xs text-gray-400">No documents index yet.</li>
        )}
        {docs.map((d) => (
          <li key={d.id} className="text-sm bg-gray-50 border rounded p-2">
            <div className="flex items-center gap-2">
              <p className="font-medium text-gray-800 truncate flex-1">
                {d.filename}
              </p>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                  d.source === "upload"
                    ? "bg-primary-100 text-primary-700"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                {d.source}
              </span>
            </div>
            <div className="flex items-center justify-between mt-1">
              <p className="text-xs text-gray-500">
                {d.num_chunks} chunks
                {d.uploaded_at
                  ? ` • ${new Date(d.uploaded_at).toLocaleDateString()}`
                  : ""}
              </p>
              {d.local_path && (
                <a
                  href={documentFileUrl(d.id)}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-primary-600 hover:underline"
                >
                  Download
                </a>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default DocumentsList;