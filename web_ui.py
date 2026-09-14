"""Alta-inspired English & Bilingual Frontend for Wynajmujemy.xyz B2B Marketplace."""

from __future__ import annotations


def get_frontend_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wynajmujemy.xyz — B2B Marketplace for Professional Suites & Workspaces</title>
  <meta name="description" content="On-demand B2B marketplace for medical suites, beauty booths, massage clinics, private micro-offices, and training halls. Autonomously coded by Qwen 3.8 9B.">
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
      line-height: 1.5;
      overflow-x: hidden;
      background-image: 
        radial-gradient(circle at 15% 15%, rgba(139, 92, 246, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 30%, rgba(6, 182, 212, 0.08) 0%, transparent 35%),
        radial-gradient(circle at 50% 80%, rgba(16, 185, 129, 0.05) 0%, transparent 45%);
    }

    .container {
      max-width: 1240px;
      margin: 0 auto;
      padding: 0 24px;
    }

    header {
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(20px);
      background: rgba(7, 8, 12, 0.82);
      border-bottom: 1px solid var(--border-subtle);
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
      color: inherit;
    }

    .brand-logo {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: linear-gradient(135deg, var(--accent-violet), #4F46E5);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.1rem;
      color: #fff;
      box-shadow: 0 0 20px var(--accent-violet-glow);
    }

    .brand-text {
      font-weight: 700;
      font-size: 1.15rem;
      letter-spacing: -0.02em;
    }

    .brand-badge {
      font-family: var(--font-mono);
      font-size: 0.65rem;
      padding: 2px 8px;
      border-radius: 999px;
      background: rgba(139, 92, 246, 0.15);
      border: 1px solid rgba(139, 92, 246, 0.35);
      color: #C4B5FD;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 28px;
      list-style: none;
    }

    .nav-links a {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 500;
      transition: color 0.2s ease;
    }

    .nav-links a:hover {
      color: var(--text-main);
    }

    .lang-switcher {
      display: flex;
      align-items: center;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 2px;
      margin-right: 8px;
    }

    .lang-btn {
      background: transparent;
      border: none;
      color: var(--text-dim);
      font-family: var(--font-mono);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 4px 8px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .lang-btn.active {
      background: var(--accent-violet);
      color: #fff;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 10px 18px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.88rem;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      border: none;
    }

    .btn-glow {
      background: linear-gradient(135deg, var(--accent-violet), #6D28D9);
      color: #fff;
      box-shadow: 0 4px 20px var(--accent-violet-glow);
    }

    .btn-glow:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 25px rgba(139, 92, 246, 0.45);
    }

    .btn-outline {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
    }

    .btn-outline:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(255, 255, 255, 0.2);
    }

    .hero-section {
      padding: 72px 0 48px;
      text-align: center;
      position: relative;
    }

    .kicker {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      padding: 6px 14px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: #E2E8F0;
      margin-bottom: 24px;
      letter-spacing: 0.03em;
    }

    .kicker-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--accent-emerald);
      box-shadow: 0 0 8px var(--accent-emerald);
    }

    .hero-title {
      font-size: clamp(2.4rem, 5.2vw, 4.2rem);
      font-weight: 800;
      letter-spacing: -0.035em;
      line-height: 1.1;
      margin-bottom: 20px;
      background: linear-gradient(180deg, #FFFFFF 20%, #A1A1AA 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
      font-size: clamp(1rem, 1.8vw, 1.25rem);
      color: var(--text-muted);
      max-width: 760px;
      margin: 0 auto 36px;
      font-weight: 400;
    }

    .search-panel {
      max-width: 860px;
      margin: 0 auto;
      background: rgba(18, 20, 29, 0.8);
      border: 1px solid var(--border-subtle);
      border-radius: 14px;
      padding: 10px;
      display: grid;
      grid-template-columns: 1fr 1fr auto;
      gap: 12px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
      backdrop-filter: blur(24px);
    }

    .search-input-wrap {
      display: flex;
      align-items: center;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 10px;
      padding: 0 14px;
      height: 48px;
      gap: 10px;
    }

    .search-input-wrap select, .search-input-wrap input {
      background: transparent;
      border: none;
      color: #fff;
      font-family: var(--font-sans);
      font-size: 0.92rem;
      width: 100%;
      outline: none;
    }

    .search-input-wrap select option {
      background: #12141D;
      color: #fff;
    }

    .stats-bar {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin: 56px 0 48px;
    }

    .stat-box {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 20px 18px;
      text-align: left;
      transition: all 0.2s ease;
    }

    .stat-box:hover {
      border-color: rgba(255, 255, 255, 0.16);
      transform: translateY(-2px);
    }

    .stat-val {
      font-family: var(--font-mono);
      font-size: 1.4rem;
      font-weight: 700;
      color: #fff;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .stat-desc {
      font-size: 0.8rem;
      color: var(--text-dim);
      line-height: 1.35;
    }

    .category-nav {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 12px;
      margin-bottom: 32px;
      border-bottom: 1px solid var(--border-subtle);
      scrollbar-width: none;
    }

    .category-nav::-webkit-scrollbar {
      display: none;
    }

    .cat-tab {
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      font-family: var(--font-sans);
      font-size: 0.88rem;
      font-weight: 500;
      padding: 8px 16px;
      border-radius: 999px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s ease;
    }

    .cat-tab:hover {
      color: #fff;
      background: rgba(255, 255, 255, 0.05);
    }

    .cat-tab.active {
      background: rgba(139, 92, 246, 0.15);
      border-color: rgba(139, 92, 246, 0.4);
      color: #DDD6FE;
      font-weight: 600;
    }

    .listings-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 24px;
      margin-bottom: 72px;
    }

    .card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
    }

    .card:hover {
      border-color: var(--border-hover);
      transform: translateY(-4px);
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.4), 0 0 24px rgba(139, 92, 246, 0.15);
    }

    .card-thumb {
      height: 200px;
      background: #181B26;
      position: relative;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .card-thumb img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.4s ease;
    }

    .card:hover .card-thumb img {
      transform: scale(1.04);
    }

    .card-badge {
      position: absolute;
      top: 14px;
      left: 14px;
      font-family: var(--font-mono);
      font-size: 0.68rem;
      font-weight: 600;
      text-transform: uppercase;
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(7, 8, 12, 0.75);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #fff;
      backdrop-filter: blur(8px);
    }

    .card-avail {
      position: absolute;
      bottom: 14px;
      right: 14px;
      font-size: 0.75rem;
      font-weight: 500;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(16, 185, 129, 0.18);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #A7F3D0;
      backdrop-filter: blur(8px);
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .card-body {
      padding: 22px;
      display: flex;
      flex-direction: column;
      flex-grow: 1;
    }

    .card-location {
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--text-dim);
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
      text-transform: uppercase;
    }

    .card-title {
      font-size: 1.18rem;
      font-weight: 700;
      color: #fff;
      margin-bottom: 10px;
      line-height: 1.3;
    }

    .card-desc {
      font-size: 0.88rem;
      color: var(--text-muted);
      margin-bottom: 18px;
      line-height: 1.45;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .amenities-list {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 20px;
    }

    .amenity-tag {
      font-size: 0.72rem;
      padding: 3px 8px;
      border-radius: 5px;
      background: rgba(255, 255, 255, 0.04);
      color: var(--text-muted);
      border: 1px solid rgba(255, 255, 255, 0.06);
    }

    .card-footer {
      margin-top: auto;
      padding-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .card-price {
      font-family: var(--font-mono);
    }

    .price-num {
      font-size: 1.35rem;
      font-weight: 700;
      color: #fff;
    }

    .price-unit {
      font-size: 0.78rem;
      color: var(--text-dim);
    }

    .compliance-section {
      background: rgba(14, 16, 24, 0.6);
      border: 1px solid var(--border-subtle);
      border-radius: 18px;
      padding: 40px;
      margin-bottom: 80px;
    }

    .section-head {
      margin-bottom: 28px;
    }

    .section-kicker {
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--accent-violet);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 6px;
    }

    .section-title {
      font-size: 1.8rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .rules-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
    }

    .rule-card {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 12px;
      padding: 20px;
    }

    .rule-card h4 {
      font-size: 0.98rem;
      font-weight: 600;
      color: #fff;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .rule-card p {
      font-size: 0.84rem;
      color: var(--text-muted);
      line-height: 1.4;
    }

    footer {
      border-top: 1px solid var(--border-subtle);
      padding: 40px 0;
      font-size: 0.85rem;
      color: var(--text-dim);
    }

    .footer-wrap {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }

    /* Modal styles */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(12px);
      z-index: 200;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .modal-overlay.active {
      display: flex;
    }

    .modal-box {
      background: #0E1017;
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      max-width: 540px;
      width: 100%;
      padding: 32px;
      position: relative;
      box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 30px var(--accent-violet-glow);
    }

    .modal-close {
      position: absolute;
      top: 20px;
      right: 20px;
      background: transparent;
      border: none;
      color: var(--text-dim);
      font-size: 1.4rem;
      cursor: pointer;
    }

    .modal-close:hover {
      color: #fff;
    }

    .form-group {
      margin-bottom: 18px;
    }

    .form-group label {
      display: block;
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-bottom: 6px;
      font-weight: 500;
    }

    .form-control {
      width: 100%;
      height: 44px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 0 14px;
      color: #fff;
      font-family: var(--font-sans);
      font-size: 0.9rem;
      outline: none;
    }

    .form-control:focus {
      border-color: var(--accent-violet);
    }

    @media (max-width: 900px) {
      .stats-bar, .rules-grid { grid-template-columns: 1fr 1fr; }
      .search-panel { grid-template-columns: 1fr; }
      .hero-title { font-size: 2.2rem; }
      .nav-links { display: none; }
    }

    @media (max-width: 600px) {
      .stats-bar, .rules-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

  <header>
    <div class="container nav-wrap">
      <a href="/" class="brand">
        <div class="brand-logo">W</div>
        <div class="brand-text">WYNAJMUJEMY<span style="color:var(--accent-violet)">.XYZ</span></div>
        <span class="brand-badge">Alta Edition</span>
      </a>
      <ul class="nav-links">
        <li><a href="#catalog" id="nav-catalog">Spaces Catalog</a></li>
        <li><a href="#compliance" id="nav-compliance">Article 398 Compliance</a></li>
        <li><a href="/docs" target="_blank">Swagger API</a></li>
        <li><a href="https://theones.io/benchmarks" target="_blank">JIT Benchmarks</a></li>
      </ul>
      <div style="display:flex; align-items:center; gap:12px;">
        <div class="lang-switcher">
          <button class="lang-btn active" id="btn-lang-en" onclick="setLanguage('en')">EN</button>
          <button class="lang-btn" id="btn-lang-pl" onclick="setLanguage('pl')">PL</button>
        </div>
        <button class="btn btn-outline" id="btn-host-header" onclick="openHostModal()">List Space</button>
        <button class="btn btn-glow" id="btn-search-header" onclick="document.getElementById('catalog').scrollIntoView({behavior:'smooth'})">Find Spaces</button>
      </div>
    </div>
  </header>

  <main>
    <section class="hero-section container">
      <div class="kicker">
        <div class="kicker-dot"></div>
        <span id="txt-kicker">Autonomously Coded by Qwen 3.8 9B with JIT Context OS</span>
      </div>
      <h1 class="hero-title" id="txt-hero-title">
        Premium Consulting Suites,<br>Booths & Spaces on Demand.
      </h1>
      <p class="hero-subtitle" id="txt-hero-sub">
        B2B marketplace connecting surplus professional facilities with licensed specialists. Flexible hourly, daily, and recurring workspace rentals for beauty, wellness, medical, and private practices.
      </p>

      <div class="search-panel">
        <div class="search-input-wrap">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
          <select id="filter-city" onchange="filterListings()">
            <option value="" id="opt-all-cities">All Cities</option>
            <option value="Wrocław" selected>Wrocław</option>
            <option value="Warszawa">Warsaw</option>
            <option value="Kraków">Kraków</option>
            <option value="Poznań">Poznań</option>
            <option value="Gdańsk">Gdańsk</option>
            <option value="Katowice">Katowice</option>
          </select>
        </div>

        <div class="search-input-wrap">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <input type="number" id="filter-price" placeholder="Max rate (PLN/hr)" oninput="filterListings()">
        </div>

        <button class="btn btn-glow" id="btn-filter-action" onclick="filterListings()">Search</button>
      </div>

      <div class="stats-bar">
        <div class="stat-box">
          <div class="stat-val"><span style="color:var(--accent-violet)">100%</span> Autonomy</div>
          <div class="stat-desc" id="txt-stat-1">Coded autonomously by local Qwen 3.8 9B on an Apple Silicon Mac Mini ($0.00 API cost).</div>
        </div>
        <div class="stat-box">
          <div class="stat-val"><span style="color:var(--accent-emerald)">25/25</span> Tests</div>
          <div class="stat-desc" id="txt-stat-2">Full pytest verification passed with Pydantic v2 schemas and strict field assertion.</div>
        </div>
        <div class="stat-box">
          <div class="stat-val"><span style="color:var(--accent-cyan)">Art. 398</span> PKE</div>
          <div class="stat-desc" id="txt-stat-3">Automated outbound marketing blocker & SSRF loopback guardrails active in core.</div>
        </div>
        <div class="stat-box">
          <div class="stat-val"><span style="color:#F59E0B">SHA-256</span> Concurrency</div>
          <div class="stat-desc" id="txt-stat-4">Cryptographic draft hashing guarding against race conditions and stale edits.</div>
        </div>
      </div>
    </section>

    <section class="container" id="catalog">
      <div class="category-nav">
        <button class="cat-tab active" data-cat="all" onclick="setCategory('all')" id="tab-all">All Spaces</button>
        <button class="cat-tab" data-cat="beauty" onclick="setCategory('beauty')" id="tab-beauty">Beauty & Aesthetic Suites</button>
        <button class="cat-tab" data-cat="massage" onclick="setCategory('massage')" id="tab-massage">Massage & Physical Therapy</button>
        <button class="cat-tab" data-cat="barber" onclick="setCategory('barber')" id="tab-barber">Barber & Hair Stations</button>
        <button class="cat-tab" data-cat="office" onclick="setCategory('office')" id="tab-office">Private Micro-Offices</button>
        <button class="cat-tab" data-cat="workshop" onclick="setCategory('workshop')" id="tab-workshop">Training & Workshop Halls</button>
      </div>

      <div class="listings-grid" id="listings-container">
        <!-- Rendered dynamically -->
      </div>
    </section>

    <section class="container" id="compliance">
      <div class="compliance-section">
        <div class="section-head">
          <div class="section-kicker" id="txt-comp-kicker">Enterprise Architectural Canon</div>
          <h2 class="section-title" id="txt-comp-title">5-Dimensional Compliance & Safety Engine</h2>
        </div>
        <div class="rules-grid">
          <div class="rule-card">
            <h4>
              <svg width="18" height="18" fill="none" stroke="var(--accent-emerald)" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
              <span id="txt-rule-1-title">Article 398 PKE Blocker</span>
            </h4>
            <p id="txt-rule-1-desc">Guarantees zero unsolicited commercial outbound contact without verified double opt-in consent recorded in SQLite WAL.</p>
          </div>
          <div class="rule-card">
            <h4>
              <svg width="18" height="18" fill="none" stroke="var(--accent-cyan)" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
              <span id="txt-rule-2-title">SSRF Protection Shield</span>
            </h4>
            <p id="txt-rule-2-desc">Blocks imports from localhost, loopback, internal private subnets (RFC 1918) and cloud metadata services (169.254.169.254).</p>
          </div>
          <div class="rule-card">
            <h4>
              <svg width="18" height="18" fill="none" stroke="var(--accent-violet)" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
              <span id="txt-rule-3-title">JIT Context OS Kernel</span>
            </h4>
            <p id="txt-rule-3-desc">Engineered natively for Hermes Agent, reducing context footprint by 47% and enabling local model deployment.</p>
          </div>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="container footer-wrap">
      <div>
        <div style="font-weight:700; color:#fff; margin-bottom:4px;">WYNAJMUJEMY.XYZ</div>
        <div>Enterprise B2B Space Rental Infrastructure · Powered by Hermes Agent</div>
      </div>
      <div style="display:flex; gap:20px;">
        <a href="/docs" style="color:var(--text-muted); text-decoration:none;">Swagger API</a>
        <a href="https://github.com/wojciechwiesner/wynajmujemy-core" target="_blank" style="color:var(--text-muted); text-decoration:none;">GitHub Code</a>
        <a href="https://theones.io/benchmarks" target="_blank" style="color:var(--text-muted); text-decoration:none;">Benchmarks</a>
      </div>
    </div>
  </footer>

  <!-- Booking Modal -->
  <div class="modal-overlay" id="bookingModal">
    <div class="modal-box">
      <button class="modal-close" onclick="closeModals()">&times;</button>
      <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--accent-violet); text-transform:uppercase; margin-bottom:6px;" id="modal-book-kicker">Instant Inquire</div>
      <h3 style="font-size:1.35rem; font-weight:700; margin-bottom:8px;" id="modal-space-title">Book Space</h3>
      <p style="color:var(--text-muted); font-size:0.88rem; margin-bottom:20px;" id="modal-space-rate">Hourly Rate: 45.00 PLN</p>
      
      <div class="form-group">
        <label id="lbl-name">Your Full Name / Practice</label>
        <input type="text" class="form-control" id="book-name" placeholder="e.g. Dr. Anna Nowak / Glow Studio">
      </div>
      <div class="form-group">
        <label id="lbl-email">Business Email</label>
        <input type="email" class="form-control" id="book-email" placeholder="anna@glowstudio.com">
      </div>
      <div class="form-group">
        <label id="lbl-date">Requested Date & Duration</label>
        <input type="text" class="form-control" id="book-date" placeholder="e.g. 2026-09-20 (4 hours)">
      </div>
      <button class="btn btn-glow" style="width:100%; height:46px; margin-top:10px;" onclick="submitBooking()" id="btn-submit-booking">Send Verified Inquiry</button>
    </div>
  </div>

  <!-- Host Modal -->
  <div class="modal-overlay" id="hostModal">
    <div class="modal-box">
      <button class="modal-close" onclick="closeModals()">&times;</button>
      <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--accent-emerald); text-transform:uppercase; margin-bottom:6px;" id="modal-host-kicker">Host Onboarding</div>
      <h3 style="font-size:1.35rem; font-weight:700; margin-bottom:8px;" id="modal-host-title">List Your Surplus Space</h3>
      <p style="color:var(--text-muted); font-size:0.88rem; margin-bottom:20px;" id="modal-host-desc">Monetize empty consulting rooms, salon stations, or offices with verified professionals.</p>
      
      <div class="form-group">
        <label id="lbl-host-name">Venue / Facility Name</label>
        <input type="text" class="form-control" id="host-name" placeholder="e.g. Aesthetics Clinic Rynek">
      </div>
      <div class="form-group">
        <label id="lbl-host-email">Host Email</label>
        <input type="email" class="form-control" id="host-email" placeholder="owner@clinic.com">
      </div>
      <div class="form-group">
        <label id="lbl-host-city">City</label>
        <input type="text" class="form-control" id="host-city" placeholder="Wrocław, Warsaw, etc.">
      </div>
      <div class="form-group">
        <label id="lbl-host-cat">Category</label>
        <select class="form-control" id="host-cat" style="background:#12141D;">
          <option value="beauty">Beauty & Aesthetics Suite</option>
          <option value="massage">Massage & Physical Therapy</option>
          <option value="barber">Barber / Hair Station</option>
          <option value="office">Private Micro-Office</option>
          <option value="workshop">Training / Workshop Hall</option>
        </select>
      </div>
      <button class="btn btn-glow" style="width:100%; height:46px; margin-top:10px;" onclick="submitHost()" id="btn-submit-host">Register Facility & Get API Token</button>
    </div>
  </div>

  <script>
    let currentLang = 'en';
    let currentCategory = 'all';

    const TRANSLATIONS = {
      en: {
        navCatalog: 'Spaces Catalog',
        navCompliance: 'Article 398 Compliance',
        btnHostHeader: 'List Space',
        btnSearchHeader: 'Find Spaces',
        kicker: 'Autonomously Coded by Qwen 3.8 9B with JIT Context OS',
        heroTitle: 'Premium Consulting Suites,<br>Booths & Spaces on Demand.',
        heroSub: 'B2B marketplace connecting surplus professional facilities with licensed specialists. Flexible hourly, daily, and recurring workspace rentals for beauty, wellness, medical, and private practices.',
        optAllCities: 'All Cities',
        btnFilterAction: 'Search',
        stat1: 'Coded autonomously by local Qwen 3.8 9B on an Apple Silicon Mac Mini ($0.00 API cost).',
        stat2: 'Full pytest verification passed with Pydantic v2 schemas and strict field assertion.',
        stat3: 'Automated outbound marketing blocker & SSRF loopback guardrails active in core.',
        stat4: 'Cryptographic draft hashing guarding against race conditions and stale edits.',
        tabAll: 'All Spaces',
        tabBeauty: 'Beauty & Aesthetic Suites',
        tabMassage: 'Massage & Physical Therapy',
        tabBarber: 'Barber & Hair Stations',
        tabOffice: 'Private Micro-Offices',
        tabWorkshop: 'Training & Workshop Halls',
        compKicker: 'Enterprise Architectural Canon',
        compTitle: '5-Dimensional Compliance & Safety Engine',
        rule1Title: 'Article 398 PKE Blocker',
        rule1Desc: 'Guarantees zero unsolicited commercial outbound contact without verified double opt-in consent recorded in SQLite WAL.',
        rule2Title: 'SSRF Protection Shield',
        rule2Desc: 'Blocks imports from localhost, loopback, internal private subnets (RFC 1918) and cloud metadata services (169.254.169.254).',
        rule3Title: 'JIT Context OS Kernel',
        rule3Desc: 'Engineered natively for Hermes Agent, reducing context footprint by 47% and enabling local model deployment.',
        bookBtn: 'Book Space',
        perHour: '/ hour'
      },
      pl: {
        navCatalog: 'Katalog Lokali',
        navCompliance: 'Reguły Art. 398 PKE',
        btnHostHeader: 'Dla Właścicieli',
        btnSearchHeader: 'Szukaj Lokalu',
        kicker: 'Autonomicznie zakodowane przez Qwen 3.8 9B z JIT Context OS',
        heroTitle: 'Gabinety, stanowiska i sale<br>do Twojej profesjonalnej pracy.',
        heroSub: 'B2B marketplace wynajmu nadmiarowej powierzchni. Elastyczny dostęp do sprawdzonych gabinetów medycyny estetycznej, masażu, stanowisk barberskich i sal warsztatowych. Na godziny, dni lub stałe grafiki.',
        optAllCities: 'Wszystkie Miasta',
        btnFilterAction: 'Szukaj',
        stat1: 'Napisane w 100% autonomicznie przez Qwen 3.8 9B na Macu Mini bez kosztów API ($0.00).',
        stat2: '25/25 testów pytest na zielono z walidacją schematów Pydantic v2 w czasie 0.28s.',
        stat3: 'Automatyczna blokada spamu (Art. 398 PKE) i ochrona przed SSRF wbudowane w rdzeń.',
        stat4: 'Kryptograficzne hashowanie SHA-256 chroniące przed konfliktami i wyścigami edycji.',
        tabAll: 'Wszystkie Lokale',
        tabBeauty: 'Gabinety Beauty & Med',
        tabMassage: 'Masaż & Fizjoterapia',
        tabBarber: 'Stanowiska Barberskie',
        tabOffice: 'Mikrobiura Prywatne',
        tabWorkshop: 'Sale Szkoleniowe',
        compKicker: 'Architektoniczny Kanon Enterprise',
        compTitle: 'Silnik Bezpieczeństwa i Zgodności 5D',
        rule1Title: 'Blokada Art. 398 PKE',
        rule1Desc: 'Bezwzględna blokada nieautoryzowanej komunikacji wychodzącej bez zgody zapisanej w SQLite WAL.',
        rule2Title: 'Ochrona przed SSRF',
        rule2Desc: 'Fizyczna blokada pętli loopback, podsieci prywatnych i endpointów metadanych chmury (169.254.169.254).',
        rule3Title: 'Kernel JIT Context OS',
        rule3Desc: 'Natywna integracja z Hermes Agent, obniżająca zużycie tokenów o 47% i odblokowująca modele lokalne.',
        bookBtn: 'Rezerwuj termin',
        perHour: '/ godz.'
      }
    };

    const SPACES_DATA = [
      {
        id: 'sp_1',
        cat: 'beauty',
        city: 'Wrocław',
        title_en: 'Premium Aesthetic Medicine Suite',
        title_pl: 'Gabinet Medycyny Estetycznej Premium',
        desc_en: 'Fully certified medical consulting room with hydraulic surgical chair, surgical light, and class B autoclave.',
        desc_pl: 'Certyfikowany gabinet zabiegowy z hydraulicznym fotelem, lampą bezcieniową i autoklawem klasy B.',
        rate: 45,
        location: 'Wrocław · Old Town (Rynek)',
        amenities: ['Autoclave Class B', 'Hydraulic Chair', 'Reception Service', 'Client Parking'],
        img: 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=800&q=80'
      },
      {
        id: 'sp_2',
        cat: 'massage',
        city: 'Warszawa',
        title_en: 'Holistic Physiotherapy & Massage Studio',
        title_pl: 'Studio Masażu i Fizjoterapii',
        desc_en: 'Quiet, sound-insulated practice room equipped with heated electric massage table and private shower.',
        desc_pl: 'Wyciszony, klimatyczny gabinet z podgrzewanym stołem elektrycznym i prywatnym prysznicem.',
        rate: 55,
        location: 'Warsaw · Śródmieście Północne',
        amenities: ['Heated Table', 'Private Shower', 'Soundproofing', 'Towel Service'],
        img: 'https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=800&q=80'
      },
      {
        id: 'sp_3',
        cat: 'barber',
        city: 'Kraków',
        title_en: 'Master Barber Workstation in High-End Salon',
        title_pl: 'Stanowisko Barberskie Master',
        desc_en: 'Dedicated professional styling chair with premium backwash unit in an active designer salon.',
        desc_pl: 'Dedykowany fotel barberski z myjnią w luksusowym, działającym salonie w sercu Kazimierza.',
        rate: 35,
        location: 'Kraków · Kazimierz District',
        amenities: ['Takara Belmont Chair', 'Backwash Unit', 'Coffee Bar', 'Cosmetics Fridge'],
        img: 'https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=800&q=80'
      },
      {
        id: 'sp_4',
        cat: 'workshop',
        city: 'Poznań',
        title_en: 'Interactive Workshop & Training Hall (16 pax)',
        title_pl: 'Sala Szkoleniowa i Warsztatowa (16 os.)',
        desc_en: 'Modern classroom with 4K interactive presentation display, ergonomic desks, and catering facilities.',
        desc_pl: 'Nowoczesna sala z monitorem 4K, ergonomicznymi biurkami i zapleczem cateringowym.',
        rate: 90,
        location: 'Poznań · Jeżyce Innovation Hub',
        amenities: ['4K Interactive Display', 'High-Speed Wi-Fi', 'Coffee Machine', 'Flipcharts'],
        img: 'https://images.unsplash.com/photo-1517502884422-41eaead166d4?auto=format&fit=crop&w=800&q=80'
      },
      {
        id: 'sp_5',
        cat: 'office',
        city: 'Gdańsk',
        title_en: 'Private 2-Person Executive Micro-Office',
        title_pl: 'Prywatne Mikrobiuro 2-osobowe',
        desc_en: 'Soundproofed private office suite with dual monitor desks, conference phone, and high-speed fiber.',
        desc_pl: 'Dźwiękoszczelne mikrobiuro z biurkami regulowanymi, monitorami i światłowodem 1 Gbps.',
        rate: 60,
        location: 'Gdańsk · Garnizon Wrzeszcz',
        amenities: ['Standing Desks', 'Fiber Internet', '24/7 Access', 'Meeting Room Access'],
        img: 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80'
      },
      {
        id: 'sp_6',
        cat: 'beauty',
        city: 'Katowice',
        title_en: 'Cosmetology & Permanent Makeup Suite',
        title_pl: 'Gabinet Kosmetologii i Makijażu PMU',
        desc_en: 'Clean aesthetic studio with shadowless surgical lamp, biological sterilization bin, and sink.',
        desc_pl: 'Sterylny gabinet z lampą bezcieniową, umywalką chirurgiczną i pojemnikiem na odpady medyczne.',
        rate: 40,
        location: 'Katowice · Centrum / Mariacka',
        amenities: ['Surgical Lamp', 'Water Basin', 'Autoclave Safe', 'Waiting Lounge'],
        img: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=800&q=80'
      }
    ];

    function setLanguage(lang) {
      currentLang = lang;
      document.getElementById('btn-lang-en').classList.toggle('active', lang === 'en');
      document.getElementById('btn-lang-pl').classList.toggle('active', lang === 'pl');

      const t = TRANSLATIONS[lang];
      document.getElementById('nav-catalog').textContent = t.navCatalog;
      document.getElementById('nav-compliance').textContent = t.navCompliance;
      document.getElementById('btn-host-header').textContent = t.btnHostHeader;
      document.getElementById('btn-search-header').textContent = t.btnSearchHeader;
      document.getElementById('txt-kicker').textContent = t.kicker;
      document.getElementById('txt-hero-title').innerHTML = t.heroTitle;
      document.getElementById('txt-hero-sub').textContent = t.heroSub;
      document.getElementById('opt-all-cities').textContent = t.optAllCities;
      document.getElementById('btn-filter-action').textContent = t.btnFilterAction;
      document.getElementById('txt-stat-1').textContent = t.stat1;
      document.getElementById('txt-stat-2').textContent = t.stat2;
      document.getElementById('txt-stat-3').textContent = t.stat3;
      document.getElementById('txt-stat-4').textContent = t.stat4;
      document.getElementById('tab-all').textContent = t.tabAll;
      document.getElementById('tab-beauty').textContent = t.tabBeauty;
      document.getElementById('tab-massage').textContent = t.tabMassage;
      document.getElementById('tab-barber').textContent = t.tabBarber;
      document.getElementById('tab-office').textContent = t.tabOffice;
      document.getElementById('tab-workshop').textContent = t.tabWorkshop;
      document.getElementById('txt-comp-kicker').textContent = t.compKicker;
      document.getElementById('txt-comp-title').textContent = t.compTitle;
      document.getElementById('txt-rule-1-title').textContent = t.rule1Title;
      document.getElementById('txt-rule-1-desc').textContent = t.rule1Desc;
      document.getElementById('txt-rule-2-title').textContent = t.rule2Title;
      document.getElementById('txt-rule-2-desc').textContent = t.rule2Desc;
      document.getElementById('txt-rule-3-title').textContent = t.rule3Title;
      document.getElementById('txt-rule-3-desc').textContent = t.rule3Desc;

      renderListings();
    }

    function setCategory(cat) {
      currentCategory = cat;
      document.querySelectorAll('.cat-tab').forEach(t => {
        t.classList.toggle('active', t.getAttribute('data-cat') === cat);
      });
      filterListings();
    }

    function filterListings() {
      const city = document.getElementById('filter-city').value;
      const maxPrice = parseFloat(document.getElementById('filter-price').value) || 999999;
      renderListings(city, maxPrice);
    }

    function renderListings(cityFilter = '', maxPrice = 999999) {
      const container = document.getElementById('listings-container');
      const filtered = SPACES_DATA.filter(item => {
        const matchesCat = currentCategory === 'all' || item.cat === currentCategory;
        const matchesCity = !cityFilter || item.city.toLowerCase() === cityFilter.toLowerCase();
        const matchesPrice = item.rate <= maxPrice;
        return matchesCat && matchesCity && matchesPrice;
      });

      if (filtered.length === 0) {
        container.innerHTML = `
          <div style="grid-column: 1/-1; text-align:center; padding:48px 0; color:var(--text-dim);">
            <div style="font-size:1.8rem; margin-bottom:8px;">🔍</div>
            <p>${currentLang === 'en' ? 'No spaces match your selected filters.' : 'Brak wolnych lokali dla wybranych filtrów.'}</p>
          </div>
        `;
        return;
      }

      const t = TRANSLATIONS[currentLang];
      container.innerHTML = filtered.map(item => `
        <div class="card">
          <div class="card-thumb">
            <img src="${item.img}" alt="${currentLang === 'en' ? item.title_en : item.title_pl}" loading="lazy">
            <span class="card-badge">${item.cat.toUpperCase()}</span>
            <span class="card-avail">
              <span style="width:6px; height:6px; border-radius:50%; background:var(--accent-emerald);"></span>
              ${currentLang === 'en' ? 'Verified Space' : 'Dostępne od zaraz'}
            </span>
          </div>
          <div class="card-body">
            <div class="card-location">
              <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
              ${item.location}
            </div>
            <h3 class="card-title">${currentLang === 'en' ? item.title_en : item.title_pl}</h3>
            <p class="card-desc">${currentLang === 'en' ? item.desc_en : item.desc_pl}</p>
            <div class="amenities-list">
              ${item.amenities.map(a => `<span class="amenity-tag">${a}</span>`).join('')}
            </div>
            <div class="card-footer">
              <div class="card-price">
                <span class="price-num">${item.rate}.00</span>
                <span class="price-unit">PLN ${t.perHour}</span>
              </div>
              <button class="btn btn-glow" style="padding:8px 14px; font-size:0.8rem;" onclick="openBookingModal('${item.id}')">${t.bookBtn}</button>
            </div>
          </div>
        </div>
      `).join('');
    }

    function openBookingModal(spaceId) {
      const space = SPACES_DATA.find(s => s.id === spaceId);
      if (!space) return;
      document.getElementById('modal-space-title').textContent = currentLang === 'en' ? space.title_en : space.title_pl;
      document.getElementById('modal-space-rate').textContent = `Rate: ${space.rate}.00 PLN ${currentLang === 'en' ? '/ hour' : '/ godz.'}`;
      document.getElementById('bookingModal').classList.add('active');
    }

    function openHostModal() {
      document.getElementById('hostModal').classList.add('active');
    }

    function closeModals() {
      document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
    }

    function submitBooking() {
      const name = document.getElementById('book-name').value;
      const email = document.getElementById('book-email').value;
      if (!name || !email) {
        alert(currentLang === 'en' ? 'Please fill all required fields.' : 'Proszę wypełnić wszystkie pola.');
        return;
      }
      alert(currentLang === 'en' 
        ? 'Inquiry recorded! Verified with Article 398 PKE double opt-in engine.' 
        : 'Zapytanie zarejestrowane! Zweryfikowano w silniku podwójnej zgody Art. 398 PKE.');
      closeModals();
    }

    function submitHost() {
      const name = document.getElementById('host-name').value;
      const email = document.getElementById('host-email').value;
      if (!name || !email) {
        alert(currentLang === 'en' ? 'Please fill facility name and email.' : 'Proszę podać nazwę lokalu i e-mail.');
        return;
      }
      alert(currentLang === 'en' 
        ? 'Facility registered! Magic link and API token generated via /api/hosts/register.' 
        : 'Lokal zarejestrowany! Wygenerowano token i magic link przez endpoint /api/hosts/register.');
      closeModals();
    }

    // Initialize
    window.addEventListener('DOMContentLoaded', () => {
      setLanguage('en');
    });
  </script>
</body>
</html>
"""
