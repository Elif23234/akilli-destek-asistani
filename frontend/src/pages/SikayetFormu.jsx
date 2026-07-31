import { useState } from "react";
import { Link } from "react-router-dom";

import { yeniTalepOlustur } from "../services/api";

import "./SikayetFormu.css";

function SikayetFormu() {
  const [formBilgileri, setFormBilgileri] =
    useState({
      ad_soyad: "",
      eposta: "",
      baslik: "",
      icerik: "",
    });

  const [gonderiliyor, setGonderiliyor] =
    useState(false);

  const [basariMesaji, setBasariMesaji] =
    useState("");

  const [hataMesaji, setHataMesaji] =
    useState("");

  function alanDegistir(event) {
    const { name, value } = event.target;

    setFormBilgileri({
      ...formBilgileri,
      [name]: value,
    });
  }

  async function formuGonder(event) {
    event.preventDefault();

    setBasariMesaji("");
    setHataMesaji("");

    if (
      !formBilgileri.ad_soyad.trim() ||
      !formBilgileri.eposta.trim() ||
      !formBilgileri.baslik.trim() ||
      !formBilgileri.icerik.trim()
    ) {
      setHataMesaji(
        "Lütfen bütün alanları doldurunuz."
      );

      return;
    }

    try {
      setGonderiliyor(true);

      const sonuc = await yeniTalepOlustur({
        ad_soyad:
          formBilgileri.ad_soyad.trim(),

        eposta:
          formBilgileri.eposta.trim(),

        baslik:
          formBilgileri.baslik.trim(),

        icerik:
          formBilgileri.icerik.trim(),

        kaynak: "web",
      });

      if (sonuc.durum === "reddedildi") {
        setHataMesaji(sonuc.mesaj);

        return;
      }

      setBasariMesaji(
        `${sonuc.mesaj} Talep numaranız: ${sonuc.talep_id}`
      );

      setFormBilgileri({
        ad_soyad: "",
        eposta: "",
        baslik: "",
        icerik: "",
      });
    } catch (error) {
      setHataMesaji(error.message);
    } finally {
      setGonderiliyor(false);
    }
  }

  return (
    <section className="sikayet-sayfasi">
      <div className="sikayet-dekor sikayet-dekor-bir"></div>
      <div className="sikayet-dekor sikayet-dekor-iki"></div>
      <div className="sikayet-dekor sikayet-dekor-uc"></div>

      <div className="sikayet-ust-menu">
        <Link
          to="/"
          className="sikayet-geri-linki"
        >
          <span>←</span>
          Ana sayfaya dön
        </Link>
      </div>

      <div className="sikayet-karti">
        <aside className="sikayet-bilgi-alani">
          <span className="sikayet-rozet">
            ✨ Akıllı destek sistemi
          </span>

          <div className="sikayet-buyuk-ikon">
            💬
          </div>

          <h1>
            Sorununuzu birlikte
            <span> çözelim.</span>
          </h1>

          <p className="sikayet-aciklama">
            Destek talebinizi birkaç adımda
            oluşturabilirsiniz. Talebiniz yapay
            zekâ tarafından analiz edilerek ilgili
            destek ekibine yönlendirilir.
          </p>

          <div className="sikayet-adimlari">
            <div className="sikayet-adimi">
              <span className="adim-numarasi">
                1
              </span>

              <div>
                <strong>Bilgilerinizi girin</strong>
                <p>
                  İletişim ve talep bilgilerinizi
                  doldurun.
                </p>
              </div>
            </div>

            <div className="sikayet-adimi">
              <span className="adim-numarasi">
                2
              </span>

              <div>
                <strong>Yapay zekâ analizi</strong>
                <p>
                  Talebinizin konusu ve önceliği
                  belirlenir.
                </p>
              </div>
            </div>

            <div className="sikayet-adimi">
              <span className="adim-numarasi">
                3
              </span>

              <div>
                <strong>Doğru ekibe yönlendirme</strong>
                <p>
                  Talebiniz ilgili destek ekibine
                  iletilir.
                </p>
              </div>
            </div>
          </div>

          <div className="sikayet-guvenlik-notu">
            <span>🔒</span>

            <p>
              Bilgileriniz güvenli şekilde
              işlenmektedir.
            </p>
          </div>
        </aside>

        <main className="sikayet-form-alani">
          <div className="form-baslik-alani">
            <span className="form-kucuk-etiket">
              Destek Formu
            </span>

            <h2>Yeni Talep Oluştur</h2>

            <p>
              Size daha hızlı yardımcı olabilmemiz
              için alanları eksiksiz doldurun.
            </p>
          </div>

          <form
            className="sikayet-formu"
            onSubmit={formuGonder}
          >
            <div className="form-satiri">
              <div className="form-alani">
                <label htmlFor="ad_soyad">
                  <span>👤</span>
                  Ad Soyad
                </label>

                <input
                  id="ad_soyad"
                  name="ad_soyad"
                  type="text"
                  value={formBilgileri.ad_soyad}
                  onChange={alanDegistir}
                  placeholder="Adınızı ve soyadınızı girin"
                  disabled={gonderiliyor}
                />
              </div>

              <div className="form-alani">
                <label htmlFor="eposta">
                  <span>✉️</span>
                  E-posta
                </label>

                <input
                  id="eposta"
                  name="eposta"
                  type="email"
                  value={formBilgileri.eposta}
                  onChange={alanDegistir}
                  placeholder="ornek@email.com"
                  disabled={gonderiliyor}
                />
              </div>
            </div>

            <div className="form-alani">
              <label htmlFor="baslik">
                <span>🏷️</span>
                Talep Başlığı
              </label>

              <input
                id="baslik"
                name="baslik"
                type="text"
                value={formBilgileri.baslik}
                onChange={alanDegistir}
                placeholder="Probleminizi kısaca yazın"
                disabled={gonderiliyor}
              />
            </div>

            <div className="form-alani">
              <div className="textarea-baslik">
                <label htmlFor="icerik">
                  <span>📝</span>
                  Talep Açıklaması
                </label>

                <span className="karakter-sayaci">
                  {formBilgileri.icerik.length}/1500
                </span>
              </div>

              <textarea
                id="icerik"
                name="icerik"
                rows="6"
                maxLength="1500"
                value={formBilgileri.icerik}
                onChange={alanDegistir}
                placeholder="Yaşadığınız problemi ayrıntılı olarak açıklayın..."
                disabled={gonderiliyor}
              />
            </div>

            {hataMesaji && (
              <div
                className="form-mesaji hata-mesaji"
                role="alert"
              >
                <span>⚠️</span>
                {hataMesaji}
              </div>
            )}

            {basariMesaji && (
              <div
                className="form-mesaji basari-mesaji"
                role="status"
              >
                <span>✅</span>
                {basariMesaji}
              </div>
            )}

            <button
              className="talep-gonder-butonu"
              type="submit"
              disabled={gonderiliyor}
            >
              <span>
                {gonderiliyor
                  ? "Talebiniz gönderiliyor..."
                  : "Talebi Gönder"}
              </span>

              <span className="buton-oku">
                {gonderiliyor ? "⏳" : "→"}
              </span>
            </button>
          </form>
        </main>
      </div>
    </section>
  );
}

export default SikayetFormu;