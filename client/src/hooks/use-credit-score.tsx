import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface CreditScoreData {
  creditScore: number;
  category: string;
  lastUpdated: string;
  totalInvoices: number;
  loading: boolean;
  error: string | null;
  refreshCreditScore: () => Promise<void>;
}

export function useCreditScore(): CreditScoreData {
  const [creditScore, setCreditScore] = useState(0); // Start with 0 for no invoices
  const [category, setCategory] = useState('No Data');
  const [lastUpdated, setLastUpdated] = useState('');
  const [totalInvoices, setTotalInvoices] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  // Debugging: Log the current token being used
  useEffect(() => {
    console.log('🔐 Credit score hook - Current auth token:', token?.substring(0, 20) + '...');
    console.log('🔐 Credit score hook - Full token for debugging (REMOVE IN PRODUCTION):', token);
  }, [token]);

  const fetchCreditScore = async () => {
    if (!token) {
      console.log('⚠️ No token available for credit score calculation, waiting for authentication...');
      setError('User not authenticated');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('📊 Fetching dashboard credit score from Supabase API...');
      
      // Use the new dashboard credit score endpoint
      const creditScoreResponse = await fetch('https://nexora-2-0-6.onrender.com/dashboard/credit-score', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (creditScoreResponse.status === 401) {
        console.error('❌ Authentication failed for dashboard credit score - token may be expired');
        setError('Authentication failed');
        return;
      }

      if (creditScoreResponse.ok) {
        const dashboardData = await creditScoreResponse.json();
        
        console.log('✅ Dashboard credit score fetched from database:', {
          score: dashboardData.credit_score,
          category: dashboardData.category,
          totalInvoices: dashboardData.total_invoices,
          debugInfo: dashboardData.debug_info
        });
        
        setCreditScore(dashboardData.credit_score);
        setCategory(dashboardData.category);
        setTotalInvoices(dashboardData.total_invoices);
        setLastUpdated(dashboardData.last_updated);
        
        if (dashboardData.error) {
          setError(dashboardData.error);
        }
        
        console.log('✅ Dashboard credit score updated from database:', dashboardData.credit_score, dashboardData.category);
      } else {
        console.error('Failed to fetch dashboard credit score - Response not OK');
        console.error('Response status:', creditScoreResponse.status);
        console.error('Response text:', await creditScoreResponse.text());
        setError('Failed to fetch dashboard credit score');
      }
    } catch (err) {
      console.error('Error fetching dashboard credit score:', err);
      setError('Network error while fetching credit score');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      console.log('🔄 useEffect triggered - fetching credit score for dashboard');
      fetchCreditScore();
    }
  }, [token]);

  // Add another useEffect to refresh when the component mounts or token changes
  useEffect(() => {
    const intervalId = setInterval(() => {
      if (token && !loading) {
        console.log('🔄 Periodic refresh - checking for new invoices and updating credit score');
        fetchCreditScore();
      }
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(intervalId);
  }, [token, loading]);

  return {
    creditScore,
    category,
    lastUpdated,
    totalInvoices,
    loading,
    error,
    refreshCreditScore: fetchCreditScore
  };
}
