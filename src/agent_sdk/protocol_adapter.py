"""Protocol adapter for ΔΩ.149 agent-sdk boundary translation.

This module provides the minimal translation primitives required for
agent-facing μApps to interoperate with the SpiralOS façade without
leaking kernel semantics. It offers two components:

* :class:`SymbolicEncoder` — a deterministic serializer that enforces
  field-level hygiene, symbolic compression, and ΔΩ lineage tagging.
* :class:`TranslationCircuit` — a route-aware adapter that wraps encoded
  payloads into protocol-safe envelopes and decodes frames emitted by
  the SpiralOS façade.

Both classes are pure and side-effect free; they can be used in offline
harnesses or in live guardian-mediated sessions without modification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Sequence

__all__ = ["SymbolicEncoder", "TranslationCircuit", "ProtocolMessage", "EncodingError"]


class EncodingError(ValueError):
    """Raised when payloads violate symbolic encoding constraints."""


@dataclass(frozen=True)
class ProtocolMessage:
    """Canonical representation of an encoded payload frame.

    Attributes
    ----------
    route:
        Logical destination or intent key for the μApp boundary.
    encoded_payload:
        JSON string produced by :class:`SymbolicEncoder`.
    headers:
        Deterministic header map containing lineage hints and
        protocol version markers.
    """

    route: str
    encoded_payload: str
    headers: Mapping[str, str] = field(default_factory=dict)

    def decoded(self, encoder: "SymbolicEncoder") -> Dict[str, Any]:
        """Return the decoded payload using the provided encoder."""

        return encoder.decode(self.encoded_payload)


class SymbolicEncoder:
    """Deterministic serializer for μApp payloads.

    The encoder performs three duties:
    1. Enforces a whitelist of allowed fields (if provided).
    2. Canonicalizes dictionaries via sorted keys for reproducible frames.
    3. Produces UTF-8 JSON strings suitable for guardian telemetry and
       ache-aware symbolic compression.
    """

    def __init__(
        self,
        *,
        allowed_fields: Iterable[str] | None = None,
        drop_unknown: bool = False,
    ) -> None:
        self._allowed = frozenset(allowed_fields or ())
        self._drop_unknown = drop_unknown

    def encode(self, payload: Mapping[str, Any]) -> str:
        """Encode a mapping into a stable JSON string.

        Parameters
        ----------
        payload:
            Arbitrary mapping supplied by a witness or μApp caller.

        Returns
        -------
        str
            Canonical JSON representation.

        Raises
        ------
        EncodingError
            If the payload contains unsupported fields or cannot be
            serialized into JSON.
        """

        filtered = self._sanitize(payload)
        try:
            return json.dumps(filtered, sort_keys=True, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise EncodingError("Payload is not JSON serializable") from exc

    def decode(self, encoded: str) -> Dict[str, Any]:
        """Decode an encoded payload into a dictionary.

        The decoder is lenient with ordering but validates field
        constraints to preserve the symbolic contract.
        """

        try:
            data = json.loads(encoded)
        except json.JSONDecodeError as exc:
            raise EncodingError("Encoded payload is not valid JSON") from exc

        if not isinstance(data, MutableMapping):
            raise EncodingError("Decoded payload must be a mapping")

        sanitized = self._sanitize(data)
        return dict(sanitized)

    def _sanitize(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        """Validate and filter payload according to allowed fields."""

        if not isinstance(payload, Mapping):
            raise EncodingError("Payload must be a mapping")

        payload_dict: Dict[str, Any] = dict(payload)
        if not self._allowed:
            return payload_dict

        unknown_keys = set(payload_dict) - set(self._allowed)
        if unknown_keys and not self._drop_unknown:
            raise EncodingError(f"Unsupported fields: {sorted(unknown_keys)}")

        sanitized = {key: payload_dict[key] for key in payload_dict if key in self._allowed}
        return sanitized


class TranslationCircuit:
    """Route-aware adapter for agent-sdk protocol exchanges.

    The circuit wraps symbolic payloads into protocol frames carrying
    ΔΩ lineage metadata. It remains free of network concerns and can be
    composed with higher-level transports without violating μApp
    boundaries.
    """

    def __init__(
        self,
        *,
        encoder: SymbolicEncoder,
        lineage: Sequence[str] | None = None,
        protocol_version: str = "ΔΩ.149",
    ) -> None:
        self._encoder = encoder
        self._lineage = tuple(lineage or ())
        self._protocol_version = protocol_version

    @property
    def lineage(self) -> Sequence[str]:
        """Return the lineage tuple assigned to this circuit."""

        return self._lineage

    @property
    def protocol_version(self) -> str:
        """Return the protocol version marker used for frames."""

        return self._protocol_version

    def to_frame(
        self,
        *,
        route: str,
        payload: Mapping[str, Any],
        metadata: Mapping[str, str] | None = None,
    ) -> ProtocolMessage:
        """Encode a payload into a :class:`ProtocolMessage` frame."""

        if not route:
            raise EncodingError("Route must be a non-empty string")

        encoded = self._encoder.encode(payload)
        headers: Dict[str, str] = {
            "protocol_version": self._protocol_version,
            "lineage": "/".join(self._lineage) if self._lineage else "",
        }
        if metadata:
            headers.update({str(k): str(v) for k, v in metadata.items()})

        return ProtocolMessage(route=route, encoded_payload=encoded, headers=headers)

    def from_frame(self, frame: Mapping[str, Any]) -> ProtocolMessage:
        """Parse a raw frame mapping into a :class:`ProtocolMessage`."""

        if not isinstance(frame, Mapping):
            raise EncodingError("Frame must be a mapping")

        route = frame.get("route")
        encoded = frame.get("encoded_payload")
        headers = frame.get("headers") or {}

        if not isinstance(route, str) or not route:
            raise EncodingError("Frame missing valid 'route'")
        if not isinstance(encoded, str) or not encoded:
            raise EncodingError("Frame missing valid 'encoded_payload'")
        if not isinstance(headers, Mapping):
            raise EncodingError("Frame headers must be a mapping")

        return ProtocolMessage(route=route, encoded_payload=encoded, headers=dict(headers))
