import { useState } from "react";
import { uploadPdf } from "../api.js";

function DocumentUpload({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setMessage(null);
    try {
      const { data } = await uploadPdf(file);
      setMessage(
        data.status === "success"
          ? `Uploaded ${data.chunks} chunks from ${data.filename}`
          : data.message
      );
      if (data.status === "success") onUploaded?.();
    } catch (err) {
      setMessage("Upload failed — is the backend running?");
    } finally {
      setLoading(false);
      setFile(null);
    }
  };

  return (
    <section className="bg-white rounded-xl shadow p-4">
      <h2 className="font-semibold text-gray-800 mb-3">Upload a PDF</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
          className="text-sm text-gray-600 file:mr-3 file:rounded-lg file:border-0 file:bg-primary-600 file:text-white file:px-3 file:py-1.5"
        />
        <button
          type="submit"
          disabled={!file || loading}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-40"
        >
          {loading ? "Uploading..." : "Upload"}
        </button>
        {message && <p className="text-sm text-gray-700">{message}</p>}
      </form>
    </section>
  );
}

export default DocumentUpload;