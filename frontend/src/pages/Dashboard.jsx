import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getTalepler } from "../services/api";
import "../styles/Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const [talepler, setTalepler] = useState([]);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [hata, setHata] = useState("");

  useEffect(() => {
    async function talepleriGetir() {
      try {
        const sonuc = await getTalepler();

        if (Array.isArray(sonuc.veri)) {
          setTalepler(sonuc.veri);
        } else {
          setTalepler([]);
        }
      } catch (error) {
        setHata(error.message);
      } finally {
        setYukleniyor(false);
      }
    }

    talepleriGetir();
  }, []);

  function metniKucult(deger) {
    return String(deger || "")
      .trim()
      .toLocaleLowerCase("tr-TR");
  }

  const acikTalepSayisi = talepler.filter((talep) => {
    const durum = metniKucult(talep.talep_durum);

    return durum === "acik" || durum === "açık";
  }).length;

  const onayBekleyenSayisi = talepler.filter((talep) => {
    const durum = metniKucult(talep.talep_durum);

    return durum === "onay_bekliyor";
  }).length;

  const otomatikYanitlananSayisi = talepler.filter((talep) => {
    const durum = metniKucult(talep.talep_durum);

    return durum === "otomatik_yanitlandi";
  }).length;

  const acilTalepSayisi = talepler.filter((talep) => {
    const oncelik = metniKucult(
      talep.yz_oncelik_seviyesi
    );

    return oncelik === "acil";
  }).length;

  const aiAnalizEdilenTalepSayisi = talepler.filter(
    (talep) =>
      talep.yz_ozet ||
      talep.yz_oncelik_seviyesi ||
      talep.yz_guven_skoru != null
  ).length;

  const simdi = new Date();

  const yirmiDortSaatOnce = new Date(
    simdi.getTime() - 24 * 60 * 60 * 1000
  );

  const sonYirmiDortSaatTalepSayisi = talepler.filter(
    (talep) => {
      if (!talep.talep_olusturulma_tarihi) {
        return false;
      }

      const olusturulmaTarihi = new Date(
        talep.talep_olusturulma_tarihi
      );

      return (
        !Number.isNaN(olusturulmaTarihi.getTime()) &&
        olusturulmaTarihi >= yirmiDortSaatOnce
      );
    }
  ).length;

  const kategoriSayilari = {};

  talepler.forEach((talep) => {
    const kategoriAdi =
      talep.kategori_ad?.trim() || "Kategorisiz";

    if (kategoriSayilari[kategoriAdi]) {
      kategoriSayilari[kategoriAdi] =
        kategoriSayilari[kategoriAdi] + 1;
    } else {
      kategoriSayilari[kategoriAdi] = 1;
    }
  });

  const kategoriDagilimi = Object.entries(
    kategoriSayilari
  ).sort((birinciKategori, ikinciKategori) => {
    return ikinciKategori[1] - birinciKategori[1];
  });

  if (yukleniyor) {
    return <p>Talepler yükleniyor...</p>;
  }

  if (hata) {
    return <p>Hata: {hata}</p>;
  }

  return (
    <section className="dashboard-sayfasi">
      <div className="dashboard-baslik">
        <p>Genel Bakış</p>

        <h1>Dashboard</h1>

        <span>
          Destek taleplerinin güncel durumunu buradan
          takip edebilirsiniz.
        </span>
      </div>

      <div className="dashboard-kartlari">
        <div
          className="dashboard-karti"
          onClick={() => navigate("/talepler")}
        >
          <div className="kart-ikon toplam-ikon">📋</div>

          <div>
            <p>Toplam Talep</p>
            <h2>{talepler.length}</h2>
          </div>
        </div>

        <div
          className="dashboard-karti"
          onClick={() =>
            navigate("/talepler?durum=acik")
          }
        >
          <div className="kart-ikon acik-ikon">📨</div>

          <div>
            <p>Açık Talepler</p>
            <h2>{acikTalepSayisi}</h2>
          </div>
        </div>

        <div
          className="dashboard-karti"
          onClick={() =>
            navigate("/talepler?durum=onay_bekliyor")
          }
        >
          <div className="kart-ikon bekleyen-ikon">
            ⏳
          </div>

          <div>
            <p>Onay Bekleyen</p>
            <h2>{onayBekleyenSayisi}</h2>
          </div>
        </div>

        <div
          className="dashboard-karti"
          onClick={() =>
            navigate(
              "/talepler?durum=otomatik_yanitlandi"
            )
          }
        >
          <div className="kart-ikon yanitlanan-ikon">
            🤖
          </div>

          <div>
            <p>Otomatik Yanıtlanan</p>
            <h2>{otomatikYanitlananSayisi}</h2>
          </div>
        </div>

        <div
          className="dashboard-karti"
          onClick={() =>
            navigate("/talepler?oncelik=acil")
          }
        >
          <div className="kart-ikon bekleyen-ikon">
            🚨
          </div>

          <div>
            <p>Acil Talepler</p>
            <h2>{acilTalepSayisi}</h2>
          </div>
        </div>

        <div
          className="dashboard-karti"
          onClick={() =>
            navigate("/talepler?zaman=son24saat")
          }
        >
          <div className="kart-ikon toplam-ikon">
            🕐
          </div>

          <div>
            <p>Son 24 Saat</p>
            <h2>{sonYirmiDortSaatTalepSayisi}</h2>
          </div>
        </div>

        <div
          className="dashboard-karti"
          onClick={() =>
            navigate("/talepler?ai_analiz=true")
          }
        >
          <div className="kart-ikon acik-ikon">
            🧠
          </div>

          <div>
            <p>AI Analiz Edilen</p>
            <h2>{aiAnalizEdilenTalepSayisi}</h2>
          </div>
        </div>
      </div>

      <div className="dashboard-bilgi-karti">
        <h3>Talep Durumu Özeti</h3>

        <div className="durum-satiri">
          <span>Açık talepler</span>
          <strong>{acikTalepSayisi}</strong>
        </div>

        <div className="durum-satiri">
          <span>Onay bekleyen talepler</span>
          <strong>{onayBekleyenSayisi}</strong>
        </div>

        <div className="durum-satiri">
          <span>Otomatik yanıtlanan talepler</span>
          <strong>{otomatikYanitlananSayisi}</strong>
        </div>

        <div className="durum-satiri">
          <span>Acil talepler</span>
          <strong>{acilTalepSayisi}</strong>
        </div>

        <div className="durum-satiri">
          <span>AI analiz edilen talepler</span>
          <strong>{aiAnalizEdilenTalepSayisi}</strong>
        </div>
      </div>

      <div className="dashboard-bilgi-karti">
        <h3>Kategori Dağılımı</h3>

        {kategoriDagilimi.length === 0 ? (
          <p>Henüz kategori bilgisi bulunmuyor.</p>
        ) : (
          kategoriDagilimi.map(
            ([kategoriAdi, talepSayisi]) => (
              <div
                className="durum-satiri"
                key={kategoriAdi}
              >
                <span>{kategoriAdi}</span>
                <strong>{talepSayisi}</strong>
              </div>
            )
          )
        )}
      </div>
    </section>
  );
}

export default Dashboard;