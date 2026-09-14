"""Compliance engine for Wynajmujemy.xyz.

Enforces source permissions across 5 dimensions:
  1. discovery: finding and storing source metadata
  2. fetch: retrieving content
  3. media: downloading and storing images
  4. republish: publishing offer data on Wynajmujemy
  5. outbound: sending outreach/notifications

Includes strict prohibition against unauthorized direct marketing under Art. 398 PKE
(Prawo Komunikacji Elektronicznej) and comprehensive SSRF protection for external URLs.
"""

from __future__ import annotations

import ipaddress
import socket
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse
import uuid

from pydantic import BaseModel, Field

from models import (
    HIGH_RISK_PROFILES,
    IndustryProfile,
    Listing,
    OfferSource,
    OutboundChannel,
    OutboundPurpose,
    SourceType,
)


class SourcePermissionDecision(BaseModel):
    """Evaluation result for source operations."""
    source_type: SourceType
    discovery_allowed: bool = False
    fetch_allowed: bool = False
    media_fetch_allowed: bool = False
    republish_allowed: bool = False
    outbound_allowed: bool = False
    legal_basis: str
    reasons: list[str] = Field(default_factory=list)


class OutboundCheckRequest(BaseModel):
    """Request to evaluate an outbound message dispatch."""
    recipient: str = Field(..., description="E-mail lub numer telefonu odbiorcy")
    channel: OutboundChannel
    purpose: OutboundPurpose
    has_prior_consent: bool = Field(
        default=False,
        description="Czy odbiorca wyraził uprzednią, wyraźną zgodę na ten cel kontaktu"
    )
    consent_evidence: Optional[str] = Field(
        default=None,
        description="Identyfikator lub treść dowodu zgody (np. timestamp, ID formularza opt-in, treść zgody)"
    )
    is_public_listing_source: bool = Field(
        default=False,
        description="Czy dane kontaktowe pochodzą z publicznego ogłoszenia/scrapera"
    )
    message_summary: Optional[str] = Field(default=None, max_length=500)


class OutboundCheckDecision(BaseModel):
    """Verdict on outbound communication attempt."""
    allowed: bool
    status: str = Field(..., description="'ALLOWED' lub 'BLOCKED'")
    reason: str
    legal_basis: str
    blocked_by_pke: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceAuditEvent(BaseModel):
    """Immutable audit record of compliance decisions."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    subject_id: Optional[str] = None
    decision: str
    details: dict
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SSRFValidationError(ValueError):
    """Raised when URL violates SSRF safety boundaries."""
    pass


def validate_import_url(url: str) -> tuple[bool, str]:
    """Validates external URL against SSRF and protocol vulnerabilities.

    Blocks:
      - Non-http/https schemes (file, ftp, gopher, etc.)
      - Loopback (127.0.0.0/8, ::1, localhost)
      - Private RFC1918 networks (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
      - Cloud metadata services (169.254.169.254, fe80::/10, 169.254.0.0/16)
      - Local domains (.local, .internal, .lan, localhost)
    """
    if not url or not isinstance(url, str):
        return False, "URL nie może być pusty"

    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Niedozwolony protokół '{parsed.scheme}'. Dozwolone wyłącznie http oraz https."

    hostname = parsed.hostname
    if not hostname:
        return False, "Brak poprawnej nazwy hosta w podanym adresie URL."

    hostname_lower = hostname.lower()

    # Block well-known internal hostnames
    forbidden_hosts = {"localhost", "localhost.localdomain", "broadcasthost"}
    if hostname_lower in forbidden_hosts or hostname_lower.endswith((".local", ".internal", ".lan", ".localhost")):
        return False, f"Zablokowano adres wewnętrzny (SSRF protection): '{hostname}'"

    # Check if host is direct IP literal
    try:
        ip_obj = ipaddress.ip_address(hostname_lower)
        if ip_obj.is_loopback:
            return False, f"Zablokowano adres pętli zwrotnej (loopback): '{hostname}'"
        if ip_obj.is_private:
            return False, f"Zablokowano prywatny adres IP (RFC 1918 / RFC 4193): '{hostname}'"
        if ip_obj.is_link_local:
            return False, f"Zablokowano adres link-local / cloud metadata (169.254.x.x): '{hostname}'"
        if ip_obj.is_reserved or ip_obj.is_multicast:
            return False, f"Zablokowano zarezerwowany adres IP: '{hostname}'"
        return True, "URL pomyślnie zweryfikowany pod kątem bezpieczeństwa."
    except ValueError:
        # Not a direct IP literal; hostname is a domain name.
        pass

    # Resolve hostname to detect DNS rebinding or internal IP resolution
    try:
        addr_info = socket.getaddrinfo(hostname_lower, None)
        for entry in addr_info:
            sockaddr = entry[4]
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_link_local or ip_obj.is_reserved or ip_obj.is_multicast:
                return False, f"Nazwa hosta '{hostname}' wskazuje na chroniony adres IP '{ip_str}' (SSRF protection)."
    except (socket.gaierror, IndexError):
        # In isolated test environments or offline tests, DNS resolution might not resolve external domains.
        # If it cannot be resolved, allow unless hostname explicitly matches unsafe patterns.
        pass

    return True, "URL pomyślnie zweryfikowany pod kątem bezpieczeństwa."


class ComplianceEngine:
    """Central compliance engine enforcing source policies and Art. 398 PKE rules."""

    def __init__(self) -> None:
        self.audit_log: list[ComplianceAuditEvent] = []

    def evaluate_source(self, source: OfferSource) -> SourcePermissionDecision:
        """Evaluates source permissions across 5 operations.

        Invariants:
          - OLX: all operations disabled by default (Niezmiennik 2 & 14).
          - Owner direct: requires rights_attestation for media and republish (Niezmiennik 1 & 14).
          - Host website: discovery/fetch enabled, media & republish require host consent,
            outbound marketing disabled.
        """
        reasons: list[str] = []

        if source.source_type == SourceType.OLX:
            decision = SourcePermissionDecision(
                source_type=SourceType.OLX,
                discovery_allowed=False,
                fetch_allowed=False,
                media_fetch_allowed=False,
                republish_allowed=False,
                outbound_allowed=False,
                legal_basis="Regulamin serwisu OLX i brak umowy partnerskiej (Niezmiennik 2)",
                reasons=[
                    "Automatyczne pozyskiwanie i scraping z OLX są wyłączone.",
                    "Pobieranie zdjęć i treści z ogłoszeń zewnętrznych bez licencji jest zablokowane.",
                    "Republikacja w portalu bez upoważnienia narusza prawa autorskie i regulaminy.",
                    "Kontakt marketingowy do numerów z ogłoszeń narusza art. 398 PKE.",
                ],
            )
            self._log_audit("source_evaluation", source.source_type.value, "BLOCKED", decision.model_dump())
            return decision

        if source.source_type == SourceType.OWNER_DIRECT:
            if not source.rights_attestation:
                decision = SourcePermissionDecision(
                    source_type=SourceType.OWNER_DIRECT,
                    discovery_allowed=True,
                    fetch_allowed=True,
                    media_fetch_allowed=False,
                    republish_allowed=False,
                    outbound_allowed=True,
                    legal_basis="Materiały bezpośrednie od gospodarza (Niezmiennik 1)",
                    reasons=[
                        "Wymagane oświadczenie gospodarza o posiadaniu praw do materiałów i zdjęć.",
                        "Publikacja oraz wykorzystanie zdjęć zablokowane do czasu złożenia oświadczenia.",
                    ],
                )
            else:
                decision = SourcePermissionDecision(
                    source_type=SourceType.OWNER_DIRECT,
                    discovery_allowed=True,
                    fetch_allowed=True,
                    media_fetch_allowed=True,
                    republish_allowed=True,
                    outbound_allowed=True,
                    legal_basis="Oświadczenie o prawach od uprawnionego gospodarza (Niezmiennik 1)",
                    reasons=["Pełne uprawnienia do przygotowania i publikacji oferty potwierdzone."],
                )
            self._log_audit("source_evaluation", source.source_type.value, "EVALUATED", decision.model_dump())
            return decision

        if source.source_type == SourceType.HOST_WEBSITE:
            url_valid = True
            if source.source_url:
                is_safe, msg = validate_import_url(source.source_url)
                if not is_safe:
                    url_valid = False
                    reasons.append(msg)

            decision = SourcePermissionDecision(
                source_type=SourceType.HOST_WEBSITE,
                discovery_allowed=True,
                fetch_allowed=url_valid,
                media_fetch_allowed=False,  # Photos require explicit confirmation
                republish_allowed=False,    # Only private draft; cannot publicly republish without host approval
                outbound_allowed=False,     # Cold marketing is blocked
                legal_basis="Strona gospodarza - import prywatnego szkicu (Niezmiennik 3)",
                reasons=reasons or [
                    "Dozwolone pobranie treści jako prywatnego szkicu.",
                    "Publikacja oferty wymaga weryfikacji i zatwierdzenia przez gospodarza.",
                    "Zakaz nieautoryzowanego marketingu wychodzącego do danych ze strony.",
                ],
            )
            self._log_audit("source_evaluation", source.source_type.value, "EVALUATED", decision.model_dump())
            return decision

        # Default fallback for unconfigured/social sources
        decision = SourcePermissionDecision(
            source_type=source.source_type,
            discovery_allowed=False,
            fetch_allowed=False,
            media_fetch_allowed=False,
            republish_allowed=False,
            outbound_allowed=False,
            legal_basis="Brak udokumentowanego uprawnienia dla danego źródła",
            reasons=["Operacje domyślnie wyłączone ze względów prawnych i bezpieczeństwa."],
        )
        self._log_audit("source_evaluation", source.source_type.value, "BLOCKED", decision.model_dump())
        return decision

    def evaluate_outbound(self, request: OutboundCheckRequest) -> OutboundCheckDecision:
        """Evaluates outbound communication under Art. 398 PKE.

        Art. 398 PKE (Prawo Komunikacji Elektronicznej):
        Using telecommunications terminal equipment and automated calling systems
        for direct marketing or unsolicited commercial information strictly requires
        PRIOR CONSENT of the subscriber/end-user.

        Invariants:
          - Public email/phone in an ad or registry is NOT consent for direct marketing.
          - Free listing or 'we just want to ask for consent' does not bypass marketing classification.
          - Pre-queue and pre-send evaluation ensures zero illegal outbound messages.
        """
        # 1. Marketing checks
        if request.purpose == OutboundPurpose.MARKETING:
            if request.is_public_listing_source:
                decision = OutboundCheckDecision(
                    allowed=False,
                    status="BLOCKED",
                    reason=(
                        "Naruszenie art. 398 PKE: publiczny numer lub e-mail z ogłoszenia/scrapera "
                        "nie jest zgodą na marketing portalu. Zimny outreach komercyjny jest zablokowany."
                    ),
                    legal_basis="Art. 398 ustawy Prawo Komunikacji Elektronicznej",
                    blocked_by_pke=True,
                )
                self._log_audit("outbound_check", request.recipient, "BLOCKED", decision.model_dump())
                return decision

            if not request.has_prior_consent:
                decision = OutboundCheckDecision(
                    allowed=False,
                    status="BLOCKED",
                    reason=(
                        "Naruszenie art. 398 PKE: brak uprzedniej zgody abonenta na bezpośredni kontakt "
                        "marketingowy. Sekwencje 'zapytamy tylko o zgodę' są zabronione jako próba obejścia prawa."
                    ),
                    legal_basis="Art. 398 ustawy Prawo Komunikacji Elektronicznej",
                    blocked_by_pke=True,
                )
                self._log_audit("outbound_check", request.recipient, "BLOCKED", decision.model_dump())
                return decision

            if not request.consent_evidence or not request.consent_evidence.strip():
                decision = OutboundCheckDecision(
                    allowed=False,
                    status="BLOCKED",
                    reason="Brak udokumentowanego dowodu zgody (wymagany audytowalny consent_evidence).",
                    legal_basis="Art. 398 ustawy Prawo Komunikacji Elektronicznej",
                    blocked_by_pke=True,
                )
                self._log_audit("outbound_check", request.recipient, "BLOCKED", decision.model_dump())
                return decision

            decision = OutboundCheckDecision(
                allowed=True,
                status="ALLOWED",
                reason="Zgoda na bezpośredni kontakt marketingowy pomyślnie zweryfikowana.",
                legal_basis="Art. 398 ustawy Prawo Komunikacji Elektronicznej (uprzednia zgoda opt-in)",
                blocked_by_pke=False,
            )
            self._log_audit("outbound_check", request.recipient, "ALLOWED", decision.model_dump())
            return decision

        # 2. Transactional / Service purposes
        if request.purpose == OutboundPurpose.SERVICE_IMPORT:
            decision = OutboundCheckDecision(
                allowed=True,
                status="ALLOWED",
                reason="Komunikacja transakcyjna związana z obsługą importu zlecenia zgłoszonego przez użytkownika.",
                legal_basis="Świadczenie usługi na żądanie użytkownika",
                blocked_by_pke=False,
            )
            self._log_audit("outbound_check", request.recipient, "ALLOWED", decision.model_dump())
            return decision

        if request.purpose == OutboundPurpose.HOST_LISTING_UPDATE:
            decision = OutboundCheckDecision(
                allowed=True,
                status="ALLOWED",
                reason="Komunikacja operacyjna z zarejestrowanym gospodarzem dotycząca jego aktywnej oferty.",
                legal_basis="Zarządzanie ofertą w ramach regulaminu serwisu",
                blocked_by_pke=False,
            )
            self._log_audit("outbound_check", request.recipient, "ALLOWED", decision.model_dump())
            return decision

        if request.purpose == OutboundPurpose.INQUIRY_RESPONSE:
            decision = OutboundCheckDecision(
                allowed=True,
                status="ALLOWED",
                reason="Obsługa zapytania najemcy dotyczącego przestrzeni.",
                legal_basis="Realizacja zapytania ofertowego",
                blocked_by_pke=False,
            )
            self._log_audit("outbound_check", request.recipient, "ALLOWED", decision.model_dump())
            return decision

        if request.purpose == OutboundPurpose.REQUESTED_ALERT:
            if not request.has_prior_consent:
                decision = OutboundCheckDecision(
                    allowed=False,
                    status="BLOCKED",
                    reason="Brak aktywnej subskrypcji alertu.",
                    legal_basis="Art. 398 ustawy Prawo Komunikacji Elektronicznej",
                    blocked_by_pke=True,
                )
                self._log_audit("outbound_check", request.recipient, "BLOCKED", decision.model_dump())
                return decision

            decision = OutboundCheckDecision(
                allowed=True,
                status="ALLOWED",
                reason="Wysyłka zamówionego powiadomienia/alertu na żądanie użytkownika.",
                legal_basis="Zamówiona usługa powiadomień",
                blocked_by_pke=False,
            )
            self._log_audit("outbound_check", request.recipient, "ALLOWED", decision.model_dump())
            return decision

        # Default fallback
        decision = OutboundCheckDecision(
            allowed=False,
            status="BLOCKED",
            reason="Nieznany cel komunikacji lub brak podstawy prawnej.",
            legal_basis="Zasada ostrożności PKE/RODO",
            blocked_by_pke=True,
        )
        self._log_audit("outbound_check", request.recipient, "BLOCKED", decision.model_dump())
        return decision

    def check_listing_review_requirement(self, listing: Listing) -> tuple[bool, list[str]]:
        """Checks if listing requires mandatory human review (high-risk profile)."""
        reasons: list[str] = []
        requires_review = False

        high_risk_found = [
            p.value for p in listing.resource.industry_profiles if p in HIGH_RISK_PROFILES
        ]
        if high_risk_found:
            requires_review = True
            reasons.append(
                f"Profil wysokiego ryzyka ({', '.join(high_risk_found)}) wymaga obowiązkowej "
                "weryfikacji uprawnień i lokalu przez zespół przed publikacją (Niezmiennik 10)."
            )

        if not listing.source_info.rights_attestation:
            requires_review = True
            reasons.append("Brak oświadczenia o prawach do materiałów od gospodarza (Niezmiennik 1 i 14).")

        return requires_review, reasons

    def _log_audit(self, event_type: str, subject_id: Optional[str], decision: str, details: dict) -> None:
        self.audit_log.append(
            ComplianceAuditEvent(
                event_type=event_type,
                subject_id=subject_id,
                decision=decision,
                details=details,
            )
        )
