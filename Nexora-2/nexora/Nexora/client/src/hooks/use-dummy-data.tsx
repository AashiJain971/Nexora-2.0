import { useState, useCallback } from 'react';
import * as dummyData from '@/lib/dummy-data';

export function useDummyData() {
  const [isLoading, setIsLoading] = useState(false);

  const simulateApiCall = useCallback(async (delay = 1000) => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, delay));
    setIsLoading(false);
  }, []);

  const simulateWalletConnection = useCallback(async () => {
    await simulateApiCall(2000);
    return {
      success: true,
      address: "0x1234567890abcdef1234567890abcdef12345678",
    };
  }, [simulateApiCall]);

  /**
   * Main updated logic for invoice & credit score
   */
  const simulateInvoiceProcessing = useCallback(async (file: File) => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append("image", file);

      // Step 1: Extract invoice information
      const extractRes = await fetch("http://localhost:8001/extract-invoice", {
        method: "POST",
        body: formData,
      });
      if (!extractRes.ok) throw new Error(`API Error: ${extractRes.status} ${extractRes.statusText}`);
      const data = await extractRes.json();
      const invoice = data.invoice_details;

      // Step 2: Prepare credit model payload
      const pending = invoice.total_amount_pending ?? 0;
      const paid = invoice.total_amount_paid ?? (invoice.total_amount - pending);

      const creditScorePayload = {
        no_of_invoices: 1,
        total_amount: invoice.total_amount,
        total_amount_pending: pending,
        total_amount_paid: paid,
        tax: invoice.tax_amount ?? 0,
        extra_charges: invoice.extra_charges ?? 0,
        payment_completion_rate: invoice.payment_completion_rate ?? 0,
        paid_to_pending_ratio: paid / (pending || 1),
      };

      // Step 3: Call credit score API
      const scoreRes = await fetch("http://localhost:8001/calculate-credit-score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(creditScorePayload),
      });
      if (!scoreRes.ok) throw new Error(`Credit Score API Error: ${scoreRes.status} ${scoreRes.statusText}`);
      const scoreData = await scoreRes.json();
      const csAnalysis = scoreData.credit_score_analysis;

      // Step 4: Return combined analysis (add credit score info)
      return {
        success: true,
        analysis: {
          invoiceNumber: invoice.invoice_number,
          client: invoice.client,
          date: invoice.date,
          paymentTerms: invoice.payment_terms,
          industry: invoice.industry,
          totalAmount: invoice.total_amount,
          currency: invoice.currency,
          lineItems: invoice.line_items,
          taxAmount: invoice.tax_amount,
          extraCharges: invoice.extra_charges,
          totalLineItems: data.total_line_items,
          credibilityScore: csAnalysis.final_weighted_credit_score,
          scoreCategory: csAnalysis.score_category,
          factorBreakdown: csAnalysis.factor_breakdown,
          detailedAnalysis: csAnalysis.detailed_analysis,
          recommendations: csAnalysis.recommendations,
          loanEligibility: invoice.total_amount ? invoice.total_amount * 0.6 : 0,
        },
      };
    } catch (error) {
      console.error("Invoice processing failed:", error);
      return {
        success: false,
        analysis: null,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const simulateLoanApplication = useCallback(async (loanId: string) => {
    await simulateApiCall(2000);
    return {
      success: true,
      applicationId: `APP-${Date.now()}`,
      status: "submitted",
    };
  }, [simulateApiCall]);

  const simulateProductListing = useCallback(async (productData: any) => {
    await simulateApiCall(1500);
    return {
      success: true,
      productId: `PROD-${Date.now()}`,
    };
  }, [simulateApiCall]);

  const simulateMilestoneRelease = useCallback(async (milestoneId: number) => {
    await simulateApiCall(2500);
    return {
      success: true,
      transactionHash: `0x${Math.random().toString(16).substr(2, 40)}`,
    };
  }, [simulateApiCall]);

  const getRandomAIResponse = useCallback(() => {
    const responses = dummyData.dummyAIResponses;
    return responses[Math.floor(Math.random() * responses.length)];
  }, []);

  return {
    isLoading,
    businessProfile: dummyData.dummyBusinessProfile,
    loans: dummyData.dummyLoans,
    products: dummyData.dummyProducts,
    invoices: dummyData.dummyInvoices,
    badges: dummyData.dummyBadges,
    orders: dummyData.dummyOrders,
    customers: dummyData.dummyCustomers,
    expenses: dummyData.dummyExpenses,
    recentExpenses: dummyData.dummyRecentExpenses,
    learningProgress: dummyData.dummyLearningProgress,
    learningCourses: dummyData.dummyLearningCourses,
    escrowMilestones: dummyData.dummyEscrowMilestones,
    marketplaceProducts: dummyData.dummyMarketplaceProducts,
    buyerInquiries: dummyData.dummyBuyerInquiries,
    simulateApiCall,
    simulateWalletConnection,
    simulateInvoiceProcessing,
    simulateLoanApplication,
    simulateProductListing,
    simulateMilestoneRelease,
    getRandomAIResponse,
  };
}
