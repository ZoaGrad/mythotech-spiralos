"""
ScarMarket DEX Core - Multi-Token Composability Layer

Implements ERC-1155-style multi-token standard for SpiralOS, enabling atomic
exchange of fungible (ScarCoin), semi-fungible (VaultNode assets), and
non-fungible (EMP) tokens within a single composable framework.

This is a proof-of-concept implementation demonstrating constitutional liquidity
principles without requiring full production blockchain deployment.
"""

from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
import uuid
import hashlib
import json


class TokenType(Enum):
    """Token type classification"""
    FUNGIBLE = "fungible"          # ScarCoin
    SEMI_FUNGIBLE = "semi_fungible"  # VaultNode assets
    NON_FUNGIBLE = "non_fungible"    # EMP (soul-bound)


class TokenStandard(Enum):
    """Token standard (ERC-1155 analogue)"""
    MULTI_TOKEN = "multi_token"  # Supports all token types


@dataclass
class Token:
    """
    Multi-Token Standard (ERC-1155 analogue)
    
    Supports fungible, semi-fungible, and non-fungible tokens
    in a single unified interface.
    """
    token_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    token_type: TokenType = TokenType.FUNGIBLE
    symbol: str = ""
    name: str = ""
    
    # Supply
    total_supply: Decimal = Decimal('0')
    circulating_supply: Decimal = Decimal('0')
    
    # Metadata
    metadata: Dict = field(default_factory=dict)
    
    # Transfer restrictions
    transferable: bool = True
    
    # VaultNode specific
    vaultnode_id: Optional[str] = None
    knowledge_hash: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'token_id': self.token_id,
            'token_type': self.token_type.value,
            'symbol': self.symbol,
            'name': self.name,
            'total_supply': str(self.total_supply),
            'circulating_supply': str(self.circulating_supply),
            'transferable': self.transferable,
            'vaultnode_id': self.vaultnode_id,
            'knowledge_hash': self.knowledge_hash,
            'metadata': self.metadata
        }


@dataclass
class LiquidityPool:
    """
    Automated Market Maker (AMM) Liquidity Pool
    
    Implements constant product formula: x * y = k
    """
    pool_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Token pair
    token_a_id: str = ""
    token_b_id: str = ""
    
    # Reserves
    reserve_a: Decimal = Decimal('0')
    reserve_b: Decimal = Decimal('0')
    
    # Liquidity
    total_liquidity: Decimal = Decimal('0')
    liquidity_providers: Dict[str, Decimal] = field(default_factory=dict)
    
    # Fee
    fee_rate: Decimal = Decimal('0.003')  # 0.3% default
    
    # Statistics
    total_trades: int = 0
    total_volume_a: Decimal = Decimal('0')
    total_volume_b: Decimal = Decimal('0')
    last_trade_at: Optional[datetime] = None
    
    def get_constant_product(self) -> Decimal:
        """Calculate k = x * y"""
        return self.reserve_a * self.reserve_b
    
    def get_price_a_in_b(self) -> Decimal:
        """Get price of token A in terms of token B"""
        if self.reserve_a == 0:
            return Decimal('0')
        return self.reserve_b / self.reserve_a
    
    def get_price_b_in_a(self) -> Decimal:
        """Get price of token B in terms of token A"""
        if self.reserve_b == 0:
            return Decimal('0')
        return self.reserve_a / self.reserve_b
    
    def calculate_output_amount(
        self,
        input_amount: Decimal,
        input_is_a: bool
    ) -> Decimal:
        """
        Calculate output amount using constant product formula
        
        Formula: (x + Δx * (1 - fee)) * (y - Δy) = k
        Solving for Δy: Δy = y * Δx * (1 - fee) / (x + Δx * (1 - fee))
        """
        if input_is_a:
            input_reserve = self.reserve_a
            output_reserve = self.reserve_b
        else:
            input_reserve = self.reserve_b
            output_reserve = self.reserve_a
        
        # Apply fee
        input_with_fee = input_amount * (Decimal('1') - self.fee_rate)
        
        # Calculate output
        numerator = output_reserve * input_with_fee
        denominator = input_reserve + input_with_fee
        
        return numerator / denominator if denominator > 0 else Decimal('0')
    
    def calculate_slippage(
        self,
        input_amount: Decimal,
        output_amount: Decimal,
        input_is_a: bool
    ) -> Decimal:
        """Calculate slippage percentage"""
        spot_price = self.get_price_a_in_b() if input_is_a else self.get_price_b_in_a()
        
        if spot_price == 0:
            return Decimal('0')
        
        effective_price = output_amount / input_amount if input_amount > 0 else Decimal('0')
        slippage = abs(effective_price - spot_price) / spot_price
        
        return slippage * Decimal('100')  # Return as percentage
    
    def to_dict(self) -> Dict:
        return {
            'pool_id': self.pool_id,
            'created_at': self.created_at.isoformat(),
            'token_a_id': self.token_a_id,
            'token_b_id': self.token_b_id,
            'reserve_a': str(self.reserve_a),
            'reserve_b': str(self.reserve_b),
            'total_liquidity': str(self.total_liquidity),
            'fee_rate': str(self.fee_rate),
            'price_a_in_b': str(self.get_price_a_in_b()),
            'price_b_in_a': str(self.get_price_b_in_a()),
            'total_trades': self.total_trades,
            'total_volume_a': str(self.total_volume_a),
            'total_volume_b': str(self.total_volume_b)
        }


@dataclass
class Trade:
    """DEX trade record"""
    trade_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    pool_id: str = ""
    trader_address: str = ""
    
    # Trade details
    token_in_id: str = ""
    token_out_id: str = ""
    amount_in: Decimal = Decimal('0')
    amount_out: Decimal = Decimal('0')
    
    # Pricing
    price: Decimal = Decimal('0')
    slippage: Decimal = Decimal('0')
    
    # VaultNode linkage
    vault_block_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'trade_id': self.trade_id,
            'timestamp': self.timestamp.isoformat(),
            'pool_id': self.pool_id,
            'trader_address': self.trader_address,
            'token_in_id': self.token_in_id,
            'token_out_id': self.token_out_id,
            'amount_in': str(self.amount_in),
            'amount_out': str(self.amount_out),
            'price': str(self.price),
            'slippage': str(self.slippage),
            'vault_block_id': self.vault_block_id
        }


class ScarMarketDEX:
    """
    ScarMarket Decentralized Exchange
    
    Multi-token composability layer for SpiralOS economic system,
    enabling atomic exchange of SCAR, EMP, and VaultNode assets.
    """
    
    def __init__(self):
        """Initialize ScarMarket DEX"""
        # Token registry
        self.tokens: Dict[str, Token] = {}
        
        # Liquidity pools
        self.pools: Dict[str, LiquidityPool] = {}
        self.pool_lookup: Dict[Tuple[str, str], str] = {}  # (token_a, token_b) -> pool_id
        
        # Balances: address -> token_id -> amount
        self.balances: Dict[str, Dict[str, Decimal]] = {}
        
        # Trade history
        self.trades: Dict[str, Trade] = {}
        
        # Statistics
        self.total_trades = 0
        self.total_volume_usd = Decimal('0')
    
    def register_token(
        self,
        symbol: str,
        name: str,
        token_type: TokenType,
        transferable: bool = True,
        **kwargs
    ) -> Token:
        """Register new token in the DEX"""
        token = Token(
            symbol=symbol,
            name=name,
            token_type=token_type,
            transferable=transferable,
            **kwargs
        )
        
        self.tokens[token.token_id] = token
        return token
    
    def get_token(self, token_id: str) -> Optional[Token]:
        """Get token by ID"""
        return self.tokens.get(token_id)
    
    def get_token_by_symbol(self, symbol: str) -> Optional[Token]:
        """Get token by symbol"""
        for token in self.tokens.values():
            if token.symbol == symbol:
                return token
        return None
    
    def mint_tokens(
        self,
        token_id: str,
        to_address: str,
        amount: Decimal
    ) -> bool:
        """Mint tokens to address"""
        token = self.get_token(token_id)
        if not token:
            return False
        
        # Update supply
        token.total_supply += amount
        token.circulating_supply += amount
        
        # Update balance
        if to_address not in self.balances:
            self.balances[to_address] = {}
        
        if token_id not in self.balances[to_address]:
            self.balances[to_address][token_id] = Decimal('0')
        
        self.balances[to_address][token_id] += amount
        return True
    
    def get_balance(self, address: str, token_id: str) -> Decimal:
        """Get token balance for address"""
        if address not in self.balances:
            return Decimal('0')
        return self.balances[address].get(token_id, Decimal('0'))
    
    def create_liquidity_pool(
        self,
        token_a_id: str,
        token_b_id: str,
        initial_a: Decimal,
        initial_b: Decimal,
        provider_address: str,
        fee_rate: Decimal = Decimal('0.003')
    ) -> Optional[LiquidityPool]:
        """Create new liquidity pool"""
        # Validate tokens exist
        if not self.get_token(token_a_id) or not self.get_token(token_b_id):
            return None
        
        # Check if pool already exists
        pool_key = tuple(sorted([token_a_id, token_b_id]))
        if pool_key in self.pool_lookup:
            return None
        
        # Check provider has sufficient balance
        if self.get_balance(provider_address, token_a_id) < initial_a:
            return None
        if self.get_balance(provider_address, token_b_id) < initial_b:
            return None
        
        # Create pool
        pool = LiquidityPool(
            token_a_id=token_a_id,
            token_b_id=token_b_id,
            reserve_a=initial_a,
            reserve_b=initial_b,
            fee_rate=fee_rate
        )
        
        # Calculate initial liquidity (geometric mean)
        pool.total_liquidity = (initial_a * initial_b).sqrt()
        pool.liquidity_providers[provider_address] = pool.total_liquidity
        
        # Deduct from provider balance
        self.balances[provider_address][token_a_id] -= initial_a
        self.balances[provider_address][token_b_id] -= initial_b
        
        # Register pool
        self.pools[pool.pool_id] = pool
        self.pool_lookup[pool_key] = pool.pool_id
        
        return pool
    
    def get_pool(
        self,
        token_a_id: str,
        token_b_id: str
    ) -> Optional[LiquidityPool]:
        """Get liquidity pool for token pair"""
        pool_key = tuple(sorted([token_a_id, token_b_id]))
        pool_id = self.pool_lookup.get(pool_key)
        return self.pools.get(pool_id) if pool_id else None
    
    def execute_swap(
        self,
        trader_address: str,
        token_in_id: str,
        token_out_id: str,
        amount_in: Decimal,
        min_amount_out: Decimal = Decimal('0'),
        max_slippage: Decimal = Decimal('5.0')  # 5% default
    ) -> Optional[Trade]:
        """
        Execute token swap
        
        Args:
            trader_address: Trader's address
            token_in_id: Input token ID
            token_out_id: Output token ID
            amount_in: Input amount
            min_amount_out: Minimum acceptable output amount
            max_slippage: Maximum acceptable slippage percentage
            
        Returns:
            Trade object if successful, None otherwise
        """
        # Get pool
        pool = self.get_pool(token_in_id, token_out_id)
        if not pool:
            return None
        
        # Check trader balance
        if self.get_balance(trader_address, token_in_id) < amount_in:
            return None
        
        # Check transferability
        token_in = self.get_token(token_in_id)
        token_out = self.get_token(token_out_id)
        if not token_in or not token_out:
            return None
        
        if not token_in.transferable or not token_out.transferable:
            return None
        
        # Determine direction
        input_is_a = (token_in_id == pool.token_a_id)
        
        # Calculate output amount
        amount_out = pool.calculate_output_amount(amount_in, input_is_a)
        
        # Check minimum output
        if amount_out < min_amount_out:
            return None
        
        # Calculate slippage
        slippage = pool.calculate_slippage(amount_in, amount_out, input_is_a)
        
        # Check maximum slippage
        if slippage > max_slippage:
            return None
        
        # Update pool reserves
        if input_is_a:
            pool.reserve_a += amount_in
            pool.reserve_b -= amount_out
            pool.total_volume_a += amount_in
            pool.total_volume_b += amount_out
        else:
            pool.reserve_b += amount_in
            pool.reserve_a -= amount_out
            pool.total_volume_b += amount_in
            pool.total_volume_a += amount_out
        
        # Update balances
        self.balances[trader_address][token_in_id] -= amount_in
        
        if token_out_id not in self.balances[trader_address]:
            self.balances[trader_address][token_out_id] = Decimal('0')
        self.balances[trader_address][token_out_id] += amount_out
        
        # Calculate price
        price = amount_out / amount_in if amount_in > 0 else Decimal('0')
        
        # Create trade record
        trade = Trade(
            pool_id=pool.pool_id,
            trader_address=trader_address,
            token_in_id=token_in_id,
            token_out_id=token_out_id,
            amount_in=amount_in,
            amount_out=amount_out,
            price=price,
            slippage=slippage
        )
        
        # Update statistics
        pool.total_trades += 1
        pool.last_trade_at = trade.timestamp
        self.total_trades += 1
        
        # Store trade
        self.trades[trade.trade_id] = trade
        
        return trade
    
    def get_market_stats(self) -> Dict:
        """Get DEX market statistics"""
        return {
            'total_tokens': len(self.tokens),
            'total_pools': len(self.pools),
            'total_trades': self.total_trades,
            'total_volume_usd': str(self.total_volume_usd),
            'total_liquidity_providers': sum(
                len(pool.liquidity_providers) for pool in self.pools.values()
            )
        }


# Example usage
def example_scarmarket_dex():
    """Example of ScarMarket DEX"""
    print("=" * 70)
    print("ScarMarket DEX - Multi-Token Composability Layer")
    print("=" * 70)
    print()
    
    # Initialize DEX
    dex = ScarMarketDEX()
    
    print("Initializing ScarMarket DEX...")
    print()
    
    # Register tokens
    print("Registering tokens...")
    print("-" * 70)
    
    scar = dex.register_token(
        symbol="SCAR",
        name="ScarCoin",
        token_type=TokenType.FUNGIBLE,
        transferable=True
    )
    print(f"✅ Registered SCAR (Fungible): {scar.token_id[:8]}...")
    
    emp = dex.register_token(
        symbol="EMP",
        name="Empathy Token",
        token_type=TokenType.NON_FUNGIBLE,
        transferable=False  # Soul-bound
    )
    print(f"✅ Registered EMP (Non-Fungible, Soul-Bound): {emp.token_id[:8]}...")
    
    vault = dex.register_token(
        symbol="VAULT",
        name="VaultNode Asset",
        token_type=TokenType.SEMI_FUNGIBLE,
        transferable=True,
        vaultnode_id="ΔΩ.123.0"
    )
    print(f"✅ Registered VAULT (Semi-Fungible): {vault.token_id[:8]}...")
    print()
    
    # Mint tokens
    print("Minting tokens to liquidity provider...")
    print("-" * 70)
    
    provider = "alice"
    dex.mint_tokens(scar.token_id, provider, Decimal('10000'))
    dex.mint_tokens(vault.token_id, provider, Decimal('100'))
    
    print(f"Alice SCAR balance: {dex.get_balance(provider, scar.token_id)}")
    print(f"Alice VAULT balance: {dex.get_balance(provider, vault.token_id)}")
    print()
    
    # Create liquidity pool
    print("Creating SCAR/VAULT liquidity pool...")
    print("-" * 70)
    
    pool = dex.create_liquidity_pool(
        token_a_id=scar.token_id,
        token_b_id=vault.token_id,
        initial_a=Decimal('1000'),
        initial_b=Decimal('10'),
        provider_address=provider
    )
    
    if pool:
        print(f"✅ Pool created: {pool.pool_id[:8]}...")
        print(f"  Reserve SCAR: {pool.reserve_a}")
        print(f"  Reserve VAULT: {pool.reserve_b}")
        print(f"  Price (SCAR/VAULT): {pool.get_price_a_in_b():.2f}")
        print(f"  Price (VAULT/SCAR): {pool.get_price_b_in_a():.2f}")
        print()
    
    # Execute swap
    print("Executing swap: 100 SCAR → VAULT...")
    print("-" * 70)
    
    trader = "bob"
    dex.mint_tokens(scar.token_id, trader, Decimal('1000'))
    
    trade = dex.execute_swap(
        trader_address=trader,
        token_in_id=scar.token_id,
        token_out_id=vault.token_id,
        amount_in=Decimal('100'),
        max_slippage=Decimal('10.0')
    )
    
    if trade:
        print(f"✅ Trade executed: {trade.trade_id[:8]}...")
        print(f"  Amount In (SCAR): {trade.amount_in}")
        print(f"  Amount Out (VAULT): {trade.amount_out}")
        print(f"  Price: {trade.price:.4f}")
        print(f"  Slippage: {trade.slippage:.2f}%")
        print()
        
        print(f"Bob SCAR balance: {dex.get_balance(trader, scar.token_id)}")
        print(f"Bob VAULT balance: {dex.get_balance(trader, vault.token_id)}")
        print()
    
    # Market statistics
    print("=" * 70)
    print("Market Statistics")
    print("=" * 70)
    
    stats = dex.get_market_stats()
    print(f"\nTotal Tokens: {stats['total_tokens']}")
    print(f"Total Pools: {stats['total_pools']}")
    print(f"Total Trades: {stats['total_trades']}")
    print(f"Total Liquidity Providers: {stats['total_liquidity_providers']}")


if __name__ == '__main__':
    example_scarmarket_dex()
