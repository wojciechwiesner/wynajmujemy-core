# Project State: Wynajmujemy.xyz Backend Module

Last Updated: 2026-09-14
Status: FEATURE_VERIFIED (DoD PASS)
Test Suite: 25/25 PASS (pytest)

---

## Phases & Deliverables

### Phase 1: Specification Analysis & Data Architecture
- [x] Read and analyze `/Users/wojciechwiesner/Downloads/wynajmujemy_xyz_specyfikacja_v1.md`
- [x] Implement Pydantic v2 data models in `models.py`
  - [x] `Venue`, `Resource`, `ResourceType` vs `IndustryProfile` separation
  - [x] `PricingRate` with PLN grosze (`amount_minor`)
  - [x] `DeclaredAvailability` with TimeWindows and 30-day stale tracking
  - [x] `OfferSource` with rights attestation
  - [x] Cryptographic deterministic SHA-256 `draft_hash` calculation
  - [x] Risk identification for `beauty_med` and `tattoo_pmu`

### Phase 2: Compliance & Legal Protection Engine
- [x] Implement 5D source permission engine in `compliance.py`
  - [x] Independent evaluation of `discovery`, `fetch`, `media`, `republish`, `outbound`
  - [x] Full block for OLX portal sources
  - [x] Requirement of `rights_attestation` for owner materials
  - [x] SSRF guardrail (`validate_import_url`) against loopback, private ranges, and cloud metadata (169.254.169.254)
- [x] Implement Outbound Marketing Engine under Art. 398 PKE
  - [x] Strict blocking of cold marketing without prior explicit consent
  - [x] Scraped public contacts do NOT constitute consent under Art. 398 PKE
  - [x] Dual-stage evaluation (pre-queue and pre-send) with audit logging

### Phase 3: REST API Implementation
- [x] Implement FastAPI server in `server.py`
  - [x] Host registration and passwordless session authentication (`/api/hosts/register`, `/api/hosts/me`)
  - [x] Draft listing creation with SSRF validation and SHA-256 calculation (`/api/listings/draft`)
  - [x] Draft listing updates with version incrementing and hash updates (`PATCH /api/listings/{id}/draft`)
  - [x] Read-only draft preview without side-effects (`GET /api/listings/{id}/preview`)
  - [x] Concurrency-protected publication approval with `expected_version` & `draft_hash` (`POST /api/listings/{id}/approve`)
  - [x] Mandatory rights attestation check
  - [x] Risk-based routing of `beauty_med` & `tattoo_pmu` to `pending_review`
  - [x] Public catalog strictly isolating drafts and unapproved offers (`GET /api/catalog`)
  - [x] Availability reconfirmation & 30-day stale pause maintenance (`/api/listings/{id}/confirm-availability`, `/api/maintenance/pause-stale`)
  - [x] Direct compliance check endpoints and Health telemetry (`/health`)

### Phase 4: Verification & DoD Confirmation
- [x] Write comprehensive test suite in `test_wynajmujemy.py` (25 tests)
- [x] Terminal verification: `pytest -v test_wynajmujemy.py` -> 25 PASSED (100%)
- [x] Documentation: README.md, CHANGELOG.md, and STATE.md
