import { useEffect, useState } from "react";
import ChatInterface from "./components/ChatInterface.jsx";
import DocumentUpload from "./components/DocumentUpload.jsx";
import DocumentsList from "./components/DocumentsList.jsx";
import History from "./components/History.jsx";

function App() {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL || "/api"}/health`)
      .then((r) => r.json())
      .then((d) => setStatus(`Backend OK — ${d.chunks} chunks indexed`))
      .catch(() => setStatus("Backend not reachable"));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      <div className="flex flex-col md:flex-row h-screen">
        <aside className="md:w-80 bg-white border-r border-gray-200 p-5 flex flex-col gap-5 overflow-y-auto">
          <header>
            <h1 className="text-2xl font-bold text-primary-700">ResearchMate</h1>
            <p className="text-sm text-gray-500 mt-1">{status}</p>
          </header>
          <DocumentUpload />
          <DocumentsList />
          <History />
        </aside>

        <main className="flex-1 flex flex-col min-h-0">
          <ChatInterface />
        </main>
      </div>
    </div>
  );
}

export default App;