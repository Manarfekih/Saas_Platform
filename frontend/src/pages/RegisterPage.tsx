import logo from "../assets/logo.png";
import 
{ useState } from "react";
import api from "../api/auth";
import { Link, useNavigate } from "react-router-dom";

export default function RegisterPage() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    try {
      setLoading(true);
      await api.post("/auth/register", { name, email, password });
      navigate("/login");
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Registration failed. Try a different email.");
    } finally {
      setLoading(false);
    }
  };

 

  return (
    <div style={{ minHeight: "100vh", display: "flex", fontFamily: "var(--font-body)" }}>

      {/* ── LEFT PANEL ── */}
      <div
        className="itgate-auth-left"
        style={{
          width: "50%",
          padding: "60px 64px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          color: "white",
        }}
      >
        {/* Blobs */}
        <div className="itgate-auth-left-blob-1" />
        <div className="itgate-auth-left-blob-2" />
        <div className="itgate-auth-left-blob-3" />

        {/* Logo */}
        <div className="animate-fadeInDown" style={{ position: "relative", zIndex: 1, display: "flex", alignItems: "center", gap: "14px" }}>
          <img
            src={logo}
            alt="Logo"
            className="w-9 h-9 object-contain"
            style={{ width: "150px", height: "150px" }}
          />
        </div>

        {/* Content */}
        <div className="animate-fadeInUp" style={{ position: "relative", zIndex: 1, maxWidth: "480px" }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: "8px",
            padding: "6px 16px",
            background: "rgba(255,255,255,0.10)",
            border: "1px solid rgba(255,255,255,0.18)",
            borderRadius: "50px",
            fontSize: "12px", fontWeight: 600, letterSpacing: "0.8px",
            textTransform: "uppercase", marginBottom: "24px",
            color: "rgba(255,255,255,0.80)",
          }}>
            <span style={{ width: "7px", height: "7px", borderRadius: "50%", background: "#6EE89A", display: "inline-block" }} />
            Get Started Free
          </div>

          <h1 style={{
            fontSize: "46px", fontWeight: 800, lineHeight: 1.15,
            marginBottom: "20px", color: "white",
          }}>
            Start processing<br />
            <span style={{ background: "linear-gradient(135deg, #ffffff 30%, #a8c4ff 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              documents in seconds.
            </span>
          </h1>

          <p style={{ fontSize: "17px", lineHeight: 1.7, color: "rgba(255,255,255,0.70)", marginBottom: "40px", fontWeight: 400 }}>
            Create an account to upload, structure, and orchestrate automated
            AI workflows on your files.
          </p>

          
        </div>

        {/* Footer */}
        <div style={{ position: "relative", zIndex: 1, fontSize: "13px", color: "rgba(255,255,255,0.35)", fontWeight: 500 }}>
          © 2026 DocuAI Platform · All rights reserved
        </div>
      </div>

      {/* ── RIGHT PANEL ── */}
      <div style={{
        width: "50%",
        background: "white",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 64px",
      }}>
        <div style={{ width: "100%", maxWidth: "420px" }} className="animate-fadeIn">

          <div style={{ marginBottom: "36px" }}>
            <h2 style={{ fontSize: "30px", fontWeight: 800, color: "var(--dark)", marginBottom: "8px" }}>
              Create Account
            </h2>
            <p style={{ fontSize: "15px", color: "var(--body-color)", fontWeight: 400 }}>
              Set up your workspace credentials below.
            </p>
          </div>

          {errorMsg && (
            <div style={{
              padding: "12px 16px",
              background: "rgba(242,111,77,0.08)",
              border: "1px solid rgba(242,111,77,0.25)",
              borderRadius: "var(--radius-md)",
              color: "var(--danger)",
              fontSize: "14px",
              fontWeight: 500,
              marginBottom: "24px",
              display: "flex", alignItems: "center", gap: "8px",
            }}>
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleRegister} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>

            <div>
              <label className="label-itgate" htmlFor="register-name">Full Name</label>
              <input
                id="register-name"
                type="text"
                required
                className="input-itgate"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            <div>
              <label className="label-itgate" htmlFor="register-email">Email Address</label>
              <input
                id="register-email"
                type="email"
                required
                className="input-itgate"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div>
              <label className="label-itgate" htmlFor="register-password">Password</label>
              <input
                id="register-password"
                type="password"
                required
                className="input-itgate"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button
              id="register-submit-btn"
              type="submit"
              disabled={loading}
              className="btn-itgate btn-itgate-gradient"
              style={{ width: "100%", marginTop: "4px", padding: "16px 36px", fontSize: "15px" }}
            >
              {loading ? (
                <>
                  <span className="itgate-spinner" />
                  Creating Account...
                </>
              ) : "Create Account"}
            </button>
          </form>

          <div style={{ marginTop: "28px", textAlign: "center" }}>
            <p style={{ fontSize: "14px", color: "var(--body-color)" }}>
              Already have an account?{" "}
              <Link to="/login" style={{ color: "var(--primary)", fontWeight: 700 }}>
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}