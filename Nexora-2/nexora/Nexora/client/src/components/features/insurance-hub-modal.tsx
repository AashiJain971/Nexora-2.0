import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import {
  Shield,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Calendar,
  Upload,
  Download,
  ExternalLink,
  Plus,
  FileText,
  DollarSign,
} from "lucide-react";

interface InsuranceHubModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface BusinessRiskAssessment {
  business_type: string;
  industry: string;
  employee_count: number;
  annual_revenue?: number;
  assets: Record<string, number>;
  risk_concerns: string[];
  has_existing_insurance: boolean;
  existing_policies: string[];
}

interface InsuranceRecommendation {
  template_id: number;
  policy_name: string;
  policy_type: string;
  provider_name: string;
  coverage_description: string;
  recommended_coverage: number;
  estimated_premium: number;
  legal_compliance: boolean;
  compliance_authority: string;
  coverage_features: Record<string, any>;
  optional_addons: Record<string, any>;
  relevance_score: number;
  matching_risks: string[];
  match_score?: number;
  reason?: string;
}

interface InsurancePolicy {
  id: number;
  policy_name: string;
  policy_type: string;
  provider_name: string;
  coverage_amount: number;
  premium_amount: number;
  premium_frequency: string;
  start_date: string;
  expiry_date: string;
  policy_number?: string;
  legal_compliance: boolean;
  compliance_authority: string;
  status: string;
  document_url?: string;
  notes?: string;
}

const riskOptions = [
  {
    value: "fire",
    label: "Fire & Allied Perils",
    description: "Fire, explosion, lightning damage",
  },
  {
    value: "theft",
    label: "Theft & Burglary",
    description: "Asset theft and burglary protection",
  },
  {
    value: "cyber",
    label: "Cyber Security",
    description: "Data breach, cyber fraud protection",
  },
  {
    value: "liability",
    label: "Public Liability",
    description: "Third-party injury and property damage",
  },
  {
    value: "employee_welfare",
    label: "Employee Health",
    description: "Group health insurance for staff",
  },
  {
    value: "natural_disasters",
    label: "Natural Disasters",
    description: "Earthquake, flood, cyclone coverage",
  },
  {
    value: "transport",
    label: "Goods in Transit",
    description: "Transportation and logistics risks",
  },
];

const businessTypes = [
  { value: "manufacturing", label: "Manufacturing" },
  { value: "retail", label: "Retail" },
  { value: "services", label: "Services" },
  { value: "digital", label: "Digital/IT" },
  { value: "export", label: "Export/Import" },
  { value: "warehouse", label: "Warehousing" },
];

export function InsuranceHubModal({
  open,
  onOpenChange,
}: InsuranceHubModalProps) {
  const [currentStep, setCurrentStep] = useState<
    "dashboard" | "assessment" | "recommendations" | "policies"
  >("dashboard");
  const [loading, setLoading] = useState(false);
  const [riskAssessment, setRiskAssessment] = useState<BusinessRiskAssessment>({
    business_type: "",
    industry: "",
    employee_count: 1,
    assets: {},
    risk_concerns: [],
    has_existing_insurance: false,
    existing_policies: [],
  });
  const [recommendations, setRecommendations] = useState<
    InsuranceRecommendation[]
  >([]);
  const [userPolicies, setUserPolicies] = useState<InsurancePolicy[]>([]);
  const [expiringPolicies, setExpiringPolicies] = useState<InsurancePolicy[]>(
    []
  );
  const [riskScore, setRiskScore] = useState<number>(0);

  const { token } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    if (open && token) {
      loadUserPolicies();
      loadExpiringPolicies();
    }
  }, [open, token]);

  const mapPolicy = (p: any): InsurancePolicy => ({
    id: p.policy_id || p.id,
    policy_name: p.policy_name,
    policy_type: p.policy_type,
    provider_name: p.provider_name || "Unknown",
    coverage_amount: p.coverage_amount || p.estimated_coverage_amount || 0,
    premium_amount: p.premium_amount || p.premium_estimate || 0,
    premium_frequency: "annual",
    start_date: p.start_date || p.created_at || new Date().toISOString(),
    expiry_date: p.expiry_date || p.renewal_date || new Date().toISOString(),
    policy_number: p.policy_number,
    legal_compliance: p.legal_compliance !== false,
    compliance_authority: p.compliance_authority || "IRDAI",
    status: p.status || "active",
    document_url: p.document_url,
    notes: "",
  });

  const loadUserPolicies = async () => {
    try {
      const response = await fetch(
        "https://nexora-2-0-6.onrender.com/insurance/policies",
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.ok) {
        const result = await response.json();
        const mapped = (result.policies || []).map(mapPolicy);
        setUserPolicies(mapped);
      }
    } catch (error) {
      console.error("Error loading policies:", error);
    }
  };

  const loadExpiringPolicies = async () => {
    try {
      // Reuse all policies and filter locally by days_to_expiry if backend provided; else compute
      const response = await fetch(
        "https://nexora-2-0-6.onrender.com/insurance/policies",
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );
      if (response.ok) {
        const result = await response.json();
        const mapped = (result.policies || []).map(mapPolicy);
        const now = new Date();
        const expiring = mapped.filter((p: InsurancePolicy) => {
          const d = new Date(p.expiry_date);
          const diff = (d.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
          return diff >= 0 && diff <= 60;
        });
        setExpiringPolicies(expiring);
      }
    } catch (error) {
      console.error("Error loading expiring policies:", error);
    }
  };

  const handleRiskAssessment = async () => {
    if (
      !riskAssessment.business_type ||
      !riskAssessment.industry ||
      riskAssessment.risk_concerns.length === 0
    ) {
      toast({
        title: "Incomplete Assessment",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        "https://nexora-2-0-6.onrender.com/insurance/assess",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            business_type: riskAssessment.business_type,
            assets: riskAssessment.assets,
            workforce_size: riskAssessment.employee_count,
            risk_concerns: riskAssessment.risk_concerns,
            region: "India",
            annual_revenue: riskAssessment.annual_revenue,
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        // Map backend recommendation fields to UI expectation
        const recs = (result.recommendations || []).map((r: any) => ({
          template_id: r.template_id,
          policy_name: r.policy_name,
          policy_type: r.policy_type,
          provider_name: r.provider_name,
          coverage_description: r.coverage_details || "",
          recommended_coverage:
            r.estimated_coverage_amount || r.coverage_amount || 0,
          estimated_premium: r.premium_estimate || 0,
          legal_compliance: r.legal_compliance !== false,
          compliance_authority: r.compliance_authority || "IRDAI",
          coverage_features: r.optional_addons || {},
          optional_addons: r.optional_addons || {},
          relevance_score: 0,
          matching_risks: r.risk_match || [],
          match_score: r.match_score,
          reason: r.reason,
        }));
        setRecommendations(recs);
        setRiskScore(result.risk_score || result.riskScore || 0);
        setCurrentStep("recommendations");

        toast({
          title: "Risk Assessment Complete",
          description: `Found ${recs.length} insurance recommendations`,
          variant: "default",
        });
      } else {
        throw new Error("Assessment failed");
      }
    } catch (error) {
      toast({
        title: "Assessment Failed",
        description: "Unable to process risk assessment",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  const getRiskScoreColor = (score: number) => {
    if (score >= 80) return "text-red-600";
    if (score >= 60) return "text-orange-600";
    if (score >= 40) return "text-yellow-600";
    return "text-green-600";
  };

  const handleRiskToggle = (riskValue: string) => {
    setRiskAssessment((prev) => ({
      ...prev,
      risk_concerns: prev.risk_concerns.includes(riskValue)
        ? prev.risk_concerns.filter((r) => r !== riskValue)
        : [...prev.risk_concerns, riskValue],
    }));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-7xl max-h-[95vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Shield className="w-6 h-6 text-teal-accent" />
            Insurance Hub - MSME Protection Center
          </DialogTitle>
          <p className="text-muted-foreground">
            Discover, compare, and manage legally compliant insurance policies
            for your business
          </p>
        </DialogHeader>

        {/* Navigation Tabs */}
        <div className="flex space-x-1 bg-muted/30 p-1 rounded-lg">
          {[
            { id: "dashboard", label: "Dashboard", icon: TrendingUp },
            { id: "assessment", label: "Risk Assessment", icon: AlertTriangle },
            {
              id: "recommendations",
              label: "Recommendations",
              icon: CheckCircle,
            },
            { id: "policies", label: "My Policies", icon: FileText },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <Button
                key={tab.id}
                variant={currentStep === tab.id ? "default" : "ghost"}
                className="flex-1 justify-center gap-2"
                onClick={() => setCurrentStep(tab.id as any)}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </Button>
            );
          })}
        </div>

        {/* Dashboard */}
        {currentStep === "dashboard" && (
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="p-4">
                <div className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-teal-accent" />
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Active Policies
                    </p>
                    <p className="text-2xl font-bold">
                      {userPolicies.filter((p) => p.status === "active").length}
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-orange-accent" />
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Expiring Soon
                    </p>
                    <p className="text-2xl font-bold">
                      {expiringPolicies.length}
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <div className="flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-green-accent" />
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Total Coverage
                    </p>
                    <p className="text-2xl font-bold">
                      {formatCurrency(
                        userPolicies.reduce(
                          (sum, p) => sum + p.coverage_amount,
                          0
                        )
                      )}
                    </p>
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-blue-accent" />
                  <div>
                    <p className="text-sm text-muted-foreground">
                      IRDAI Compliant
                    </p>
                    <p className="text-2xl font-bold">
                      {userPolicies.filter((p) => p.legal_compliance).length}/
                      {userPolicies.length}
                    </p>
                  </div>
                </div>
              </Card>
            </div>

            {/* Action Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-6 border-teal-accent/20 bg-gradient-to-r from-teal-accent/5 to-transparent">
                <CardHeader className="p-0 pb-4">
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-teal-accent" />
                    Get Insurance Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <p className="text-sm text-muted-foreground mb-4">
                    Assess your business risks and get personalized insurance
                    recommendations based on IRDAI-approved policies.
                  </p>
                  <Button
                    onClick={() => setCurrentStep("assessment")}
                    className="bg-teal-accent hover:bg-teal-accent/90"
                  >
                    Start Risk Assessment
                  </Button>
                </CardContent>
              </Card>

              <Card className="p-6 border-orange-accent/20 bg-gradient-to-r from-orange-accent/5 to-transparent">
                <CardHeader className="p-0 pb-4">
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-orange-accent" />
                    Manage Your Policies
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <p className="text-sm text-muted-foreground mb-4">
                    Track renewal dates, upload documents, and manage your
                    existing insurance portfolio in one place.
                  </p>
                  <Button
                    onClick={() => setCurrentStep("policies")}
                    variant="outline"
                    className="border-orange-accent text-orange-accent hover:bg-orange-accent/10"
                  >
                    View Policies
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Expiring Policies Alert */}
            {expiringPolicies.length > 0 && (
              <Card className="border-red-200 bg-red-50 dark:bg-red-900/10">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-red-600">
                    <AlertTriangle className="w-5 h-5" />
                    Policies Expiring Soon
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {expiringPolicies.slice(0, 3).map((policy) => (
                      <div
                        key={policy.id}
                        className="flex justify-between items-center"
                      >
                        <div>
                          <p className="font-medium">{policy.policy_name}</p>
                          <p className="text-sm text-muted-foreground">
                            {policy.provider_name}
                          </p>
                        </div>
                        <Badge variant="destructive">
                          Expires {formatDate(policy.expiry_date)}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Risk Assessment */}
        {currentStep === "assessment" && (
          <div className="space-y-6">
            <Card className="p-6">
              <CardHeader className="p-0 pb-4">
                <CardTitle>Business Risk Assessment</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Help us understand your business to recommend the most
                  suitable insurance policies
                </p>
              </CardHeader>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="business_type">Business Type *</Label>
                    <Select
                      value={riskAssessment.business_type}
                      onValueChange={(value) =>
                        setRiskAssessment((prev) => ({
                          ...prev,
                          business_type: value,
                        }))
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select business type" />
                      </SelectTrigger>
                      <SelectContent>
                        {businessTypes.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="industry">Industry *</Label>
                    <Input
                      value={riskAssessment.industry}
                      onChange={(e) =>
                        setRiskAssessment((prev) => ({
                          ...prev,
                          industry: e.target.value,
                        }))
                      }
                      placeholder="e.g., Textiles, Electronics, Food Processing"
                    />
                  </div>

                  <div>
                    <Label htmlFor="employee_count">Employee Count *</Label>
                    <Input
                      type="number"
                      value={riskAssessment.employee_count}
                      onChange={(e) =>
                        setRiskAssessment((prev) => ({
                          ...prev,
                          employee_count: parseInt(e.target.value),
                        }))
                      }
                      placeholder="Number of employees"
                      min="1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="annual_revenue">
                      Annual Revenue (Optional)
                    </Label>
                    <Input
                      type="number"
                      value={riskAssessment.annual_revenue || ""}
                      onChange={(e) =>
                        setRiskAssessment((prev) => ({
                          ...prev,
                          annual_revenue: e.target.value
                            ? parseFloat(e.target.value)
                            : undefined,
                        }))
                      }
                      placeholder="Annual revenue in INR"
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <Label>Asset Values (INR)</Label>
                    <div className="space-y-2">
                      {["machinery", "inventory", "building", "equipment"].map(
                        (asset) => (
                          <div
                            key={asset}
                            className="flex items-center space-x-2"
                          >
                            <Label className="w-20 text-sm capitalize">
                              {asset}:
                            </Label>
                            <Input
                              type="number"
                              value={riskAssessment.assets[asset] || ""}
                              onChange={(e) =>
                                setRiskAssessment((prev) => ({
                                  ...prev,
                                  assets: {
                                    ...prev.assets,
                                    [asset]: e.target.value
                                      ? parseFloat(e.target.value)
                                      : 0,
                                  },
                                }))
                              }
                              placeholder="0"
                              className="flex-1"
                            />
                          </div>
                        )
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                <Label>Risk Concerns (Select all that apply) *</Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                  {riskOptions.map((risk) => (
                    <div
                      key={risk.value}
                      className={`p-3 border-2 rounded-lg cursor-pointer transition-colors ${
                        riskAssessment.risk_concerns.includes(risk.value)
                          ? "border-teal-accent bg-teal-accent/10"
                          : "border-border hover:border-teal-accent/50"
                      }`}
                      onClick={() => handleRiskToggle(risk.value)}
                    >
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={riskAssessment.risk_concerns.includes(
                            risk.value
                          )}
                          onChange={() => handleRiskToggle(risk.value)}
                          className="rounded"
                        />
                        <div>
                          <p className="font-medium">{risk.label}</p>
                          <p className="text-xs text-muted-foreground">
                            {risk.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-6 flex justify-between">
                <Button
                  variant="outline"
                  onClick={() => setCurrentStep("dashboard")}
                >
                  Back to Dashboard
                </Button>
                <Button
                  onClick={handleRiskAssessment}
                  disabled={loading}
                  className="bg-teal-accent hover:bg-teal-accent/90"
                >
                  {loading ? "Assessing..." : "Get Recommendations"}
                </Button>
              </div>
            </Card>
          </div>
        )}

        {/* Recommendations */}
        {currentStep === "recommendations" && (
          <div className="space-y-6">
            {riskScore > 0 && (
              <Card className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Your Business Risk Score
                    </p>
                    <p
                      className={`text-2xl font-bold ${getRiskScoreColor(
                        riskScore
                      )}`}
                    >
                      {riskScore}/100
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Risk Level</p>
                    <Badge
                      variant={
                        riskScore >= 70
                          ? "destructive"
                          : riskScore >= 50
                          ? "secondary"
                          : "default"
                      }
                      className="text-sm"
                    >
                      {riskScore >= 70
                        ? "High Risk"
                        : riskScore >= 50
                        ? "Medium Risk"
                        : "Low Risk"}
                    </Badge>
                  </div>
                </div>
              </Card>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {recommendations.map((rec, index) => (
                <Card
                  key={rec.template_id}
                  className="border-2 hover:border-teal-accent/50 transition-colors"
                >
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-lg">
                          {rec.policy_name}
                        </CardTitle>
                        <p className="text-sm text-muted-foreground">
                          {rec.provider_name}
                        </p>
                      </div>
                      {rec.legal_compliance && (
                        <Badge className="bg-green-100 text-green-800">
                          ✅ {rec.compliance_authority} Approved
                        </Badge>
                      )}
                    </div>
                  </CardHeader>

                  <CardContent>
                    <p className="text-sm mb-4">{rec.coverage_description}</p>

                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium">
                          Coverage Amount:
                        </span>
                        <span className="font-bold text-green-600">
                          {formatCurrency(rec.recommended_coverage)}
                        </span>
                      </div>

                      <div className="flex justify-between">
                        <span className="text-sm font-medium">
                          Estimated Premium:
                        </span>
                        <span className="font-bold">
                          {formatCurrency(rec.estimated_premium)}
                        </span>
                      </div>

                      <div>
                        <p className="text-sm font-medium mb-1">
                          Covers Your Risks:
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {rec.matching_risks.map((risk) => (
                            <Badge
                              key={risk}
                              variant="outline"
                              className="text-xs"
                            >
                              {risk.replace("_", " ")}
                            </Badge>
                          ))}
                          {rec.matching_risks.length === 0 && (
                            <span className="text-xs text-muted-foreground">
                              General coverage
                            </span>
                          )}
                        </div>
                      </div>
                      {rec.reason && (
                        <div className="text-xs text-muted-foreground mt-2 leading-snug">
                          <span className="font-medium text-foreground">
                            Why:{" "}
                          </span>
                          {rec.reason}
                          {typeof rec.match_score === "number" && (
                            <span className="ml-2 text-[10px] px-1 py-0.5 bg-muted rounded">
                              Score {rec.match_score}
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="mt-4 pt-4 border-t">
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          className="flex-1 bg-teal-accent hover:bg-teal-accent/90"
                        >
                          Get Quote
                        </Button>
                        <Button size="sm" variant="outline">
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {recommendations.length === 0 && (
              <Card className="p-8 text-center">
                <AlertTriangle className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">
                  No Recommendations Found
                </h3>
                <p className="text-muted-foreground mb-4">
                  Complete the risk assessment to get personalized insurance
                  recommendations.
                </p>
                <Button onClick={() => setCurrentStep("assessment")}>
                  Complete Assessment
                </Button>
              </Card>
            )}
          </div>
        )}

        {/* My Policies */}
        {currentStep === "policies" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold">
                  Your Insurance Policies
                </h3>
                <p className="text-sm text-muted-foreground">
                  Manage and track all your business insurance policies
                </p>
              </div>
              <Button className="bg-teal-accent hover:bg-teal-accent/90">
                <Plus className="w-4 h-4 mr-2" />
                Add Policy
              </Button>
            </div>

            {userPolicies.length > 0 ? (
              <div className="space-y-4">
                {userPolicies.map((policy) => (
                  <Card key={policy.id} className="p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-semibold">
                            {policy.policy_name}
                          </h4>
                          <Badge
                            variant={
                              policy.status === "active"
                                ? "default"
                                : "secondary"
                            }
                          >
                            {policy.status}
                          </Badge>
                          {policy.legal_compliance && (
                            <Badge className="bg-green-100 text-green-800">
                              ✅ {policy.compliance_authority}
                            </Badge>
                          )}
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-muted-foreground">Provider</p>
                            <p className="font-medium">
                              {policy.provider_name}
                            </p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Coverage</p>
                            <p className="font-medium">
                              {formatCurrency(policy.coverage_amount)}
                            </p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Premium</p>
                            <p className="font-medium">
                              {formatCurrency(policy.premium_amount)}
                            </p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Expires</p>
                            <p className="font-medium">
                              {formatDate(policy.expiry_date)}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="flex space-x-2">
                        {policy.document_url && (
                          <Button size="sm" variant="outline">
                            <Download className="w-4 h-4" />
                          </Button>
                        )}
                        <Button size="sm" variant="outline">
                          <Upload className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="p-8 text-center">
                <FileText className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">
                  No Policies Found
                </h3>
                <p className="text-muted-foreground mb-4">
                  Start by getting insurance recommendations based on your
                  business risks.
                </p>
                <Button onClick={() => setCurrentStep("assessment")}>
                  Get Recommendations
                </Button>
              </Card>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
