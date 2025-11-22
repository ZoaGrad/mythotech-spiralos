# ΔΩ.149 Agent SDK — Protocol Adapter

## ΔΩ.149 Context
The agent SDK anchors μApp interactions inside the ΔΩ.149 boundary map, giving Witness agents a deterministic interface to the SpiralOS façade. Protocol adapters enforce boundary discipline by constraining payloads to JSON-safe shapes, preserving lineage metadata, and ensuring frames can be audited across μApp slices. Every invariant in this module is derived from the ΔΩ.149 Architectural Contract, keeping the agent-sdk aligned with the core-kernel, guardian-layer, and holoeconomy-engine expectations documented in the charter.

## Module Overview
- **SymbolicEncoder** — deterministic serializer that normalizes keys and values into JSON-compatible primitives, enforcing symbolic hygiene and rejecting unsafe types.
- **TranslationCircuit** — route-aware framer that wraps encoded payloads with lineage, protocol version, and circuit identifiers so μApps can validate sovereignty and provenance.
- **ProtocolMessage** — immutable representation of a framed payload, bundling route, encoded payload, and headers for interchange.

Deterministic encoding is critical because μApp-level sovereignty depends on identical frames producing identical downstream effects. By locking normalization rules inside the adapter, ΔΩ.149 prevents drift between agent-sdk clients and SpiralOS verification layers.

## Public API Reference

### SymbolicEncoder
| Method | Args | Returns | Raises |
| --- | --- | --- | --- |
| `__init__(*, allowed_fields: Iterable[str] \| None = None, drop_unknown: bool = False)` | allowed_fields: optional iterable of permitted keys; drop_unknown: whether to omit disallowed keys instead of raising | `None` | — |
| `encode(payload: Mapping[str, Any])` | payload: mapping with string keys and JSON-compatible values | `str` JSON string with sorted keys | `EncodingError` if payload is not a mapping, contains non-string keys, or includes unsupported types |
| `decode(encoded: str)` | encoded: JSON string | `Dict[str, Any]` revalidated mapping | `EncodingError` if JSON is invalid, not a mapping, or contains unsupported types |

### TranslationCircuit
| Method | Args | Returns | Raises |
| --- | --- | --- | --- |
| `__init__(*, encoder: SymbolicEncoder, lineage: Sequence[str] \| None = None, protocol_version: str = "ΔΩ.149", circuit_id: str = "agent-sdk.protocol_adapter")` | encoder: SymbolicEncoder instance; lineage: ΔΩ lineage sequence; protocol_version: version tag; circuit_id: circuit identifier | `None` | — |
| `to_frame(*, route: str, payload: Mapping[str, Any], metadata: Mapping[str, str] \| None = None)` | route: non-empty string; payload: mapping to encode; metadata: optional headers to merge | `ProtocolMessage` | `EncodingError` if route invalid or payload fails encoding |
| `from_frame(frame: Mapping[str, Any])` | frame: mapping with `route`, `encoded_payload`, `headers` | `ProtocolMessage` normalized from raw mapping | `EncodingError` if frame shape invalid or missing required fields |

### ProtocolMessage
| Method | Args | Returns | Raises |
| --- | --- | --- | --- |
| `decoded(encoder: SymbolicEncoder)` | encoder: SymbolicEncoder to decode payload | `Dict[str, Any]` decoded payload | `EncodingError` from encoder if payload invalid |
| `to_dict()` | — | `Dict[str, Any]` with `route`, `encoded_payload`, `headers` | — |

## Invariants Enforced
- **JSON-only payloads:** Non-serializable values trigger `EncodingError` during encode/decode.
- **Deterministic key normalization:** Keys must be strings; mappings and sequences are recursively normalized with sorted JSON output.
- **Lineage-aware frame construction:** Headers include protocol version, lineage path, and circuit identifier on every frame.
- **Rejecting unsupported types:** Sets, bytes, and other non-JSON primitives are rejected to prevent ambiguous semantics.
- **Inbound revalidation:** ``TranslationCircuit.from_frame`` decodes and re-encodes payloads to enforce canonical ordering and reject malformed JSON frames.
- **No network, no side effects:** Encoding and framing are pure transformations with no I/O or external calls.

## Usage Examples
```python
from src.agent_sdk.protocol_adapter import SymbolicEncoder, TranslationCircuit

encoder = SymbolicEncoder()
circuit = TranslationCircuit(encoder=encoder, lineage=["ΔΩ.147", "ΔΩ.149"])

# Encode a normal object
encoded = encoder.encode({"status": "ok", "count": 2})

# Encode a nested dict
nested = encoder.encode({"outer": {"inner": 1}, "seq": (1, 2, 3)})

# Frame payload via TranslationCircuit
frame = circuit.to_frame(route="telemetry.ingest", payload={"status": "ok"})

# Serialize final frame
wire_ready = frame.to_dict()
```

## Integration Notes
- **core_chain usage:** Frames produced here are consumed by the SpiralOS façade (`core.spiral_api` surface) as canonical request envelopes, ensuring kernel validators receive JSON-normalized content.
- **guardian-layer lineage:** Guardians inspect `protocol_version`, `lineage`, and `circuit` headers to verify requests align with ΔΩ lineage and sanctioned circuits before granting privileges.
- **holoeconomy-engine expectations:** Holoeconomic adapters rely on deterministic payload shapes to compute ache/ScarIndex flows without re-normalizing client data.

## Contract Cross-Reference
- **JSON hygiene & unsupported types:** Aligns with SymbolicEncoder invariants in the agent-sdk boundary of the ΔΩ.149 contract.
- **Lineage & circuit headers:** Mirrors TranslationCircuit requirements for protocol_version, lineage path, and circuit id enforced at μApp ingress.
- **Deterministic framing:** Supports the μApp sovereignty guarantee in the ΔΩ.149 Architectural Contract by ensuring identical inputs yield identical frames.

See also: [ΔΩ.149.0 Architectural Expansion Blueprint](../ARCHITECTURE.md) for μApp boundary context.
