import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getDashboardIstatistikleri,
  getGecikenTalepler,
} from "../services/api";

import "../styles/Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const [dashboardVerisi, setDashboardVerisi] =
    useState(null);

  const [yukleniyor, setYukleniyor] =
    useState(true);

  const [hata, setHata] = useState("");

  const [gecikenTalepler, setGecikenTalepler] =
    useState([]);

  useEffect(() => {
    async function dashboardVerileriniGetir() {
      try {
        const [dashboardSonucu, gecikenSonucu] =
          await Promise.all([
            getDashboardIstatistikleri(),
            getGecikenTalepler(),
          ]);

        if (dashboardSonucu.veri) {
          setDashboardVerisi(
            dashboardSonucu.veri
          );
        } else {
          setDashboardVerisi(null);
        }

        setGecikenTalepler(
          Array.isArray(gecikenSonucu.veri)
            ? gecikenSonucu.veri
            : []
        );
      } catch (error) {
        setHata(error.message);
      } finally {
        setYukleniyor(false);
      }
    }

    dashboardVerileriniGetir();
  }, []);

  const toplamTalepSayisi =
    dashboardVerisi?.toplam_talep_sayisi || 0;

  const acikTalepSayisi =
    dashboardVerisi?.acik_talep_sayisi || 0;

  const onayBekleyenSayisi =
    dashboardVerisi
      ?.onay_bekleyen_talep_sayisi || 0;

  const incelenenTalepSayisi =
    dashboardVerisi?.incelenen_talep_sayisi || 0;

  const otomatikYanitlananSayisi =
    dashboardVerisi
      ?.otomatik_yanitlanan_talep_sayisi || 0;

  const musteriYanitiBekleyenSayisi =
    dashboardVerisi
      ?.musteri_yaniti_bekleyen_talep_sayisi ||
    0;

  const cozulenTalepSayisi =
    dashboardVerisi?.cozulen_talep_sayisi || 0;

  const aiAnalizEdilenTalepSayisi =
    dashboardVerisi
      ?.ai_analiz_edilen_talep_sayisi || 0;

  const sonYirmiDortSaatTalepSayisi =
    dashboardVerisi
      ?.son_24_saat_talep_sayisi || 0;

  const kritikTalepSayisi =
    dashboardVerisi?.kritik_talep_sayisi ||
    0;

  const ortalamaYanitBeklemeSuresi =
    dashboardVerisi
      ?.ortalama_yanit_bekleme_suresi ||
    "Henüz yanıt verisi yok";

  const kategoriDagilimi =
    dashboardVerisi?.kategori_dagilimi ||
    [];
  
  const personelDagilimi =
    dashboardVerisi?.personel_dagilimi ||
    [];

  const aktifPersonelDagilimi =
    personelDagilimi.filter((personel) => {
      const talepSayisi =
        Number(personel.talep_sayisi) || 0;

      const personelAdi =
        personel.personel_adi
          ?.toLocaleLowerCase("tr-TR")
          .trim();

      return (
        talepSayisi > 0 &&
        personelAdi !== "sistem personeli"
      );
    });

  const enYuksekPersonelTalepSayisi =
    Math.max(
      ...aktifPersonelDagilimi.map(
        (personel) =>
          Number(personel.talep_sayisi) || 0
      ),
      1
    );

  if (yukleniyor) {
    return (
      <section className="dashboard-durum-ekrani">
        <div className="dashboard-yukleniyor-ikonu">
          ✨
        </div>

        <h2>Dashboard hazırlanıyor</h2>

        <p>
          Güncel destek talepleri getiriliyor...
        </p>

        <div className="dashboard-yukleme-cubugu">
          <span></span>
        </div>
      </section>
    );
  }

  if (hata) {
    return (
      <section className="dashboard-durum-ekrani">
        <div className="dashboard-hata-ikonu">
          ⚠️
        </div>

        <h2>Bir sorun oluştu</h2>
        <p>{hata}</p>
      </section>
    );
  }

  return (
    <section className="dashboard-sayfasi">
      {/* Arka plandaki dekoratif şekiller */}
      <div className="dashboard-dekor dashboard-dekor-bir"></div>
      <div className="dashboard-dekor dashboard-dekor-iki"></div>
      <div className="dashboard-dekor dashboard-dekor-uc"></div>

      <header className="dashboard-baslik">
        <div className="dashboard-baslik-ikonu">
          ✨
        </div>

        <div>
          <span className="dashboard-rozet">
            Akıllı destek merkezi
          </span>

          <h1>
            Yönetim
            <span> Paneli</span>
          </h1>

          <p>
            Destek taleplerinin güncel durumunu,
            yapay zekâ analizlerini ve önemli
            istatistikleri buradan takip
            edebilirsiniz.
          </p>
        </div>
      </header>

      <div className="dashboard-kartlari">
        <article
          className="dashboard-karti kart-toplam"
          onClick={() => navigate("/talepler")}
        >
          <div className="kart-parilti"></div>

          <div className="kart-ikon toplam-ikon">
            📋
          </div>

          <div className="kart-icerik">
            <span>Toplam Talep</span>
            <strong>{toplamTalepSayisi}</strong>
            <small>Tüm destek talepleri</small>
          </div>

          <div className="kart-ok">→</div>
        </article>

        <article
          className="dashboard-karti kart-acik"
          onClick={() =>
            navigate("/talepler?durum=acik")
          }
        >
          <div className="kart-parilti"></div>

          <div className="kart-ikon acik-ikon">
            📨
          </div>

          <div className="kart-icerik">
            <span>Açık Talepler</span>
            <strong>{acikTalepSayisi}</strong>
            <small>İşlem bekleyen talepler</small>
          </div>

          <div className="kart-ok">→</div>
        </article>

        <article
          className="dashboard-karti kart-incelenen"
          onClick={() =>
            navigate("/talepler?durum=inceleniyor")
          }
        >
          <div className="kart-parilti"></div>

          <div className="kart-ikon incelenen-ikon">
            🔎
          </div>

          <div className="kart-icerik">
            <span>İncelenen Talepler</span>
            <strong>{incelenenTalepSayisi}</strong>
            <small>Personel incelemesi gerekiyor</small>
          </div>

          <div className="kart-ok">→</div>
        </article>

        <article
          className="dashboard-karti kart-bekleyen"
          onClick={() =>
            navigate(
              "/talepler?durum=onay_bekliyor"
            )
          }
        >
          <div className="kart-parilti"></div>

          <div className="kart-ikon bekleyen-ikon">
            ⏳
          </div>

          <div className="kart-icerik">
            <span>Onay Bekleyen</span>
            <strong>
              {onayBekleyenSayisi}
            </strong>
            <small>Yönetici onayı gerekli</small>
          </div>

          <div className="kart-ok">→</div>
        </article>

        <article
          className="dashboard-karti kart-yanitlanan"
          onClick={() =>
            navigate(
              "/talepler?durum=otomatik_yanitlandi"
            )
          }
        >
          <div className="kart-parilti"></div>

          <div className="kart-ikon yanitlanan-ikon">
            🤖
          </div>

          <div className="kart-icerik">
            <span>Otomatik Yanıtlanan</span>
            <strong>
              {otomatikYanitlananSayisi}
            </strong>
            <small>AI tarafından yanıtlandı</small>
          </div>

          <div className="kart-ok">→</div>
        </article>

        <article
          className="dashboard-karti kart-musteri-bekleyen"
          onClick={() =>
            navigate(
              "/talepler?durum=musteri_yaniti_bekleniyor"
            )
          }
        >
          <div className="kart-parilti"></div>

          <div className="kart-ikon musteri-bekleyen-ikon">
            📬
          </div>

          <div className="kart-icerik">
            <span>Müşteri Yanıtı Bekleyen</span>
            <strong>
              {musteriYanitiBekleyenSayisi}
            </strong>
            <small>Çözüm onayı bekleniyor</small>
          </div>

          <div className="kart-ok">→</div>
        </article>

        <article
          className="dashboard-karti kart-cozulen"
          onClick={() =>
            navigate("/talepler?durum=cozuldu")
          }
        >
          <div className="kart-parilti"></div>

          <div className="kart-ikon cozulen-ikon">
            ✅
          </div>

          <div className="kart-icerik">
            <span>Çözülen Talepler</span>
            <strong>{cozulenTalepSayisi}</strong>
            <small>Müşteri tarafından onaylandı</small>
          </div>

          <div className="kart-ok">→</div>
        </article>

        <article
          className="dashboard-karti kart-kritik"
          onClick={() =>
            navigate(
              "/talepler?oncelik=kritik"
            )
          }
        >
          <div className="kart-parilti"></div>

          <div className="kart-ikon kritik-ikon">
            🚨
          </div>

          <div className="kart-icerik">
            <span>Kritik Talepler</span>
            <strong>{kritikTalepSayisi}</strong>
            <small>Acil müdahale gerektiriyor</small>
          </div>

          <div className="kart-ok">→</div>
        </article>

        <article
          className="dashboard-karti kart-son-saat"
          onClick={() =>
            navigate(
              "/talepler?zaman=son24saat"
            )
          }
        >
          <div className="kart-parilti"></div>

          <div className="kart-ikon saat-ikon">
            🕐
          </div>

          <div className="kart-icerik">
            <span>Son 24 Saat</span>
            <strong>
              {sonYirmiDortSaatTalepSayisi}
            </strong>
            <small>Yeni gelen talepler</small>
          </div>

          <div className="kart-ok">→</div>
        </article>

        <article className="dashboard-karti kart-sure sabit-kart">
          <div className="kart-parilti"></div>

          <div className="kart-ikon sure-ikon">
            ⏱️
          </div>

          <div className="kart-icerik">
            <span>Ortalama Yanıt Süresi</span>

            <strong className="uzun-deger">
              {ortalamaYanitBeklemeSuresi}
            </strong>

            <small>Ortalama bekleme zamanı</small>
          </div>
        </article>

        <article
          className="dashboard-karti kart-ai"
          onClick={() =>
            navigate(
              "/talepler?ai_analiz=true"
            )
          }
        >
          <div className="kart-parilti"></div>

          <div className="kart-ikon ai-ikon">
            🧠
          </div>

          <div className="kart-icerik">
            <span>AI Analiz Edilen</span>
            <strong>
              {aiAnalizEdilenTalepSayisi}
            </strong>
            <small>Yapay zekâ analizi tamamlandı</small>
          </div>

          <div className="kart-ok">→</div>
        </article>
      </div>



      <article className="dashboard-bilgi-karti geciken-talepler-karti">
        <div className="bilgi-karti-baslik">
          <div className="bilgi-baslik-ikonu gecikme-ikonu">
            ⏰
          </div>

          <div>
            <span>SLA ve bekleme takibi</span>
            <h3>Geciken Talepler</h3>
          </div>
        </div>

        {gecikenTalepler.length === 0 ? (
          <div className="kategori-bos-alani">
            <div>✅</div>
            <h4>Geciken talep yok</h4>
            <p>
              Belirlenen süre eşiklerini aşan aktif
              bir talep bulunmuyor.
            </p>
          </div>
        ) : (
          <div className="geciken-talepler-listesi">
            {gecikenTalepler.map((talep) => (
              <button
                type="button"
                className="geciken-talep-satiri"
                key={talep.talep_id}
                onClick={() =>
                  navigate(
                    `/talep-detay/${encodeURIComponent(
                      talep.talep_takip_no
                    )}`
                  )
                }
              >
                <div className="geciken-talep-ust-satir">
                  <strong>{talep.talep_takip_no}</strong>

                  <span
                    className={`gecikme-rozeti ${
                      talep.gecikme_seviyesi ===
                      "kritik_gecikme"
                        ? "gecikme-kritik"
                        : talep.gecikme_seviyesi ===
                          "gecikmis"
                        ? "gecikme-gecikmis"
                        : "gecikme-uyari"
                    }`}
                  >
                    {talep.gecikme_seviyesi ===
                    "kritik_gecikme"
                      ? "Kritik gecikme"
                      : talep.gecikme_seviyesi ===
                        "gecikmis"
                      ? "Gecikmiş"
                      : "Uyarı"}
                  </span>
                </div>

                <span className="geciken-talep-baslik">
                  {talep.talep_baslik}
                </span>

                <small>
                  ⏱ {talep.bekleme_suresi}
                </small>

                <p>{talep.gecikme_nedeni}</p>
              </button>
            ))}
          </div>
        )}
      </article>
<article className="dashboard-bilgi-karti personel-is-yuku-karti">
  <div className="bilgi-karti-baslik">
    <div className="bilgi-baslik-ikonu personel-yuku-ikonu">
      👥
    </div>

    <div>
      <span>Personel performansı</span>
      <h3>Personel İş Yükü</h3>
    </div>
  </div>

  {aktifPersonelDagilimi.length === 0 ? (
    <div className="kategori-bos-alani">
      <div>👤</div>

      <h4>Personel verisi bulunamadı</h4>

      <p>
        Personellere talep atandığında iş yükü
        dağılımı burada görünecek.
      </p>
    </div>
  ) : (
    <div className="personel-yuku-listesi">
      {aktifPersonelDagilimi.map((personel) => {
        const talepSayisi =
          Number(personel.talep_sayisi) || 0;

        const cubukGenisligi =
          (talepSayisi /
            enYuksekPersonelTalepSayisi) *
          100;

        return (
          <div
            className="personel-yuku-satiri"
            key={personel.personel_id}
          >
            <div className="personel-yuku-bilgisi">
              <div className="personel-yuku-avatar">
                {personel.personel_adi
                  ?.charAt(0)
                  .toLocaleUpperCase("tr-TR") ||
                  "P"}
              </div>

              <div className="personel-yuku-metin">
                <strong>
                  {personel.personel_adi
                    ? personel.personel_adi
                        .split("(")[0]
                        .trim()
                    : "İsimsiz Personel"}
                </strong>

                <span>
                  Atanmış destek talepleri
                </span>
              </div>

              <div className="personel-yuku-sayisi">
                <strong>{talepSayisi}</strong>
                <span>Talep</span>
              </div>
            </div>

            <div className="personel-yuku-cubuk-alani">
              <div
                className="personel-yuku-cubugu"
                style={{
                  width: `${cubukGenisligi}%`,
                }}
              ></div>
            </div>
          </div>
        );
      })}
    </div>
  )}
</article>
      <div className="dashboard-alt-grid">
        <article className="dashboard-bilgi-karti">
          <div className="bilgi-karti-baslik">
            <div className="bilgi-baslik-ikonu durum-ozeti-ikonu">
              📊
            </div>

            <div>
              <span>Güncel durumlar</span>
              <h3>Talep Durumu Özeti</h3>
            </div>
          </div>

          <div className="durum-listesi">
            <div className="durum-satiri">
              <div>
                <span className="satir-noktasi nokta-mavi"></span>
                Açık talepler
              </div>

              <strong>{acikTalepSayisi}</strong>
            </div>

            <div className="durum-satiri">
              <div>
                <span className="satir-noktasi nokta-turuncu"></span>
                Onay bekleyen talepler
              </div>

              <strong>
                {onayBekleyenSayisi}
              </strong>
            </div>

            <div className="durum-satiri">
              <div>
                <span className="satir-noktasi nokta-mor"></span>
                Otomatik yanıtlanan talepler
              </div>

              <strong>
                {otomatikYanitlananSayisi}
              </strong>
            </div>

            <div className="durum-satiri">
              <div>
                <span className="satir-noktasi nokta-kirmizi"></span>
                Kritik talepler
              </div>

              <strong>{kritikTalepSayisi}</strong>
            </div>

            <div className="durum-satiri">
              <div>
                <span className="satir-noktasi nokta-pembe"></span>
                Son 24 saatte gelen talepler
              </div>

              <strong>
                {sonYirmiDortSaatTalepSayisi}
              </strong>
            </div>

            <div className="durum-satiri">
              <div>
                <span className="satir-noktasi nokta-yesil"></span>
                AI analiz edilen talepler
              </div>

              <strong>
                {aiAnalizEdilenTalepSayisi}
              </strong>
            </div>

            <div className="durum-satiri">
              <div>
                <span className="satir-noktasi nokta-lila"></span>
                Ortalama yanıt bekleme süresi
              </div>

              <strong className="sure-rozeti">
                {ortalamaYanitBeklemeSuresi}
              </strong>
            </div>
          </div>
        </article>

        <article className="dashboard-bilgi-karti">
          <div className="bilgi-karti-baslik">
            <div className="bilgi-baslik-ikonu kategori-ikonu">
              🗂️
            </div>

            <div>
              <span>Talep konuları</span>
              <h3>Kategori Dağılımı</h3>
            </div>
          </div>

          {kategoriDagilimi.length === 0 ? (
            <div className="kategori-bos-alani">
              <div>🌸</div>

              <h4>Henüz kategori yok</h4>

              <p>
                Talepler analiz edildiğinde kategori
                bilgileri burada görünecek.
              </p>
            </div>
          ) : (
            <div className="durum-listesi">
              {kategoriDagilimi.map(
                (kategori, index) => (
                  <div
                    className="durum-satiri kategori-satiri"
                    key={kategori.kategori}
                  >
                    <div>
                      <span
                        className={`kategori-numarasi kategori-renk-${
                          (index % 5) + 1
                        }`}
                      >
                        {index + 1}
                      </span>

                      {kategori.kategori}
                    </div>

                    <strong>
                      {kategori.talep_sayisi}
                    </strong>
                  </div>
                )
              )}
            </div>
          )}
        </article>
      </div>
    </section>
  );
}

export default Dashboard;