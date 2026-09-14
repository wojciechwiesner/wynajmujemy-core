"""Comprehensive verification test suite for Wynajmujemy.xyz.

Covers:
  1. Data models (models.py): ResourceType vs IndustryProfile, PricingRate, DeclaredAvailability,
     deterministic cryptographic SHA-256 draft hashing.
  2. Compliance engine (compliance.py): source permission evaluation, SSRF validation,
     Art. 398 PKE direct marketing prohibitions.
  3. API Server (server.py): host registration, draft lifecycle, read-only preview,
     concurrency collision detection (version + draft_hash), high-risk profile review routing,
     strict catalog isolation, availability staleness and reactivation.
"""

from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient

from compliance import (
    ComplianceEngine,
    OutboundCheckRequest,
    validate_import_url,
)
from models import (
    AvailabilityType,
    DeclaredAvailability,
    Host,
    IndustryProfile,
    Listing,
    ListingStatus,
    OfferSource,
    OutboundChannel,
    OutboundPurpose,
    PricingRate,
    PricingUnit,
    Resource,
    ResourceType,
    SourceType,
    TimeWindow,
    Venue,
)
from server import app, db


@pytest.fixture(autouse=True)
def reset_database():
    """Ensures a clean state before each test."""
    db.clear()
    yield
    db.clear()


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


# =====================================================================
# 1. Models & Cryptographic Hashing Tests
# =====================================================================

def test_models_resource_and_industry_profile_separation():
    """Separation invariant: resource_type and industry_profile are independent."""
    venue = Venue(
        name="Studio Przestrzeni",
        address="ul. Świdnicka 10",
        city="Wrocław",
        district="Stare Miasto",
    )
    # A single office room can serve both beauty and massage specialists
    resource = Resource(
        venue_id=venue.id,
        name="Gabinet A",
        resource_type=ResourceType.OFFICE_ROOM,
        industry_profiles=[IndustryProfile.BEAUTY, IndustryProfile.MASSAGE_WELLNESS],
        equipment=["Kozetka elektryczna", "Lampa lupa", "Autoklaw"],
        area_sqm=18.5,
    )
    assert resource.resource_type == ResourceType.OFFICE_ROOM
    assert len(resource.industry_profiles) == 2
    assert IndustryProfile.BEAUTY in resource.industry_profiles
    assert IndustryProfile.MASSAGE_WELLNESS in resource.industry_profiles


def test_pricing_rate_minor_units_and_conversions():
    """Prices must be strictly positive and stored in grosze (minor units)."""
    rate = PricingRate(
        pricing_unit=PricingUnit.PER_HOUR,
        amount_minor=6500,  # 65.00 PLN
        currency="PLN",
        tax_included=True,
        deposit_minor=20000, # 200.00 PLN
    )
    assert rate.amount_minor == 6500
    assert rate.amount_pln == 65.0
    assert rate.deposit_pln == 200.0

    # Validation: amount_minor cannot be zero or negative
    with pytest.raises(ValueError):
        PricingRate(pricing_unit=PricingUnit.PER_HOUR, amount_minor=0)


def test_time_window_validation():
    """TimeWindow enforces valid format and start < end."""
    valid_window = TimeWindow(day_of_week=1, start_time="08:00", end_time="16:00")
    assert valid_window.day_of_week == 1

    with pytest.raises(ValueError):
        # start_time >= end_time
        TimeWindow(day_of_week=1, start_time="17:00", end_time="09:00")


def test_declared_availability_staleness():
    """Availability older than 30 days must be recognized as stale."""
    now = datetime.now(timezone.utc)
    fresh_avail = DeclaredAvailability(last_confirmed_at=now - timedelta(days=10))
    assert fresh_avail.is_stale(max_age_days=30) is False

    stale_avail = DeclaredAvailability(last_confirmed_at=now - timedelta(days=35))
    assert stale_avail.is_stale(max_age_days=30) is True

    unconfirmed_avail = DeclaredAvailability(last_confirmed_at=None)
    assert unconfirmed_avail.is_stale(max_age_days=30) is True


def test_draft_hash_determinism_and_sensitivity():
    """Draft hash must be deterministic and sensitive to any business field edit."""
    venue = Venue(name="Gabinet Medyczny", address="ul. Dubois 5", city="Wrocław")
    resource = Resource(
        venue_id=venue.id,
        name="Gabinet 1",
        resource_type=ResourceType.OFFICE_ROOM,
        industry_profiles=[IndustryProfile.PSYCHOLOGY_CONSULTING],
    )
    rate = PricingRate(pricing_unit=PricingUnit.PER_HOUR, amount_minor=5000)
    source = OfferSource(source_type=SourceType.OWNER_DIRECT, rights_attestation=True)

    listing1 = Listing(
        host_id="host-1",
        venue=venue,
        resource=resource,
        title="Elegancki gabinet dla psychoterapeuty",
        description="Cicha i dyskretna przestrzeń w centrum Wrocławia z poczekalnią.",
        rates=[rate],
        source_info=source,
    )
    hash1 = listing1.compute_draft_hash()

    # Exact duplicate must yield identical hash
    listing2 = Listing(
        host_id="host-2", # Note: host_id is not part of canonical draft representation
        venue=venue,
        resource=resource,
        title="Elegancki gabinet dla psychoterapeuty",
        description="Cicha i dyskretna przestrzeń w centrum Wrocławia z poczekalnią.",
        rates=[rate],
        source_info=source,
    )
    hash2 = listing2.compute_draft_hash()
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex string

    # Modifying price must change hash
    listing2.rates = [PricingRate(pricing_unit=PricingUnit.PER_HOUR, amount_minor=5500)]
    hash3 = listing2.compute_draft_hash()
    assert hash1 != hash3

    # Modifying description must change hash
    listing2.rates = [rate]
    listing2.description = "Zmieniony opis gabinetu."
    hash4 = listing2.compute_draft_hash()
    assert hash1 != hash4


# =====================================================================
# 2. Compliance Engine & Art. 398 PKE Tests
# =====================================================================

def test_compliance_olx_source_completely_blocked():
    """OLX source must be disabled across all 5 operational dimensions (Niezmiennik 2)."""
    engine = ComplianceEngine()
    source = OfferSource(source_type=SourceType.OLX, source_url="https://www.olx.pl/d/oferta/gabinet-CID3.html")
    decision = engine.evaluate_source(source)

    assert decision.discovery_allowed is False
    assert decision.fetch_allowed is False
    assert decision.media_fetch_allowed is False
    assert decision.republish_allowed is False
    assert decision.outbound_allowed is False
    assert "Regulamin serwisu OLX" in decision.legal_basis


def test_compliance_owner_direct_rights_attestation():
    """Owner materials require explicit rights attestation for republishing & media."""
    engine = ComplianceEngine()

    # Without attestation: republish and media are blocked
    source_no_rights = OfferSource(source_type=SourceType.OWNER_DIRECT, rights_attestation=False)
    dec_no_rights = engine.evaluate_source(source_no_rights)
    assert dec_no_rights.republish_allowed is False
    assert dec_no_rights.media_fetch_allowed is False

    # With attestation: authorized
    source_with_rights = OfferSource(source_type=SourceType.OWNER_DIRECT, rights_attestation=True)
    dec_with_rights = engine.evaluate_source(source_with_rights)
    assert dec_with_rights.republish_allowed is True
    assert dec_with_rights.media_fetch_allowed is True


def test_compliance_ssrf_validator():
    """SSRF guardrail blocks local, private, and cloud metadata addresses."""
    # Loopback
    is_safe, _ = validate_import_url("http://127.0.0.1:8000/listing")
    assert is_safe is False
    is_safe, _ = validate_import_url("http://localhost:3000/spec")
    assert is_safe is False

    # Cloud metadata
    is_safe, _ = validate_import_url("http://169.254.169.254/latest/meta-data")
    assert is_safe is False

    # Private RFC 1918
    is_safe, _ = validate_import_url("http://192.168.1.100/page")
    assert is_safe is False
    is_safe, _ = validate_import_url("http://10.0.0.1/admin")
    assert is_safe is False

    # Non-HTTP protocol
    is_safe, _ = validate_import_url("file:///etc/passwd")
    assert is_safe is False

    # Valid external public domain
    is_safe, _ = validate_import_url("https://salon-urody.wroclaw.pl/oferta-wynajmu")
    assert is_safe is True


def test_compliance_outbound_art_398_pke_marketing_block():
    """Art. 398 PKE strictly prohibits unsolicited direct marketing."""
    engine = ComplianceEngine()

    # 1. Marketing to scraped public ad without consent -> BLOCKED
    req_scraped = OutboundCheckRequest(
        recipient="kontakt@fryzjer-wroclaw.pl",
        channel=OutboundChannel.EMAIL,
        purpose=OutboundPurpose.MARKETING,
        has_prior_consent=False,
        is_public_listing_source=True,
    )
    dec_scraped = engine.evaluate_outbound(req_scraped)
    assert dec_scraped.allowed is False
    assert dec_scraped.status == "BLOCKED"
    assert dec_scraped.blocked_by_pke is True
    assert "publiczny numer lub e-mail z ogłoszenia" in dec_scraped.reason

    # 2. Marketing sequence asking 'just for consent' without prior consent -> BLOCKED
    req_unsolicited = OutboundCheckRequest(
        recipient="+48600111222",
        channel=OutboundChannel.SMS,
        purpose=OutboundPurpose.MARKETING,
        has_prior_consent=False,
    )
    dec_unsolicited = engine.evaluate_outbound(req_unsolicited)
    assert dec_unsolicited.allowed is False
    assert dec_unsolicited.status == "BLOCKED"
    assert dec_unsolicited.blocked_by_pke is True

    # 3. Marketing with explicit documented prior consent -> ALLOWED
    req_consented = OutboundCheckRequest(
        recipient="gospodarz@studio.pl",
        channel=OutboundChannel.EMAIL,
        purpose=OutboundPurpose.MARKETING,
        has_prior_consent=True,
        consent_evidence="FORM_OPTIN_2026_09_14_ID_98213",
    )
    dec_consented = engine.evaluate_outbound(req_consented)
    assert dec_consented.allowed is True
    assert dec_consented.status == "ALLOWED"
    assert dec_consented.blocked_by_pke is False


def test_compliance_outbound_transactional_allowed():
    """Transactional communication (service_import, host_listing_update) is permitted."""
    engine = ComplianceEngine()

    # Service import response
    req_import = OutboundCheckRequest(
        recipient="user@wroclaw.pl",
        channel=OutboundChannel.EMAIL,
        purpose=OutboundPurpose.SERVICE_IMPORT,
    )
    dec_import = engine.evaluate_outbound(req_import)
    assert dec_import.allowed is True
    assert dec_import.status == "ALLOWED"

    # Host operational listing update
    req_update = OutboundCheckRequest(
        recipient="host@wroclaw.pl",
        channel=OutboundChannel.EMAIL,
        purpose=OutboundPurpose.HOST_LISTING_UPDATE,
    )
    dec_update = engine.evaluate_outbound(req_update)
    assert dec_update.allowed is True
    assert dec_update.status == "ALLOWED"


# =====================================================================
# 3. FastAPI Server API Workflow Tests
# =====================================================================

def test_host_registration_and_authentication(client):
    """Host can register and receive session token."""
    res = client.post(
        "/api/hosts/register",
        json={
            "email": "karolina@salonwroclaw.pl",
            "full_name": "Karolina Nowak",
            "phone": "+48501234567",
            "company_name": "Studio Urody Nowak",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert "token" in data
    assert data["host"]["email"] == "karolina@salonwroclaw.pl"
    token = data["token"]

    # Verify protected endpoint
    me_res = client.get("/api/hosts/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["full_name"] == "Karolina Nowak"

    # Unauthorized access
    unauth_res = client.get("/api/hosts/me", headers={"Authorization": "Bearer invalid_token"})
    assert unauth_res.status_code == 401


def test_create_draft_and_read_only_preview(client):
    """Draft creation calculates version 1 and draft_hash; preview is strictly read-only."""
    # 1. Register host
    host_res = client.post(
        "/api/hosts/register",
        json={"email": "anna@fizjoterapia.pl", "full_name": "Anna Kowalska"},
    )
    token = host_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create draft
    draft_payload = {
        "venue": {
            "name": "Centrum Terapii Ciała",
            "address": "ul. Grabiszyńska 45",
            "city": "Wrocław",
            "district": "Fabryczna",
            "amenities": ["Wi-Fi", "Poczekalnia", "Winda"],
        },
        "resource": {
            "name": "Gabinet Masażu i Fizjoterapii",
            "resource_type": "office_room",
            "industry_profiles": ["massage_wellness"],
            "equipment": ["Stół do masażu Habys", "Prześcieradła", "Ręczniki"],
            "area_sqm": 16.0,
            "max_capacity": 2,
        },
        "title": "Przestronny gabinet do masażu i rehabilitacji",
        "description": "Jasny gabinet z oknem, wyposażony w profesjonalny stół, w przyjaznym centrum medycznym.",
        "rates": [
            {"pricing_unit": "per_hour", "amount_minor": 4500, "tax_included": True},
            {"pricing_unit": "per_day", "amount_minor": 25000, "tax_included": True},
        ],
        "availability": {
            "availability_type": "fixed_schedule",
            "time_windows": [
                {"day_of_week": 1, "start_time": "08:00", "end_time": "20:00"},
                {"day_of_week": 2, "start_time": "08:00", "end_time": "20:00"},
            ],
            "min_slot_duration_minutes": 60,
        },
        "photos": ["https://img.wynajmujemy.xyz/foto1.jpg"],
        "source_info": {
            "source_type": "owner_direct",
            "rights_attestation": False,
        },
    }

    create_res = client.post("/api/listings/draft", json=draft_payload, headers=headers)
    assert create_res.status_code == 201
    listing = create_res.json()
    listing_id = listing["id"]
    assert listing["version"] == 1
    assert listing["status"] == "draft"
    assert len(listing["draft_hash"]) == 64
    initial_hash = listing["draft_hash"]

    # 3. Preview draft - must be read-only!
    prev_res = client.get(f"/api/listings/{listing_id}/preview", headers=headers)
    assert prev_res.status_code == 200
    prev_data = prev_res.json()
    assert prev_data["version"] == 1
    assert prev_data["draft_hash"] == initial_hash
    assert prev_data["is_high_risk"] is False
    assert prev_data["can_approve"] is True

    # Check that GET preview did not mutate version or status
    check_res = client.get(f"/api/listings/{listing_id}/preview", headers=headers)
    assert check_res.json()["version"] == 1
    assert check_res.json()["listing"]["status"] == "draft"


def test_create_draft_ssrf_and_olx_blocking(client):
    """Server rejects draft creation if source violates SSRF or is OLX."""
    host_res = client.post(
        "/api/hosts/register",
        json={"email": "security@test.pl", "full_name": "Tester"},
    )
    token = host_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    base_payload = {
        "venue": {"name": "Lokal", "address": "ul. Testowa 1", "city": "Wrocław"},
        "resource": {
            "name": "Stanowisko",
            "resource_type": "workstation",
            "industry_profiles": ["beauty"],
        },
        "title": "Stanowisko manicure",
        "description": "Wynajem stanowiska w salonie urody",
        "rates": [{"pricing_unit": "per_hour", "amount_minor": 3000}],
    }

    # 1. Reject OLX source
    olx_payload = {
        **base_payload,
        "source_info": {"source_type": "olx", "source_url": "https://olx.pl/d/oferta/stanowisko"},
    }
    olx_res = client.post("/api/listings/draft", json=olx_payload, headers=headers)
    assert olx_res.status_code == 403
    assert "OLX jest zablokowane" in olx_res.json()["detail"]

    # 2. Reject SSRF URL
    ssrf_payload = {
        **base_payload,
        "source_info": {
            "source_type": "host_website",
            "source_url": "http://169.254.169.254/latest/meta-data",
        },
    }
    ssrf_res = client.post("/api/listings/draft", json=ssrf_payload, headers=headers)
    assert ssrf_res.status_code == 400
    assert "SSRF" in ssrf_res.json()["detail"]


def test_draft_update_increments_version_and_updates_hash(client):
    """Updating a draft increments version and recalculates hash."""
    host_res = client.post(
        "/api/hosts/register",
        json={"email": "marek@psycholog.pl", "full_name": "Marek Nowak"},
    )
    token = host_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/api/listings/draft",
        json={
            "venue": {"name": "Gabinet Wroc", "address": "ul. Ruska 1", "city": "Wrocław"},
            "resource": {
                "name": "Gabinet Konsultacyjny",
                "resource_type": "office_room",
                "industry_profiles": ["psychology_consulting"],
            },
            "title": "Gabinet psychoterapii",
            "description": "Przytulny gabinet na godziny",
            "rates": [{"pricing_unit": "per_hour", "amount_minor": 5000}],
            "source_info": {"source_type": "owner_direct", "rights_attestation": False},
        },
        headers=headers,
    )
    listing_id = create_res.json()["id"]
    initial_hash = create_res.json()["draft_hash"]
    assert create_res.json()["version"] == 1

    # Update draft
    update_res = client.patch(
        f"/api/listings/{listing_id}/draft",
        json={"title": "Ekskluzywny gabinet psychoterapii i coachingu"},
        headers=headers,
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["version"] == 2
    assert updated["draft_hash"] != initial_hash
    assert updated["title"] == "Ekskluzywny gabinet psychoterapii i coachingu"


def test_approval_concurrency_conflict_detection(client):
    """Attempting approval with stale version or mismatched draft_hash returns HTTP 409 Conflict."""
    host_res = client.post(
        "/api/hosts/register",
        json={"email": "pawel@trener.pl", "full_name": "Paweł Trener"},
    )
    token = host_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/api/listings/draft",
        json={
            "venue": {"name": "Studio Szkoleń", "address": "ul. Kościuszki 15", "city": "Wrocław"},
            "resource": {
                "name": "Sala Warsztatowa",
                "resource_type": "training_room",
                "industry_profiles": ["training_professional"],
            },
            "title": "Sala szkoleniowa na 12 osób",
            "description": "Wyposażona w rzutnik, flipchart i Wi-Fi.",
            "rates": [{"pricing_unit": "per_hour", "amount_minor": 8000}],
            "source_info": {"source_type": "owner_direct", "rights_attestation": False},
        },
        headers=headers,
    )
    listing_id = create_res.json()["id"]
    initial_hash = create_res.json()["draft_hash"]

    # Another edit occurs in background
    client.patch(
        f"/api/listings/{listing_id}/draft",
        json={"title": "Sala szkoleniowa na 15 osób z rzutnikiem"},
        headers=headers,
    )

    # Attempting to approve using the old hash & version 1 must trigger 409 Conflict
    approve_res = client.post(
        f"/api/listings/{listing_id}/approve",
        json={
            "expected_version": 1,
            "draft_hash": initial_hash,
            "rights_attestation": True,
        },
        headers=headers,
    )
    assert approve_res.status_code == 409
    assert "Konflikt wersji szkicu" in approve_res.json()["detail"]


def test_approval_rights_attestation_requirement(client):
    """Approval without rights_attestation returns HTTP 400 Bad Request."""
    host_res = client.post(
        "/api/hosts/register",
        json={"email": "monika@studio.pl", "full_name": "Monika Studio"},
    )
    token = host_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/api/listings/draft",
        json={
            "venue": {"name": "Beauty Salon", "address": "ul. Oławska 2", "city": "Wrocław"},
            "resource": {
                "name": "Stanowisko Wizażu",
                "resource_type": "workstation",
                "industry_profiles": ["beauty"],
            },
            "title": "Stanowisko do makijażu",
            "description": "Lustro z oświetleniem bezcieniowym",
            "rates": [{"pricing_unit": "per_hour", "amount_minor": 3500}],
            "source_info": {"source_type": "owner_direct", "rights_attestation": False},
        },
        headers=headers,
    )
    listing_id = create_res.json()["id"]
    current_hash = create_res.json()["draft_hash"]

    approve_res = client.post(
        f"/api/listings/{listing_id}/approve",
        json={
            "expected_version": 1,
            "draft_hash": current_hash,
            "rights_attestation": False,  # Host refused or forgot attestation
        },
        headers=headers,
    )
    assert approve_res.status_code == 400
    assert "Wymagane jest potwierdzenie oświadczenia o posiadaniu praw" in approve_res.json()["detail"]


def test_approval_high_risk_profile_routed_to_pending_review(client):
    """High risk profiles (beauty_med, tattoo_pmu) are routed to pending_review instead of active."""
    host_res = client.post(
        "/api/hosts/register",
        json={"email": "dr.kamil@medestetica.pl", "full_name": "Dr Kamil Medycyna"},
    )
    token = host_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # High risk listing: beauty_med
    create_res = client.post(
        "/api/listings/draft",
        json={
            "venue": {"name": "Klinika Med Estetycznej", "address": "ul. Piłsudskiego 10", "city": "Wrocław"},
            "resource": {
                "name": "Gabinet Zabiegowy",
                "resource_type": "office_room",
                "industry_profiles": ["beauty_med"],
                "equipment": ["Fotel zabiegowy", "Autoklaw medyczny kl. B"],
            },
            "title": "Gabinet zabiegowy dla lekarza medycyny estetycznej",
            "description": "Zgodny z wymogami sanepidu dla zabiegów inwazyjnych.",
            "rates": [{"pricing_unit": "per_hour", "amount_minor": 12000}],
            "source_info": {"source_type": "owner_direct", "rights_attestation": True},
        },
        headers=headers,
    )
    listing_id = create_res.json()["id"]
    current_hash = create_res.json()["draft_hash"]

    approve_res = client.post(
        f"/api/listings/{listing_id}/approve",
        json={
            "expected_version": 1,
            "draft_hash": current_hash,
            "rights_attestation": True,
        },
        headers=headers,
    )
    assert approve_res.status_code == 200
    data = approve_res.json()
    assert data["status"] == "pending_review"
    assert data["is_active"] is False
    assert data["requires_manual_review"] is True
    assert "profil wysokiego ryzyka" in data["message"]


def test_approval_standard_profile_activates_immediately(client):
    """Standard profile (e.g. massage_wellness) activates immediately upon approval."""
    host_res = client.post(
        "/api/hosts/register",
        json={"email": "tomasz@masaz.pl", "full_name": "Tomasz Masażysta"},
    )
    token = host_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/api/listings/draft",
        json={
            "venue": {"name": "Harmonia", "address": "ul. Dubois 20", "city": "Wrocław"},
            "resource": {
                "name": "Pokój Relaksacyjny",
                "resource_type": "office_room",
                "industry_profiles": ["massage_wellness"],
            },
            "title": "Gabinet masażu na Krzykach",
            "description": "Przytulny gabinet z matami i stołem do masażu.",
            "rates": [{"pricing_unit": "per_hour", "amount_minor": 5000}],
            "source_info": {"source_type": "owner_direct", "rights_attestation": True},
        },
        headers=headers,
    )
    listing_id = create_res.json()["id"]
    current_hash = create_res.json()["draft_hash"]

    approve_res = client.post(
        f"/api/listings/{listing_id}/approve",
        json={
            "expected_version": 1,
            "draft_hash": current_hash,
            "rights_attestation": True,
        },
        headers=headers,
    )
    assert approve_res.status_code == 200
    data = approve_res.json()
    assert data["status"] == "active"
    assert data["is_active"] is True
    assert data["requires_manual_review"] is False


def test_catalog_isolation_of_drafts_and_unapproved_listings(client):
    """Public catalog must strictly show ONLY active listings (Niezmiennik 8 & 26)."""
    host_res = client.post(
        "/api/hosts/register",
        json={"email": "host@katalog.pl", "full_name": "Katalog Host"},
    )
    token = host_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create draft (not approved)
    client.post(
        "/api/listings/draft",
        json={
            "venue": {"name": "Lokal 1", "address": "ul. Prosta 1", "city": "Wrocław"},
            "resource": {"name": "Gabinet 1", "resource_type": "office_room", "industry_profiles": ["beauty"]},
            "title": "Szkic nieopublikowany",
            "description": "Opis szkicu",
            "rates": [{"pricing_unit": "per_hour", "amount_minor": 4000}],
            "source_info": {"source_type": "owner_direct", "rights_attestation": True},
        },
        headers=headers,
    )

    # 2. Create and approve standard listing (becomes ACTIVE)
    create_res = client.post(
        "/api/listings/draft",
        json={
            "venue": {"name": "Lokal 2", "address": "ul. Prosta 2", "city": "Wrocław", "district": "Śródmieście"},
            "resource": {"name": "Gabinet 2", "resource_type": "office_room", "industry_profiles": ["massage_wellness"]},
            "title": "Opublikowany gabinet masażu",
            "description": "Opis opublikowanego gabinetu",
            "rates": [{"pricing_unit": "per_hour", "amount_minor": 6000}],
            "source_info": {"source_type": "owner_direct", "rights_attestation": True},
        },
        headers=headers,
    )
    id2 = create_res.json()["id"]
    hash2 = create_res.json()["draft_hash"]
    client.post(
        f"/api/listings/{id2}/approve",
        json={"expected_version": 1, "draft_hash": hash2, "rights_attestation": True},
        headers=headers,
    )

    # 3. Check public catalog
    cat_res = client.get("/api/catalog")
    assert cat_res.status_code == 200
    items = cat_res.json()
    assert len(items) == 1
    assert items[0]["id"] == id2
    assert items[0]["title"] == "Opublikowany gabinet masażu"

    # Filter catalog by district and industry
    filtered_res = client.get("/api/catalog?district=Śródmieście&industry_profile=massage_wellness")
    assert len(filtered_res.json()) == 1

    empty_res = client.get("/api/catalog?district=Krzyki")
    assert len(empty_res.json()) == 0


def test_availability_stale_detection_and_reconfirmation(client):
    """Listings without availability confirmation for >30 days are paused and can be reactivated."""
    host_res = client.post(
        "/api/hosts/register",
        json={"email": "stale@test.pl", "full_name": "Stale Host"},
    )
    token = host_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/api/listings/draft",
        json={
            "venue": {"name": "Stale Venue", "address": "ul. Dawna 1", "city": "Wrocław"},
            "resource": {"name": "Gabinet", "resource_type": "office_room", "industry_profiles": ["beauty"]},
            "title": "Gabinet kosmetyczny",
            "description": "Świetny gabinet w dobrej cenie",
            "rates": [{"pricing_unit": "per_hour", "amount_minor": 5000}],
            "source_info": {"source_type": "owner_direct", "rights_attestation": True},
        },
        headers=headers,
    )
    listing_id = create_res.json()["id"]
    h = create_res.json()["draft_hash"]

    # Approve to make active
    client.post(
        f"/api/listings/{listing_id}/approve",
        json={"expected_version": 1, "draft_hash": h, "rights_attestation": True},
        headers=headers,
    )

    # Manually age the confirmation date to 40 days ago
    listing = db.listings[listing_id]
    listing.last_confirmed_at = datetime.now(timezone.utc) - timedelta(days=40)

    # Run maintenance check
    maint_res = client.post("/api/maintenance/pause-stale?max_days=30")
    assert maint_res.status_code == 200
    assert maint_res.json()["paused_stale_count"] == 1
    assert db.listings[listing_id].status == ListingStatus.PAUSED_STALE

    # It must disappear from public catalog
    cat_res = client.get("/api/catalog")
    assert len(cat_res.json()) == 0

    # Host reconfirms availability
    reconfirm_res = client.post(f"/api/listings/{listing_id}/confirm-availability", headers=headers)
    assert reconfirm_res.status_code == 200
    assert reconfirm_res.json()["status"] == "active"

    # It reappears in public catalog
    cat_res_after = client.get("/api/catalog")
    assert len(cat_res_after.json()) == 1


def test_health_check_endpoint(client):
    """Health endpoint reports operational status and autocheck spots."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["autocheck_spots"]["pke_compliance_engine"] == "active"
    assert data["autocheck_spots"]["ssrf_protection"] == "active"
    assert "metrics" in data


def test_approval_tattoo_pmu_routed_to_pending_review(client):
    """Tattoo & PMU profile is high risk and must be routed to pending_review (Niezmiennik 10)."""
    host_res = client.post(
        "/api/hosts/register",
        json={"email": "ink@tattoo-wroclaw.pl", "full_name": "Tattoo Master"},
    )
    token = host_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/api/listings/draft",
        json={
            "venue": {"name": "Ink Studio", "address": "ul. Szewska 12", "city": "Wrocław"},
            "resource": {
                "name": "Stanowisko Tatuażu",
                "resource_type": "workstation",
                "industry_profiles": ["tattoo_pmu"],
                "equipment": ["Fotel hydrauliczny", "Lampa ring", "Autoklaw"],
            },
            "title": "Stanowisko dla tatuatora w centrum",
            "description": "W pełni wyposażone stanowisko z odbiorem sanepidu pod tatuaż i PMU.",
            "rates": [{"pricing_unit": "per_day", "amount_minor": 20000}],
            "source_info": {"source_type": "owner_direct", "rights_attestation": True},
        },
        headers=headers,
    )
    listing_id = create_res.json()["id"]
    h = create_res.json()["draft_hash"]

    approve_res = client.post(
        f"/api/listings/{listing_id}/approve",
        json={"expected_version": 1, "draft_hash": h, "rights_attestation": True},
        headers=headers,
    )
    assert approve_res.status_code == 200
    data = approve_res.json()
    assert data["status"] == "pending_review"
    assert data["is_active"] is False
    assert data["requires_manual_review"] is True


def test_compliance_endpoints_api(client):
    """Direct API endpoints for compliance check correctly evaluate sources and PKE outbound."""
    # 1. Check OLX source
    source_res = client.post(
        "/api/compliance/check-source",
        json={"source_type": "olx", "source_url": "https://olx.pl/oferta"},
    )
    assert source_res.status_code == 200
    s_data = source_res.json()
    assert s_data["discovery_allowed"] is False
    assert s_data["republish_allowed"] is False

    # 2. Check Outbound without consent (PKE block)
    outbound_res = client.post(
        "/api/compliance/check-outbound",
        json={
            "recipient": "marketing@cel.pl",
            "channel": "email",
            "purpose": "marketing",
            "has_prior_consent": False,
        },
    )
    assert outbound_res.status_code == 200
    o_data = outbound_res.json()
    assert o_data["allowed"] is False
    assert o_data["blocked_by_pke"] is True
    assert o_data["status"] == "BLOCKED"


def test_non_owner_forbidden_from_edit_and_approve(client):
    """A host cannot edit or approve a listing owned by another host (403 Forbidden)."""
    # Host 1
    h1_res = client.post("/api/hosts/register", json={"email": "h1@test.pl", "full_name": "Host One"})
    t1 = h1_res.json()["token"]

    # Host 2
    h2_res = client.post("/api/hosts/register", json={"email": "h2@test.pl", "full_name": "Host Two"})
    t2 = h2_res.json()["token"]

    # Host 1 creates draft
    draft_res = client.post(
        "/api/listings/draft",
        json={
            "venue": {"name": "Lokal H1", "address": "ul. H1 1", "city": "Wrocław"},
            "resource": {"name": "G1", "resource_type": "office_room", "industry_profiles": ["beauty"]},
            "title": "Gabinet H1",
            "description": "Opis H1 dla testu uprawnień",
            "rates": [{"pricing_unit": "per_hour", "amount_minor": 5000}],
            "source_info": {"source_type": "owner_direct", "rights_attestation": True},
        },
        headers={"Authorization": f"Bearer {t1}"},
    )
    listing_id = draft_res.json()["id"]
    h = draft_res.json()["draft_hash"]

    # Host 2 tries to edit Host 1's draft -> 403
    patch_res = client.patch(
        f"/api/listings/{listing_id}/draft",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {t2}"},
    )
    assert patch_res.status_code == 403

    # Host 2 tries to approve Host 1's draft -> 403
    appr_res = client.post(
        f"/api/listings/{listing_id}/approve",
        json={"expected_version": 1, "draft_hash": h, "rights_attestation": True},
        headers={"Authorization": f"Bearer {t2}"},
    )
    assert appr_res.status_code == 403


def test_archived_listing_approval_rejected(client):
    """Cannot approve an archived listing (400 Bad Request)."""
    h_res = client.post("/api/hosts/register", json={"email": "arch@test.pl", "full_name": "Arch Host"})
    tok = h_res.json()["token"]
    headers = {"Authorization": f"Bearer {tok}"}

    create_res = client.post(
        "/api/listings/draft",
        json={
            "venue": {"name": "Lokal Arch", "address": "ul. Arch 1", "city": "Wrocław"},
            "resource": {"name": "G_Arch", "resource_type": "office_room", "industry_profiles": ["beauty"]},
            "title": "Gabinet do archiwizacji",
            "description": "Opis do archiwizacji",
            "rates": [{"pricing_unit": "per_hour", "amount_minor": 5000}],
            "source_info": {"source_type": "owner_direct", "rights_attestation": True},
        },
        headers=headers,
    )
    listing_id = create_res.json()["id"]
    h = create_res.json()["draft_hash"]

    # Manually archive listing
    db.listings[listing_id].status = ListingStatus.ARCHIVED

    # Attempt to approve archived listing -> 400
    appr_res = client.post(
        f"/api/listings/{listing_id}/approve",
        json={"expected_version": 1, "draft_hash": h, "rights_attestation": True},
        headers=headers,
    )
    assert appr_res.status_code == 400
    assert "Nie można zatwierdzić zarchiwizowanej" in appr_res.json()["detail"]
