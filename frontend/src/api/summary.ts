import api from "./auth";

export async function getSummary(documentId: number) {
  const res = await api.get(`/documents/${documentId}/summary`);
  return res.data;
}

export async function regenerateSummary(documentId: number) {
  const res = await api.post(`/documents/${documentId}/regenerate-summary`);
  return res.data;
}

export async function downloadSummary(documentId: number) {
  return api.get(`/documents/${documentId}/summary/download`, {
    responseType: "blob"
  });
}

export async function previewSummaryFile(documentId: number) {
  const res = await api.get(`/documents/${documentId}/summary/download`, {
    responseType: "text",
  });

  return res.data as string;
}
