const API_URL = "http://127.0.0.1:8000";

export async function getTalepler() {
  const response = await fetch(
    `${API_URL}/talepler/filtreli`
  );

  if (!response.ok) {
    throw new Error("Talepler alınamadı.");
  }

  return response.json();
}

export async function getTalepDetayi(takipNo) {
  const response = await fetch(
    `${API_URL}/talepler/${encodeURIComponent(takipNo)}`
  );

  if (!response.ok) {
    throw new Error("Talep detayı alınamadı.");
  }

  return response.json();
}

export async function getBenzerTalepler(kelime) {
  const response = await fetch(
    `${API_URL}/talepler/rag/arama?kelime=${encodeURIComponent(
      kelime
    )}`
  );

  if (!response.ok) {
    throw new Error("Benzer talepler alınamadı.");
  }

  return response.json();
}