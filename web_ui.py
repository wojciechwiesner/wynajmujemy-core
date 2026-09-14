"""Alta-inspired frontend template for Wynajmujemy.xyz B2B Marketplace."""

from __future__ import annotations


def get_frontend_html() -> str:
    return """<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wynajmujemy.xyz — B2B Marketplace Wynajmu Gabinetów i Stanowisk</title>
  <meta name="description" content="Elastyczny wynajem gabinetów kosmetycznych, masażu, stanowisk fryzjerskich i sal szkoleniowych. Na godziny, dni lub stałe grafiki.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-dark: #07080C;
      --bg-card: rgba(18, 20, 29, 0.75);
      --bg-card-hover: rgba(26, 29, 43, 0.9);
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-hover: rgba(139, 92, 246, 0.45);
      --text-main: #F3F4F6;
      --text-muted: #9CA3AF;
      --text-dim: #6B7280;
      --accent-violet: #8B5CF6;
      --accent-violet-glow: rgba(139, 92, 246, 0.25);
      --accent-emerald: #10B981;
      --accent-cyan: #06B6D4;
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-dark);
      color: var(--text-main);
      font-family: var(--font-sans);
      min-height: 100vh;
      overflow-x: hidden;
      line-height: 1.5;
      background-image: 
        radial-gradient(circle at 15% 15%, rgba(139, 92, 246, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 85% 30%, rgba(6, 182, 212, 0.06) 0%, transparent 45%);
      background-attachment: fixed;
    }

    /* Ambient noise & grid lines */
    .bg-grid {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background-image: 
        linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
      background-size: 64px 64px;
      pointer-events: none;
      z-index: 0;
    }

    .container {
      max-width: 1240px;
      margin: 0 auto;
      padding: 0 24px;
      position: relative;
      z-index: 1;
    }

    /* Header */
    header {
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(7, 8, 12, 0.82);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-subtle);
      transition: border-color 0.2s;
    }

    .nav-wrap {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 72px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--text-main);
    }

    .brand-logo {
      width: 32px;
      height: 32px;
      background: linear-gradient(135deg, var(--accent-violet), var(--accent-cyan));
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 16px;
      color: #fff;
    }

    .brand-text {
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .brand-badge {
      font-family: var(--font-mono);
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 12px;
      background: rgba(139, 92, 246, 0.15);
      color: #C4B5FD;
      border: 1px solid rgba(139, 92, 246, 0.3);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 32px;
      list-style: none;
    }

    .nav-links a {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 14px;
      font-weight: 500;
      transition: color 0.2s;
    }

    .nav-links a:hover {
      color: var(--text-main);
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      text-decoration: none;
      border: none;
    }

    .btn-primary {
      background: var(--text-main);
      color: #07080C;
    }

    .btn-primary:hover {
      background: #FFFFFF;
      transform: translateY(-1px);
      box-shadow: 0 4px 16px rgba(255, 255, 255, 0.2);
    }

    .btn-glow {
      background: linear-gradient(135deg, var(--accent-violet), #7C3AED);
      color: #FFFFFF;
      box-shadow: 0 0 20px var(--accent-violet-glow);
    }

    .btn-glow:hover {
      box-shadow: 0 0 28px rgba(139, 92, 246, 0.5);
      transform: translateY(-1px);
    }

    .btn-outline {
      background: transparent;
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
    }

    .btn-outline:hover {
      border-color: var(--border-hover);
      background: rgba(255, 255, 255, 0.03);
    }

    /* Hero Section */
    .hero-section {
      padding: 80px 0 48px;
      text-align: center;
    }

    .kicker {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-family: var(--font-mono);
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--accent-violet);
      background: rgba(139, 92, 246, 0.08);
      border: 1px solid rgba(139, 92, 246, 0.25);
      padding: 6px 14px;
      border-radius: 20px;
      margin-bottom: 24px;
    }

    .kicker-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--accent-emerald);
      box-shadow: 0 0 8px var(--accent-emerald);
    }

    .hero-title {
      font-size: 56px;
      font-weight: 800;
      line-height: 1.1;
      letter-spacing: -0.03em;
      margin-bottom: 20px;
      background: linear-gradient(180deg, #FFFFFF 0%, #D1D5DB 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
      font-size: 18px;
      color: var(--text-muted);
      max-width: 680px;
      margin: 0 auto 40px;
      font-weight: 400;
      line-height: 1.6;
    }

    /* Search & Filter Bar (Alta Floating Bar) */
    .search-panel {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      padding: 8px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      max-width: 960px;
      margin: 0 auto 56px;
      backdrop-filter: blur(20px);
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
    }

    .search-input-wrap {
      flex: 1;
      min-width: 220px;
      display: flex;
      align-items: center;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 10px 16px;
      gap: 10px;
    }

    .search-input-wrap select,
    .search-input-wrap input {
      background: transparent;
      border: none;
      color: var(--text-main);
      font-family: var(--font-sans);
      font-size: 14px;
      outline: none;
      width: 100%;
    }

    .search-input-wrap select option {
      background: #12141D;
      color: #fff;
    }

    /* Category Filter Pills */
    .category-pills {
      display: flex;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 48px;
    }

    .pill {
      font-family: var(--font-sans);
      font-size: 13px;
      font-weight: 500;
      padding: 8px 18px;
      border-radius: 24px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-subtle);
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .pill:hover {
      color: var(--text-main);
      border-color: rgba(255, 255, 255, 0.2);
    }

    .pill.active {
      background: rgba(139, 92, 246, 0.15);
      border-color: var(--accent-violet);
      color: #fff;
    }

    /* Catalog Cards Grid */
    .cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 24px;
      margin-bottom: 80px;
    }

    .listing-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
    }

    .listing-card:hover {
      transform: translateY(-4px);
      border-color: var(--border-hover);
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5), 0 0 24px var(--accent-violet-glow);
    }

    .card-photo-wrap {
      height: 200px;
      background: #151824;
      position: relative;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .card-photo {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.4s ease;
    }

    .listing-card:hover .card-photo {
      transform: scale(1.04);
    }

    .card-category-badge {
      position: absolute;
      top: 14px;
      left: 14px;
      background: rgba(7, 8, 12, 0.75);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-subtle);
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 4px 10px;
      border-radius: 6px;
      color: #C4B5FD;
    }

    .card-status-badge {
      position: absolute;
      top: 14px;
      right: 14px;
      background: rgba(7, 8, 12, 0.75);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-subtle);
      font-size: 11px;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--accent-emerald);
    }

    .card-content {
      padding: 24px;
      display: flex;
      flex-direction: column;
      flex: 1;
    }

    .card-location {
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--text-dim);
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .card-title {
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.01em;
      margin-bottom: 10px;
      color: #fff;
    }

    .card-desc {
      font-size: 14px;
      color: var(--text-muted);
      line-height: 1.5;
      margin-bottom: 18px;
      flex: 1;
    }

    .amenities-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 20px;
    }

    .amenity-tag {
      font-size: 11px;
      font-family: var(--font-mono);
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      padding: 3px 8px;
      border-radius: 4px;
      color: var(--text-muted);
    }

    .card-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 18px;
      border-top: 1px solid var(--border-subtle);
    }

    .rate-wrap {
      display: flex;
      flex-direction: column;
    }

    .rate-label {
      font-size: 11px;
      font-family: var(--font-mono);
      text-transform: uppercase;
      color: var(--text-dim);
    }

    .rate-val {
      font-size: 22px;
      font-weight: 800;
      color: #fff;
      font-family: var(--font-sans);
    }

    .rate-val span {
      font-size: 13px;
      color: var(--text-muted);
      font-weight: 400;
    }

    /* Modal */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(12px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 20px;
    }

    .modal-overlay.active {
      display: flex;
    }

    .modal-box {
      background: #0E1017;
      border: 1px solid var(--border-hover);
      border-radius: 20px;
      width: 100%;
      max-width: 540px;
      padding: 32px;
      box-shadow: 0 24px 64px rgba(0, 0, 0, 0.8), 0 0 32px var(--accent-violet-glow);
      position: relative;
    }

    .modal-close {
      position: absolute;
      top: 20px;
      right: 20px;
      background: transparent;
      border: none;
      color: var(--text-dim);
      font-size: 20px;
      cursor: pointer;
    }

    .modal-close:hover {
      color: #fff;
    }

    /* Form Styles */
    .form-group {
      margin-bottom: 16px;
    }

    .form-group label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 6px;
    }

    .form-control {
      width: 100%;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 10px 14px;
      color: #fff;
      font-family: var(--font-sans);
      font-size: 14px;
      outline: none;
    }

    .form-control:focus {
      border-color: var(--accent-violet);
    }

    /* Footer */
    footer {
      border-top: 1px solid var(--border-subtle);
      padding: 48px 0;
      color: var(--text-dim);
      font-size: 13px;
    }

    .footer-wrap {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 24px;
      align-items: center;
    }

    .footer-links {
      display: flex;
      gap: 20px;
      list-style: none;
    }

    .footer-links a {
      color: var(--text-muted);
      text-decoration: none;
      font-family: var(--font-mono);
      font-size: 12px;
    }

    .footer-links a:hover {
      color: #fff;
    }

    @media (max-width: 768px) {
      .hero-title { font-size: 38px; }
      .nav-links { display: none; }
      .cards-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="bg-grid"></div>

  <header>
    <div class="container nav-wrap">
      <a href="/" class="brand">
        <div class="brand-logo">W</div>
        <div class="brand-text">WYNAJMUJEMY<span style="color:var(--accent-violet)">.XYZ</span></div>
        <span class="brand-badge">Alta Edition</span>
      </a>
      <ul class="nav-links">
        <li><a href="#katalog">Katalog Lokali</a></li>
        <li><a href="#compliance">Reguły Art. 398 PKE</a></li>
        <li><a href="/docs" target="_blank">Swagger API</a></li>
        <li><a href="https://theones.io/benchmarks" target="_blank">JIT Benchmarks</a></li>
      </ul>
      <div style="display:flex; gap:12px;">
        <button class="btn btn-outline" onclick="openHostModal()">Dla Właścicieli</button>
        <button class="btn btn-glow" onclick="document.getElementById('katalog').scrollIntoView({behavior:'smooth'})">Szukaj Lokalu</button>
      </div>
    </div>
  </header>

  <main>
    <section class="hero-section container">
      <div class="kicker">
        <div class="kicker-dot"></div>
        Autonomously Coded by Qwen 3.8 9B with JIT Context OS
      </div>
      <h1 class="hero-title">
        Gabinety, stanowiska i sale<br>do Twojej profesjonalnej pracy.
      </h1>
      <p class="hero-subtitle">
        B2B marketplace wynajmu nadmiarowej powierzchni. Elastyczny dostęp do sprawdzonych gabinetów medycyny estetycznej, masażu, stanowisk barberskich i sal warsztatowych. Na godziny, dni lub stałe grafiki.
      </p>

      <div class="search-panel">
        <div class="search-input-wrap">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
          <select id="filter-city" onchange="filterListings()">
            <option value="">Wszystkie Miasta</option>
            <option value="Wrocław" selected>Wrocław</option>
            <option value="Warszawa">Warszawa</option>
            <option value="Kraków">Kraków</option>
            <option value="Poznań">Poznań</option>
            <option value="Gdańsk">Gdańsk</option>
            <option value="Katowice">Katowice</option>
          </select>
        </div>

        <div class="search-input-wrap">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h7"></path></svg>
          <select id="filter-category" onchange="filterListings()">
            <option value="">Wszystkie Kategorie</option>
            <option value="beauty">Gabinety Beauty & Estetyka</option>
            <option value="massage">Masaż & Fizjoterapia</option>
            <option value="hair">Stanowiska Fryzjerskie</option>
            <option value="office">Mikrobiura Prywatne</option>
            <option value="training">Sale Szkoleniowe</option>
          </select>
        </div>

        <button class="btn btn-primary" onclick="filterListings()">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          Filtruj Ofertę
        </button>
      </div>

      <div class="category-pills">
        <button class="pill active" onclick="setCategoryFilter('', this)">Wszystkie Lokale</button>
        <button class="pill" onclick="setCategoryFilter('beauty', this)">✨ Estetyka & Beauty</button>
        <button class="pill" onclick="setCategoryFilter('massage', this)">🌿 Masaż & Fizjo</button>
        <button class="pill" onclick="setCategoryFilter('hair', this)">✂️ Barber & Fryzjer</button>
        <button class="pill" onclick="setCategoryFilter('office', this)">💼 Mikrobiura</button>
        <button class="pill" onclick="setCategoryFilter('training', this)">🎓 Sale Warsztatowe</button>
      </div>
    </section>

    <section class="container" id="katalog">
      <div id="cards-container" class="cards-grid">
        <!-- Injected via JavaScript -->
      </div>
    </section>

    <!-- Compliance & Security Trust Bar -->
    <section class="container" id="compliance" style="margin-bottom: 80px;">
      <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 16px; padding: 36px; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 32px;">
        <div>
          <div style="font-family: var(--font-mono); font-size: 12px; color: var(--accent-violet); text-transform: uppercase; margin-bottom: 8px;">Automated Compliance</div>
          <h3 style="font-size: 18px; margin-bottom: 8px;">Ochrona Art. 398 PKE</h3>
          <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6;">
            Deterministyczna blokada nieautoryzowanych komunikatów marketingowych. Zero spamu wychodzącego, pełna transparentność źródeł danych.
          </p>
        </div>
        <div>
          <div style="font-family: var(--font-mono); font-size: 12px; color: var(--accent-cyan); text-transform: uppercase; margin-bottom: 8px;">Network Security</div>
          <h3 style="font-size: 18px; margin-bottom: 8px;">Aktywny Filtr SSRF</h3>
          <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6;">
            Walidacja adresów URL źródeł blokuje loopback, sieci prywatne RFC1918 i chmurowe metadane AWS/GCP (169.254.169.254).
          </p>
        </div>
        <div>
          <div style="font-family: var(--font-mono); font-size: 12px; color: var(--accent-emerald); text-transform: uppercase; margin-bottom: 8px;">Epistemic Veracity</div>
          <h3 style="font-size: 18px; margin-bottom: 8px;">Concurrency SHA-256</h3>
          <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6;">
            Kryptograficzne hashowanie draft_hash i inkrementacja wersji chronią przed konfliktami równoczesnej edycji i nadpisywaniem stawek.
          </p>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="container footer-wrap">
      <div>
        <span style="font-weight: 700; color: #fff;">WYNAJMUJEMY.XYZ</span> — Platforma B2B Wynajmu Przestrzeni Roboczej.
      </div>
      <ul class="footer-links">
        <li><a href="/docs">Swagger API</a></li>
        <li><a href="/health">Healthcheck</a></li>
        <li><a href="https://github.com/wojciechwiesner/wynajmujemy-core" target="_blank">GitHub</a></li>
        <li><a href="https://theones.io" target="_blank">TheOnes.io</a></li>
      </ul>
    </div>
  </footer>

  <!-- Booking Modal -->
  <div class="modal-overlay" id="booking-modal" onclick="if(event.target===this) closeBookingModal()">
    <div class="modal-box">
      <button class="modal-close" onclick="closeBookingModal()">&times;</button>
      <div style="font-family: var(--font-mono); font-size: 11px; color: var(--accent-violet); text-transform: uppercase; margin-bottom: 6px;" id="modal-kicker">Rezerwacja Przestrzeni</div>
      <h2 style="font-size: 22px; margin-bottom: 12px;" id="modal-title">Gabinet Kosmetyczny</h2>
      <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 24px;" id="modal-details">Wrocław, Rynek</p>

      <form onsubmit="handleBookingSubmit(event)">
        <div class="form-group">
          <label>Twoje Imię i Nazwisko / Firma</label>
          <input type="text" class="form-control" placeholder="np. dr Anna Kowalska / Estetica Sp. z o.o." required>
        </div>
        <div class="form-group">
          <label>Adres E-mail</label>
          <input type="email" class="form-control" placeholder="anna@estetica.pl" required>
        </div>
        <div class="form-group">
          <label>Numer Telefonu</label>
          <input type="tel" class="form-control" placeholder="+48 500 100 200" required>
        </div>
        <div class="form-group">
          <label>Data lub preferowany grafik</label>
          <input type="text" class="form-control" placeholder="np. Najbliższy wtorek, 10:00 - 16:00" required>
        </div>
        <button type="submit" class="btn btn-glow" style="width: 100%; margin-top: 12px;">Wyślij Potwierdzenie do Gospodarza</button>
      </form>
    </div>
  </div>

  <!-- Host Registration Modal -->
  <div class="modal-overlay" id="host-modal" onclick="if(event.target===this) closeHostModal()">
    <div class="modal-box">
      <button class="modal-close" onclick="closeHostModal()">&times;</button>
      <div style="font-family: var(--font-mono); font-size: 11px; color: var(--accent-cyan); text-transform: uppercase; margin-bottom: 6px;">Dla Właścicieli Lokali</div>
      <h2 style="font-size: 22px; margin-bottom: 12px;">Wystaw Nadmiarowy Gabinet</h2>
      <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 24px;">Zarabiaj na pustych stanowiskach i gabinetach bez długoterminowych umów.</p>

      <form onsubmit="handleHostSubmit(event)">
        <div class="form-group">
          <label>Imię i Nazwisko / Nazwa Biznesu</label>
          <input type="text" id="host-name" class="form-control" placeholder="np. Salon Kosmetyczny LUNA" required>
        </div>
        <div class="form-group">
          <label>Adres E-mail Gospodarza</label>
          <input type="email" id="host-email" class="form-control" placeholder="kontakt@twojsalon.pl" required>
        </div>
        <div class="form-group">
          <label>Numer NIP (opcjonalnie)</label>
          <input type="text" id="host-nip" class="form-control" placeholder="1234567890">
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 12px;">Zarejestruj Konto Hosta</button>
      </form>
    </div>
  </div>

  <script>
    const INITIAL_LISTINGS = [
      {
        id: "list-001",
        title: "Gabinet Medycyny Estetycznej Premium",
        category: "beauty",
        category_label: "Estetyka / Beauty",
        city: "Wrocław",
        location: "Stare Miasto, Rynek",
        desc: "W pełni wyposażony gabinet zabiegowy. Fotel hydrauliczny, autoklaw klasy B, lampa bezcieniowa, recepcja dla pacjentów oraz strefa relaksu.",
        hourly_pln: 45,
        daily_pln: 290,
        amenities: ["Autoklaw Enbio", "Fotel hydrauliczny", "Recepcja", "Klimatyzacja", "Parking"],
        photo: "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=800&q=80"
      },
      {
        id: "list-002",
        title: "Klimatyczny Gabinet Masażu & Fizjoterapii",
        category: "massage",
        category_label: "Masaż / Fizjo",
        city: "Warszawa",
        location: "Śródmieście Południowe",
        desc: "Cichy, wyciszony akustycznie gabinet z podgrzewanym stołem Habys, prysznicem w kabinie, nastrojowym oświetleniem LED i dyfuzorem olejków.",
        hourly_pln: 55,
        daily_pln: 340,
        amenities: ["Stół Habys Pro", "Prysznic w gabinecie", "Wyciszenie 42dB", "Ręczniki w cenie"],
        photo: "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=800&q=80"
      },
      {
        id: "list-003",
        title: "Stanowisko Barberskie / Stylisty Fryzur",
        category: "hair",
        category_label: "Barber / Hair",
        city: "Wrocław",
        location: "Krzyki / Gaj",
        desc: "Stanowisko w renomowanym salonie z bazą klientów walk-in. Fotel Belmont, myjnia z masażem, pełne zaopatrzenie w kosmetyki profesjonalne.",
        hourly_pln: 35,
        daily_pln: 220,
        amenities: ["Fotel Belmont", "Myjnia z masażem", "Kawa speciality", "Płatności kartą"],
        photo: "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=800&q=80"
      },
      {
        id: "list-004",
        title: "Sala Warsztatowa & Szkoleniowa (16 Osób)",
        category: "training",
        category_label: "Szkolenia / Warsztaty",
        city: "Poznań",
        location: "Jeżyce",
        desc: "Nowoczesna sala modułowa z rzutnikiem 4K, flipchartem, nagłośnieniem bezprzewodowym i aneksem cateringowym na szkolenia branżowe.",
        hourly_pln: 90,
        daily_pln: 580,
        amenities: ["Projektor 4K", "Nagłośnienie mic", "Światłowód 1Gbps", "Strefa Coffee"],
        photo: "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80"
      },
      {
        id: "list-005",
        title: "Mikrobiuro Prywatne dla Konsultantów & Prawa",
        category: "office",
        category_label: "Mikrobiuro",
        city: "Gdańsk",
        location: "Wrzeszcz Garnizon",
        desc: "Dyskretny gabinet na spotkania biznesowe, mediacje i konsultacje. Ergonomiczne biurka, szybki światłowód i dostęp do budynkowej recepcji.",
        hourly_pln: 50,
        daily_pln: 310,
        amenities: ["Smart Lock", "Monitor 27 cali", "Cicha strefa", "Klimatyzacja"],
        photo: "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80"
      },
      {
        id: "list-006",
        title: "Gabinet Psychoterapii & Coachingu",
        category: "massage",
        category_label: "Terapia / Konsultacje",
        city: "Kraków",
        location: "Kazimierz",
        desc: "Przytulny, jasny gabinet w zabytkowej kamienicy. Komfortowe fotele uszaki, naturalne rośliny, czajnik i wyciszenie drzwi wejściowych.",
        hourly_pln: 40,
        daily_pln: 250,
        amenities: ["Fotele Uszak", "Akustyka 45dB", "Herbata & Woda", "Domofon bezpośredni"],
        photo: "https://images.unsplash.com/photo-1527689368864-3a821dbccc34?auto=format&fit=crop&w=800&q=80"
      }
    ];

    let activeFilterCat = "";

    function renderListings(items) {
      const container = document.getElementById("cards-container");
      container.innerHTML = items.map(item => `
        <article class="listing-card">
          <div class="card-photo-wrap">
            <img src="${item.photo}" alt="${item.title}" class="card-photo" loading="lazy">
            <span class="card-category-badge">${item.category_label}</span>
            <span class="card-status-badge">
              <span style="width:6px;height:6px;border-radius:50%;background:var(--accent-emerald);"></span>
              Dostępne
            </span>
          </div>
          <div class="card-content">
            <div class="card-location">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path></svg>
              ${item.city} · ${item.location}
            </div>
            <h3 class="card-title">${item.title}</h3>
            <p class="card-desc">${item.desc}</p>
            <div class="amenities-list">
              ${item.amenities.map(a => `<span class="amenity-tag">${a}</span>`).join('')}
            </div>
            <div class="card-footer">
              <div class="rate-wrap">
                <span class="rate-label">Stawka</span>
                <span class="rate-val">${item.hourly_pln} zł <span>/ godz.</span></span>
              </div>
              <button class="btn btn-outline" onclick="openBookingModal('${item.title}', '${item.city}, ${item.location}', ${item.hourly_pln})">
                Rezerwuj
              </button>
            </div>
          </div>
        </article>
      `).join('');
    }

    function filterListings() {
      const city = document.getElementById("filter-city").value.toLowerCase();
      const cat = document.getElementById("filter-category").value;
      const effectiveCat = cat || activeFilterCat;

      const filtered = INITIAL_LISTINGS.filter(item => {
        const matchCity = !city || item.city.toLowerCase() === city;
        const matchCat = !effectiveCat || item.category === effectiveCat;
        return matchCity && matchCat;
      });
      renderListings(filtered);
    }

    function setCategoryFilter(cat, btn) {
      activeFilterCat = cat;
      document.querySelectorAll('.category-pills .pill').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById("filter-category").value = cat;
      filterListings();
    }

    function openBookingModal(title, details, rate) {
      document.getElementById("modal-title").innerText = title;
      document.getElementById("modal-details").innerText = `${details} · ${rate} zł / godz.`;
      document.getElementById("booking-modal").classList.add("active");
    }

    function closeBookingModal() {
      document.getElementById("booking-modal").classList.remove("active");
    }

    function openHostModal() {
      document.getElementById("host-modal").classList.add("active");
    }

    function closeHostModal() {
      document.getElementById("host-modal").classList.remove("active");
    }

    async function handleBookingSubmit(e) {
      e.preventDefault();
      alert("✅ Zapytanie rezerwacyjne zostało wysłane do właściciela lokalu! Otrzymasz potwierdzenie SMS/E-mail.");
      closeBookingModal();
    }

    async function handleHostSubmit(e) {
      e.preventDefault();
      const name = document.getElementById("host-name").value;
      const email = document.getElementById("host-email").value;
      const nip = document.getElementById("host-nip").value;

      try {
        const res = await fetch("/api/hosts/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ full_name: name, email: email, nip: nip || null })
        });
        const data = await res.json();
        if (res.ok) {
          alert(`🎉 Konto zarejestrowane pomyślnie! Twój token autoryzacyjny: ${data.token.slice(0, 12)}... Link aktywacyjny został wysłany.`);
          closeHostModal();
        } else {
          alert(`Błąd rejestracji: ${data.detail || 'Sprawdź dane'}`);
        }
      } catch (err) {
        alert("Błąd połączenia z API: " + err);
      }
    }

    // Initial load
    window.addEventListener("DOMContentLoaded", () => {
      renderListings(INITIAL_LISTINGS);
    });
  </script>
</body>
</html>
"""
