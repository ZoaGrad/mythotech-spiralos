-- SpiralOS – SWPS Witness Protocol Logic Migration
-- ΔΩ.147.2 — Triggers & Functions for First Breath

-- 1. ASSESSMENT LOGIC
CREATE OR REPLACE FUNCTION handle_assessment_logic()
RETURNS TRIGGER AS $$
BEGIN
    -- If verdict is 'verified', update claim status to 'witnessed'
    IF NEW.verdict = 'verified' THEN
        UPDATE stream_claims
        SET status = 'witnessed',
            finalized_at = now()
        WHERE id = NEW.claim_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_assessment_insert ON witness_assessments;
CREATE TRIGGER on_assessment_insert
AFTER INSERT ON witness_assessments
FOR EACH ROW
EXECUTE FUNCTION handle_assessment_logic();

-- 2. EMP QUEUE LOGIC
CREATE OR REPLACE FUNCTION trigger_emp_queue()
RETURNS TRIGGER AS $$
BEGIN
    -- When claim becomes 'witnessed', queue EMP minting
    IF NEW.status = 'witnessed' AND OLD.status != 'witnessed' THEN
        INSERT INTO emp_mint_queue (claim_id, recipient_id, amount, mint_reason, status)
        VALUES (
            NEW.id,
            NEW.user_id,
            10.0, -- Default amount for now
            'Witnessed Stream Claim',
            'queued'
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_claim_witnessed_queue ON stream_claims;
CREATE TRIGGER on_claim_witnessed_queue
AFTER UPDATE ON stream_claims
FOR EACH ROW
EXECUTE FUNCTION trigger_emp_queue();

-- 3. VAULT SEAL LOGIC
CREATE OR REPLACE FUNCTION seal_ledger_entry()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO vault_nodes (node_type, reference_id, state_hash, metadata, hash_signature, node_address)
    VALUES (
        'EMP_MINT',
        NEW.id,
        gen_random_uuid(), -- Placeholder for actual state hash
        jsonb_build_object('amount', NEW.amount, 'owner_id', NEW.owner_id),
        md5(NEW.id::text || NEW.created_at::text), -- Simple signature for First Breath
        '127.0.0.1'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_emp_ledger_seal ON emp_ledger;
CREATE TRIGGER on_emp_ledger_seal
AFTER INSERT ON emp_ledger
FOR EACH ROW
EXECUTE FUNCTION seal_ledger_entry();
