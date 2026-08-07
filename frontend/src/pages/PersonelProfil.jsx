import "./PersonelProfil.css";

import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  getPersonelProfili,
  personelSifreDegistir,
} from "../services/api";

function PersonelProfil() {
  const navigate = useNavigate();

  const [profil, setProfil] =
    useState(null);

  const [yukleniyor, setYukleniyor] =
    useState(true);

  const [hata, setHata] =
    useState("");

  const [mevcutSifre, setMevcutSifre] =
    useState("");

  const [yeniSifre, setYeniSifre] =
    useState("");

  const [
    yeniSifreTekrar,
    setYeniSifreTekrar,
  ] = useState("");

  const [
    sifreDegistiriliyor,
    setSifreDegistiriliyor,
  ] = useState(false);

  const [mesaj, setMesaj] =
    useState("");

  const [sifreHatasi, setSifreHatasi] =
    useState("");

  useEffect(() => {
    async function profiliGetir() {
      try {
        const sonuc =
          await getPersonelProfili();

        setProfil(
          sonuc.veri || null
        );
      } catch (error) {
        setHata(error.message);
      } finally {
        setYukleniyor(false);
      }
    }

    profiliGetir();
  }, []);

  async function sifreyiDegistir(
    event
  ) {
    event.preventDefault();

    setMesaj("");
    setSifreHatasi("");

    if (!mevcutSifre.trim()) {
      setSifreHatasi(
        "Mevcut şifrenizi girin."
      );
      return;
    }

    if (yeniSifre.length < 8) {
      setSifreHatasi(
        "Yeni şifre en az 8 karakter olmalıdır."
      );
      return;
    }

    if (
      yeniSifre !==
      yeniSifreTekrar
    ) {
      setSifreHatasi(
        "Yeni şifreler eşleşmiyor."
      );
      return;
    }

    try {
      setSifreDegistiriliyor(true);

      const sonuc =
        await personelSifreDegistir({
          mevcutSifre,
          yeniSifre,
        });

      setMesaj(
        sonuc.mesaj ||
          "Şifreniz başarıyla değiştirildi."
      );

      setMevcutSifre("");
      setYeniSifre("");
      setYeniSifreTekrar("");
    } catch (error) {
      setSifreHatasi(
        error.message
      );
    } finally {
      setSifreDegistiriliyor(false);
    }
  }

  if (yukleniyor) {
    return (
      <div className="profil-durum">
        Profil yükleniyor...
      </div>
    );
  }

  if (hata) {
    return (
      <div className="profil-durum hata">
        {hata}
      </div>
    );
  }

  return (
    <div className="personel-profil-sayfasi">
      <header className="profil-ust">
        <button
          type="button"
          onClick={() =>
            navigate(
              "/personel-paneli"
            )
          }
        >
          ← Panele Dön
        </button>

        <div>
          <span>PERSONEL HESABI</span>
          <h1>Profilim</h1>

          <p>
            Hesap bilgilerinizi ve iş
            istatistiklerinizi görüntüleyin.
          </p>
        </div>
      </header>

      <section className="profil-kimlik-karti">
        <div className="profil-buyuk-avatar">
          {profil?.kullanici_ad_soyad
            ?.charAt(0)
            .toLocaleUpperCase("tr-TR") ||
            "P"}
        </div>

        <div>
          <h2>
            {profil?.kullanici_ad_soyad}
          </h2>

          <p>
            {profil?.kullanici_eposta}
          </p>

          <span>
            {profil?.kullanici_departman ||
              "Departman belirtilmemiş"}
          </span>
        </div>
      </section>

      <section className="profil-istatistikleri">
        <article>
          <strong>
            {profil?.toplam_atanan_talep ||
              0}
          </strong>
          <span>Toplam Talep</span>
        </article>

        <article>
          <strong>
            {profil?.aktif_talep_sayisi ||
              0}
          </strong>
          <span>Aktif Talep</span>
        </article>

        <article>
          <strong>
            {profil?.toplam_cozulen_talep ||
              0}
          </strong>
          <span>Çözülen Talep</span>
        </article>

        <article>
          <strong>
            {profil?.bugun_cozulen_talep ||
              0}
          </strong>
          <span>Bugün Çözülen</span>
        </article>
      </section>

      <section className="profil-alt-grid">
        <article className="profil-bilgi-karti">
          <h2>Hesap Bilgileri</h2>

          <div>
            <span>Ad Soyad</span>
            <strong>
              {profil?.kullanici_ad_soyad}
            </strong>
          </div>

          <div>
            <span>E-posta</span>
            <strong>
              {profil?.kullanici_eposta}
            </strong>
          </div>

          <div>
            <span>Departman</span>
            <strong>
              {profil?.kullanici_departman ||
                "Belirtilmemiş"}
            </strong>
          </div>

          <div>
            <span>Rol</span>
            <strong>Destek Personeli</strong>
          </div>
        </article>

        <form
          className="profil-sifre-karti"
          onSubmit={sifreyiDegistir}
        >
          <h2>Şifre Değiştir</h2>

          <label>
            Mevcut Şifre
            <input
              type="password"
              value={mevcutSifre}
              onChange={(event) =>
                setMevcutSifre(
                  event.target.value
                )
              }
            />
          </label>

          <label>
            Yeni Şifre
            <input
              type="password"
              value={yeniSifre}
              onChange={(event) =>
                setYeniSifre(
                  event.target.value
                )
              }
            />
          </label>

          <label>
            Yeni Şifre Tekrar
            <input
              type="password"
              value={yeniSifreTekrar}
              onChange={(event) =>
                setYeniSifreTekrar(
                  event.target.value
                )
              }
            />
          </label>

          {mesaj && (
            <p className="profil-mesaj">
              {mesaj}
            </p>
          )}

          {sifreHatasi && (
            <p className="profil-hata">
              {sifreHatasi}
            </p>
          )}

          <button
            type="submit"
            disabled={sifreDegistiriliyor}
          >
            {sifreDegistiriliyor
              ? "Güncelleniyor..."
              : "Şifreyi Güncelle"}
          </button>
        </form>
      </section>
    </div>
  );
}

export default PersonelProfil;