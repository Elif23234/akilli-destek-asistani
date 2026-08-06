const API_URL = "http://127.0.0.1:8000";


function getAuthHeaders() {
  const token = sessionStorage.getItem(
    "admin_token"
  );

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}


function getPersonelAuthHeaders() {
  const token = sessionStorage.getItem(
    "personel_token"
  );

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}


export async function getTalepler() {
  const response = await fetch(
    `${API_URL}/talepler/filtreli`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      "Talepler alınamadı."
    );
  }

  return response.json();
}


export async function getTalepDetayi(
  takipNo
) {
  const response = await fetch(
    `${API_URL}/talepler/${encodeURIComponent(
      takipNo
    )}`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      "Talep detayı alınamadı."
    );
  }

  return response.json();
}


export async function getBenzerTalepler(
  kelime
) {
  const response = await fetch(
    `${API_URL}/talepler/rag/arama?kelime=${encodeURIComponent(
      kelime
    )}`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      "Benzer talepler alınamadı."
    );
  }

  return response.json();
}


export async function getDashboardIstatistikleri() {
  const response = await fetch(
    `${API_URL}/dashboard/istatistikler`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      "Dashboard istatistikleri alınamadı."
    );
  }

  return response.json();
}


export async function yeniTalepOlustur(
  talepBilgileri
) {
  const response = await fetch(
    `${API_URL}/talepler`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(
        talepBilgileri
      ),
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "Talep oluşturulamadı."
    );
  }

  return sonuc;
}


export async function adminGirisi(
  kullaniciAdi,
  sifre
) {
  const response = await fetch(
    `${API_URL}/admin/giris`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        kullanici_adi:
          kullaniciAdi,
        sifre: sifre,
      }),
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "Yönetici girişi yapılamadı."
    );
  }

  return sonuc;
}


export async function personelOnaylaVeGonder({
  talepId,
  yanitMetni,
  islemTipi,
}) {
  const response = await fetch(
    `${API_URL}/personel/onayla-ve-gonder`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",

        ...getPersonelAuthHeaders(),
      },
      body: JSON.stringify({
        talep_id: talepId,
        yanit_metni: yanitMetni,
        islem_tipi:
          islemTipi ||
          "AI_YANITI_ONAYLANDI",
      }),
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "Yanıt onaylanamadı."
    );
  }

  return sonuc;
}


export async function talebiYapayZekaIleAnalizEt({
  talepId,
  baslik,
  icerik,
}) {
  const parametreler =
    new URLSearchParams({
      talep_id: talepId,
      baslik: baslik,
      icerik: icerik,
    });

  const response = await fetch(
    `${API_URL}/talepler/yapay-zeka-analiz?${parametreler.toString()}`,
    {
      method: "POST",
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "Yapay zekâ analizi sırasında bir hata oluştu."
    );
  }

  return sonuc;
}


export async function incelenenTalebiYanitla({
  talepId,
  yanitMetni,
}) {
  const response = await fetch(
    `${API_URL}/personel/incelenen-yanitla`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",

        ...getPersonelAuthHeaders(),
      },
      body: JSON.stringify({
        talep_id: talepId,
        yanit_metni: yanitMetni,
        islem_tipi:
          "MANUEL_INCELEME_YANITI",
      }),
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "İncelenen talebe yanıt gönderilemedi."
    );
  }

  return sonuc;
}


export async function getGecikenTalepler() {
  const response = await fetch(
    `${API_URL}/dashboard/geciken-talepler`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "Geciken talepler alınamadı."
    );
  }

  return sonuc;
}


export async function musteriCozumOnayiGonder({
  talepId,
  cozulduMu,
}) {
  const response = await fetch(
    `${API_URL}/talepler/musteri-onayi`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        talep_id: talepId,
        cozuldu_mu: cozulduMu,
      }),
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "Müşteri onayı gönderilemedi."
    );
  }

  return sonuc;
}


export async function personelGirisi(
  eposta,
  sifre
) {
  const response = await fetch(
    `${API_URL}/personel/giris`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify({
        eposta: eposta,
        sifre: sifre,
      }),
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "Personel girişi yapılamadı."
    );
  }

  return sonuc;
}


export async function getPersonelTaleplerim() {
  const response = await fetch(
    `${API_URL}/personel/taleplerim`,
    {
      headers: {
        ...getPersonelAuthHeaders(),
      },
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "Personele atanmış talepler alınamadı."
    );
  }

  return sonuc;
}


export async function getPersonelTalepDetayi(
  talepId
) {
  const response = await fetch(
    `${API_URL}/personel/talep/${encodeURIComponent(
      talepId
    )}`,
    {
      headers: {
        ...getPersonelAuthHeaders(),
      },
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "Talep detayı alınamadı."
    );
  }

  return sonuc;
}
export async function getAdminPersonelleri() {
  const response = await fetch(
    `${API_URL}/admin/personeller`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "Personel listesi alınamadı."
    );
  }

  return sonuc;
}


export async function adminTalebiDevret({
  talepId,
  yeniPersonelId,
}) {
  const response = await fetch(
    `${API_URL}/admin/talep-devret`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        talep_id: talepId,
        yeni_personel_id:
          yeniPersonelId,
      }),
    }
  );

  let sonuc = {};

  try {
    sonuc = await response.json();
  } catch {
    sonuc = {};
  }

  if (!response.ok) {
    throw new Error(
      sonuc.detail ||
        "Talep devredilemedi."
    );
  }

  return sonuc;
}