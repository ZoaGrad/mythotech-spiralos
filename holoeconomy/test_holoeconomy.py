"""
Holo-Economy Test Suite

Comprehensive tests for ScarCoin minting, Proof-of-Ache validation,
and VaultNode blockchain integration.
"""

import sys
from decimal import Decimal
import uuid
import hashlib

from scarcoin import ScarCoinMintingEngine, ScarCoin, ProofOfAche, Wallet
from vaultnode import VaultNode, VaultEvent, MerkleTree


def test_scarcoin_minting():
    """Test ScarCoin minting with Proof-of-Ache"""
    print("\n" + "=" * 70)
    print("TEST: ScarCoin Minting")
    print("=" * 70)
    
    engine = ScarCoinMintingEngine()
    wallet = engine.create_wallet()
    
    # Test successful minting
    transmutation_id = str(uuid.uuid4())
    oracle_sigs = [
        f"oracle_1_{hashlib.sha256(transmutation_id.encode()).hexdigest()[:16]}",
        f"oracle_2_{hashlib.sha256(transmutation_id.encode()).hexdigest()[:16]}"
    ]
    
    coin = engine.mint_scarcoin(
        transmutation_id=transmutation_id,
        scarindex_before=Decimal('0.65'),
        scarindex_after=Decimal('0.80'),
        transmutation_efficiency=Decimal('0.95'),
        owner_address=wallet.address,
        oracle_signatures=oracle_sigs
    )
    
    assert coin is not None, "Minting should succeed"
    assert coin.coin_value == Decimal('114.00000000'), f"Expected 114, got {coin.coin_value}"
    assert wallet.balance == coin.coin_value, "Wallet balance should match coin value"
    
    print("✅ ScarCoin minting successful")
    print(f"   Coin value: {coin.coin_value}")
    print(f"   Wallet balance: {wallet.balance}")


def test_proof_of_ache_validation():
    """Test Proof-of-Ache validation"""
    print("\n" + "=" * 70)
    print("TEST: Proof-of-Ache Validation")
    print("=" * 70)
    
    engine = ScarCoinMintingEngine()
    
    # Test successful validation (Ache decreased)
    proof1 = engine.validate_proof_of_ache(
        transmutation_id=str(uuid.uuid4()),
        scarindex_before=Decimal('0.60'),
        scarindex_after=Decimal('0.75'),
        oracle_signatures=[
            "oracle_sig_1",
            "oracle_sig_2"
        ]
    )
    
    assert proof1.validation_passed, "Validation should pass when Ache decreases"
    assert proof1.consensus_reached, "Consensus should be reached with 2 signatures"
    
    print("✅ Successful validation (Ache decreased)")
    print(f"   Ache before: {proof1.ache_before}")
    print(f"   Ache after: {proof1.ache_after}")
    print(f"   Differential: {proof1.ache_differential}")
    
    # Test failed validation (Ache increased)
    proof2 = engine.validate_proof_of_ache(
        transmutation_id=str(uuid.uuid4()),
        scarindex_before=Decimal('0.75'),
        scarindex_after=Decimal('0.60'),
        oracle_signatures=["oracle_sig_1"]
    )
    
    assert not proof2.validation_passed, "Validation should fail when Ache increases"
    
    print("✅ Failed validation (Ache increased)")
    print(f"   Ache differential: {proof2.ache_differential}")


def test_wallet_operations():
    """Test wallet deposit and withdrawal"""
    print("\n" + "=" * 70)
    print("TEST: Wallet Operations")
    print("=" * 70)
    
    wallet = Wallet()
    
    # Test deposit
    wallet.deposit(Decimal('100'), is_minting=True)
    assert wallet.balance == Decimal('100'), "Balance should be 100"
    assert wallet.total_minted == Decimal('100'), "Total minted should be 100"
    
    print("✅ Deposit successful")
    print(f"   Balance: {wallet.balance}")
    print(f"   Total minted: {wallet.total_minted}")
    
    # Test withdrawal
    wallet.withdraw(Decimal('30'), is_burning=True)
    assert wallet.balance == Decimal('70'), "Balance should be 70"
    assert wallet.total_burned == Decimal('30'), "Total burned should be 30"
    
    print("✅ Withdrawal successful")
    print(f"   Balance: {wallet.balance}")
    print(f"   Total burned: {wallet.total_burned}")
    
    # Test insufficient balance
    try:
        wallet.withdraw(Decimal('100'))
        assert False, "Should raise ValueError"
    except ValueError:
        print("✅ Insufficient balance check works")


def test_vaultnode_blockchain():
    """Test VaultNode blockchain"""
    print("\n" + "=" * 70)
    print("TEST: VaultNode Blockchain")
    print("=" * 70)
    
    vault = VaultNode(vault_id="ΔΩ.TEST")
    
    # Check genesis block
    assert len(vault.blocks) == 1, "Should have genesis block"
    assert vault.blocks[0].block_number == 0, "Genesis block number should be 0"
    
    print("✅ Genesis block created")
    print(f"   Block number: {vault.blocks[0].block_number}")
    
    # Add events
    event1 = VaultEvent(
        event_type="test_event_1",
        event_data={'test': 'data1'}
    )
    event2 = VaultEvent(
        event_type="test_event_2",
        event_data={'test': 'data2'}
    )
    
    vault.add_event(event1)
    vault.add_event(event2)
    
    assert len(vault.pending_events) == 2, "Should have 2 pending events"
    
    print("✅ Events added")
    print(f"   Pending events: {len(vault.pending_events)}")
    
    # Create block
    oracle_signatures = {
        'chief_oracle': hashlib.sha256(b"chief").hexdigest(),
        'senior_oracle_1': hashlib.sha256(b"senior1").hexdigest(),
        'senior_oracle_2': hashlib.sha256(b"senior2").hexdigest()
    }
    
    block = vault.create_block(oracle_signatures=oracle_signatures)
    
    assert block.block_number == 1, "Block number should be 1"
    assert len(block.events) == 2, "Block should have 2 events"
    assert block.consensus_reached, "Consensus should be reached"
    assert len(vault.pending_events) == 0, "Pending events should be cleared"
    
    print("✅ Block created")
    print(f"   Block number: {block.block_number}")
    print(f"   Events: {len(block.events)}")
    print(f"   Consensus: {block.consensus_reached}")
    
    # Verify chain
    chain_valid = vault.verify_chain()
    assert chain_valid, "Chain should be valid"
    
    print("✅ Chain verification passed")


def test_merkle_tree():
    """Test Merkle tree construction"""
    print("\n" + "=" * 70)
    print("TEST: Merkle Tree")
    print("=" * 70)
    
    # Create events
    events = [
        VaultEvent(event_type="event1", event_data={'data': 1}),
        VaultEvent(event_type="event2", event_data={'data': 2}),
        VaultEvent(event_type="event3", event_data={'data': 3}),
        VaultEvent(event_type="event4", event_data={'data': 4})
    ]
    
    # Build tree
    tree = MerkleTree(events)
    root_hash = tree.get_root_hash()
    
    assert root_hash, "Root hash should exist"
    assert len(root_hash) == 64, "SHA-256 hash should be 64 chars"
    
    print("✅ Merkle tree built")
    print(f"   Root hash: {root_hash[:16]}...")
    print(f"   Events: {len(events)}")
    
    # Verify event
    assert tree.verify_event(events[0]), "Event should be in tree"
    
    print("✅ Event verification works")


def test_coin_burning():
    """Test ScarCoin burning"""
    print("\n" + "=" * 70)
    print("TEST: ScarCoin Burning")
    print("=" * 70)
    
    engine = ScarCoinMintingEngine()
    wallet = engine.create_wallet()
    
    # Mint coin
    transmutation_id = str(uuid.uuid4())
    oracle_sigs = ["oracle_1", "oracle_2"]
    
    coin = engine.mint_scarcoin(
        transmutation_id=transmutation_id,
        scarindex_before=Decimal('0.65'),
        scarindex_after=Decimal('0.80'),
        transmutation_efficiency=Decimal('0.95'),
        owner_address=wallet.address,
        oracle_signatures=oracle_sigs
    )
    
    initial_balance = wallet.balance
    
    # Burn coin
    success = engine.burn_scarcoin(coin.id, reason="Test burning")
    
    assert success, "Burning should succeed"
    assert coin.burned, "Coin should be marked as burned"
    assert wallet.balance == Decimal('0'), "Wallet balance should be 0"
    assert wallet.total_burned == initial_balance, "Total burned should match initial balance"
    
    print("✅ Coin burning successful")
    print(f"   Coin burned: {coin.burned}")
    print(f"   Wallet balance: {wallet.balance}")
    print(f"   Total burned: {wallet.total_burned}")


def test_supply_statistics():
    """Test supply statistics"""
    print("\n" + "=" * 70)
    print("TEST: Supply Statistics")
    print("=" * 70)
    
    engine = ScarCoinMintingEngine()
    wallet = engine.create_wallet()
    
    # Mint multiple coins
    for i in range(3):
        transmutation_id = str(uuid.uuid4())
        oracle_sigs = ["oracle_1", "oracle_2"]
        
        engine.mint_scarcoin(
            transmutation_id=transmutation_id,
            scarindex_before=Decimal('0.60'),
            scarindex_after=Decimal('0.75'),
            transmutation_efficiency=Decimal('0.90'),
            owner_address=wallet.address,
            oracle_signatures=oracle_sigs
        )
    
    stats = engine.get_supply_stats()
    
    assert stats['minting_count'] == 3, "Should have 3 minting events"
    assert Decimal(stats['total_supply']) > 0, "Total supply should be positive"
    
    print("✅ Supply statistics correct")
    print(f"   Total supply: {stats['total_supply']}")
    print(f"   Minting count: {stats['minting_count']}")
    print(f"   Active wallets: {stats['active_wallets']}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("HOLO-ECONOMY TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("ScarCoin Minting", test_scarcoin_minting),
        ("Proof-of-Ache Validation", test_proof_of_ache_validation),
        ("Wallet Operations", test_wallet_operations),
        ("VaultNode Blockchain", test_vaultnode_blockchain),
        ("Merkle Tree", test_merkle_tree),
        ("Coin Burning", test_coin_burning),
        ("Supply Statistics", test_supply_statistics)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
        except AssertionError as exc:
            print(f"\n❌ {test_name} FAILED: {exc}")
            failed += 1
        except Exception as exc:
            print(f"\n❌ {test_name} ERROR: {exc}")
            failed += 1
        else:
            passed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\nTotal Tests: {len(tests)}")
    print(f"Passed: {passed} ({passed/len(tests)*100:.1f}%)")
    print(f"Failed: {failed}")
    print()
    
    if failed == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ {failed} TEST(S) FAILED")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
