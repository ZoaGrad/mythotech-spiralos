"""
ScarCoin Bridge API

REST API for Holo-Economy with ScarCoin minting, Proof-of-Ache validation,
and VaultNode blockchain integration.

Provides programmatic access to the economic validation layer.
"""

# VaultNode Seal: ΔΩ.147.C — Guardian authentication canonical build

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
import os
import sys
import time
from typing import Any, Awaitable, Callable, Deque, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel, Field

# Add module and core directories to path for imports
MODULE_DIR = os.path.dirname(__file__)
sys.path.insert(0, MODULE_DIR)
sys.path.insert(0, os.path.join(MODULE_DIR, ".."))

from core.config import get_guardian_settings, get_vaultnode_settings
from core.f2_judges import JudicialSystem
from scarcoin import ScarCoinMintingEngine
from system_summary import SystemSummary
from vaultnode import VaultEvent, VaultNode


guardian_settings = get_guardian_settings()
vaultnode_settings = get_vaultnode_settings()

_guardian_rate_state: Dict[str, Deque[float]] = defaultdict(deque)


@dataclass
class GuardianContext:
    """Authenticated Guardian request context."""

    api_key: str
    guardian_id: str
    roles: List[str]


def _enforce_guardian_rate_limit(api_key: str) -> None:
    """Ensure Guardian requests stay within configured bounds."""

    window_start = time.time() - guardian_settings.rate_window_seconds
    rate_window = _guardian_rate_state[api_key]

    while rate_window and rate_window[0] < window_start:
        rate_window.popleft()

    if len(rate_window) >= guardian_settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Guardian request rate exceeded"
        )

    rate_window.append(time.time())


def _extract_roles(payload: Dict[str, Any]) -> List[str]:
    """Normalize Guardian roles from JWT payload."""

    roles: List[str] = []
    raw_roles = payload.get('roles')
    if isinstance(raw_roles, list):
        roles.extend(str(role) for role in raw_roles)
    elif isinstance(raw_roles, str):
        roles.append(raw_roles)

    single_role = payload.get('role')
    if isinstance(single_role, str) and single_role not in roles:
        roles.append(single_role)

    return roles


async def validate_guardian_request(request: Request) -> GuardianContext:
    """Validate Guardian API key, rate limits, and JWT signature."""

    api_key = request.headers.get("X-Guardian-Key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Guardian-Key header required"
        )

    if not guardian_settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Guardian keyring not configured"
        )

    if api_key not in guardian_settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Guardian API key"
        )

    _enforce_guardian_rate_limit(api_key)

    auth_header = request.headers.get("Authorization", "")
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Guardian bearer token required"
        )

    if not guardian_settings.jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Guardian signature validation unavailable"
        )

    try:
        decode_kwargs = {
            "algorithms": [guardian_settings.jwt_algorithm]
        }
        if guardian_settings.jwt_audience:
            decode_kwargs["audience"] = guardian_settings.jwt_audience
        if guardian_settings.jwt_issuer:
            decode_kwargs["issuer"] = guardian_settings.jwt_issuer

        payload = jwt.decode(
            token,
            guardian_settings.jwt_secret,
            **decode_kwargs
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Guardian signature"
        ) from exc

    roles = _extract_roles(payload)
    if "guardian" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guardian role required"
        )

    guardian_id = (
        str(payload.get("sub"))
        or str(payload.get("guardian_id"))
        or "guardian"
    )

    return GuardianContext(
        api_key=api_key,
        guardian_id=guardian_id,
        roles=roles
    )


# Pydantic models for API
class MintRequest(BaseModel):
    """Request to mint ScarCoin"""
    transmutation_id: str
    scarindex_before: Decimal = Field(..., ge=0, le=1)
    scarindex_after: Decimal = Field(..., ge=0, le=1)
    transmutation_efficiency: Decimal = Field(..., ge=0, le=1)
    owner_address: str
    oracle_signatures: Optional[List[str]] = None


class MintResponse(BaseModel):
    """Response from minting"""
    success: bool
    coin_id: Optional[str] = None
    coin_value: Optional[str] = None
    message: str


class BurnRequest(BaseModel):
    """Request to burn ScarCoin"""
    coin_id: str
    reason: str = Field(default="Failed transmutation", min_length=3, max_length=256)


class WalletResponse(BaseModel):
    """Wallet information"""
    address: str
    balance: str
    total_minted: str
    total_burned: str
    transaction_count: int


class SupplyStatsResponse(BaseModel):
    """Supply statistics"""
    total_supply: str
    total_minted: str
    total_burned: str
    minting_count: int
    burning_count: int
    active_wallets: int


class BlockResponse(BaseModel):
    """VaultNode block information"""
    block_number: int
    merkle_root: str
    timestamp: str
    events_count: int
    consensus_reached: bool
    block_hash: str


class DissentRequest(BaseModel):
    """Request to file dissent/appeal against F2 refusal"""
    refusal_id: str
    appellant_id: str
    grounds: str = Field(..., min_length=10, description="Grounds for appeal (minimum 10 characters)")
    evidence: Optional[Dict] = None


class DissentResponse(BaseModel):
    """Response from dissent filing"""
    success: bool
    appeal_id: Optional[str] = None
    refusal_id: str
    review_due_by: str
    message: str


class RefusalRequest(BaseModel):
    """Request payload for invoking Right of Refusal"""
    action_type: str
    action_id: str
    constitutional_grounds: str = Field(..., min_length=10)
    evidence: Optional[Dict] = None


class RefusalResponse(BaseModel):
    """Response for Right of Refusal"""
    refusal_id: str
    action_type: str
    action_id: str
    constitutional_grounds: str
    appeal_endpoint: str
    appeal_instructions: str
    refused_at: str


# Initialize FastAPI
app = FastAPI(
    title="ScarCoin Bridge API",
    description="Holo-Economy API for Proof-of-Ache minting and VaultNode blockchain",
    version="1.3.0-alpha",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=guardian_settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
minting_engine = ScarCoinMintingEngine(
    multiplier=Decimal("1000"),
    min_delta_c=Decimal("0.01"),
)

vaultnode = VaultNode(vault_id=vaultnode_settings.default_id)

# Initialize system summary
system_summary = SystemSummary(
    minting_engine=minting_engine,
    vaultnode=vaultnode,
)

judicial_system = JudicialSystem()


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "vault_id": vaultnode.vault_id,
        "total_blocks": len(vaultnode.blocks),
        "chain_valid": vaultnode.verify_chain()
    }


# ScarCoin endpoints
@app.post("/api/v1/scarcoin/mint", response_model=MintResponse)
async def mint_scarcoin(
    request: MintRequest,
    guardian_context: GuardianContext = Depends(validate_guardian_request)
) -> MintResponse:
    """Mint ScarCoin for a validated transmutation.

    Args:
        request: Mint parameters validated by Guardian operators.
        guardian_context: Authenticated Guardian metadata from JWT.

    Returns:
        MintResponse describing the outcome of the mint operation.

    Raises:
        HTTPException: If validation fails or the minting engine errors.
    """
    try:
        # Mint coin
        coin = minting_engine.mint_scarcoin(
            transmutation_id=request.transmutation_id,
            scarindex_before=request.scarindex_before,
            scarindex_after=request.scarindex_after,
            transmutation_efficiency=request.transmutation_efficiency,
            owner_address=request.owner_address,
            oracle_signatures=request.oracle_signatures or []
        )
        
        if not coin:
            return MintResponse(
                success=False,
                message="Minting failed: Proof-of-Ache validation failed or consensus not reached"
            )
        
        # Record in VaultNode
        minting_event = VaultEvent(
            event_type="scarcoin_minted",
            event_data={
                'coin_id': coin.id,
                'transmutation_id': coin.transmutation_id,
                'coin_value': str(coin.coin_value),
                'owner': coin.owner,
                'delta_c': str(coin.delta_c),
                'scarindex_after': str(coin.scarindex_after),
                'authorized_by': guardian_context.guardian_id
            }
        )

        vaultnode.add_event(minting_event)

        return MintResponse(
            success=True,
            coin_id=coin.id,
            coin_value=str(coin.coin_value),
            message=f"Successfully minted {coin.coin_value} ScarCoins"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/v1/scarcoin/burn")
async def burn_scarcoin(
    request: BurnRequest,
    guardian_context: GuardianContext = Depends(validate_guardian_request)
) -> Dict[str, Any]:
    """Burn an existing ScarCoin that violates constitutional constraints.

    Args:
        request: Burn payload containing the target coin identifier and reason.
        guardian_context: Authenticated Guardian metadata used for auditing.

    Returns:
        Dictionary describing the burn outcome, including auditing metadata.

    Raises:
        HTTPException: If the coin is not found or the burn operation fails.
    """

    success = minting_engine.burn_scarcoin(
        coin_id=request.coin_id,
        reason=request.reason
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coin {request.coin_id} not found or already burned"
        )

    burn_event = VaultEvent(
        event_type="scarcoin_burned",
        event_data={
            'coin_id': request.coin_id,
            'reason': request.reason,
            'authorized_by': guardian_context.guardian_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    )
    vaultnode.add_event(burn_event)

    return {
        'success': True,
        'coin_id': request.coin_id,
        'message': f"Coin {request.coin_id} burned",
        'burned_by': guardian_context.guardian_id
    }


@app.post("/api/v1/f2/refusal", response_model=RefusalResponse)
@app.post("/api/v1/refusal", response_model=RefusalResponse)
async def invoke_right_of_refusal(
    request: RefusalRequest,
    guardian_context: GuardianContext = Depends(validate_guardian_request)
) -> RefusalResponse:
    """Invoke the constitutional Right of Refusal via Guardian authorization.

    Args:
        request: Refusal payload describing the blocked action.
        guardian_context: Authenticated Guardian metadata.

    Returns:
        RefusalResponse describing the refusal and appeal instructions.
    """

    refusal = judicial_system.invoke_right_of_refusal(
        action_type=request.action_type,
        action_id=request.action_id,
        refusing_judge_id=guardian_context.guardian_id,
        constitutional_grounds=request.constitutional_grounds,
        evidence=request.evidence
    )

    refusal_event = VaultEvent(
        event_type="f2_refusal",
        event_data={
            'refusal_id': refusal.id,
            'action_type': refusal.action_type,
            'action_id': refusal.action_id,
            'refusing_judge_id': refusal.refusing_judge_id,
            'constitutional_grounds': refusal.constitutional_grounds
        }
    )
    vaultnode.add_event(refusal_event)

    return RefusalResponse(
        refusal_id=refusal.id,
        action_type=refusal.action_type,
        action_id=refusal.action_id,
        constitutional_grounds=refusal.constitutional_grounds,
        appeal_endpoint=refusal.appeal_endpoint,
        appeal_instructions=refusal.appeal_instructions,
        refused_at=refusal.refused_at.isoformat()
    )


@app.get("/api/v1/scarcoin/balance/{wallet_address}")
async def get_balance(wallet_address: str):
    """Get wallet balance"""
    balance = minting_engine.get_wallet_balance(wallet_address)
    
    if balance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet {wallet_address} not found"
        )
    
    return {"address": wallet_address, "balance": str(balance)}


@app.get("/api/v1/scarcoin/supply", response_model=SupplyStatsResponse)
async def get_supply():
    """Get supply statistics"""
    stats = minting_engine.get_supply_stats()
    return SupplyStatsResponse(**stats)


@app.get("/api/v1/wallet/{address}", response_model=WalletResponse)
async def get_wallet(address: str):
    """Get wallet information"""
    wallet = minting_engine.get_wallet(address)
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet {address} not found"
        )
    
    return WalletResponse(
        address=wallet.address,
        balance=str(wallet.balance),
        total_minted=str(wallet.total_minted),
        total_burned=str(wallet.total_burned),
        transaction_count=wallet.transaction_count
    )


@app.post("/api/v1/wallet/create")
async def create_wallet(address: Optional[str] = None):
    """Create new wallet"""
    wallet = minting_engine.create_wallet(address)
    
    return WalletResponse(
        address=wallet.address,
        balance=str(wallet.balance),
        total_minted=str(wallet.total_minted),
        total_burned=str(wallet.total_burned),
        transaction_count=wallet.transaction_count
    )


# VaultNode endpoints
@app.get("/api/v1/vault/block/{block_number}", response_model=BlockResponse)
async def get_block(block_number: int):
    """Get block by number"""
    block = vaultnode.get_block(block_number)
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block {block_number} not found"
        )
    
    return BlockResponse(
        block_number=block.block_number,
        merkle_root=block.merkle_root,
        timestamp=block.timestamp.isoformat(),
        events_count=len(block.events),
        consensus_reached=block.consensus_reached,
        block_hash=block.calculate_hash()
    )


@app.get("/api/v1/vault/latest", response_model=BlockResponse)
async def get_latest_block():
    """Get latest block"""
    block = vaultnode.get_latest_block()
    
    return BlockResponse(
        block_number=block.block_number,
        merkle_root=block.merkle_root,
        timestamp=block.timestamp.isoformat(),
        events_count=len(block.events),
        consensus_reached=block.consensus_reached,
        block_hash=block.calculate_hash()
    )


@app.get("/api/v1/vault/stats")
async def get_vault_stats():
    """Get VaultNode statistics"""
    return vaultnode.get_chain_stats()


@app.post("/api/v1/vault/create_block")
async def create_block(oracle_signatures: Dict[str, str]):
    """
    Create new block from pending events
    
    Requires Oracle Council signatures.
    """
    try:
        if not vaultnode.pending_events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending events to create block"
            )
        
        block = vaultnode.create_block(oracle_signatures=oracle_signatures)
        
        return BlockResponse(
            block_number=block.block_number,
            merkle_root=block.merkle_root,
            timestamp=block.timestamp.isoformat(),
            events_count=len(block.events),
            consensus_reached=block.consensus_reached,
            block_hash=block.calculate_hash()
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Proof-of-Ache endpoints
@app.get("/api/v1/poa/proof/{transmutation_id}")
async def get_proof(transmutation_id: str):
    """Get Proof-of-Ache for transmutation"""
    proof = minting_engine.proofs.get(transmutation_id)
    
    if not proof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proof for transmutation {transmutation_id} not found"
        )
    
    return proof.to_dict()


# System Summary endpoint
@app.get("/api/v1/summary")
async def get_system_summary():
    """
    Get comprehensive system summary
    
    Returns aggregated status from all SpiralOS components:
    - Core system status
    - ScarCoin economy metrics
    - Empathy Market activity
    - VaultNode blockchain health
    """
    return system_summary.get_summary()


@app.get("/api/v1/summary/quick")
async def get_quick_summary():
    """Get quick one-line system status"""
    return {
        "status": system_summary.get_quick_status(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "ScarCoin Bridge API",
        "version": "1.3.0-alpha",
        "vault_id": vaultnode.vault_id,
        "description": "Holo-Economy API for Proof-of-Ache minting and VaultNode blockchain",
        "endpoints": {
            "health": "/health",
            "summary": {
                "full": "GET /api/v1/summary",
                "quick": "GET /api/v1/summary/quick"
            },
            "scarcoin": {
                "mint": "POST /api/v1/scarcoin/mint",
                "balance": "GET /api/v1/scarcoin/balance/{wallet_address}",
                "supply": "GET /api/v1/scarcoin/supply"
            },
            "wallet": {
                "get": "GET /api/v1/wallet/{address}",
                "create": "POST /api/v1/wallet/create"
            },
            "vault": {
                "block": "GET /api/v1/vault/block/{block_number}",
                "latest": "GET /api/v1/vault/latest",
                "stats": "GET /api/v1/vault/stats",
                "create_block": "POST /api/v1/vault/create_block"
            },
            "poa": {
                "proof": "GET /api/v1/poa/proof/{transmutation_id}"
            }
        },
        "motto": "Where coherence becomes currency 🜂"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("ScarCoin Bridge API")
    print("=" * 70)
    print(f"Vault ID: {vaultnode.vault_id}")
    print(f"Starting server on http://0.0.0.0:8000")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
