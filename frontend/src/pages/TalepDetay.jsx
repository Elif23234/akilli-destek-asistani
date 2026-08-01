import { useEffect, useState } from "react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  getTalepDetayi,
  getBenzerTalepler,
  personelOnaylaVeGonder,
  talebiYapayZekaIleAnalizEt,
} from "../services/api";

import "../pages/TalepDetay.css";

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

  const [yanitMetni, setYanitMetni] =
    useState("");
  const [yanitKontrolEdildi, setYanitKontrolEdildi] =
    useState(false);
  const [onayGonderiliyor, setOnayGonderiliyor] =
    useState(false);
  const [onayMesaji, setOnayMesaji] =
    useState("");
  const [onayHatasi, setOnayHatasi] =
    useState("");

  const [aiAnalizYapiliyor, setAiAnalizYapiliyor] =
    useState(false);

  const [aiAnalizMesaji, setAiAnalizMesaji] =
    useState("");

  const [aiAnalizHatasi, setAiAnalizHatasi] =
    useState("");

  useEffect(() => {
  async function talepDetayiniYukle() {
    try {
      setYukleniyor(true);
      setHata("");

      const temizTakipNo =
        decodeURIComponent(takipNo);

      const sonuc =
        await getTalepDetayi(temizTakipNo);

      console.log(
        "Detay verisi:",
        sonuc.veri
      );

      setTalep(sonuc.veri);

      setYanitMetni(
        sonuc.veri?.ai_taslak_yanit || ""
      );

      setYanitKontrolEdildi(false);
      setOnayMesaji("");
      setOnayHatasi("");

      const aramaMetni = [
        sonuc.veri?.talep_baslik,
        sonuc.veri?.talep_ham_icerik,
      ]
        .filter(Boolean)
        .join(" ");

      setYukleniyor(false);

      if (aramaMetni.trim()) {
        benzerTalepleriYukle(
          aramaMetni,
          temizTakipNo
        );
      }
    } catch (error) {
      setHata(error.message);
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

    if (temizOncelik === "kritik") {
      return "oncelik-etiketi oncelik-kritik";
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

    if (temizOncelik === "kritik") {
      return "Kritik";
    }

    return "Belirtilmemiş";
  }

  function duyguSinifi(duygu) {
    const temizDuygu = duygu
      ?.toLocaleLowerCase("tr-TR")
      .trim();

    if (
      temizDuygu === "olumlu" ||
      temizDuygu === "pozitif" ||
      temizDuygu === "çok olumlu"
    ) {
      return "duygu-etiketi duygu-olumlu";
    }

    if (
      temizDuygu === "olumsuz" ||
      temizDuygu === "negatif" ||
      temizDuygu === "çok olumsuz"
    ) {
      return "duygu-etiketi duygu-olumsuz";
    }

    if (
      temizDuygu === "nötr" ||
      temizDuygu === "notr"
    ) {
      return "duygu-etiketi duygu-notr";
    }

    if (
      temizDuygu === "karışık" ||
      temizDuygu === "karisik"
    ) {
      return "duygu-etiketi duygu-karisik";
    }

    return "duygu-etiketi duygu-belirsiz";
  }

  function duyguMetni(duygu) {
    const temizDuygu = duygu
      ?.toLocaleLowerCase("tr-TR")
      .trim();

    if (temizDuygu === "çok olumlu") {
      return "Çok Olumlu";
    }

    if (
      temizDuygu === "olumlu" ||
      temizDuygu === "pozitif"
    ) {
      return "Olumlu";
    }

    if (temizDuygu === "çok olumsuz") {
      return "Çok Olumsuz";
    }

    if (
      temizDuygu === "olumsuz" ||
      temizDuygu === "negatif"
    ) {
      return "Olumsuz";
    }

    if (
      temizDuygu === "nötr" ||
      temizDuygu === "notr"
    ) {
      return "Nötr";
    }

    if (
      temizDuygu === "karışık" ||
      temizDuygu === "karisik"
    ) {
      return "Karışık";
    }

    return "Belirtilmemiş";
  }

  function durumMetni(durum) {
    const temizDurum =
      durum?.toLocaleLowerCase("tr-TR")
        .trim();

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

    if (temizDurum === "beklemede") {
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

    if (
      temizDurum === "inceleniyor"
    ) {
      return "İnceleniyor";
    }

    if (
      temizDurum ===
        "musteri_bekleniyor" ||
      temizDurum ===
        "musteri_yaniti_bekleniyor"
    ) {
      return "Müşteri Yanıtı Bekleniyor";
    }

    return durum || "Belirtilmemiş";
  }

  function durumSinifi(durum) {
    const temizDurum =
      durum?.toLocaleLowerCase("tr-TR")
        .trim();

    if (
      temizDurum === "acik" ||
      temizDurum === "açık"
    ) {
      return "durum-acik";
    }

    if (
      temizDurum === "kapali" ||
      temizDurum === "kapalı"
    ) {
      return "durum-kapali";
    }

    if (
      temizDurum === "beklemede"
    ) {
      return "durum-beklemede";
    }

    if (
      temizDurum === "onay_bekliyor"
    ) {
      return "durum-onay-bekliyor";
    }

    if (
      temizDurum ===
      "otomatik_yanitlandi"
    ) {
      return "durum-otomatik-yanitlandi";
    }

    if (
      temizDurum === "inceleniyor"
    ) {
      return "durum-inceleniyor";
    }

    if (
      temizDurum ===
        "musteri_bekleniyor" ||
      temizDurum ===
        "musteri_yaniti_bekleniyor"
    ) {
      return "durum-musteri-bekleniyor";
    }

    return "durum-belirsiz";
  }

  async function aiAnaliziniBaslat() {
    if (!talep?.talep_id) {
      setAiAnalizHatasi(
        "Talep kimliği bulunamadığı için analiz başlatılamadı."
      );
      return;
    }

    if (!talep?.talep_baslik) {
      setAiAnalizHatasi(
        "Talep başlığı bulunamadığı için analiz başlatılamadı."
      );
      return;
    }

    if (!talep?.talep_ham_icerik) {
      setAiAnalizHatasi(
        "Talep içeriği bulunamadığı için analiz başlatılamadı."
      );
      return;
    }

    try {
      setAiAnalizYapiliyor(true);
      setAiAnalizMesaji("");
      setAiAnalizHatasi("");

      const sonuc = await talebiYapayZekaIleAnalizEt({
        talepId: talep.talep_id,
        baslik: talep.talep_baslik,
        icerik: talep.talep_ham_icerik,
      });

      setAiAnalizMesaji(
        sonuc.mesaj ||
          "Yapay zekâ analizi başarıyla tamamlandı."
      );

      /*
        Endpoint analiz sonucunu döndürüyor fakat talep detay
        görünümündeki bütün alanları döndürmeyebilir.
        Bu nedenle en güvenli yöntem sayfayı yeniden yüklemektir.
      */
      window.setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (error) {
      setAiAnalizHatasi(error.message);
    } finally {
      setAiAnalizYapiliyor(false);
    }
  }

  async function yanitiOnaylaVeGonder() {
    const temizYanit = yanitMetni.trim();

    if (!temizYanit) {
      setOnayHatasi(
        "Müşteriye gönderilecek yanıt boş bırakılamaz."
      );
      return;
    }

    if (!yanitKontrolEdildi) {
      setOnayHatasi(
        "Göndermeden önce yanıtı kontrol ettiğinizi onaylayın."
      );
      return;
    }

    if (!talep?.talep_id) {
      setOnayHatasi(
        "Talep kimliği bulunamadığı için işlem yapılamadı."
      );
      return;
    }

    try {
      setOnayGonderiliyor(true);
      setOnayMesaji("");
      setOnayHatasi("");

      const sonuc = await personelOnaylaVeGonder({
        talepId: talep.talep_id,
        yanitMetni: temizYanit,
        islemTipi: "AI_YANITI_ONAYLANDI",
      });

      setOnayMesaji(
        sonuc.mesaj ||
          "Yanıt onaylandı ve müşteriye gönderilmek üzere kaydedildi."
      );

      setTalep((mevcutTalep) => ({
        ...mevcutTalep,
        talep_durum: "musteri_yaniti_bekleniyor",
      }));

      setYanitKontrolEdildi(false);
    } catch (error) {
      setOnayHatasi(error.message);
    } finally {
      setOnayGonderiliyor(false);
    }
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
      <section className="talep-detay-durum-sayfasi">
        <div className="talep-detay-durum-karti">
          <div className="yukleniyor-simgesi">
            ✨
          </div>

          <h2>Talep yükleniyor</h2>

          <p>
            Talep bilgileri ve yapay zekâ
            analizleri hazırlanıyor.
          </p>
        </div>
      </section>
    );
  }

  if (hata) {
    return (
      <section className="talep-detay-durum-sayfasi">
        <div className="talep-detay-durum-karti hata-karti">
          <div className="yukleniyor-simgesi">
            ⚠️
          </div>

          <h2>Talep yüklenemedi</h2>

          <p>{hata}</p>

          <button
            type="button"
            onClick={() =>
              navigate("/talepler")
            }
          >
            Talep listesine dön
          </button>
        </div>
      </section>
    );
  }

  if (!talep) {
    return (
      <section className="talep-detay-durum-sayfasi">
        <div className="talep-detay-durum-karti">
          <div className="yukleniyor-simgesi">
            🔎
          </div>

          <h2>Talep bulunamadı</h2>

          <p>
            Bu takip numarasına ait bir
            talep kaydı bulunmuyor.
          </p>

          <button
            type="button"
            onClick={() =>
              navigate("/talepler")
            }
          >
            Talep listesine dön
          </button>
        </div>
      </section>
    );
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

  const oncelikGerekcesi =
    talep.yz_oncelik_gerekcesi ||
    talep.oncelik_gerekcesi;

  const duygu =
    talep.yz_duygu_durumu ||
    talep.duygu_durumu ||
    talep.duygu;

  const temizTalepDurumu = String(
    talep.talep_durum || ""
  )
    .trim()
    .toLocaleLowerCase("tr-TR");

  const talepAcikMi =
    temizTalepDurumu === "acik" ||
    temizTalepDurumu === "açık";

  const aiAnalizButonuGoster =
      talepAcikMi && !aiOzeti;

  return (
    <section className="talep-detay-sayfasi">
      <div className="talep-detay-icerik">
        <div className="talep-detay-ust-satir">
          <button
            type="button"
            className="geri-don-butonu"
            onClick={() =>
              navigate("/talepler")
            }
          >
            <span>←</span>
            Talep listesine dön
          </button>

          <span className="detay-sayfa-etiketi">
            Talep yönetimi
          </span>
        </div>

        <header className="talep-detay-hero">
          <div className="talep-detay-hero-sol">
            <div className="talep-detay-hero-ikon">
              📬
            </div>

            <div>
              <span className="talep-detay-kucuk-baslik">
                Müşteri destek kaydı
              </span>

              <h1>Talep Detayı</h1>

              <p>
                Talebin orijinal içeriğini,
                yapay zekâ analizini ve benzer
                talepleri tek ekranda
                inceleyebilirsiniz.
              </p>
            </div>
          </div>

          <div className="talep-detay-hero-sag">
            <span
              className={`detay-durum-etiketi ${durumSinifi(
                talep.talep_durum
              )}`}
            >
              {durumMetni(
                talep.talep_durum
              )}
            </span>

            <span className="detay-takip-basligi">
              Takip numarası
            </span>

            <strong className="detay-takip-no">
              {talep.talep_takip_no}
            </strong>
          </div>
        </header>

        <div className="talep-detay-grid">
          <article className="detay-karti orijinal-talep-karti">
            <div className="detay-kart-basligi">
              <div className="detay-kart-ikon pembe-ikon">
                📩
              </div>

              <div>
                <span>Müşteri mesajı</span>
                <h2>Orijinal Talep</h2>
              </div>
            </div>

            <div className="talep-bilgi-grid">
              <div className="talep-bilgi-alani">
                <span className="talep-bilgi-baslik">
                  Takip No
                </span>

                <p>
                  {talep.talep_takip_no}
                </p>
              </div>

              <div className="talep-bilgi-alani">
                <span className="talep-bilgi-baslik">
                  Durum
                </span>

                <p>
                  <span
                    className={`detay-durum-etiketi kucuk-durum ${durumSinifi(
                      talep.talep_durum
                    )}`}
                  >
                    {durumMetni(
                      talep.talep_durum
                    )}
                  </span>
                </p>
              </div>

              <div className="talep-bilgi-alani">
                <span className="talep-bilgi-baslik">
                  Gönderen
                </span>

                <p>
                  {talep.talep_gonderen_ad_soyad ||
                    "Belirtilmemiş"}
                </p>
              </div>

              <div className="talep-bilgi-alani">
                <span className="talep-bilgi-baslik">
                  E-posta
                </span>

                <p className="eposta-metni">
                  {talep.talep_gonderen_eposta ||
                    "Belirtilmemiş"}
                </p>
              </div>

              <div className="talep-bilgi-alani">
                <span className="talep-bilgi-baslik">
                  Kaynak
                </span>

                <p>
                  {talep.talep_kaynak ||
                    "Belirtilmemiş"}
                </p>
              </div>
            </div>

            <div className="talep-metin-alani">
              <span className="talep-bilgi-baslik">
                Başlık
              </span>

              <p className="talep-detay-basligi">
                {talep.talep_baslik ||
                  "Başlık bulunmuyor"}
              </p>
            </div>

            <div className="talep-metin-alani talep-icerik-kutusu">
              <span className="talep-bilgi-baslik">
                Talep İçeriği
              </span>

              <p>
                {talep.talep_ham_icerik ||
                  "Talep içeriği bulunmuyor"}
              </p>
            </div>
          </article>

          <article className="detay-karti ai-analiz-karti">
            <div className="detay-kart-basligi">
              <div className="detay-kart-ikon mor-ikon">
                🤖
              </div>

              <div>
                <span>Yapay zekâ sonucu</span>
                <h2>AI Analizi</h2>
              </div>
            </div>

            <div className="ai-ozet-kutusu">
              <span className="ai-analiz-baslik">
                AI Özeti
              </span>

              <p>
                {aiOzeti ||
                  "Bu talep için henüz AI özeti oluşturulmamış."}
              </p>
            </div>

            <div className="ai-metrik-grid">
              <div className="ai-metrik-karti">
                <span>Kategori</span>

                <strong>
                  {kategori ||
                    "Belirtilmemiş"}
                </strong>
              </div>

              <div className="ai-metrik-karti">
                <span>Öncelik</span>

                <strong>
                  <span
                    className={oncelikSinifi(
                      oncelik
                    )}
                  >
                    {oncelikMetni(
                      oncelik
                    )}
                  </span>
                </strong>
              </div>

              <div className="ai-metrik-karti">
                <span>Duygu Durumu</span>

                <strong>
                  <span
                    className={duyguSinifi(
                      duygu
                    )}
                  >
                    {duyguMetni(duygu)}
                  </span>
                </strong>
              </div>
            </div>

            <div className="oncelik-gerekcesi-kutusu">
              <div className="gerekce-baslik">
                <span>💡</span>

                <strong>
                  Öncelik Gerekçesi
                </strong>
              </div>

              <p className="oncelik-gerekcesi">
                {oncelikGerekcesi ||
                  "Bu talep için henüz öncelik gerekçesi oluşturulmamış."}
              </p>
            </div>
             {aiAnalizButonuGoster && (
  <div className="ai-analiz-islem-alani">
    <div className="ai-analiz-islem-aciklama">
      <strong>Bu talep henüz analiz edilmemiş</strong>

      <p>
        Kategori, öncelik, duygu durumu ve AI
        özetini oluşturmak için analizi
        başlatabilirsiniz.
      </p>
    </div>

    {aiAnalizHatasi && (
      <div className="ai-analiz-bildirim ai-analiz-hata">
        ⚠️ {aiAnalizHatasi}
      </div>
    )}

    {aiAnalizMesaji && (
      <div className="ai-analiz-bildirim ai-analiz-basarili">
        ✅ {aiAnalizMesaji}
      </div>
    )}

    <button
      type="button"
      className="ai-analiz-baslat-butonu"
      onClick={aiAnaliziniBaslat}
      disabled={aiAnalizYapiliyor}
    >
      {aiAnalizYapiliyor
        ? "AI analiz ediyor..."
        : "🤖 AI Analizini Başlat"}
    </button>
  </div>
)}
          </article>
        </div>

        {(talep.talep_durum
          ?.toLocaleLowerCase("tr-TR")
          .trim() === "onay_bekliyor" ||
          onayMesaji) && (
          <section className="detay-karti personel-onay-bolumu">
            <div className="personel-onay-basligi">
              <div className="detay-kart-basligi">
                <div className="detay-kart-ikon yesil-ikon">
                  ✅
                </div>

                <div>
                  <span>Personel işlemi</span>
                  <h2>Yönetici Onayı</h2>
                </div>
              </div>

              <p>
                Yapay zekâ tarafından hazırlanan yanıtı
                kontrol edin. Gerekirse düzenleyip
                müşteriye gönderin.
              </p>
            </div>

            <label
              className="yanit-metin-etiketi"
              htmlFor="personel-yanit-metni"
            >
              Müşteriye gönderilecek yanıt
            </label>

            <textarea
              id="personel-yanit-metni"
              className="personel-yanit-alani"
              value={yanitMetni}
              onChange={(event) => {
                setYanitMetni(event.target.value);
                setOnayMesaji("");
                setOnayHatasi("");
                setYanitKontrolEdildi(false);
              }}
              rows={8}
              disabled={onayGonderiliyor}
              placeholder="AI yanıt taslağı bulunmuyorsa müşteriye gönderilecek yanıtı buraya yazın."
            />

            <label className="yanit-kontrol-satiri">
              <input
                type="checkbox"
                checked={yanitKontrolEdildi}
                onChange={(event) => {
                  setYanitKontrolEdildi(
                    event.target.checked
                  );
                  setOnayHatasi("");
                }}
                disabled={onayGonderiliyor}
              />

              <span>
                Yanıtı kontrol ettim ve müşteriye
                gönderilmesini onaylıyorum.
              </span>
            </label>

            {onayHatasi && (
              <div className="onay-bildirim onay-hata">
                ⚠️ {onayHatasi}
              </div>
            )}

            {onayMesaji && (
              <div className="onay-bildirim onay-basarili">
                ✅ {onayMesaji}
              </div>
            )}

            <div className="personel-onay-alt-satir">
              <small>
                Gönderilen yanıt sistem kayıtlarına
                personel yanıtı olarak eklenecektir.
              </small>

              <button
                type="button"
                className="yaniti-onayla-butonu"
                onClick={yanitiOnaylaVeGonder}
                disabled={
                  onayGonderiliyor ||
                  !yanitKontrolEdildi ||
                  !yanitMetni.trim() ||
                  talep.talep_durum
                    ?.toLocaleLowerCase("tr-TR")
                    .trim() !== "onay_bekliyor"
                }
              >
                {onayGonderiliyor
                  ? "Gönderiliyor..."
                  : "Onayla ve Gönder"}
              </button>
            </div>
          </section>
        )}

        <section className="detay-karti benzer-talepler-bolumu">
          <div className="benzer-talepler-basligi">
            <div className="detay-kart-basligi">
              <div className="detay-kart-ikon mavi-ikon">
                🔎
              </div>

              <div>
                <span>RAG benzerlik araması</span>
                <h2>Benzer Talepler</h2>
              </div>
            </div>

            <p>
              Mevcut talebe içerik bakımından
              benzeyen önceki kayıtlar.
            </p>
          </div>

          {benzerlerYukleniyor ? (
            <div className="benzer-talep-mesaji">
              <span>✨</span>

              <p>
                Benzer talepler aranıyor...
              </p>
            </div>
          ) : benzerTalepHatasi ? (
            <div className="benzer-talep-mesaji hata-mesaji">
              <span>⚠️</span>

              <p>
                {benzerTalepHatasi}
              </p>
            </div>
          ) : benzerTalepler.length === 0 ? (
            <div className="benzer-talep-mesaji">
              <span>📭</span>

              <p>
                Bu taleple benzer bir kayıt
                bulunamadı.
              </p>
            </div>
          ) : (
            <div className="benzer-talepler-listesi">
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
                    <button
                      key={
                        benzerTalep.talep_id ||
                        benzerTakipNo ||
                        index
                      }
                      type="button"
                      className="benzer-talep-butonu"
                      disabled={!benzerTakipNo}
                      onClick={() =>
                        benzerTalepDetayinaGit(
                          benzerTakipNo
                        )
                      }
                    >
                      <span className="benzer-talep-ikon">
                        📄
                      </span>

                      <span className="benzer-talep-metin">
                        <strong>
                          {benzerTakipNo ||
                            "Takip numarası yok"}
                        </strong>

                        <small>
                          {benzerBaslik}
                        </small>
                      </span>

                      <span className="benzer-talep-ok">
                        →
                      </span>
                    </button>
                  );
                }
              )}
            </div>
          )}
        </section>
      </div>
    </section>
  );
}

export default TalepDetay