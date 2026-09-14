# Changelog

All notable changes to the Wynajmujemy.xyz Backend Module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-14

### Added
- **Data Models (`models.py`)**:
  - Pydantic v2 schemas for `Venue`, `Resource`, `PricingRate`, `DeclaredAvailability`, `OfferSource`, `Host`, and `Listing`.
  - Distinct separation of `ResourceType` (`office_room`, `workstation`, `training_room`, `whole_venue`) and `IndustryProfile` (`beauty`, `massage_wellness`, `psychology_consulting`, `beauty_med`, `tattoo_pmu`, `training_professional`).
  - Strict Polish Złoty currency formatting and integer minor units (`amount_minor` in grosze).
  - TimeWindow and DeclaredAvailability validation with 30-day staleness tracking.
  - Deterministic SHA-256 cryptographic `draft_hash` calculation with canonical JSON normalization.
  - Identification of high-risk industry profiles (`beauty_med`, `tattoo_pmu`).
  - Hierarchical parent-resource conflict awareness.

- **Compliance Engine (`compliance.py`)**:
  - 5-dimensional source permission checking matrix (`discovery`, `fetch`, `media`, `republish`, `outbound`).
  - Default full block for OLX portal sources without enterprise agreement.
  - SSRF guardrail (`validate_import_url`) rejecting loopback (`127.0.0.1`, `::1`), private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `fc00::/7`), link-local/cloud metadata (`169.254.169.254`), and internal hostnames.
  - Outbound Marketing Engine under Art. 398 PKE:
    - Strict prohibition of unsolicited direct marketing and cold outreach.
    - Scraped public contacts do not constitute commercial consent.
    - Transactional notifications allowed for user-initiated service imports and host listing administration.
    - Pre-queue and pre-send evaluation with immutable audit logging.

- **FastAPI Server (`server.py`)**:
  - Host registration with passwordless Bearer session token authentication.
  - Listing draft creation with SSRF validation, policy check, and SHA-256 hashing.
  - Listing draft updates with version incrementing and hash recalculation.
  - Read-only draft preview with completeness metrics and risk analysis (strictly non-mutating).
  - Concurrency-protected publication approval endpoint requiring matching `expected_version` and `draft_hash`.
  - Mandatory host rights attestation check before publication.
  - Automatic routing of high-risk profiles (`beauty_med`, `tattoo_pmu`) to `pending_review`.
  - Public catalog endpoint strictly isolating drafts and unapproved offers.
  - Availability reconfirmation and automated 30-day stale pausing.
  - Health check endpoint `/health` with autocheck spots and service telemetry.

- **Test Suite (`test_wynajmujemy.py`)**:
  - 25 comprehensive verification tests exercising models, compliance engine, SSRF guardrails, Art. 398 PKE blocks, and all FastAPI endpoints.
  - DoD PASS confirmed with 100% test success rate.
