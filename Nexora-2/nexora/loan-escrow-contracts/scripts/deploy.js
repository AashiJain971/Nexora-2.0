const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Deploying LoanEscrow contract to localhost...");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log(
    "Account balance:",
    ethers.formatEther(await deployer.provider.getBalance(deployer.address))
  );

  const LoanEscrow = await ethers.getContractFactory("LoanEscrow");
  const loanEscrow = await LoanEscrow.deploy();

  await loanEscrow.waitForDeployment();

  const contractAddress = await loanEscrow.getAddress();
  console.log("✅ LoanEscrow deployed to:", contractAddress);

  console.log("🧪 Testing basic contract functions...");

  const nextLoanId = await loanEscrow.nextLoanId();
  console.log("Next loan ID:", nextLoanId.toString());

  const deploymentInfo = {
    contractAddress: contractAddress,
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
