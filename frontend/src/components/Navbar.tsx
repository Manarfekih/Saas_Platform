import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { userEmail } = useAuth();
  const navigate = useNavigate();

  const initials = userEmail ? userEmail[0].toUpperCase() : "?";

  return (
    <header className="itgate-navbar">

      {/* Left: Platform Title */}
      <div className="itgate-navbar-title">
        AI Document Intelligence Platform
      </div>

      {/* Right Controls */}
      <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>

        {/* Upload Button */}
        <button
          id="navbar-upload-btn"
          onClick={() => navigate("/upload")}
          className="btn-itgate btn-itgate-sm"
          style={{ gap: "7px" }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Upload
        </button>

        {/* Divider */}
        <div style={{ width: "1px", height: "32px", background: "var(--border-color)" }} />

        {/* User Avatar */}
        <div
          id="navbar-user-avatar"
          style={{
            width: "38px",
            height: "38px",
            borderRadius: "50%",
            background: "var(--gradient-primary)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 700,
            fontSize: "14px",
            color: "white",
            cursor: "default",
            flexShrink: 0,
            boxShadow: "0 2px 8px rgba(0,68,235,0.25)",
            letterSpacing: "0.5px",
          }}
          title={userEmail || ""}
        >
          {initials}
        </div>

      </div>
    </header>
  );
}
