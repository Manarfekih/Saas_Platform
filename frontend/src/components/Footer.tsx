import logo from "../assets/logo.png";
export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="site-footer">

      {/* ── Marquee Service Strip ─────────────────────────────── */}
      <div className="footer-marquee-wrap">
        <div className="footer-marquee">
          {[
            "AI Document Analysis",
            "Intelligent Extraction",
            "Smart Classification",
            
          ].flatMap((s, i) => [
            <div key={`a-${i}`} className="footer-pill">
              <span className="footer-pill-check">✓</span>
              <span>{s}</span>
            </div>,
            <div key={`b-${i}`} className="footer-pill">
              <span className="footer-pill-check">✓</span>
              <span>{s}</span>
            </div>,
          ])}
        </div>
      </div>

      {/* ── Main Footer Body ──────────────────────────────────── */}
      <div className="footer-body">
        <div className="footer-container">

          {/* Col 1 — Logo + Description */}
          <div className="footer-col ">
            <div className="footer-logo">
  
                  <div className="footer-logo-icon">
                    <img
                      src={logo}
                      className="w-9 h-9 object-contain"
                      style={{ width: "150px", height: "150px" }}
                    />
                  </div>

                  

                </div>

            <p className="footer-brand-desc">
              Our AI-powered document intelligence platform aims to
              transform our document workflows with intelligent extraction,
              classification, and real-time analytics all in one place.
            </p>
          </div>

          {/* Col 2 — Quick Links */}
          <div className="footer-col">
            <h4 className="footer-col-title">Quick Links</h4>
            <ul className="footer-link-list">
              {[
                { label: "Dashboard", href: "/dashboard" },
                { label: "Documents", href: "/documents" },
                { label: "Upload", href: "/upload" },
                
              ].map((l) => (
                <li key={l.label}>
                  <a href={l.href} className="footer-link">
                    <span className="footer-link-arrow">›</span>
                    {l.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Col 3 — Features */}
          <div className="footer-col">
            <h4 className="footer-col-title">Features</h4>
            <ul className="footer-link-list">
              {[
                "AI Document Analysis",
                "Smart Data Extraction",
                "Role-based Access",
              ].map((f) => (
                <li key={f}>
                  <a href="#" className="footer-link">
                    <span className="footer-link-arrow">›</span>
                    {f}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Col 4 — Contact + Social */}
          <div className="footer-col">
            <h4 className="footer-col-title">Get In Touch</h4>
            <ul className="footer-contact-list">
              <li>
                <a href="tel:+1234567890" className="footer-contact-item">
                  <span className="footer-contact-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="15" height="15">
                      <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 8.81a19.79 19.79 0 01-3.07-8.68A2 2 0 012 0h3a2 2 0 012 1.72c.12.96.36 1.9.7 2.81a2 2 0 01-.45 2.11L6.09 7.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.91.34 1.85.58 2.81.7A2 2 0 0122 14.92v2z"/>
                    </svg>
                  </span>
                  +(216) 73 325 001
                </a>
              </li>
              <li>
                <a href="mailto:contact@docintel.ai" className="footer-contact-item">
                  <span className="footer-contact-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="15" height="15">
                      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                      <polyline points="22,6 12,13 2,6"/>
                    </svg>
                  </span>
                  contact@itgate-group.com
                </a>
              </li>
              <li>
                <a href="#" className="footer-contact-item footer-contact-addr">
                  <span className="footer-contact-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="15" height="15">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
                      <circle cx="12" cy="10" r="3"/>
                    </svg>
                  </span>
                  2éme étage B1 . Résidence El Hamd, Rue d'Algérie,
                    Sousse 4011
                </a>
              </li>
            </ul>

            
          </div>

        </div>
      </div>

      {/* ── Bottom Bar ────────────────────────────────────────── */}
      <div className="footer-bottom">
        <div className="footer-container footer-bottom-inner">
          <p className="footer-copyright">
            Copyright © {year} ITGATE AI Platform. All rights reserved.
          </p>
        </div>
      </div>

    </footer>
  );
}
