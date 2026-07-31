import {
  Navigate,
  Outlet,
  useLocation,
} from "react-router-dom";

function ProtectedRoute() {
  const location = useLocation();

  const token = sessionStorage.getItem("admin_token");

  if (!token) {
    return (
      <Navigate
        to="/admin-giris"
        replace
        state={{
          geldigiSayfa: location.pathname,
        }}
      />
    );
  }

  return <Outlet />;
}

export default ProtectedRoute;