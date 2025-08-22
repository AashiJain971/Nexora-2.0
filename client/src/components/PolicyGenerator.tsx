import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import BusinessForm from './BusinessForm';
import { Button } from './ui/button';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { CheckCircle, FileText, Building, Download, Eye, Trash2, ArrowLeft, ArrowRight } from 'lucide-react';

interface PolicyGeneratorProps {}

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

interface GeneratedPolicy {
  id: string;
  policy_type: string;
  content: string;
  generated_at: string;
  compliance_regions: string[];
}

const PolicyGenerator: React.FC<PolicyGeneratorProps> = () => {
  const { token } = useAuth();
  const [currentStep, setCurrentStep] = useState<'business' | 'generate' | 'view'>('business');
  const [businessData, setBusinessData] = useState<BusinessDetails | null>(null);
  const [selectedPolicies, setSelectedPolicies] = useState<string[]>(['privacy_policy']);
  const [language, setLanguage] = useState('en');
  const [generatedPolicies, setGeneratedPolicies] = useState<{ [key: string]: string }>({});
  // Always keep this as an array; never allow undefined to avoid runtime errors
  const [savedPolicies, setSavedPolicies] = useState<GeneratedPolicy[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const policyTypes = [
    { value: 'privacy_policy', label: 'Privacy Policy', description: 'How you collect, use, and protect user data' },
    { value: 'terms_conditions', label: 'Terms & Conditions', description: 'Rules and guidelines for using your service' },
    { value: 'refund_policy', label: 'Refund Policy', description: 'Your refund and return policies' },
    { value: 'cookie_policy', label: 'Cookie Policy', description: 'How you use cookies and tracking technologies' }
  ];

  const languages = [
    { value: 'en', label: 'English' },
    { value: 'hi', label: 'हिन्दी (Hindi)' },
    { value: 'es', label: 'Español (Spanish)' },
    { value: 'fr', label: 'Français (French)' }
  ];

  const steps = [
    { id: 'business', name: 'Business Details', icon: Building },
    { id: 'generate', name: 'Generate Policies', icon: FileText },
    { id: 'view', name: 'View & Download', icon: Eye }
  ];

  useEffect(() => {
    loadExistingPolicies();
    loadExistingBusiness();
  }, [token]);

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
        if (result.success) {
          setBusinessData(result.data);
        }
      }
    } catch (error) {
      console.log('No existing business data found');
    }
  };

  const loadExistingPolicies = async () => {
    if (!token) return;

    try {
      const response = await fetch('https://nexora-2-0-6.onrender.com/get-policies', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
            const data = Array.isArray(result.data) ? result.data : [];
            setSavedPolicies(data);
        } else {
            setSavedPolicies([]); // ensure array
        }
      } else {
        setSavedPolicies([]);
      }
    } catch (error) {
      console.log('No existing policies found');
    }
  };

  const handleBusinessSubmit = (data: BusinessDetails) => {
    setBusinessData(data);
    setCurrentStep('generate');
  };

  const handlePolicyToggle = (policyType: string) => {
    setSelectedPolicies(prev => 
      prev.includes(policyType) 
        ? prev.filter(p => p !== policyType)
        : [...prev, policyType]
    );
  };

  const generatePolicies = async () => {
    if (!businessData || selectedPolicies.length === 0) return;

    setIsGenerating(true);

    try {
      const response = await fetch('https://nexora-2-0-6.onrender.com/generate-policies', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          business_details: businessData,
          policy_types: selectedPolicies,
          language: language
        })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setGeneratedPolicies(result.policies);
        setCurrentStep('view');
        await loadExistingPolicies(); // Refresh saved policies
      } else {
        throw new Error(result.detail || 'Failed to generate policies');
      }
    } catch (error) {
      console.error('Error generating policies:', error);
      alert('Failed to generate policies. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadPolicy = (policyType: string, content: string) => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${businessData?.business_name || 'Business'}_${policyType}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const deletePolicy = async (policyId: string) => {
    if (!confirm('Are you sure you want to delete this policy?')) return;

    try {
      const response = await fetch(`https://nexora-2-0-6.onrender.com/delete-policy/${policyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        await loadExistingPolicies();
        alert('Policy deleted successfully');
      } else {
        throw new Error('Failed to delete policy');
      }
    } catch (error) {
      console.error('Error deleting policy:', error);
      alert('Failed to delete policy');
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-teal-accent to-orange-accent bg-clip-text text-transparent mb-4">
              Privacy Policy Generator
            </h1>
            <p className="text-muted-foreground text-lg">
              Generate legally compliant policies for your MSME business
            </p>
          </div>

          {/* Step Navigation */}
          <div className="flex justify-center mb-8">
            <div className="flex items-center space-x-8">
              {steps.map((step, index) => {
                const Icon = step.icon;
                const isActive = currentStep === step.id;
                const isCompleted = 
                  (step.id === 'business' && businessData) ||
                  (step.id === 'generate' && Object.keys(generatedPolicies).length > 0);

                return (
                  <div key={step.id} className="flex items-center">
                    <div className="flex flex-col items-center">
                      <div
                        className={`flex items-center justify-center w-12 h-12 rounded-full border-2 transition-colors cursor-pointer ${
                          isActive
                            ? 'border-teal-accent bg-teal-accent text-background'
                            : isCompleted
                            ? 'border-green-accent bg-green-accent text-background'
                            : 'border-muted-foreground bg-background text-muted-foreground'
                        }`}
                        onClick={() => {
                          if (step.id === 'business' || (step.id === 'generate' && businessData) || (step.id === 'view' && Object.keys(generatedPolicies).length > 0)) {
                            setCurrentStep(step.id as 'business' | 'generate' | 'view');
                          }
                        }}
                      >
                        {isCompleted && !isActive ? (
                          <CheckCircle className="w-6 h-6" />
                        ) : (
                          <Icon className="w-6 h-6" />
                        )}
                      </div>
                      <span
                        className={`mt-2 text-sm font-medium ${
                          isActive
                            ? 'text-teal-accent'
                            : isCompleted
                            ? 'text-green-accent'
                            : 'text-muted-foreground'
                        }`}
                      >
                        {step.name}
                      </span>
                    </div>
                    {index < steps.length - 1 && (
                      <div className="w-16 h-0.5 bg-border mx-4" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Step Content */}
          {currentStep === 'business' && (
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building className="w-5 h-5 text-teal-accent" />
                  Business Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <BusinessForm
                  onSubmit={handleBusinessSubmit}
                  onCancel={() => {}}
                  initialData={businessData}
                />
              </CardContent>
            </Card>
          )}

          {currentStep === 'generate' && (
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-teal-accent" />
                  Generate Legal Policies
                  {businessData && (
                    <Badge variant="secondary" className="ml-2">
                      For {businessData.business_name}
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-8">
                {/* Policy Selection */}
                <div>
                  <h3 className="text-xl font-semibold mb-4 text-foreground">Select Policies to Generate</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {policyTypes.map(policy => (
                      <div
                        key={policy.value}
                        className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                          selectedPolicies.includes(policy.value)
                            ? 'border-teal-accent bg-teal-accent/10'
                            : 'border-border hover:border-teal-accent/50'
                        }`}
                        onClick={() => handlePolicyToggle(policy.value)}
                      >
                        <div className="flex items-center mb-2">
                          <input
                            type="checkbox"
                            checked={selectedPolicies.includes(policy.value)}
                            onChange={() => handlePolicyToggle(policy.value)}
                            className="h-4 w-4 text-teal-accent focus:ring-teal-accent border-border rounded mr-3"
                          />
                          <h4 className="font-semibold text-foreground">{policy.label}</h4>
                        </div>
                        <p className="text-sm text-muted-foreground">{policy.description}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Language Selection */}
                <div>
                  <h3 className="text-xl font-semibold mb-4 text-foreground">Language</h3>
                  <Select value={language} onValueChange={setLanguage}>
                    <SelectTrigger className="w-full max-w-xs bg-background border-border text-foreground">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-card border-border">
                      {languages.map(lang => (
                        <SelectItem key={lang.value} value={lang.value}>{lang.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Business Summary */}
                {businessData && (
                  <div className="p-4 bg-muted/50 rounded-lg border border-border">
                    <h3 className="text-lg font-semibold mb-3 text-foreground">Business Summary</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                      <div><strong className="text-foreground">Type:</strong> <span className="text-muted-foreground">{businessData.business_type}</span></div>
                      <div><strong className="text-foreground">Industry:</strong> <span className="text-muted-foreground">{businessData.industry}</span></div>
                      <div><strong className="text-foreground">Location:</strong> <span className="text-muted-foreground">{businessData.location_country}</span></div>
                      <div><strong className="text-foreground">Target:</strong> <span className="text-muted-foreground">{businessData.target_audience}</span></div>
                      <div><strong className="text-foreground">Online:</strong> <span className="text-muted-foreground">{businessData.has_online_presence ? 'Yes' : 'No'}</span></div>
                      <div><strong className="text-foreground">Payments:</strong> <span className="text-muted-foreground">{businessData.processes_payments ? 'Yes' : 'No'}</span></div>
                    </div>
                  </div>
                )}

                {/* Navigation Buttons */}
                <div className="flex justify-between pt-6 border-t border-border">
                  <Button
                    variant="outline"
                    onClick={() => setCurrentStep('business')}
                    className="flex items-center gap-2"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    Edit Business Details
                  </Button>
                  <Button
                    onClick={generatePolicies}
                    disabled={isGenerating || selectedPolicies.length === 0 || !businessData}
                    className="bg-teal-accent hover:bg-teal-accent/90 text-background flex items-center gap-2"
                  >
                    {isGenerating ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-background"></div>
                        Generating...
                      </>
                    ) : (
                      <>
                        Generate Policies
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </Button>
                </div>

                {/* Existing Policies */}
                {Array.isArray(savedPolicies) && savedPolicies.length > 0 && (
                  <div className="pt-6 border-t border-border">
                    <h3 className="text-lg font-semibold mb-4 text-foreground">Previously Generated Policies</h3>
                    <div className="space-y-4">
                      {savedPolicies.map(policy => (
                        <div key={policy.id} className="flex items-center justify-between p-4 border border-border rounded-lg bg-muted/30">
                          <div>
                            <h4 className="font-semibold text-foreground">
                              {policyTypes.find(p => p.value === policy.policy_type)?.label || policy.policy_type}
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              Generated on {new Date(policy.generated_at).toLocaleDateString()}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Compliance: {policy.compliance_regions?.join(', ')}
                            </p>
                          </div>
                          <div className="flex space-x-2">
                            <Button
                              size="sm"
                              onClick={() => downloadPolicy(policy.policy_type, policy.content)}
                              className="bg-green-accent hover:bg-green-accent/90 text-background"
                            >
                              <Download className="w-4 h-4 mr-1" />
                              Download
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => deletePolicy(policy.id)}
                            >
                              <Trash2 className="w-4 h-4 mr-1" />
                              Delete
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {currentStep === 'view' && (
            <div className="space-y-6">
              <Card className="bg-card border-border">
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <CardTitle className="flex items-center gap-2">
                      <Eye className="w-5 h-5 text-teal-accent" />
                      Generated Policies
                      <Badge variant="secondary" className="ml-2">
                        {Object.keys(generatedPolicies).length} {Object.keys(generatedPolicies).length === 1 ? 'Policy' : 'Policies'}
                      </Badge>
                    </CardTitle>
                    <Button
                      variant="outline"
                      onClick={() => setCurrentStep('generate')}
                      className="flex items-center gap-2"
                    >
                      <ArrowLeft className="w-4 h-4" />
                      Generate More
                    </Button>
                  </div>
                </CardHeader>
              </Card>

              {Object.entries(generatedPolicies).map(([policyType, content]) => (
                <Card key={policyType} className="bg-card border-border">
                  <CardHeader>
                    <div className="flex justify-between items-center">
                      <CardTitle className="text-2xl text-foreground flex items-center gap-2">
                        <FileText className="w-6 h-6 text-teal-accent" />
                        {policyTypes.find(p => p.value === policyType)?.label || policyType}
                      </CardTitle>
                      <Button
                        onClick={() => downloadPolicy(policyType, content)}
                        className="bg-teal-accent hover:bg-teal-accent/90 text-background"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="prose prose-sm max-w-none">
                      <div className="whitespace-pre-wrap text-sm bg-muted/30 text-foreground p-6 rounded-md border border-border max-h-96 overflow-y-auto font-mono leading-relaxed">
                        {content}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PolicyGenerator;
