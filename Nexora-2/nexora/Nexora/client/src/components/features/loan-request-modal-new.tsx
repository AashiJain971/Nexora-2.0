import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Alert, AlertDescription } from "../ui/alert";
import { Badge } from "../ui/badge";
import {
  Loader2,
  Wallet,
  TrendingUp,
  DollarSign,
  Building2,
} from "lucide-react";
import { useBlockchain } from "../../hooks/use-blockchain";
import { formatEther } from "../../lib/blockchain";
import { useCreditScore } from "../../hooks/use-credit-score";
import { useToast } from "../../hooks/use-toast";

const loanRequestSchema = z.object({
  amount: z
    .string()
    .min(1, "Amount is required")
    .refine((val) => {
      const num = parseFloat(val);
      return num > 0 && num <= 1000; // Max 1000 ETH for safety
    }, "Amount must be between 0 and 1000 ETH"),
  interestRate: z
    .string()
    .min(1, "Interest rate is required")
    .refine((val) => {
      const num = parseFloat(val);
      return num > 0 && num <= 100; // Max 100% APR
    }, "Interest rate must be between 0 and 100%"),
  duration: z
    .string()
    .min(1, "Duration is required")
    .refine((val) => {
      const num = parseInt(val);
      return num > 0 && num <= 365; // Max 1 year
    }, "Duration must be between 1 and 365 days"),
});

type LoanRequestForm = z.infer<typeof loanRequestSchema>;

interface LoanRequestModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function LoanRequestModal({
  open,
  onOpenChange,
}: LoanRequestModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    isConnected,
    account,
    balance,
    createLoan,
    connect,
    loading,
    error: blockchainError,
  } = useBlockchain();

  const { creditScore, loading: creditLoading } = useCreditScore();
  const { toast } = useToast();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<LoanRequestForm>({
    resolver: zodResolver(loanRequestSchema),
    defaultValues: {
      amount: "",
      interestRate: "",
      duration: "",
    },
  });

  const watchedAmount = watch("amount");
  const watchedInterestRate = watch("interestRate");
  const watchedDuration = watch("duration");

  // Calculate estimated repayment amount
  const calculateRepaymentAmount = (
    amount: string,
    interestRate: string,
    duration: string
  ): string => {
    const principal = parseFloat(amount || "0");
    const rate = parseFloat(interestRate || "0") / 100;
    const days = parseInt(duration || "0");

    if (principal && rate && days) {
      const interest = principal * rate * (days / 365);
      return (principal + interest).toFixed(4);
    }
    return "0";
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

  const getRecommendedInterestRate = (score: number): string => {
    if (score >= 800) return "5-8%";
    if (score >= 750) return "8-12%";
    if (score >= 700) return "12-16%";
    if (score >= 650) return "16-20%";
    return "20%+";
  };

  const onSubmit = async (data: LoanRequestForm) => {
    if (!isConnected) {
      toast({
        title: "Wallet Not Connected",
        description: "Please connect your wallet first",
        variant: "destructive",
      });
      return;
    }

    if (creditScore < 600) {
      toast({
        title: "Credit Score Too Low",
        description: "Your credit score must be at least 600 to request a loan",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      const txHash = await createLoan(
        data.amount,
        parseFloat(data.interestRate),
        parseInt(data.duration)
      );

      toast({
        title: "Loan Request Created",
        description: `Transaction hash: ${txHash.slice(0, 10)}...`,
      });

      // Reset form and close modal
      reset();
      onOpenChange(false);
    } catch (error: any) {
      console.error("Loan request failed:", error);
      toast({
        title: "Loan Request Failed",
        description: error.message || "Failed to create loan request",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConnectWallet = async () => {
    const success = await connect();
    if (success) {
      toast({
        title: "Wallet Connected",
        description: "Successfully connected to your wallet",
      });
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-6 w-6" />
            Create Loan Request
          </CardTitle>
          <CardDescription>
            Create a new loan request for lenders to fund
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Wallet Connection Status */}
          {!isConnected ? (
            <Alert>
              <Wallet className="h-4 w-4" />
              <AlertDescription className="flex items-center justify-between">
                <span>Please connect your wallet to continue</span>
                <Button onClick={handleConnectWallet} size="sm">
                  Connect Wallet
                </Button>
              </AlertDescription>
            </Alert>
          ) : (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Wallet className="h-4 w-4" />
              <span>
                Connected: {account?.slice(0, 6)}...{account?.slice(-4)}
              </span>
            </div>
          )}

          {/* Credit Score and Wallet Balance Display */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">Credit Score</p>
                    {creditLoading ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-sm">Loading...</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <p className="text-2xl font-bold">{creditScore}</p>
                        <Badge className={getCreditScoreColor(creditScore)}>
                          {getCreditScoreLabel(creditScore)}
                        </Badge>
                      </div>
                    )}
                  </div>
                  <TrendingUp className="h-8 w-8 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">Wallet Balance</p>
                    <p className="text-2xl font-bold">
                      {formatEther(balance)} ETH
                    </p>
                  </div>
                  <Building2 className="h-8 w-8 text-muted-foreground" />
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

          {/* Loan Request Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="amount">Loan Amount (ETH)</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.001"
                  {...register("amount")}
                  placeholder="e.g., 10"
                />
                {errors.amount && (
                  <p className="text-sm text-red-500">
                    {errors.amount.message}
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="interestRate">Interest Rate (% APR)</Label>
                <Input
                  id="interestRate"
                  type="number"
                  step="0.1"
                  {...register("interestRate")}
                  placeholder="e.g., 12"
                />
                {errors.interestRate && (
                  <p className="text-sm text-red-500">
                    {errors.interestRate.message}
                  </p>
                )}
                {creditScore > 0 && (
                  <p className="text-sm text-muted-foreground">
                    Recommended for your credit score:{" "}
                    {getRecommendedInterestRate(creditScore)}
                  </p>
                )}
              </div>
            </div>

            <div>
              <Label htmlFor="duration">Loan Duration (days)</Label>
              <Input
                id="duration"
                type="number"
                {...register("duration")}
                placeholder="e.g., 30"
              />
              {errors.duration && (
                <p className="text-sm text-red-500">
                  {errors.duration.message}
                </p>
              )}
            </div>

            {/* Loan Summary */}
            {watchedAmount && watchedInterestRate && watchedDuration && (
              <Alert>
                <TrendingUp className="h-4 w-4" />
                <AlertDescription>
                  <div className="space-y-1">
                    <p className="font-medium">Loan Summary:</p>
                    <p>Principal Amount: {watchedAmount} ETH</p>
                    <p>Interest Rate: {watchedInterestRate}% APR</p>
                    <p>Duration: {watchedDuration} days</p>
                    <p className="font-medium">
                      Total Repayment:{" "}
                      {calculateRepaymentAmount(
                        watchedAmount,
                        watchedInterestRate,
                        watchedDuration
                      )}{" "}
                      ETH
                    </p>
                  </div>
                </AlertDescription>
              </Alert>
            )}

            {/* Credit Score Warning */}
            {creditScore < 600 && creditScore > 0 && (
              <Alert variant="destructive">
                <AlertDescription>
                  Your credit score of {creditScore} is below the minimum
                  requirement of 600. Please improve your credit score by
                  uploading more invoices.
                </AlertDescription>
              </Alert>
            )}

            {/* Action Buttons */}
            <div className="flex justify-end gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={
                  !isConnected ||
                  isSubmitting ||
                  loading ||
                  creditScore < 600 ||
                  creditLoading
                }
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  "Create Loan Request"
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
