-- SpiralOS – SWPS VaultNode Schema Fix
-- ΔΩ.147.4 — Add missing columns for Witness Protocol

ALTER TABLE vault_nodes
    ADD COLUMN IF NOT EXISTS reference_id uuid,
    ADD COLUMN IF NOT EXISTS node_type text,
    ADD COLUMN IF NOT EXISTS state_hash text;

-- Add index for reference_id for performance
CREATE INDEX IF NOT EXISTS idx_vault_nodes_reference_id ON vault_nodes(reference_id);
