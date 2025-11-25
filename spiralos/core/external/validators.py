"""Validation helpers for the External Witness Telemetry adapter."""

from __future__ import annotations

import hmac
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Optional, Set

from pydantic import ValidationError

from .schemas import ExternalQuarantineRecord, ExternalWitnessEvent

SignatureValidator = Callable[[ExternalWitnessEvent], bool]


class SchemaValidationError(ValueError):
    """Raised when inbound payloads cannot be coerced into the schema."""


def validate_event_schema(payload: Mapping[str, Any]) -> ExternalWitnessEvent:
    """Parse and validate an external witness event payload."""

    try:
        return ExternalWitnessEvent.model_validate(payload)
    except ValidationError as exc:  # noqa: B904 - surface structured error
        raise SchemaValidationError(str(exc)) from exc


def build_allowlist(sources: Iterable[str] | None = None) -> Set[str]:
    """Normalize an allowlist into a deterministic set."""

    return {item for item in sources or [] if item}


def is_allowlisted(event: ExternalWitnessEvent, allowlist: Set[str]) -> bool:
    return event.source in allowlist or event.witness_id in allowlist


def validate_signature(
    event: ExternalWitnessEvent,
    *,
    expected_signatures: Mapping[str, str] | None = None,
    validator: SignatureValidator | None = None,
) -> tuple[bool, str | None]:
    """Perform a lightweight signature check when available.

    The function is intentionally simple to preserve offline determinism. When an
    expected signature is provided for a witness or source, the comparison uses
    ``hmac.compare_digest`` to avoid timing leaks. Custom validators can be
    supplied for adapters that need stronger checks.
    """

    if validator:
        outcome = validator(event)
        return outcome, None if outcome else "invalid_signature"

    if not expected_signatures:
        return True, None

    expected = expected_signatures.get(event.witness_id) or expected_signatures.get(event.source)
    if expected is None:
        return True, None

    if not event.signature:
        return False, "missing_signature"

    is_valid = hmac.compare_digest(event.signature, expected)
    return is_valid, None if is_valid else "invalid_signature"


def compute_trust_score(
    event: ExternalWitnessEvent,
    *,
    allowlist: Set[str],
    expected_signatures: Mapping[str, str] | None = None,
    base_score: float = 0.5,
    signature_validator: SignatureValidator | None = None,
) -> tuple[float, str | None]:
    """Compute a deterministic trust score for an external event."""

    score = base_score
    reason = None

    if is_allowlisted(event, allowlist):
        score = 1.0
        reason = "allowlist"

    valid, signature_reason = validate_signature(
        event,
        expected_signatures=expected_signatures,
        validator=signature_validator,
    )
    if not valid:
        return 0.0, signature_reason or "invalid_signature"

    if event.signature:
        score = max(score, 0.9)
        reason = reason or "signature"

    return score, reason


def quarantine_record(reason: str, raw_event: Mapping[str, Any], detail: str | None = None) -> ExternalQuarantineRecord:
    """Create a quarantine record using the canonical schema."""

    return ExternalQuarantineRecord(reason=reason, raw_event=dict(raw_event), detail=detail)


__all__ = [
    "SchemaValidationError",
    "build_allowlist",
    "compute_trust_score",
    "is_allowlisted",
    "quarantine_record",
    "validate_event_schema",
    "validate_signature",
]
