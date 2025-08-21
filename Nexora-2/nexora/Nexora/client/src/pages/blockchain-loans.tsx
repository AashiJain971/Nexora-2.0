import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Alert, AlertDescription } from "../components/ui/alert";
import {
  DollarSign,
  TrendingUp,
  Wallet,
  Building2,
  PiggyBank,
  CreditCard,
  Shield,
  Zap,
  Users,
  CheckCircle,
  ArrowRight,
  Info,
} from "lucide-react";
import { useBlockchain } from "../hooks/use-blockchain";
import { useCreditScore } from "../hooks/use-credit-score";
import { formatEther } from "../lib/blockchain";
import { LoanRequestModal } from "../components/features/loan-request-modal-new";
import { LenderDepositModal } from "../components/features/lender-deposit-modal";
import { LoanManagementDashboard } from "../components/features/loan-management-dashboard";

export default function BlockchainLoansPage() {
  const [loanRequestOpen, setLoanRequestOpen] = useState(false);
  const [depositModalOpen, setDepositModalOpen] = useState(false);
  const [dashboardOpen, setDashboardOpen] = useState(false);
  const {
    isConnected,
    account,
    balance,
    connect,
    connecting,
    error: blockchainError,
  } = useBlockchain();

  const { creditScore, loading: creditLoading } = useCreditScore();

  // Calculate estimated max loan amount based on credit score
  const getEstimatedMaxLoan = (score: number): number => {
    if (score >= 800) return 100; // 100 ETH for excellent credit
    if (score >= 750) return 75; // 75 ETH for very good credit
    if (score >= 700) return 50; // 50 ETH for good credit
    if (score >= 650) return 25; // 25 ETH for fair credit
    return 10; // 10 ETH for poor credit (if >= 600)
  };

  const getCreditScoreColor = (score: number): string => {
    if (score >= 800) return "bg-green-500";
    if (score >= 750) return "bg-blue-500";
    if (score >= 700) return "bg-yellow-500";
    if (score >= 650) return "bg-orange-500";
    return "bg-red-500";
  };

  const getCreditScoreLabel = (score: number): string => {
    if (score >= 800) return "Excellent";
    if (score >= 750) return "Very Good";
    if (score >= 700) return "Good";
    if (score >= 650) return "Fair";
    return "Poor";
  };

  const features = [
    {
      icon: Shield,
      title: "Secure Escrow",
      description:
        "Smart contract-based escrow ensures transparent and secure individual loan management",
    },
    {
      icon: Zap,
      title: "Direct Funding",
      description:
        "Lenders fund specific loans directly, creating direct borrower-lender relationships",
    },
    {
      icon: TrendingUp,
      title: "Credit-Based Terms",
      description:
        "Loan terms and availability determined by credit score and business performance",
    },
    {
      icon: Users,
      title: "Decentralized P2P",
      description:
        "Peer-to-peer lending without traditional banking intermediaries",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Blockchain Loan Platform
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Decentralized lending platform powered by smart contracts. Borrow
            funds based on your credit score or lend to earn returns.
          </p>
        </div>

        {/* Connection Status */}
        {!isConnected ? (
          <Card className="mb-8">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Wallet className="h-8 w-8 text-blue-500" />
                  <div>
                    <h3 className="text-lg font-semibold">
                      Connect Your Wallet
                    </h3>
                    <p className="text-muted-foreground">
                      Connect your Web3 wallet to access blockchain lending
                      features
                    </p>
                  </div>
                </div>
                <Button onClick={connect} disabled={connecting} size="lg">
                  {connecting ? "Connecting..." : "Connect Wallet"}
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          /* Connected Dashboard */
          <div className="space-y-8">
            {/* User Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">
                        Your Balance
                      </p>
                      <p className="text-2xl font-bold">
                        {formatEther(balance)} ETH
                      </p>
                    </div>
                    <Wallet className="h-8 w-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">
                        Credit Score
                      </p>
                      {creditLoading ? (
                        <p className="text-2xl font-bold">Loading...</p>
                      ) : (
                        <div className="flex items-center gap-2">
                          <p className="text-2xl font-bold">{creditScore}</p>
                          {creditScore > 0 && (
                            <Badge className={getCreditScoreColor(creditScore)}>
                              {getCreditScoreLabel(creditScore)}
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                    <TrendingUp className="h-8 w-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">
                        Est. Max Loan
                      </p>
                      <p className="text-2xl font-bold">
                        {creditScore >= 600
                          ? getEstimatedMaxLoan(creditScore)
                          : 0}{" "}
                        ETH
                      </p>
                    </div>
                    <DollarSign className="h-8 w-8 text-purple-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Error Display */}
            {blockchainError && (
              <Alert variant="destructive">
                <AlertDescription>{blockchainError}</AlertDescription>
              </Alert>
            )}

            {/* Action Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Borrower Section */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CreditCard className="h-6 w-6" />
                    Borrow Funds
                  </CardTitle>
                  <CardDescription>
                    Request a loan based on your credit score and business
                    information
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Your Credit Score:</span>
                      <span className="font-medium">
                        {creditScore || "Not available"}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Est. Max Loan Amount:</span>
                      <span className="font-medium">
                        {creditScore >= 600
                          ? getEstimatedMaxLoan(creditScore)
                          : 0}{" "}
                        ETH
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Minimum Credit Score:</span>
                      <span className="font-medium">600</span>
                    </div>
                  </div>

                  {creditScore >= 600 ? (
                    <Alert>
                      <CheckCircle className="h-4 w-4" />
                      <AlertDescription>
                        ✅ You qualify for loans! Your credit score meets the
                        minimum requirement.
                      </AlertDescription>
                    </Alert>
                  ) : creditScore > 0 ? (
                    <Alert variant="destructive">
                      <AlertDescription>
                        ❌ Credit score too low. Upload more invoices to improve
                        your score.
                      </AlertDescription>
                    </Alert>
                  ) : (
                    <Alert>
                      <Info className="h-4 w-4" />
                      <AlertDescription>
                        Upload invoices first to calculate your credit score.
                      </AlertDescription>
                    </Alert>
                  )}

                  <Button
                    className="w-full"
                    onClick={() => setLoanRequestOpen(true)}
                    disabled={creditScore < 600 || creditLoading}
                  >
                    Request Loan
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>

              {/* Lender Section */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <PiggyBank className="h-6 w-6" />
                    Lend & Earn
                  </CardTitle>
                  <CardDescription>
                    Fund specific loan requests and earn returns from borrower
                    repayments
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Your Balance:</span>
                      <span className="font-medium">
                        {formatEther(balance)} ETH
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Lending Model:</span>
                      <span className="font-medium">Direct Loan Funding</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Minimum to Lend:</span>
                      <span className="font-medium">Variable by loan</span>
                    </div>
                  </div>

                  <Alert>
                    <TrendingUp className="h-4 w-4" />
                    <AlertDescription>
                      💰 Fund specific loans and earn interest when borrowers
                      repay on time.
                    </AlertDescription>
                  </Alert>

                  <Button
                    className="w-full"
                    variant="outline"
                    onClick={() => setDepositModalOpen(true)}
                    disabled={parseFloat(balance) <= 0.01}
                  >
                    Learn About Lending
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Management Section */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-6 w-6" />
                  Loan Management
                </CardTitle>
                <CardDescription>
                  View and manage your loan requests and funding activities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={() => setDashboardOpen(true)}
                  className="w-full md:w-auto"
                >
                  Open Dashboard
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Features Section */}
        <div className="mt-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">
            Platform Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card key={index}>
                <CardContent className="p-6 text-center">
                  <feature.icon className="h-12 w-12 mx-auto mb-4 text-blue-500" />
                  <h3 className="text-lg font-semibold mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground text-sm">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* How It Works */}
        <div className="mt-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">
            How It Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 dark:bg-blue-900 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600 dark:text-blue-300">
                  1
                </span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Upload Invoices</h3>
              <p className="text-muted-foreground">
                Upload your business invoices to calculate your credit score
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 dark:bg-green-900 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-green-600 dark:text-green-300">
                  2
                </span>
              </div>
              <h3 className="text-xl font-semibold mb-2">
                Create Loan Request
              </h3>
              <p className="text-muted-foreground">
                Submit a detailed loan request with amount, interest rate, and
                duration
              </p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 dark:bg-purple-900 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-purple-600 dark:text-purple-300">
                  3
                </span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Get Funded</h3>
              <p className="text-muted-foreground">
                Lenders review and fund your loan request directly through the
                platform
              </p>
            </div>
          </div>
        </div>

        {/* Risk Warning */}
        <div className="mt-16">
          <Alert>
            <Shield className="h-4 w-4" />
            <AlertDescription>
              <strong>Risk Warning:</strong> This is experimental DeFi software.
              Only invest what you can afford to lose. Smart contracts carry
              inherent risks. Please understand the technology before
              participating.
            </AlertDescription>
          </Alert>
        </div>
      </div>

      {/* Modals */}
      <LoanRequestModal
        open={loanRequestOpen}
        onOpenChange={setLoanRequestOpen}
      />
      <LenderDepositModal
        open={depositModalOpen}
        onOpenChange={setDepositModalOpen}
      />
      <LoanManagementDashboard
        open={dashboardOpen}
        onOpenChange={setDashboardOpen}
      />
    </div>
  );
}
