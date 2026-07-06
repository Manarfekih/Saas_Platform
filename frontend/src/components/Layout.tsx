import { Outlet, Navigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import Footer from "./Footer";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { token } = useAuth();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="itgate-layout">
      <Sidebar />
      <div className="itgate-main">
        <Navbar />
        <main className="itgate-content">
          <Outlet />
        </main>
        <Footer />
      </div>
    </div>
  );
}

