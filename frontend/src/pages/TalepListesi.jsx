import { useEffect, useState } from "react";
import {
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import { getTalepler } from "../services/api";
import "./TalepListesi.css";

function TalepListesi() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [talepler, setTalepler] = useState([]);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [hata, setHata] = useState("");
  const [aramaMetni, setAramaMetni] = useState("");

  const durumFiltresi = searchParams.get("durum");
  const oncelikFiltresi = searchParams.get("oncelik");
  const zamanFiltresi = searchParams.get("zaman");
  const aiAnalizFiltresi = searchParams.get("ai_analiz");

  useEffect(() => {
    async function talepleriYukle() {
      try {
        const sonuc = await getTalepler();

        setTalepler(sonuc.veri || []);
      } catch (error) {
        setHata(error.message);
      } finally {
        setYukleniyor(false);
      }
    }

    talepleriYukle();
  }, []);

  const durumFiltreliTalepler = durumFiltresi
    ? talepler.filter((talep) => {
        const talepDurumu =
          talep.talep_durum?.toLowerCase();

        if (durumFiltresi === "acik") {
          return (
            talepDurumu === "acik" ||
            talepDurumu === "açık"
          );
        }

        return (
          talepDurumu === durumFiltresi.toLowerCase()
        );
      })
    : talepler;

  const oncelikFiltreliTalepler = oncelikFiltresi
    ? durumFiltreliTalepler.filter((talep) => {
        const talepOnceligi =
          talep.yz_oncelik_seviyesi
            ?.trim()
            .toLocaleLowerCase("tr-TR");

        const secilenOncelik =
          oncelikFiltresi
            .trim()
            .toLocaleLowerCase("tr-TR");

        return talepOnceligi === secilenOncelik;
      })
    : durumFiltreliTalepler;

  const zamanFiltreliTalepler =
    zamanFiltresi === "son24saat"
      ? oncelikFiltreliTalepler.filter((talep) => {
          if (!talep.talep_olusturulma_tarihi) {
            return false;
          }

          const olusturma = new Date(
            talep.talep_olusturulma_tarihi
          );

          const yirmiDortSaatOnce = new Date(
            Date.now() - 24 * 60 * 60 * 1000
          );

          return olusturma >= yirmiDortSaatOnce;
        })
      : oncelikFiltreliTalepler;

  const aiFiltreliTalepler =
    aiAnalizFiltresi === "true"
      ? zamanFiltreliTalepler.filter(
          (talep) =>
            talep.yz_ozet ||
            talep.yz_oncelik_seviyesi ||
            talep.yz_guven_skoru != null
        )
      : zamanFiltreliTalepler;

  const filtrelenmisTalepler =
    aiFiltreliTalepler.filter((talep) => {
      const temizAramaMetni =
        aramaMetni.toLocaleLowerCase("tr-TR").trim();

      const takipNo =
        talep.talep_takip_no
          ?.toLocaleLowerCase("tr-TR") || "";

      const baslik =
        talep.talep_baslik
          ?.toLocaleLowerCase("tr-TR") || "";

      const kategori =
        talep.kategori_ad
          ?.toLocaleLowerCase("tr-TR") || "";

      const gonderen =
        talep.talep_gonderen_ad_soyad
          ?.toLocaleLowerCase("tr-TR") || "";

      return (
        takipNo.includes(temizAramaMetni) ||
        baslik.includes(temizAramaMetni) ||
        kategori.includes(temizAramaMetni) ||
        gonderen.includes(temizAramaMetni)
      );
    });

  function talepDetayinaGit(takipNo) {
    const kodlanmisTakipNo =
      encodeURIComponent(takipNo);

    navigate(`/talep-detay/${kodlanmisTakipNo}`);
  }

  function durumSinifi(durum) {
    const temizDurum = durum?.toLowerCase();

    if (
      temizDurum === "acik" ||
      temizDurum === "açık"
    ) {
      return "durum-etiketi durum-acik";
    }

    if (
      temizDurum === "kapali" ||
      temizDurum === "kapalı"
    ) {
      return "durum-etiketi durum-kapali";
    }

    if (
      temizDurum === "cozuldu" ||
      temizDurum === "çözüldü"
    ) {
      return "durum-etiketi durum-kapali";
    }

    if (temizDurum === "beklemede") {
      return "durum-etiketi durum-beklemede";
    }

    if (temizDurum === "onay_bekliyor") {
      return "durum-etiketi durum-onay-bekliyor";
    }

    if (temizDurum === "otomatik_yanitlandi") {
      return "durum-etiketi durum-otomatik-yanitlandi";
    }

    if (temizDurum === "inceleniyor") {
      return "durum-etiketi durum-inceleniyor";
    }

    if (
      temizDurum === "musteri_yaniti_bekleniyor"
    ) {
      return "durum-etiketi durum-musteri-bekleniyor";
    }

    return "durum-etiketi durum-belirsiz";
  }

  function durumMetni(durum) {
    const temizDurum = durum?.toLowerCase();

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
      temizDurum === "cozuldu" ||
      temizDurum === "çözüldü"
    ) {
      return "Çözüldü";
    }

    if (temizDurum === "beklemede") {
      return "Beklemede";
    }

    if (temizDurum === "onay_bekliyor") {
      return "Onay Bekliyor";
    }

    if (temizDurum === "otomatik_yanitlandi") {
      return "Otomatik Yanıtlandı";
    }

    if (temizDurum === "inceleniyor") {
      return "İnceleniyor";
    }

    if (
      temizDurum === "musteri_yaniti_bekleniyor"
    ) {
      return "Müşteri Yanıtı Bekleniyor";
    }

    return durum || "Belirtilmemiş";
  }

  function oncelikSinifi(oncelik) {
    const temizOncelik =
      oncelik?.trim().toLocaleLowerCase("tr-TR");

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
      oncelik?.trim().toLocaleLowerCase("tr-TR");

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
    const temizDuygu =
      duygu?.trim().toLocaleLowerCase("tr-TR");

    if (
      temizDuygu === "çok olumsuz" ||
      temizDuygu === "cok olumsuz"
    ) {
      return "duygu-etiketi duygu-cok-olumsuz";
    }

    if (temizDuygu === "olumsuz") {
      return "duygu-etiketi duygu-olumsuz";
    }

    if (
      temizDuygu === "olumlu" ||
      temizDuygu === "çok olumlu" ||
      temizDuygu === "cok olumlu"
    ) {
      return "duygu-etiketi duygu-olumlu";
    }

    if (
      temizDuygu === "nötr" ||
      temizDuygu === "notr"
    ) {
      return "duygu-etiketi duygu-notr";
    }

    return "duygu-etiketi duygu-belirsiz";
  }

  function duyguMetni(duygu) {
    if (!duygu) {
      return "Analiz edilmedi";
    }

    return duygu;
  }

  function tarihFormatla(tarih) {
    if (!tarih) {
      return "Belirtilmemiş";
    }

    const tarihNesnesi = new Date(tarih);

    if (Number.isNaN(tarihNesnesi.getTime())) {
      return "Geçersiz tarih";
    }

    return tarihNesnesi.toLocaleString("tr-TR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function beklemeSuresiHesapla(tarih, durum) {
    if (!tarih) {
      return "Belirtilmemiş";
    }

    const olusturmaTarihi = new Date(tarih);

    if (Number.isNaN(olusturmaTarihi.getTime())) {
      return "Belirtilmemiş";
    }

    const temizDurum =
      durum?.trim().toLocaleLowerCase("tr-TR");

    if (
      temizDurum === "kapali" ||
      temizDurum === "kapalı" ||
      temizDurum === "cozuldu" ||
      temizDurum === "çözüldü"
    ) {
      return "Tamamlandı";
    }

    const farkMilisaniye =
      Date.now() - olusturmaTarihi.getTime();

    if (farkMilisaniye < 0) {
      return "Yeni";
    }

    const toplamDakika = Math.floor(
      farkMilisaniye / (1000 * 60)
    );

    if (toplamDakika < 1) {
      return "1 dakikadan az";
    }

    if (toplamDakika < 60) {
      return `${toplamDakika} dakika`;
    }

    const toplamSaat = Math.floor(
      toplamDakika / 60
    );

    if (toplamSaat < 24) {
      const kalanDakika = toplamDakika % 60;

      if (kalanDakika === 0) {
        return `${toplamSaat} saat`;
      }

      return `${toplamSaat} saat ${kalanDakika} dakika`;
    }

    const toplamGun = Math.floor(
      toplamSaat / 24
    );

    const kalanSaat = toplamSaat % 24;

    if (kalanSaat === 0) {
      return `${toplamGun} gün`;
    }

    return `${toplamGun} gün ${kalanSaat} saat`;
  }

  function aiOzetiKisalt(ozet) {
    if (!ozet) {
      return "AI analizi henüz tamamlanmadı.";
    }

    if (ozet.length <= 160) {
      return ozet;
    }

    return `${ozet.substring(0, 160)}...`;
  }

  if (yukleniyor) {
    return <p>Talepler yükleniyor...</p>;
  }

  if (hata) {
    return <p>Hata: {hata}</p>;
  }

  return (
    <section className="talep-listesi-sayfasi">
      <div className="talep-listesi-baslik">
        <div>
          <p className="sayfa-etiketi">
            Talep Yönetimi
          </p>

          <h2>Talep Listesi</h2>

          <p className="sayfa-aciklama">
            Sisteme gelen destek taleplerini,
            yapay zekâ analizleriyle birlikte
            görüntüleyebilirsiniz.
          </p>
        </div>

        <div className="toplam-talep-karti">
          <span>Gösterilen Talep</span>

          <strong>
            {filtrelenmisTalepler.length}
          </strong>
        </div>
      </div>

      <div className="arama-alani">
        <input
          type="text"
          placeholder="Takip no, başlık, kategori veya gönderen ara..."
          value={aramaMetni}
          onChange={(event) =>
            setAramaMetni(event.target.value)
          }
        />
      </div>

      {filtrelenmisTalepler.length === 0 ? (
        <p>Aramanıza uygun talep bulunmuyor.</p>
      ) : (
        <div className="tablo-karti">
          <div className="tablo-kapsayici">
            <table className="talep-tablosu">
              <thead>
                <tr>
                  <th>Takip No</th>
                  <th>Talep ve AI Özeti</th>
                  <th>Kategori</th>
                  <th>Durum</th>
                  <th>Öncelik</th>
                  <th>Duygu</th>
                  <th>Geliş Zamanı</th>
                  <th>Bekleme Süresi</th>
                </tr>
              </thead>

              <tbody>
                {filtrelenmisTalepler.map(
                  (talep) => (
                    <tr
                      key={talep.talep_id}
                      onClick={() =>
                        talepDetayinaGit(
                          talep.talep_takip_no
                        )
                      }
                    >
                      <td className="takip-no">
                        {talep.talep_takip_no}
                      </td>

                      <td className="talep-ozet-hucresi">
                        <strong className="talep-basligi">
                          {talep.talep_baslik ||
                            "Başlık bulunmuyor"}
                        </strong>

                        <p className="ai-ozeti">
                          {aiOzetiKisalt(
                            talep.yz_ozet
                          )}
                        </p>
                      </td>

                      <td>
                        <span className="kategori-etiketi">
                          {talep.kategori_ad ||
                            "Kategorisiz"}
                        </span>
                      </td>

                      <td>
                        <span
                          className={durumSinifi(
                            talep.talep_durum
                          )}
                        >
                          {durumMetni(
                            talep.talep_durum
                          )}
                        </span>
                      </td>

                      <td>
                        <span
                          className={oncelikSinifi(
                            talep.yz_oncelik_seviyesi
                          )}
                        >
                          {oncelikMetni(
                            talep.yz_oncelik_seviyesi
                          )}
                        </span>
                      </td>

                      <td>
                        <span
                          className={duyguSinifi(
                            talep.yz_duygu_durumu
                          )}
                        >
                          {duyguMetni(
                            talep.yz_duygu_durumu
                          )}
                        </span>
                      </td>

                      <td className="tarih-hucresi">
                        {tarihFormatla(
                          talep.talep_olusturulma_tarihi
                        )}
                      </td>

                      <td className="bekleme-suresi">
                        {beklemeSuresiHesapla(
                          talep.talep_olusturulma_tarihi,
                          talep.talep_durum
                        )}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}

export default TalepListesi;