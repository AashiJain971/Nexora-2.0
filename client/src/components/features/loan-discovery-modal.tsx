import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Star, Clock, Shield, CheckCircle, Loader2 } from 'lucide-react';
import { useDummyData } from '@/hooks/use-dummy-data';
import { useToast } from '@/hooks/use-toast';

interface LoanDiscoveryModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function LoanDiscoveryModal({ open, onOpenChange }: LoanDiscoveryModalProps) {
  const [filters, setFilters] = useState({
    amount: 'all',
    tenure: 'all',
    interestRate: 'all',
    lender: 'all',
  });
  const [applyingLoan, setApplyingLoan] = useState<string | null>(null);
  
  const { loans, simulateLoanApplication } = useDummyData();
  const { toast } = useToast();

  const applyForLoan = async (loanId: string) => {
    setApplyingLoan(loanId);
    try {
      const result = await simulateLoanApplication(loanId);
      if (result.success) {
        toast({
          title: "Application Submitted!",
          description: `Your loan application ${result.applicationId} has been submitted successfully.`,
        });
      }
    } catch (error) {
      toast({
        title: "Application Failed",
        description: "Failed to submit loan application. Please try again.",
        variant: "destructive",
      });
    } finally {
      setApplyingLoan(null);
    }
  };

  const formatCurrency = (amount: string) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(parseInt(amount));
  };

  const getMatchPercentage = (loan: any) => {
    // Simple matching logic based on loan features
    let score = 70;
    if (parseFloat(loan.interestRate) < 8) score += 15;
    if (loan.rating > 4.5) score += 10;
    if (loan.features.includes("No Collateral")) score += 5;
    return Math.min(score, 100);
  };

  const getMatchColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-green-accent/20 text-green-accent';
    if (percentage >= 80) return 'bg-orange-accent/20 text-orange-accent';
    return 'bg-muted text-muted-foreground';
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Loan Discovery & Matching</DialogTitle>
        </DialogHeader>
        
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Filters */}
          <div className="lg:col-span-1">
            <Card className="p-6 sticky top-0">
              <h3 className="text-lg font-semibold mb-4">Filter Options</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Loan Amount</label>
                  <Select value={filters.amount} onValueChange={(value) => setFilters(prev => ({ ...prev, amount: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any Amount</SelectItem>
                      <SelectItem value="5k-25k">₹5K - ₹25K</SelectItem>
                      <SelectItem value="25k-100k">₹25K - ₹1L</SelectItem>
                      <SelectItem value="100k-500k">₹1L - ₹5L</SelectItem>
                      <SelectItem value="500k+">₹5L+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Interest Rate</label>
                  <Select value={filters.interestRate} onValueChange={(value) => setFilters(prev => ({ ...prev, interestRate: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any Rate</SelectItem>
                      <SelectItem value="0-5">0% - 5%</SelectItem>
                      <SelectItem value="5-10">5% - 10%</SelectItem>
                      <SelectItem value="10-15">10% - 15%</SelectItem>
                      <SelectItem value="15+">15%+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Term Length</label>
                  <Select value={filters.tenure} onValueChange={(value) => setFilters(prev => ({ ...prev, tenure: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any Term</SelectItem>
                      <SelectItem value="6months">6 months</SelectItem>
                      <SelectItem value="1year">1 year</SelectItem>
                      <SelectItem value="2-3years">2-3 years</SelectItem>
                      <SelectItem value="5+years">5+ years</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Loan Type</label>
                  <Select value={filters.lender} onValueChange={(value) => setFilters(prev => ({ ...prev, lender: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      <SelectItem value="working-capital">Working Capital</SelectItem>
                      <SelectItem value="equipment">Equipment</SelectItem>
                      <SelectItem value="invoice">Invoice Financing</SelectItem>
                      <SelectItem value="expansion">Business Expansion</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <Button className="w-full bg-teal-accent hover:bg-teal-accent/90">
                  Apply Filters
                </Button>
              </div>
            </Card>
          </div>
          
          {/* Loan Options */}
          <div className="lg:col-span-3">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold">Available Loans ({loans.length} matches)</h3>
              <Select defaultValue="best-match">
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="best-match">Best Match</SelectItem>
                  <SelectItem value="lowest-rate">Lowest Rate</SelectItem>
                  <SelectItem value="highest-amount">Highest Amount</SelectItem>
                  <SelectItem value="fastest-approval">Fastest Approval</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-6">
              {loans.map((loan) => {
                const matchPercentage = getMatchPercentage(loan);
                const matchColor = getMatchColor(matchPercentage);
                
                return (
                  <Card key={loan.id} className="p-6 hover:border-teal-accent/50 transition-colors">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-teal-accent rounded-lg flex items-center justify-center">
                          <Shield className="w-6 h-6 text-background" />
                        </div>
                        <div>
                          <h4 className="text-lg font-semibold">{loan.lenderName}</h4>
                          <div className="flex items-center space-x-2">
                            <div className="flex text-yellow-400">
                              {Array.from({ length: 5 }).map((_, i) => (
                                <Star
                                  key={i}
                                  className={`w-4 h-4 ${
                                    i < Math.floor(loan.rating) ? 'fill-current' : ''
                                  }`}
                                />
                              ))}
                            </div>
                            <span className="text-sm text-muted-foreground">
                              {loan.rating}/5 ({loan.reviews} reviews)
                            </span>
                          </div>
                        </div>
                      </div>
                      <Badge className={matchColor}>
                        {matchPercentage}% Match
                      </Badge>
                    </div>
                    
                    <div className="grid md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <div className="text-sm text-muted-foreground">Loan Amount</div>
                        <div className="text-lg font-semibold text-teal-accent">
                          {formatCurrency(loan.amount)}
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Interest Rate</div>
                        <div className="text-lg font-semibold text-orange-accent">
                          {loan.interestRate}% APR
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Term</div>
                        <div className="text-lg font-semibold">{loan.tenure} months</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Approval Time</div>
                        <div className="text-lg font-semibold text-green-accent">
                          {loan.approvalTime}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-sm">
                        {loan.features.map((feature: string) => (
                          <span key={feature} className="flex items-center">
                            <CheckCircle className="w-4 h-4 text-green-accent mr-1" />
                            {feature}
                          </span>
                        ))}
                      </div>
                      <div className="flex space-x-2">
                        <Button variant="outline" className="border-teal-accent text-teal-accent hover:bg-teal-accent hover:text-background">
                          View Details
                        </Button>
                        <Button
                          onClick={() => applyForLoan(loan.id)}
                          disabled={applyingLoan === loan.id}
                          className="bg-gradient-to-r from-teal-accent to-green-accent"
                        >
                          {applyingLoan === loan.id ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Applying...
                            </>
                          ) : (
                            "Apply Now"
                          )}
                        </Button>
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
