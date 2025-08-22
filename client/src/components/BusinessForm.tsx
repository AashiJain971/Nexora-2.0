import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Checkbox } from './ui/checkbox';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface BusinessDetails {
  business_name: string;
  business_type: string;
  industry: string;
  location_country: string;
  location_state?: string;
  location_city?: string;
  website_url?: string;
  has_online_presence: boolean;
  has_physical_store: boolean;
  collects_personal_data: boolean;
  processes_payments: boolean;
  uses_cookies: boolean;
  has_newsletter: boolean;
  target_audience: string;
  data_retention_period: number;
}

interface BusinessFormProps {
  onSubmit: (businessData: BusinessDetails) => void;
  onCancel: () => void;
  initialData?: BusinessDetails | null;
}

const BusinessForm: React.FC<BusinessFormProps> = ({ onSubmit, onCancel, initialData }) => {
  const { token } = useAuth();
  const [formData, setFormData] = useState<BusinessDetails>({
    business_name: '',
    business_type: 'retail',
    industry: '',
    location_country: 'India',
    location_state: '',
    location_city: '',
    website_url: '',
    has_online_presence: false,
    has_physical_store: false,
    collects_personal_data: true,
    processes_payments: false,
    uses_cookies: false,
    has_newsletter: false,
    target_audience: 'B2C',
    data_retention_period: 365
  });

  const [isLoading, setIsLoading] = useState(false);
  const [loadingExisting, setLoadingExisting] = useState(true);

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
      setLoadingExisting(false);
    } else {
      // Try to load existing business data
      loadExistingBusiness();
    }
  }, [initialData, token]);

  const loadExistingBusiness = async () => {
    if (!token) return;

    try {
      const response = await fetch('https://nexora-2-0-6.onrender.com/get-business', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success && result.business) {
          // Map backend business data to frontend form structure
          const businessData = result.business;
          setFormData({
            business_name: businessData.business_name || '',
            business_type: 'retail',
            industry: businessData.industry || '',
            location_country: 'India',
            location_state: '',
            location_city: businessData.location || '',
            website_url: '',
            has_online_presence: false,
            has_physical_store: false,
            collects_personal_data: true,
            processes_payments: false,
            uses_cookies: false,
            has_newsletter: false,
            target_audience: 'B2C',
            data_retention_period: 365
          });
        }
      }
    } catch (error) {
      console.log('No existing business data found');
    } finally {
      setLoadingExisting(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checkbox = e.target as HTMLInputElement;
      setFormData(prev => ({
        ...prev,
        [name]: checkbox.checked
      }));
    } else if (type === 'number') {
      setFormData(prev => ({
        ...prev,
        [name]: parseInt(value) || 0
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('https://nexora-2-0-6.onrender.com/register-business', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();

      if (response.ok && result.success) {
        onSubmit(formData);
      } else {
        throw new Error(result.detail || 'Failed to save business details');
      }
    } catch (error) {
      console.error('Error saving business:', error);
      alert('Failed to save business details. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (loadingExisting) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-accent"></div>
      </div>
    );
  }

  // Safety check to ensure formData is properly initialized
  if (!formData) {
    return (
      <div className="flex justify-center items-center p-8 text-red-500">
        Error: Form data not initialized properly
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Business Information */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-foreground">Basic Business Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="business_name" className="text-foreground">Business Name *</Label>
                <Input
                  id="business_name"
                  name="business_name"
                  type="text"
                  value={formData?.business_name || ''}
                  onChange={handleInputChange}
                  required
                  className="bg-background border-border text-foreground"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="business_type" className="text-foreground">Business Type *</Label>
                <Select 
                  value={formData?.business_type || 'retail'} 
                  onValueChange={(value) => setFormData(prev => ({...prev, business_type: value}))}
                >
                  <SelectTrigger className="bg-background border-border text-foreground">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    <SelectItem value="retail">Retail</SelectItem>
                    <SelectItem value="service">Service</SelectItem>
                    <SelectItem value="manufacturing">Manufacturing</SelectItem>
                    <SelectItem value="e-commerce">E-commerce</SelectItem>
                    <SelectItem value="saas">SaaS</SelectItem>
                    <SelectItem value="consulting">Consulting</SelectItem>
                    <SelectItem value="restaurant">Restaurant</SelectItem>
                    <SelectItem value="healthcare">Healthcare</SelectItem>
                    <SelectItem value="education">Education</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="industry" className="text-foreground">Industry *</Label>
                <Input
                  id="industry"
                  name="industry"
                  type="text"
                  value={formData?.industry || ''}
                  onChange={handleInputChange}
                  required
                  placeholder="e.g., Technology, Finance, Healthcare"
                  className="bg-background border-border text-foreground"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="target_audience" className="text-foreground">Target Audience *</Label>
                <Select 
                  value={formData?.target_audience || 'B2C'} 
                  onValueChange={(value) => setFormData(prev => ({...prev, target_audience: value}))}
                >
                  <SelectTrigger className="bg-background border-border text-foreground">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    <SelectItem value="B2C">Business to Consumer (B2C)</SelectItem>
                    <SelectItem value="B2B">Business to Business (B2B)</SelectItem>
                    <SelectItem value="Both">Both B2B and B2C</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Location Information */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-foreground">Location</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <Label htmlFor="location_country" className="text-foreground">Country *</Label>
                <Input
                  id="location_country"
                  name="location_country"
                  type="text"
                  value={formData?.location_country || 'India'}
                  onChange={handleInputChange}
                  required
                  className="bg-background border-border text-foreground"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location_state" className="text-foreground">State/Province</Label>
                <Input
                  id="location_state"
                  name="location_state"
                  type="text"
                  value={formData.location_state || ''}
                  onChange={handleInputChange}
                  className="bg-background border-border text-foreground"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location_city" className="text-foreground">City</Label>
                <Input
                  id="location_city"
                  name="location_city"
                  type="text"
                  value={formData.location_city || ''}
                  onChange={handleInputChange}
                  className="bg-background border-border text-foreground"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Website Information */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Online Presence</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label className="text-sm font-medium text-muted-foreground">Website URL</Label>
              <Input
                type="url"
                name="website_url"
                value={formData.website_url || ''}
                onChange={handleInputChange}
                placeholder="https://example.com"
                className="bg-background border-border text-foreground placeholder:text-muted-foreground/60"
              />
              <p className="text-xs text-muted-foreground">Include https://. Leave blank if none.</p>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium text-muted-foreground">Data Retention Period (days)</Label>
              <Input
                type="number"
                name="data_retention_period"
                value={formData?.data_retention_period || 365}
                onChange={handleInputChange}
                min={30}
                max={3650}
                className="bg-background border-border text-foreground"
              />
              <p className="text-xs text-muted-foreground">How long you keep user data (30 - 3650 days).</p>
            </div>
          </div>
        </div>

        {/* Business Features */}
        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Business Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { id: 'has_online_presence', label: 'Has Online Presence (Website/App)' },
              { id: 'has_physical_store', label: 'Has Physical Store/Office' },
              { id: 'collects_personal_data', label: 'Collects Personal Data' },
              { id: 'processes_payments', label: 'Processes Online Payments' },
              { id: 'uses_cookies', label: 'Uses Cookies/Tracking' },
              { id: 'has_newsletter', label: 'Sends Marketing/Newsletter' }
            ].map(opt => (
              <label key={opt.id} className="flex items-center space-x-2 rounded-md border border-border/60 bg-background px-3 py-2 hover:bg-accent/30 transition-colors cursor-pointer">
                <input
                  type="checkbox"
                  id={opt.id}
                  name={opt.id}
                  checked={(formData as any)?.[opt.id] || false}
                  onChange={handleInputChange}
                  className="h-4 w-4 rounded border-border text-teal-500 focus:ring-teal-500 focus:ring-offset-0 bg-background"
                />
                <span className="text-sm text-foreground leading-snug">{opt.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-4 pt-6 border-t">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 rounded-md border border-border text-muted-foreground hover:bg-accent/40 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-2 rounded-md bg-gradient-to-r from-teal-500 to-blue-600 text-white shadow hover:opacity-90 disabled:opacity-50 transition-colors"
          >
            {isLoading ? 'Saving...' : 'Save Business Details'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default BusinessForm;
