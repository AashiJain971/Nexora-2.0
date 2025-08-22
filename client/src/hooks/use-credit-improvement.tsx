import { useState, useEffect } from 'react';
import { useCreditScore } from './use-credit-score';

interface CreditScoreImprovement {
  improvement: number;
  message: string;
  monthlyGrowthRate: number;
  projectedScore: number;
}

export function useCreditScoreImprovement(): CreditScoreImprovement {
  const { creditScore, category, totalInvoices } = useCreditScore();
  const [improvement, setImprovement] = useState(0);
  const [message, setMessage] = useState('');
  const [monthlyGrowthRate, setMonthlyGrowthRate] = useState(0);

  useEffect(() => {
    // Calculate improvement based on current score and invoice count
    // Simulate realistic improvement based on business activity
    let calculatedImprovement = 0;
    let growthRate = 0;
    
    if (creditScore > 0) {
      // Base improvement on score range and invoice count
      if (creditScore >= 80) {
        calculatedImprovement = Math.floor(Math.random() * 8) + 2; // 2-10 points for excellent scores
        growthRate = Math.floor(Math.random() * 5) + 2; // 2-7%
      } else if (creditScore >= 70) {
        calculatedImprovement = Math.floor(Math.random() * 12) + 8; // 8-20 points for good scores
        growthRate = Math.floor(Math.random() * 8) + 5; // 5-13%
      } else if (creditScore >= 60) {
        calculatedImprovement = Math.floor(Math.random() * 15) + 10; // 10-25 points for fair scores
        growthRate = Math.floor(Math.random() * 12) + 8; // 8-20%
      } else {
        calculatedImprovement = Math.floor(Math.random() * 20) + 15; // 15-35 points for low scores
        growthRate = Math.floor(Math.random() * 15) + 10; // 10-25%
      }

      // Adjust based on invoice count
      const invoiceMultiplier = Math.min(2.0, 1 + (totalInvoices * 0.1));
      calculatedImprovement = Math.round(calculatedImprovement * invoiceMultiplier);
      
      setImprovement(calculatedImprovement);
      setMonthlyGrowthRate(growthRate);

      // Generate contextual message
      if (calculatedImprovement > 25) {
        setMessage('Exceptional growth! Your consistent invoice uploads and payment history are significantly boosting your credibility.');
      } else if (calculatedImprovement > 15) {
        setMessage('Great progress! Your business activity and payment consistency are building strong credibility.');
      } else if (calculatedImprovement > 5) {
        setMessage('Steady improvement! Keep uploading invoices to maintain this positive momentum.');
      } else {
        setMessage('Your score is stabilizing at a high level. Continue your excellent payment practices!');
      }
    } else {
      setImprovement(0);
      setMonthlyGrowthRate(0);
      setMessage('Upload your first invoice to start building your credibility score!');
    }
  }, [creditScore, category, totalInvoices]);

  const projectedScore = Math.min(100, creditScore + (monthlyGrowthRate * 2)); // Project 2 months ahead

  return {
    improvement,
    message,
    monthlyGrowthRate,
    projectedScore
  };
}
