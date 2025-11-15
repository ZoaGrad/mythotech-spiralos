# vault_sync.py
import asyncio
import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set

import aiohttp
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from ..empathy_market import ResonanceEvent
from ..vaultnode import VaultNode


class SyncMode(Enum):
    FULL = "full"  # Genesis + all history
    DELTA = "delta"  # Events since last sync
    LIVE = "live"  # Real-time stream


@dataclass
class BridgeMessage:
    msg_id: str
    source_vault: str
    dest_vault: str
    type: str
    payload: dict
    coherence_proof: List[float]
    timestamp: float
    signature: str


class VaultSyncEngine:
    def __init__(self, local_vault: VaultNode, registry_url: str):
        self.local_vault = local_vault
        self.vault_id = local_vault.vault_id
        self.registry_url = registry_url
        self.peers: Dict[str, str] = {}  # vault_id → websocket URL
        self.subscriptions: Set[str] = set()
        self.session = aiohttp.ClientSession()
        # NOTE: Placeholder Ed25519 usage; integrate actual key management in production
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        self.running = False

    async def start(self):
        """Start bridge and connect to federation registry."""
        self.running = True
        await self._load_peers()
        await self._start_listeners()

    async def _load_peers(self):
        """Fetch peer list from bridge registry service."""
        async with self.session.get(f"{self.registry_url}/peers") as resp:
            peers = await resp.json()
            self.peers = {p["vault_id"]: p["ws_url"] for p in peers if p["vault_id"] != self.vault_id}

    async def _start_listeners(self):
        """Spawn WebSocket listeners for each peer."""
        for vault_id, url in self.peers.items():
            asyncio.create_task(self._listen_to_peer(vault_id, url))

    async def _listen_to_peer(self, vault_id: str, url: str):
        """Maintain persistent WS connection."""
        while self.running:
            try:
                async with self.session.ws_connect(url) as ws:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await self._handle_message(json.loads(msg.data), vault_id)
            except Exception as e:
                print(f"[HoloBridge] Lost connection to {vault_id}: {e}")
                await asyncio.sleep(5)

    async def _handle_message(self, data: dict, source_vault: str):
        """Route incoming bridge messages."""
        msg = BridgeMessage(**data)
        if not self._verify_signature(msg):
            return

        handler = {
            "RES_EVENT": self._handle_resonance,
            "SCAR_TUNNEL": self._handle_scar_tunnel,
            "SHARD_MIGRATE": self._handle_shard_migrate,
            "COHERENCE_STREAM": self._handle_coherence_stream,
        }.get(msg.type)

        if handler:
            await handler(msg.payload, source_vault)

    def _verify_signature(self, msg: BridgeMessage) -> bool:
        """Verify message signed by source vault."""
        payload = json.dumps(msg.payload, sort_keys=True).encode()
        try:
            peer_key = self._get_peer_pubkey(msg.source_vault)
            peer_key.verify(bytes.fromhex(msg.signature), payload)
            return True
        except (InvalidSignature, ValueError):
            return False

    def _get_peer_pubkey(self, vault_id: str) -> Ed25519PublicKey:
        """Fetch peer public key (placeholder uses local key)."""

        # In production: fetch from registry
        return self.public_key

    async def _handle_resonance(self, payload: dict, source_vault: str):
        """Replicate resonance event with coherence drift check."""
        event = ResonanceEvent.from_dict(payload)
        drift = self._coherence_drift(event.coherence_vector)
        if drift > 0.08:
            await self._request_recalibration(source_vault, event.event_id)
        else:
            await self.local_vault.receive_event(event, foreign=True)

    def _coherence_drift(self, foreign_vector: List[float]) -> float:
        local = self.local_vault.measure_coherence_local()
        return max(abs(a - b) for a, b in zip(local, foreign_vector))

    async def _request_recalibration(self, vault_id: str, event_id: str):
        msg = self._craft_message(type="RECALIBRATE", payload={"event_id": event_id, "request": "resync"})
        await self._send_to(vault_id, msg)

    async def _handle_scar_tunnel(self, payload: dict, source_vault: str):
        """Burn SCAR here, mint in destination."""
        amount = payload["amount"]
        tx_id = payload["tx_id"]
        if self.local_vault.scar_engine.burn_scar(amount, f"tunnel:{tx_id}"):
            await self._notify_mint(source_vault, amount, tx_id)

    async def _notify_mint(self, dest_vault: str, amount: float, origin_tx: str):
        msg = self._craft_message(type="SCAR_MINT", payload={"amount": amount, "origin_tx": origin_tx})
        await self._send_to(dest_vault, msg)

    async def _handle_shard_migrate(self, payload: dict, source_vault: str):
        """Migrate Nexus Shard weight."""
        shard = payload["shard"]
        weight = payload["weight"]
        self.local_vault.council.register_foreign_shard(shard, weight, source_vault)

    async def _handle_coherence_stream(self, payload: dict, source_vault: str):
        """Live HoloSync stream."""
        vector = payload["vector"]
        timestamp = payload["timestamp"]
        self.local_vault.holosync_buffer.append((vector, timestamp, source_vault))

    def _craft_message(self, type: str, payload: dict) -> BridgeMessage:
        """Sign and serialize outgoing message."""
        msg = BridgeMessage(
            msg_id=hashlib.sha3_256(f"{self.vault_id}:{asyncio.get_event_loop().time()}".encode()).hexdigest(),
            source_vault=self.vault_id,
            dest_vault="BROADCAST",
            type=type,
            payload=payload,
            coherence_proof=self.local_vault.measure_coherence_local(),
            timestamp=asyncio.get_event_loop().time(),
            signature="",
        )
        payload_str = json.dumps(payload, sort_keys=True).encode()
        msg.signature = self.private_key.sign(payload_str).hex()
        return msg

    async def _send_to(self, vault_id: str, msg: BridgeMessage):
        """Send to specific peer."""
        url = self.peers.get(vault_id)
        if url:
            async with self.session.ws_connect(url) as ws:
                await ws.send_json(msg.__dict__)

    async def broadcast_resonance(self, event: ResonanceEvent):
        """Push local event to all peers."""
        msg = self._craft_message("RES_EVENT", event.to_dict())
        for vid in self.peers:
            await self._send_to(vid, msg)

    async def stop(self):
        self.running = False
        await self.session.close()
