#!/bin/bash

# Quick Setup Script for Blockchain Loan System
# Run this script to automatically set up the development environment

echo "🚀 Starting Blockchain Loan System Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "Please run this script from the Nexora root directory"
    exit 1
fi

print_status "Setting up blockchain contracts directory..."

# Create contracts directory
mkdir -p ../loan-escrow-contracts
cd ../loan-escrow-contracts

# Initialize npm project if not exists
if [ ! -f "package.json" ]; then
    print_status "Initializing npm project..."
    npm init -y
fi

# Install dependencies
print_status "Installing Hardhat and dependencies..."
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox @openzeppelin/contracts
npm install dotenv

# Initialize Hardhat if not exists
if [ ! -f "hardhat.config.js" ]; then
    print_status "Initializing Hardhat project..."
    echo "Creating Hardhat project structure..."
    
    # Create hardhat.config.js
    cat > hardhat.config.js << 'EOF'
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337
    },
    hardhat: {
      chainId: 31337
    }
  }
};
EOF

    # Create directories
    mkdir -p contracts scripts test

    # Create the smart contract
    cat > contracts/LoanEscrow.sol << 'EOF'
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract LoanEscrow {
    address public admin;
    uint256 public totalEscrowBalance;
    uint256 public loanCounter;
    
    struct LoanRequest {
        address borrower;
        uint256 amount;
        uint256 creditScore;
        bool approved;
        bool disbursed;
        bool repaid;
        uint256 timestamp;
        string businessName;
        string businessType;
    }
    
    struct Lender {
        address lenderAddress;
        uint256 amountDeposited;
        string name;
        uint256 timestamp;
    }
    
    mapping(uint256 => LoanRequest) public loanRequests;
    mapping(address => Lender) public lenders;
    mapping(address => uint256[]) public borrowerLoans;
    
    event LoanRequested(uint256 loanId, address borrower, uint256 amount, uint256 creditScore);
    event LoanApproved(uint256 loanId, address borrower, uint256 amount);
    event LoanDisbursed(uint256 loanId, address borrower, uint256 amount);
    event LoanRepaid(uint256 loanId, address borrower, uint256 amount);
    event FundsDeposited(address lender, uint256 amount, string name);
    event FundsWithdrawn(address lender, uint256 amount);
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }
    
    constructor() {
        admin = msg.sender;
    }
    
    function requestLoan(
        uint256 _amount,
        uint256 _creditScore,
        string memory _businessName,
        string memory _businessType
    ) external {
        require(_amount > 0, "Loan amount must be greater than 0");
        require(_creditScore >= 600, "Credit score must be at least 600");
        require(_amount <= calculateMaxLoanAmount(_creditScore), "Loan amount exceeds maximum allowed");
        require(_amount <= totalEscrowBalance * 80 / 100, "Insufficient escrow balance");
        
        loanCounter++;
        
        loanRequests[loanCounter] = LoanRequest({
            borrower: msg.sender,
            amount: _amount,
            creditScore: _creditScore,
            approved: false,
            disbursed: false,
            repaid: false,
            timestamp: block.timestamp,
            businessName: _businessName,
            businessType: _businessType
        });
        
        borrowerLoans[msg.sender].push(loanCounter);
        
        emit LoanRequested(loanCounter, msg.sender, _amount, _creditScore);
    }
    
    function approveLoan(uint256 _loanId) external onlyAdmin {
        require(_loanId <= loanCounter && _loanId > 0, "Invalid loan ID");
        require(!loanRequests[_loanId].approved, "Loan already approved");
        
        loanRequests[_loanId].approved = true;
        
        emit LoanApproved(_loanId, loanRequests[_loanId].borrower, loanRequests[_loanId].amount);
    }
    
    function disburseLoan(uint256 _loanId) external onlyAdmin {
        require(_loanId <= loanCounter && _loanId > 0, "Invalid loan ID");
        require(loanRequests[_loanId].approved, "Loan not approved");
        require(!loanRequests[_loanId].disbursed, "Loan already disbursed");
        require(address(this).balance >= loanRequests[_loanId].amount, "Insufficient contract balance");
        
        loanRequests[_loanId].disbursed = true;
        totalEscrowBalance -= loanRequests[_loanId].amount;
        
        payable(loanRequests[_loanId].borrower).transfer(loanRequests[_loanId].amount);
        
        emit LoanDisbursed(_loanId, loanRequests[_loanId].borrower, loanRequests[_loanId].amount);
    }
    
    function repayLoan(uint256 _loanId) external payable {
        require(_loanId <= loanCounter && _loanId > 0, "Invalid loan ID");
        require(loanRequests[_loanId].borrower == msg.sender, "Not the borrower");
        require(loanRequests[_loanId].disbursed, "Loan not disbursed");
        require(!loanRequests[_loanId].repaid, "Loan already repaid");
        require(msg.value >= loanRequests[_loanId].amount, "Insufficient repayment amount");
        
        loanRequests[_loanId].repaid = true;
        totalEscrowBalance += msg.value;
        
        emit LoanRepaid(_loanId, msg.sender, msg.value);
    }
    
    function depositFunds(string memory _name) external payable {
        require(msg.value > 0, "Deposit amount must be greater than 0");
        
        if (lenders[msg.sender].lenderAddress == address(0)) {
            lenders[msg.sender] = Lender({
                lenderAddress: msg.sender,
                amountDeposited: msg.value,
                name: _name,
                timestamp: block.timestamp
            });
        } else {
            lenders[msg.sender].amountDeposited += msg.value;
        }
        
        totalEscrowBalance += msg.value;
        
        emit FundsDeposited(msg.sender, msg.value, _name);
    }
    
    function withdrawFunds(uint256 _amount) external {
        require(lenders[msg.sender].lenderAddress != address(0), "Not a registered lender");
        require(lenders[msg.sender].amountDeposited >= _amount, "Insufficient deposited amount");
        require(address(this).balance >= _amount, "Insufficient contract balance");
        
        lenders[msg.sender].amountDeposited -= _amount;
        totalEscrowBalance -= _amount;
        
        payable(msg.sender).transfer(_amount);
        
        emit FundsWithdrawn(msg.sender, _amount);
    }
    
    function calculateMaxLoanAmount(uint256 _creditScore) public pure returns (uint256) {
        if (_creditScore < 600) return 0;
        if (_creditScore >= 600 && _creditScore < 700) return 1 ether;
        if (_creditScore >= 700 && _creditScore < 800) return 3 ether;
        if (_creditScore >= 800) return 5 ether;
        return 0;
    }
    
    function getLoanRequest(uint256 _loanId) external view returns (LoanRequest memory) {
        require(_loanId <= loanCounter && _loanId > 0, "Invalid loan ID");
        return loanRequests[_loanId];
    }
    
    function getBorrowerLoans(address _borrower) external view returns (uint256[] memory) {
        return borrowerLoans[_borrower];
    }
    
    function getEscrowBalance() external view returns (uint256) {
        return totalEscrowBalance;
    }
    
    function getContractBalance() external view returns (uint256) {
        return address(this).balance;
    }
    
    function getLender(address _lender) external view returns (Lender memory) {
        return lenders[_lender];
    }
    
    receive() external payable {
        totalEscrowBalance += msg.value;
        emit FundsDeposited(msg.sender, msg.value, "Direct Deposit");
    }
    
    fallback() external payable {
        totalEscrowBalance += msg.value;
        emit FundsDeposited(msg.sender, msg.value, "Fallback Deposit");
    }
}
EOF

    # Create deployment script
    cat > scripts/deploy.js << 'EOF'
const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Deploying LoanEscrow contract to localhost...");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  const LoanEscrow = await ethers.getContractFactory("LoanEscrow");
  const loanEscrow = await LoanEscrow.deploy();

  await loanEscrow.waitForDeployment();

  const contractAddress = await loanEscrow.getAddress();
  console.log("✅ LoanEscrow deployed to:", contractAddress);

  console.log("💰 Funding contract with 10 ETH for testing...");
  const fundTx = await deployer.sendTransaction({
    to: contractAddress,
    value: ethers.parseEther("10.0")
  });
  await fundTx.wait();

  console.log("✅ Contract funded successfully!");
  
  console.log("🧪 Testing basic contract functions...");
  
  const admin = await loanEscrow.admin();
  console.log("Admin address:", admin);
  
  const escrowBalance = await loanEscrow.getEscrowBalance();
  console.log("Escrow balance:", ethers.formatEther(escrowBalance), "ETH");

  const maxLoan600 = await loanEscrow.calculateMaxLoanAmount(600);
  const maxLoan700 = await loanEscrow.calculateMaxLoanAmount(700);
  const maxLoan800 = await loanEscrow.calculateMaxLoanAmount(800);
  
  console.log("Max loan for credit score 600:", ethers.formatEther(maxLoan600), "ETH");
  console.log("Max loan for credit score 700:", ethers.formatEther(maxLoan700), "ETH");
  console.log("Max loan for credit score 800:", ethers.formatEther(maxLoan800), "ETH");

  const deploymentInfo = {
    contractAddress: contractAddress,
    adminAddress: admin,
    networkName: "localhost",
    chainId: 31337,
    deployedAt: new Date().toISOString()
  };

  console.log("\n📝 Deployment Summary:");
  console.log(JSON.stringify(deploymentInfo, null, 2));
  
  return deploymentInfo;
}

main()
  .then((deploymentInfo) => {
    console.log("\n🎉 Deployment completed successfully!");
    console.log("\n📋 Next Steps:");
    console.log("1. Copy the contract address:", deploymentInfo.contractAddress);
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
EOF

fi

print_status "Blockchain setup completed!"
print_warning "Now run the following commands in separate terminals:"
echo ""
echo "Terminal 1 - Start Hardhat Node:"
echo "cd loan-escrow-contracts && npx hardhat node"
echo ""
echo "Terminal 2 - Deploy Contract:"
echo "cd loan-escrow-contracts && npx hardhat run scripts/deploy.js --network localhost"
echo ""
echo "Terminal 3 - Start Backend:"
echo "cd nexora/python_services && .\.venv\Scripts\Activate.ps1 && python combined_api.py"
echo ""
echo "Terminal 4 - Start Frontend:"
echo "cd nexora/Nexora && npm run dev"
echo ""
print_status "Setup script completed! Follow the instructions above."
