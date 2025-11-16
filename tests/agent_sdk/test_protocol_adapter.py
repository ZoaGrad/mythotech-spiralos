import json

import pytest

from src.agent_sdk.protocol_adapter import EncodingError, ProtocolMessage, SymbolicEncoder, TranslationCircuit


def test_symbolic_encoder_empty_payload_round_trip():
    encoder = SymbolicEncoder()
    encoded = encoder.encode({})
    assert encoded == "{}"
    assert encoder.decode(encoded) == {}


def test_symbolic_encoder_normalizes_nested_structures_and_keys():
    encoder = SymbolicEncoder()
    payload = {
        "outer": {"inner": 1, 2: "two"},
        "sequence": (1, "a", {"x": 3}),
    }

    encoded = encoder.encode(payload)
    decoded = json.loads(encoded)

    assert decoded == {
        "outer": {"inner": 1, "2": "two"},
        "sequence": [1, "a", {"x": 3}],
    }
    assert encoder.decode(encoded) == decoded


def test_symbolic_encoder_rejects_unsupported_types():
    encoder = SymbolicEncoder()

    with pytest.raises(EncodingError):
        encoder.encode({"bad": {1, 2}})

    with pytest.raises(EncodingError):
        encoder.encode({"bytes": b"data"})


def test_symbolic_encoder_decode_rejects_non_mapping():
    encoder = SymbolicEncoder()

    with pytest.raises(EncodingError):
        encoder.decode("[]")

    with pytest.raises(EncodingError):
        encoder.decode("null")



def test_symbolic_encoder_enforces_json_compatibility():
    encoder = SymbolicEncoder()
    payload = {"b": 1, "a": True}

    encoded = encoder.encode(payload)
    rehydrated = json.loads(encoded)

    assert rehydrated == {"a": True, "b": 1}
    assert encoder.decode(encoded) == rehydrated



def test_translation_circuit_builds_lineage_headers_and_frames_payload():
    encoder = SymbolicEncoder()
    circuit = TranslationCircuit(encoder=encoder, lineage=["ΔΩ.147", "ΔΩ.149"], circuit_id="agent-sdk.protocol_adapter")

    frame = circuit.to_frame(route="telemetry.ingest", payload={"status": "ok"})

    assert isinstance(frame, ProtocolMessage)
    assert frame.headers["protocol_version"] == "ΔΩ.149"
    assert frame.headers["lineage"] == "ΔΩ.147/ΔΩ.149"
    assert frame.headers["circuit"] == "agent-sdk.protocol_adapter"
    assert encoder.decode(frame.encoded_payload) == {"status": "ok"}



def test_translation_circuit_serializes_frame_with_metadata():
    encoder = SymbolicEncoder()
    circuit = TranslationCircuit(encoder=encoder, lineage=None)

    frame = circuit.to_frame(
        route="guardian.route",
        payload={"value": 3},
        metadata={"trace": "abc-123"},
    )

    serialized = frame.to_dict()

    assert serialized["headers"]["protocol_version"] == "ΔΩ.149"
    assert serialized["headers"]["lineage"] == ""
    assert serialized["headers"]["trace"] == "abc-123"
    assert encoder.decode(serialized["encoded_payload"]) == {"value": 3}



def test_translation_circuit_rejects_invalid_route():
    encoder = SymbolicEncoder()
    circuit = TranslationCircuit(encoder=encoder)

    with pytest.raises(EncodingError):
        circuit.to_frame(route="", payload={})

    with pytest.raises(EncodingError):
        circuit.to_frame(route=None, payload={})  # type: ignore[arg-type]



def test_translation_circuit_handles_invalid_circuit_identifier_gracefully():
    encoder = SymbolicEncoder()
    circuit = TranslationCircuit(encoder=encoder, circuit_id="")

    frame = circuit.to_frame(route="noop", payload={})

    assert frame.headers["circuit"] == ""
    assert encoder.decode(frame.encoded_payload) == {}



def test_translation_circuit_from_frame_normalizes_headers():
    encoder = SymbolicEncoder()
    circuit = TranslationCircuit(encoder=encoder)

    original = circuit.to_frame(route="guardian.route", payload={"ok": True}, metadata={"trace": 9})
    protocol_frame = original.to_dict()

    recovered = circuit.from_frame(protocol_frame)

    assert isinstance(recovered, ProtocolMessage)
    assert recovered.headers["trace"] == "9"
    assert encoder.decode(recovered.encoded_payload) == {"ok": True}


def test_translation_circuit_from_frame_rejects_invalid_frame_shapes():
    encoder = SymbolicEncoder()
    circuit = TranslationCircuit(encoder=encoder)

    with pytest.raises(EncodingError):
        circuit.from_frame([])  # type: ignore[arg-type]

    with pytest.raises(EncodingError):
        circuit.from_frame({"encoded_payload": "{}"})

    with pytest.raises(EncodingError):
        circuit.from_frame({"route": "", "encoded_payload": "{}"})

    with pytest.raises(EncodingError):
        circuit.from_frame({"route": "ok", "encoded_payload": "{}", "headers": "oops"})


def test_translation_circuit_from_frame_rejects_invalid_encoded_payload():
    encoder = SymbolicEncoder()
    circuit = TranslationCircuit(encoder=encoder)

    with pytest.raises(EncodingError):
        circuit.from_frame({"route": "ok", "encoded_payload": "not json", "headers": {}})

    with pytest.raises(EncodingError):
        circuit.from_frame(
            {"route": "ok", "encoded_payload": "[]", "headers": {}}
        )
