import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import logo from "../assets/logo.png";

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleSignOut = () => {
    logout();
    navigate("/login");
  };

  const menuItems = [
    {
      name: "Dashboard",
      path: "/dashboard",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4zM14 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2v-4z" />
        </svg>
      ),
    },
    {
      name: "My Documents",
      path: "/documents",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
    },
    {
      name: "IA Assistant",
      path: "/chat/all",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h8M8 14h5m6 7l-3-3H7a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v10a2 2 0 01-.586 1.414L19 21z" />
        </svg>
      ),
    },
    {
      name: "Upload Document",
      path: "/upload",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
      ),
    },
    {
      name: "Profile Settings",
      path: "/profile",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      ),
    },
  ];

  const isDocumentPage =
    location.pathname.startsWith("/documents/") &&
    location.pathname !== "/documents";

  return (
    <aside className="itgate-sidebar">
      {/* TOP SECTION */}
      <div>

        {/* Logo */}
        <div className="itgate-sidebar-logo">
          <img
            src={logo}
            alt="Logo"
            className="w-9 h-9 object-contain"
            style={{ width: "150px", height: "150px" }}
          />
        </div>

        {/* Navigation */}
        <nav className="itgate-sidebar-nav">
          <p className="itgate-sidebar-nav-label">Navigation</p>

          {menuItems.map((item) => {
            const isActive =
              location.pathname === item.path ||
              (item.path === "/documents" && isDocumentPage);

            return (
              <Link
                key={item.name}
                to={item.path}
                className={`itgate-nav-item${isActive ? " active" : ""}`}
              >
                {item.icon}
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* BOTTOM SECTION */}
      <div className="itgate-sidebar-bottom">
        <button
          onClick={handleSignOut}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            width: "100%",
            padding: "11px 14px",
            borderRadius: "var(--radius-pill)",
            fontSize: "14px",
            fontWeight: 500,
            color: "rgba(255,255,255,0.50)",
            background: "none",
            border: "none",
            cursor: "pointer",
            transition: "var(--transition)",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.color = "#F26F4D";
            (e.currentTarget as HTMLButtonElement).style.background =
              "rgba(242,111,77,0.08)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.color =
              "rgba(255,255,255,0.50)";
            (e.currentTarget as HTMLButtonElement).style.background = "none";
          }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
            />
          </svg>
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}