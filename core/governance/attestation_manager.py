"""
AttestationManager - Bridge between Off-Chain Witnessing and On-Chain Truth
"""
import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from core.db import get_supabase

logger = logging.getLogger("governance.attestation_manager")

class AttestationManager:
    def __init__(self):
        self.supabase = get_supabase()

    def create_attestation(self, witness_id: str, narrative: str, evidence: Dict) -> Optional[Dict]:
        """
        Submit a new witness attestation.
        
        Args:
            witness_id: ID of the witness submitting.
            narrative: The witness's statement/observation.
            evidence: Supporting data (JSON).
            
        Returns:
            Created attestation record or None on failure.
        """
        try:
            # Generate a hash of the content (simulating on-chain hash)
            content_str = f"{witness_id}:{narrative}:{json.dumps(evidence, sort_keys=True)}"
            attestation_hash = hashlib.sha256(content_str.encode()).hexdigest()
            
            entry_data = {
                "narrative": narrative,
                "evidence": evidence
            }
            
            payload = {
                "witness_id": witness_id,
                "attestation_hash": attestation_hash,
                "entry_data": entry_data,
                "status": "pending",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            res = self.supabase.table("witness_entries").insert(payload).execute()
            if res.data:
                logger.info(f"Attestation created: {res.data[0]['id']}")
                return res.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to create attestation: {e}")
            return None

    def verify_attestation(self, attestation_id: str, verifier_id: str, status: str = "attested") -> bool:
        """
        Verify an existing attestation.
        
        Args:
            attestation_id: UUID of the attestation.
            verifier_id: ID of the entity verifying.
            status: New status ('attested', 'challenged').
            
        Returns:
            True if successful.
        """
        try:
            # In a real system, this would check on-chain signatures or verifier authority
            # For now, we trust the caller (Guardian/Admin)
            
            payload = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
                # We could add a 'verified_by' field to metadata if we expand the schema
            }
            
            res = self.supabase.table("witness_entries").update(payload).eq("id", attestation_id).execute()
            
            if res.data:
                logger.info(f"Attestation {attestation_id} verified as {status} by {verifier_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to verify attestation: {e}")
            return False

    def get_pending_attestations(self) -> List[Dict]:
        """Get all attestations waiting for verification."""
        try:
            res = self.supabase.table("witness_entries").select("*").eq("status", "pending").execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Failed to fetch pending attestations: {e}")
            return []

# Singleton
attestation_manager = AttestationManager()
