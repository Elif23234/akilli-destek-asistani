import { Outlet } from "react-router-dom";

import Header from "../components/Header";
import Sidebar from "../components/Sidebar";

function AdminLayout() {
  return (
    <div className="app">
      <Header />

      <div className="main-layout">
        <Sidebar />

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AdminLayout;