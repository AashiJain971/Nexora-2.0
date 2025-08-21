# Complete Localhost Deployment Guide for Blockchain Loan System

This guide will walk you through setting up and running the complete blockchain loan system on your local machine.

## 🔧 Prerequisites

1. **Node.js** (v16 or higher) - [Download here](https://nodejs.org/)
2. **Python** (v3.8 or higher) - Already installed ✅
3. **Git** - [Download here](https://git-scm.com/)
4. **MetaMask Browser Extension** - [Install here](https://metamask.io/)

## 📋 Step-by-Step Deployment

### Step 1: Set Up Local Blockchain (Hardhat Network)

```powershell
# Create a new directory for blockchain contracts
mkdir loan-escrow-contracts
cd loan-escrow-contracts

# Initialize npm project
npm init -y

# Install Hardhat and dependencies
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox @openzeppelin/contracts
npm install dotenv

# Initialize Hardhat project
npx hardhat
# Choose "Create a JavaScript project" when prompted
```

### Step 2: Configure Hardhat

Create/update `hardhat.config.js`:

```javascript
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337,
    },
    hardhat: {
      chainId: 31337,
    },
  },
};
```

### Step 3: Create the Smart Contract

Create `contracts/LoanEscrow.sol` and copy the contract code from your project:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract LoanEscrow {
    // ... (copy the full contract code from your LoanEscrow.sol file)
}
```

### Step 4: Create Deployment Script

Create `scripts/deploy.js`:

```javascript
const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Deploying LoanEscrow contract to localhost...");

  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Deploy the contract
  const LoanEscrow = await ethers.getContractFactory("LoanEscrow");
  const loanEscrow = await LoanEscrow.deploy();

  await loanEscrow.waitForDeployment();

  const contractAddress = await loanEscrow.getAddress();
  console.log("✅ LoanEscrow deployed to:", contractAddress);

  // Fund the contract with some ETH for testing
  console.log("💰 Funding contract with 10 ETH for testing...");
  const fundTx = await deployer.sendTransaction({
    to: contractAddress,
    value: ethers.parseEther("10.0"),
  });
  await fundTx.wait();

  console.log("✅ Contract funded successfully!");

  // Test basic functionality
  console.log("🧪 Testing basic contract functions...");

  const admin = await loanEscrow.admin();
  console.log("Admin address:", admin);

  const escrowBalance = await loanEscrow.getEscrowBalance();
  console.log("Escrow balance:", ethers.formatEther(escrowBalance), "ETH");

  // Calculate max loan for different credit scores
  const maxLoan600 = await loanEscrow.calculateMaxLoanAmount(600);
  const maxLoan700 = await loanEscrow.calculateMaxLoanAmount(700);
  const maxLoan800 = await loanEscrow.calculateMaxLoanAmount(800);

  console.log(
    "Max loan for credit score 600:",
    ethers.formatEther(maxLoan600),
    "ETH"
  );
  console.log(
    "Max loan for credit score 700:",
    ethers.formatEther(maxLoan700),
    "ETH"
  );
  console.log(
    "Max loan for credit score 800:",
    ethers.formatEther(maxLoan800),
    "ETH"
  );

  // Save deployment info
  const deploymentInfo = {
    contractAddress: contractAddress,
    adminAddress: admin,
    networkName: "localhost",
    chainId: 31337,
    deployedAt: new Date().toISOString(),
  };

  console.log("\n📝 Deployment Summary:");
  console.log(JSON.stringify(deploymentInfo, null, 2));

  return deploymentInfo;
}

main()
  .then((deploymentInfo) => {
    console.log("\n🎉 Deployment completed successfully!");
    console.log("\n📋 Next Steps:");
    console.log(
      "1. Copy the contract address:",
      deploymentInfo.contractAddress
    );
    console.log("2. Update your backend .env file");
    console.log("3. Update your frontend blockchain.ts file");
    console.log("4. Configure MetaMask for localhost network");
    console.log("5. Start your backend and frontend servers");
    process.exit(0);
  })
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
```

### Step 5: Start Local Blockchain Network

Open a new PowerShell terminal and run:

```powershell
cd loan-escrow-contracts
npx hardhat node
```

**Keep this terminal running!** This is your local blockchain network.

### Step 6: Deploy the Smart Contract

In another terminal:

```powershell
cd loan-escrow-contracts
npx hardhat run scripts/deploy.js --network localhost
```

**Save the contract address** that gets printed!

### Step 7: Configure MetaMask for Localhost

1. Open MetaMask in your browser
2. Click on the network dropdown (usually shows "Ethereum Mainnet")
3. Click "Add Network" → "Add a network manually"
4. Fill in:
   - **Network Name**: Hardhat Localhost
   - **New RPC URL**: http://127.0.0.1:8545
   - **Chain ID**: 31337
   - **Currency Symbol**: ETH
5. Click "Save"

### Step 8: Import Test Account to MetaMask

When you ran `npx hardhat node`, it showed you test accounts with private keys. Import one:

1. In MetaMask, click your account icon → "Import Account"
2. Paste one of the private keys from the Hardhat node output
3. You should now have ~10,000 ETH for testing

### Step 9: Configure Backend Environment

Navigate to your python_services directory and create/update `.env`:

```powershell
cd "c:\Users\souna\OneDrive\Desktop\Nexora-2.0\Nexora-2\nexora\python_services"
```

Create `.env` file:

```env
# Blockchain Configuration
ETH_RPC_URL=http://127.0.0.1:8545
LOAN_ESCROW_ADDRESS=YOUR_CONTRACT_ADDRESS_FROM_STEP_6
ADMIN_PRIVATE_KEY=YOUR_ADMIN_PRIVATE_KEY_FROM_HARDHAT_NODE

# Supabase Configuration (your existing values)
SUPABASE_URL=https://eecbqzvcnwrkcxgwjxlt.supabase.co
SUPABASE_KEY=your_supabase_key_here

# GROQ API Key (your existing value)
GROQ_API_KEY=your_groq_api_key_here
```

### Step 10: Update Frontend Configuration

Update `client/src/lib/blockchain.ts`:

```typescript
// Replace YOUR_CONTRACT_ADDRESS with the address from Step 6
export const LOAN_ESCROW_ADDRESS = "YOUR_CONTRACT_ADDRESS_FROM_STEP_6";

// Make sure the network configuration matches localhost
export const LOCALHOST_NETWORK = {
  chainId: 31337,
  name: "Hardhat Localhost",
  rpcUrl: "http://127.0.0.1:8545",
};
```

### Step 11: Start Backend Server

```powershell
cd "c:\Users\souna\OneDrive\Desktop\Nexora-2.0\Nexora-2\nexora\python_services"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start the server
python combined_api.py
```

You should see blockchain initialization messages.

### Step 12: Start Frontend Server

In a new terminal:

```powershell
cd "c:\Users\souna\OneDrive\Desktop\Nexora-2.0\Nexora-2\nexora\Nexora"
npm run dev
```

### Step 13: Test the Complete System

1. **Open your browser** to `http://localhost:5002` (or whatever port Vite shows)

2. **Connect MetaMask**:

   - Make sure you're on the Hardhat Localhost network
   - Connect your imported test account

3. **Test User Registration/Login**:

   - Create a test account or login with existing credentials

4. **Upload Test Invoices**:

   - Go to the invoice upload section
   - Upload some test invoices to build credit score

5. **Test Blockchain Loan Flow**:
   - Navigate to the blockchain loans page
   - Try requesting a loan
   - Check if the wallet connection works
   - Verify the credit score calculation

## 🔧 Troubleshooting

### Common Issues & Solutions

1. **"Contract not deployed" error**:

   ```powershell
   # Restart Hardhat node and redeploy
   npx hardhat node
   # In another terminal:
   npx hardhat run scripts/deploy.js --network localhost
   ```

2. **MetaMask transaction fails**:

   - Reset your MetaMask account: Settings → Advanced → Reset Account

3. **Backend can't connect to blockchain**:

   - Check if Hardhat node is running
   - Verify contract address in .env file
   - Check RPC URL is correct

4. **Frontend wallet connection issues**:

   - Make sure MetaMask is on Hardhat Localhost network
   - Refresh the page and try connecting again

5. **Python packages missing**:
   ```powershell
   pip install fastapi uvicorn web3 python-dotenv supabase
   ```

## 📊 Testing the System

### Test Scenarios

1. **Loan Request with Good Credit**:

   - Upload invoices with good payment history
   - Request a loan within limits
   - Should succeed

2. **Loan Request with Poor Credit**:

   - Request a loan with credit score < 600
   - Should be rejected

3. **Loan Request Exceeding Limits**:

   - Request more than maximum allowed for credit score
   - Should be rejected

4. **Admin Functions** (if configured):
   - Approve/reject loan requests
   - Check escrow balance

## 🚀 Production Deployment Notes

When you're ready to deploy to a real testnet:

1. Replace localhost RPC with Infura/Alchemy URL
2. Use real testnet (Sepolia) instead of localhost
3. Get testnet ETH from faucets
4. Never use mainnet for testing!

## 📝 Important Files Summary

- **Smart Contract**: `loan-escrow-contracts/contracts/LoanEscrow.sol`
- **Backend Config**: `python_services/.env`
- **Frontend Config**: `client/src/lib/blockchain.ts`
- **Deployment Script**: `loan-escrow-contracts/scripts/deploy.js`

## 🎯 Expected Results

After successful deployment, you should be able to:

✅ Connect MetaMask wallet to localhost network  
✅ Request loans based on credit score  
✅ See real-time blockchain transactions  
✅ View loan status and history  
✅ Experience smooth UI interactions

## 🆘 Getting Help

If you encounter issues:

1. Check terminal outputs for error messages
2. Verify all configuration files have correct values
3. Make sure all services are running (Hardhat node, backend, frontend)
4. Check MetaMask network and account settings
5. Look at browser console for frontend errors

**Remember**: This is a development setup for testing only. Never use real funds or private keys from this setup in production!
