import logo from "../assets/logo.png";

import 
{ useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    try {
      setLoading(true);
      const response = await api.post("/auth/login", { email, password });
      login(response.data.access_token);
      navigate("/documents");
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Invalid email or password");
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
                      className="w-9 h-9 object-contain"
                      style={{ width: "150px", height: "150px" }}
                    />
        </div>

        {/* Hero content */}
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
            AI-Powered Platform
          </div>

          <h1 style={{
            fontSize: "48px", fontWeight: 800, lineHeight: 1.15,
            marginBottom: "20px", color: "white",
          }}>
            Chat with your<br />
            <span style={{ background: "linear-gradient(135deg, #ffffff 30%, #a8c4ff 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              documents using AI
            </span>
          </h1>

          <p style={{ fontSize: "17px", lineHeight: 1.7, color: "rgba(255,255,255,0.70)", marginBottom: "36px", fontWeight: 400 }}>
            Upload PDFs, Word files, presentations and instantly search,
            analyze, and ask questions using Retrieval-Augmented Generation.
          </p>

        
        </div>

        {/* Footer */}
        <div style={{ position: "relative", zIndex: 1, fontSize: "13px", color: "rgba(255,255,255,0.35)", fontWeight: 500 }}>
          © 2026 ITGATE AI Platform · All rights reserved
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

          {/* Header */}
          <div style={{ marginBottom: "36px" }}>
            <h2 style={{ fontSize: "30px", fontWeight: 800, color: "var(--dark)", marginBottom: "8px" }}>
              Welcome back
            </h2>
            <p style={{ fontSize: "15px", color: "var(--body-color)", fontWeight: 400 }}>
              Sign in to access your AI document workspace.
            </p>
          </div>

          {/* Error */}
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

          {/* Form */}
          <form onSubmit={handleLogin} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>

            <div>
              <label className="label-itgate" htmlFor="login-email">Email Address</label>
              <input
                id="login-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="input-itgate"
              />
            </div>

            <div>
              <label className="label-itgate" htmlFor="login-password">Password</label>
              <div style={{ position: "relative" }}>
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="input-itgate"
                  style={{ paddingRight: "56px" }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: "absolute", right: "16px", top: "50%",
                    transform: "translateY(-50%)",
                    background: "none", border: "none", cursor: "pointer",
                    color: "var(--body-color)", fontSize: "12px", fontWeight: 600,
                    letterSpacing: "0.5px", textTransform: "uppercase",
                    padding: "4px",
                  }}
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>

            <button
              id="login-submit-btn"
              type="submit"
              disabled={loading}
              className="btn-itgate btn-itgate-gradient"
              style={{ width: "100%", marginTop: "4px", padding: "16px 36px", fontSize: "15px" }}
            >
              {loading ? (
                <>
                  <span className="itgate-spinner" />
                  Signing In...
                </>
              ) : "Sign In"}
            </button>
          </form>

          {/* Register link */}
          <div style={{ marginTop: "28px", textAlign: "center" }}>
            <p style={{ fontSize: "14px", color: "var(--body-color)" }}>
              Don't have an account?{" "}
              <Link
                to="/register"
                style={{ color: "var(--primary)", fontWeight: 700 }}
              >
                Create Account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
