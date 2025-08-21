import { useState, useEffect, useCallback } from "react";
import { blockchainService, type Loan } from "../lib/blockchain";

export interface UseBlockchainReturn {
  // Connection state
  isConnected: boolean;
  account: string | null;
  balance: string;

  // Loading states
  connecting: boolean;
  loading: boolean;

  // Functions
  connect: () => Promise<boolean>;
  disconnect: () => void;

  // Loan functions
  createLoan: (
    amount: string,
    interestRate: number,
    duration: number
  ) => Promise<string>;
  fundLoan: (loanId: number, amount: string) => Promise<string>;
  repayLoan: (loanId: number, amount: string) => Promise<string>;
  markDefault: (loanId: number) => Promise<string>;

  // View functions
  getLoan: (loanId: number) => Promise<Loan | null>;
  getNextLoanId: () => Promise<number>;

  // Refresh functions
  refreshBalance: () => Promise<void>;

  // Error state
  error: string | null;
}

export function useBlockchain(): UseBlockchainReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [account, setAccount] = useState<string | null>(null);
  const [balance, setBalance] = useState("0");
  const [connecting, setConnecting] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Connect to wallet
  const connect = useCallback(async (): Promise<boolean> => {
    setConnecting(true);
    setError(null);

    try {
      const success = await blockchainService.connect();
      if (success) {
        const userAccount = await blockchainService.getAccount();
        const userBalance = await blockchainService.getBalance(userAccount!);

        setAccount(userAccount);
        setBalance(userBalance);
        setIsConnected(true);

        // Set up event listeners
        setupEventListeners();

        return true;
      }
      return false;
    } catch (err: any) {
      setError(err.message || "Failed to connect wallet");
      return false;
    } finally {
      setConnecting(false);
    }
  }, []);

  // Disconnect wallet
  const disconnect = useCallback(() => {
    setIsConnected(false);
    setAccount(null);
    setBalance("0");
    setError(null);
    blockchainService.removeAllListeners();
  }, []);

  // Setup event listeners
  const setupEventListeners = useCallback(() => {
    blockchainService.onLoanCreated((loanId, borrower, amount) => {
      console.log(`Loan created: ${amount} ETH by ${borrower} (ID: ${loanId})`);
    });

    blockchainService.onLoanFunded((loanId, lender) => {
      console.log(`Loan funded: ID ${loanId} by ${lender}`);
      if (lender.toLowerCase() === account?.toLowerCase()) {
        refreshBalance();
      }
    });

    blockchainService.onLoanRepaid((loanId) => {
      console.log(`Loan repaid: ID ${loanId}`);
      refreshBalance();
    });

    blockchainService.onLoanDefaulted((loanId) => {
      console.log(`Loan defaulted: ID ${loanId}`);
    });
  }, [account]);

  // Refresh user balance
  const refreshBalance = useCallback(async () => {
    if (account) {
      try {
        const newBalance = await blockchainService.getBalance(account);
        setBalance(newBalance);
      } catch (err: any) {
        setError(err.message || "Failed to refresh balance");
      }
    }
  }, [account]);

  // Create loan
  const createLoan = useCallback(
    async (
      amount: string,
      interestRate: number,
      duration: number
    ): Promise<string> => {
      setLoading(true);
      setError(null);

      try {
        const txHash = await blockchainService.createLoan(
          amount,
          interestRate,
          duration
        );
        return txHash;
      } catch (err: any) {
        setError(err.message || "Failed to create loan");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  // Fund loan
  const fundLoan = useCallback(
    async (loanId: number, amount: string): Promise<string> => {
      setLoading(true);
      setError(null);

      try {
        const txHash = await blockchainService.fundLoan(loanId, amount);
        await refreshBalance();
        return txHash;
      } catch (err: any) {
        setError(err.message || "Failed to fund loan");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [refreshBalance]
  );

  // Repay loan
  const repayLoan = useCallback(
    async (loanId: number, amount: string): Promise<string> => {
      setLoading(true);
      setError(null);

      try {
        const txHash = await blockchainService.repayLoan(loanId, amount);
        await refreshBalance();
        return txHash;
      } catch (err: any) {
        setError(err.message || "Failed to repay loan");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [refreshBalance]
  );

  // Mark loan as default
  const markDefault = useCallback(async (loanId: number): Promise<string> => {
    setLoading(true);
    setError(null);

    try {
      const txHash = await blockchainService.markDefault(loanId);
      return txHash;
    } catch (err: any) {
      setError(err.message || "Failed to mark loan as default");
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Get loan
  const getLoan = useCallback(async (loanId: number): Promise<Loan | null> => {
    try {
      return await blockchainService.getLoan(loanId);
    } catch (err: any) {
      setError(err.message || "Failed to get loan");
      return null;
    }
  }, []);

  // Get next loan ID
  const getNextLoanId = useCallback(async (): Promise<number> => {
    try {
      return await blockchainService.getNextLoanId();
    } catch (err: any) {
      setError(err.message || "Failed to get next loan ID");
      return 0;
    }
  }, []);

  // Auto-connect if previously connected
  useEffect(() => {
    const autoConnect = async () => {
      if (window.ethereum) {
        try {
          const accounts = await window.ethereum.request({
            method: "eth_accounts",
          });
          if (accounts.length > 0) {
            await connect();
          }
        } catch (err) {
          console.warn("Auto-connect failed:", err);
        }
      }
    };

    autoConnect();
  }, [connect]);

  // Listen for account changes
  useEffect(() => {
    if (window.ethereum) {
      const handleAccountsChanged = (accounts: string[]) => {
        if (accounts.length === 0) {
          disconnect();
        } else if (accounts[0] !== account) {
          connect();
        }
      };

      const handleChainChanged = () => {
        window.location.reload();
      };

      window.ethereum.on("accountsChanged", handleAccountsChanged);
      window.ethereum.on("chainChanged", handleChainChanged);

      return () => {
        window.ethereum?.removeListener(
          "accountsChanged",
          handleAccountsChanged
        );
        window.ethereum?.removeListener("chainChanged", handleChainChanged);
      };
    }
  }, [account, connect, disconnect]);

  return {
    // Connection state
    isConnected,
    account,
    balance,

    // Loading states
    connecting,
    loading,

    // Functions
    connect,
    disconnect,

    // Loan functions
    createLoan,
    fundLoan,
    repayLoan,
    markDefault,

    // View functions
    getLoan,
    getNextLoanId,

    // Refresh functions
    refreshBalance,

    // Error state
    error,
  };
}
