import { NavLink } from "react-router-dom";
import "../styles/Sidebar.css";

function Sidebar() {
  function linkSinifi({ isActive }) {
    if (isActive) {
      return "sidebar-link sidebar-link-aktif";
    }

    return "sidebar-link";
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-marka">
        <div className="sidebar-logo">
          ✨
        </div>

        <div>
          <strong>Destek Merkezi</strong>
          <span>Yönetici Paneli</span>
        </div>
      </div>

      <div className="sidebar-ayirici"></div>

      <span className="sidebar-menu-basligi">
        Yönetim
      </span>

      <nav className="sidebar-menu">
        <ul>
          <li>
            <NavLink
              to="/dashboard"
              className={linkSinifi}
            >
              <span className="sidebar-link-ikonu">
                🏠
              </span>

              <span className="sidebar-link-metni">
                Dashboard
              </span>

              <span className="sidebar-link-oku">
                →
              </span>
            </NavLink>
          </li>

          <li>
            <NavLink
              to="/talepler"
              className={linkSinifi}
            >
              <span className="sidebar-link-ikonu">
                📋
              </span>

              <span className="sidebar-link-metni">
                Talepler
              </span>

              <span className="sidebar-link-oku">
                →
              </span>
            </NavLink>
          </li>
        </ul>
      </nav>

      <div className="sidebar-alt-bolum">
        <div className="sidebar-bilgi-karti">
          <span className="sidebar-bilgi-ikonu">
            🤖
          </span>

          <div>
            <strong>AI Destekli</strong>

            <p>
              Talepler yapay zekâ ile analiz edilir.
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;