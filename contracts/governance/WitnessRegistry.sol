// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title WitnessRegistry
 * @dev Manages the registration and lifecycle of Witnesses in the SpiralOS ecosystem.
 * A Witness is an identity-verified entity responsible for attesting to the state of the system.
 */
contract WitnessRegistry is Ownable {
    using Counters for Counters.Counter;

    // Counter for generating unique Witness IDs
    Counters.Counter private _witnessIds;

    // Struct to store Witness data
    struct Witness {
        uint256 id;
        address account;
        string metadataUri; // IPFS hash or URL to witness metadata
        bool isActive;
        uint256 registrationTimestamp;
    }

    // Mapping from Witness ID to Witness struct
    mapping(uint256 => Witness) private _witnesses;

    // Mapping from address to Witness ID
    mapping(address => uint256) private _witnessIdByAddress;

    // Event emitted when a new Witness is registered
    event WitnessRegistered(uint256 indexed witnessId, address indexed account, string metadataUri);

    // Event emitted when a Witness's status is updated
    event WitnessStatusUpdated(uint256 indexed witnessId, bool isActive);

    /**
     * @dev Registers a new Witness.
     * @param account The Ethereum address of the Witness.
     * @param metadataUri A URI pointing to the Witness's metadata.
     *
     * Requirements:
     * - The caller must be the contract owner.
     * - The account must not already be registered as a Witness.
     */
    function registerWitness(address account, string calldata metadataUri) public onlyOwner {
        require(_witnessIdByAddress[account] == 0, "WitnessRegistry: Account already registered");

        _witnessIds.increment();
        uint256 newWitnessId = _witnessIds.current();

        _witnesses[newWitnessId] = Witness({
            id: newWitnessId,
            account: account,
            metadataUri: metadataUri,
            isActive: true,
            registrationTimestamp: block.timestamp
        });

        _witnessIdByAddress[account] = newWitnessId;

        emit WitnessRegistered(newWitnessId, account, metadataUri);
    }

    /**
     * @dev Deactivates a Witness.
     * @param witnessId The ID of the Witness to deactivate.
     *
     * Requirements:
     * - The caller must be the contract owner.
     */
    function deactivateWitness(uint256 witnessId) public onlyOwner {
        _witnesses[witnessId].isActive = false;
        emit WitnessStatusUpdated(witnessId, false);
    }

    /**
     * @dev Reactivates a Witness.
     * @param witnessId The ID of the Witness to reactivate.
     *
     * Requirements:
     * - The caller must be the contract owner.
     */
    function reactivateWitness(uint256 witnessId) public onlyOwner {
        _witnesses[witnessId].isActive = true;
        emit WitnessStatusUpdated(witnessId, true);
    }

    /**
     * @dev Retrieves the details of a Witness.
     * @param witnessId The ID of the Witness.
     * @return The Witness struct.
     */
    function getWitness(uint256 witnessId) public view returns (Witness memory) {
        return _witnesses[witnessId];
    }

    /**
     * @dev Retrieves the Witness ID for a given address.
     * @param account The address of the Witness.
     * @return The Witness ID.
     */
    function getWitnessIdByAddress(address account) public view returns (uint256) {
        return _witnessIdByAddress[account];
    }

    /**
     * @dev Returns the total number of registered Witnesses.
     * @return The total number of Witnesses.
     */
    function getTotalWitnesses() public view returns (uint256) {
        return _witnessIds.current();
    }
}
