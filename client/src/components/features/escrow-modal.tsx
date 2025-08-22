import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Shield, CheckCircle, Clock, ExternalLink, Loader2 } from 'lucide-react';
import { useDummyData } from '@/hooks/use-dummy-data';
import { useToast } from '@/hooks/use-toast';

interface EscrowModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EscrowModal({ open, onOpenChange }: EscrowModalProps) {
  const [requestingRelease, setRequestingRelease] = useState<number | null>(null);
  const { escrowMilestones, simulateMilestoneRelease } = useDummyData();
  const { toast } = useToast();

  const requestMilestoneRelease = async (milestoneId: number) => {
    setRequestingRelease(milestoneId);
    try {
      const result = await simulateMilestoneRelease(milestoneId);
      if (result.success) {
        toast({
          title: "Release Requested!",
          description: `Milestone ${milestoneId} release request submitted. Transaction: ${result.transactionHash.slice(0, 10)}...`,
        });
      }
    } catch (error) {
      toast({
        title: "Request Failed",
        description: "Failed to submit release request. Please try again.",
        variant: "destructive",
      });
    } finally {
      setRequestingRelease(null);
    }
  };

  const formatCurrency = (amount: string) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(parseInt(amount));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-accent/20 text-green-accent border-green-accent';
      case 'in-progress':
        return 'bg-orange-accent/20 text-orange-accent border-orange-accent';
      case 'pending':
        return 'bg-muted text-muted-foreground border-border';
      default:
        return 'bg-muted text-muted-foreground border-border';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-accent" />;
      case 'in-progress':
        return <Clock className="w-5 h-5 text-orange-accent" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-muted-foreground" />;
      default:
        return <Clock className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const completedMilestones = escrowMilestones.filter(m => m.status === 'completed').length;
  const totalProgress = (completedMilestones / escrowMilestones.length) * 100;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Smart Contract Escrow</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Contract Overview */}
          <Card className="p-6 bg-gradient-to-r from-teal-accent/10 to-green-accent/10 border-teal-accent/20">
            <div className="flex items-center space-x-3 mb-4">
              <Shield className="w-6 h-6 text-teal-accent" />
              <h3 className="text-lg font-semibold">Active Loan Contract</h3>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <div className="text-sm text-muted-foreground">Contract ID</div>
                <div className="font-semibold">SC-2024-001</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Total Value</div>
                <div className="font-semibold text-green-accent">₹3,50,000</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Parties</div>
                <div className="font-semibold">Lender & Borrower</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Status</div>
                <Badge className="bg-green-accent/20 text-green-accent">Active</Badge>
              </div>
            </div>

            <div className="mb-2">
              <div className="flex justify-between text-sm mb-1">
                <span>Overall Progress</span>
                <span>{completedMilestones}/{escrowMilestones.length} milestones</span>
              </div>
              <Progress value={totalProgress} className="w-full" />
            </div>
          </Card>

          {/* Milestone Progress */}
          <div>
            <h3 className="text-xl font-semibold mb-4">Milestone Progress</h3>
            <div className="space-y-4">
              {escrowMilestones.map((milestone) => (
                <Card key={milestone.id} className={`p-4 border-l-4 ${
                  milestone.status === 'completed' ? 'border-green-accent' :
                  milestone.status === 'in-progress' ? 'border-orange-accent' :
                  'border-border'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(milestone.status)}
                      <h4 className="font-semibold">
                        {milestone.id}. {milestone.title}
                      </h4>
                    </div>
                    <Badge className={getStatusColor(milestone.status)}>
                      {milestone.status === 'completed' ? 'Completed' :
                       milestone.status === 'in-progress' ? 'In Progress' :
                       'Pending'}
                    </Badge>
                  </div>
                  
                  <p className="text-sm text-muted-foreground mb-3">
                    {milestone.description}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <span className="text-sm">
                        Amount: <span className="font-semibold">{formatCurrency(milestone.amount)}</span>
                      </span>
                      <span className="text-sm">
                        ({milestone.percentage}% of total)
                      </span>
                      {milestone.completedDate && (
                        <span className="text-sm text-muted-foreground">
                          Completed: {milestone.completedDate}
                        </span>
                      )}
                    </div>
                    
                    {milestone.status === 'completed' ? (
                      <span className="text-sm text-green-accent font-semibold">
                        ✓ Funds Released
                      </span>
                    ) : milestone.status === 'in-progress' ? (
                      <Button
                        onClick={() => requestMilestoneRelease(milestone.id)}
                        disabled={requestingRelease === milestone.id}
                        className="bg-orange-accent hover:bg-orange-accent/90"
                      >
                        {requestingRelease === milestone.id ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Requesting...
                          </>
                        ) : (
                          "Request Release"
                        )}
                      </Button>
                    ) : (
                      <span className="text-sm text-muted-foreground">
                        Awaiting Previous Milestone
                      </span>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* Smart Contract Features */}
          <Card className="p-6">
            <h4 className="text-lg font-semibold mb-4">Smart Contract Features</h4>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Shield className="w-5 h-5 text-green-accent" />
                  <span>Automated milestone verification</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Shield className="w-5 h-5 text-green-accent" />
                  <span>Secure escrow management</span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Shield className="w-5 h-5 text-green-accent" />
                  <span>Real-time payment tracking</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Shield className="w-5 h-5 text-green-accent" />
                  <span>Dispute resolution protocol</span>
                </div>
              </div>
            </div>
          </Card>

          {/* Blockchain Transaction History */}
          <Card className="p-6">
            <h4 className="text-lg font-semibold mb-4">Blockchain Transaction History</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <span className="text-sm">Contract Created:</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-mono text-teal-accent">0x1234...5678</span>
                  <ExternalLink className="w-4 h-4 text-muted-foreground" />
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <span className="text-sm">Milestone 1 Release:</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-mono text-green-accent">0x9876...5432</span>
                  <ExternalLink className="w-4 h-4 text-muted-foreground" />
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <span className="text-sm">Gas Used:</span>
                <span className="text-sm">0.0024 ETH</span>
              </div>
            </div>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
}
