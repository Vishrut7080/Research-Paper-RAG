import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
});

export const uploadPdf = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const askQuestion = (queryText) =>
  api.post("/query", { query_text: queryText });

export const fetchHistory = () => api.get("/history");

export const fetchDocuments = () => api.get("/documents");

export const documentFileUrl = (docId) =>
  `${import.meta.env.VITE_API_URL || "/api"}/documents/${docId}/file`;

export default api;