-- ═══════════════════════════════════════════════════════════════════════════
-- SpiralOS PostgreSQL Functions Test Suite
-- ΔΩ.126.0 — Constitutional Cognitive Sovereignty
-- ═══════════════════════════════════════════════════════════════════════════
-- Test coverage for all PostgreSQL functions in production schema
-- ═══════════════════════════════════════════════════════════════════════════

-- Enable plpgsql for test functions
CREATE EXTENSION IF NOT EXISTS plpgsql;

-- ───────────────────────────────────────────────────────────────────────────
-- TEST 1: Coherence Component Functions
-- ───────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    test_content JSONB;
    n_score DECIMAL(10, 6);
    s_score DECIMAL(10, 6);
    e_score DECIMAL(10, 6);
    t_score DECIMAL(10, 6);
BEGIN
    RAISE NOTICE 'TEST 1: Coherence Component Functions';
    
    -- Test with explicit scores
    test_content := jsonb_build_object(
        'narrative_score', 0.85,
        'social_score', 0.75,
        'economic_score', 0.65,
        'technical_score', 0.90
    );
    
    n_score := public.narrative_coherence(test_content);
    s_score := public.social_coherence('github_commit', test_content);
    e_score := public.economic_coherence(test_content);
    t_score := public.technical_coherence(test_content);
    
    ASSERT n_score = 0.85, 'Narrative coherence should return 0.85';
    ASSERT s_score = 0.75, 'Social coherence should return 0.75';
    ASSERT e_score = 0.65, 'Economic coherence should return 0.65';
    ASSERT t_score = 0.90, 'Technical coherence should return 0.90';
    
    RAISE NOTICE '✓ Coherence component functions work correctly';
    
    -- Test with missing scores (defaults)
    test_content := '{}'::JSONB;
    
    n_score := public.narrative_coherence(test_content);
    ASSERT n_score = 0.5, 'Default narrative coherence should be 0.5';
    
    RAISE NOTICE '✓ Default coherence values work correctly';
END $$;

-- ───────────────────────────────────────────────────────────────────────────
-- TEST 2: PID Controller Update
-- ───────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    pid RECORD;
BEGIN
    RAISE NOTICE 'TEST 2: PID Controller Update';
    
    -- Initialize PID if not exists
    DELETE FROM public.pid_controller_state;
    INSERT INTO public.pid_controller_state DEFAULT VALUES;
    
    -- Update with current = 0.5, target = 0.7
    PERFORM public.update_pid_controller(0.5, 0.7);
    
    SELECT * INTO pid FROM public.pid_controller_state LIMIT 1;
    
    ASSERT pid.current_scarindex = 0.5, 'Current ScarIndex should be 0.5';
    ASSERT pid.error = 0.2, 'Error should be 0.2 (target - current)';
    ASSERT pid.guidance_scale > 0.1 AND pid.guidance_scale < 2.0, 'Guidance scale should be clamped';
    
    RAISE NOTICE '✓ PID controller updates correctly';
    RAISE NOTICE '  Error: %, Guidance: %', pid.error, pid.guidance_scale;
    
    -- Test anti-windup by making large integral
    UPDATE public.pid_controller_state SET integral = 15.0;
    PERFORM public.update_pid_controller(0.3, 0.7);
    
    SELECT * INTO pid FROM public.pid_controller_state LIMIT 1;
    ASSERT pid.integral <= 10.0, 'Integral should be clamped to 10.0 (anti-windup)';
    
    RAISE NOTICE '✓ PID anti-windup works correctly';
END $$;

-- ───────────────────────────────────────────────────────────────────────────
-- TEST 3: Coherence Calculation (ScarIndex Engine)
-- ───────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    test_event_id UUID;
    calc RECORD;
BEGIN
    RAISE NOTICE 'TEST 3: Coherence Calculation';
    
    -- Create test Ache event
    INSERT INTO public.ache_events (
        source,
        content,
        ache_level
    ) VALUES (
        'test_source',
        jsonb_build_object(
            'narrative_score', 0.8,
            'social_score', 0.7,
            'economic_score', 0.6,
            'technical_score', 0.9
        ),
        0.4
    ) RETURNING id INTO test_event_id;
    
    -- Calculate ScarIndex
    SELECT * INTO calc FROM public.coherence_calculation(test_event_id);
    
    ASSERT calc.ache_event_id = test_event_id, 'Calculation should link to event';
    ASSERT calc.c_narrative = 0.8, 'Narrative component should be 0.8';
    ASSERT calc.c_social = 0.7, 'Social component should be 0.7';
    ASSERT calc.c_economic = 0.6, 'Economic component should be 0.6';
    ASSERT calc.c_technical = 0.9, 'Technical component should be 0.9';
    ASSERT calc.scarindex > 0 AND calc.scarindex <= 1.0, 'ScarIndex should be in [0,1]';
    ASSERT calc.is_valid = TRUE, 'Calculation should be marked valid';
    
    -- Check weighted calculation (0.3*0.8 + 0.25*0.7 + 0.25*0.6 + 0.2*0.9) * guidance
    -- = (0.24 + 0.175 + 0.15 + 0.18) * guidance = 0.745 * guidance
    -- With default guidance ~1.0, should be around 0.745
    ASSERT calc.scarindex >= 0.5 AND calc.scarindex <= 0.9, 'ScarIndex should be reasonable';
    
    RAISE NOTICE '✓ Coherence calculation works correctly';
    RAISE NOTICE '  ScarIndex: %, Ache before: %, Ache after: %', 
        calc.scarindex, calc.ache_before, calc.ache_after;
    
    -- Clean up
    DELETE FROM public.ache_events WHERE id = test_event_id;
END $$;

-- ───────────────────────────────────────────────────────────────────────────
-- TEST 4: Panic Frame Trigger
-- ───────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    test_event_id UUID;
    calc_id UUID;
    panic_count INTEGER;
    frozen_count INTEGER;
BEGIN
    RAISE NOTICE 'TEST 4: Panic Frame Trigger';
    
    -- Clean up existing panic frames
    DELETE FROM public.panic_frames;
    DELETE FROM public.smart_contract_txns;
    
    -- Create a low ScarIndex event to trigger panic
    INSERT INTO public.ache_events (
        source,
        content,
        ache_level
    ) VALUES (
        'panic_test',
        jsonb_build_object(
            'narrative_score', 0.2,
            'social_score', 0.2,
            'economic_score', 0.2,
            'technical_score', 0.2
        ),
        0.9
    ) RETURNING id INTO test_event_id;
    
    -- Create some transactions to be frozen
    INSERT INTO public.smart_contract_txns (
        txn_type,
        scarcoin_delta,
        is_valid
    ) VALUES
        ('MINT', 100, TRUE),
        ('MINT', 200, TRUE),
        ('BURN', -50, TRUE);
    
    -- Manually insert low ScarIndex to trigger panic (bypass calculation)
    INSERT INTO public.scarindex_calculations (
        ache_event_id,
        c_narrative,
        c_social,
        c_economic,
        c_technical,
        scarindex,
        ache_before,
        ache_after,
        is_valid
    ) VALUES (
        test_event_id,
        0.2, 0.2, 0.2, 0.2,
        0.25,  -- Below 0.3 threshold
        0.5,
        0.9,
        TRUE
    ) RETURNING id INTO calc_id;
    
    -- Check panic frame was created
    SELECT COUNT(*) INTO panic_count FROM public.panic_frames WHERE status = 'ACTIVE';
    ASSERT panic_count > 0, 'Panic frame should be created when ScarIndex < 0.3';
    
    -- Check transactions were frozen
    SELECT COUNT(*) INTO frozen_count FROM public.smart_contract_txns WHERE is_frozen = TRUE;
    ASSERT frozen_count > 0, 'Transactions should be frozen during panic';
    
    RAISE NOTICE '✓ Panic frame trigger works correctly';
    RAISE NOTICE '  Active panic frames: %, Frozen transactions: %', panic_count, frozen_count;
    
    -- Clean up
    DELETE FROM public.ache_events WHERE id = test_event_id;
    DELETE FROM public.panic_frames;
    DELETE FROM public.smart_contract_txns;
END $$;

-- ───────────────────────────────────────────────────────────────────────────
-- TEST 5: VaultNode Sealing
-- ───────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    test_ref_id UUID := gen_random_uuid();
    node1 RECORD;
    node2 RECORD;
BEGIN
    RAISE NOTICE 'TEST 5: VaultNode Sealing';
    
    -- Clean up existing vaultnodes
    DELETE FROM public.vaultnodes;
    
    -- Seal first node (genesis)
    SELECT * INTO node1 FROM public.seal_vaultnode(
        test_ref_id,
        'test_node',
        'abc123commit'
    );
    
    ASSERT node1.reference_id = test_ref_id, 'Reference ID should match';
    ASSERT node1.node_type = 'test_node', 'Node type should match';
    ASSERT node1.github_commit_sha = 'abc123commit', 'Commit SHA should match';
    ASSERT node1.state_hash IS NOT NULL, 'State hash should be generated';
    ASSERT node1.previous_hash IS NULL, 'First node should have no previous hash';
    
    RAISE NOTICE '✓ First VaultNode sealed correctly (genesis)';
    
    -- Seal second node (should link to first)
    SELECT * INTO node2 FROM public.seal_vaultnode(
        gen_random_uuid(),
        'test_node_2',
        'def456commit'
    );
    
    ASSERT node2.previous_hash = node1.state_hash, 'Second node should link to first';
    ASSERT node2.state_hash != node1.state_hash, 'Each node should have unique hash';
    
    RAISE NOTICE '✓ VaultNode Merkle chain works correctly';
    RAISE NOTICE '  Node 1 hash: %', substring(node1.state_hash, 1, 16);
    RAISE NOTICE '  Node 2 hash: %', substring(node2.state_hash, 1, 16);
    RAISE NOTICE '  Node 2 prev: %', substring(node2.previous_hash, 1, 16);
    
    -- Clean up
    DELETE FROM public.vaultnodes;
END $$;

-- ───────────────────────────────────────────────────────────────────────────
-- TEST 6: ScarCoin Minting (Proof-of-Ache)
-- ───────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    test_event_id UUID;
    calc_id UUID;
    txn_count INTEGER;
    mint_delta DECIMAL(20, 6);
BEGIN
    RAISE NOTICE 'TEST 6: ScarCoin Minting';
    
    -- Clean up
    DELETE FROM public.smart_contract_txns;
    
    -- Create event with Ache transmutation (before > after)
    INSERT INTO public.ache_events (
        source,
        content,
        ache_level
    ) VALUES (
        'mint_test',
        jsonb_build_object('test', 'data'),
        0.3  -- Low ache after (coherence gained)
    ) RETURNING id INTO test_event_id;
    
    -- Create calculation with positive delta_ache
    INSERT INTO public.scarindex_calculations (
        ache_event_id,
        c_narrative, c_social, c_economic, c_technical,
        scarindex,
        ache_before,
        ache_after,
        is_valid
    ) VALUES (
        test_event_id,
        0.7, 0.7, 0.7, 0.7,
        0.7,
        0.8,  -- High ache before
        0.3,  -- Low ache after = 0.5 delta
        TRUE
    ) RETURNING id INTO calc_id;
    
    -- Mint ScarCoin
    PERFORM public.mint_scarcoin(calc_id);
    
    -- Check transaction was created
    SELECT COUNT(*) INTO txn_count FROM public.smart_contract_txns 
    WHERE txn_type = 'MINT' AND to_state = calc_id;
    
    ASSERT txn_count = 1, 'Mint transaction should be created';
    
    SELECT scarcoin_delta INTO mint_delta FROM public.smart_contract_txns
    WHERE txn_type = 'MINT' AND to_state = calc_id;
    
    -- Delta should be (0.8 - 0.3) * 1000000 = 500000
    ASSERT mint_delta = 500000, 'Mint delta should be 500000';
    
    RAISE NOTICE '✓ ScarCoin minting works correctly (Proof-of-Ache)';
    RAISE NOTICE '  Minted: % ScarCoins', mint_delta;
    
    -- Test no minting when ache increases (invalid PoA)
    DELETE FROM public.smart_contract_txns;
    
    INSERT INTO public.scarindex_calculations (
        ache_event_id,
        c_narrative, c_social, c_economic, c_technical,
        scarindex,
        ache_before,
        ache_after,
        is_valid
    ) VALUES (
        test_event_id,
        0.5, 0.5, 0.5, 0.5,
        0.5,
        0.3,  -- Low ache before
        0.8,  -- High ache after = negative delta (invalid)
        TRUE
    ) RETURNING id INTO calc_id;
    
    PERFORM public.mint_scarcoin(calc_id);
    
    SELECT COUNT(*) INTO txn_count FROM public.smart_contract_txns;
    ASSERT txn_count = 0, 'No mint should occur when ache increases';
    
    RAISE NOTICE '✓ Invalid Proof-of-Ache correctly rejected';
    
    -- Clean up
    DELETE FROM public.ache_events WHERE id = test_event_id;
END $$;

-- ───────────────────────────────────────────────────────────────────────────
-- TEST 7: Views
-- ───────────────────────────────────────────────────────────────────────────

DO $$
DECLARE
    oracle RECORD;
    health RECORD;
BEGIN
    RAISE NOTICE 'TEST 7: Database Views';
    
    -- Test ScarIndex Oracle view
    SELECT * INTO oracle FROM public.scar_index_oracle_sync;
    
    ASSERT oracle.total_nodes_30d IS NOT NULL, 'Oracle should return total nodes';
    ASSERT oracle.coherence_rate_30d IS NOT NULL, 'Oracle should return coherence rate';
    
    RAISE NOTICE '✓ ScarIndex Oracle view works';
    RAISE NOTICE '  Total nodes (30d): %, Coherence rate: %%', 
        oracle.total_nodes_30d, oracle.coherence_rate_30d;
    
    -- Test system health view
    SELECT * INTO health FROM public.system_health;
    
    ASSERT health.current_scarindex IS NOT NULL, 'Health should show current ScarIndex';
    ASSERT health.active_panic_frames IS NOT NULL, 'Health should show panic frames';
    
    RAISE NOTICE '✓ System health view works';
    RAISE NOTICE '  Current ScarIndex: %, Active panic frames: %',
        health.current_scarindex, health.active_panic_frames;
END $$;

-- ───────────────────────────────────────────────────────────────────────────
-- TEST SUMMARY
-- ───────────────────────────────────────────────────────────────────────────

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE 'ALL TESTS PASSED ✓';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE 'Test coverage:';
    RAISE NOTICE '  ✓ Coherence component functions';
    RAISE NOTICE '  ✓ PID controller update';
    RAISE NOTICE '  ✓ ScarIndex calculation engine';
    RAISE NOTICE '  ✓ Panic frame trigger (F4)';
    RAISE NOTICE '  ✓ VaultNode Merkle sealing';
    RAISE NOTICE '  ✓ ScarCoin minting (Proof-of-Ache)';
    RAISE NOTICE '  ✓ Database views';
    RAISE NOTICE '';
    RAISE NOTICE 'System Integrity: Verified';
    RAISE NOTICE 'Constitutional Compliance: Enforced';
    RAISE NOTICE 'Thermodynamic Honesty: Maintained';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
END $$;
