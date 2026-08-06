import { useState } from "react";
import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import { personelGirisi } from "../services/api";
import "./AdminGiris.css";

function PersonelGiris() {
  const navigate = useNavigate();
  const location = useLocation();

  const [eposta, setEposta] =
    useState("");

  const [sifre, setSifre] =
    useState("");

  const [hata, setHata] =
    useState("");

  const [yukleniyor, setYukleniyor] =
    useState(false);

  async function girisYap(event) {
    event.preventDefault();

    setHata("");

    if (!eposta.trim() || !sifre) {
      setHata(
        "E-posta ve şifre boş bırakılamaz."
      );
      return;
    }

    try {
      setYukleniyor(true);

      const sonuc = await personelGirisi(
        eposta.trim(),
        sifre
      );

      sessionStorage.setItem(
        "personel_token",
        sonuc.access_token
      );

      sessionStorage.setItem(
        "personel_bilgisi",
        JSON.stringify(
          sonuc.personel
        )
      );

      const hedefSayfa =
        location.state?.geldigiSayfa ||
        "/personel-paneli";

      navigate(
        hedefSayfa,
        {
          replace: true,
        }
      );
    } catch (error) {
      setHata(
        error.message
      );
    } finally {
      setYukleniyor(false);
    }
  }

  return (
    <div className="admin-giris-sayfasi">
      <div className="admin-giris-karti">
        <div className="admin-giris-baslik">
          <h1>Personel Girişi</h1>

          <p>
            Size atanmış destek taleplerini
            görüntülemek için giriş yapın.
          </p>
        </div>

        <form
          className="admin-giris-formu"
          onSubmit={girisYap}
        >
          <div className="admin-giris-alani">
            <label htmlFor="eposta">
              E-posta
            </label>

            <input
              id="eposta"
              type="email"
              value={eposta}
              onChange={(event) =>
                setEposta(
                  event.target.value
                )
              }
              autoComplete="email"
              placeholder="E-posta adresinizi girin"
            />
          </div>

          <div className="admin-giris-alani">
            <label htmlFor="sifre">
              Şifre
            </label>

            <input
              id="sifre"
              type="password"
              value={sifre}
              onChange={(event) =>
                setSifre(
                  event.target.value
                )
              }
              autoComplete="current-password"
              placeholder="Şifrenizi girin"
            />
          </div>

          {hata && (
            <div className="admin-giris-hata">
              {hata}
            </div>
          )}

          <button
            type="submit"
            disabled={yukleniyor}
          >
            {yukleniyor
              ? "Giriş yapılıyor..."
              : "Giriş Yap"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default PersonelGiris;