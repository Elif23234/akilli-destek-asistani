import { useState } from "react";
import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import { adminGirisi } from "../services/api";
import "./AdminGiris.css";

function AdminGiris() {
  const navigate = useNavigate();
  const location = useLocation();

  const [kullaniciAdi, setKullaniciAdi] =
    useState("");

  const [sifre, setSifre] = useState("");
  const [hata, setHata] = useState("");
  const [yukleniyor, setYukleniyor] =
    useState(false);

  async function girisYap(event) {
    event.preventDefault();

    setHata("");

    if (!kullaniciAdi.trim() || !sifre) {
      setHata(
        "Kullanıcı adı ve şifre boş bırakılamaz."
      );
      return;
    }

    try {
      setYukleniyor(true);

      const sonuc = await adminGirisi(
        kullaniciAdi.trim(),
        sifre
      );

      sessionStorage.setItem(
        "admin_token",
        sonuc.access_token
      );

      const hedefSayfa =
        location.state?.geldigiSayfa ||
        "/dashboard";

      navigate(hedefSayfa, {
        replace: true,
      });
    } catch (error) {
      setHata(error.message);
    } finally {
      setYukleniyor(false);
    }
  }

  return (
    <div className="admin-giris-sayfasi">
      <div className="admin-giris-karti">
        <div className="admin-giris-baslik">
          <h1>Yönetici Girişi</h1>

          <p>
            Destek taleplerini görüntülemek için
            giriş yapın.
          </p>
        </div>

        <form
          className="admin-giris-formu"
          onSubmit={girisYap}
        >
          <div className="admin-giris-alani">
            <label htmlFor="kullaniciAdi">
              Kullanıcı adı
            </label>

            <input
              id="kullaniciAdi"
              type="text"
              value={kullaniciAdi}
              onChange={(event) =>
                setKullaniciAdi(
                  event.target.value
                )
              }
              autoComplete="username"
              placeholder="Kullanıcı adınızı girin"
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
                setSifre(event.target.value)
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

export default AdminGiris;