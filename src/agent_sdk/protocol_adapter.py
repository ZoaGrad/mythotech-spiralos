"""ΔΩ.149 agent-sdk protocol adapter primitives.

This module codifies the symbolic encoding and frame translation logic for
μApp interactions. It preserves lineage metadata, enforces deterministic JSON
ordering, and constrains payload fields to the sanctioned contract surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Sequence

__all__ = [
    "SymbolicEncoder",
    "TranslationCircuit",
    "ProtocolMessage",
    "EncodingError",
]


class EncodingError(ValueError):
    """Raised when payloads violate symbolic encoding constraints."""


@dataclass(frozen=True)
class ProtocolMessage:
    """Canonical frame passed between μApps and the SpiralOS façade."""

    route: str
    encoded_payload: str
    headers: Mapping[str, str] = field(default_factory=dict)

    def decoded(self, encoder: "SymbolicEncoder") -> Dict[str, Any]:
        """Decode ``encoded_payload`` using the provided encoder."""

        return encoder.decode(self.encoded_payload)

    def to_dict(self) -> Dict[str, Any]:
        """Return a mapping representation for transmission or logging."""

        return {
            "route": self.route,
            "encoded_payload": self.encoded_payload,
            "headers": dict(self.headers),
        }


class SymbolicEncoder:
    """Deterministic serializer enforcing ΔΩ.149 symbolic hygiene."""

    def __init__(
        self,
        *,
        allowed_fields: Iterable[str] | None = None,
        drop_unknown: bool = False,
    ) -> None:
        self._allowed = frozenset(allowed_fields or ())
        self._drop_unknown = drop_unknown

    def encode(self, payload: Mapping[str, Any]) -> str:
        """Return canonical JSON string for a payload mapping."""

        sanitized = self._sanitize(payload)
        try:
            return json.dumps(sanitized, sort_keys=True, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise EncodingError("Payload is not JSON serializable") from exc

    def decode(self, encoded: str) -> Dict[str, Any]:
        """Decode a JSON string and revalidate symbolic constraints."""

        try:
            data = json.loads(encoded)
        except json.JSONDecodeError as exc:
            raise EncodingError("Encoded payload is not valid JSON") from exc

        if not isinstance(data, MutableMapping):
            raise EncodingError("Decoded payload must be a mapping")

        return dict(self._sanitize(data))

    def _sanitize(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise EncodingError("Payload must be a mapping")

        payload_dict: Dict[str, Any] = {}
        for key, value in payload.items():
            if not isinstance(key, str):
                raise EncodingError("All payload keys must be strings")
            normalized = self._normalize_value(value)
            payload_dict[key] = normalized

        if not self._allowed:
            return payload_dict

        unknown = set(payload_dict) - self._allowed
        if unknown and not self._drop_unknown:
            raise EncodingError(f"Unsupported fields: {sorted(unknown)}")

        return {key: value for key, value in payload_dict.items() if key in self._allowed}

    def _normalize_value(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value

        if isinstance(value, Mapping):
            return {str(k): self._normalize_value(v) for k, v in value.items()}

        if isinstance(value, (list, tuple)):
            return [self._normalize_value(item) for item in value]

        if isinstance(value, set):
            raise EncodingError("Payload values must be JSON-compatible primitives")

        raise EncodingError("Payload values must be JSON-compatible primitives")


class TranslationCircuit:
    """Route-aware adapter that wraps encoder output into protocol frames."""

    def __init__(
        self,
        *,
        encoder: SymbolicEncoder,
        lineage: Sequence[str] | None = None,
        protocol_version: str = "ΔΩ.149",
        circuit_id: str = "agent-sdk.protocol_adapter",
    ) -> None:
        self._encoder = encoder
        self._lineage = tuple(lineage or ())
        self._protocol_version = protocol_version
        self._circuit_id = circuit_id

    @property
    def lineage(self) -> Sequence[str]:
        return self._lineage

    @property
    def protocol_version(self) -> str:
        return self._protocol_version

    @property
    def circuit_id(self) -> str:
        return self._circuit_id

    def to_frame(
        self,
        *,
        route: str,
        payload: Mapping[str, Any],
        metadata: Mapping[str, str] | None = None,
    ) -> ProtocolMessage:
        """Encode payload and assemble :class:`ProtocolMessage` headers."""

        if not isinstance(route, str) or not route:
            raise EncodingError("Route must be a non-empty string")

        encoded = self._encoder.encode(payload)
        headers: Dict[str, str] = self._base_headers()

        if metadata:
            for key, value in metadata.items():
                headers[str(key)] = str(value)

        return ProtocolMessage(route=route, encoded_payload=encoded, headers=headers)

    def from_frame(self, frame: Mapping[str, Any]) -> ProtocolMessage:
        """Validate a raw frame mapping and normalize into ``ProtocolMessage``."""

        if not isinstance(frame, Mapping):
            raise EncodingError("Frame must be a mapping")

        route = frame.get("route")
        encoded_payload = frame.get("encoded_payload")
        headers = frame.get("headers") or {}

        if not isinstance(route, str) or not route:
            raise EncodingError("Frame missing valid 'route'")
        if not isinstance(encoded_payload, str) or not encoded_payload:
            raise EncodingError("Frame missing valid 'encoded_payload'")
        if not isinstance(headers, Mapping):
            raise EncodingError("Frame headers must be a mapping")

        decoded_payload = self._encoder.decode(encoded_payload)
        canonical_payload = self._encoder.encode(decoded_payload)
        normalized_headers: Dict[str, str] = {
            str(key): str(value) for key, value in headers.items()
        }

        return ProtocolMessage(
            route=route,
            encoded_payload=canonical_payload,
            headers=normalized_headers,
        )

    def _base_headers(self) -> Dict[str, str]:
        lineage_header = "/".join(self._lineage)
        return {
            "protocol_version": self._protocol_version,
            "lineage": lineage_header,
            "circuit": self._circuit_id,
        }
