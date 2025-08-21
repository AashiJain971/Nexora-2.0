# MetaMask Setup for Local Development

## 🦊 Step 1: Install MetaMask

1. Install MetaMask browser extension from https://metamask.io/
2. Create a new wallet or import existing one
3. Complete the setup process

## 🌐 Step 2: Add Localhost Network

1. Open MetaMask
2. Click on the network dropdown (currently showing "Ethereum Mainnet")
3. Click "Add network"
4. Click "Add a network manually"
5. Fill in the following details:
   - **Network name**: Hardhat Local
   - **New RPC URL**: http://127.0.0.1:8545
   - **Chain ID**: 31337
   - **Currency symbol**: ETH
   - **Block explorer URL**: (leave empty)
6. Click "Save"

## 💰 Step 3: Import Test Account

Hardhat provides test accounts with ETH for development:

1. In MetaMask, click on the account icon (top right)
2. Click "Import Account"
3. Select "Private Key" as the import method
4. Use one of these Hardhat test private keys:

**Account #0 (Deployer)**

- Address: `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`
- Private Key: `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`

**Account #1**

- Address: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`
- Private Key: `0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d`

**Account #2**

- Address: `0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC`
- Private Key: `0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a`

## ⚠️ Security Note

**NEVER use these private keys on mainnet or with real funds!** These are well-known test keys.

## 🧪 Step 4: Verify Setup

1. Switch to "Hardhat Local" network in MetaMask
2. Your imported account should show 10,000 ETH
3. You're ready to interact with the deployed contract!

## 🔗 Contract Information

- **Contract Address**: `0x5FbDB2315678afecb367f032d93F642f64180aa3`
- **Network**: Hardhat Local (localhost:8545)
- **Chain ID**: 31337
