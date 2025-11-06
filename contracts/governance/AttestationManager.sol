// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./WitnessRegistry.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title AttestationManager
 * @dev Manages attestations made by Witnesses.
 * Attestations are cryptographic signatures that vouch for the state of off-chain data.
 */
contract AttestationManager is Ownable {
    using Counters for Counters.Counter;

    // Reference to the WitnessRegistry contract
    WitnessRegistry public witnessRegistry;

    // Counter for generating unique Attestation IDs
    Counters.Counter private _attestationIds;

    // Struct to store Attestation data
    struct Attestation {
        uint256 id;
        uint256 witnessId;
        bytes32 dataHash; // The hash of the attested data
        uint256 timestamp;
    }

    // Mapping from Attestation ID to Attestation struct
    mapping(uint256 => Attestation) private _attestations;

    // Event emitted when a new Attestation is created
    event AttestationCreated(
        uint256 indexed attestationId,
        uint256 indexed witnessId,
        bytes32 dataHash
    );

    /**
     * @dev Sets the WitnessRegistry address.
     * @param registryAddress The address of the WitnessRegistry contract.
     */
    constructor(address registryAddress) {
        witnessRegistry = WitnessRegistry(registryAddress);
    }

    /**
     * @dev Submits a new attestation.
     * @param dataHash The hash of the data being attested to.
     *
     * Requirements:
     * - The caller must be a registered and active Witness.
     */
    function submitAttestation(bytes32 dataHash) public {
        uint256 witnessId = witnessRegistry.getWitnessIdByAddress(msg.sender);
        require(witnessId != 0, "AttestationManager: Caller is not a registered Witness");

        WitnessRegistry.Witness memory witness = witnessRegistry.getWitness(witnessId);
        require(witness.isActive, "AttestationManager: Witness is not active");

        _attestationIds.increment();
        uint256 newAttestationId = _attestationIds.current();

        _attestations[newAttestationId] = Attestation({
            id: newAttestationId,
            witnessId: witnessId,
            dataHash: dataHash,
            timestamp: block.timestamp
        });

        emit AttestationCreated(newAttestationId, witnessId, dataHash);
    }

    /**
     * @dev Retrieves the details of an Attestation.
     * @param attestationId The ID of the Attestation.
     * @return The Attestation struct.
     */
    function getAttestation(uint256 attestationId) public view returns (Attestation memory) {
        return _attestations[attestationId];
    }

    /**
     * @dev Returns the total number of attestations.
     * @return The total number of attestations.
     */
    function getTotalAttestations() public view returns (uint256) {
        return _attestationIds.current();
    }
}
