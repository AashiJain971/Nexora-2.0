import { useState, useRef } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { CloudUpload, FileText, CheckCircle, Loader2, Bot } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface InvoiceUploadModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function InvoiceUploadModal({ open, onOpenChange }: InvoiceUploadModalProps) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [analysis, setAnalysis] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files && e.target.files.length > 0 ? e.target.files[0] : null;
    if (file) {
      setUploadedFile(file);
      setAnalysis(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const dtFiles = e.dataTransfer.files;
    const file = dtFiles && dtFiles.length > 0 ? dtFiles[0] : null;
    if (file && (file.type === 'application/pdf' || file.type.startsWith('image/'))) {
      setUploadedFile(file);
      setAnalysis(null);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const processInvoice = async () => {
    if (!uploadedFile) return;
    setIsProcessing(true);
    setProcessingProgress(0);

    const progressInterval = setInterval(() => {
      setProcessingProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 300);

    try {
      // Use the new process-invoice endpoint that handles everything
      const formData = new FormData();
      formData.append('image', uploadedFile);

      // Get authentication token
      const token = localStorage.getItem('nexora_token');
      if (!token) {
        throw new Error('Please log in to process invoices');
      }

      const processResponse = await fetch('http://localhost:8001/process-invoice', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!processResponse.ok) {
        throw new Error(`Invoice processing failed: ${processResponse.statusText}`);
      }

      const result = await processResponse.json();
      console.log('Invoice processing result:', result);

      // Extract data from the unified response
      const invoiceDetails = result.invoice_details;
      const creditScoreAnalysis = result.credit_score_analysis;
      const historicalSummary = result.historical_summary;

      // Combine all data for display
      const combinedAnalysis = {
        // Invoice details
        invoiceNumber: invoiceDetails.invoice_number,
        client: invoiceDetails.client,
        date: invoiceDetails.date,
        paymentTerms: invoiceDetails.payment_terms,
        industry: invoiceDetails.industry,
        totalAmount: invoiceDetails.total_amount,
        currency: invoiceDetails.currency,
        taxAmount: invoiceDetails.tax_amount,
        extraCharges: invoiceDetails.extra_charges,
        lineItems: invoiceDetails.line_items,
        totalLineItems: result.total_line_items,
        // Credit score analysis based on real historical data
        credit_score_analysis: creditScoreAnalysis,
        // Historical context
        historical_summary: historicalSummary,
      };

      setAnalysis(combinedAnalysis);
      setProcessingProgress(100);
      toast({
        title: "Invoice Processed Successfully!",
        description: `AI analysis complete. Credit score calculated based on ${historicalSummary.total_historical_invoices} historical invoices.`,
      });
    } catch (error) {
      console.error('Processing error:', error);
      toast({
        title: "Processing Failed",
        description: error instanceof Error ? error.message : "Failed to process invoice. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
      clearInterval(progressInterval);
    }
  };

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(amount ?? 0);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold">Upload & Verify Invoice</DialogTitle>
        </DialogHeader>
        <div className="grid md:grid-cols-2 gap-6">
          {/* -------- LEFT SIDE -------- */}
          <div className="space-y-6">
            {/* Upload Area */}
            <Card
              className="border-2 border-dashed border-border hover:border-teal-accent transition-colors cursor-pointer p-8 text-center"
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <CloudUpload className="w-12 h-12 text-teal-600 mx-auto mb-4" />
              <p className="text-lg mb-2">Drop your invoice here or click to upload</p>
              <p className="text-sm text-muted-foreground">Supports PDF, PNG, JPG up to 10MB</p>
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={handleFileSelect}
              />
            </Card>

            {/* Uploaded File */}
            {uploadedFile && (
              <Card className="p-4 bg-green-50 border-green-200">
                <div className="flex items-center space-x-3">
                  <FileText className="w-8 h-8 text-green-600" />
                  <div>
                    <div className="font-semibold">{uploadedFile.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                    </div>
                  </div>
                  <CheckCircle className="w-6 h-6 text-green-600 ml-auto" />
                </div>
              </Card>
            )}

            {/* Processing Status */}
            {isProcessing && (
              <Card className="p-4">
                <div className="space-y-3">
                  <div className="flex items-center text-orange-500">
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processing invoice with AI...
                  </div>
                  <Progress value={processingProgress} className="w-full" />
                  <div className="text-sm text-muted-foreground">
                    Analyzing document structure, extracting data, and verifying authenticity...
                  </div>
                </div>
              </Card>
            )}

            <Button
              onClick={processInvoice}
              disabled={!uploadedFile || isProcessing}
              className="w-full bg-gradient-to-r from-teal-500 to-green-500 text-white"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                "Process & Verify Invoice"
              )}
            </Button>
          </div>

          {/* -------- RIGHT SIDE -------- */}
          <div className="space-y-6">
            {analysis && (
              <Card className="p-6 overflow-auto max-h-[80vh]">
                <div className="flex items-center space-x-2 mb-4">
                  <Bot className="w-5 h-5 text-teal-600" />
                  <h4 className="text-lg font-semibold">AI Analysis Results</h4>
                </div>

                {/* Invoice Details */}
                <div className="space-y-3 mb-6 text-sm">
                  <div className="flex justify-between"><strong>Invoice Number:</strong> <span>{analysis.invoiceNumber}</span></div>
                  <div className="flex justify-between"><strong>Client:</strong> <span>{analysis.client}</span></div>
                  <div className="flex justify-between"><strong>Date:</strong> <span>{analysis.date}</span></div>
                  <div className="flex justify-between"><strong>Payment Terms:</strong> <span>{analysis.paymentTerms}</span></div>
                  <div className="flex justify-between"><strong>Industry:</strong> <span>{analysis.industry}</span></div>
                  <div className="flex justify-between"><strong>Total Amount:</strong> <span>{formatCurrency(analysis.totalAmount)}</span></div>
                  <div className="flex justify-between"><strong>Currency:</strong> <span>{analysis.currency}</span></div>
                  <div className="flex justify-between"><strong>Tax:</strong> <span>{formatCurrency(analysis.taxAmount || 0)}</span></div>
                  <div className="flex justify-between"><strong>Extra Charges:</strong> <span>{formatCurrency(analysis.extraCharges || 0)}</span></div>
                  <div className="flex justify-between"><strong>Total Line Items:</strong> <span>{analysis.totalLineItems}</span></div>
                </div>

                {/* Line Items */}
                <h5 className="font-semibold text-lg mb-3 text-foreground">Line Items</h5>
                <div className="overflow-hidden rounded-lg border border-border shadow-sm">
                  <table className="w-full text-sm">
                    <thead className="bg-gradient-to-r from-teal-100 to-blue-100 dark:from-teal-900 dark:to-blue-900">
                      <tr>
                        <th className="p-3 text-left font-semibold text-gray-800 dark:text-gray-100 border-b border-border">Description</th>
                        <th className="p-3 text-right font-semibold text-gray-800 dark:text-gray-100 border-b border-border">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Array.isArray(analysis.lineItems) &&
                        analysis.lineItems.map((item: any, index: number) => (
                          <tr key={index} className="bg-card hover:bg-accent/50 transition-colors duration-150">
                            <td className="p-3 border-b border-border/30 font-medium text-foreground">{item.description}</td>
                            <td className="p-3 text-right border-b border-border/30 font-semibold text-foreground">{formatCurrency(item.amount)}</td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>

                {/* Credit Score Analysis */}
                <div className="mt-6">
                  <h5 className="font-semibold text-lg mb-3 text-foreground">Credit Score Analysis</h5>
                  <div className="overflow-hidden rounded-lg border border-border shadow-sm">
                    <div className="bg-gradient-to-r from-teal-100 to-blue-100 dark:from-teal-900 dark:to-blue-900 p-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="text-gray-600 dark:text-gray-300 text-sm">Final Weighted Score</div>
                          <div className="font-bold text-teal-accent text-2xl">
                            {analysis?.credit_score_analysis?.final_weighted_credit_score?.toFixed(1)}/100
                          </div>
                          <div className="text-sm font-medium text-gray-800 dark:text-gray-100">{analysis?.credit_score_analysis?.score_category}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Detailed Analysis */}
                {analysis.credit_score_analysis?.detailed_analysis && (
                  <div className="mt-6">
                    <h5 className="font-semibold mb-2">Detailed Analysis</h5>
                    <div className="space-y-3 text-sm">
                      {/* Strengths */}
                      {analysis.credit_score_analysis.detailed_analysis.strengths?.length > 0 && (
                        <div>
                          <h6 className="font-medium text-green-600 mb-1">Strengths:</h6>
                          <ul className="list-disc pl-5 space-y-1">
                            {analysis.credit_score_analysis.detailed_analysis.strengths.map(
                              (strength: string, idx: number) => (
                                <li key={idx} className="text-green-700">{strength}</li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                      
                      {/* Weaknesses */}
                      {analysis.credit_score_analysis.detailed_analysis.weaknesses?.length > 0 && (
                        <div>
                          <h6 className="font-medium text-red-600 mb-1">Weaknesses:</h6>
                          <ul className="list-disc pl-5 space-y-1">
                            {analysis.credit_score_analysis.detailed_analysis.weaknesses.map(
                              (weakness: string, idx: number) => (
                                <li key={idx} className="text-red-700">{weakness}</li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                      
                      {/* Risk Assessment */}
                      {analysis.credit_score_analysis.detailed_analysis.risk_assessment && (
                        <div>
                          <h6 className="font-medium text-orange-600 mb-1">Risk Assessment:</h6>
                          <p className="text-orange-700">{analysis.credit_score_analysis.detailed_analysis.risk_assessment}</p>
                        </div>
                      )}
                      
                      {/* Creditworthiness Summary */}
                      {analysis.credit_score_analysis.detailed_analysis.creditworthiness_summary?.length > 0 && (
                        <div>
                          <h6 className="font-medium text-blue-600 mb-1">Creditworthiness Summary:</h6>
                          <ul className="list-disc pl-5 space-y-1">
                            {analysis.credit_score_analysis.detailed_analysis.creditworthiness_summary.map(
                              (summary: string, idx: number) => (
                                <li key={idx} className="text-blue-700">{summary}</li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Factor Breakdown Table */}
                {analysis.credit_score_analysis?.factor_breakdown && (
                  <div className="mt-6">
                    <h5 className="font-semibold text-lg mb-3 text-foreground">Score Factor Breakdown</h5>
                    <div className="overflow-hidden rounded-lg border border-border shadow-sm">
                      <table className="w-full text-sm">
                        <thead className="bg-gradient-to-r from-teal-100 to-blue-100 dark:from-teal-900 dark:to-blue-900">
                          <tr>
                            <th className="p-3 text-left font-semibold text-gray-800 dark:text-gray-100 border-b border-border">Factor</th>
                            <th className="p-3 text-center font-semibold text-gray-800 dark:text-gray-100 border-b border-border">Score</th>
                            <th className="p-3 text-center font-semibold text-gray-800 dark:text-gray-100 border-b border-border">Weight %</th>
                            <th className="p-3 text-left font-semibold text-gray-800 dark:text-gray-100 border-b border-border">Comment</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(analysis.credit_score_analysis.factor_breakdown).map(
                            ([factor, details]: [string, any], idx) => (
                              <tr key={idx} className="bg-card hover:bg-accent/50 transition-colors duration-150">
                                <td className="p-3 border-b border-border/30 font-medium text-foreground">
                                  {factor.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </td>
                                <td className="p-3 text-center border-b border-border/30 font-semibold text-foreground">
                                  {details?.individual_score ?? '-'}
                                </td>
                                <td className="p-3 text-center border-b border-border/30 font-semibold text-teal-accent">
                                  {details?.weight_percentage ?? '-'}%
                                </td>
                                <td className="p-3 border-b border-border/30 text-muted-foreground text-xs leading-relaxed">
                                  {details?.comment ?? '-'}
                                </td>
                              </tr>
                            )
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                {analysis.credit_score_analysis?.recommendations && (
                  <div className="mt-6">
                    <h5 className="font-semibold mb-2">AI Recommendations</h5>
                    <div className="space-y-3">
                      {/* Immediate Actions */}
                      {analysis.credit_score_analysis.recommendations.immediate_actions?.length > 0 && (
                        <div>
                          <h6 className="font-medium text-red-600 mb-1">Immediate Actions:</h6>
                          <ul className="list-disc pl-5 text-sm space-y-1">
                            {analysis.credit_score_analysis.recommendations.immediate_actions.map(
                              (action: string, idx: number) => (
                                <li key={idx} className="text-red-700">{action}</li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                      
                      {/* Long Term Improvements */}
                      {analysis.credit_score_analysis.recommendations.long_term_improvements?.length > 0 && (
                        <div>
                          <h6 className="font-medium text-blue-600 mb-1">Long-term Improvements:</h6>
                          <ul className="list-disc pl-5 text-sm space-y-1">
                            {analysis.credit_score_analysis.recommendations.long_term_improvements.map(
                              (improvement: string, idx: number) => (
                                <li key={idx} className="text-blue-700">{improvement}</li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                      
                      {/* Priority Focus Areas */}
                      {analysis.credit_score_analysis.recommendations.priority_focus_areas?.length > 0 && (
                        <div>
                          <h6 className="font-medium text-orange-600 mb-1">Priority Focus Areas:</h6>
                          <ul className="list-disc pl-5 text-sm space-y-1">
                            {analysis.credit_score_analysis.recommendations.priority_focus_areas.map(
                              (area: string, idx: number) => (
                                <li key={idx} className="text-orange-700">{area}</li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </Card>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
