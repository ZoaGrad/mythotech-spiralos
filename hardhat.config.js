require("@nomiclabs/hardhat-waffle");
require("dotenv").config();

const { POLYGON_MUMBAI_API_KEY, DEPLOYER_PRIVATE_KEY } = process.env;

module.exports = {
  solidity: "0.8.20",
  networks: {
    mumbai: {
      url: POLYGON_MUMBAI_API_KEY || "",
      accounts: DEPLOYER_PRIVATE_KEY ? [DEPLOYER_PRIVATE_KEY] : [],
    },
  },
};
