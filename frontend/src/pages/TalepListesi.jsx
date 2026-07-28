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

  useEffect(() => {
    async function talepleriYukle() {
      try {
        const sonuc = await getTalepler();
        setTalepler(sonuc.veri);
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

  const filtrelenmisTalepler =
    durumFiltreliTalepler.filter((talep) => {
      const temizAramaMetni =
        aramaMetni.toLowerCase().trim();

      const takipNo =
        talep.talep_takip_no?.toLowerCase() || "";

      const baslik =
        talep.talep_baslik?.toLowerCase() || "";

      return (
        takipNo.includes(temizAramaMetni) ||
        baslik.includes(temizAramaMetni)
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

    if (temizDurum === "beklemede") {
      return "durum-etiketi durum-beklemede";
    }

    if (temizDurum === "onay_bekliyor") {
      return "durum-etiketi durum-onay-bekliyor";
    }

    if (temizDurum === "otomatik_yanitlandi") {
      return "durum-etiketi durum-otomatik-yanitlandi";
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

    if (temizDurum === "beklemede") {
      return "Beklemede";
    }

    if (temizDurum === "onay_bekliyor") {
      return "Onay Bekliyor";
    }

    if (temizDurum === "otomatik_yanitlandi") {
      return "Otomatik Yanıtlandı";
    }

    return durum || "Belirtilmemiş";
  }

  function oncelikSinifi(oncelik) {
    const temizOncelik = oncelik?.toLowerCase();

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
    const temizOncelik = oncelik?.toLowerCase();

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
            Sisteme gelen destek taleplerini
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
          placeholder="Takip no veya başlık ara..."
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
                  <th>Başlık</th>
                  <th>Durum</th>
                  <th>Öncelik</th>
                  <th>Kaynak</th>
                  <th>Gönderen</th>
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

                      <td className="baslik-hucresi">
                        {talep.talep_baslik ||
                          "Başlık bulunmuyor"}
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
                        {talep.talep_kaynak ||
                          "Belirtilmemiş"}
                      </td>

                      <td>
                        {talep.talep_gonderen_ad_soyad ||
                          "Belirtilmemiş"}
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