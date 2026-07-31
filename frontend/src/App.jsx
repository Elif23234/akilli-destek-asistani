import {
  Routes,
  Route,
} from "react-router-dom";

import "./styles/Layout.css";

import ProtectedRoute from "./components/ProtectedRoute";
import AdminLayout from "./layouts/AdminLayout";

import AnaSayfa from "./pages/AnaSayfa";
import AdminGiris from "./pages/AdminGiris";
import Dashboard from "./pages/Dashboard";
import TalepListesi from "./pages/TalepListesi";
import TalepDetay from "./pages/TalepDetay";
import SikayetFormu from "./pages/SikayetFormu";

function App() {
  return (
    <Routes>
      {/* Ana seçim ekranı */}
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

      {/* Yönetici giriş ekranı */}
      <Route
        path="/admin-giris"
        element={<AdminGiris />}
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
    </Routes>
  );
}

export default App;