import { useState, useEffect } from 'react';
import { useCreditScore } from './use-credit-score';

interface AIInsight {
  id: string;
  type: 'credit' | 'revenue' | 'business' | 'loan';
  icon: string;
  message: string;
  color: 'teal' | 'orange' | 'green' | 'blue';
  priority: number;
}

export function useAIInsights() {
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const { creditScore, category, totalInvoices } = useCreditScore();
  const [previousScore, setPreviousScore] = useState<number | null>(null);

  useEffect(() => {
    // Calculate score improvement (simulate previous score for demo)
    const simulatedPreviousScore = creditScore > 0 ? Math.max(0, creditScore - Math.floor(Math.random() * 20) - 10) : 0;
    const scoreImprovement = creditScore - simulatedPreviousScore;
    
    const generatedInsights: AIInsight[] = [];

    // Credit Score Insight
    if (creditScore > 0) {
      if (scoreImprovement > 0) {
        generatedInsights.push({
          id: 'credit-improvement',
          type: 'credit',
          icon: 'Lightbulb',
          message: `Your credit score improved by ${Math.max(1, Math.round(scoreImprovement))} points! ${
            creditScore >= 80 ? 'Excellent - consider applying for premium loan products.' :
            creditScore >= 70 ? 'Good progress - you\'re eligible for competitive rates.' :
            creditScore >= 60 ? 'Fair improvement - continue building your credit history.' :
            'Keep uploading invoices to improve your score further.'
          }`,
          color: 'teal',
          priority: 1
        });
      } else {
        generatedInsights.push({
          id: 'credit-stable',
          type: 'credit',
          icon: 'Lightbulb',
          message: `Credit score: ${creditScore}/100 (${category}). ${
            creditScore >= 80 ? 'Excellent score - you qualify for the best rates!' :
            creditScore >= 70 ? 'Good score - consider applying for larger loan amounts.' :
            creditScore >= 60 ? 'Fair score - upload more invoices to improve further.' :
            'Upload invoices regularly to build your credit history.'
          }`,
          color: creditScore >= 70 ? 'teal' : 'orange',
          priority: 2
        });
      }
    } else {
      generatedInsights.push({
        id: 'credit-start',
        type: 'credit',
        icon: 'Lightbulb',
        message: 'Start building your credit score by uploading your first invoice!',
        color: 'blue',
        priority: 1
      });
    }

    // Business Growth Insight
    if (totalInvoices > 1) {
      const revenueGrowth = Math.floor(Math.random() * 25) + 5; // Simulate 5-30% growth
      generatedInsights.push({
        id: 'revenue-growth',
        type: 'revenue',
        icon: 'ChartLine',
        message: `Revenue increased ${revenueGrowth}% based on your ${totalInvoices} invoices - ${
          revenueGrowth > 20 ? 'perfect time to expand your product line!' :
          revenueGrowth > 15 ? 'great progress, consider diversifying your services.' :
          'steady growth, keep building your customer base.'
        }`,
        color: 'orange',
        priority: 3
      });
    } else if (totalInvoices === 1) {
      generatedInsights.push({
        id: 'first-invoice',
        type: 'business',
        icon: 'ChartLine',
        message: 'Great start! Upload more invoices to track your business growth.',
        color: 'green',
        priority: 2
      });
    }

    // Loan Opportunities
    if (creditScore >= 70) {
      generatedInsights.push({
        id: 'loan-opportunity',
        type: 'loan',
        icon: 'Users',
        message: `${Math.floor(Math.random() * 5) + 2} premium lenders matched for your business profile this week.`,
        color: 'green',
        priority: 4
      });
    } else if (creditScore >= 50) {
      generatedInsights.push({
        id: 'building-eligibility',
        type: 'business',
        icon: 'Users',
        message: 'You\'re building loan eligibility! Continue uploading invoices for better rates.',
        color: 'blue',
        priority: 3
      });
    }

    // Sort by priority and take top 3
    const sortedInsights = generatedInsights.sort((a, b) => a.priority - b.priority).slice(0, 3);
    setInsights(sortedInsights);
    
    if (previousScore === null) {
      setPreviousScore(simulatedPreviousScore);
    }
  }, [creditScore, category, totalInvoices, previousScore]);

  return insights;
}
