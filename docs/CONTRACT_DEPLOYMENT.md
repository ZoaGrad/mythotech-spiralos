# Smart Contract Deployment Guide

## Overview
This guide details the deployment process for SpiralOS smart contracts (`AttestationManager.sol`, `WitnessRegistry.sol`) to the target blockchain (e.g., Ethereum, Polygon, or a local Hardhat network).

## Prerequisites
- Node.js & npm
- Hardhat (`npm install --save-dev hardhat`)
- Wallet Private Key (stored in `.env` as `PRIVATE_KEY`)
- RPC URL (stored in `.env` as `RPC_URL`)

## Deployment Steps

1.  **Compile Contracts**
    ```bash
    npx hardhat compile
    ```

2.  **Deploy to Network**
    Create a deployment script `scripts/deploy.js`:
    ```javascript
    const hre = require("hardhat");

    async function main() {
      const AttestationManager = await hre.ethers.getContractFactory("AttestationManager");
      const attestationManager = await AttestationManager.deploy();
      await attestationManager.deployed();
      console.log("AttestationManager deployed to:", attestationManager.address);

      const WitnessRegistry = await hre.ethers.getContractFactory("WitnessRegistry");
      const witnessRegistry = await WitnessRegistry.deploy(attestationManager.address);
      await witnessRegistry.deployed();
      console.log("WitnessRegistry deployed to:", witnessRegistry.address);
    }

    main().catch((error) => {
      console.error(error);
      process.exitCode = 1;
    });
    ```

    Run the deployment:
    ```bash
    npx hardhat run scripts/deploy.js --network <network_name>
    ```

3.  **Verify Contracts**
    ```bash
    npx hardhat verify --network <network_name> <contract_address> <constructor_arguments>
    ```

## Integration
After deployment, update the `core/contracts/config.py` or `.env` with the new contract addresses.
- `ATTESTATION_MANAGER_ADDRESS`
- `WITNESS_REGISTRY_ADDRESS`

## Security
- Never commit `.env` files containing private keys.
- Use a dedicated deployer wallet with limited funds.
