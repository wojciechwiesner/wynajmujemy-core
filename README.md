# Wynajmujemy.xyz — Backend Module (MVP)

> **Live Production API & Swagger UI**: [https://wynajmujemy.theones.io/docs](https://wynajmujemy.theones.io/docs)  
> **Health Check**: [https://wynajmujemy.theones.io/health](https://wynajmujemy.theones.io/health)

> **B2B Marketplace for professional space rentals**: Offices, consulting rooms, workstations, and training halls (`gabinety, stanowiska, sale szkoleniowe`).

Platform connecting hosts with surplus space (beauty salons, massage studios, medical practices, coworking spaces) with verified professionals seeking flexible workspace without long-term commitments.

---

## Architecture & Tech Stack

- **Runtime**: Python 3.11+ / FastAPI
- **Data Modeling & Validation**: Pydantic v2 (strict typings, serialization, validators, autocheck spots)
- **Compliance & Security**:
  - **Art. 398 PKE Engine**: Strict blocking of unauthorized outbound marketing and commercial communications.
  - **Source Policy Engine**: Independent 5-dimensional permission matrix (`discovery`, `fetch`, `media`, `republish`, `outbound`).
  - **SSRF Guardrail**: Protection against loopback, private IPv4/IPv6 networks, and cloud instance metadata (e.g. AWS/GCP `169.254.169.254`).
  - **Optimistic Concurrency Locking**: Cryptographic SHA-256 `draft_hash` and integer `version` guarding against stale edits.
  - **Risk-Based Review Routing**: Mandatory human review (`pending_review`) for high-risk industry profiles (`beauty_med`, `tattoo_pmu`).
  - **Catalog Isolation**: Strict hiding of drafts, awaiting owner approval, and pending review listings from the public catalog.
  - **Staleness Tracking**: 30-day availability expiration (`paused_stale`) to prevent ghost listings.

---

## Project Structure

```
.
├── models.py            # Pydantic v2 data models (Venues, Resources, Rates, Availability, OfferSources)
├── compliance.py        # 5D Source Policy Engine, Art. 398 PKE Blocker, SSRF Guardrail
├── server.py            # FastAPI REST API (Auth, Drafts, Preview, Approval, Catalog, Health)
├── test_wynajmujemy.py  # 25 verification tests (DoD PASS)
├── CHANGELOG.md         # Semantic versioning changelog
└── README.md            # Project documentation
```

---

## Quickstart

### 1. Requirements
- Python 3.10+
- Dependencies: `fastapi`, `pydantic>=2.0`, `httpx`, `pytest`

### 2. Run Test Suite
```bash
pytest -v test_wynajmujemy.py
```

### 3. Start API Server
```bash
python3 -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Core API Endpoints

### 1. Host Authentication & Registration
- `POST /api/hosts/register` — Register a host and receive a passwordless Bearer session token.
- `GET /api/hosts/me` — Retrieve the authenticated host profile.

### 2. Listing Draft Management
- `POST /api/listings/draft` — Create a listing draft with automatic SHA-256 hash and version 1.
- `PATCH /api/listings/{id}/draft` — Update draft contents, increment version, and recalculate hash.
- `GET /api/listings/{id}/preview` — Read-only draft preview with completeness metrics and risk check (strictly idempotent, does not mutate status).

### 3. Publication Approval
- `POST /api/listings/{id}/approve` — Approve listing publication.
  - Requires `expected_version` and `draft_hash` (optimistic concurrency).
  - Requires `rights_attestation: true`.
  - Routes `beauty_med` and `tattoo_pmu` to `pending_review`.
  - Standard profiles activate immediately to `active`.

### 4. Public Catalog
- `GET /api/catalog` (or `/api/listings`) — Public search of active listings with filtering by city, district, profile, resource type, and price. Drafts and pending listings are strictly excluded.

### 5. Availability & Maintenance
- `POST /api/listings/{id}/confirm-availability` — Host confirms schedule freshness (reactivates `paused_stale` listings).
- `POST /api/maintenance/pause-stale` — Marks listings untouched for >30 days as `paused_stale`.

### 6. Compliance & Health
- `POST /api/compliance/check-source` — Evaluate source permissions across discovery, fetch, media, republish, and outbound.
- `POST /api/compliance/check-outbound` — Evaluate outbound message compliance under Art. 398 PKE.
- `GET /health` — Health check endpoint reporting autocheck spots and system metrics.

---

## SOTA Invariants Maintained

| Invariant | Description | Verification |
|---|---|---|
| **I1** | No publication without host rights attestation | HTTP 400 when `rights_attestation=False` |
| **I2** | No scraping/fetching without policy (OLX blocked by default) | HTTP 403 when source is OLX without partnership |
| **I3** | Strict Art. 398 PKE compliance: no cold marketing | BLOCKED status if purpose=marketing without prior opt-in |
| **I4** | SSRF protection for external source URLs | HTTP 400 rejecting private, loopback, and metadata IPs |
| **I5** | Concurrency conflict detection via `draft_hash` + `version` | HTTP 409 Conflict if draft was edited concurrently |
| **I6** | High-risk profile routing to manual review | Sets status to `pending_review` for `beauty_med` & `tattoo_pmu` |
| **I7** | Draft isolation from public catalog | Catalog only returns listings with `status == active` |
| **I8** | 30-day stale availability auto-pause | Transition to `paused_stale` if unconfirmed for >30 days |
