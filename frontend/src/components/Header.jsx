import "../styles/Header.css";

function Header() {
  return (
    <header className="header">
      <div className="header-sol-alan">
        <div className="header-logo">
          ✨
        </div>

        <div className="header-baslik-alani">
          <h1>
            Akıllı Destek
            <span> Asistanı</span>
          </h1>

          <p>
            Yönetim Paneli
          </p>
        </div>
      </div>

      <div className="header-sag-alan">
        <div className="header-durum">
          <span className="header-durum-noktasi"></span>

          <div>
            <strong>Sistem Aktif</strong>
            <small>AI destek hizmeti çalışıyor</small>
          </div>
        </div>

        <div className="header-profil">
          <span>👤</span>

          <div>
            <strong>Yönetici</strong>
            <small>Admin hesabı</small>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;