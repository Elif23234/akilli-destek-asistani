import { Link } from "react-router-dom";
import "./AnaSayfa.css";

function AnaSayfa() {
  function yoneticiGirisineGit() {
    sessionStorage.removeItem("admin_token");
  }

  function personelGirisineGit() {
    sessionStorage.removeItem("personel_token");
    sessionStorage.removeItem("personel_bilgisi");
  }

  return (
    <div className="ana-sayfa">
      {/* Arka plandaki dekoratif şekiller */}
      <div className="dekor-sekil dekor-sekil-bir"></div>
      <div className="dekor-sekil dekor-sekil-iki"></div>
      <div className="dekor-sekil dekor-sekil-uc"></div>

      <main className="ana-sayfa-icerik">
        <header className="ana-sayfa-baslik">
          <span className="ust-rozet">
            ✨ Akıllı müşteri destek sistemi
          </span>

          <h1>
            Size nasıl yardımcı
            <span> olabiliriz?</span>
          </h1>

          <p>
            Destek talebinizi oluşturun, yönetici
            paneline erişin veya personel hesabınızla
            size atanmış talepleri yönetin.
          </p>
        </header>

        <section className="ana-sayfa-kartlar">
          <article className="secim-karti talep-karti">
            <div className="kart-ust-alan">
              <div className="secim-ikonu talep-ikonu">
                📝
              </div>

              <span className="kart-etiketi">
                Müşteri
              </span>
            </div>

            <h2>Yeni Talep Oluştur</h2>

            <p>
              Şikâyet, öneri veya destek ihtiyacınızı
              birkaç adımda bize iletin.
            </p>

            <ul className="kart-ozellikleri">
              <li>✓ Hızlı başvuru</li>
              <li>✓ Yapay zekâ analizi</li>
              <li>✓ Kolay takip</li>
            </ul>

            <Link
              to="/destek-talebi"
              className="secim-butonu talep-butonu"
            >
              Talep Oluştur
              <span>→</span>
            </Link>
          </article>

          <article className="secim-karti admin-karti">
            <div className="kart-ust-alan">
              <div className="secim-ikonu admin-ikonu">
                🔐
              </div>

              <span className="kart-etiketi">
                Yönetici
              </span>
            </div>

            <h2>Yönetici Paneli</h2>

            <p>
              Gelen talepleri görüntüleyin, analizleri
              inceleyin ve müşteri süreçlerini yönetin.
            </p>

            <ul className="kart-ozellikleri">
              <li>✓ Talep yönetimi</li>
              <li>✓ Öncelik analizi</li>
              <li>✓ Detaylı raporlar</li>
            </ul>

            <Link
              to="/admin-giris"
              onClick={yoneticiGirisineGit}
              className="secim-butonu admin-butonu"
            >
              Yönetici Paneline Geç
              <span>→</span>
            </Link>
          </article>

          <article className="secim-karti personel-karti">
            <div className="kart-ust-alan">
              <div className="secim-ikonu personel-ikonu">
                👨‍💻
              </div>

              <span className="kart-etiketi">
                Personel
              </span>
            </div>

            <h2>Personel Paneli</h2>

            <p>
              Size otomatik olarak atanmış destek
              taleplerini inceleyin ve müşterilere
              yanıt verin.
            </p>

            <ul className="kart-ozellikleri">
              <li>✓ Atanan talepler</li>
              <li>✓ Müşteriye yanıt gönderme</li>
              <li>✓ Talep durumu yönetimi</li>
            </ul>

            <Link
              to="/personel-giris"
              onClick={personelGirisineGit}
              className="secim-butonu personel-butonu"
            >
              Personel Paneline Geç
              <span>→</span>
            </Link>
          </article>
        </section>

        <footer className="ana-sayfa-alt-yazi">
          <span>💜</span>
          Talepleriniz güvenli şekilde işlenir.
        </footer>
      </main>
    </div>
  );
}

export default AnaSayfa;