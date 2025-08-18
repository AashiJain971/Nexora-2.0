import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { FileText, Eye, Download, Calendar, DollarSign, Building, TrendingUp } from 'lucide-react';

interface Invoice {
  id: number;
  invoice_number: string;
  client: string;
  date: string;
  total_amount: number;
  currency: string;
  payment_terms: string;
  industry: string;
  status: string;
  created_at: string;
  tax_amount?: number;
  line_items: Array<{
    description: string;
    amount: number;
  }>;
}

interface InvoiceManagementModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function InvoiceManagementModal({ open, onOpenChange }: InvoiceManagementModalProps) {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const { toast } = useToast();
  const { token } = useAuth();

  // Debugging: Log the current token being used
  useEffect(() => {
    console.log('🔐 Current auth token for invoice management:', token?.substring(0, 20) + '...');
    console.log('🔐 Full token for debugging (REMOVE IN PRODUCTION):', token);
  }, [token]);

  const formatCurrency = (amount: number, currency: string = 'INR') =>
    new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      maximumFractionDigits: 2,
    }).format(amount ?? 0);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const fetchInvoices = async () => {
    if (!token) {
      console.log('⚠️ No token available for fetching invoices');
      return;
    }
    
    setLoading(true);
    try {
      console.log('🔍 Fetching invoices with token:', token?.substring(0, 20) + '...');
      console.log('🌐 Making request to: http://localhost:8001/user/invoices');
      
      const response = await fetch('http://localhost:8001/user/invoices', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      console.log('📊 Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Fetched invoices data:', data);
        console.log('📊 Number of invoices found:', data.invoices?.length || 0);
        console.log('📋 All invoices:', data.invoices);
        
        // Set ALL invoices to state for proper scrolling
        setInvoices(data.invoices || []);
        
        // Enhanced debugging
        console.log('📋 SETTING INVOICES STATE:', data.invoices?.length || 0);
        console.log('📋 ALL INVOICE DETAILS:');
        data.invoices?.forEach((invoice: any, index: number) => {
          console.log(`  Invoice ${index + 1}:`, {
            id: invoice.id,
            number: invoice.invoice_number,
            client: invoice.client,
            amount: invoice.total_amount,
            date: invoice.date,
            status: invoice.status
          });
        });
        
        // Additional debugging
        if (data.invoices && data.invoices.length > 0) {
          console.log('📋 First invoice details:', data.invoices[0]);
          console.log('📋 Last invoice details:', data.invoices[data.invoices.length - 1]);
        } else {
          console.log('⚠️ No invoices found for current user');
        }

        if (data.invoices?.length === 0) {
          toast({
            title: 'No Invoices Found',
            description: 'Upload your first invoice to start building your credibility history!',
          });
        } else if (data.invoices?.length > 0) {
          console.log(`✅ Successfully loaded ${data.invoices.length} invoices for display`);
        }
      } else {
        console.error('❌ Failed to fetch invoices - response not ok:', response.status, response.statusText);
        toast({
          title: 'Failed to Load Invoices',
          description: 'Could not retrieve your invoice history. Please try again.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('❌ Error fetching invoices:', error);
      toast({
        title: 'Network Error',
        description: 'Failed to load invoices. Please check your connection and try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, [token]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return <Badge className="bg-green-100 text-green-800">Paid</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case 'overdue':
        return <Badge className="bg-red-100 text-red-800">Overdue</Badge>;
      default:
        return <Badge className="bg-slate-200 text-slate-800 dark:bg-slate-700 dark:text-slate-200">Processed</Badge>;
    }
  };

  const addSampleInvoices = async () => {
    if (!token) return;
    
    try {
      const response = await fetch('http://localhost:8001/add-sample-invoices', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Sample Invoices Added',
          description: data.message,
          variant: 'default',
        });
        // Refresh the invoices list
        fetchInvoices();
      } else {
        toast({
          title: 'Failed to Add Sample Invoices',
          description: 'Could not add sample invoices. Please try again.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error adding sample invoices:', error);
      toast({
        title: 'Network Error',
        description: 'Please try again.',
        variant: 'destructive',
      });
    }
  };

  const totalInvoiceValue = invoices.reduce((sum, inv) => sum + inv.total_amount, 0);
  const avgInvoiceValue = invoices.length > 0 ? totalInvoiceValue / invoices.length : 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[95vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-2xl font-bold flex items-center gap-2">
              <FileText className="w-6 h-6 text-teal-accent" />
              Invoice Management & Credibility History
            </DialogTitle>
            <button
              onClick={addSampleInvoices}
              className="bg-gradient-to-r from-teal-600 to-purple-600 hover:from-teal-700 hover:to-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 shadow-md hover:shadow-lg"
            >
              Add Sample Data
            </button>
          </div>
          <p className="text-muted-foreground">
            View your uploaded invoices that contribute to your credibility score. 
            Each invoice adds to your payment history, financial stability analysis, and industry risk assessment.
          </p>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <span className="ml-2">Loading your invoices...</span>
          </div>
        ) : (
          <div className="space-y-6">
            {invoices.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <FileText className="w-16 h-16 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Invoices Yet</h3>
                <p className="text-muted-foreground mb-4 max-w-md">
                  Start building your credibility history by uploading your first invoice. 
                  Each invoice contributes to your credibility analysis.
                </p>
                <Button onClick={() => onOpenChange(false)} className="bg-teal-accent hover:bg-teal-accent/90">
                  Upload Your First Invoice
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="p-4">
                    <div className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-teal-accent" />
                      <div>
                        <p className="text-sm text-muted-foreground">Total Invoices</p>
                        <p className="text-2xl font-bold">{invoices.length}</p>
                      </div>
                    </div>
                  </Card>
                  
                  <Card className="p-4">
                    <div className="flex items-center gap-2">
                      <DollarSign className="w-5 h-5 text-green-accent" />
                      <div>
                        <p className="text-sm text-muted-foreground">Total Value</p>
                        <p className="text-2xl font-bold">{formatCurrency(totalInvoiceValue)}</p>
                      </div>
                    </div>
                  </Card>
                  
                  <Card className="p-4">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-orange-accent" />
                      <div>
                        <p className="text-sm text-muted-foreground">Avg Invoice</p>
                        <p className="text-2xl font-bold">{formatCurrency(avgInvoiceValue)}</p>
                      </div>
                    </div>
                  </Card>
                </div>

                {/* Credit Score Info */}
                <Card className="p-4 bg-gradient-to-r from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-900 border-slate-300 dark:border-slate-600">
                  <div className="flex items-start gap-3">
                    <TrendingUp className="w-5 h-5 text-teal-accent mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-slate-800 dark:text-slate-100 mb-1">
                        How Your Credibility Score is Calculated
                      </h4>
                      <p className="text-sm text-slate-700 dark:text-slate-200">
                        Your credibility is analyzed based on: <strong>Payment Completion Rate (40%)</strong> - 
                        consistency in invoice payments, <strong>Paid-to-Pending Ratio (30%)</strong> - cash flow management, 
                        <strong>Tax Compliance (15%)</strong> - regulatory adherence, and <strong>Extra Charges Management (15%)</strong> - 
                        operational efficiency. More invoices provide better analysis accuracy.
                      </p>
                    </div>
                  </div>
                </Card>

                {/* Invoice List with Improved Scrolling */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">All Invoices ({invoices.length})</h3>
                  <div className="min-h-[400px] max-h-[50vh] overflow-y-auto border rounded-lg p-4 space-y-4 bg-slate-50 dark:bg-slate-900/30 border-slate-200 dark:border-slate-700">
                    {invoices.map((invoice, index) => (
                      <Card key={`${invoice.id}-${index}`} className="p-4 hover:shadow-md transition-shadow bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-600">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-semibold text-lg">{invoice.invoice_number}</h4>
                              {getStatusBadge(invoice.status || 'processed')}
                            </div>
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div className="flex items-center gap-1">
                                <Building className="w-4 h-4 text-muted-foreground" />
                                <span className="text-muted-foreground">Client:</span>
                                <span className="font-medium">{invoice.client}</span>
                              </div>
                              
                              <div className="flex items-center gap-1">
                                <Calendar className="w-4 h-4 text-muted-foreground" />
                                <span className="text-muted-foreground">Date:</span>
                                <span className="font-medium">{formatDate(invoice.date)}</span>
                              </div>
                              
                              <div className="flex items-center gap-1">
                                <DollarSign className="w-4 h-4 text-muted-foreground" />
                                <span className="text-muted-foreground">Amount:</span>
                                <span className="font-medium text-green-600">
                                  {formatCurrency(invoice.total_amount, invoice.currency)}
                                </span>
                              </div>
                              
                              <div className="flex items-center gap-1">
                                <span className="text-muted-foreground">Industry:</span>
                                <span className="font-medium">{invoice.industry}</span>
                              </div>
                            </div>
                            
                            <div className="mt-2 text-sm text-muted-foreground">
                              <span>Payment Terms: {invoice.payment_terms}</span>
                              <span className="mx-2">•</span>
                              <span>{invoice.line_items?.length || 0} line items</span>
                            </div>
                          </div>
                          
                          <div className="flex gap-2">
                            <Button 
                              variant="outline" 
                              size="sm" 
                              onClick={() => setSelectedInvoice(invoice)}
                              className="flex items-center gap-1"
                            >
                              <Eye className="w-4 h-4" />
                              View
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm" 
                              className="flex items-center gap-1"
                            >
                              <Download className="w-4 h-4" />
                              Download
                            </Button>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
