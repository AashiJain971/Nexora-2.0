import { ethers } from "ethers";

// Contract ABI for the LoanEscrow contract
export const LOAN_ESCROW_ABI = [
  "function createLoan(uint256 _amount, uint256 _interestRate, uint256 _duration) external returns (uint256)",
  "function fundLoan(uint256 _loanId) external payable",
  "function repayLoan(uint256 _loanId) external payable",
  "function markDefault(uint256 _loanId) external",
  "function getLoan(uint256 _loanId) external view returns (tuple(address borrower, address lender, uint256 amount, uint256 interestRate, uint256 duration, uint256 createdAt, uint256 dueDate, bool funded, bool repaid, bool defaulted))",
  "function nextLoanId() external view returns (uint256)",
  "event LoanCreated(uint256 indexed loanId, address indexed borrower, uint256 amount)",
  "event LoanFunded(uint256 indexed loanId, address indexed lender)",
  "event LoanRepaid(uint256 indexed loanId)",
  "event LoanDefaulted(uint256 indexed loanId)",
];

// Replace with your deployed contract address
export const LOAN_ESCROW_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"; // Deployed LoanEscrow contract

export interface Loan {
  borrower: string;
  lender: string;
  amount: bigint;
  interestRate: bigint;
  duration: bigint;
  createdAt: bigint;
  dueDate: bigint;
  funded: boolean;
  repaid: boolean;
  defaulted: boolean;
}

export class BlockchainService {
  private provider: ethers.BrowserProvider | null = null;
  private signer: ethers.JsonRpcSigner | null = null;
  private contract: ethers.Contract | null = null;

  async connect(): Promise<boolean> {
    try {
      if (!window.ethereum) {
        throw new Error("Please install MetaMask!");
      }

      this.provider = new ethers.BrowserProvider(window.ethereum);
      await this.provider.send("eth_requestAccounts", []);
      this.signer = await this.provider.getSigner();
      this.contract = new ethers.Contract(
        LOAN_ESCROW_ADDRESS,
        LOAN_ESCROW_ABI,
        this.signer
      );

      return true;
    } catch (error) {
      console.error("Failed to connect to wallet:", error);
      return false;
    }
  }

  async getAccount(): Promise<string | null> {
    try {
      if (!this.signer) {
        await this.connect();
      }
      return (await this.signer?.getAddress()) || null;
    } catch (error) {
      console.error("Failed to get account:", error);
      return null;
    }
  }

  async getBalance(address: string): Promise<string> {
    try {
      if (!this.provider) {
        await this.connect();
      }
      const balance = await this.provider!.getBalance(address);
      return ethers.formatEther(balance);
    } catch (error) {
      console.error("Failed to get balance:", error);
      return "0";
    }
  }

  async createLoan(
    amount: string,
    interestRate: number,
    duration: number
  ): Promise<string> {
    try {
      if (!this.contract) {
        await this.connect();
      }

      const tx = await this.contract!.createLoan(
        ethers.parseEther(amount),
        interestRate,
        duration
      );

      const receipt = await tx.wait();
      return receipt.hash;
    } catch (error) {
      console.error("Failed to create loan:", error);
      throw error;
    }
  }

  async fundLoan(loanId: number, amount: string): Promise<string> {
    try {
      if (!this.contract) {
        await this.connect();
      }

      const tx = await this.contract!.fundLoan(loanId, {
        value: ethers.parseEther(amount),
      });

      const receipt = await tx.wait();
      return receipt.hash;
    } catch (error) {
      console.error("Failed to fund loan:", error);
      throw error;
    }
  }

  async repayLoan(loanId: number, amount: string): Promise<string> {
    try {
      if (!this.contract) {
        await this.connect();
      }

      const tx = await this.contract!.repayLoan(loanId, {
        value: ethers.parseEther(amount),
      });

      const receipt = await tx.wait();
      return receipt.hash;
    } catch (error) {
      console.error("Failed to repay loan:", error);
      throw error;
    }
  }

  async markDefault(loanId: number): Promise<string> {
    try {
      if (!this.contract) {
        await this.connect();
      }

      const tx = await this.contract!.markDefault(loanId);
      const receipt = await tx.wait();
      return receipt.hash;
    } catch (error) {
      console.error("Failed to mark loan as default:", error);
      throw error;
    }
  }

  async getLoan(loanId: number): Promise<Loan | null> {
    try {
      if (!this.contract) {
        await this.connect();
      }

      const loan = await this.contract!.getLoan(loanId);
      return {
        borrower: loan.borrower,
        lender: loan.lender,
        amount: loan.amount,
        interestRate: loan.interestRate,
        duration: loan.duration,
        createdAt: loan.createdAt,
        dueDate: loan.dueDate,
        funded: loan.funded,
        repaid: loan.repaid,
        defaulted: loan.defaulted,
      };
    } catch (error) {
      console.error("Failed to get loan:", error);
      return null;
    }
  }

  async getNextLoanId(): Promise<number> {
    try {
      if (!this.contract) {
        await this.connect();
      }

      const nextId = await this.contract!.nextLoanId();
      return Number(nextId);
    } catch (error) {
      console.error("Failed to get next loan ID:", error);
      return 0;
    }
  }

  // Listen for contract events
  onLoanCreated(
    callback: (loanId: number, borrower: string, amount: string) => void
  ) {
    if (!this.contract) return;

    this.contract.on("LoanCreated", (loanId, borrower, amount) => {
      callback(Number(loanId), borrower, ethers.formatEther(amount));
    });
  }

  onLoanFunded(callback: (loanId: number, lender: string) => void) {
    if (!this.contract) return;

    this.contract.on("LoanFunded", (loanId, lender) => {
      callback(Number(loanId), lender);
    });
  }

  onLoanRepaid(callback: (loanId: number) => void) {
    if (!this.contract) return;

    this.contract.on("LoanRepaid", (loanId) => {
      callback(Number(loanId));
    });
  }

  onLoanDefaulted(callback: (loanId: number) => void) {
    if (!this.contract) return;

    this.contract.on("LoanDefaulted", (loanId) => {
      callback(Number(loanId));
    });
  }

  removeAllListeners() {
    if (this.contract) {
      this.contract.removeAllListeners();
    }
  }
}

// Export singleton instance
export const blockchainService = new BlockchainService();

// Helper function to format addresses
export const formatAddress = (address: string): string => {
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
};

// Helper function to format ether amounts
export const formatEther = (value: string): string => {
  const num = parseFloat(value);
  if (num === 0) return "0";
  if (num < 0.0001) return "< 0.0001";
  return num.toFixed(4);
};
