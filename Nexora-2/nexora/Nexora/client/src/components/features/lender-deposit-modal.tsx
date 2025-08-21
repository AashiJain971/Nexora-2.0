import React from "react";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Alert, AlertDescription } from "../ui/alert";
import { Wallet, Info, TrendingUp, DollarSign } from "lucide-react";
import { useBlockchain } from "../../hooks/use-blockchain";
import { formatEther } from "../../lib/blockchain";

interface LenderDepositModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function LenderDepositModal({
  open,
  onOpenChange,
}: LenderDepositModalProps) {
  const { isConnected, account, balance, connect, loading } = useBlockchain();

  const handleConnectWallet = async () => {
    await connect();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-6 w-6" />
            Lender Information
          </CardTitle>
          <CardDescription>
            How lending works in the new escrow system
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
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Wallet className="h-4 w-4" />
                <span>
                  Connected: {account?.slice(0, 6)}...{account?.slice(-4)}
                </span>
              </div>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Wallet Balance</p>
                      <p className="text-2xl font-bold">
                        {formatEther(balance)} ETH
                      </p>
                    </div>
                    <TrendingUp className="h-8 w-8 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Information about the new lending process */}
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <p className="font-medium">How Lending Works:</p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Browse available loan requests in the dashboard</li>
                  <li>Select a loan request you want to fund</li>
                  <li>Click "Fund Loan" to provide the requested amount</li>
                  <li>Your ETH will be held in escrow until loan is repaid</li>
                  <li>Earn interest when the borrower repays the loan</li>
                </ul>
              </div>
            </AlertDescription>
          </Alert>

          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <p className="font-medium">Benefits of the New System:</p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>No need to pre-deposit funds to an escrow pool</li>
                  <li>Fund specific loans that meet your criteria</li>
                  <li>Better control over your lending portfolio</li>
                  <li>Direct relationship with borrowers</li>
                </ul>
              </div>
            </AlertDescription>
          </Alert>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Close
            </Button>
            <Button onClick={() => onOpenChange(false)} disabled={!isConnected}>
              View Loan Requests
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
