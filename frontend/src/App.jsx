import {
  Route,
  Routes,
} from "react-router-dom";

import "./styles/Layout.css";

import ProtectedRoute
  from "./components/ProtectedRoute";

import PersonelProtectedRoute
  from "./components/PersonelProtectedRoute";

import AdminLayout
  from "./layouts/AdminLayout";

import AnaSayfa
  from "./pages/AnaSayfa";

import AdminGiris
  from "./pages/AdminGiris";

import PersonelGiris
  from "./pages/PersonelGiris";

import Dashboard
  from "./pages/Dashboard";

import MusteriOnayi
  from "./pages/MusteriOnayi";

import SikayetFormu
  from "./pages/SikayetFormu";

import TalepDetay
  from "./pages/TalepDetay";

import TalepListesi
  from "./pages/TalepListesi";

import PersonelPaneli
  from "./pages/PersonelPaneli";

import PersonelTalepDetay
  from "./pages/PersonelTalepDetay";

import PersonelProfil
  from "./pages/PersonelProfil";

function App() {
  return (
    <Routes>
      {/* Herkese açık ana sayfa */}
      <Route
        path="/"
        element={<AnaSayfa />}
      />

      {/* Herkese açık müşteri sayfaları */}
      <Route
        path="/destek-talebi"
        element={<SikayetFormu />}
      />

      <Route
        path="/sikayet-olustur"
        element={<SikayetFormu />}
      />

      <Route
        path="/musteri-onayi"
        element={<MusteriOnayi />}
      />

      {/* Yönetici giriş ekranı */}
      <Route
        path="/admin-giris"
        element={<AdminGiris />}
      />

      {/* Personel giriş ekranı */}
      <Route
        path="/personel-giris"
        element={<PersonelGiris />}
      />

      {/* Korunan yönetici sayfaları */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AdminLayout />}>
          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/talepler"
            element={<TalepListesi />}
          />

          <Route
            path="/talep-detay/:takipNo"
            element={<TalepDetay />}
          />
        </Route>
      </Route>

      {/* Korunan personel sayfaları */}
      <Route
        element={<PersonelProtectedRoute />}
      >
        <Route
          path="/personel-paneli"
          element={<PersonelPaneli />}
        />

        <Route
          path="/personel-talep/:talepId"
          element={<PersonelTalepDetay />}
        />

        <Route
          path="/personel-profil"
          element={<PersonelProfil />}
        />
      </Route>
    </Routes>
  );
}

export default App;