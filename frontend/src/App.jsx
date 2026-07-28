import { Routes, Route } from "react-router-dom";

import "./styles/Layout.css";

import Header from "./components/Header";
import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import TalepListesi from "./pages/TalepListesi";
import TalepDetay from "./pages/TalepDetay";

function App() {
  return (
    <div className="app">
      <Header />

      <div className="main-layout">
        <Sidebar />

        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/talepler" element={<TalepListesi />} />

            <Route
              path="/talep-detay/:takipNo"
              element={<TalepDetay />}
            />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;