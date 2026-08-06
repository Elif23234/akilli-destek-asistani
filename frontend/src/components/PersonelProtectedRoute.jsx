import {
  Navigate,
  Outlet,
  useLocation,
} from "react-router-dom";

function PersonelProtectedRoute() {
  const location = useLocation();

  const token = sessionStorage.getItem(
    "personel_token"
  );

  if (!token) {
    return (
      <Navigate
        to="/personel-giris"
        replace
        state={{
          geldigiSayfa: location.pathname,
        }}
      />
    );
  }

  return <Outlet />;
}

export default PersonelProtectedRoute;