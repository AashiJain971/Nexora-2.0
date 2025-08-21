import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Alert, AlertDescription } from "../ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import {
  DollarSign,
  TrendingUp,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  Wallet,
  Building2,
  Calendar,
} from "lucide-react";
import { useBlockchain } from "../../hooks/use-blockchain";
import { type Loan } from "../../lib/blockchain";
import { formatEther, formatAddress } from "../../lib/blockchain";
import { useToast } from "../../hooks/use-toast";

interface LoanManagementDashboardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function LoanManagementDashboard({
  open,
  onOpenChange,
}: LoanManagementDashboardProps) {
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loadingLoans, setLoadingLoans] = useState(false);
  const [processingLoan, setProcessingLoan] = useState<number | null>(null);
  const [nextLoanId, setNextLoanId] = useState<number>(0);

  const {
    isConnected,
    account,
    getLoan,
    getNextLoanId,
    fundLoan,
    repayLoan,
    markDefault,
    connect,
    error: blockchainError,
  } = useBlockchain();

  const { toast } = useToast();

  // Load loans by iterating through loan IDs
  useEffect(() => {
    const loadLoans = async () => {
      if (isConnected && account) {
        setLoadingLoans(true);
        try {
          const nextId = await getNextLoanId();
          setNextLoanId(nextId);

          const allLoans: Loan[] = [];

          // Get all loans from 0 to nextLoanId-1
          for (let i = 0; i < nextId; i++) {
            try {
              const loan = await getLoan(i);
              if (
                loan &&
                (loan.borrower.toLowerCase() === account.toLowerCase() ||
                  loan.lender.toLowerCase() === account.toLowerCase())
              ) {
                allLoans.push(loan);
              }
            } catch (error) {
              console.warn(`Failed to load loan ${i}:`, error);
            }
          }

          setLoans(allLoans);
        } catch (error) {
          console.error("Failed to load loans:", error);
        } finally {
          setLoadingLoans(false);
        }
      }
    };

    loadLoans();
  }, [isConnected, account, getLoan, getNextLoanId]);

  const handleConnectWallet = async () => {
    const success = await connect();
    if (success) {
      toast({
        title: "Wallet Connected",
        description: "Successfully connected to your wallet",
      });
    }
  };

  const handleFundLoan = async (loanId: number) => {
    setProcessingLoan(loanId);
    try {
      const loan = await getLoan(loanId);
      if (!loan) throw new Error("Loan not found");

      const txHash = await fundLoan(
        loanId,
        formatEther(loan.amount.toString())
      );
      toast({
        title: "Loan Funded",
        description: `Loan ${loanId} has been funded. Transaction: ${txHash.slice(
          0,
          10
        )}...`,
      });

      // Refresh loans
      await refreshLoans();
    } catch (error: any) {
      toast({
        title: "Funding Failed",
        description: error.message || "Failed to fund loan",
        variant: "destructive",
      });
    } finally {
      setProcessingLoan(null);
    }
  };

  const handleRepayLoan = async (loanId: number) => {
    setProcessingLoan(loanId);
    try {
      const loan = await getLoan(loanId);
      if (!loan) throw new Error("Loan not found");

      // Calculate repayment amount (principal + interest)
      const principal = parseFloat(formatEther(loan.amount.toString()));
      const interestRate = Number(loan.interestRate);
      const repaymentAmount = principal + (principal * interestRate) / 100;

      const txHash = await repayLoan(loanId, repaymentAmount.toString());
      toast({
        title: "Loan Repaid",
        description: `Loan ${loanId} has been repaid. Transaction: ${txHash.slice(
          0,
          10
        )}...`,
      });

      // Refresh loans
      await refreshLoans();
    } catch (error: any) {
      toast({
        title: "Repayment Failed",
        description: error.message || "Failed to repay loan",
        variant: "destructive",
      });
    } finally {
      setProcessingLoan(null);
    }
  };

  const handleMarkDefault = async (loanId: number) => {
    setProcessingLoan(loanId);
    try {
      const txHash = await markDefault(loanId);
      toast({
        title: "Loan Marked as Default",
        description: `Loan ${loanId} has been marked as default. Transaction: ${txHash.slice(
          0,
          10
        )}...`,
      });

      // Refresh loans
      await refreshLoans();
    } catch (error: any) {
      toast({
        title: "Failed to Mark Default",
        description: error.message || "Failed to mark loan as default",
        variant: "destructive",
      });
    } finally {
      setProcessingLoan(null);
    }
  };

  const refreshLoans = async () => {
    if (isConnected && account) {
      try {
        const nextId = await getNextLoanId();
        const allLoans: Loan[] = [];

        for (let i = 0; i < nextId; i++) {
          try {
            const loan = await getLoan(i);
            if (
              loan &&
              (loan.borrower.toLowerCase() === account.toLowerCase() ||
                loan.lender.toLowerCase() === account.toLowerCase())
            ) {
              allLoans.push(loan);
            }
          } catch (error) {
            console.warn(`Failed to load loan ${i}:`, error);
          }
        }

        setLoans(allLoans);
      } catch (error) {
        console.error("Failed to refresh loans:", error);
      }
    }
  };

  const getLoanStatusBadge = (loan: Loan) => {
    if (loan.repaid) {
      return <Badge className="bg-green-500">Repaid</Badge>;
    }
    if (loan.defaulted) {
      return <Badge className="bg-red-500">Defaulted</Badge>;
    }
    if (loan.funded) {
      return <Badge className="bg-blue-500">Active</Badge>;
    }
    return <Badge variant="outline">Unfunded</Badge>;
  };

  const getLoanActions = (loan: Loan, loanId: number) => {
    const isOwner =
      account &&
      (loan.borrower.toLowerCase() === account.toLowerCase() ||
        loan.lender.toLowerCase() === account.toLowerCase());

    if (!isOwner) return null;

    // If loan is not funded and user is not the borrower, allow funding
    if (
      !loan.funded &&
      loan.borrower.toLowerCase() !== account!.toLowerCase()
    ) {
      return (
        <Button
          size="sm"
          onClick={() => handleFundLoan(loanId)}
          disabled={processingLoan === loanId}
        >
          {processingLoan === loanId ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Funding...
            </>
          ) : (
            "Fund Loan"
          )}
        </Button>
      );
    }

    // If loan is funded, not repaid, not defaulted, and user is borrower, allow repayment
    if (
      loan.funded &&
      !loan.repaid &&
      !loan.defaulted &&
      loan.borrower.toLowerCase() === account!.toLowerCase()
    ) {
      const now = Date.now() / 1000;
      const isOverdue = Number(loan.dueDate) > 0 && now > Number(loan.dueDate);

      return (
        <div className="flex gap-2">
          <Button
            size="sm"
            onClick={() => handleRepayLoan(loanId)}
            disabled={processingLoan === loanId}
            className={isOverdue ? "bg-orange-500 hover:bg-orange-600" : ""}
          >
            {processingLoan === loanId ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Repaying...
              </>
            ) : (
              `Repay ${isOverdue ? "(Overdue)" : ""}`
            )}
          </Button>
        </div>
      );
    }

    // If loan is overdue and user is lender, allow marking as default
    if (
      loan.funded &&
      !loan.repaid &&
      !loan.defaulted &&
      loan.lender.toLowerCase() === account!.toLowerCase()
    ) {
      const now = Date.now() / 1000;
      const isOverdue = Number(loan.dueDate) > 0 && now > Number(loan.dueDate);

      if (isOverdue) {
        return (
          <Button
            size="sm"
            variant="destructive"
            onClick={() => handleMarkDefault(loanId)}
            disabled={processingLoan === loanId}
          >
            {processingLoan === loanId ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Marking Default...
              </>
            ) : (
              "Mark Default"
            )}
          </Button>
        );
      }
    }

    return null;
  };

  const formatTimestamp = (timestamp: bigint): string => {
    const date = new Date(Number(timestamp) * 1000);
    return date.toLocaleDateString();
  };

  const getLoanStats = () => {
    const totalLoans = loans.length;
    const fundedLoans = loans.filter((loan) => loan.funded).length;
    const activeLoans = loans.filter(
      (loan) => loan.funded && !loan.repaid && !loan.defaulted
    ).length;
    const repaidLoans = loans.filter((loan) => loan.repaid).length;
    const defaultedLoans = loans.filter((loan) => loan.defaulted).length;
    const totalAmount = loans.reduce(
      (sum, loan) => sum + parseFloat(formatEther(loan.amount.toString())),
      0
    );

    return {
      totalLoans,
      fundedLoans,
      activeLoans,
      repaidLoans,
      defaultedLoans,
      totalAmount,
    };
  };

  if (!open) return null;

  const stats = getLoanStats();

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-6xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-6 w-6" />
                Loan Management Dashboard
              </CardTitle>
              <CardDescription>
                View and manage your loans and lending activities
              </CardDescription>
            </div>
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Wallet Connection Status */}
          {!isConnected ? (
            <Alert>
              <Wallet className="h-4 w-4" />
              <AlertDescription className="flex items-center justify-between">
                <span>Please connect your wallet to view loans</span>
                <Button onClick={handleConnectWallet} size="sm">
                  Connect Wallet
                </Button>
              </AlertDescription>
            </Alert>
          ) : (
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Wallet className="h-4 w-4" />
                <span>Connected: {formatAddress(account!)}</span>
              </div>
            </div>
          )}

          {/* Error Display */}
          {blockchainError && (
            <Alert variant="destructive">
              <AlertDescription>{blockchainError}</AlertDescription>
            </Alert>
          )}

          {/* Statistics Cards */}
          {isConnected && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Total Loans</p>
                      <p className="text-2xl font-bold">{stats.totalLoans}</p>
                    </div>
                    <DollarSign className="h-8 w-8 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Funded</p>
                      <p className="text-2xl font-bold">{stats.fundedLoans}</p>
                    </div>
                    <CheckCircle className="h-8 w-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Active</p>
                      <p className="text-2xl font-bold">{stats.activeLoans}</p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Repaid</p>
                      <p className="text-2xl font-bold">{stats.repaidLoans}</p>
                    </div>
                    <CheckCircle className="h-8 w-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Defaulted</p>
                      <p className="text-2xl font-bold">
                        {stats.defaultedLoans}
                      </p>
                    </div>
                    <XCircle className="h-8 w-8 text-red-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Total Value</p>
                      <p className="text-2xl font-bold">
                        {stats.totalAmount.toFixed(2)} ETH
                      </p>
                    </div>
                    <DollarSign className="h-8 w-8 text-purple-500" />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Loans List */}
          {isConnected && (
            <Tabs defaultValue="all" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="all">All Loans</TabsTrigger>
                <TabsTrigger value="unfunded">Unfunded</TabsTrigger>
                <TabsTrigger value="active">Active</TabsTrigger>
                <TabsTrigger value="completed">Completed</TabsTrigger>
              </TabsList>

              <TabsContent value="all" className="space-y-4">
                {loadingLoans ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin" />
                    <span className="ml-2">Loading loans...</span>
                  </div>
                ) : loans.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No loans found. Create a loan request to get started.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {loans.map((loan, index) => (
                      <Card key={index}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="space-y-2">
                              <div className="flex items-center gap-3">
                                <h3 className="font-semibold">Loan #{index}</h3>
                                {getLoanStatusBadge(loan)}
                              </div>
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                                <div className="flex items-center gap-2">
                                  <DollarSign className="h-4 w-4" />
                                  <span>
                                    {formatEther(loan.amount.toString())} ETH
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <TrendingUp className="h-4 w-4" />
                                  <span>
                                    Interest: {loan.interestRate.toString()}%
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Calendar className="h-4 w-4" />
                                  <span>{formatTimestamp(loan.createdAt)}</span>
                                </div>
                              </div>
                              <div className="text-sm text-muted-foreground">
                                <p>
                                  Duration:{" "}
                                  {Math.floor(Number(loan.duration) / 86400)}{" "}
                                  days
                                </p>
                                <p>Borrower: {formatAddress(loan.borrower)}</p>
                                {loan.lender !==
                                  "0x0000000000000000000000000000000000000000" && (
                                  <p>Lender: {formatAddress(loan.lender)}</p>
                                )}
                                {loan.funded && Number(loan.dueDate) > 0 && (
                                  <p>
                                    Due Date: {formatTimestamp(loan.dueDate)}
                                  </p>
                                )}
                              </div>
                            </div>
                            <div className="flex flex-col gap-2">
                              {getLoanActions(loan, index)}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="unfunded">
                <div className="space-y-4">
                  {loans
                    .filter((loan) => !loan.funded)
                    .map((loan, index) => (
                      <Card key={index}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="space-y-2">
                              <div className="flex items-center gap-3">
                                <h3 className="font-semibold">Loan #{index}</h3>
                                <Badge variant="outline">
                                  Awaiting Funding
                                </Badge>
                              </div>
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                                <div className="flex items-center gap-2">
                                  <DollarSign className="h-4 w-4" />
                                  <span>
                                    {formatEther(loan.amount.toString())} ETH
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <TrendingUp className="h-4 w-4" />
                                  <span>
                                    Interest: {loan.interestRate.toString()}%
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Calendar className="h-4 w-4" />
                                  <span>{formatTimestamp(loan.createdAt)}</span>
                                </div>
                              </div>
                            </div>
                            <div className="flex flex-col gap-2">
                              {getLoanActions(loan, index)}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                </div>
              </TabsContent>

              <TabsContent value="active">
                <div className="space-y-4">
                  {loans
                    .filter(
                      (loan) => loan.funded && !loan.repaid && !loan.defaulted
                    )
                    .map((loan, index) => (
                      <Card key={index}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="space-y-2">
                              <div className="flex items-center gap-3">
                                <h3 className="font-semibold">Loan #{index}</h3>
                                <Badge className="bg-blue-500">Active</Badge>
                              </div>
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                                <div className="flex items-center gap-2">
                                  <DollarSign className="h-4 w-4" />
                                  <span>
                                    {formatEther(loan.amount.toString())} ETH
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <TrendingUp className="h-4 w-4" />
                                  <span>
                                    Interest: {loan.interestRate.toString()}%
                                  </span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Calendar className="h-4 w-4" />
                                  <span>
                                    Due: {formatTimestamp(loan.dueDate)}
                                  </span>
                                </div>
                              </div>
                            </div>
                            <div className="flex flex-col gap-2">
                              {getLoanActions(loan, index)}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                </div>
              </TabsContent>

              <TabsContent value="completed">
                <div className="space-y-4">
                  {loans
                    .filter((loan) => loan.repaid || loan.defaulted)
                    .map((loan, index) => (
                      <Card key={index}>
                        <CardContent className="p-6">
                          <div className="space-y-2">
                            <div className="flex items-center gap-3">
                              <h3 className="font-semibold">Loan #{index}</h3>
                              {loan.repaid ? (
                                <Badge className="bg-green-500">Repaid</Badge>
                              ) : (
                                <Badge className="bg-red-500">Defaulted</Badge>
                              )}
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                              <div className="flex items-center gap-2">
                                <DollarSign className="h-4 w-4" />
                                <span>
                                  {formatEther(loan.amount.toString())} ETH
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <TrendingUp className="h-4 w-4" />
                                <span>
                                  Interest: {loan.interestRate.toString()}%
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Calendar className="h-4 w-4" />
                                <span>{formatTimestamp(loan.createdAt)}</span>
                              </div>
                            </div>
                            {loan.repaid && (
                              <Alert>
                                <CheckCircle className="h-4 w-4" />
                                <AlertDescription>
                                  This loan has been successfully repaid.
                                </AlertDescription>
                              </Alert>
                            )}
                            {loan.defaulted && (
                              <Alert variant="destructive">
                                <XCircle className="h-4 w-4" />
                                <AlertDescription>
                                  This loan has been marked as defaulted.
                                </AlertDescription>
                              </Alert>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                </div>
              </TabsContent>
            </Tabs>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
