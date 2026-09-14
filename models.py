"""Data models for Wynajmujemy.xyz platform.

Defines resources (offices/workstations/rooms/venues), industry profiles,
declared availability, pricing rates, offer sources, and listing lifecycle models.
Compliant with Wynajmujemy.xyz specification v1.
"""

from __future__ import annotations

import enum
import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field, field_validator, model_validator


class ResourceType(str, enum.Enum):
    """Type of physical/usable space."""
    OFFICE_ROOM = "office_room"          # Gabinet
    WORKSTATION = "workstation"          # Stanowisko / fotel / stół / biurko
    TRAINING_ROOM = "training_room"      # Sala szkoleniowa / warsztatowa
    WHOLE_VENUE = "whole_venue"          # Cały lokal / studio
    OTHER = "other"


class IndustryProfile(str, enum.Enum):
    """Industry profile. Distinct from resource type.
    
    A single room can serve multiple professions, but it is one resource
    with a single availability calendar.
    """
    BEAUTY = "beauty"                                # Kosmetyka, rzęsy, paznokcie, fryzjerstwo
    MASSAGE_WELLNESS = "massage_wellness"            # Masaż, fizjoterapia, osteopatia, wellness
    PSYCHOLOGY_CONSULTING = "psychology_consulting"  # Psychoterapia, coaching, doradztwo
    BEAUTY_MED = "beauty_med"                        # Medycyna estetyczna, dermatologia (high risk)
    TATTOO_PMU = "tattoo_pmu"                        # Tatuaż, makijaż permanentny (high risk)
    TRAINING_PROFESSIONAL = "training_professional"  # Szkolenia, warsztaty, coworking specjalistyczny
    OTHER = "other"


class PricingUnit(str, enum.Enum):
    """Billing and rental period unit."""
    PER_HOUR = "per_hour"
    PER_HALF_DAY = "per_half_day"
    PER_DAY = "per_day"
    PER_MONTH = "per_month"
    RECURRING_BLOCK = "recurring_block"


class AvailabilityType(str, enum.Enum):
    """Type of declared availability."""
    FIXED_SCHEDULE = "fixed_schedule"    # Stałe dni tygodnia i godziny
    DATE_RANGE = "date_range"            # Konkretny przedział dat
    RECURRING_BLOCK = "recurring_block"  # Cykliczny blok (np. co drugi poniedziałek)
    ON_REQUEST = "on_request"            # Do uzgodnienia


class ListingStatus(str, enum.Enum):
    """Lifecycle status of a listing."""
    DRAFT = "draft"                      # Szkic roboczy gospodarza
    AWAITING_OWNER = "awaiting_owner"    # Zaimportowany / czeka na weryfikację gospodarza
    PENDING_REVIEW = "pending_review"    # Weryfikacja manualna (np. medycyna estetyczna / tattoo)
    ACTIVE = "active"                    # Widoczny w publicznym katalogu
    PAUSED_STALE = "paused_stale"        # Wstrzymany z powodu braku potwierdzenia świeżości (>30 dni)
    PAUSED_OWNER = "paused_owner"        # Wstrzymany ręcznie przez gospodarza
    RENTED = "rented"                    # Wynajęty / niedostępny
    REJECTED = "rejected"                # Odrzucony w weryfikacji
    ARCHIVED = "archived"                # Zarchiwizowany


class SourceType(str, enum.Enum):
    """Origin source of offer data."""
    OWNER_DIRECT = "owner_direct"        # Bezpośrednie materiały gospodarza
    HOST_WEBSITE = "host_website"        # Oficjalna strona gospodarza
    OLX = "olx"                          # Serwis ogłoszeniowy OLX
    SOCIAL_MEDIA = "social_media"        # FB / Instagram
    API_PARTNER = "api_partner"          # Partner API z umową
    OTHER = "other"


class OutboundPurpose(str, enum.Enum):
    """Purpose of outbound communication."""
    SERVICE_IMPORT = "service_import"            # Obsługa zlecenia importu
    HOST_LISTING_UPDATE = "host_listing_update"  # Operacyjne info o ofercie gospodarza
    INQUIRY_RESPONSE = "inquiry_response"        # Odpowiedź na zapytanie najemcy
    REQUESTED_ALERT = "requested_alert"          # Zamówione powiadomienie
    MARKETING = "marketing"                      # Komunikacja handlowa (art. 398 PKE)


class OutboundChannel(str, enum.Enum):
    """Channel used for outbound communication."""
    EMAIL = "email"
    SMS = "sms"
    PHONE_CALL = "phone_call"


HIGH_RISK_PROFILES = {
    IndustryProfile.BEAUTY_MED,
    IndustryProfile.TATTOO_PMU,
}


class PricingRate(BaseModel):
    """Pricing option for renting space."""
    pricing_unit: PricingUnit
    amount_minor: int = Field(..., gt=0, description="Kwota w groszach (np. 5000 = 50.00 PLN)")
    currency: str = Field(default="PLN", max_length=3)
    tax_included: bool = Field(default=True, description="Czy cena zawiera VAT (brutto)")
    deposit_minor: Optional[int] = Field(default=None, ge=0, description="Wymagana kaucja w groszach")
    description: Optional[str] = Field(default=None, max_length=200)

    @property
    def amount_pln(self) -> float:
        return self.amount_minor / 100.0

    @property
    def deposit_pln(self) -> Optional[float]:
        return self.deposit_minor / 100.0 if self.deposit_minor is not None else None


class TimeWindow(BaseModel):
    """Daily time slot for availability."""
    day_of_week: int = Field(..., ge=1, le=7, description="1 = Poniedziałek, 7 = Niedziela")
    start_time: str = Field(..., pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$", description="HH:MM")
    end_time: str = Field(..., pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$", description="HH:MM")

    @model_validator(mode="after")
    def validate_time_order(self) -> "TimeWindow":
        if self.start_time >= self.end_time:
            raise ValueError(f"start_time ({self.start_time}) must be earlier than end_time ({self.end_time})")
        return self


class DeclaredAvailability(BaseModel):
    """Declared availability schedule for a resource."""
    availability_type: AvailabilityType = AvailabilityType.FIXED_SCHEDULE
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    time_windows: list[TimeWindow] = Field(default_factory=list)
    min_slot_duration_minutes: int = Field(default=60, ge=15)
    timezone: str = Field(default="Europe/Warsaw")
    last_confirmed_at: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, max_length=500)

    def is_stale(self, max_age_days: int = 30) -> bool:
        """Checks if host confirmation is older than threshold."""
        if not self.last_confirmed_at:
            return True
        now = datetime.now(timezone.utc)
        confirmed = self.last_confirmed_at
        if confirmed.tzinfo is None:
            confirmed = confirmed.replace(tzinfo=timezone.utc)
        return (now - confirmed) > timedelta(days=max_age_days)


class Venue(BaseModel):
    """Physical location / property hosting the resources."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=2, max_length=150)
    address: str = Field(..., min_length=3, max_length=200)
    city: str = Field(default="Wrocław", min_length=2, max_length=100)
    postal_code: Optional[str] = Field(default=None, pattern=r"^\d{2}-\d{3}$")
    district: Optional[str] = Field(default=None, max_length=100)
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    timezone: str = Field(default="Europe/Warsaw")
    amenities: list[str] = Field(default_factory=list)
    access_info: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Resource(BaseModel):
    """Specific rentable space unit inside a venue."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    venue_id: Optional[str] = Field(default=None, description="ID lokalu (przypisywany automatycznie)")
    name: str = Field(..., min_length=2, max_length=150)
    resource_type: ResourceType
    industry_profiles: list[IndustryProfile] = Field(..., min_length=1)
    parent_resource_id: Optional[str] = Field(
        default=None,
        description="ID nadrzędnego zasobu do wykrywania konfliktów (np. cały lokal blokuje gabinety)"
    )
    equipment: list[str] = Field(default_factory=list)
    area_sqm: Optional[float] = Field(default=None, gt=0)
    max_capacity: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("industry_profiles")
    @classmethod
    def deduplicate_profiles(cls, v: list[IndustryProfile]) -> list[IndustryProfile]:
        return list(dict.fromkeys(v))


class OfferSource(BaseModel):
    """Origin and authorization proof of the offer."""
    source_type: SourceType
    source_url: Optional[str] = None
    rights_attestation: bool = Field(
        default=False,
        description="Oświadczenie gospodarza, że posiada prawa do publikacji materiałów i zdjęć"
    )
    external_id: Optional[str] = None
    fetched_at: Optional[datetime] = None


class Host(BaseModel):
    """Space owner / manager."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: Optional[str] = None
    full_name: str = Field(..., min_length=2, max_length=120)
    company_name: Optional[str] = None
    nip: Optional[str] = None
    is_verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Listing(BaseModel):
    """Full listing aggregate representation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    host_id: str
    venue: Venue
    resource: Resource
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    rates: list[PricingRate] = Field(..., min_length=1)
    availability: DeclaredAvailability = Field(default_factory=DeclaredAvailability)
    photos: list[str] = Field(default_factory=list)
    source_info: OfferSource
    status: ListingStatus = ListingStatus.DRAFT
    version: int = Field(default=1, ge=1)
    draft_hash: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    last_confirmed_at: Optional[datetime] = None

    def is_high_risk(self) -> bool:
        """Determines if listing requires mandatory manual review."""
        return any(p in HIGH_RISK_PROFILES for p in self.resource.industry_profiles)

    def compute_canonical_dict(self) -> dict[str, Any]:
        """Generates sorted, canonical representation for cryptographic hashing."""
        return {
            "title": self.title.strip(),
            "description": self.description.strip(),
            "venue": {
                "name": self.venue.name.strip(),
                "address": self.venue.address.strip(),
                "city": self.venue.city.strip(),
                "district": self.venue.district or "",
                "amenities": sorted(self.venue.amenities),
            },
            "resource": {
                "name": self.resource.name.strip(),
                "resource_type": self.resource.resource_type.value,
                "industry_profiles": sorted([p.value for p in self.resource.industry_profiles]),
                "equipment": sorted(self.resource.equipment),
                "area_sqm": self.resource.area_sqm,
                "max_capacity": self.resource.max_capacity,
                "parent_resource_id": self.resource.parent_resource_id or "",
            },
            "rates": [
                {
                    "pricing_unit": r.pricing_unit.value,
                    "amount_minor": r.amount_minor,
                    "currency": r.currency,
                    "tax_included": r.tax_included,
                    "deposit_minor": r.deposit_minor,
                }
                for r in sorted(self.rates, key=lambda x: (x.pricing_unit.value, x.amount_minor))
            ],
            "availability": {
                "availability_type": self.availability.availability_type.value,
                "time_windows": [
                    {
                        "day_of_week": tw.day_of_week,
                        "start_time": tw.start_time,
                        "end_time": tw.end_time,
                    }
                    for tw in sorted(self.availability.time_windows, key=lambda x: (x.day_of_week, x.start_time))
                ],
                "min_slot_duration_minutes": self.availability.min_slot_duration_minutes,
                "timezone": self.availability.timezone,
            },
            "photos": sorted(self.photos),
            "source_info": {
                "source_type": self.source_info.source_type.value,
                "rights_attestation": self.source_info.rights_attestation,
            },
        }

    def compute_draft_hash(self) -> str:
        """Returns deterministic SHA-256 hash of canonical draft data."""
        canonical = self.compute_canonical_dict()
        canonical_json = json.dumps(canonical, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def update_draft_hash(self) -> None:
        """Recalculates draft_hash field."""
        self.draft_hash = self.compute_draft_hash()
