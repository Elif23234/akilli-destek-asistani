import "./PersonelTalepDetay.css";

import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  getPersonelTalepDetayi,
  personelOnaylaVeGonder,
} from "../services/api";

function PersonelTalepDetay() {
  const navigate = useNavigate();

  const { talepId } = useParams();

  const [talep, setTalep] =
    useState(null);

  const [yukleniyor, setYukleniyor] =
    useState(true);

  const [hata, setHata] =
    useState("");

  const [yanitMetni, setYanitMetni] =
    useState("");

  useEffect(() => {
    async function yukle() {
      try {
        const veri =
          await getPersonelTalepDetayi(
            talepId
          );

        setTalep(veri);

        setYanitMetni(
          veri.yz_musteri_cevabi || ""
        );
      } catch (error) {
        setHata(error.message);
      } finally {
        setYukleniyor(false);
      }
    }

    yukle();
  }, [talepId]);

  if (yukleniyor) {
    return (
      <h2>
        Yükleniyor...
      </h2>
    );
  }

  if (hata) {
    return (
      <h2>
        {hata}
      </h2>
    );
  }

  async function gonder() {
    try {
      await personelOnaylaVeGonder({
        talepId: talep.talep_id,
        yanitMetni: yanitMetni,
      });

      alert(
        "Yanıt müşteriye gönderildi."
      );

      navigate(
        "/personel-paneli"
      );
    } catch (error) {
      alert(error.message);
    }
  }

  return (
    <div className="personel-detay-sayfasi">
      <header className="detay-ust">
        <button
          className="geri-butonu"
          onClick={() =>
            navigate(
              "/personel-paneli"
            )
          }
        >
          ← Geri
        </button>

        <div>
          <h1>
            Talep Detayı
          </h1>

          <p>
            Yapay zekâ analizi ve
            müşteri cevabı
          </p>
        </div>
      </header>

      <div className="detay-grid">
        <section className="detay-kart">
          <h2>
            Talep Bilgileri
          </h2>

          <p>Başlık</p>

          <strong>
            {talep.talep_baslik}
          </strong>

          <p>Takip No</p>

          <strong>
            {talep.talep_takip_no}
          </strong>

          <p>Durum</p>

          <strong>
            {talep.talep_durum}
          </strong>

          <p>Öncelik</p>

          <strong>
            {
              talep.yz_oncelik_seviyesi
            }
          </strong>
        </section>

        <section className="detay-kart">
          <h2>Müşteri</h2>

          <p>
            {
              talep.talep_gonderen_ad_soyad
            }
          </p>

          <p>
            {
              talep.talep_gonderen_eposta
            }
          </p>

          <br />

          <p>
            <strong>
              Kategori:
            </strong>{" "}
            {talep.kategori_ad}
          </p>

          <p>
            <strong>
              Departman:
            </strong>{" "}
            {
              talep.kategori_departman
            }
          </p>
        </section>
      </div>

      <section className="detay-kart">
        <h2>
          Müşteri Talebi
        </h2>

        <p>
          {
            talep.talep_ham_icerik
          }
        </p>
      </section>

      <section className="detay-kart">
        <h2>
          Yapay Zekâ Analizi
        </h2>

        <p>
          {talep.yz_ozet}
        </p>

        <br />

        <p>
          <strong>
            Duygu Durumu:
          </strong>{" "}
          {
            talep.yz_duygu_durumu
          }
        </p>

        <p>
          <strong>
            Güven Skoru:
          </strong>{" "}
          {Math.round(
            talep.yz_guven_skoru *
              100
          )}
          %
        </p>

        <br />

        <p>
          <strong>
            Yapay Zekâ Çözüm
            Önerisi
          </strong>
        </p>

        <p>
          {
            talep.yz_cozum_onerisi
          }
        </p>
      </section>

      <section className="detay-kart">
        <h2>
          Yapay Zekâ'nın
          Hazırladığı Cevap
        </h2>

        <textarea
          rows={10}
          value={yanitMetni}
          onChange={(event) =>
            setYanitMetni(
              event.target.value
            )
          }
        />

        <button
          className="gonder-butonu"
          onClick={gonder}
        >
          Müşteriye Gönder
        </button>
      </section>
    </div>
  );
}

export default PersonelTalepDetay;