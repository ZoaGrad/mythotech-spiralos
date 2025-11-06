// scripts/etl/wi_indexer.ts

import { ethers } from 'ethers';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
import express from 'express';

dotenv.config();

// --- Environment Setup ---
const {
    POLYGON_MUMBAI_API_KEY,
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
    WITNESS_REGISTRY_ADDRESS,
    ATTESTATION_MANAGER_ADDRESS
} = process.env;

if (!POLYGON_MUMBAI_API_KEY || !SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY || !WITNESS_REGISTRY_ADDRESS || !ATTESTATION_MANAGER_ADDRESS) {
    console.error("🚨 Missing required environment variables.");
    process.exit(1);
}

// --- Supabase & Ethers Clients ---
const supabase: SupabaseClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
const provider = new ethers.providers.JsonRpcProvider(POLYGON_MUMBAI_API_KEY);

// --- Contract ABIs (Simplified for event listening) ---
const witnessRegistryAbi = [
    "event WitnessRegistered(uint256 indexed witnessId, address indexed account, string metadataUri)"
];

const attestationManagerAbi = [
    "event AttestationCreated(uint256 indexed attestationId, uint256 indexed witnessId, bytes32 dataHash)"
];

// --- Contract Instances ---
const registryContract = new ethers.Contract(WITNESS_REGISTRY_ADDRESS, witnessRegistryAbi, provider);
const attestationContract = new ethers.Contract(ATTESTATION_MANAGER_ADDRESS, attestationManagerAbi, provider);

// --- Event Handlers ---

/**
 * Handles the WitnessRegistered event.
 * @param witnessId - The ID of the new witness.
 * @param account - The Ethereum address of the witness.
 * @param metadataUri - The metadata URI for the witness.
 */
async function handleWitnessRegistered(witnessId: ethers.BigNumber, account: string, metadataUri: string) {
    console.log(`Received WitnessRegistered event: ID=${witnessId}, Account=${account}`);

    const { data, error } = await supabase.from('witnesses').insert({
        witness_id: witnessId.toNumber(),
        account: account,
        metadata_uri: metadataUri,
        is_active: true,
        registration_timestamp: new Date().toISOString()
    });

    if (error) {
        console.error(`Error inserting new witness (ID: ${witnessId}):`, error.message);
    } else {
        console.log(`Successfully indexed new witness: ID=${witnessId}`);
    }
}

/**
 * Handles the AttestationCreated event.
 * @param attestationId - The ID of the new attestation.
 * @param witnessId - The ID of the witness who created the attestation.
 * @param dataHash - The hash of the attested data.
 */
async function handleAttestationCreated(attestationId: ethers.BigNumber, witnessId: ethers.BigNumber, dataHash: string) {
    console.log(`Received AttestationCreated event: ID=${attestationId}, WitnessID=${witnessId}`);

    const { data, error } = await supabase.from('attestations').insert({
        attestation_id: attestationId.toNumber(),
        witness_id: witnessId.toNumber(),
        data_hash: dataHash,
        timestamp: new Date().toISOString()
    });

    if (error) {
        console.error(`Error inserting new attestation (ID: ${attestationId}):`, error.message);
    } else {
        console.log(`Successfully indexed new attestation: ID=${attestationId}`);
    }
}

// --- Main Logic ---

function main() {
    console.log("🌀 Starting SpiralOS Witness Indexer...");
    console.log("Listening for on-chain events...");

    registryContract.on("WitnessRegistered", handleWitnessRegistered);
    attestationContract.on("AttestationCreated", handleAttestationCreated);

    const app = express();
    const port = process.env.PORT || 8080;

    app.get('/', (req, res) => {
        res.send('Witness Indexer is running.');
    });

    app.listen(port, () => {
        console.log(`Server listening on port ${port}`);
    });
}

main();
