const { ethers } = require("hardhat");
const fs = require("fs");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);

  // Deploy WitnessRegistry
  const WitnessRegistry = await ethers.getContractFactory("WitnessRegistry");
  const witnessRegistry = await WitnessRegistry.deploy();
  await witnessRegistry.deployed();
  console.log("WitnessRegistry deployed to:", witnessRegistry.address);

  // Deploy AttestationManager
  const AttestationManager = await ethers.getContractFactory("AttestationManager");
  const attestationManager = await AttestationManager.deploy(witnessRegistry.address);
  await attestationManager.deployed();
  console.log("AttestationManager deployed to:", attestationManager.address);

  // Save contract addresses to a file
  const contracts = {
    WitnessRegistry: witnessRegistry.address,
    AttestationManager: attestationManager.address,
  };

  fs.writeFileSync("contracts.json", JSON.stringify(contracts));
  console.log("Contract addresses saved to contracts.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
