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
export async function getDashboardIstatistikleri() {
  const response = await fetch(
    `${API_URL}/dashboard/istatistikler`
  );

  if (!response.ok) {
    throw new Error(
      "Dashboard istatistikleri alınamadı."
    );
  }

  return response.json();
}

export async function yeniTalepOlustur(talepBilgileri) {
  const response = await fetch(`${API_URL}/talepler`, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify(talepBilgileri),
  });

  const sonuc = await response.json();

  if (!response.ok) {
    throw new Error(
      sonuc.detail || "Talep oluşturulamadı."
    );
  }

  return sonuc;
}
export async function adminGirisi(kullaniciAdi, sifre) {
  const response = await fetch(`${API_URL}/admin/giris`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      kullanici_adi: kullaniciAdi,
      sifre: sifre,
    }),
  });

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail || "Yönetici girişi yapılamadı."
    );
  }

  return sonuc;
}