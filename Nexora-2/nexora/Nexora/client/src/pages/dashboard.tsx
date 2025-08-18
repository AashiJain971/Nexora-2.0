import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

import { LearningModal } from '@/components/features/learning-modal';
import { InvoiceUploadModal } from '@/components/features/invoice-upload-modal';
import { InvoiceManagementModal } from '@/components/features/invoice-management-modal';
import { LoanDiscoveryModal } from '@/components/features/loan-discovery-modal';
import { MarketplaceModal } from '@/components/features/marketplace-modal';
import { useCreditScore } from '@/hooks/use-credit-score';
import { useAIInsights } from '@/hooks/use-ai-insights';
import { 
  TrendingUp, 
  CreditCard, 
  BarChart3, 
  Medal,
  File,
  BadgeDollarSign,
  Store,
  GraduationCap,
  CheckCircle,
  Clock,
  FileText,
  Activity,
  AlertCircle,
  Lightbulb,
  Users,
  ChartLine,
  Loader2,
  Brain
} from 'lucide-react';
import { useDummyData } from '@/hooks/use-dummy-data';
import { Link } from 'wouter';

export default function Dashboard() {
  const [activeModal, setActiveModal] = useState<string | null>(null);
  const { 
    businessProfile, 
    loans, 
    learningProgress,
    orders,
    getRandomAIResponse 
  } = useDummyData();

  // Get real credit score data
  const { creditScore, category, lastUpdated, totalInvoices, loading: creditLoading, refreshCreditScore } = useCreditScore();
  
  // Get dynamic AI insights based on credit score
  const aiInsights = useAIInsights();

  const openModal = (modalName: string) => setActiveModal(modalName);
  const closeModal = () => setActiveModal(null);

  const formatCurrency = (amount: string | number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(typeof amount === 'string' ? parseInt(amount) : amount);
  };

  const activeLoan = loans.find(loan => loan.status === 'active');
  const loanProgress = activeLoan ? (parseInt(activeLoan.repaidAmount) / parseInt(activeLoan.disbursedAmount)) * 100 : 0;

  return (
    <div className="pt-16 min-h-screen bg-background">
      <div className="container mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Business Dashboard</h1>
            <p className="text-xl text-muted-foreground">Complete overview of your business operations</p>
          </div>
          <div className="flex space-x-4">
            <Link href="/profile">
              <Button variant="outline" className="border-teal-accent text-teal-accent hover:bg-teal-accent hover:text-background">
                View Profile
              </Button>
            </Link>
            <Button className="bg-gradient-to-r from-teal-accent to-green-accent">
              Export Report
            </Button>
            <Button 
              onClick={() => {
                console.log('🔘 MAIN Dashboard Invoice Management button clicked!');
                openModal('invoiceManagement');
              }}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg"
            >
              📋 View Invoice History
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Total Credibility Score</h3>
              {creditLoading ? (
                <Loader2 className="w-5 h-5 text-blue-accent animate-spin" />
              ) : (
                <TrendingUp className="w-5 h-5 text-green-accent" />
              )}
            </div>
            <div className="flex items-center gap-2 mb-2">
              <div className="text-3xl font-bold text-green-accent">{creditScore}</div>
              <Badge variant="outline" className="text-xs">
                {category}
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  console.log('🔄 Refreshing credit score...');
                  refreshCreditScore();
                }}
                className="h-6 w-6 p-0 ml-2"
                title="Refresh Credit Score"
              >
                <Activity className="w-3 h-3" />
              </Button>
            </div>
            <div className="text-sm text-muted-foreground">
              Based on {totalInvoices} invoice{totalInvoices !== 1 ? 's' : ''}
              {lastUpdated && ` • Updated: ${lastUpdated}`}
            </div>
            
            {/* Temporary debugging info - TODO: Remove in production */}
            <div className="mt-4 p-3 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-md text-xs">
              <div className="font-semibold mb-1 text-slate-800 dark:text-slate-200">🐛 Debug Info:</div>
              <div className="text-slate-700 dark:text-slate-300">Score: {creditScore} | Category: {category}</div>
              <div className="text-slate-700 dark:text-slate-300">Total Invoices: {totalInvoices} | Loading: {creditLoading ? 'Yes' : 'No'}</div>
              <div className="text-slate-700 dark:text-slate-300">Last Updated: {lastUpdated}</div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Active Loans</h3>
              <CreditCard className="w-5 h-5 text-teal-accent" />
            </div>
            <div className="text-3xl font-bold text-teal-accent mb-2">2</div>
            <div className="text-sm text-muted-foreground">₹75,000 total borrowed</div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Monthly Revenue</h3>
              <BarChart3 className="w-5 h-5 text-orange-accent" />
            </div>
            <div className="text-3xl font-bold text-orange-accent mb-2">₹42K</div>
            <div className="text-sm text-muted-foreground">+18% from last month</div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">MSME Badges</h3>
              <Medal className="w-5 h-5 text-green-accent" />
            </div>
            <div className="text-3xl font-bold text-green-accent mb-2">7</div>
            <div className="text-sm text-muted-foreground">2 badges earned this month</div>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Loan Portfolio */}
            <Card className="p-6">
              <h3 className="text-xl font-semibold mb-6">Loan Portfolio</h3>
              <div className="space-y-4">
                {loans.slice(0, 2).map((loan) => (
                  <Card key={loan.id} className="p-4 border border-border">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-semibold">Equipment Purchase Loan</h4>
                        <p className="text-sm text-muted-foreground">{loan.lenderName} • {loan.interestRate}% APR</p>
                      </div>
                      <Badge className={
                        loan.status === 'active' ? 'bg-green-accent/20 text-green-accent' :
                        loan.status === 'processing' ? 'bg-orange-accent/20 text-orange-accent' :
                        'bg-muted text-muted-foreground'
                      }>
                        {loan.status === 'active' ? 'Active' : 
                         loan.status === 'processing' ? 'Processing' : 'Available'}
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4 mb-3">
                      <div>
                        <div className="text-sm text-muted-foreground">
                          {loan.status === 'active' ? 'Borrowed' : 'Approved'}
                        </div>
                        <div className="font-semibold">{formatCurrency(loan.amount)}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">
                          {loan.status === 'active' ? 'Remaining' : 'Disbursement'}
                        </div>
                        <div className="font-semibold">
                          {loan.status === 'active' ? 
                            formatCurrency((parseInt(loan.amount) - parseInt(loan.repaidAmount)).toString()) :
                            'Pending'
                          }
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">
                          {loan.status === 'active' ? 'Next Payment' : 'Expected'}
                        </div>
                        <div className="font-semibold">
                          {loan.status === 'active' ? 'March 15' : 'March 20'}
                        </div>
                      </div>
                    </div>
                    
                    {loan.status === 'active' && (
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Repayment Progress</span>
                          <span>{Math.round(loanProgress)}%</span>
                        </div>
                        <Progress value={loanProgress} className="w-full" />
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            </Card>

            {/* Problem vs Solution Table */}
            <Card className="p-6">
              <h3 className="text-xl font-semibold mb-6">How MSME Booster Solves Your Problems</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 text-red-400">Traditional Problems</th>
                      <th className="text-left py-3 text-green-accent">Our Solutions</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    <tr className="border-b border-border">
                      <td className="py-4">
                        <div className="flex items-start space-x-2">
                          <AlertCircle className="w-4 h-4 text-red-400 mt-1" />
                          <span>Difficulty getting loans without credit history</span>
                        </div>
                      </td>
                      <td className="py-4">
                        <div className="flex items-start space-x-2">
                          <CheckCircle className="w-4 h-4 text-green-accent mt-1" />
                          <span>AI-powered creditworthiness using business data</span>
                        </div>
                      </td>
                    </tr>
                    <tr className="border-b border-border">
                      <td className="py-4">
                        <div className="flex items-start space-x-2">
                          <AlertCircle className="w-4 h-4 text-red-400 mt-1" />
                          <span>Limited market reach and buyer connections</span>
                        </div>
                      </td>
                      <td className="py-4">
                        <div className="flex items-start space-x-2">
                          <CheckCircle className="w-4 h-4 text-green-accent mt-1" />
                          <span>AI-powered buyer matching and marketplace</span>
                        </div>
                      </td>
                    </tr>
                    <tr className="border-b border-border">
                      <td className="py-4">
                        <div className="flex items-start space-x-2">
                          <AlertCircle className="w-4 h-4 text-red-400 mt-1" />
                          <span>Lack of business management tools</span>
                        </div>
                      </td>
                      <td className="py-4">
                        <div className="flex items-start space-x-2">
                          <CheckCircle className="w-4 h-4 text-green-accent mt-1" />
                          <span>Integrated CRM, ERP, and analytics dashboard</span>
                        </div>
                      </td>
                    </tr>
                    <tr className="border-b border-border">
                      <td className="py-4">
                        <div className="flex items-start space-x-2">
                          <AlertCircle className="w-4 h-4 text-red-400 mt-1" />
                          <span>Complex loan processes and paperwork</span>
                        </div>
                      </td>
                      <td className="py-4">
                        <div className="flex items-start space-x-2">
                          <CheckCircle className="w-4 h-4 text-green-accent mt-1" />
                          <span>Blockchain smart contracts with automated escrow</span>
                        </div>
                      </td>
                    </tr>
                    <tr>
                      <td className="py-4">
                        <div className="flex items-start space-x-2">
                          <AlertCircle className="w-4 h-4 text-red-400 mt-1" />
                          <span>Limited access to business education</span>
                        </div>
                      </td>
                      <td className="py-4">
                        <div className="flex items-start space-x-2">
                          <CheckCircle className="w-4 h-4 text-green-accent mt-1" />
                          <span>Video learning platform with AI chatbot mentor</span>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Button 
                  onClick={() => openModal('invoice')}
                  variant="ghost" 
                  className="w-full justify-start hover:bg-muted"
                >
                  <File className="w-5 h-5 mr-3 text-teal-accent" />
                  Upload Invoice
                </Button>
                <Button 
                  onClick={() => {
                    console.log('🔘 Invoice Management button clicked!');
                    console.log('Current activeModal:', activeModal);
                    openModal('invoiceManagement');
                    console.log('New activeModal should be: invoiceManagement');
                  }}
                  variant="ghost" 
                  className="w-full justify-start hover:bg-muted bg-blue-50 border border-blue-200"
                >
                  <FileText className="w-5 h-5 mr-3 text-blue-600" />
                  📋 Invoice Management (VIEW HISTORY)
                </Button>
                <Button 
                  onClick={() => openModal('loans')}
                  variant="ghost" 
                  className="w-full justify-start hover:bg-muted"
                >
                  <BadgeDollarSign className="w-5 h-5 mr-3 text-orange-accent" />
                  Find Loans
                </Button>
                <Button 
                  onClick={() => openModal('marketplace')}
                  variant="ghost" 
                  className="w-full justify-start hover:bg-muted"
                >
                  <Store className="w-5 h-5 mr-3 text-green-accent" />
                  List Product
                </Button>
                <Button 
                  onClick={() => openModal('learning')}
                  variant="ghost" 
                  className="w-full justify-start hover:bg-muted"
                >
                  <GraduationCap className="w-5 h-5 mr-3 text-teal-accent" />
                  Learn & Grow
                </Button>
              </div>
            </Card>

            {/* Recent Activity */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-accent rounded-full flex items-center justify-center">
                    <CheckCircle className="w-4 h-4 text-background" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold">Loan payment processed</div>
                    <div className="text-xs text-muted-foreground">2 hours ago</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-teal-accent rounded-full flex items-center justify-center">
                    <FileText className="w-4 h-4 text-background" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold">Invoice uploaded and verified</div>
                    <div className="text-xs text-muted-foreground">1 day ago</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-orange-accent rounded-full flex items-center justify-center">
                    <Medal className="w-4 h-4 text-background" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold">Earned "Reliable Payer" badge</div>
                    <div className="text-xs text-muted-foreground">3 days ago</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-green-accent rounded-full flex items-center justify-center">
                    <Activity className="w-4 h-4 text-background" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold">New product inquiry received</div>
                    <div className="text-xs text-muted-foreground">5 days ago</div>
                  </div>
                </div>
              </div>
            </Card>

            {/* AI Insights */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">AI Insights</h3>
              <div className="space-y-3">
                {aiInsights.map((insight) => {
                  const IconComponent = insight.icon === 'Lightbulb' ? Lightbulb :
                                      insight.icon === 'ChartLine' ? ChartLine :
                                      insight.icon === 'Users' ? Users : TrendingUp;
                  
                  return (
                    <div 
                      key={insight.id}
                      className={`p-3 bg-${insight.color}-accent/20 border border-${insight.color}-accent rounded-lg`}
                    >
                      <div className={`text-sm text-${insight.color}-accent`}>
                        <IconComponent className="w-4 h-4 mr-1 inline" />
                        {insight.message}
                      </div>
                    </div>
                  );
                })}
                {aiInsights.length === 0 && (
                  <div className="p-3 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg">
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      <Brain className="w-4 h-4 mr-1 inline" />
                      Upload invoices to get personalized AI insights!
                    </div>
                  </div>
                )}
              </div>
            </Card>


          </div>
        </div>
      </div>

      {/* Modals */}
      <LearningModal open={activeModal === 'learning'} onOpenChange={closeModal} />
      <InvoiceUploadModal 
        open={activeModal === 'invoice'} 
        onOpenChange={closeModal} 
        onUploadComplete={() => {
          console.log('🔄 Invoice uploaded, refreshing dashboard credit score...');
          refreshCreditScore();
        }}
      />
      <InvoiceManagementModal open={activeModal === 'invoiceManagement'} onOpenChange={closeModal} />
      <LoanDiscoveryModal open={activeModal === 'loans'} onOpenChange={closeModal} />
      <MarketplaceModal open={activeModal === 'marketplace'} onOpenChange={closeModal} />
    </div>
  );
}
