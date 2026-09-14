"""FastAPI Server for Wynajmujemy.xyz.

Provides endpoints for:
  - Host registration and passwordless session authentication
  - Draft listing creation, updating, and read-only preview
  - Publication approval with cryptographic draft_hash & version concurrency check
  - High-risk review routing (beauty_med, tattoo_pmu -> pending_review)
  - Public catalog filtering with strict isolation of private drafts
  - Declared availability confirmation and stale listing detection
  - Source permission and Art. 398 PKE outbound compliance checking
  - Health panel and autocheck spots
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Optional
import uuid

from fastapi import Depends, FastAPI, HTTPException, Header, Query, status
from pydantic import BaseModel, Field

from compliance import (
    ComplianceEngine,
    OutboundCheckDecision,
    OutboundCheckRequest,
    SourcePermissionDecision,
    validate_import_url,
)
from models import (
    DeclaredAvailability,
    Host,
    IndustryProfile,
    Listing,
    ListingStatus,
    OfferSource,
    PricingRate,
    PricingUnit,
    Resource,
    ResourceType,
    SourceType,
    TimeWindow,
    Venue,
)

app = FastAPI(
    title="Wynajmujemy.xyz API",
    version="1.0.0",
    description="Backend API for professional space rental platform (offices/workstations/rooms)",
)

# Shared in-memory database store
class DataStore:
    def __init__(self) -> None:
        self.hosts: dict[str, Host] = {}              # host_id -> Host
        self.tokens: dict[str, str] = {}              # token -> host_id
        self.listings: dict[str, Listing] = {}        # listing_id -> Listing
        self.compliance_engine = ComplianceEngine()

    def clear(self) -> None:
        self.hosts.clear()
        self.tokens.clear()
        self.listings.clear()
        self.compliance_engine = ComplianceEngine()


db = DataStore()


# --- Request & Response Models ---

class HostRegisterRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    full_name: str = Field(..., min_length=2, max_length=120)
    phone: Optional[str] = None
    company_name: Optional[str] = None
    nip: Optional[str] = None


class HostRegisterResponse(BaseModel):
    host: Host
    token: str
    magic_link: str


class CreateDraftRequest(BaseModel):
    venue: Venue
    resource: Resource
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    rates: list[PricingRate] = Field(..., min_length=1)
    availability: Optional[DeclaredAvailability] = None
    photos: list[str] = Field(default_factory=list)
    source_info: OfferSource


class UpdateDraftRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=5, max_length=200)
    description: Optional[str] = Field(default=None, min_length=10, max_length=5000)
    rates: Optional[list[PricingRate]] = Field(default=None, min_length=1)
    availability: Optional[DeclaredAvailability] = None
    photos: Optional[list[str]] = None
    equipment: Optional[list[str]] = None
    amenities: Optional[list[str]] = None


class ListingPreviewResponse(BaseModel):
    listing: Listing
    version: int
    draft_hash: str
    is_high_risk: bool
    requires_manual_review: bool
    review_reasons: list[str]
    completeness_score: float
    missing_fields: list[str]
    can_approve: bool


class ApproveListingRequest(BaseModel):
    expected_version: int = Field(..., ge=1, description="Oczekiwany numer wersji szkicu")
    draft_hash: str = Field(..., description="Kryptograficzny SHA-256 z podglądu oferty")
    rights_attestation: bool = Field(
        ...,
        description="Oświadczenie gospodarza o prawach do materiałów i zdjęć"
    )


class ApproveListingResponse(BaseModel):
    listing_id: str
    status: ListingStatus
    version: int
    draft_hash: str
    message: str
    is_active: bool
    requires_manual_review: bool


# --- Dependencies ---

def get_current_host(authorization: Optional[str] = Header(default=None)) -> Host:
    """Extracts authenticated host from Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Brak lub niepoprawny nagłówek autoryzacji Bearer",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization[7:].strip()
    host_id = db.tokens.get(token)
    if not host_id or host_id not in db.hosts:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy lub wygasły token autoryzacyjny",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db.hosts[host_id]


# --- Health & Autocheck Endpoints ---

@app.get("/health", tags=["System"])
def health_check() -> dict[str, Any]:
    """Autocheck health panel and operational metrics."""
    now = datetime.now(timezone.utc)
    active_count = sum(1 for l in db.listings.values() if l.status == ListingStatus.ACTIVE)
    draft_count = sum(1 for l in db.listings.values() if l.status == ListingStatus.DRAFT)
    pending_count = sum(1 for l in db.listings.values() if l.status == ListingStatus.PENDING_REVIEW)
    audit_events_count = len(db.compliance_engine.audit_log)

    return {
        "status": "ok",
        "timestamp": now.isoformat(),
        "service": "Wynajmujemy.xyz API",
        "autocheck_spots": {
            "pke_compliance_engine": "active",
            "ssrf_protection": "active",
            "concurrency_hashing": "active",
            "catalog_isolation": "active",
        },
        "metrics": {
            "hosts_total": len(db.hosts),
            "listings_total": len(db.listings),
            "listings_active": active_count,
            "listings_draft": draft_count,
            "listings_pending_review": pending_count,
            "compliance_audit_events": audit_events_count,
        },
    }


# --- Host & Auth Endpoints ---

@app.post("/api/hosts/register", response_model=HostRegisterResponse, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register_host(req: HostRegisterRequest) -> HostRegisterResponse:
    """Registers new host and returns session token (passwordless flow)."""
    # Check if host already exists
    existing = next((h for h in db.hosts.values() if h.email.lower() == req.email.lower()), None)
    if existing:
        host = existing
    else:
        host = Host(
            email=req.email.lower(),
            full_name=req.full_name,
            phone=req.phone,
            company_name=req.company_name,
            nip=req.nip,
            is_verified=True,
        )
        db.hosts[host.id] = host

    # Generate session token
    token = f"wnj_{uuid.uuid4().hex}"
    db.tokens[token] = host.id
    magic_link = f"https://wynajmujemy.xyz/auth/verify?token={token}"

    return HostRegisterResponse(host=host, token=token, magic_link=magic_link)


@app.get("/api/hosts/me", response_model=Host, tags=["Auth"])
def get_host_profile(host: Host = Depends(get_current_host)) -> Host:
    """Returns profile of currently authenticated host."""
    return host


# --- Listings Endpoints ---

@app.post("/api/listings/draft", response_model=Listing, status_code=status.HTTP_201_CREATED, tags=["Listings"])
def create_listing_draft(
    req: CreateDraftRequest,
    host: Host = Depends(get_current_host),
) -> Listing:
    """Creates a new listing draft.
    
    Performs source policy validation, SSRF checks on external URLs,
    computes deterministic SHA-256 draft_hash, and sets version=1.
    """
    # 1. Source compliance check
    source_decision = db.compliance_engine.evaluate_source(req.source_info)
    if req.source_info.source_type == SourceType.OLX:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pobieranie i importowanie ofert z serwisu OLX jest zablokowane (Niezmiennik 2).",
        )

    # 2. SSRF check if URL is provided
    if req.source_info.source_url:
        is_safe, msg = validate_import_url(req.source_info.source_url)
        if not is_safe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Błąd bezpieczeństwa URL (SSRF): {msg}",
            )

    # 3. Build Resource & Venue links
    now = datetime.now(timezone.utc)
    venue = req.venue
    resource = req.resource
    resource.venue_id = venue.id

    availability = req.availability or DeclaredAvailability()
    if availability.last_confirmed_at is None:
        availability.last_confirmed_at = now

    initial_status = ListingStatus.DRAFT
    if req.source_info.source_type == SourceType.HOST_WEBSITE:
        initial_status = ListingStatus.AWAITING_OWNER

    listing = Listing(
        host_id=host.id,
        venue=venue,
        resource=resource,
        title=req.title,
        description=req.description,
        rates=req.rates,
        availability=availability,
        photos=req.photos,
        source_info=req.source_info,
        status=initial_status,
        version=1,
        created_at=now,
        updated_at=now,
        last_confirmed_at=now,
    )
    listing.update_draft_hash()

    db.listings[listing.id] = listing
    return listing


@app.patch("/api/listings/{listing_id}/draft", response_model=Listing, tags=["Listings"])
def update_listing_draft(
    listing_id: str,
    req: UpdateDraftRequest,
    host: Host = Depends(get_current_host),
) -> Listing:
    """Updates an existing listing draft.
    
    Increments version and recalculates draft_hash.
    """
    listing = db.listings.get(listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta nie została znaleziona.")

    if listing.host_id != host.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień do edycji tej oferty.",
        )

    if listing.status in (ListingStatus.ARCHIVED, ListingStatus.RENTED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nie można edytować zarchiwizowanej lub wynajętej oferty.",
        )

    # Apply updates
    if req.title is not None:
        listing.title = req.title
    if req.description is not None:
        listing.description = req.description
    if req.rates is not None:
        listing.rates = req.rates
    if req.availability is not None:
        listing.availability = req.availability
    if req.photos is not None:
        listing.photos = req.photos
    if req.equipment is not None:
        listing.resource.equipment = req.equipment
    if req.amenities is not None:
        listing.venue.amenities = req.amenities

    now = datetime.now(timezone.utc)
    listing.updated_at = now
    listing.version += 1
    listing.update_draft_hash()

    # If it was rejected or awaiting owner, reset to draft
    if listing.status in (ListingStatus.REJECTED, ListingStatus.AWAITING_OWNER):
        listing.status = ListingStatus.DRAFT

    return listing


@app.get("/api/listings/{listing_id}/preview", response_model=ListingPreviewResponse, tags=["Listings"])
def preview_listing_draft(
    listing_id: str,
    host: Host = Depends(get_current_host),
) -> ListingPreviewResponse:
    """Read-only preview of a listing draft.
    
    Strictly read-only: does not modify listing status or version.
    Returns completeness score, risk flags, and current cryptographic hash.
    """
    listing = db.listings.get(listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta nie została znaleziona.")

    if listing.host_id != host.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień do podglądu tej oferty.",
        )

    # Calculate completeness and missing fields
    missing: list[str] = []
    if len(listing.photos) == 0:
        missing.append("Brak zdjęć lokalu / gabinetu (min. 1 zalecane)")
    if len(listing.resource.equipment) == 0:
        missing.append("Brak określonego wyposażenia gabinetu/stanowiska")
    if not listing.venue.address:
        missing.append("Brak dokładnego adresu lokalu")

    total_checks = 5
    passed_checks = total_checks - len(missing)
    completeness = round(max(0.0, min(1.0, passed_checks / total_checks)), 2)

    requires_review, review_reasons = db.compliance_engine.check_listing_review_requirement(listing)
    can_approve = len(listing.rates) > 0 and bool(listing.title) and bool(listing.description)

    return ListingPreviewResponse(
        listing=listing,
        version=listing.version,
        draft_hash=listing.draft_hash,
        is_high_risk=listing.is_high_risk(),
        requires_manual_review=requires_review,
        review_reasons=review_reasons,
        completeness_score=completeness,
        missing_fields=missing,
        can_approve=can_approve,
    )


@app.post("/api/listings/{listing_id}/approve", response_model=ApproveListingResponse, tags=["Listings"])
def approve_listing_publication(
    listing_id: str,
    req: ApproveListingRequest,
    host: Host = Depends(get_current_host),
) -> ApproveListingResponse:
    """Approves listing publication.
    
    Enforces:
      1. Concurrency check: expected_version == listing.version AND draft_hash == listing.draft_hash.
         Returns 409 Conflict if draft changed in the background.
      2. Rights attestation: requires host to attest ownership of content/photos.
      3. Risk routing:
         - High risk (beauty_med, tattoo_pmu) -> PENDING_REVIEW (mandatory manual check).
         - Standard profiles -> ACTIVE (immediately published).
    """
    listing = db.listings.get(listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta nie została znaleziona.")

    if listing.host_id != host.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień do zatwierdzenia tej oferty.",
        )

    if listing.status in (ListingStatus.ARCHIVED, ListingStatus.RENTED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nie można zatwierdzić zarchiwizowanej lub wynajętej oferty.",
        )

    # 1. Concurrency guard (expected_version + draft_hash)
    if req.expected_version != listing.version or req.draft_hash != listing.draft_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Konflikt wersji szkicu. Przesłano wersję {req.expected_version} (hash: {req.draft_hash[:8]}...), "
                f"lecz aktualna wersja w systemie to {listing.version} (hash: {listing.draft_hash[:8]}...). "
                "Odśwież podgląd i zatwierdź aktualne dane oferty."
            ),
        )

    # 2. Rights attestation requirement
    if not req.rights_attestation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Wymagane jest potwierdzenie oświadczenia o posiadaniu praw do materiałów i zdjęć "
                "przed publikacją oferty (Niezmiennik 1 i 14)."
            ),
        )

    listing.source_info.rights_attestation = True
    now = datetime.now(timezone.utc)
    listing.updated_at = now
    listing.last_confirmed_at = now

    # 3. High-risk profile check
    is_high_risk = listing.is_high_risk()
    if is_high_risk:
        listing.status = ListingStatus.PENDING_REVIEW
        message = (
            "Oferta została przekazana do obowiązkowej weryfikacji przez zespół Wynajmujemy.xyz "
            "z uwagi na profil wysokiego ryzyka (medycyna estetyczna / tatuaż / PMU). Zostanie opublikowana "
            "po zatwierdzeniu uprawnień lokalu."
        )
        is_active = False
    else:
        listing.status = ListingStatus.ACTIVE
        listing.published_at = now
        message = "Oferta została pomyślnie zatwierdzona i opublikowana w publicznym katalogu."
        is_active = True

    listing.update_draft_hash()

    return ApproveListingResponse(
        listing_id=listing.id,
        status=listing.status,
        version=listing.version,
        draft_hash=listing.draft_hash,
        message=message,
        is_active=is_active,
        requires_manual_review=is_high_risk,
    )


# --- Catalog & Discovery (Public) ---

@app.get("/api/catalog", response_model=list[Listing], tags=["Catalog"])
@app.get("/api/listings", response_model=list[Listing], tags=["Catalog"])
def get_public_catalog(
    city: Optional[str] = Query(default=None, description="Miasto (np. Wrocław)"),
    district: Optional[str] = Query(default=None, description="Dzielnica"),
    resource_type: Optional[ResourceType] = Query(default=None, description="Typ zasobu"),
    industry_profile: Optional[IndustryProfile] = Query(default=None, description="Profil branżowy"),
    max_price_hourly: Optional[float] = Query(default=None, description="Maksymalna cena za godzinę w PLN"),
) -> list[Listing]:
    """Public search and discovery catalog.
    
    STRICT INVARIANT: Only listings with status == ACTIVE are returned!
    Drafts, awaiting_owner, pending_review, and paused listings are isolated and hidden.
    """
    results: list[Listing] = []

    for listing in db.listings.values():
        # Isolation guard
        if listing.status != ListingStatus.ACTIVE:
            continue

        if city and listing.venue.city.lower() != city.strip().lower():
            continue

        if district and (not listing.venue.district or listing.venue.district.lower() != district.strip().lower()):
            continue

        if resource_type and listing.resource.resource_type != resource_type:
            continue

        if industry_profile and industry_profile not in listing.resource.industry_profiles:
            continue

        if max_price_hourly is not None:
            hourly_rate = next((r for r in listing.rates if r.pricing_unit == PricingUnit.PER_HOUR), None)
            if not hourly_rate or hourly_rate.amount_pln > max_price_hourly:
                continue

        results.append(listing)

    return results


# --- Availability & Stale Management ---

@app.post("/api/listings/{listing_id}/confirm-availability", response_model=Listing, tags=["Listings"])
def confirm_listing_availability(
    listing_id: str,
    host: Host = Depends(get_current_host),
) -> Listing:
    """Host confirms that declared availability is up to date.
    
    Refreshes last_confirmed_at timestamp. If listing was paused_stale, restores it to ACTIVE.
    """
    listing = db.listings.get(listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta nie została znaleziona.")

    if listing.host_id != host.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień do potwierdzenia dostępności tej oferty.",
        )

    now = datetime.now(timezone.utc)
    listing.last_confirmed_at = now
    if listing.availability:
        listing.availability.last_confirmed_at = now

    if listing.status == ListingStatus.PAUSED_STALE:
        listing.status = ListingStatus.ACTIVE

    listing.updated_at = now
    listing.update_draft_hash()
    return listing


@app.post("/api/maintenance/pause-stale", tags=["Maintenance"])
def pause_stale_listings(max_days: int = 30) -> dict[str, Any]:
    """Scans active listings and moves them to PAUSED_STALE if unconfirmed for >30 days."""
    now = datetime.now(timezone.utc)
    paused_count = 0
    cutoff = now - timedelta(days=max_days)

    for listing in db.listings.values():
        if listing.status == ListingStatus.ACTIVE:
            confirmed = listing.last_confirmed_at
            if confirmed and confirmed.tzinfo is None:
                confirmed = confirmed.replace(tzinfo=timezone.utc)

            if not confirmed or confirmed < cutoff:
                listing.status = ListingStatus.PAUSED_STALE
                listing.updated_at = now
                paused_count += 1

    return {"status": "ok", "paused_stale_count": paused_count, "cutoff": cutoff.isoformat()}


# --- Compliance Inspection Endpoints ---

@app.post("/api/compliance/check-source", response_model=SourcePermissionDecision, tags=["Compliance"])
def check_source_compliance(source: OfferSource) -> SourcePermissionDecision:
    """Direct verification of source permissions across the 5 dimensions."""
    return db.compliance_engine.evaluate_source(source)


@app.post("/api/compliance/check-outbound", response_model=OutboundCheckDecision, tags=["Compliance"])
def check_outbound_compliance(req: OutboundCheckRequest) -> OutboundCheckDecision:
    """Verifies outbound communication against Art. 398 PKE."""
    return db.compliance_engine.evaluate_outbound(req)
