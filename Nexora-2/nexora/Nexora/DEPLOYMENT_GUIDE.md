# Smart Contract Deployment Guide

This guide will help you deploy the LoanEscrow smart contract to a testnet and configure the application.

## Prerequisites

1. Install [Node.js](https://nodejs.org/) (v16 or higher)
2. Install [Hardhat](https://hardhat.org/): `npm install -g hardhat`
3. Install [MetaMask](https://metamask.io/) browser extension
4. Get some testnet ETH from [Sepolia Faucet](https://sepoliafaucet.com/)

## Step 1: Setup Hardhat Project

```bash
mkdir loan-escrow-contracts
cd loan-escrow-contracts
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npx hardhat
```

Choose "Create a JavaScript project" when prompted.

## Step 2: Update hardhat.config.js

Replace the contents of `hardhat.config.js`:

```javascript
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.19",
  networks: {
    sepolia: {
      url: `https://sepolia.infura.io/v3/${process.env.INFURA_PROJECT_ID}`,
      accounts: [process.env.PRIVATE_KEY],
    },
    localhost: {
      url: "http://127.0.0.1:8545",
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY,
  },
};
```

## Step 3: Create Environment File

Create a `.env` file in the project root:

```env
PRIVATE_KEY=your_wallet_private_key_here
INFURA_PROJECT_ID=your_infura_project_id_here
ETHERSCAN_API_KEY=your_etherscan_api_key_here
```

**⚠️ Never commit your private key to version control!**

## Step 4: Copy the Smart Contract

Copy the `LoanEscrow.sol` contract from `contracts/LoanEscrow.sol` to `contracts/LoanEscrow.sol` in your Hardhat project.

## Step 5: Create Deployment Script

Create `scripts/deploy.js`:

```javascript
const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying LoanEscrow contract...");

  const LoanEscrow = await ethers.getContractFactory("LoanEscrow");
  const loanEscrow = await LoanEscrow.deploy();

  await loanEscrow.waitForDeployment();

  const contractAddress = await loanEscrow.getAddress();
  console.log("LoanEscrow deployed to:", contractAddress);

  // Verify contract on Etherscan (optional)
  if (network.name !== "hardhat" && network.name !== "localhost") {
    console.log("Waiting for block confirmations...");
    await loanEscrow.deploymentTransaction().wait(6);

    console.log("Verifying contract...");
    try {
      await hre.run("verify:verify", {
        address: contractAddress,
        constructorArguments: [],
      });
    } catch (error) {
      console.log("Verification failed:", error);
    }
  }

  return contractAddress;
}

main()
  .then((address) => {
    console.log("\n🎉 Deployment completed!");
    console.log("📝 Contract Address:", address);
    console.log("\n📋 Next steps:");
    console.log("1. Update LOAN_ESCROW_ADDRESS in your .env file");
    console.log("2. Update the contract address in blockchain.ts");
    console.log("3. Fund the contract with some test ETH");
    process.exit(0);
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

## Step 6: Deploy to Sepolia Testnet

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

## Step 7: Update Application Configuration

1. **Update Backend (.env)**:

   ```env
   ETH_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
   LOAN_ESCROW_ADDRESS=YOUR_DEPLOYED_CONTRACT_ADDRESS
   ADMIN_PRIVATE_KEY=YOUR_ADMIN_PRIVATE_KEY
   ```

2. **Update Frontend** (`client/src/lib/blockchain.ts`):
   ```typescript
   export const LOAN_ESCROW_ADDRESS = "YOUR_DEPLOYED_CONTRACT_ADDRESS";
   ```

## Step 8: Test the Deployment

1. **Check contract on Etherscan**:

   - Go to https://sepolia.etherscan.io/
   - Search for your contract address
   - Verify the contract is deployed and verified

2. **Test basic functions**:

   ```bash
   npx hardhat console --network sepolia
   ```

   ```javascript
   const LoanEscrow = await ethers.getContractFactory("LoanEscrow");
   const contract = LoanEscrow.attach("YOUR_CONTRACT_ADDRESS");

   // Check admin
   console.log("Admin:", await contract.admin());

   // Check escrow balance
   console.log("Escrow Balance:", await contract.getEscrowBalance());
   ```

## Step 9: Fund the Contract (For Testing)

You can deposit some test ETH to the escrow for testing:

```javascript
// In Hardhat console or create a separate script
const tx = await contract.depositFunds("Test Lender", {
  value: ethers.parseEther("1.0"), // 1 ETH
});
await tx.wait();
```

## Environment Variables Summary

### Backend (.env in python_services folder):

```env
ETH_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID
LOAN_ESCROW_ADDRESS=0xYourContractAddress
ADMIN_PRIVATE_KEY=0xYourAdminPrivateKey
```

### Frontend (update in blockchain.ts):

```typescript
export const LOAN_ESCROW_ADDRESS = "0xYourContractAddress";
```

## Security Notes

1. **Never use mainnet for testing** - Always use testnets
2. **Keep private keys secure** - Never commit them to version control
3. **Use environment variables** - Store sensitive data in .env files
4. **Test thoroughly** - Test all functions before deploying to mainnet
5. **Consider multi-sig** - For production, consider using a multi-signature wallet for admin functions

## Troubleshooting

### Common Issues:

1. **"insufficient funds for intrinsic transaction cost"**

   - Solution: Make sure you have enough ETH in your wallet for gas fees

2. **"nonce too high"**

   - Solution: Reset MetaMask account or check transaction history

3. **"contract not deployed"**

   - Solution: Verify the contract address and network configuration

4. **"execution reverted"**
   - Solution: Check function parameters and contract state

### Getting Help:

- Check transaction on Etherscan for detailed error messages
- Use `console.log` in smart contracts for debugging
- Test functions individually before running the full application

## Production Deployment

For production deployment to mainnet:

1. Use a hardware wallet or multi-sig for admin functions
2. Audit the smart contract thoroughly
3. Implement proper access controls
4. Consider implementing upgradeable contracts
5. Set up monitoring and alerts
6. Have an emergency pause mechanism

## Next Steps

After successful deployment:

1. Test the loan request flow
2. Test the approval and disbursement process
3. Set up monitoring for contract events
4. Configure proper user permissions
5. Test the repayment functionality

Remember: This is experimental software. Only use with test funds and understand the risks involved in DeFi applications.
