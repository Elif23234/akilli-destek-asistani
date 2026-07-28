import { useEffect, useState } from "react";
import {
  useNavigate,
  useParams,
} from "react-router-dom";
import {
  getBenzerTalepler,
  getTalepDetayi,
} from "../services/api";

function TalepDetay() {
  const { takipNo } = useParams();
  const navigate = useNavigate();

  const [talep, setTalep] = useState(null);
  const [benzerTalepler, setBenzerTalepler] =
    useState([]);

  const [yukleniyor, setYukleniyor] =
    useState(true);

  const [
    benzerlerYukleniyor,
    setBenzerlerYukleniyor,
  ] = useState(false);

  const [hata, setHata] = useState("");

  const [
    benzerTalepHatasi,
    setBenzerTalepHatasi,
  ] = useState("");

  useEffect(() => {
    async function talepDetayiniYukle() {
      try {
        const temizTakipNo =
          decodeURIComponent(takipNo);

        const sonuc =
          await getTalepDetayi(temizTakipNo);

        console.log(
          "Detay verisi:",
          sonuc.veri
        );

        setTalep(sonuc.veri);

        const aramaMetni = [
          sonuc.veri?.talep_baslik,
          sonuc.veri?.talep_ham_icerik,
        ]
          .filter(Boolean)
          .join(" ");

        if (aramaMetni.trim()) {
          await benzerTalepleriYukle(
            aramaMetni,
            temizTakipNo
          );
        }
      } catch (error) {
        setHata(error.message);
      } finally {
        setYukleniyor(false);
      }
    }

    talepDetayiniYukle();
  }, [takipNo]);

  async function benzerTalepleriYukle(
    aramaMetni,
    mevcutTakipNo
  ) {
    try {
      setBenzerlerYukleniyor(true);
      setBenzerTalepHatasi("");

      const sonuc =
        await getBenzerTalepler(aramaMetni);

      console.log(
        "Benzer talepler cevabı:",
        sonuc
      );

      let gelenTalepler = [];

      if (Array.isArray(sonuc)) {
        gelenTalepler = sonuc;
      } else if (
        Array.isArray(sonuc.veri)
      ) {
        gelenTalepler = sonuc.veri;
      } else if (
        Array.isArray(sonuc.sonuclar)
      ) {
        gelenTalepler = sonuc.sonuclar;
      } else if (
        Array.isArray(
          sonuc.benzer_talepler
        )
      ) {
        gelenTalepler =
          sonuc.benzer_talepler;
      }

      const mevcutTalepHaric =
        gelenTalepler.filter(
          (benzerTalep) => {
            return (
              benzerTalep.talep_takip_no !==
              mevcutTakipNo
            );
          }
        );

      setBenzerTalepler(
        mevcutTalepHaric.slice(0, 4)
      );
    } catch (error) {
      console.error(
        "Benzer talepler hatası:",
        error
      );

      setBenzerTalepHatasi(
        error.message
      );
    } finally {
      setBenzerlerYukleniyor(false);
    }
  }

  function oncelikSinifi(oncelik) {
    const temizOncelik =
      oncelik?.toLowerCase();

    if (
      temizOncelik === "dusuk" ||
      temizOncelik === "düşük"
    ) {
      return "oncelik-etiketi oncelik-dusuk";
    }

    if (temizOncelik === "orta") {
      return "oncelik-etiketi oncelik-orta";
    }

    if (
      temizOncelik === "yuksek" ||
      temizOncelik === "yüksek"
    ) {
      return "oncelik-etiketi oncelik-yuksek";
    }

    return "oncelik-etiketi oncelik-belirsiz";
  }

  function oncelikMetni(oncelik) {
    const temizOncelik =
      oncelik?.toLowerCase();

    if (
      temizOncelik === "dusuk" ||
      temizOncelik === "düşük"
    ) {
      return "Düşük";
    }

    if (temizOncelik === "orta") {
      return "Orta";
    }

    if (
      temizOncelik === "yuksek" ||
      temizOncelik === "yüksek"
    ) {
      return "Yüksek";
    }

    return "Belirtilmemiş";
  }

  function durumMetni(durum) {
    const temizDurum =
      durum?.toLowerCase();

    if (
      temizDurum === "acik" ||
      temizDurum === "açık"
    ) {
      return "Açık";
    }

    if (
      temizDurum === "kapali" ||
      temizDurum === "kapalı"
    ) {
      return "Kapalı";
    }

    if (
      temizDurum === "beklemede"
    ) {
      return "Beklemede";
    }

    if (
      temizDurum === "onay_bekliyor"
    ) {
      return "Onay Bekliyor";
    }

    if (
      temizDurum ===
      "otomatik_yanitlandi"
    ) {
      return "Otomatik Yanıtlandı";
    }

    return (
      durum || "Belirtilmemiş"
    );
  }

  function benzerTalepDetayinaGit(
    benzerTakipNo
  ) {
    if (!benzerTakipNo) {
      return;
    }

    navigate(
      `/talep-detay/${encodeURIComponent(
        benzerTakipNo
      )}`
    );
  }

  if (yukleniyor) {
    return (
      <p>
        Talep detayı yükleniyor...
      </p>
    );
  }

  if (hata) {
    return <p>Hata: {hata}</p>;
  }

  if (!talep) {
    return <p>Talep bulunamadı.</p>;
  }

  const aiOzeti =
    talep.yz_ozet ||
    talep.ai_ozet ||
    talep.talep_ozet;

  const kategori =
    talep.kategori_ad ||
    talep.talep_kategori_ad ||
    talep.kategori;

  const oncelik =
    talep.yz_oncelik_seviyesi ||
    talep.oncelik;

  return (
    <section>
      <button
        type="button"
        onClick={() =>
          navigate("/talepler")
        }
      >
        ← Talep listesine dön
      </button>

      <h2>Talep Detayı</h2>

      <p>
        <strong>Takip No:</strong>{" "}
        {talep.talep_takip_no}
      </p>

      <p>
        <strong>Başlık:</strong>{" "}
        {talep.talep_baslik ||
          "Başlık bulunmuyor"}
      </p>

      <p>
        <strong>İçerik:</strong>{" "}
        {talep.talep_ham_icerik ||
          "Talep içeriği bulunmuyor"}
      </p>

      <p>
        <strong>Durum:</strong>{" "}
        {durumMetni(
          talep.talep_durum
        )}
      </p>

      <p>
        <strong>Gönderen:</strong>{" "}
        {talep.talep_gonderen_ad_soyad ||
          "Belirtilmemiş"}
      </p>

      <p>
        <strong>E-posta:</strong>{" "}
        {talep.talep_gonderen_eposta ||
          "Belirtilmemiş"}
      </p>

      <p>
        <strong>Kaynak:</strong>{" "}
        {talep.talep_kaynak ||
          "Belirtilmemiş"}
      </p>

      <hr />

      <h3>AI Analizi</h3>

      <p>
        <strong>AI Özeti:</strong>{" "}
        {aiOzeti ||
          "Bu talep için henüz AI özeti oluşturulmamış."}
      </p>

      <p>
        <strong>Kategori:</strong>{" "}
        {kategori ||
          "Belirtilmemiş"}
      </p>

      <p>
        <strong>Öncelik:</strong>{" "}
        <span
          className={oncelikSinifi(
            oncelik
          )}
        >
          {oncelikMetni(oncelik)}
        </span>
      </p>

      <hr />

      <h3>Benzer Talepler</h3>

      {benzerlerYukleniyor ? (
        <p>
          Benzer talepler aranıyor...
        </p>
      ) : benzerTalepHatasi ? (
        <p>
          Hata: {benzerTalepHatasi}
        </p>
      ) : benzerTalepler.length ===
        0 ? (
        <p>
          Bu taleple benzer bir kayıt
          bulunamadı.
        </p>
      ) : (
        <div>
          {benzerTalepler.map(
            (benzerTalep, index) => {
              const benzerTakipNo =
                benzerTalep.talep_takip_no ||
                benzerTalep.takip_no;

              const benzerBaslik =
                benzerTalep.talep_baslik ||
                benzerTalep.baslik ||
                "Başlık bulunmuyor";

              return (
                <div
                  key={
                    benzerTalep.talep_id ||
                    benzerTakipNo ||
                    index
                  }
                >
                  <button
                    type="button"
                    disabled={
                      !benzerTakipNo
                    }
                    onClick={() =>
                      benzerTalepDetayinaGit(
                        benzerTakipNo
                      )
                    }
                  >
                    {benzerTakipNo ||
                      "Takip numarası yok"}{" "}
                    - {benzerBaslik}
                  </button>
                </div>
              );
            }
          )}
        </div>
      )}
    </section>
  );
}

export default TalepDetay;