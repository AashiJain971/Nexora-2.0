import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useCreditScore } from '@/hooks/use-credit-score';
import { useCreditScoreImprovement } from '@/hooks/use-credit-improvement';

import { 
  Crown,
  ChartLine, 
  Leaf, 
  Handshake, 
  Rocket,
  GraduationCap,
  Trophy,
  CheckCircle,
  TrendingUp,
  PlayCircle,
  Clock,
  Calendar
} from 'lucide-react';
import { useDummyData } from '@/hooks/use-dummy-data';

export default function Profile() {
  const { 
    businessProfile, 
    badges, 
    loans,
    learningProgress,
    learningCourses
  } = useDummyData();
  
  // Get real credit score data
  const { creditScore, category, totalInvoices } = useCreditScore();
  const { improvement, message } = useCreditScoreImprovement();

  const formatCurrency = (amount: string | number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(typeof amount === 'string' ? parseInt(amount) : amount);
  };

  const getBadgeIcon = (iconType: string) => {
    switch (iconType) {
      case 'crown': return Crown;
      case 'chart-line': return ChartLine;
      case 'leaf': return Leaf;
      case 'handshake': return Handshake;
      case 'rocket': return Rocket;
      case 'graduation-cap': return GraduationCap;
      default: return Trophy;
    }
  };

  const getBadgeColor = (color: string) => {
    switch (color) {
      case 'gold': return 'from-yellow-400 to-yellow-600';
      case 'blue': return 'from-blue-400 to-blue-600';
      case 'green': return 'from-green-400 to-green-600';
      case 'purple': return 'from-purple-400 to-purple-600';
      case 'red': return 'from-red-400 to-red-600';
      case 'orange': return 'from-orange-400 to-orange-600';
      default: return 'from-gray-400 to-gray-600';
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 80) return 'teal';
    if (progress >= 50) return 'orange';
    return 'green';
  };

  const totalLoans = loans.length;
  const activeLoans = loans.filter(loan => loan.status === 'active').length;
  const totalBorrowed = loans.reduce((sum, loan) => sum + parseInt(loan.amount), 0);
  const totalRepaid = loans.reduce((sum, loan) => sum + parseInt(loan.repaidAmount), 0);

  return (
    <div className="pt-16 min-h-screen bg-background">
      <div className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">MSME Profile</h1>
          <p className="text-xl text-muted-foreground">Your complete business profile and achievements</p>
        </div>
        
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Profile Info */}
          <div className="lg:col-span-1 space-y-6">
            <Card className="p-6">
              <div className="text-center mb-6">
                <div className="w-24 h-24 bg-gradient-to-r from-teal-accent to-green-accent rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-background">AC</span>
                </div>
                <h3 className="text-xl font-semibold">{businessProfile.businessName}</h3>
                <p className="text-muted-foreground">{businessProfile.category}</p>
              </div>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Founded</span>
                  <span>{businessProfile.establishedYear}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Employees</span>
                  <span>{businessProfile.employees}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Location</span>
                  <span>{businessProfile.location}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Business Type</span>
                  <span>{businessProfile.businessType}</span>
                </div>
              </div>
              
              <div className="mt-6 pt-6 border-t border-border">
                <h4 className="font-semibold mb-3">Verification Status</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Business Registration</span>
                    <CheckCircle className="w-4 h-4 text-green-accent" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Tax Compliance</span>
                    <CheckCircle className="w-4 h-4 text-green-accent" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Bank Verification</span>
                    <CheckCircle className="w-4 h-4 text-green-accent" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Blockchain Identity</span>
                    <CheckCircle className="w-4 h-4 text-green-accent" />
                  </div>
                </div>
              </div>
            </Card>
            
            {/* Credit Score */}
            <Card className="p-6">
              <h4 className="text-lg font-semibold mb-4">Credit Score</h4>
              <div className="text-center">
                <div className="text-4xl font-bold text-green-accent mb-2">{creditScore}</div>
                <div className="text-sm text-muted-foreground mb-4">{category} Rating</div>
                <div className="w-full bg-muted rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-orange-accent via-teal-accent to-green-accent h-3 rounded-full transition-all duration-500" 
                    style={{ width: `${Math.min(100, (creditScore / 100) * 100)}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-muted-foreground mt-2">
                  <span>0</span>
                  <span>100</span>
                </div>
              </div>
              
              <div className="mt-4 p-3 bg-green-accent/20 border border-green-accent rounded-lg">
                <div className="text-sm text-green-accent">
                  <TrendingUp className="w-4 h-4 mr-1 inline" />
                  {improvement > 0 ? `+${improvement} points this month! ` : ''}{message}
                </div>
              </div>
            </Card>
          </div>
          
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Achievements & Badges */}
            <Card className="p-6">
              <h3 className="text-xl font-semibold mb-6">MSME Badges & Achievements</h3>
              <div className="grid md:grid-cols-3 gap-6">
                {badges.map((badge) => {
                  const IconComponent = getBadgeIcon(badge.iconType);
                  const colorClass = getBadgeColor(badge.color);
                  
                  return (
                    <div key={badge.id} className="text-center p-4 hover:bg-muted/50 rounded-lg transition-colors">
                      <div className={`w-16 h-16 bg-gradient-to-r ${colorClass} rounded-full flex items-center justify-center mx-auto mb-3`}>
                        <IconComponent className="w-8 h-8 text-background" />
                      </div>
                      <h4 className="font-semibold mb-1">{badge.name}</h4>
                      <p className="text-sm text-muted-foreground">{badge.description}</p>
                      <div className="text-xs text-green-accent mt-2">Earned {badge.earnedAt}</div>
                    </div>
                  );
                })}
              </div>
            </Card>

            {/* Dashboard Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold">Active Loans</h4>
                  <ChartLine className="w-5 h-5 text-green-accent" />
                </div>
                <div className="text-2xl font-bold text-green-accent mb-2">{formatCurrency(totalBorrowed)}</div>
                <div className="text-sm text-muted-foreground">{activeLoans} loans • {Math.round((totalRepaid / totalBorrowed) * 100)}% repaid</div>
              </Card>
              
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold">Products Listed</h4>
                  <Badge className="w-5 h-5 text-orange-accent" />
                </div>
                <div className="text-2xl font-bold text-orange-accent mb-2">15</div>
                <div className="text-sm text-muted-foreground">8 categories • 12 active</div>
              </Card>
              
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold">Total Sales</h4>
                  <TrendingUp className="w-5 h-5 text-teal-accent" />
                </div>
                <div className="text-2xl font-bold text-teal-accent mb-2">₹8,45,230</div>
                <div className="text-sm text-muted-foreground">156 orders • 4.8★ rating</div>
              </Card>
              
              <Card className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold">Learning Progress</h4>
                  <GraduationCap className="w-5 h-5 text-purple-400" />
                </div>
                <div className="text-2xl font-bold text-purple-400 mb-2">85%</div>
                <div className="text-sm text-muted-foreground">17/20 modules completed</div>
              </Card>
            </div>

            {/* Learning & AI Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Recent Learning */}
              <Card className="p-6">
                <h4 className="text-xl font-semibold mb-4">Recent Learning</h4>
                <div className="space-y-4">
                  {learningCourses.slice(0, 3).map((course, index) => (
                    <div key={course.id} className="flex items-center space-x-4 p-3 bg-muted/50 rounded-lg">
                      <div className="w-12 h-12 bg-teal-accent rounded-lg flex items-center justify-center">
                        {course.id === '1' ? (
                          <PlayCircle className="w-6 h-6 text-background" />
                        ) : index === 1 ? (
                          <CheckCircle className="w-6 h-6 text-background" />
                        ) : (
                          <Clock className="w-6 h-6 text-background" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium">{course.title}</div>
                        <div className="text-sm text-muted-foreground">
                          {course.id === '1' ? `Progress: ${course.progress}% • 12 min left` :
                           index === 1 ? 'Completed • Certificate earned' :
                           `Next in queue • ${course.duration}`}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <Button className="w-full mt-4 bg-gradient-to-r from-teal-accent to-green-accent">
                  Continue Learning
                </Button>
              </Card>
              
              {/* Quick Actions */}
              <Card className="p-6">
                <h4 className="text-xl font-semibold mb-4">Quick Actions</h4>
                <div className="space-y-3">
                  <Button className="w-full justify-start" variant="outline">
                    <TrendingUp className="w-4 h-4 mr-2" />
                    View Analytics Dashboard
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <Calendar className="w-4 h-4 mr-2" />
                    Schedule Business Review
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <PlayCircle className="w-4 h-4 mr-2" />
                    Explore New Courses
                  </Button>
                </div>
              </Card>
            </div>

            {/* Learning Progress Details */}
            <Card className="p-6">
              <h4 className="text-xl font-semibold mb-4">Learning Progress Overview</h4>
              <div className="space-y-4">
                {learningProgress.map((item) => (
                  <div key={item.course}>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="font-medium">{item.course}</span>
                      <span className="text-muted-foreground">{item.progress}%</span>
                    </div>
                    <Progress 
                      value={item.progress} 
                      className={`w-full ${
                        item.color === 'teal' ? 'bg-teal-accent' :
                        item.color === 'orange' ? 'bg-orange-accent' :
                        'bg-green-accent'
                      }`}
                    />
                  </div>
                ))}
              </div>
              
              <div className="mt-6 p-4 bg-green-accent/20 border border-green-accent rounded-lg">
                <div className="text-sm text-green-accent">
                  <Trophy className="w-4 h-4 mr-1 inline" />
                  Complete 3 more courses to earn the "Business Strategist" badge!
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
